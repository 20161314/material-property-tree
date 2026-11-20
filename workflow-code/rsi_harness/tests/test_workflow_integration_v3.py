"""End-to-end synthetic records only: no real source approval or model calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_data_v3 import example_bundle, recompute
from workflow_plan_v3 import CONFIG
from workflow_runtime_v3 import freeze, digest


class IntegrationTests(unittest.TestCase):
    def test_collection_independent_review_merge_state_and_resume(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "synthetic.json"
            source.write_text(json.dumps({"fixture_only": True}))
            run = freeze(root / "run", project_root=root, run_id="fixture", parent_release_id="fixture-parent",
                         inputs={"source": source}, workflow=json.loads(CONFIG.read_text()), bundle=example_bundle())
            try:
                records = [{"record_id": "fixture-material", "source_locator": "synthetic:1"}]
                run.enqueue("F5-normalize", records, "fixture-source-curator", route="ordinary")
                task = run.claim("fixture-collector", now=100)
                def dispatch(task, call, agent):
                    receipt = {key: task[key] for key in ("task_id", "attempt", "run_id", "epoch", "parent_release_id", "candidate_sha256", "reviewer", "model", "reasoning_effort")}
                    receipt.update(host_call_id=call, agent_id=agent, lease_sha256=digest(task["lease_token"]))
                    run.record_dispatch(task["task_id"], task["lease_token"], receipt, now=task["lease_until"] - 899)
                dispatch(task, "fixture-collection-call", "fixture-collector-agent")
                candidate = {"worker": task["reviewer"], "candidate_sha256": task["candidate_sha256"],
                             "input_sha256": task["input_sha256"], "host_call_id": "fixture-collection-call",
                             "results": [{"record_id": "fixture-material", "source_locator": "synthetic:1", "outcome": "CANDIDATE",
                                          "reason": "Synthetic integration fixture, no material claim", "operations": [
                                              {"table": "materials", "id": "fixture-new", "before_sha256": None, "action": "upsert",
                                               "value": {"material_id": "fixture-new", "name_zh": "测试材料", "scope": "solid"}}]}]}
                run.submit_candidate(task["task_id"], task["lease_token"], candidate, now=102)
                self.assertNotIn("fixture-new", {r["material_id"] for r in run.bundle()["materials"]})
                run.enqueue_review(task["task_id"], "F5-review")
                review_task = run.claim("fixture-independent-reviewer", now=103)
                self.assertEqual(review_task["collector"], "fixture-collector-agent")
                dispatch(review_task, "fixture-review-call", "fixture-review-agent")
                review = {"reviewer": review_task["reviewer"], "candidate_sha256": review_task["candidate_sha256"],
                          "input_sha256": review_task["input_sha256"], "host_call_id": "fixture-review-call",
                          "decisions": [{"record_id": "fixture-material", "decision": "PASS", "reason": "Synthetic input verified", "source_locator": "synthetic:1"}]}
                run.submit_review(review_task["task_id"], review_task["lease_token"], review, now=105)
                merged = run.merge([review_task["task_id"]], actor="fixture-merger", expected_parent="fixture-parent")
                self.assertEqual(merged["operations"], 1)
                state = next(r for r in recompute(run.bundle())["material_states"] if r["material_id"] == "fixture-new")
                self.assertEqual(state["state"], "S4")
                tasks = run.frontier()
                first = tasks[0]
                run.frontier(complete=[(first["material_id"], first["revision"])])
                self.assertNotIn(first["material_id"], {r["material_id"] for r in run.frontier()})
                before = run.checkpoint()
                run.close()
                from workflow_runtime_v3 import Run
                run = Run(root / "run")
                self.assertEqual(before, run.checkpoint())
            finally:
                run.close()


if __name__ == "__main__":
    unittest.main()
