#!/usr/bin/env python3
"""Validate material-option cardinality and source-relation semantics."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


SINGLE_ASSIGNMENT = "SINGLE_ASSIGNMENT"
ALTERNATIVE = "PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS"
KNOWN_OPTION_RELATIONS = frozenset({SINGLE_ASSIGNMENT, ALTERNATIVE})
REGION_CLAIMS = frozenset({
    "SOURCE_AUTHORED_MATERIAL_REGION_BINDING_NOT_ALTERNATIVE_NOT_EXTRA_MECHANICAL_COMPONENT",
    "SOURCE_AUTHORED_BINDING_STATEMENT_NOT_ALTERNATIVE_NOT_VERIFIED_NONEMPTY_FACE_REGION",
})
VARIANT_CLAIM = "SOURCE_CONFIRMED_MATERIAL_VARIANT_NOT_SIMULTANEOUS"
REGION_PROOF_FIELDS = (
    "material_region_id", "binding_target", "binding_owner_prim_path",
    "base_geometry_prim_path", "geometry_membership_source_locator",
    "geometry_membership_review_id", "geometry_membership_reviewer",
    "geometry_membership_review_decision", "collector_id",
)
VARIANT_PROOF_FIELDS = (
    "material_variant_group_id", "material_variant_id", "variant_source_locator",
    "variant_review_id", "variant_reviewer", "variant_review_decision", "collector_id",
)
SOURCE_BINDING_FIELDS = (
    "relation_type", "source_quote", "source_locator", "source_local_file",
    "source_sha256", "binding_quote", "binding_source_file", "binding_source_sha256",
)


def _issue(code: str, message: str, samples: list[str]) -> dict:
    return {"code": code, "message": message, "count": len(samples), "samples": samples[:10]}


def audit_option_relation_semantics(rows: list[dict]) -> tuple[dict, list[dict]]:
    """Check that assignment rows encode one label or a well-formed alternative set."""
    errors: list[dict] = []
    bad_relation: list[str] = []
    bad_single: list[str] = []
    bad_alt_group: list[str] = []
    groups: dict[str, list[dict]] = defaultdict(list)
    relation_counts: Counter[str] = Counter()

    for index, row in enumerate(rows, 2):
        relation = row.get("assignment_relation", "").strip()
        group_id = row.get("assignment_option_group_id", "").strip()
        assignment_id = row.get("assignment_id", "").strip() or f"row {index}"
        relation_counts[relation or "<blank>"] += 1

        if relation not in KNOWN_OPTION_RELATIONS:
            bad_relation.append(f"{assignment_id}: {relation or '<blank>'}")
            continue

        if relation == SINGLE_ASSIGNMENT:
            if group_id:
                bad_single.append(f"{assignment_id}: singleton has option group {group_id}")
            if row.get("option_position", "").strip() != "1":
                bad_single.append(f"{assignment_id}: singleton position must be 1")
            continue

        if not group_id:
            bad_alt_group.append(f"{assignment_id}: alternative has no group ID")
            continue
        groups[group_id].append(row)

    for group_id, group_rows in groups.items():
        scope_keys = {
            tuple(row.get(field, "").strip() for field in (
                "source_row_id", "object_id", "component_id", "source_family", "source_asset_id"
            ))
            for row in group_rows
        }
        material_ids = [row.get("assigned_material_id", "").strip() for row in group_rows]
        positions: list[int] = []
        for row in group_rows:
            try:
                positions.append(int(row.get("option_position", "")))
            except (TypeError, ValueError):
                positions.append(-1)

        if len(group_rows) < 2:
            bad_alt_group.append(f"{group_id}: alternative group has fewer than two rows")
        if len(scope_keys) != 1:
            bad_alt_group.append(f"{group_id}: rows mix source/object/component scope")
        if any(not mid for mid in material_ids) or len(set(material_ids)) != len(material_ids):
            bad_alt_group.append(f"{group_id}: material IDs are blank or duplicated")
        if sorted(positions) != list(range(1, len(group_rows) + 1)):
            bad_alt_group.append(f"{group_id}: option positions must be unique and contiguous from 1")

    if bad_relation:
        errors.append(_issue(
            "OPTION_RELATION_UNKNOWN",
            "assignment_relation must be a declared one-label or non-simultaneous alternative relation",
            bad_relation,
        ))
    if bad_single:
        errors.append(_issue(
            "OPTION_SINGLE_ASSIGNMENT_MALFORMED",
            "single assignments require no option group and position 1",
            bad_single,
        ))
    if bad_alt_group:
        errors.append(_issue(
            "OPTION_ALTERNATIVE_GROUP_MALFORMED",
            "alternative groups must be scoped, multi-row, unique, and contiguous",
            bad_alt_group,
        ))

    return {
        "relation_counts": dict(sorted(relation_counts.items())),
        "alternative_groups": len(groups),
        "alternative_group_rows": sum(map(len, groups.values())),
        "malformed_relation_rows": len(bad_relation) + len(bad_single),
        "malformed_alternative_groups": len(bad_alt_group),
    }, errors


def audit_simready_component_relations(rows: list[dict]) -> tuple[dict, list[dict]]:
    """Preserve official SimReady bindings without inflating physical components.

    An official source-authored material binding is a valid source relation. This
    project policy does not require a face-level geometry audit to retain it;
    simultaneous regions are asserted only when independently reviewed region
    evidence is present. Unverified concurrency is recorded as unspecified.
    """
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        object_id = row.get("object_id", "").strip()
        component_id = row.get("component_id", "").strip()
        if object_id and component_id:
            grouped[(object_id, component_id)].append(row)

    findings: list[dict] = []
    classes: Counter[str] = Counter()
    for (object_id, component_id), group_rows in sorted(grouped.items()):
        labels = {
            row.get("canonical_material_id", "").strip()
            or row.get("source_label_normalized", "").strip()
            for row in group_rows
        } - {""}
        source_chain_incomplete = any(
            not row.get(field, "").strip() for row in group_rows for field in SOURCE_BINDING_FIELDS
        ) or any(
            row.get("audit_status", "").strip() != "SOURCE_CHAIN_VERIFIED_LOGIC_REVIEW_REQUIRED"
            for row in group_rows
        )
        if len(labels) < 2:
            relation_class = "SINGLE_SOURCE_MATERIAL_LABEL"
            reason = ""
        elif all(row.get("label_relationship", "").strip() in REGION_CLAIMS for row in group_rows):
            missing = sorted({
                field for row in group_rows for field in REGION_PROOF_FIELDS
                if not row.get(field, "").strip()
            })
            regions = [row.get("material_region_id", "").strip() for row in group_rows]
            invalid_reviews = [
                row.get("relation_id", "<missing relation id>")
                for row in group_rows
                if row.get("geometry_membership_review_decision", "").strip() != "PASS"
                or row.get("geometry_membership_reviewer", "").strip()
                == row.get("collector_id", "").strip()
            ]
            if source_chain_incomplete:
                relation_class = "HOLD_SOURCE_BINDING_PROVENANCE_INCOMPLETE"
                reason = "OFFICIAL_SOURCE_BINDING_CHAIN_MISSING_OR_NOT_VERIFIED"
            elif missing or invalid_reviews or len(set(regions)) != len(regions):
                relation_class = "SIMREADY_SOURCE_AUTHORED_BINDING_RELATIONS"
                reason = "OFFICIAL_SOURCE_RELATIONS_RETAINED;FACE_LEVEL_COVERAGE_NOT_SEPARATELY_REVIEWED"
            else:
                relation_class = "SIMULTANEOUS_MATERIAL_REGIONS_REVIEWED"
                reason = ""
        elif all(row.get("label_relationship", "").strip() == VARIANT_CLAIM for row in group_rows):
            missing = sorted({
                field for row in group_rows for field in VARIANT_PROOF_FIELDS
                if not row.get(field, "").strip()
            })
            variant_ids = [row.get("material_variant_id", "").strip() for row in group_rows]
            variant_groups = {row.get("material_variant_group_id", "").strip() for row in group_rows}
            invalid_reviews = [
                row.get("relation_id", "<missing relation id>")
                for row in group_rows
                if row.get("variant_review_decision", "").strip() != "PASS"
                or row.get("variant_reviewer", "").strip() == row.get("collector_id", "").strip()
            ]
            if source_chain_incomplete:
                relation_class = "HOLD_SOURCE_BINDING_PROVENANCE_INCOMPLETE"
                reason = "OFFICIAL_SOURCE_BINDING_CHAIN_MISSING_OR_NOT_VERIFIED"
            elif missing or invalid_reviews or len(set(variant_ids)) != len(variant_ids) or len(variant_groups) != 1:
                relation_class = "SIMREADY_SOURCE_REPORTED_MATERIAL_VARIANTS"
                reason_parts = ["SOURCE_VARIANT_RELATIONS_RETAINED"]
                if missing:
                    reason_parts.append("OPTIONAL_VARIANT_REVIEW_FIELDS_MISSING:" + ",".join(missing))
                if invalid_reviews:
                    reason_parts.append("OPTIONAL_VARIANT_REVIEW_NOT_INDEPENDENT_OR_NOT_PASS")
                if len(set(variant_ids)) != len(variant_ids) or len(variant_groups) != 1:
                    reason_parts.append("OPTIONAL_VARIANT_GROUP_IDS_NOT_UNIQUE_OR_CONSISTENT")
                reason = ";".join(reason_parts)
            else:
                relation_class = "ALTERNATIVE_MATERIAL_VARIANTS_REVIEWED"
                reason = ""
        else:
            if source_chain_incomplete:
                relation_class = "HOLD_SOURCE_BINDING_PROVENANCE_INCOMPLETE"
                reason = "OFFICIAL_SOURCE_BINDING_CHAIN_MISSING_OR_NOT_VERIFIED"
            else:
                relation_class = "SIMREADY_SOURCE_AUTHORED_BINDING_SCOPE_UNSPECIFIED"
                reason = "OFFICIAL_SOURCE_BINDINGS_RETAINED;RELATION_SCOPE_UNSPECIFIED"

        classes[relation_class] += 1
        relationship_kinds = {row.get("label_relationship", "").strip() for row in group_rows}
        if relationship_kinds == {"SOURCE_AUTHORED_MATERIAL_REGION_BINDING_NOT_ALTERNATIVE_NOT_EXTRA_MECHANICAL_COMPONENT"}:
            simultaneity_status = "SOURCE_DECLARED_MATERIAL_REGION_BINDINGS_FACE_COVERAGE_UNREVIEWED"
        elif relationship_kinds == {"SOURCE_AUTHORED_BINDING_STATEMENT_NOT_ALTERNATIVE_NOT_VERIFIED_NONEMPTY_FACE_REGION"}:
            simultaneity_status = "SOURCE_DECLARED_NONALTERNATIVE_BINDING_FACE_REGION_UNVERIFIED"
        elif relationship_kinds == {VARIANT_CLAIM}:
            simultaneity_status = "SOURCE_REPORTED_VARIANTS"
        elif relationship_kinds.intersection(REGION_CLAIMS):
            simultaneity_status = "SOURCE_BINDING_RELATIONSHIPS_RETAINED_DETAIL_MIXED"
        else:
            simultaneity_status = "NOT_ASSERTED"
        findings.append({
            "object_id": object_id,
            "component_id": component_id,
            "source_relation_rows": len(group_rows),
            "distinct_material_labels": len(labels),
            "relation_class": relation_class,
            "reason": reason,
            "simultaneity_status": simultaneity_status,
            "relation_ids": ";".join(row.get("relation_id", "").strip() for row in group_rows),
        })

    metrics = {
        "source_relation_rows": len(rows),
        "distinct_object_component_pairs": len(grouped),
        "multi_label_component_pairs": sum(1 for r in findings if r["distinct_material_labels"] > 1),
        "relation_class_counts": dict(sorted(classes.items())),
        "mechanical_component_count_delta_from_material_regions": 0,
        "policy": "Official binding relations are retained; geometry-level simultaneity is optional evidence, never a mechanical-component multiplier.",
    }
    return metrics, findings


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--simready-candidates", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, required=True)
    parser.add_argument("--findings-out", type=Path, required=True)
    args = parser.parse_args()
    metrics, findings = audit_simready_component_relations(_read_csv(args.simready_candidates))
    args.report_out.parent.mkdir(parents=True, exist_ok=True)
    args.findings_out.parent.mkdir(parents=True, exist_ok=True)
    args.report_out.write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = list(findings[0]) if findings else [
        "object_id", "component_id", "source_relation_rows", "distinct_material_labels",
        "relation_class", "reason", "simultaneity_status", "relation_ids",
    ]
    with args.findings_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(findings)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
