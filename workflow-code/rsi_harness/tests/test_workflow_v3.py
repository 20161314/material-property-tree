"""Boundaries for the read-only workflow planner; no production data fixtures."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_plan_v3 import CONFIG, ROUTING, build_plan, validate_workflow


class WorkflowV3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = json.loads(CONFIG.read_bytes())
        cls.policy = json.loads(ROUTING.read_bytes())

    def test_real_contract_accepts_fixed_model_policy(self):
        validate_workflow(self.config, self.policy)
        browser = next(step for step in self.config["steps"] if step["id"] == "F8-browser")
        self.assertIn("四页", browser["name"])
        self.assertTrue(any("工作流" in action for action in browser["actions"]))

    def test_bulk_reviews_request_luna_but_never_claim_dispatch(self):
        result = build_plan(self.config, self.policy, step_ids=["F4-review", "F6-review"])
        self.assertEqual(len(result["tasks"]), 2)
        for task in result["tasks"]:
            self.assertEqual((task["route"]["model"], task["route"]["reasoning_effort"]), ("gpt-6-luna", "max"))
            self.assertEqual(task["execution_status"], "NOT_EXECUTED")
            self.assertFalse(task["dispatch_executed"])
            self.assertEqual(task["batch"]["records_assigned"], 0)
            self.assertEqual(task["handoff"]["pin_status"], "REQUIRES_INPUT_FREEZE")
            self.assertTrue(task["blocking_conditions"])

    def test_ordinary_conflicts_request_sol_without_mutating_contract(self):
        before = copy.deepcopy(self.config)
        result = build_plan(self.config, self.policy, step_ids=["F4-conflicts", "F6-conflicts"])
        for task in result["tasks"]:
            self.assertEqual((task["route"]["model"], task["route"]["reasoning_effort"]), ("gpt-6.1-sol", "high"))
            self.assertEqual(task["max_attempts"], task["max_retries"] + 1)
        self.assertEqual(self.config, before)

    def test_rejects_routing_drift_and_silent_fallback(self):
        for target in ("workflow", "policy"):
            config, policy = copy.deepcopy(self.config), copy.deepcopy(self.policy)
            if target == "workflow":
                config["steps"][6]["model"] = "gpt-6.1-sol/high"
            else:
                policy["silent_model_fallback_allowed"] = True
            with self.subTest(target=target), self.assertRaises(ValueError):
                validate_workflow(config, policy)

    def test_bounded_batches_plans_and_unknown_steps_fail_closed(self):
        for args in ({"batch_size": 49}, {"batch_size": 201}, {"limit": 0}, {"limit": 9},
                     {"step_ids": ["missing"]}, {"step_ids": ["P0-plan", "P0-plan"]},
                     {"run_id": "../escape"}):
            with self.subTest(args=args), self.assertRaises(ValueError):
                build_plan(self.config, self.policy, **args)
        for size in (50, 100, 200):
            result = build_plan(self.config, self.policy, batch_size=size, limit=1)
            self.assertEqual(result["tasks"][0]["batch"]["capacity"], size)
            self.assertEqual(len(result["tasks"]), 1)
            self.assertTrue(result["remaining_step_ids"])

    def test_duplicate_ids_or_dependency_cycles_rejected(self):
        config = copy.deepcopy(self.config)
        config["steps"][1]["id"] = config["steps"][0]["id"]
        with self.assertRaises(ValueError):
            validate_workflow(config, self.policy)
        config = copy.deepcopy(self.config)
        config["steps"][0]["dependsOn"] = [config["steps"][-1]["id"]]
        with self.assertRaises(ValueError):
            validate_workflow(config, self.policy)

    def test_task_identity_is_reproducible_and_input_bound(self):
        kwargs = dict(step_ids=["F4-review"], run_id="review-001", parent_release_id="parent-A", config_sha256="aaa")
        a = build_plan(self.config, self.policy, **kwargs)
        self.assertEqual(a, build_plan(self.config, self.policy, **kwargs))
        kwargs["parent_release_id"] = "parent-B"
        b = build_plan(self.config, self.policy, **kwargs)
        self.assertNotEqual(a["tasks"][0]["task_id"], b["tasks"][0]["task_id"])

    def test_cli_from_empty_directory_only_prints_unexecuted_plan(self):
        script = CONFIG.parents[1] / "rsi_harness/workflow_plan_v3.py"
        config_hash = hashlib.sha256(CONFIG.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(script), "--step", "F8-preflight", "--limit", "1"],
                                    cwd=directory, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertFalse(payload["commands_executed"])
            self.assertFalse(payload["data_modified"])
            self.assertEqual(payload["config_sha256"], config_hash)
            self.assertEqual(list(Path(directory).iterdir()), [])
        self.assertEqual(hashlib.sha256(CONFIG.read_bytes()).hexdigest(), config_hash)

    def test_cli_invalid_contract_or_batch_returns_nonzero(self):
        script = CONFIG.parents[1] / "rsi_harness/workflow_plan_v3.py"
        with tempfile.TemporaryDirectory() as directory:
            bad = Path(directory) / "bad.json"
            bad.write_text('{"steps": []}')
            for args in (["--config", str(bad), "--validate"], ["--batch-size", "500"]):
                result = subprocess.run([sys.executable, str(script)] + args, cwd=directory, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2)
                self.assertIn("workflow plan error:", result.stderr)


if __name__ == "__main__":
    unittest.main()
