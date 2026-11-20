from __future__ import annotations

import unittest

from relation_contract_v24 import (
    REGION_CLAIMS,
    VARIANT_CLAIM,
    audit_option_relation_semantics,
    audit_simready_component_relations,
)


def option(relation: str, assignment_id: str, group: str = "", position: str = "1",
           material: str = "MAT-A", source_row: str = "SRC-1", component: str = "COMP-1") -> dict:
    return {
        "assignment_id": assignment_id,
        "source_row_id": source_row,
        "object_id": "OBJ-1",
        "component_id": component,
        "source_family": "TEST",
        "source_asset_id": "ASSET-1",
        "assigned_material_id": material,
        "assignment_relation": relation,
        "assignment_option_group_id": group,
        "option_position": position,
    }


def region(relation_id: str, material: str, region_id: str = "", **extra: str) -> dict:
    row = {
        "relation_id": relation_id,
        "object_id": "OBJ-1",
        "component_id": "COMP-1",
        "canonical_material_id": material,
        "label_relationship": "SOURCE_AUTHORED_MATERIAL_REGION_BINDING_NOT_ALTERNATIVE_NOT_EXTRA_MECHANICAL_COMPONENT",
        "relation_type": "OFFICIAL_BOUND_NONVISUAL_LABEL",
        "source_quote": f'token[] semantics:labels:material = ["{material}"]',
        "source_locator": "materials.usda:semanticsline10",
        "source_local_file": "materials.usda",
        "source_sha256": "a" * 64,
        "binding_quote": "prepend rel material:binding = </Model/Geom/Looks/Material>",
        "binding_source_file": "instances.usda",
        "binding_source_sha256": "b" * 64,
        "audit_status": "SOURCE_CHAIN_VERIFIED_LOGIC_REVIEW_REQUIRED",
        "material_region_id": region_id,
        "binding_target": "/Model/Geom/Looks/Material",
        "binding_owner_prim_path": "/Model/Geom",
        "base_geometry_prim_path": "/Model/Geom",
        "geometry_membership_source_locator": "geometry.usda:line10",
        "geometry_membership_review_id": "REV-1",
        "geometry_membership_reviewer": "reviewer-1",
        "geometry_membership_review_decision": "PASS",
        "collector_id": "collector-1",
    }
    row.update(extra)
    return row


