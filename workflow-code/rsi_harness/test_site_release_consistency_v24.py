import json
import tempfile
import unittest
from pathlib import Path

from site_release_consistency_v24 import pointer_release_id, run_preflight, sha256


class SiteReleaseConsistencyV24Tests(unittest.TestCase):
    def test_pointer_parser_rejects_ambiguous_ids(self):
        with tempfile.TemporaryDirectory() as td:
            pointer = Path(td) / "current_release_pointer.md"
            pointer.write_text("release: rel-1234\nrelease `rel-5678`\n", encoding="utf-8")
            self.assertIsNone(pointer_release_id(pointer))

    def test_manifest_cannot_pin_a_file_outside_project_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data/current_two_table_delivery_v1").mkdir(parents=True)
            (root / "site_v3").mkdir()
            (root / "audit/rsi_framework_review_2026-11-15").mkdir(parents=True)
            summary = {"object_identities": 1, "distinct_component_pairs": 1, "state_rows": 1,
                       "material_nodes": 1, "main_complete_groups": 1, "main_partial_groups": 0}
            (root / "data/current_two_table_delivery_v1/summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (root / "current_release_pointer.md").write_text("release: same\n", encoding="utf-8")
            (root / "audit/rsi_framework_review_2026-11-15/rsi_v24_release_gate.json").write_text(
                json.dumps({"status": "BLOCKED_RSI_V24_RELEASE_GATE"}), encoding="utf-8")
            status = {"release_id": "same", "object_identities": 1, "distinct_object_component_pairs": 1,
                      "component_status_rows": 1, "material_labels": 1, "main_complete": 1, "main_partial": 0}
            (root / "site_v3/release-status.json").write_text(json.dumps(status), encoding="utf-8")
            manifest = {"id": "same", "inputs": {"../outside.csv": "irrelevant"},
                        "objects": {"total": 1, "components": 1, "rows": 1}, "materials": {"total": 1},
                        "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = {"id": "same", "objects": {"total": 1, "components": 1, "rows": 1},
                    "materials": {"total": 1}, "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-data.js").write_text(
                "window.DATASET_RELEASE = " + json.dumps(data) + ";\n", encoding="utf-8")
            result = run_preflight(root)
            self.assertIn("SITE_MANIFEST_INPUT_PATH_OUTSIDE_ROOT", {error["code"] for error in result["errors"]})

    def test_mismatched_release_ids_and_blocked_gate_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data/current_two_table_delivery_v1").mkdir(parents=True)
            (root / "site_v3").mkdir()
            (root / "audit/rsi_framework_review_2026-11-15").mkdir(parents=True)
            summary = {
                "object_identities": 1, "distinct_component_pairs": 1, "state_rows": 1,
                "material_nodes": 1, "main_complete_groups": 1, "main_partial_groups": 0,
            }
            (root / "data/current_two_table_delivery_v1/summary.json").write_text(json.dumps(summary), encoding="utf-8")
            (root / "current_release_pointer.md").write_text("# release: r-current\n", encoding="utf-8")
            (root / "audit/rsi_framework_review_2026-11-15/rsi_v24_release_gate.json").write_text(json.dumps({"status": "BLOCKED_RSI_V24_RELEASE_GATE"}), encoding="utf-8")
            site_status = {"release_id": "r-site", "object_identities": 1, "distinct_object_component_pairs": 1, "component_status_rows": 1, "material_labels": 1, "main_complete": 1, "main_partial": 0}
            (root / "site_v3/release-status.json").write_text(json.dumps(site_status), encoding="utf-8")
            (root / "site_v3/release-manifest.json").write_text(json.dumps({"id": "r-site", "inputs": {"data/current_two_table_delivery_v1/summary.json": "bad"}}), encoding="utf-8")
            data = {"id": "r-site", "objects": {"total": 1, "components": 1, "rows": 1}, "materials": {"total": 1}, "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-data.js").write_text("window.DATASET_RELEASE = " + json.dumps(data) + ";\n", encoding="utf-8")
            result = run_preflight(root)
            codes = {e["code"] for e in result["errors"]}
            self.assertEqual(result["status"], "BLOCKED_SITE_RELEASE_CONSISTENCY")
            self.assertIn("SITE_RELEASE_ID_MISMATCH", codes)
            self.assertIn("SITE_SUMMARY_INPUT_PIN_MISMATCH", codes)
            self.assertIn("RSI_GATE_BLOCKED_SITE_PUBLICATION", codes)

    def test_manifest_input_contract_and_manifest_counts_are_checked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data/current_two_table_delivery_v1").mkdir(parents=True)
            (root / "site_v3").mkdir()
            (root / "audit/rsi_framework_review_2026-11-15").mkdir(parents=True)
            summary = {
                "object_identities": 1, "distinct_component_pairs": 1, "state_rows": 1,
                "material_nodes": 1, "main_complete_groups": 1, "main_partial_groups": 0,
            }
            summary_path = root / "data/current_two_table_delivery_v1/summary.json"
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            (root / "current_release_pointer.md").write_text("# release: same\n", encoding="utf-8")
            (root / "audit/rsi_framework_review_2026-11-15/rsi_v24_release_gate.json").write_text(
                json.dumps({"status": "PASS_RSI_V24_RELEASE_GATE"}), encoding="utf-8")
            status = {"release_id": "same", "object_identities": 1,
                      "distinct_object_component_pairs": 1, "component_status_rows": 1,
                      "material_labels": 1, "main_complete": 1, "main_partial": 0}
            (root / "site_v3/release-status.json").write_text(json.dumps(status), encoding="utf-8")
            manifest = {
                "id": "same",
                "inputs": {str(summary_path.relative_to(root)): "bad"},
                "objects": {"total": 99, "components": 1, "rows": 1},
                "materials": {"total": 1},
                "records": {"main": {"complete": 1, "incomplete": 0}},
            }
            (root / "site_v3/release-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = {"id": "same", "objects": {"total": 1, "components": 1, "rows": 1},
                    "materials": {"total": 1}, "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-data.js").write_text(
                "window.DATASET_RELEASE = " + json.dumps(data) + ";\n", encoding="utf-8")
            result = run_preflight(root)
            codes = {e["code"] for e in result["errors"]}
            self.assertIn("SITE_MANIFEST_INPUT_PIN_MISMATCH", codes)
            self.assertIn("SITE_MANIFEST_COUNT_MISMATCH", codes)

    def test_preflight_can_read_the_gate_report_from_this_run(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "data/current_two_table_delivery_v1").mkdir(parents=True)
            (root / "site_v3").mkdir()
            (root / "audit/rsi_framework_review_2026-11-15").mkdir(parents=True)
            summary = {"object_identities": 1, "distinct_component_pairs": 1, "state_rows": 1,
                       "material_nodes": 1, "main_complete_groups": 1, "main_partial_groups": 0}
            summary_path = root / "data/current_two_table_delivery_v1/summary.json"
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            (root / "current_release_pointer.md").write_text("# release: same\n", encoding="utf-8")
            old_gate = root / "audit/rsi_framework_review_2026-11-15/rsi_v24_release_gate.json"
            old_gate.write_text(json.dumps({"status": "BLOCKED_RSI_V24_RELEASE_GATE"}), encoding="utf-8")
            current_gate = root / "gate-this-run.json"
            current_gate.write_text(json.dumps({"status": "PASS_RSI_V24_RELEASE_GATE"}), encoding="utf-8")
            status = {"release_id": "same", "object_identities": 1, "distinct_object_component_pairs": 1,
                      "component_status_rows": 1, "material_labels": 1, "main_complete": 1, "main_partial": 0}
            (root / "site_v3/release-status.json").write_text(json.dumps(status), encoding="utf-8")
            manifest = {"id": "same", "inputs": {"data/current_two_table_delivery_v1/summary.json": sha256(summary_path)},
                        "objects": {"total": 1, "components": 1, "rows": 1}, "materials": {"total": 1},
                        "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            data = {"id": "same", "objects": {"total": 1, "components": 1, "rows": 1},
                    "materials": {"total": 1}, "records": {"main": {"complete": 1, "incomplete": 0}}}
            (root / "site_v3/release-data.js").write_text("window.DATASET_RELEASE = " + json.dumps(data) + ";\n", encoding="utf-8")
            result = run_preflight(root, current_gate)
            self.assertNotIn("RSI_GATE_BLOCKED_SITE_PUBLICATION", {e["code"] for e in result["errors"]})


if __name__ == "__main__":
    unittest.main()
