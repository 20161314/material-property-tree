import unittest

from delta_reconciliation_v23 import (
    ReconciliationError,
    verify_delta_reconciliation,
)


def maprow(source, target, locator, kind="EXACT_ID", **extra):
    return {
        "source_record_id": source,
        "target_record_id": target,
        "target_locator": locator,
        "mapping_kind": kind,
        "mapping_status": "MAPPED",
        "content_match": "PASS",
        "basis": "independently checked values and source identity",
        **extra,
    }


class DeltaReconciliationTests(unittest.TestCase):
    def test_exact_id_retention(self):
        result = verify_delta_reconciliation(
            [{"record_id": "R1"}], [{"record_id": "R1"}],
            [maprow("R1", "R1", "record")],
        )
        self.assertEqual(result["mapped_source_ids"], 1)
        self.assertEqual(result["mapping_edges"], 1)

    def test_aggregation_maps_rows_to_distinct_nested_subresults(self):
        result = verify_delta_reconciliation(
            [{"record_id": "R1"}, {"record_id": "R2"}],
            [{"record_id": "G1"}],
            [
                maprow("R1", "G1", "property_citations_json#/E/observations/0",
                       "AGGREGATED_SUBRESULT"),
                maprow("R2", "G1", "property_citations_json#/E/observations/1",
                       "AGGREGATED_SUBRESULT"),
            ],
        )
        self.assertEqual(result["unique_target_rows_referenced"], 1)
        self.assertEqual(result["unique_target_locators"], 2)

    def test_split_source_record_can_map_to_multiple_targets(self):
        result = verify_delta_reconciliation(
            [{"record_id": "R1"}],
            [{"record_id": "T1"}, {"record_id": "T2"}],
            [
                maprow("R1", "T1", "record", "SPLIT_SUBRESULT"),
                maprow("R1", "T2", "record", "SPLIT_SUBRESULT"),
            ],
        )
        self.assertEqual(result["mapping_edges"], 2)
        self.assertEqual(result["mapped_source_ids"], 1)

    def test_missing_accepted_source_is_rejected(self):
        with self.assertRaisesRegex(ReconciliationError, "unmapped accepted"):
            verify_delta_reconciliation(
                [{"record_id": "R1"}, {"record_id": "R2"}],
                [{"record_id": "R1"}],
                [maprow("R1", "R1", "record")],
            )

    def test_duplicate_target_locator_is_rejected(self):
        with self.assertRaisesRegex(ReconciliationError, "target locator reused"):
            verify_delta_reconciliation(
                [{"record_id": "R1"}, {"record_id": "R2"}],
                [{"record_id": "G1"}],
                [
                    maprow("R1", "G1", "property_citations_json#/E/observations/0",
                           "AGGREGATED_SUBRESULT"),
                    maprow("R2", "G1", "property_citations_json#/E/observations/0",
                           "AGGREGATED_SUBRESULT"),
                ],
            )

    def test_nonmatching_content_is_rejected(self):
        row = maprow("R1", "T1", "record")
        row["content_match"] = "UNVERIFIED"
        with self.assertRaisesRegex(ReconciliationError, "passing content check"):
            verify_delta_reconciliation([{"record_id": "R1"}],
                                        [{"record_id": "T1"}], [row])

    def test_retraction_requires_independent_decision(self):
        row = {
            "source_record_id": "R1",
            "mapping_status": "RETRACTED",
            "disposition_id": "D1",
            "reviewer_id": "reviewer-2",
            "rationale": "duplicate source group",
            "review_status": "PENDING",
            "target_record_id": "",
            "target_locator": "",
        }
        with self.assertRaisesRegex(ReconciliationError, "not independently approved"):
            verify_delta_reconciliation([{"record_id": "R1"}], [], [row])

    def test_duplicate_source_row_is_rejected(self):
        with self.assertRaisesRegex(ReconciliationError, "duplicate source"):
            verify_delta_reconciliation(
                [{"record_id": "R1"}, {"record_id": "R1"}],
                [{"record_id": "R1"}],
                [maprow("R1", "R1", "record")],
            )

    def test_duplicate_retraction_is_rejected(self):
        row = {
            "source_record_id": "R1",
            "mapping_status": "RETRACTED",
            "disposition_id": "D1",
            "reviewer_id": "reviewer-2",
            "rationale": "duplicate source group",
            "review_status": "PASS",
            "target_record_id": "",
            "target_locator": "",
        }
        with self.assertRaisesRegex(ReconciliationError, "duplicate retraction"):
            verify_delta_reconciliation([{"record_id": "R1"}], [], [row, row])

    def test_multiple_targets_require_split_semantics(self):
        with self.assertRaisesRegex(ReconciliationError, "require SPLIT_SUBRESULT"):
            verify_delta_reconciliation(
                [{"record_id": "R1"}],
                [{"record_id": "T1"}, {"record_id": "T2"}],
                [
                    maprow("R1", "T1", "record", "REKEYED_ROW"),
                    maprow("R1", "T2", "record", "REKEYED_ROW"),
                ],
            )


if __name__ == "__main__":
    unittest.main()
