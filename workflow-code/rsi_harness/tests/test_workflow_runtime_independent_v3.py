"""Independent trust-boundary regressions, using synthetic temporary runs only."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_plan_v3 import CONFIG
from workflow_runtime_v3 import Run, digest, freeze


class IndependentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.input = self.root / "input.json"
        self.input.write_text('{"version":1}')
        self.workflow = json.loads(CONFIG.read_text())
        self.bundle = {key: [] for key in ("objects", "components", "materials", "relations", "taxonomy", "evidence")}
        self.run = self.new_run("run")

    def new_run(self, name, **options):
        run = freeze(self.root / name, project_root=self.root, run_id=name, parent_release_id="parent",
                     inputs={"input": self.input}, workflow=self.workflow, bundle=self.bundle, **options)
        self.addCleanup(run.close)
        return run

    def claim(self, run=None, collector="collector", now=100):
        run = self.run if run is None else run
        run.enqueue("F4-review", [{"record_id": "record-1", "source_locator": "source.csv:2"}], collector)
        return run.claim("reviewer", now=now)

    def receipt(self, task):
        return {"host_call_id": "unique-host-call", "agent_id": "host-agent", "model": "gpt-6-luna",
                "reasoning_effort": "max", "candidate_sha256": task["candidate_sha256"], "reviewer": "reviewer",
                "task_id": task["task_id"], "attempt": task["attempt"], "run_id": task["run_id"],
                "epoch": task["epoch"], "lease_sha256": digest(task["lease_token"]),
                "parent_release_id": task["parent_release_id"]}

    def review(self, task, locator="source.csv:2"):
        return {"candidate_sha256": task["candidate_sha256"], "input_sha256": task["input_sha256"],
                "reviewer": "reviewer", "host_call_id": "unique-host-call", "task_id": task["task_id"],
                "attempt": task["attempt"], "run_id": task["run_id"], "epoch": task["epoch"],
                "decisions": [{"record_id": "record-1", "decision": "PASS", "reason": "Read supplied synthetic locator",
                               "source_locator": locator}]}

    def test_review_cannot_substitute_an_unrelated_source_locator(self):
        task = self.claim()
        self.run.record_dispatch(task["task_id"], task["lease_token"], self.receipt(task), now=101)
        with self.assertRaises(ValueError):
            self.run.submit_review(task["task_id"], task["lease_token"],
                                   self.review(task, locator="unrelated-document.pdf:99"), now=102)

    def test_dispatch_cannot_name_the_collector_as_the_actual_review_agent(self):
        task = self.claim(collector="collector-agent")
        receipt = {**self.receipt(task), "agent_id": "collector-agent"}
        with self.assertRaises(ValueError):
            self.run.record_dispatch(task["task_id"], task["lease_token"], receipt, now=101)

    def test_actual_host_receipt_cannot_be_replayed_for_another_task(self):
        first = self.claim(collector="collector-a")
        receipt = self.receipt(first)
        self.run.record_dispatch(first["task_id"], first["lease_token"], receipt, now=101)
        self.run.submit_review(first["task_id"], first["lease_token"], self.review(first), now=102)
        second = self.claim(collector="collector-b", now=200)
        self.assertEqual(first["candidate_sha256"], second["candidate_sha256"])
        self.assertNotEqual(first["task_id"], second["task_id"])
        with self.assertRaises(ValueError):
            self.run.record_dispatch(second["task_id"], second["lease_token"], receipt, now=201)
        # Correcting all task bindings must still not reuse the real host call.
        with self.assertRaises(ValueError):
            self.run.record_dispatch(second["task_id"], second["lease_token"], self.receipt(second), now=201)

    def test_old_attempt_dispatch_receipt_cannot_be_replayed_after_recovery(self):
        first = self.claim()
        receipt = self.receipt(first)
        self.run.record_dispatch(first["task_id"], first["lease_token"], receipt, now=101)
        self.run.recover(first["task_id"], "synthetic crash", actor="supervisor", now=1001)
        second = self.run.claim("reviewer", now=1100)
        self.assertEqual(second["attempt"], first["attempt"] + 1)
        with self.assertRaises(ValueError):
            self.run.record_dispatch(second["task_id"], second["lease_token"], receipt, now=1101)

    def test_remaining_run_seconds_bound_the_new_lease(self):
        run = self.new_run("tiny-budget", max_seconds=1)
        task = self.claim(run)
        self.assertLessEqual(task["lease_until"], 101)

    def advance_parent(self, task):
        self.run.record_dispatch(task["task_id"], task["lease_token"], self.receipt(task), now=101)
        self.run.submit_review(task["task_id"], task["lease_token"], self.review(task), now=102)
        return self.run.merge([task["task_id"]], actor="merger", expected_parent="parent")

    def test_ready_task_from_an_old_parent_cannot_consume_a_new_lease(self):
        first = self.claim(collector="collector-a")
        self.run.enqueue("F4-review", [{"record_id": "record-1", "source_locator": "source.csv:2"}], "collector-b")
        self.advance_parent(first)
        try:
            stale = self.run.claim("new-reviewer", now=103)
        except ValueError:
            return
        self.assertIsNone(stale, "Old-parent candidate cannot be reviewed against the new release")

    def test_parent_advance_invalidates_an_outstanding_old_parent_lease(self):
        first = self.claim(collector="collector-a")
        self.run.enqueue("F4-review", [{"record_id": "record-1", "source_locator": "source.csv:2"}], "collector-b")
        second = self.run.claim("second-reviewer", now=100)
        self.advance_parent(first)
        with self.assertRaises(ValueError):
            self.run.handoff(second["task_id"], second["lease_token"], now=103)

    def test_inflight_work_reserves_run_seconds_across_owners(self):
        run = self.new_run("concurrent-budget", max_seconds=1)
        self.claim(run)
        run.enqueue("F4-review", [{"record_id": "record-2", "source_locator": "source.csv:3"}], "collector")
        try:
            task = run.claim("another-reviewer", now=100)
        except ValueError:
            return
        self.assertIsNone(task, "Outstanding lease already reserves the entire remaining budget")

    def test_concurrent_recovery_does_not_charge_the_same_lease_twice(self):
        task = self.claim()
        barrier = threading.Barrier(2)
        errors, outcomes = [], []

        class CursorGate:
            def __init__(self, cursor):
                self.cursor = cursor

            def fetchone(self):
                value = self.cursor.fetchone()
                # This widens the real read-before-write race only when both
                # connections can read. A BEGIN IMMEDIATE repair serializes it.
                try:
                    barrier.wait(timeout=0.5)
                except threading.BrokenBarrierError:
                    pass
                return value

        class ConnectionGate:
            def __init__(self, connection):
                self.connection = connection

            def execute(self, sql, parameters=()):
                cursor = self.connection.execute(sql, parameters)
                if sql.startswith("SELECT * FROM tasks WHERE id="):
                    return CursorGate(cursor)
                return cursor

            def __getattr__(self, key):
                return getattr(self.connection, key)

            def __enter__(self):
                self.connection.__enter__()
                return self

            def __exit__(self, *args):
                return self.connection.__exit__(*args)

        def recover():
            run = Run(self.root / "run")
            run.db = ConnectionGate(run.db)
            try:
                outcomes.append(run.recover(task["task_id"], "synthetic concurrent recovery", actor="supervisor", now=1001))
            except ValueError:
                outcomes.append("already recovered")
            except Exception as exc:
                errors.append(exc)
            finally:
                run.close()

        workers = [threading.Thread(target=recover) for _ in range(2)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join(timeout=5)
        self.assertFalse(any(worker.is_alive() for worker in workers))
        self.assertEqual(errors, [])
        self.assertEqual(self.run.checkpoint()["seconds_spent"], 900)
        self.assertEqual(sum(isinstance(value, dict) for value in outcomes), 1)

    def test_freeze_api_rejects_fixed_model_route_drift(self):
        self.workflow = copy.deepcopy(self.workflow)
        self.workflow["modelRoutes"][1]["model"] = "silently-substituted-model"
        with self.assertRaises(ValueError):
            self.new_run("drifted-routing")


if __name__ == "__main__":
    unittest.main()
