"""Crash, stale-input, independent-review and atomic-merge boundaries."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_plan_v3 import CONFIG
from workflow_runtime_v3 import freeze, digest


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input = self.root / "input.json"
        self.input.write_text('{"version":1}')
        self.bundle = {key: [] for key in ("objects", "components", "materials", "relations", "taxonomy", "evidence")}
        self.run = freeze(self.root / "run", project_root=self.root, run_id="test", parent_release_id="parent",
                          inputs={"input": self.input}, workflow=json.loads(CONFIG.read_text()), bundle=self.bundle)

    def tearDown(self):
        self.run.close()
        self.temp.cleanup()

    def task(self, operations=None):
        record = {"record_id": "r1", "source_locator": "source.csv:2"}
        if operations is not None:
            record["operations"] = operations
        tasks = self.run.enqueue("F4-review", [record], "collector")
        return self.run.claim("reviewer", now=100)

    def dispatch(self, task):
        receipt = {"host_call_id": "test-host-call", "agent_id": "test-agent", "model": "gpt-6-luna",
                   "reasoning_effort": "max", "candidate_sha256": task["candidate_sha256"], "reviewer": "reviewer",
                   "task_id": task["task_id"], "run_id": task["run_id"], "epoch": task["epoch"],
                   "parent_release_id": task["parent_release_id"], "attempt": task["attempt"],
                   "lease_sha256": digest(task["lease_token"])}
        self.run.record_dispatch(task["task_id"], task["lease_token"], receipt, now=101)
        return receipt

    def reviewed(self, task, decision="PASS"):
        dispatch = self.dispatch(task)
        review = {"candidate_sha256": task["candidate_sha256"], "input_sha256": task["input_sha256"],
                  "reviewer": "reviewer", "host_call_id": dispatch["host_call_id"],
                  "decisions": [{"record_id": "r1", "decision": decision, "reason": "Fixture source readback", "source_locator": "source.csv:2"}]}
        self.run.submit_review(task["task_id"], task["lease_token"], review, now=102)

    def test_changed_frozen_input_stops_resume(self):
        self.input.write_text('{"version":2}')
        with self.assertRaisesRegex(ValueError, "changed"):
            self.run.verify_inputs()

    def test_dedup_batches_and_explicit_tail(self):
        records = [{"record_id": str(i), "source_locator": "source.csv:" + str(i + 2)} for i in range(201)]
        a = self.run.enqueue("F4-review", records, "collector", 100)
        b = self.run.enqueue("F4-review", records, "collector", 100)
        self.assertEqual(a, b)
        self.assertEqual([t["records"] for t in a], [100, 100, 1])
        self.assertTrue(a[-1]["tail_batch"])
        self.assertEqual(len(self.run.checkpoint()["tasks"]), 3)

    def test_no_self_claim_or_duplicate_owner_lease(self):
        self.run.enqueue("F4-review", [{"record_id": "r1", "source_locator": "s:1"}], "collector")
        self.assertIsNone(self.run.claim("collector", now=100))
        self.run.claim("reviewer", now=100)
        with self.assertRaisesRegex(ValueError, "active"):
            self.run.claim("reviewer", now=101)

    def test_model_fallback_and_false_review_fail(self):
        task = self.task()
        receipt = {"host_call_id": "call", "agent_id": "agent", "model": "gpt-6.1-sol", "reasoning_effort": "high",
                   "candidate_sha256": task["candidate_sha256"], "reviewer": "reviewer"}
        with self.assertRaisesRegex(ValueError, "routing mismatch"):
            self.run.record_dispatch(task["task_id"], task["lease_token"], receipt, now=101)
        with self.assertRaisesRegex(ValueError, "dispatch"):
            self.run.submit_review(task["task_id"], task["lease_token"], {}, now=101)

    def test_missing_decision_fails_and_expired_token_stays_invalid(self):
        task = self.task()
        self.dispatch(task)
        review = {"candidate_sha256": task["candidate_sha256"], "input_sha256": task["input_sha256"],
                  "reviewer": "reviewer", "host_call_id": "test-host-call", "decisions": []}
        with self.assertRaisesRegex(ValueError, "exactly once"):
            self.run.submit_review(task["task_id"], task["lease_token"], review, now=102)
        with self.assertRaisesRegex(ValueError, "expired"):
            self.run.submit_review(task["task_id"], task["lease_token"], review, now=1001)

    def test_three_crashes_preserve_budget_and_cooldown(self):
        task = self.task()
        for attempt in (1, 2, 3):
            now = 100 + (attempt - 1) * 1000
            result = self.run.recover(task["task_id"], "worker crashed", actor="supervisor", now=now + 901)
            self.assertEqual(result["attempts_preserved"], attempt)
            if attempt < 3:
                task = self.run.claim("reviewer", now=now + 1000)
        self.assertEqual(result["status"], "COOLDOWN")
        checkpoint = self.run.checkpoint()
        self.assertEqual(checkpoint["attempts_used"], 3)
        self.assertEqual(checkpoint["seconds_spent"], 2700)
        self.assertIsNone(self.run.claim("another-reviewer", now=5000))

    def test_atomic_merge_rollback_and_preimage(self):
        operations = [{"table": "relations", "id": "orphan", "action": "upsert", "before_sha256": None,
                       "value": {"relation_id": "orphan", "component_id": "missing", "material_id": "missing", "decision": "PASS"}}]
        task = self.task(operations)
        self.reviewed(task)
        with self.assertRaises((ValueError, KeyError)):
            self.run.merge([task["task_id"]], actor="merger", expected_parent="parent")
        self.assertEqual(self.run.meta("current_release"), "parent")
        self.assertEqual(self.run.bundle(), self.bundle)
        self.assertEqual(self.run.checkpoint()["tasks"][0]["status"], "REVIEWED")

    def test_hold_never_applies_delta_and_merge_is_idempotent(self):
        task = self.task([{"table": "not-a-table"}])
        self.reviewed(task, "HOLD")
        result = self.run.merge([task["task_id"]], actor="merger", expected_parent="parent")
        self.assertEqual(result["operations"], 0)
        self.assertEqual(self.run.bundle(), self.bundle)
        again = self.run.merge([task["task_id"]], actor="merger", expected_parent="parent")
        self.assertTrue(again["idempotent"])
        self.assertEqual(result["release_id"], again["release_id"])

    def test_merger_cannot_be_reviewer_and_parent_must_match(self):
        task = self.task()
        self.reviewed(task)
        with self.assertRaisesRegex(ValueError, "independent"):
            self.run.merge([task["task_id"]], actor="reviewer", expected_parent="parent")
        with self.assertRaisesRegex(ValueError, "independent"):
            self.run.merge([task["task_id"]], actor="test-agent", expected_parent="parent")
        with self.assertRaisesRegex(ValueError, "Parent"):
            self.run.merge([task["task_id"]], actor="merger", expected_parent="changed")


if __name__ == "__main__":
    unittest.main()
