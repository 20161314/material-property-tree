import unittest

from field_preservation_v23 import audit_row_fields, row_sha256


class FieldPreservationTests(unittest.TestCase):
    def test_alias_and_numeric_equivalence_are_explicit(self):
        source = {
            "record_id": "R1",
            "conditions_or_group": "room temperature",
            "E_low_GPa": "70",
            "record_origin": "old",
        }
        target = {
            "record_id": "R1",
            "conditions": "room temperature",
            "E_low_GPa": "70.0",
            "record_origin": "new",
        }
        rows, summary = audit_row_fields(
            source, target,
            source_archive_ref="frozen/source.csv",
            source_file_sha256="a" * 64,
            target_record_id="R1",
        )
        status = {row["source_field"]: row["field_status"] for row in rows}
        self.assertEqual(status["conditions_or_group"], "ALIAS_EXACT")
        self.assertEqual(status["E_low_GPa"], "DIRECT_NUMERIC_EQUIVALENT")
        self.assertEqual(status["record_origin"], "TARGET_VALUE_MISMATCH")
        self.assertEqual(summary["status"], "HOLD_FIELD_PRESERVATION_REVIEW")

    def test_missing_critical_material_mapping_blocks_row(self):
        source = {
            "record_id": "R2",
            "material_identity": "Hard porcelain",
            "target_material_id": "MAT-PORCELAIN-BROAD",
            "target_memberships": '[{"target_material_id":"MAT-PORCELAIN-BROAD"}]',
        }
        target = {"record_id": "R2", "material_identity": "Hard porcelain"}
        rows, summary = audit_row_fields(
            source, target,
            source_archive_ref="frozen/source.csv",
            source_file_sha256="b" * 64,
            target_record_id="R2",
        )
        self.assertEqual(summary["critical_unmapped_fields"], ["target_material_id", "target_memberships"])
        self.assertEqual(summary["status"], "HOLD_FIELD_PRESERVATION_REVIEW")
        self.assertTrue(all(row["source_row_sha256"] == row_sha256(source) for row in rows))

    def test_archive_only_is_distinct_from_value_mismatch(self):
        source = {"record_id": "R3", "source_row_raw": "raw source row"}
        target = {"record_id": "R3"}
        rows, summary = audit_row_fields(
            source, target,
            source_archive_ref="frozen/source.csv",
            source_file_sha256="c" * 64,
            target_record_id="R3",
        )
        self.assertEqual(
            next(row["field_status"] for row in rows if row["source_field"] == "source_row_raw"),
            "ARCHIVED_ONLY",
        )
        self.assertEqual(summary["unresolved_mismatch_fields"], [])
        self.assertEqual(summary["archived_only_fields"], 1)


if __name__ == "__main__":
    unittest.main()
