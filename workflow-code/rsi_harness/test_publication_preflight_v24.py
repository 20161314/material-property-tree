import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publication_preflight_v24 import run_publication_preflight


class PublicationPreflightV24Tests(unittest.TestCase):
    def test_any_blocked_gate_blocks_combined_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            queue = root / "queue.csv"
            gate_out = root / "gate.json"
            site_out = root / "site.json"
            with patch("publication_preflight_v24.run_gate", return_value={"status": "BLOCKED_RSI_V24_RELEASE_GATE"}), \
                 patch("publication_preflight_v24.run_site_preflight", return_value={"status": "PASS_SITE_RELEASE_CONSISTENCY"}):
                result = run_publication_preflight(root, queue, gate_out, site_out)
            self.assertEqual(result["status"], "BLOCKED_RSI_V24_PUBLICATION_PREFLIGHT")
            self.assertTrue(gate_out.is_file())
            self.assertTrue(site_out.is_file())
            self.assertEqual(json.loads(gate_out.read_text())["status"], "BLOCKED_RSI_V24_RELEASE_GATE")

    def test_both_gates_must_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch("publication_preflight_v24.run_gate", return_value={"status": "PASS_RSI_V24_RELEASE_GATE"}), \
                 patch("publication_preflight_v24.run_site_preflight", return_value={"status": "PASS_SITE_RELEASE_CONSISTENCY"}):
                result = run_publication_preflight(root, root / "q.csv", root / "g.json", root / "s.json")
            self.assertEqual(result["status"], "PASS_RSI_V24_PUBLICATION_PREFLIGHT")

    def test_preflight_reports_the_release_gate_rules_version(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch("publication_preflight_v24.run_gate", return_value={
                "status": "PASS_RSI_V24_RELEASE_GATE", "rules_version": "2.4.3-H4",
            }), patch("publication_preflight_v24.run_site_preflight", return_value={
                "status": "PASS_SITE_RELEASE_CONSISTENCY",
            }):
                result = run_publication_preflight(root, root / "q.csv", root / "g.json", root / "s.json")
            self.assertEqual(result["rules_version"], "2.4.3-H4")

    def test_relative_outputs_are_rooted_under_release_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with patch("publication_preflight_v24.run_gate", return_value={"status": "BLOCKED_RSI_V24_RELEASE_GATE"}), \
                 patch("publication_preflight_v24.run_site_preflight", return_value={"status": "BLOCKED_SITE_RELEASE_CONSISTENCY"}):
                result = run_publication_preflight(root, Path("out/q.csv"), Path("out/g.json"), Path("out/s.json"))
            root = root.resolve()
            self.assertEqual(result["gate_report"], str(root / "out/g.json"))
            self.assertEqual(result["site_report"], str(root / "out/s.json"))
            self.assertEqual(result["queue"], str(root / "out/q.csv"))


if __name__ == "__main__":
    unittest.main()
