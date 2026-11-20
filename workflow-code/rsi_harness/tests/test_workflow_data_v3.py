"""Synthetic boundary fixtures only; no live data or scientific admission."""
import copy
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from workflow_data_v3 import (bfs_tasks, deduplicate, enumerate_sources,
                              example_bundle, reconcile, recompute,
                              source_identity, validate_bundle)


def material_rows(result):
    return {row["material_id"]: row for row in result["material_states"]}


class WorkflowDataV3Tests(unittest.TestCase):
    def test_enumeration_stable_identity_field_preservation_and_nonassets(self):
        row = {"namespace": "a:b", "source_uid": "c", "name": "chair", "raw": {"definition": "source wording"}}
        same_name = {"namespace": "a", "source_uid": "b:c", "name": "chair"}
        headline = {"record_type": "headline", "count": 100000}
        inputs = [row, headline, same_name, copy.deepcopy(row)]
        before = copy.deepcopy(inputs)
        result = enumerate_sources(inputs)
        self.assertEqual(result, enumerate_sources(reversed(inputs)))
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(result["duplicates"][0]["count"], 1)
        self.assertEqual(result["gaps"], [headline])
        self.assertNotEqual(source_identity("a:b", "c"), source_identity("a", "b:c"))
        self.assertEqual(next(row for row in result["sources"] if "raw" in row)["raw"], before[0]["raw"])
        self.assertEqual(inputs, before)
        result["sources"][0]["name"] = "changed"
        self.assertEqual(inputs, before)

    def test_identity_conflicts_retained_and_cannot_silently_merge(self):
        rows = [{"namespace": "source", "source_uid": "1", "name": name,
                 "asset_sha256": "a" * 64, "asset_sha256_verified": True} for name in ("x", "y")]
        rows.append({"namespace": "source", "source_uid": "2", "asset_sha256": "a" * 64,
                     "asset_sha256_verified": True})
        result = deduplicate(rows)
        self.assertEqual(result["source_count"], 2)
        self.assertEqual(result["geometry_count"], 2)
        self.assertEqual(len(result["conflicts"][0]["rows"]), 2)
        for invalid in ({"namespace": "a", "source_uid": ""}, {"namespace": "a"},
                        {"namespace": "a", "source_uid": "1", "source_id": "forged"}):
            with self.subTest(row=invalid), self.assertRaises(ValueError):
                enumerate_sources([invalid])

    def test_dedup_only_trusted_hashes_or_reviewed_aliases(self):
        rows = [{"namespace": "dataset", "source_uid": str(index), "name": "same-name",
                 "asset_sha256": "a" * 64} for index in range(4)]
        self.assertEqual(deduplicate(rows)["geometry_count"], 4)
        rows[0]["asset_sha256_verified"] = rows[1]["asset_sha256_verified"] = True
        ids = [source_identity("dataset", str(index)) for index in range(4)]
        alias = {"left_source_id": ids[2], "right_source_id": ids[3], "decision": "PASS",
                 "reviewer": "reviewer", "source_locator": "manifest:alias"}
        result = deduplicate(rows, [alias])
        self.assertEqual(result["geometry_count"], 2)
        self.assertEqual(result["source_to_geometry"][ids[0]], result["source_to_geometry"][ids[1]])
        self.assertEqual(result, deduplicate(reversed(rows), [alias]))
        with self.assertRaises(ValueError):
            deduplicate(rows, [{**alias, "reviewer": ""}])
        with self.assertRaises(ValueError):
            deduplicate(rows, [{**alias, "left_source_id": "missing"}])
        rows[0]["asset_sha256"] = "not-a-sha"
        with self.assertRaises(ValueError):
            deduplicate(rows)

    def test_reviewed_rejection_blocks_direct_and_transitive_merges(self):
        rows = [{"namespace": "d", "source_uid": str(index)} for index in range(3)]
        ids = [source_identity("d", str(index)) for index in range(3)]
        def alias(a, b, decision="PASS"):
            return {"left_source_id": ids[a], "right_source_id": ids[b], "decision": decision,
                    "reviewer": "r", "source_locator": "manifest:alias"}
        result = deduplicate(rows, [alias(0, 1), alias(1, 2), alias(0, 2, "REJECT")])
        self.assertNotEqual(result["source_to_geometry"][ids[0]], result["source_to_geometry"][ids[2]])
        self.assertTrue(result["conflicts"])
        direct = deduplicate(rows, [alias(0, 1), alias(0, 1, "REJECT")])
        self.assertEqual(direct["geometry_count"], 3)
        self.assertEqual(direct["conflicts"][0]["code"], "ALIAS_DECISION_CONFLICT")

    def test_example_validation_and_pure_recompute(self):
        bundle = example_bundle()
        before = copy.deepcopy(bundle)
        self.assertTrue(validate_bundle(bundle)["valid"])
        result = recompute(bundle)
        self.assertEqual(bundle, before)
        self.assertEqual(result["counts"]["states"], {"S1": 2, "S2": 0, "S3": 0, "S4": 0})
        parent = material_rows(result)["example-solid"]
        self.assertEqual(parent["direct_object_count"], 0)
        self.assertEqual(parent["rolled_up_object_count"], 1)
        self.assertEqual(parent["ranges"]["E"]["lower"], 1e9)

    def test_cross_document_coverage_is_not_a_complete_source_group(self):
        bundle = example_bundle()
        original = bundle["evidence"].pop()
        for index, prop in enumerate(("E", "nu", "rho")):
            bundle["evidence"].append({**original, "record_id": "record-" + prop,
                                       "document_id": "document-" + prop, "source_group_id": "group-" + prop,
                                       "properties": {prop: original["properties"][prop]}})
        result = recompute(bundle)
        row = material_rows(result)["example-subtype"]
        self.assertEqual(row["state"], "S1")
        self.assertEqual(row["covered_properties"], ["E", "nu", "rho"])
        self.assertEqual(row["complete_group_count"], 0)
        self.assertEqual(row["partial_group_count"], 3)
        self.assertEqual(row["document_count"], 3)
        self.assertEqual(result["counts"]["complete_group_count"], 0)

    def test_complete_and_partial_concurrent_unknown_conditions_and_units(self):
        bundle = example_bundle()
        original = bundle["evidence"][0]
        bundle["evidence"].append({**original, "record_id": "partial", "source_group_id": "another-group",
                                   "conditions": "unknown", "properties": {"E": {"lower": 500, "upper": 1500, "unit": "MPa"}}})
        row = material_rows(recompute(bundle))["example-subtype"]
        self.assertEqual((row["complete_group_count"], row["partial_group_count"], row["document_count"]), (1, 1, 1))
        self.assertEqual(row["ranges"]["E"]["lower"], 5e8)
        self.assertEqual(row["ranges"]["E"]["upper"], 1.5e9)
        bundle["evidence"][1]["source_group_id"] = original["source_group_id"]
        with self.assertRaises(ValueError):
            validate_bundle(bundle)

    def test_rejects_forbidden_origins_and_numerical_boundaries(self):
        for origin in ("model", "simulation_input", "solver_default", "AI", "semantic_approximation"):
            bundle = example_bundle()
            bundle["evidence"][0]["origin"] = origin
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                validate_bundle(bundle)
        invalid = [{"value": 0, "unit": "GPa"}, {"value": -1, "unit": "GPa"},
                   {"lower": 2, "upper": 1, "unit": "Pa"}, {"value": float("nan"), "unit": "Pa"},
                   {"value": float("inf"), "unit": "Pa"}, {"value": True, "unit": "Pa"},
                   {"value": 1e308, "unit": "GPa"}, {"value": 10 ** 400, "unit": "Pa"},
                   {"value": "1", "unit": "Pa"}, {"value": 1, "unit": "unknown"},
                   {"value": 1, "lower": 1, "upper": 2, "unit": "Pa"}]
        for value in invalid:
            bundle = example_bundle()
            bundle["evidence"][0]["properties"]["E"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                validate_bundle(bundle)
        bundle = example_bundle()
        bundle["evidence"][0]["properties"]["nu"]["value"] = -0.1
        validate_bundle(bundle)  # Auxetic materials are not missing-value sentinels.
        bundle["evidence"][0]["is_simulation_input"] = True
        with self.assertRaises(ValueError):
            validate_bundle(bundle)
        bundle = example_bundle()
        bundle["evidence"][0]["properties"]["E"]["origin"] = "model"
        with self.assertRaises(ValueError):
            validate_bundle(bundle)
        bundle["evidence"][0]["properties"]["E"] = {"value": 1, "unit": "Pa", "is_simulation_input": True}
        with self.assertRaises(ValueError):
            validate_bundle(bundle)

    def test_requires_accepted_provenance_and_independent_reviewer(self):
        for table, field in (("relations", "basis"), ("relations", "source_locator"),
                             ("taxonomy", "basis"), ("taxonomy", "source_locator"),
                             ("evidence", "source_quote"), ("evidence", "source_url"),
                             ("evidence", "source_locator"), ("evidence", "reviewer")):
            bundle = example_bundle()
            bundle[table][0][field] = " "
            with self.subTest(table=table, field=field), self.assertRaises(ValueError):
                validate_bundle(bundle)
        bundle = example_bundle()
        bundle["evidence"][0]["collector"] = bundle["evidence"][0]["reviewer"]
        with self.assertRaises(ValueError):
            validate_bundle(bundle)

    def test_schema_foreign_keys_duplicate_ids_and_cycles_fail_closed(self):
        for table, field in (("components", "object_id"), ("relations", "component_id"),
                             ("relations", "material_id"), ("taxonomy", "child_id"),
                             ("taxonomy", "parent_id"), ("evidence", "material_id")):
            bundle = example_bundle()
            bundle[table][0][field] = "orphan"
            with self.subTest(table=table, field=field), self.assertRaises(ValueError):
                validate_bundle(bundle)
        for table in ("objects", "components", "materials", "relations", "taxonomy", "evidence"):
            bundle = example_bundle()
            bundle[table].append(copy.deepcopy(bundle[table][0]))
            with self.subTest(table=table), self.assertRaises(ValueError):
                validate_bundle(bundle)
        bundle = example_bundle()
        edge = bundle["taxonomy"][0]
        bundle["taxonomy"].append({**edge, "edge_id": "cycle", "child_id": edge["parent_id"], "parent_id": edge["child_id"]})
        with self.assertRaises(ValueError):
            validate_bundle(bundle)
        # A root path into a cycle must still fail.
        bundle["materials"].append({"material_id": "root"})
        bundle["taxonomy"].append({**edge, "edge_id": "root-path", "parent_id": "root"})
        with self.assertRaises(ValueError):
            validate_bundle(bundle)

    def test_only_pass_and_only_is_a_roll_up_no_downward_inheritance(self):
        bundle = example_bundle()
        bundle["relations"][0]["decision"] = "HOLD"
        bundle["evidence"][0]["material_id"] = "example-solid"
        rows = material_rows(recompute(bundle))
        self.assertEqual(rows["example-solid"]["state"], "S2")
        self.assertEqual(rows["example-subtype"]["state"], "S4")
        bundle["relations"][0]["decision"] = "PASS"
        bundle["taxonomy"][0]["relation"] = "COMPOSED_OF"
        rows = material_rows(recompute(bundle))
        self.assertEqual(rows["example-solid"]["state"], "S2")
        self.assertEqual(rows["example-subtype"]["state"], "S3")
        bundle["taxonomy"][0]["relation"] = "IS_A"
        bundle["taxonomy"][0]["decision"] = "HOLD"
        self.assertEqual(material_rows(recompute(bundle))["example-solid"]["object_count"], 0)

    def test_diamond_deduplicates_evidence_documents_and_object_components(self):
        bundle = example_bundle()
        bundle["materials"].extend({"material_id": identity} for identity in ("left", "right"))
        edge = bundle["taxonomy"].pop()
        for index, (child, parent) in enumerate((("example-subtype", "left"), ("example-subtype", "right"),
                                                 ("left", "example-solid"), ("right", "example-solid"))):
            bundle["taxonomy"].append({**edge, "edge_id": str(index), "child_id": child, "parent_id": parent})
        bundle["components"].append({**bundle["components"][0], "component_id": "second-component"})
        bundle["relations"].append({**bundle["relations"][0], "relation_id": "second-link", "component_id": "second-component"})
        root = material_rows(recompute(bundle))["example-solid"]
        self.assertEqual((root["object_count"], root["record_count"], root["document_count"], root["complete_group_count"]), (1, 1, 1, 1))

    def test_four_states_excluded_scopes_and_no_excluded_evidence_rollup(self):
        bundle = example_bundle()
        bundle["taxonomy"] = []
        bundle["materials"].extend({"material_id": identity, "scope": scope} for identity, scope in
                                   (("empty", "solid"), ("water", "liquid"), ("air-space", "void"), ("folder", "organizational")))
        bundle["evidence"].append({**bundle["evidence"][0], "record_id": "parent-complete", "material_id": "example-solid"})
        result = recompute(bundle)
        self.assertEqual(result["counts"]["states"], {"S1": 1, "S2": 1, "S3": 0, "S4": 1})
        self.assertEqual(result["counts"]["excluded_material_count"], 3)
        self.assertIsNone(material_rows(result)["water"]["state"])
        bundle["evidence"][0]["properties"].pop("nu")
        self.assertEqual(material_rows(recompute(bundle))["example-subtype"]["state"], "S3")
        bundle["evidence"][0]["material_id"] = "water"
        bundle["taxonomy"] = [{**example_bundle()["taxonomy"][0], "child_id": "water"}]
        root = material_rows(recompute(bundle))["example-solid"]
        self.assertEqual(root["record_ids"], ["parent-complete"])

    def test_bfs_depth_then_state_then_soft_weight_with_deterministic_ties(self):
        bundle = example_bundle()
        bundle["taxonomy"] = []
        bundle["materials"].extend({"material_id": identity} for identity in ("s3", "s4"))
        bundle["relations"].append({**bundle["relations"][0], "relation_id": "s3-link", "material_id": "s3"})
        bundle["evidence"].append({**bundle["evidence"][0], "record_id": "s2-data", "material_id": "example-solid"})
        tasks = bfs_tasks(bundle, soft_weights={"s4": 1e30, "example-solid": 1e30})
        self.assertEqual([task["state"] for task in tasks], ["S3", "S2", "S4", "S1"])
        self.assertEqual({task["state"] for task in bfs_tasks(bundle, kind="object")}, {"S1", "S2"})
        edge = example_bundle()["taxonomy"][0]
        bundle["taxonomy"] = [{**edge, "child_id": "s3", "parent_id": "s4"}]
        tasks = bfs_tasks(bundle, soft_weights={"s3": 1e30})
        self.assertEqual(tasks[-1]["material_id"], "s3")
        self.assertEqual(tasks[-1]["depth"], 1)
        before = copy.deepcopy(bundle)
        random.Random(1).shuffle(bundle["materials"])
        self.assertEqual(tasks, bfs_tasks(bundle, soft_weights={"s3": 1e30}))
        self.assertEqual(len(bfs_tasks(bundle, limit=1)), 1)
        self.assertNotIn("s3", [row["material_id"] for row in bfs_tasks(bundle, visited=["s3"])])
        self.assertEqual(sorted(bundle["materials"], key=lambda r: r["material_id"]),
                         sorted(before["materials"], key=lambda r: r["material_id"]))
        for options in ({"limit": 0}, {"limit": True}, {"kind": "bad"}, {"soft_weights": {"s3": float("inf")}}):
            with self.subTest(options=options), self.assertRaises(ValueError):
                bfs_tasks(bundle, **options)

    def test_reconciliation_independent_add_withdraw_change_and_duplicate_counts(self):
        parent = example_bundle()
        bundle = copy.deepcopy(parent)
        bundle["objects"] = [{"object_id": "new-object"}, {"object_id": "new-object"}]
        bundle["evidence"][0]["source_quote"] = "An explicitly changed quote"
        bundle["materials"].append(copy.deepcopy(bundle["materials"][0]))
        report = reconcile(parent, bundle)
        objects = report["tables"]["objects"]
        self.assertEqual((objects["added"], objects["withdrawn"], objects["duplicates"]), (1, 1, 1))
        self.assertEqual(report["tables"]["evidence"]["changed"], 1)
        self.assertEqual(report["totals"]["duplicates"], 2)
        self.assertEqual(report["tables"]["materials"]["unchanged"], 2)
        self.assertEqual(reconcile(parent, parent)["totals"]["added"], 0)


if __name__ == "__main__":
    unittest.main()
