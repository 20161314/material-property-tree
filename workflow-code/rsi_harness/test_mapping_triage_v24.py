import unittest
from pathlib import Path
import tempfile
import csv
import hashlib

from mapping_triage_v24 import build_triage, classify_route
from simready_binding_audit_v24 import audit_batch


class MappingTriageV24Tests(unittest.TestCase):
    def test_unmapped_vomp_is_candidate_route(self):
        route, evidence, _ = classify_route({
            "reason_code": "MATERIAL_NODE_SENTINEL_UNMAPPED",
            "source_dataset": "VoMP GVM public preprocessed set (simready)",
            "original_material_label": "metal",
        })
        self.assertEqual(route, "VOMP_INDEPENDENT_MATERIAL_REVIEW")
        self.assertEqual(evidence, "VLM_OR_SEGMENT_CANDIDATE")

    def test_unmapped_simready_unparsed_is_parse_route(self):
        route, evidence, _ = classify_route({
            "reason_code": "MATERIAL_NODE_SENTINEL_UNMAPPED",
            "source_dataset": "NVIDIA SimReady Assets official Hugging Face release",
            "original_material_label": "MATERIAL_NOT_YET_PARSED_FROM_AUTHORED_USD",
            "material_node_id": "UNMAPPED",
        })
        self.assertEqual(route, "SIMREADY_USD_PARSE_ROUTE")
        self.assertEqual(evidence, "OFFICIAL_BINDING_UNPARSED")

    def test_build_triage_keeps_source_groups_separate(self):
        rows = [
            {"reason_code": "MATERIAL_NODE_SENTINEL_UNMAPPED", "source_dataset": "PHYSXNET-FINALINDEX", "material_node_id": "UNMAPPED", "original_material_label": "x", "object_id": "o1"},
            {"reason_code": "MATERIAL_NODE_SENTINEL_UNMAPPED", "source_dataset": "VoMP GVM public preprocessed set (simready)", "material_node_id": "UNMAPPED", "original_material_label": "metal", "object_id": "o2"},
        ]
        groups = build_triage(rows)
        self.assertEqual(sum(int(x["row_count"]) for x in groups), 2)
        self.assertEqual({x["source_family"] for x in groups}, {"PhysX_3D", "VoMP_GVM"})

    def test_simready_binding_audit_accepts_exact_official_binding_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "asset"
            evidence.mkdir()
            semantic_quote = 'token[] semantics:labels:material = ["steel"]'
            binding_quote = 'prepend rel material:binding = </Materials/steel>'
            source = evidence / "materials.usda"
            binding = evidence / "instances.usda"
            source.write_text(semantic_quote + "\n", encoding="utf-8")
            binding.write_text(binding_quote + "\n", encoding="utf-8")
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            queue = [{"object_id": "OBJ-SIMREADYHF-part_a01", "component_id": "CMP-1",
                      "source_dataset": "NVIDIA SimReady Assets official Hugging Face release"}]
            relation = {
                "relation_id": "rel-1", "object_id": queue[0]["object_id"], "component_id": "CMP-1",
                "source_label_raw": "steel", "source_label_normalized": "steel",
                "relation_type": "OFFICIAL_BOUND_NONVISUAL_LABEL", "source_quote": semantic_quote,
                "source_local_file": str(source), "source_sha256": digest(source),
                "source_locator": "asset/instances.usda:1;asset/materials.usda:1",
                "semantic_source_locator": "asset/materials.usda:1",
                "binding_source_locator": "asset/instances.usda:1",
                "canonical_material_id": "MAT-STEEL-BROAD",
                "canonical_mapping_status": "REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT",
                "plausibility_status": "ACCEPTED_PLAUSIBLE_SOURCE_REPORTED_LABEL",
                "binding_quote": binding_quote, "binding_source_file": str(binding),
                "binding_source_sha256": digest(binding), "source_url": "https://example.test/asset.usd",
                "bound_material_name": "steel_surface",
            }
            candidates, holds, metrics = audit_batch(
                root, queue, [relation], [{"material_id": "MAT-STEEL-BROAD", "material_name_en": "Steel"}]
            )
            self.assertEqual(len(candidates), 1)
            self.assertEqual(holds, [])
            self.assertEqual(metrics["verified_component_pairs"], 1)

            bad = dict(relation, source_quote='token[] semantics:labels:material = ["wood"]')
            candidates, holds, _ = audit_batch(
                root, queue, [bad], [{"material_id": "MAT-STEEL-BROAD", "material_name_en": "Steel"}]
            )
            self.assertEqual(candidates, [])
            reasons = {reason for row in holds for reason in row["hold_reason"].split(";")}
            self.assertIn("SOURCE_QUOTE_LABEL_MISMATCH", reasons)

    def test_simready_binding_audit_rejects_locator_to_wrong_line(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            evidence = root / "asset"
            evidence.mkdir()
            semantic_quote = 'token[] semantics:labels:material = ["steel"]'
            binding_quote = 'prepend rel material:binding = </Materials/steel>'
            source = evidence / "materials.usda"
            binding = evidence / "instances.usda"
            source.write_text("# header\n" + semantic_quote + "\n", encoding="utf-8")
            binding.write_text(binding_quote + "\n", encoding="utf-8")
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            queue = [{"object_id": "OBJ-SIMREADYHF-part_a01", "component_id": "CMP-1",
                      "source_dataset": "NVIDIA SimReady Assets official Hugging Face release"}]
            relation = {
                "relation_id": "rel-1", "object_id": queue[0]["object_id"], "component_id": "CMP-1",
                "source_label_raw": "steel", "source_label_normalized": "steel",
                "relation_type": "OFFICIAL_BOUND_NONVISUAL_LABEL", "source_quote": semantic_quote,
                "source_local_file": str(source), "source_sha256": digest(source),
                "source_locator": "asset/instances.usda:line1;materialrefline2;asset/materials.usda:line1",
                "semantic_source_locator": "asset/materials.usda:line1",
                "canonical_material_id": "MAT-STEEL-BROAD",
                "canonical_mapping_status": "REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT",
                "plausibility_status": "ACCEPTED_PLAUSIBLE_SOURCE_REPORTED_LABEL",
                "binding_quote": binding_quote, "binding_source_file": str(binding),
                "binding_source_sha256": digest(binding), "binding_source_locator": "asset/instances.usda:line1",
                "source_url": "https://example.test/asset.usd", "bound_material_name": "steel_surface",
            }
            candidates, holds, _ = audit_batch(
                root, queue, [relation], [{"material_id": "MAT-STEEL-BROAD", "material_name_en": "Steel"}]
            )
            self.assertEqual(candidates, [])
            reasons = {reason for row in holds for reason in row["hold_reason"].split(";")}
            self.assertIn("SEMANTIC_LOCATOR_DOES_NOT_POINT_TO_QUOTE", reasons)

    def test_simready_binding_audit_supports_usdcat_flattened_locator(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "asset.usda"
            semantic_quote = 'token[] semantics:labels:material = ["fabric"]'
            binding_quote = 'rel material:binding = </Root/Materials/fabric>'
            source.write_text(semantic_quote + "\n" + binding_quote + "\n", encoding="utf-8")
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            queue = [{"object_id": "OBJ-SIMREADYHF-part_a01", "component_id": "CMP-1",
                      "source_dataset": "NVIDIA SimReady Assets official Hugging Face release"}]
            relation = {
                "relation_id": "rel-1", "object_id": queue[0]["object_id"], "component_id": "CMP-1",
                "source_label_raw": "fabric", "source_label_normalized": "fabric",
                "relation_type": "OFFICIAL_BOUND_NONVISUAL_LABEL", "source_quote": semantic_quote,
                "source_local_file": str(source), "source_sha256": digest,
                "source_locator": "asset.usd via usdcat:asset.usda:bindingL2;materialSemanticL1",
                "canonical_material_id": "MAT-FABRIC", "canonical_mapping_status": "REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT",
                "plausibility_status": "ACCEPTED_PLAUSIBLE_SOURCE_REPORTED_LABEL",
                "binding_quote": binding_quote, "binding_source_file": str(source),
                "binding_source_sha256": digest, "source_url": "https://example.test/asset.usd",
                "bound_material_name": "fabric_surface",
            }
            candidates, holds, _ = audit_batch(
                root, queue, [relation], [{"material_id": "MAT-FABRIC", "material_name_en": "Fabric"}]
            )
            self.assertEqual(len(candidates), 1)
            self.assertEqual(holds, [])


if __name__ == "__main__":
    unittest.main()