class RelationContractTests(unittest.TestCase):
    def test_single_assignment_requires_no_group_and_position_one(self):
        metrics, errors = audit_option_relation_semantics([
            option("SINGLE_ASSIGNMENT", "A1")
        ])
        self.assertEqual(errors, [])
        self.assertEqual(metrics["relation_counts"]["SINGLE_ASSIGNMENT"], 1)

    def test_alternative_group_requires_same_scope_unique_materials_and_contiguous_positions(self):
        rows = [
            option("PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS", "A1", "G1", "1", "MAT-A"),
            option("PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS", "A2", "G1", "2", "MAT-B"),
        ]
        metrics, errors = audit_option_relation_semantics(rows)
        self.assertEqual(errors, [])
        self.assertEqual(metrics["alternative_groups"], 1)

    def test_singleton_cannot_be_encoded_as_an_alternative_or_grouped_assignment(self):
        rows = [
            option("PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS", "A1", "G1"),
            option("SINGLE_ASSIGNMENT", "A2", "G2"),
        ]
        _, errors = audit_option_relation_semantics(rows)
        self.assertIn("OPTION_ALTERNATIVE_GROUP_MALFORMED", {e["code"] for e in errors})
        self.assertIn("OPTION_SINGLE_ASSIGNMENT_MALFORMED", {e["code"] for e in errors})

    def test_alternatives_cannot_mix_components_or_duplicate_materials(self):
        rows = [
            option("PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS", "A1", "G1", "1", "MAT-A"),
            option("PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS", "A2", "G1", "2", "MAT-A", component="COMP-2"),
        ]
        _, errors = audit_option_relation_semantics(rows)
        self.assertTrue(any(e["code"] == "OPTION_ALTERNATIVE_GROUP_MALFORMED" for e in errors))

    def test_official_simready_bindings_are_retained_without_face_region_proof(self):
        rows = [
            region("R1", "MAT-RUBBER", region_id=""),
            region("R2", "MAT-PLASTIC", region_id=""),
        ]
        metrics, findings = audit_simready_component_relations(rows)
        self.assertEqual(metrics["distinct_object_component_pairs"], 1)
        self.assertEqual(metrics["mechanical_component_count_delta_from_material_regions"], 0)
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_AUTHORED_BINDING_RELATIONS")
        self.assertIn("FACE_COVERAGE_UNREVIEWED", findings[0]["simultaneity_status"])
        self.assertIn("OFFICIAL_SOURCE_RELATIONS_RETAINED", findings[0]["reason"])

    def test_binding_statement_not_alternative_is_retained_without_face_region_proof(self):
        rows = [region("R1", "MAT-RUBBER", ""), region("R2", "MAT-PLASTIC", "")]
        rows[0]["label_relationship"] = "SOURCE_AUTHORED_BINDING_STATEMENT_NOT_ALTERNATIVE_NOT_VERIFIED_NONEMPTY_FACE_REGION"
        rows[1]["label_relationship"] = "SOURCE_AUTHORED_BINDING_STATEMENT_NOT_ALTERNATIVE_NOT_VERIFIED_NONEMPTY_FACE_REGION"
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_AUTHORED_BINDING_RELATIONS")
        self.assertIn("NONALTERNATIVE_BINDING_FACE_REGION_UNVERIFIED", findings[0]["simultaneity_status"])
        self.assertIn("OFFICIAL_SOURCE_RELATIONS_RETAINED", findings[0]["reason"])

    def test_geometry_review_can_upgrade_recorded_binding_to_reviewed_region_claim(self):
        metrics, findings = audit_simready_component_relations([
            region("R1", "MAT-RUBBER", "REGION-1"),
            region("R2", "MAT-PLASTIC", "REGION-2", binding_target="/Model/Geom/Subsets/plastic"),
        ])
        self.assertEqual(findings[0]["relation_class"], "SIMULTANEOUS_MATERIAL_REGIONS_REVIEWED")
        self.assertEqual(metrics["distinct_object_component_pairs"], 1)

    def test_official_bindings_without_region_or_variant_claim_are_retained_as_unspecified(self):
        rows = [region("R1", "MAT-A", "REGION-1"), region("R2", "MAT-B", "REGION-2")]
        rows[1]["label_relationship"] = "UNSPECIFIED"
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_AUTHORED_BINDING_SCOPE_UNSPECIFIED")
        self.assertEqual(findings[0]["simultaneity_status"], "SOURCE_BINDING_RELATIONSHIPS_RETAINED_DETAIL_MIXED")

    def test_missing_official_binding_provenance_still_holds(self):
        rows = [region("R1", "MAT-A"), region("R2", "MAT-B", binding_quote="")]
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "HOLD_SOURCE_BINDING_PROVENANCE_INCOMPLETE")

    def test_source_confirmed_material_variants_are_allowed_with_independent_review(self):
        rows = [region("R1", "MAT-RUBBER", "REGION-1"), region("R2", "MAT-PLASTIC", "REGION-2")]
        for position, row in enumerate(rows, 1):
            row.update({
                "label_relationship": VARIANT_CLAIM,
                "material_variant_group_id": "VG-1",
                "material_variant_id": f"V-{position}",
                "variant_source_locator": f"variants.csv:line{position}",
                "variant_review_id": f"VR-{position}",
                "variant_reviewer": "reviewer-2",
                "variant_review_decision": "PASS",
            })
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "ALTERNATIVE_MATERIAL_VARIANTS_REVIEWED")

    def test_variant_claim_without_independent_review_is_retained_as_reported_variant(self):
        rows = [region("R1", "MAT-RUBBER", "REGION-1"), region("R2", "MAT-PLASTIC", "REGION-2")]
        for row in rows:
            row["label_relationship"] = VARIANT_CLAIM
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_REPORTED_MATERIAL_VARIANTS")

    def test_region_review_must_be_independent_to_claim_reviewed_region(self):
        rows = [
            region("R1", "MAT-RUBBER", "REGION-1"),
            region("R2", "MAT-PLASTIC", "REGION-2", collector_id="reviewer-1"),
        ]
        _, findings = audit_simready_component_relations(rows)
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_AUTHORED_BINDING_RELATIONS")

    def test_duplicate_region_ids_do_not_erase_official_bindings(self):
        _, findings = audit_simready_component_relations([
            region("R1", "MAT-RUBBER", "REGION-1"),
            region("R2", "MAT-PLASTIC", "REGION-1"),
        ])
        self.assertEqual(findings[0]["relation_class"], "SIMREADY_SOURCE_AUTHORED_BINDING_RELATIONS")
        self.assertIn("OFFICIAL_SOURCE_RELATIONS_RETAINED", findings[0]["reason"])


if __name__ == "__main__":
    unittest.main()
