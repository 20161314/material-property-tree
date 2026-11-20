#!/usr/bin/env python3
"""Validate the RSI object-first phase contract without changing facts.

This check separates structural workflow failures from unresolved research
obligations.  A valid contract means that the object table, reverse material
index, evidence ledger, and named-source report are present and mutually
well-formed.  It does not claim that all source objects are mapped or that all
materials have complete evidence; the release gate handles those obligations.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from evidence_route_contract_v24 import run_route_contract
from relation_contract_v24 import audit_option_relation_semantics
from source_coverage_v24 import validate_report


OBJECT_REL = Path("data/scaling_release_v1/object_component_inventory.csv")
MATERIAL_REL = Path("data/current_two_table_delivery_v1/material_reverse_index_and_property_ranges.csv")
OPTION_REL = Path("data/current_two_table_delivery_v1/current_material_options.csv")
EVIDENCE_REL = Path("data/current_two_table_delivery_v1/main_property_source_groups.csv")
SUMMARY_REL = Path("data/current_two_table_delivery_v1/summary.json")
SOURCE_COVERAGE_REL = Path("audit/rsi_framework_review_2026-11-15/rsi_v24_source_coverage.json")
SCOPE_REL = Path("data/material_scope_policy.json")
TAXONOMY_REL = Path("data/research_material_release_v1/material_tree_research_v1.json")

UNRESOLVED_IDS = frozenset({"", "UNMAPPED", "NOT_MAPPED", "UNASSIGNED", "UNKNOWN"})
REQUIRED_SOURCE_FAMILIES = frozenset({
    "VoMP_GVM", "PIXIEVerse", "PhysX_3D", "PhysX_Mobility", "ABO", "NVIDIA_SimReady",
})
ALIAS_SOURCE_FAMILIES = frozenset({"SLAT_Phys_ALIAS", "NVIDIA_SimReady_LEGACY_ALIAS"})
ROOT_IDS = frozenset({"", "ROOT", "MATERIAL_ROOT", "MAT-ROOT"})
EXPLICIT_NON_MATERIAL_IDS = frozenset({"SPECIAL-DOMAIN-VOID"})
RULES_VERSION = "2.4.3-H4"


def _rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _issue(code: str, message: str, count: int = 1, samples: list[str] | None = None) -> dict:
    return {"code": code, "message": message, "count": count, "samples": (samples or [])[:10]}


def _parent_graph_issues(material_rows: list[dict], allowed_external_ids: set[str] | None = None) -> list[dict]:
    ids = {r.get("material_id", "").strip() for r in material_rows if r.get("material_id", "").strip()}
    allowed_external_ids = allowed_external_ids or set()
    errors: list[dict] = []
    missing = sorted({
        r.get("parent_id", "").strip()
        for r in material_rows
        if r.get("parent_id", "").strip() not in ids | allowed_external_ids | ROOT_IDS
    })
    if missing:
        errors.append(_issue("MATERIAL_PARENT_ORPHAN", "material parent is absent from the current node set", len(missing), missing))
    edges = {r.get("material_id", "").strip(): r.get("parent_id", "").strip() for r in material_rows if r.get("material_id", "").strip()}
    globally_seen: set[str] = set()
    cycles: list[str] = []
    for start in edges:
        if start in globally_seen:
            continue
        trail: list[str] = []
        position: dict[str, int] = {}
        node = start
        while node in edges and node not in globally_seen:
            if node in position:
                cycles.append(" -> ".join(trail[position[node]:] + [node]))
                break
            position[node] = len(trail)
            trail.append(node)
            node = edges[node]
        globally_seen.update(trail)
    if cycles:
        errors.append(_issue("MATERIAL_TREE_CYCLE", "material parent graph contains a cycle", len(cycles), cycles))
    return errors


def run_workflow_contract(root: Path) -> dict:
    root = root.resolve()
    required = {
        "objects": root / OBJECT_REL,
        "materials": root / MATERIAL_REL,
        "options": root / OPTION_REL,
        "evidence": root / EVIDENCE_REL,
        "summary": root / SUMMARY_REL,
        "source_coverage": root / SOURCE_COVERAGE_REL,
        "scope": root / SCOPE_REL,
        "taxonomy": root / TAXONOMY_REL,
    }
    errors: list[dict] = []
    for name, path in required.items():
        if not path.is_file():
            errors.append(_issue("WORKFLOW_REQUIRED_FILE_MISSING", f"missing {name}: {path}"))
    if errors:
        return {"status": "BLOCKED_RSI_WORKFLOW_CONTRACT", "rules_version": RULES_VERSION, "errors": errors}

    from current_object_inventory_v24 import iter_inventory
    summary = json.loads(required["summary"].read_text(encoding="utf-8"))
    objects = list(iter_inventory(root, summary))
    materials = _rows(required["materials"])
    options = _rows(required["options"])
    evidence = _rows(required["evidence"])
    summary = json.loads(required["summary"].read_text(encoding="utf-8"))
    coverage = json.loads(required["source_coverage"].read_text(encoding="utf-8"))
    scope = json.loads(required["scope"].read_text(encoding="utf-8"))
    taxonomy = json.loads(required["taxonomy"].read_text(encoding="utf-8"))
    route_contract = run_route_contract(root)
    if route_contract.get("status") != "PASS_RSI_EVIDENCE_ROUTE_CONTRACT":
        errors.append(_issue(
            "EVIDENCE_ROUTE_CONTRACT_BLOCKED",
            "evidence route registry lacks an explicit, validated admission policy",
            len(route_contract.get("errors", [])) or 1,
            [e.get("code", "") for e in route_contract.get("errors", [])],
        ))

    object_fields = {
        "object_id", "component_id", "source_dataset", "source_asset_id", "object_name_en",
        "object_name_cn", "component_scope", "material_node_id", "material_label",
        "mapping_source_ids", "mapping_evidence", "asset_status", "source_record_locator",
    }
    material_fields = {"material_id", "material_name_cn", "material_name_en", "parent_id", "material_presence"}
    evidence_fields = {
        "record_id", "material_identity", "source_id", "document_key", "url", "locator",
        "local_file", "sha256", "unique_record_key", "E_low_GPa", "nu_low", "rho_low_kg_m3",
    }
    option_fields = {
        "assignment_id", "source_row_id", "object_id", "component_id", "source_family",
        "source_asset_id", "assigned_material_id", "assignment_relation",
        "assignment_option_group_id", "option_position", "assignment_basis",
        "original_admission_status", "source_record_locator",
    }
    for label, rows, fields in (("object", objects, object_fields), ("material", materials, material_fields),
                                ("option", options, option_fields), ("evidence", evidence, evidence_fields)):
        actual = set(rows[0]) if rows else set()
        missing = sorted(fields - actual)
        if missing:
            errors.append(_issue("WORKFLOW_SCHEMA_MISSING_COLUMNS", f"{label} table lacks required columns", len(missing), missing))
        if not rows:
            errors.append(_issue("WORKFLOW_TABLE_EMPTY", f"{label} table has no records"))

    object_ids = {r.get("object_id", "").strip() for r in objects if r.get("object_id", "").strip()}
    component_pairs = {
        (r.get("object_id", "").strip(), r.get("component_id", "").strip())
        for r in objects
        if r.get("object_id", "").strip() and r.get("component_id", "").strip()
    }
    material_ids = {r.get("material_id", "").strip() for r in materials if r.get("material_id", "").strip()}
    object_material_ids = Counter(r.get("material_node_id", "").strip() for r in objects)
    excluded = set(summary.get("excluded_liquid_material_ids", [])) | set(scope.get("excluded_material_ids", []))
    orphan_ids = sorted(
        mid for mid in object_material_ids
        if mid not in UNRESOLVED_IDS and mid not in excluded and mid not in material_ids
    )
    if orphan_ids:
        errors.append(_issue("WORKFLOW_ORPHAN_MATERIAL_FOREIGN_KEY", "object table references absent material nodes", len(orphan_ids), orphan_ids))

    option_orphans: list[str] = []
    option_material_orphans: list[str] = []
    option_ids: set[str] = set()
    option_relation_metrics, option_relation_errors = audit_option_relation_semantics(options)
    errors.extend(option_relation_errors)
    for row in options:
        assignment_id = row.get("assignment_id", "").strip()
        if not assignment_id or assignment_id in option_ids:
            option_orphans.append(f"duplicate/blank assignment_id={assignment_id or '<blank>'}")
        option_ids.add(assignment_id)
        pair = (row.get("object_id", "").strip(), row.get("component_id", "").strip())
        if pair not in component_pairs:
            option_orphans.append(f"object/component={pair[0]}|{pair[1]}")
        option_mid = row.get("assigned_material_id", "").strip()
        if (not option_mid or option_mid in UNRESOLVED_IDS or
                (option_mid not in material_ids and option_mid not in excluded and
                 option_mid not in EXPLICIT_NON_MATERIAL_IDS)):
            option_material_orphans.append(f"{assignment_id or '<blank>'}:{option_mid or '<blank>'}")
    if options and summary.get("current_material_option_rows") is not None and len(options) != summary.get("current_material_option_rows"):
        errors.append(_issue("OPTION_ROW_COUNT_DRIFT", "option table count disagrees with summary", 1,
                             [f"actual={len(options)} summary={summary.get('current_material_option_rows')}"]))
    if option_orphans:
        errors.append(_issue("OPTION_OBJECT_COMPONENT_INVALID", "option table has duplicate IDs or orphan object/component references",
                             len(option_orphans), option_orphans))
    if option_material_orphans:
        errors.append(_issue("OPTION_MATERIAL_FOREIGN_KEY_INVALID", "option table references absent or unresolved material nodes",
                             len(option_material_orphans), option_material_orphans))

    presence_errors: list[str] = []
    for row in materials:
        mid = row.get("material_id", "").strip()
        presence = row.get("material_presence", "").strip()
        try:
            linked = int(row.get("linked_object_identities", "0") or 0)
        except ValueError:
            presence_errors.append(f"{mid}: nonnumeric linked_object_identities")
            continue
        if (presence == "OBJECT_LINKED") != (linked > 0):
            presence_errors.append(f"{mid}: presence={presence}, linked_object_identities={linked}")
    if presence_errors:
        errors.append(_issue("MATERIAL_PRESENCE_INCONSISTENT", "material reverse index presence disagrees with linked object count", len(presence_errors), presence_errors))
    taxonomy_ids = {
        node_id
        for node in taxonomy.get("nodes", [])
        for node_id in [node.get("material_node_id") or node.get("id")]
        if node_id
    }
    errors.extend(_parent_graph_issues(materials, taxonomy_ids))

    complete = partial = 0
    evidence_keys: set[str] = set()
    evidence_bad: list[str] = []
    for i, row in enumerate(evidence, 2):
        key = row.get("unique_record_key", "").strip()
        if not key or key in evidence_keys:
            evidence_bad.append(f"row {i}: duplicate/blank unique_record_key={key}")
        evidence_keys.add(key)
        is_complete = all(row.get(k, "").strip() for k in ("E_low_GPa", "nu_low", "rho_low_kg_m3"))
        complete += int(is_complete)
        partial += int(not is_complete)
        if is_complete and not all(row.get(k, "").strip() for k in ("source_id", "document_key", "url", "locator", "local_file", "sha256")):
            evidence_bad.append(f"row {i}: complete group lacks provenance")
    if evidence_bad:
        errors.append(_issue("EVIDENCE_LEDGER_INVALID", "evidence ledger has duplicate keys or incomplete provenance", len(evidence_bad), evidence_bad))

    coverage_problems = validate_report(root, coverage, summary)
    if coverage_problems:
        errors.append(_issue("SOURCE_COVERAGE_STALE_OR_UNPINNED",
                             "source coverage must match current counts and frozen inputs",
                             len(coverage_problems), coverage_problems))
    coverage_families = {row.get("family") for row in coverage.get("families", []) if row.get("family")}
    missing_families = sorted(REQUIRED_SOURCE_FAMILIES - coverage_families)
    if missing_families:
        errors.append(_issue("REQUIRED_SOURCE_FAMILY_NOT_REPORTED", "required source family absent from coverage report", len(missing_families), missing_families))
    missing_aliases = sorted(ALIAS_SOURCE_FAMILIES - coverage_families)
    if missing_aliases:
        errors.append(_issue("SOURCE_ALIAS_NOT_REPORTED", "declared source alias absent from coverage report", len(missing_aliases), missing_aliases))

    special_void_rows = sum(
        1 for row in objects
        if row.get("source_dataset", "").strip() == "PHYSX-MOBILITY"
        and "empty space" in " ".join(
            row.get(k, "").strip().lower()
            for k in ("material_label", "component_material_label_raw", "material_candidate_raw")
        )
    )
    unresolved = sum(object_material_ids[k] for k in UNRESOLVED_IDS if k in object_material_ids) - special_void_rows
    metrics = {
        "object_identities": len(object_ids),
        "distinct_component_pairs": len(component_pairs),
        "option_rows": len(options),
        "option_assignment_ids": len(option_ids - {""}),
        "option_relation_semantics": option_relation_metrics,
        "option_orphan_object_component_rows": len(option_orphans),
        "option_orphan_material_rows": len(option_material_orphans),
        "object_state_rows": len(objects),
        "material_nodes": len(material_ids),
        "object_material_id_count": len(object_material_ids),
        "unresolved_object_material_rows": unresolved,
        "evidence_rows": len(evidence),
        "complete_evidence_groups": complete,
        "partial_evidence_groups": partial,
        "source_families_reported": sorted(coverage_families),
        "required_source_families": sorted(REQUIRED_SOURCE_FAMILIES),
        "alias_source_families": sorted(ALIAS_SOURCE_FAMILIES),
        "object_table_precedes_material_reverse_index": True,
        "taxonomy_nodes_available_for_parent_edges": len(taxonomy_ids),
        "special_domain_void_rows_excluded": special_void_rows,
        "evidence_route_contract_status": route_contract.get("status"),
        "evidence_route_count": route_contract.get("metrics", {}).get("route_rows"),
    }
    pending = {
        "unresolved_object_material_rows": unresolved,
        "summary_geometry_content_deduplication_complete": summary.get("geometry_content_deduplication_complete") is True,
        "summary_all_physical_components_enumerated": summary.get("all_physical_components_enumerated") is True,
        "summary_all_approximate_options_individually_verified": summary.get("all_approximate_options_individually_verified") is True,
    }
    return {
        "status": "PASS_RSI_WORKFLOW_CONTRACT" if not errors else "BLOCKED_RSI_WORKFLOW_CONTRACT",
        "rules_version": RULES_VERSION,
        "phase_order": ["object_table", "object_material_option_projection", "reverse_material_index", "property_evidence_ledger", "release_views"],
        "metrics": metrics,
        "pending_obligations": pending,
        "errors": errors,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_workflow_contract(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "out": str(args.out)}, ensure_ascii=False))
    if result["status"] != "PASS_RSI_WORKFLOW_CONTRACT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
