import unittest

from field_preservation_v23 import row_sha256, value_sha256
from field_repair_v23 import (
    FieldRepairError,
    apply_repairs,
    build_field_overrides,
    validate_repair_manifest,
)


class FieldRepairTests(unittest.TestCase):
    def setUp(self):
        self.source = [{
            "record_id": "SRC-1",
            "target_material_id": "MAT-PORCELAIN-BROAD",
            "target_memberships": '[{"target_material_id":"MAT-PORCELAIN-BROAD","relation":"REVIEWED_TRUE_CONTAINMENT"}]',
            "record_origin": "new-batch",
            "unique_record_key": "new-key",
        }]
        self.target = [{
            "record_id": "TGT-1",
            "target_material_id": "",
            "target_memberships": "",
            "record_origin": "canonical-release",
            "unique_record_key": "canonical-key",
        }]

    def manifest(self):
        source, target = self.source[0], self.target[0]
        membership = source["target_memberships"]
        return {
            "schema_version": "RSI_FIELD_REPAIR_V23_1",
            "repair_id": "repair-1",
            "proposer": "collector",
            "reviewer": "independent-reviewer",
            "review_basis": "source membership crosswalk and canonical release key review",
            "base_target_file_sha256": "target-sha",
            "source_files": {"source.csv": "source-sha"},
            "repairs": [{
                "source_record_id": source["record_id"],
                "target_record_id": target["record_id"],
                "target_row_sha256_before": row_sha256(target),
                "patches": [
                    {
                        "source_field": "target_material_id",
                        "target_field": "target_material_id",
                        "disposition": "REVIEWED_MATERIAL_MEMBERSHIP",
                        "basis": "explicit reviewed true-containment mapping",
                        "after_value": "MAT-PORCELAIN-BROAD",
                        "source_value_sha256": value_sha256(source["target_material_id"]),
                        "target_value_sha256_before": value_sha256(""),
                        "target_locator": "membership-review.csv#SRC-1/target_material_id",
                    },
                    {
                        "source_field": "target_memberships",
                        "target_field": "target_memberships",
                        "disposition": "REVIEWED_MATERIAL_MEMBERSHIP",
                        "basis": "explicit reviewed true-containment mapping",
                        "after_value": membership,
                        "source_value_sha256": value_sha256(membership),
                        "target_value_sha256_before": value_sha256(""),
                        "target_locator": "membership-review.csv#SRC-1/target_memberships",
                    },
                    {
                        "source_field": "record_origin",
                        "target_field": "record_origin",
                        "disposition": "REVIEWED_CANONICAL_REKEY",
                        "basis": "source origin retained in frozen archive; target uses canonical release origin",
                        "after_value": "canonical-release",
                        "source_value_sha256": value_sha256(source["record_origin"]),
                        "target_value_sha256_before": value_sha256("canonical-release"),
                        "target_locator": "release-key-crosswalk.csv#SRC-1/record_origin",
                    },
                    {
                        "source_field": "unique_record_key",
                        "target_field": "unique_record_key",
                        "disposition": "REVIEWED_CANONICAL_REKEY",
                        "basis": "target key is canonical and source key is archived",
                        "after_value": "canonical-key",
                        "source_value_sha256": value_sha256(source["unique_record_key"]),
                        "target_value_sha256_before": value_sha256("canonical-key"),
                        "target_locator": "release-key-crosswalk.csv#SRC-1/unique_record_key",
                    },
                ],
            }],
        }

    def test_valid_repair_projects_without_mutating_input(self):
        manifest = validate_repair_manifest(
            self.manifest(), source_rows=self.source, target_rows=self.target,
            target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
        )
        projected = apply_repairs(self.target, manifest)
        self.assertEqual(projected[0]["target_material_id"], "MAT-PORCELAIN-BROAD")
        self.assertEqual(self.target[0]["target_material_id"], "")
        overrides = build_field_overrides(manifest)
        self.assertEqual(overrides["SRC-1"]["record_origin"][0], "REVIEWED_CANONICAL_REKEY")

    def test_stale_target_row_is_rejected(self):
        manifest = self.manifest()
        manifest["repairs"][0]["target_row_sha256_before"] = row_sha256({"record_id": "TGT-1"})
        with self.assertRaises(FieldRepairError):
            validate_repair_manifest(
                manifest, source_rows=self.source, target_rows=self.target,
                target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
            )

    def test_material_id_repair_requires_membership_repair(self):
        manifest = self.manifest()
        manifest["repairs"][0]["patches"] = [manifest["repairs"][0]["patches"][0]]
        with self.assertRaises(FieldRepairError):
            validate_repair_manifest(
                manifest, source_rows=self.source, target_rows=self.target,
                target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
            )

    def test_same_reviewer_cannot_propose_and_review(self):
        manifest = self.manifest()
        manifest["reviewer"] = manifest["proposer"]
        with self.assertRaises(FieldRepairError):
            validate_repair_manifest(
                manifest, source_rows=self.source, target_rows=self.target,
                target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
            )

    def test_schema_drift_is_rejected(self):
        manifest = self.manifest()
        manifest["repairs"][0]["patches"][0]["target_field"] = "field_removed_in_target"
        with self.assertRaises(FieldRepairError):
            validate_repair_manifest(
                manifest, source_rows=self.source, target_rows=self.target,
                target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
            )

    def test_duplicate_target_ids_are_rejected(self):
        manifest = self.manifest()
        duplicate_target = dict(self.target[0])
        with self.assertRaises(FieldRepairError):
            validate_repair_manifest(
                manifest, source_rows=self.source, target_rows=self.target + [duplicate_target],
                target_file_sha256="target-sha", source_file_sha256s={"source.csv": "source-sha"},
            )


if __name__ == "__main__":
    unittest.main()
