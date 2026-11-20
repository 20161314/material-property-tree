"""Independent acceptance regressions; temporary synthetic inputs, no model calls."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_plan_v3 import CONFIG
from workflow_runtime_v3 import file_sha, freeze


class AcceptanceRegressions(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.source = root / "private-inputs/source.json"
        self.source.parent.mkdir()
        self.source.write_text('{"value":1}')
        index = root / "INDEX.json"
        index.write_text(json.dumps({"schema": "rsi-site-review-packet-index-v3", "packets": [],
                                    "private_inputs": {"private-inputs/source.json": file_sha(self.source)}}))
        bundle = {table: [] for table in ("objects", "components", "materials", "relations", "taxonomy", "evidence")}
        self.run = freeze(root / "run", project_root=root, run_id="acceptance", parent_release_id="parent",
                          inputs={"index": index}, workflow=json.loads(CONFIG.read_text()), bundle=bundle)
        self.addCleanup(self.run.close)
        self.record = {"record_id": "synthetic-record", "source_locator": "synthetic:1",
                       "input_locators": ["private-inputs/source.json#/value"], "operations": [
                           {"table": "materials", "id": "synthetic-added", "before_sha256": None,
                            "action": "upsert", "value": {"material_id": "synthetic-added", "scope": "solid"}}]}

    def dispatched(self, step="F4-review", route="bulk_review"):
        self.run.enqueue(step, [self.record], "source-collector", route=route)
        handoff = self.run.claim("task-owner", now=100)
        receipt = dict(handoff["dispatch_bindings"], host_call_id="synthetic-call", agent_id="actual-model-agent")
        self.run.record_dispatch(handoff["task_id"], handoff["lease_token"], receipt, now=101)
        return handoff

    def review(self, handoff):
        return {"reviewer": "task-owner", "candidate_sha256": handoff["candidate_sha256"],
                "input_sha256": handoff["input_sha256"], "host_call_id": "synthetic-call",
                "decisions": [{"record_id": self.record["record_id"], "decision": "PASS",
                               "reason": "Synthetic boundary test only", "source_locator": "synthetic:1"}]}

    def change_source(self):
        self.source.write_text('{"value":999}')

    def test_changed_private_source_blocks_candidate_submission(self):
        handoff = self.dispatched("F5-normalize", "ordinary")
        candidate = {"worker": "task-owner", "candidate_sha256": handoff["candidate_sha256"],
                     "input_sha256": handoff["input_sha256"], "host_call_id": "synthetic-call",
                     "results": [{"record_id": self.record["record_id"], "source_locator": "synthetic:1",
                                  "outcome": "CANDIDATE", "reason": "Synthetic test", "operations": self.record["operations"]}]}
        self.change_source()
        with self.assertRaisesRegex(ValueError, "source SHA mismatch"):
            self.run.submit_candidate(handoff["task_id"], handoff["lease_token"], candidate, now=102)

    def test_changed_private_source_blocks_review_submission(self):
        handoff = self.dispatched()
        self.change_source()
        with self.assertRaisesRegex(ValueError, "source SHA mismatch"):
            self.run.submit_review(handoff["task_id"], handoff["lease_token"], self.review(handoff), now=102)

    def test_changed_private_source_blocks_merge_and_preserves_parent(self):
        handoff = self.dispatched()
        self.run.submit_review(handoff["task_id"], handoff["lease_token"], self.review(handoff), now=102)
        self.change_source()
        with self.assertRaisesRegex(ValueError, "source SHA mismatch"):
            self.run.merge([handoff["task_id"]], actor="independent-merger", expected_parent="parent")
        self.assertEqual(self.run.meta("current_release"), "parent")
        self.assertEqual(self.run.bundle()["materials"], [])

    def test_actual_review_agent_cannot_merge_through_a_different_owner_name(self):
        handoff = self.dispatched()
        self.run.submit_review(handoff["task_id"], handoff["lease_token"], self.review(handoff), now=102)
        with self.assertRaisesRegex(ValueError, "Merger must be independent"):
            self.run.merge([handoff["task_id"]], actor="actual-model-agent", expected_parent="parent")
        self.assertEqual(self.run.meta("current_release"), "parent")


if __name__ == "__main__":
    unittest.main()
