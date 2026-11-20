import csv
import json
import tempfile
import unittest
from pathlib import Path

from release_gate_v24 import _pointer_release_id, audit_evidence, audit_object_table, audit_option_table, run_gate, verify_input_pins


class ReleaseGateV24Tests(unittest.TestCase):
    def test_pointer_parser_rejects_missing_release_id(self):
        with tempfile.TemporaryDirectory() as td:
            pointer = Path(td) / "current_release_pointer.md"
            pointer.write_text("# no release here\n", encoding="utf-8")
            self.assertIsNone(_pointer_release_id(pointer))
            pointer.write_text("release: rel-1234\n", encoding="utf-8")
            self.assertEqual(_pointer_release_id(pointer), "rel-1234")
            pointer.write_text("release `rel-5678`\n", encoding="utf-8")
            self.assertEqual(_pointer_release_id(pointer), "rel-5678")
            pointer.write_text("release: rel-1234\nprevious release: rel-5678\n", encoding="utf-8")
            self.assertIsNone(_pointer_release_id(pointer))

    def test_input_pins_reject_paths_outside_project_root(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "project"
            root.mkdir()
            outside = Path(td) / "outside.csv"
            outside.write_text("pinned elsewhere", encoding="utf-8")
            (root / "linked.csv").symlink_to(outside)
            summary = {"input_sha256": {
                "../outside.csv": "not-a-project-input",
                str(outside): "not-a-project-input",
                "linked.csv": "not-a-project-input",
            }}
            metrics, errors = verify_input_pins(root, summary)
            self.assertEqual(metrics["unsafe"], 3)
            self.assertIn("INPUT_PIN_PATH_OUTSIDE_ROOT", {error["code"] for error in errors})

    def test_malformed_input_pin_container_returns_a_structured_error(self):
        with tempfile.TemporaryDirectory() as td:
            metrics, errors = verify_input_pins(Path(td), {"input_sha256": []})
            self.assertEqual(metrics["undeclared"], 10)
            self.assertIn("INPUT_PINS_INVALID", {error["code"] for error in errors})
    def test_object_queue_is_explicit_and_deterministic(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "objects.csv"
            fields = [
                "object_id", "component_id", "source_dataset", "source_asset_id",
                "object_name_en", "object_name_cn", "component_scope", "material_node_id",
                "material_label", "material_identity_status", "mapping_source_ids",
                "mapping_evidence", "asset_status", "source_record_locator",
            ]
            row = {k: "x" for k in fields}
            row.update({"object_id": "o1", "component_id": "c1", "source_dataset": "GoogleResearch Scanned Objects (official Fuel release)",
                        "material_node_id": "", "material_label": "NOT_REPORTED_IN_MANIFEST"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors, queue = audit_object_table(path, {"state_rows": 1, "object_identities": 1, "distinct_component_pairs": 1})
            self.assertEqual(metrics["missing_material_node_rows"], 1)
            self.assertEqual(queue[0]["reason_code"], "SOURCE_MANIFEST_NO_MATERIAL")
            self.assertTrue(queue[0]["queue_id"].startswith("MATERIAL-MAP-"))
            self.assertFalse(any(e["code"] == "OBJECT_REQUIRED_FIELD_BLANK" for e in errors))

    def test_evidence_count_drift_is_blocking(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator", "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3"]
            row = {k: "x" for k in fields}
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 2, "main_complete_groups": 1, "main_partial_groups": 1})
            self.assertEqual(metrics["rows"], 1)
            self.assertTrue(any(e["code"] == "EVIDENCE_ROW_COUNT_DRIFT" for e in errors))

    def test_complete_group_rejects_solver_or_model_origin(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator", "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3", "source_is_model_or_solver_input"]
            row = {k: "x" for k in fields}
            row.update({"E_low_GPa": "1", "nu_low": "0.3", "rho_low_kg_m3": "1000", "source_is_model_or_solver_input": "YES"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 1, "main_partial_groups": 0})
            self.assertEqual(metrics["complete_disallowed_origin"], 1)
            self.assertTrue(any(e["code"] == "COMPLETE_EVIDENCE_DISALLOWED_ORIGIN" for e in errors))

    def test_partial_group_rejects_model_generated_property(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator",
                      "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low",
                      "rho_low_kg_m3", "source_is_model_or_solver_input"]
            row = {k: "source" for k in fields}
            row.update({"E_low_GPa": "1", "nu_low": "", "rho_low_kg_m3": "",
                        "source_is_model_or_solver_input": "YES"})
            with path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader(); writer.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 0, "main_partial_groups": 1})
            self.assertEqual(metrics["partial_disallowed_origin"], 1)
            self.assertIn("PARTIAL_EVIDENCE_DISALLOWED_ORIGIN", {error["code"] for error in errors})

    def test_partial_group_requires_traceable_material_source(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator",
                      "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3"]
            row = {k: "source" for k in fields}
            row.update({"material_identity": "", "source_id": "", "document_key": "", "url": "",
                        "locator": "", "local_file": "", "sha256": "", "E_low_GPa": "1",
                        "nu_low": "", "rho_low_kg_m3": ""})
            with path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader(); writer.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 0, "main_partial_groups": 1})
            self.assertEqual(metrics["partial_missing_provenance"], 1)
            self.assertIn("PARTIAL_EVIDENCE_MISSING_PROVENANCE", {error["code"] for error in errors})

    def test_partial_source_excerpt_is_checked_for_provenance_and_disallowed_origin(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator",
                      "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3",
                      "E_source_value", "source_is_model_or_solver_input"]
            row = {k: "source" for k in fields}
            row.update({"source_id": "", "E_low_GPa": "", "nu_low": "", "rho_low_kg_m3": "",
                        "E_source_value": "E = 2.4 GPa", "source_is_model_or_solver_input": "MODEL_GENERATED"})
            with path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader(); writer.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 0, "main_partial_groups": 1})
            self.assertEqual(metrics["partial_without_numeric_normalization"], 1)
            self.assertEqual(metrics["partial_missing_provenance"], 1)
            self.assertEqual(metrics["partial_disallowed_origin"], 1)
            codes = {error["code"] for error in errors}
            self.assertIn("PARTIAL_EVIDENCE_MISSING_PROVENANCE", codes)
            self.assertIn("PARTIAL_EVIDENCE_DISALLOWED_ORIGIN", codes)

    def test_evidence_group_without_any_property_value_is_blocked(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator",
                      "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3",
                      "E_source_value", "nu_source_value", "rho_source_value"]
            row = {k: "source" for k in fields}
            row.update({k: "" for k in ("E_low_GPa", "nu_low", "rho_low_kg_m3",
                                         "E_source_value", "nu_source_value", "rho_source_value")})
            with path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader(); writer.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 0, "main_partial_groups": 1})
            self.assertEqual(metrics["empty_property_rows"], 1)
            self.assertIn("EVIDENCE_GROUP_WITHOUT_PROPERTY_VALUE", {error["code"] for error in errors})

    def test_partial_group_allows_explicit_not_simulation_input_note(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator",
                      "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low",
                      "rho_low_kg_m3", "source_parameter_validity"]
            row = {k: "source" for k in fields}
            row.update({"E_low_GPa": "1", "nu_low": "", "rho_low_kg_m3": "",
                        "source_parameter_validity": "RESEARCH_SOURCE_MEASUREMENT_WITH_REPORTED_LIMITATIONS_NOT_VALIDATED_SIMULATION_INPUT"})
            with path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=fields); writer.writeheader(); writer.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 0, "main_partial_groups": 1})
            self.assertEqual(metrics["partial_disallowed_origin"], 0)
            self.assertFalse(any(error["code"] == "PARTIAL_EVIDENCE_DISALLOWED_ORIGIN" for error in errors))

    def test_complete_group_rejects_nonpositive_modulus_or_density(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator", "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3"]
            row = {k: "x" for k in fields}
            row.update({"E_low_GPa": "0", "nu_low": "0.3", "rho_low_kg_m3": "1000"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 1, "main_partial_groups": 0})
            self.assertEqual(metrics["complete_invalid_numeric"], 1)
            self.assertTrue(any(e["code"] == "COMPLETE_EVIDENCE_INVALID_NUMERIC" for e in errors))

    def test_complete_group_rejects_malformed_high_bound(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "evidence.csv"
            fields = ["record_id", "material_identity", "source_id", "document_key", "url", "locator", "local_file", "sha256", "unique_record_key", "E_low_GPa", "E_high_GPa", "nu_low", "rho_low_kg_m3"]
            row = {k: "x" for k in fields}
            row.update({"E_low_GPa": "1", "E_high_GPa": "bad", "nu_low": "0.3", "rho_low_kg_m3": "1000"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_evidence(path, {"main_source_groups": 1, "main_complete_groups": 1, "main_partial_groups": 0})
            self.assertEqual(metrics["complete_invalid_numeric"], 1)
            self.assertTrue(any(e["code"] == "EVIDENCE_INVALID_NUMERIC" for e in errors))

    def test_option_projection_checks_foreign_keys_and_pairs(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "options.csv"
            fields = ["assignment_id", "source_row_id", "object_id", "component_id", "source_family", "source_asset_id", "assigned_material_id", "assignment_relation", "assignment_option_group_id", "option_position", "assignment_basis", "original_admission_status", "source_record_locator"]
            row = {k: "x" for k in fields}
            row.update({"assignment_id": "a1", "object_id": "o1", "component_id": "c1", "assigned_material_id": "MISSING",
                        "assignment_relation": "SINGLE_ASSIGNMENT", "assignment_option_group_id": "", "option_position": "1"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_option_table(path, {"current_material_option_rows": 1}, {("o2", "c2")}, {"MAT-REAL"})
            self.assertEqual(metrics["orphan_object_component_rows"], 1)
            self.assertEqual(metrics["orphan_material_rows"], 1)
            codes = {e["code"] for e in errors}
            self.assertIn("OPTION_ORPHAN_OBJECT_COMPONENT", codes)
            self.assertIn("OPTION_ORPHAN_MATERIAL_REFERENCE", codes)

    def test_empty_space_special_domain_is_not_a_material_foreign_key_error(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "options.csv"
            fields = ["assignment_id", "source_row_id", "object_id", "component_id", "source_family", "source_asset_id", "assigned_material_id", "assignment_relation", "assignment_option_group_id", "option_position", "assignment_basis", "original_admission_status", "source_record_locator"]
            row = {k: "x" for k in fields}
            row.update({"assignment_id": "a1", "object_id": "o1", "component_id": "c1",
                        "assigned_material_id": "SPECIAL-DOMAIN-VOID", "assignment_relation": "SINGLE_ASSIGNMENT",
                        "assignment_option_group_id": "", "option_position": "1"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors = audit_option_table(path, {"current_material_option_rows": 1}, {("o1", "c1")}, {"MAT-REAL"})
            self.assertEqual(metrics["orphan_material_rows"], 0)
            self.assertEqual(errors, [])

    def test_unmapped_sentinel_is_not_a_material_foreign_key(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "objects.csv"
            fields = [
                "object_id", "component_id", "source_dataset", "source_asset_id",
                "object_name_en", "object_name_cn", "component_scope", "material_node_id",
                "material_label", "material_identity_status", "mapping_source_ids",
                "mapping_evidence", "asset_status", "source_record_locator",
            ]
            row = {k: "x" for k in fields}
            row.update({"object_id": "o1", "component_id": "c1", "material_node_id": "UNMAPPED"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors, queue = audit_object_table(
                path, {"state_rows": 1, "object_identities": 1, "distinct_component_pairs": 1},
                known_material_ids={"MAT-REAL"}, excluded_material_ids=set()
            )
            self.assertEqual(metrics["missing_material_node_rows"], 1)
            self.assertEqual(queue[0]["reason_code"], "MATERIAL_NODE_SENTINEL_UNMAPPED")
            self.assertEqual(queue[0]["material_node_id"], "UNMAPPED")

    def test_orphan_material_reference_is_queued(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "objects.csv"
            fields = [
                "object_id", "component_id", "source_dataset", "source_asset_id",
                "object_name_en", "object_name_cn", "component_scope", "material_node_id",
                "material_label", "material_identity_status", "mapping_source_ids",
                "mapping_evidence", "asset_status", "source_record_locator",
            ]
            row = {k: "x" for k in fields}
            row.update({"object_id": "o1", "component_id": "c1", "material_node_id": "MAT-NOT-IN-TABLE"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors, queue = audit_object_table(
                path, {"state_rows": 1, "object_identities": 1, "distinct_component_pairs": 1},
                known_material_ids={"MAT-REAL"}, excluded_material_ids=set()
            )
            self.assertEqual(metrics["missing_material_node_rows"], 1)
            self.assertEqual(queue[0]["reason_code"], "ORPHAN_MATERIAL_NODE_REFERENCE")

    def test_physx_empty_space_is_special_domain_history(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "objects.csv"
            fields = [
                "object_id", "component_id", "source_dataset", "source_asset_id",
                "object_name_en", "object_name_cn", "component_scope", "material_node_id",
                "material_label", "component_material_label_raw", "material_candidate_raw",
                "material_identity_status", "mapping_source_ids", "mapping_evidence",
                "asset_status", "source_record_locator",
            ]
            row = {k: "x" for k in fields}
            row.update({"object_id": "o1", "component_id": "c1", "source_dataset": "PHYSX-MOBILITY",
                        "material_node_id": "UNMAPPED", "material_label": "N/A (Empty Space)"})
            with path.open("w", newline="", encoding="utf-8") as out:
                w = csv.DictWriter(out, fieldnames=fields); w.writeheader(); w.writerow(row)
            metrics, errors, queue = audit_object_table(
                path, {"state_rows": 1, "object_identities": 1, "distinct_component_pairs": 1},
                known_material_ids={"MAT-REAL"}, excluded_material_ids=set()
            )
            self.assertEqual(metrics["special_domain_rows"], 1)
            self.assertEqual(metrics["missing_material_node_rows"], 0)
            self.assertEqual(queue, [])

    def test_gate_blocks_known_incomplete_release(self):
        root = Path(__file__).resolve().parents[1]
        result = run_gate(root)
        self.assertEqual(result["status"], "BLOCKED_RSI_V24_RELEASE_GATE")
        codes = {e["code"] for e in result["errors"]}
        self.assertIn("UNRESOLVED_MATERIAL_MAPPING_QUEUE", codes)
        self.assertIn("RELEASE_COMPLETENESS_FLAG_FALSE", codes)


if __name__ == "__main__":
    unittest.main()
