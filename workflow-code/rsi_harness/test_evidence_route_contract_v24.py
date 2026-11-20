import json
import tempfile
import unittest
from pathlib import Path

from evidence_route_contract_v24 import run_route_contract


class EvidenceRouteContractV24Tests(unittest.TestCase):
    def test_missing_route_files_block(self):
        with tempfile.TemporaryDirectory() as td:
            result = run_route_contract(Path(td))
        self.assertEqual(result["status"], "BLOCKED_RSI_EVIDENCE_ROUTE_CONTRACT")
        self.assertIn("EVIDENCE_ROUTE_REQUIRED_FILE_MISSING", {e["code"] for e in result["errors"]})

    def test_current_route_registry_passes(self):
        root = Path(__file__).resolve().parents[1]
        result = run_route_contract(root)
        self.assertEqual(result["status"], "PASS_RSI_EVIDENCE_ROUTE_CONTRACT")
        self.assertEqual(result["metrics"]["route_rows"], 21)


if __name__ == "__main__":
    unittest.main()
