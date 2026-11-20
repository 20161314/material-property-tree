import json
import tempfile
import unittest
from pathlib import Path

from workflow_contract_v24 import _parent_graph_issues, run_workflow_contract


class WorkflowContractV24Tests(unittest.TestCase):
    def test_parent_cycle_is_rejected(self):
        rows = [
            {"material_id": "A", "parent_id": "B"},
            {"material_id": "B", "parent_id": "A"},
        ]
        codes = {e["code"] for e in _parent_graph_issues(rows)}
        self.assertIn("MATERIAL_TREE_CYCLE", codes)

    def test_parent_orphan_is_rejected(self):
        rows = [{"material_id": "A", "parent_id": "MISSING"}]
        codes = {e["code"] for e in _parent_graph_issues(rows)}
        self.assertIn("MATERIAL_PARENT_ORPHAN", codes)

    def test_missing_required_file_blocks_contract(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_workflow_contract(Path(td))
        self.assertEqual(result["status"], "BLOCKED_RSI_WORKFLOW_CONTRACT")
        self.assertIn("WORKFLOW_REQUIRED_FILE_MISSING", {e["code"] for e in result["errors"]})

    def test_option_table_is_required(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_workflow_contract(Path(td))
        missing = [e for e in result["errors"] if e["code"] == "WORKFLOW_REQUIRED_FILE_MISSING"]
        self.assertTrue(any("options" in e["message"] for e in missing))



if __name__ == "__main__":
    unittest.main()
