import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADAPTER_PATH = ROOT / "audit/rsi_framework_review_2026-11-15/reconcile_cycle5_to_current.py"
SPEC = importlib.util.spec_from_file_location("cycle5_reconciliation_adapter", ADAPTER_PATH)
ADAPTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ADAPTER)


class Cycle5ReconciliationAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = [row for path in ADAPTER.SOURCE_FILES for row in ADAPTER.read_csv(path)]
        cls.targets = ADAPTER.read_csv(ADAPTER.TARGET_FILE)

    def test_frozen_cycle5_delta_maps_to_current_c41(self):
        rows, metrics = ADAPTER.build_crosswalk(self.sources, self.targets)
        self.assertEqual(len(rows), 88)
        self.assertEqual(metrics["mapped_source_ids"], 88)
        self.assertEqual(metrics["unique_target_locators"], 88)
        self.assertEqual(sum(row["mapping_kind"] == "EXACT_ID" for row in rows), 28)
        self.assertEqual(sum(row["mapping_kind"] == "AGGREGATED_SUBRESULT" for row in rows), 60)
        self.assertEqual(len({
            row["target_record_id"] for row in rows
            if row["mapping_kind"] == "AGGREGATED_SUBRESULT"
        }), 15)

    def test_changed_nested_measurement_is_detected(self):
        source = next(row for row in self.sources
                      if row["record_id"] == "SC5-PMC10725245-T4-R001")
        targets = [dict(row) for row in self.targets]
        target = next(row for row in targets
                      if row["record_id"] == "C6-GROUP-04E50F8EB2E636823A11")
        citations = json.loads(target["property_citations_json"])
        citations["E"]["observations"][0]["median_MPa"] = "1.488"
        target["property_citations_json"] = json.dumps(citations)
        with self.assertRaisesRegex(ValueError, "expected one exact"):
            ADAPTER.find_subresult(
                source,
                [row for row in targets if row.get("source_id") == "PMC10725245"
                 and "Table4" in row.get("locator", "")
                 and row.get("property_citations_json")],
            )

    def test_changed_shared_testing_conditions_are_detected(self):
        source = next(row for row in self.sources
                      if row["record_id"] == "SC5-PMC10725245-T4-R001")
        targets = [dict(row) for row in self.targets]
        target = next(row for row in targets
                      if row["record_id"] == "C6-GROUP-04E50F8EB2E636823A11")
        target["conditions_or_group"] = target["conditions_or_group"].replace(
            "500mm/min", "501mm/min"
        )
        with self.assertRaisesRegex(ValueError, "expected one exact"):
            ADAPTER.find_subresult(source, [target])

    def test_source_and_target_inputs_are_unchanged(self):
        self.assertEqual(ADAPTER.read_csv(ADAPTER.TARGET_FILE), self.targets)
        self.assertTrue(ADAPTER.TARGET_FILE.is_file())

    def test_row_field_audit_blocks_the_hard_porcelain_scope_loss(self):
        mappings, _ = ADAPTER.build_crosswalk(self.sources, self.targets)
        field_rows, summaries, metrics = ADAPTER.build_field_audit(
            self.sources, self.targets, mappings
        )
        hard_porcelain = summaries["FNC-CERAMICTECH-HARDPORCELAIN"]
        self.assertEqual(hard_porcelain["status"], "HOLD_FIELD_PRESERVATION_REVIEW")
        self.assertEqual(
            hard_porcelain["critical_unmapped_fields"],
            ["target_material_id", "target_memberships"],
        )
        self.assertIn("record_origin", hard_porcelain["unresolved_mismatch_fields"])
        self.assertEqual(metrics["source_rows_audited"], 88)
        self.assertEqual(metrics["source_rows_without_any_field_gaps"], 87)
        self.assertEqual(metrics["rows_with_critical_gaps"], 1)
        self.assertEqual(metrics["rows_with_unresolved_mismatches"], 1)
        self.assertEqual(len(field_rows), 4919)

    def test_nested_field_audit_preserves_rows_through_unique_observation_locators(self):
        mappings, _ = ADAPTER.build_crosswalk(self.sources, self.targets)
        _, summaries, metrics = ADAPTER.build_field_audit(self.sources, self.targets, mappings)
        nested = [row for row in mappings if row["mapping_kind"] == "AGGREGATED_SUBRESULT"]
        self.assertEqual(len(nested), 60)
        self.assertEqual(len({(row["target_record_id"], row["target_locator"]) for row in nested}), 60)
        self.assertTrue(all(summaries[row["source_record_id"]]["status"] == "PASS" for row in nested))
        self.assertEqual(metrics["overall_status"], "HOLD_FIELD_PRESERVATION_REVIEW")


if __name__ == "__main__":
    unittest.main()
