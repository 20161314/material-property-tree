#!/usr/bin/env python3
"""Fail-closed release gate for the RSI 2.4 shadow workflow.

The gate checks the files that actually feed the three site views.  It does
not repair facts or infer materials.  A failed gate produces a diagnostic
report and, optionally, a deterministic queue for unresolved object rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
from typing import Iterable

from project_paths_v24 import resolve_project_input
from relation_contract_v24 import audit_option_relation_semantics
from release_identity_v24 import parse_release_pointer
from workflow_contract_v24 import run_workflow_contract, SOURCE_COVERAGE_REL, TAXONOMY_REL
from evidence_route_contract_v24 import ROUTES_REL, POLICY_REL
from object_alias_projection_v24 import load_alias_projection, AliasValidationError


OBJECT_FILE = Path("data/scaling_release_v1/object_component_inventory.csv")
MATERIAL_FILE = Path("data/current_two_table_delivery_v1/material_reverse_index_and_property_ranges.csv")
OPTION_FILE = Path("data/current_two_table_delivery_v1/current_material_options.csv")
EVIDENCE_FILE = Path("data/current_two_table_delivery_v1/main_property_source_groups.csv")
SUMMARY_FILE = Path("data/current_two_table_delivery_v1/summary.json")
SCOPE_POLICY_FILE = Path("data/material_scope_policy.json")
POINTER_FILE = Path("current_release_pointer.md")

# Bookkeeping sentinels are not material identities and must never satisfy the
# object -> material foreign-key check.
UNRESOLVED_MATERIAL_IDS = frozenset({"", "UNMAPPED", "NOT_MAPPED", "UNASSIGNED", "UNKNOWN"})
SPECIAL_DOMAIN_VOID_LABELS = frozenset({"N/A (Empty Space)", "Empty Space", "N/A (empty space)"})
EXPLICIT_NON_MATERIAL_IDS = frozenset({"SPECIAL-DOMAIN-VOID"})

OBJECT_REQUIRED = (
    "object_id", "component_id", "source_dataset", "source_asset_id",
    "object_name_en", "object_name_cn", "component_scope", "material_label",
    "mapping_source_ids", "mapping_evidence", "asset_status",
    "source_record_locator",
)
EVIDENCE_REQUIRED = (
    "record_id", "material_identity", "source_id", "document_key",
    "url", "locator", "local_file", "sha256", "unique_record_key",
)
EVIDENCE_VALUES = ("E_low_GPa", "nu_low", "rho_low_kg_m3")
EVIDENCE_BOUND_PAIRS = (
    ("E_low_GPa", "E_high_GPa"),
    ("nu_low", "nu_high"),
    ("rho_low_kg_m3", "rho_high_kg_m3"),
)
EVIDENCE_SOURCE_VALUE_FIELDS = (
    "E_source_value", "nu_source_value", "rho_source_value",
    "source_reported_values_json", "reported_values_json",
    "directional_values_json", "measured_values_json",
    "property_observations_json", "source_observations_json",
    "source_subresults_json",
)
OPTION_REQUIRED = (
    "assignment_id", "source_row_id", "object_id", "component_id",
    "source_family", "source_asset_id", "assigned_material_id",
    "assignment_relation", "assignment_option_group_id", "option_position",
    "assignment_basis", "original_admission_status", "source_record_locator",
)
RULES_VERSION = "2.4.3-H4"
EVIDENCE_SOURCE_FLAGS = (
    "source_is_model_or_solver_input", "simulation_numerical_assignment",
    "property_value_origin", "source_value_origin", "admission_recommendation",
    "source_parameter_validity",
)
DISALLOWED_PROPERTY_ORIGIN = re.compile(
    r"(?i)\b(predicted|model\s+generated|generated\s+by\s+model|"
    r"ai\s+generated|generated\s+by\s+ai|vlm|clip|llm|"
    r"solver\s+default|solver\s+input|simulation\s+input)\b"
)
NEGATED_PROPERTY_ORIGIN = re.compile(
    r"(?i)\b(?:not|no|without|non)\s+(?:(?:validated|verified|a|an|the)\s+)*"
    r"(?:predicted|model\s+generated|generated\s+by\s+model|ai\s+generated|"
    r"generated\s+by\s+ai|solver\s+default|solver\s+input|simulation\s+input)\b"
)


def _is_disallowed_property_origin(value: str) -> bool:
    normalized = re.sub(r"[_-]+", " ", value.strip().lower())
    normalized = NEGATED_PROPERTY_ORIGIN.sub(" ", normalized)
    return bool(DISALLOWED_PROPERTY_ORIGIN.search(normalized))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _issue(code: str, message: str, count: int = 1, samples: Iterable[str] = ()) -> dict:
    return {"code": code, "message": message, "count": count,
            "samples": list(samples)[:10]}


def _required_file(root: Path, rel: Path) -> tuple[Path | None, list[dict]]:
    path = root / rel
    if not path.is_file():
        return None, [_issue("MISSING_REQUIRED_FILE", str(rel))]
    return path, []


def _pointer_release_id(path: Path) -> str | None:
    return parse_release_pointer(path)


def audit_object_table(
    path: Path,
    expected: dict,
    queue_path: Path | None = None,
    known_material_ids: set[str] | None = None,
    excluded_material_ids: set[str] | None = None,
    identity_projection=None,
    projected_inventory=None,
) -> tuple[dict, list[dict], list[dict]]:
    errors: list[dict] = []
    queue: list[dict] = []
    duplicate_counts: Counter[tuple[str, ...]] = Counter()
    raw_object_ids: set[str] = set()
    raw_component_pairs: set[tuple[str, str]] = set()
    object_ids: set[str] = set()
    component_pairs: set[tuple[str, str]] = set()
    rows = 0
    blank_required = Counter()
    unresolved_by_reason: Counter[str] = Counter()
    excluded_scope_rows = 0
    special_domain_rows = 0
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [c for c in OBJECT_REQUIRED if c not in (reader.fieldnames or [])]
        if missing_columns:
            errors.append(_issue("OBJECT_SCHEMA_MISSING_COLUMNS", "object table schema is incomplete",
                                 len(missing_columns), missing_columns))
        for row in (projected_inventory if projected_inventory is not None else reader):
            rows += 1
            raw_object_ids.add(row.get("object_id", "").strip())
            raw_component_pairs.add((row.get("object_id", "").strip(), row.get("component_id", "").strip()))
            if identity_projection is not None:
                try:
                    row = identity_projection.project(row)
                except AliasValidationError as exc:
                    errors.append(_issue("OBJECT_ALIAS_PREIMAGE_INVALID", str(exc)))
            object_id = row.get("object_id", "").strip()
            component_id = row.get("component_id", "").strip()
            material_id = row.get("material_node_id", "").strip()
            material_label = row.get("material_label", "").strip()
            status = row.get("material_identity_status", "").strip()
            object_ids.add(object_id)
            component_pairs.add((object_id, component_id))
            key = tuple(row.get(c, "").strip() for c in (
                "object_id", "component_id", "material_node_id", "material_label",
                "material_identity_status", "mapping_source_ids", "mapping_evidence"))
            duplicate_counts[key] += 1
            for field in OBJECT_REQUIRED:
                if not row.get(field, "").strip():
                    blank_required[field] += 1
            raw_material_text = " | ".join(
                row.get(field, "").strip()
                for field in ("material_label", "component_material_label_raw", "material_candidate_raw")
            )
            is_special_domain_void = any(label in raw_material_text for label in SPECIAL_DOMAIN_VOID_LABELS)
            unresolved_reason = None
            if is_special_domain_void and row.get("source_dataset", "").strip() == "PHYSX-MOBILITY":
                special_domain_rows += 1
                # Retain the source row for audit, but do not treat it as an
                # unresolved solid material mapping.
                continue
            if material_id in UNRESOLVED_MATERIAL_IDS:
                if material_id == "UNMAPPED":
                    unresolved_reason = "MATERIAL_NODE_SENTINEL_UNMAPPED"
                elif material_id:
                    unresolved_reason = "MATERIAL_NODE_SENTINEL_UNRESOLVED"
            elif excluded_material_ids and material_id in excluded_material_ids:
                excluded_scope_rows += 1
            elif known_material_ids is not None and material_id not in known_material_ids:
                unresolved_reason = "ORPHAN_MATERIAL_NODE_REFERENCE"

            if unresolved_reason or not material_id:
                if "GoogleResearch Scanned Objects" in row.get("source_dataset", ""):
                    reason = "SOURCE_MANIFEST_NO_MATERIAL"
                elif "3DCoMPaT++" in row.get("source_dataset", ""):
                    reason = "NO_ACCEPTED_SOURCE_OPTION"
                elif unresolved_reason:
                    reason = unresolved_reason
                else:
                    reason = "UNRESOLVED_MATERIAL_ID"
                unresolved_by_reason[reason] += 1
                stable_key = "\x1f".join(row.get(c, "").strip() for c in (
                    "object_id", "component_id", "source_dataset", "source_asset_id",
                    "source_record_locator", "material_node_id", "material_label", "mapping_evidence"))
                queue.append({
                    "queue_id": "MATERIAL-MAP-" + hashlib.sha256(stable_key.encode("utf-8")).hexdigest()[:20].upper(),
                    "reason_code": reason,
                    "object_id": object_id,
                    "component_id": component_id,
                    "source_dataset": row.get("source_dataset", ""),
                    "source_asset_id": row.get("source_asset_id", ""),
                    "material_node_id": material_id,
                    "object_name_en": row.get("object_name_en", ""),
                    "object_name_cn": row.get("object_name_cn", ""),
                    "component_scope": row.get("component_scope", ""),
                    "source_record_locator": row.get("source_record_locator", ""),
                    "original_material_label": material_label,
                    "material_identity_status": status,
                    "mapping_evidence": row.get("mapping_evidence", ""),
                    "next_action": "优先查作者或官方材料说明；依当前用户授权，也可结合来源对象角色、类别定义及构造合理性独立审核粗粒度近似标签，保留依据与范围。角色冲突未解时保持 HOLD；不得据此生成 E/nu/rho。",
                })
    alias_metrics = {}
    if identity_projection is not None:
        try:
            alias_metrics = identity_projection.finish(expected, raw_object_ids, object_ids)
        except AliasValidationError as exc:
            errors.append(_issue("OBJECT_ALIAS_PROJECTION_INCOMPLETE", str(exc)))
    duplicate_rows = sum(n - 1 for n in duplicate_counts.values() if n > 1)
    if duplicate_rows:
        errors.append(_issue("DUPLICATE_OBJECT_MATERIAL_KEY", "exact object/component/material evidence key repeats",
                             duplicate_rows, ["|".join(k[:4]) for k, n in duplicate_counts.items() if n > 1]))
    if rows != expected.get("state_rows"):
        errors.append(_issue("OBJECT_ROW_COUNT_DRIFT", f"actual rows {rows} != summary state_rows {expected.get('state_rows')}"))
    if len(object_ids) != expected.get("object_identities"):
        errors.append(_issue("OBJECT_IDENTITY_COUNT_DRIFT", f"actual identities {len(object_ids)} != summary object_identities {expected.get('object_identities')}"))
    if len(component_pairs) != expected.get("distinct_component_pairs"):
        errors.append(_issue("COMPONENT_PAIR_COUNT_DRIFT", f"actual pairs {len(component_pairs)} != summary distinct_component_pairs {expected.get('distinct_component_pairs')}"))
    if blank_required:
        # Material ID may be blank only in the explicit repair queue. All other
        # identity and provenance fields must be present on every row.
        illegal = {k: v for k, v in blank_required.items() if k != "material_label"}
        if illegal:
            errors.append(_issue("OBJECT_REQUIRED_FIELD_BLANK", "formal object identity/provenance field is blank",
                                 sum(illegal.values()), [f"{k}={v}" for k, v in illegal.items()]))
    queue.sort(key=lambda item: item["queue_id"])
    if queue_path is not None:
        queue_path.parent.mkdir(parents=True, exist_ok=True)
        fields = list(queue[0]) if queue else [
            "queue_id", "reason_code", "object_id", "component_id", "source_dataset",
            "source_asset_id", "material_node_id", "object_name_en", "object_name_cn", "component_scope",
            "source_record_locator", "original_material_label", "material_identity_status",
            "mapping_evidence", "next_action"]
        with queue_path.open("w", encoding="utf-8", newline="") as out:
            writer = csv.DictWriter(out, fieldnames=fields)
            writer.writeheader()
            writer.writerows(queue)
    metrics = {
        "rows": rows, "object_identities": len(object_ids),
        "raw_object_identities": len(raw_object_ids), "canonical_object_identities": len(object_ids),
        "raw_distinct_component_pairs": len(raw_component_pairs),
        "canonical_distinct_component_pairs": len(component_pairs), "identity_alias_projection": alias_metrics,
        "distinct_component_pairs": len(component_pairs),
        "exact_duplicate_rows": duplicate_rows,
        "missing_material_node_rows": len(queue),
        "resolved_material_node_rows": rows - len(queue) - excluded_scope_rows - special_domain_rows,
        "missing_material_by_reason": dict(unresolved_by_reason),
        "excluded_scope_rows": excluded_scope_rows,
        "special_domain_rows": special_domain_rows,
        "blank_required_fields": dict(blank_required),
    }
    return metrics, errors, queue


def audit_option_table(
    path: Path,
    expected: dict,
    object_pairs: set[tuple[str, str]],
    known_material_ids: set[str],
    excluded_material_ids: set[str] | None = None,
) -> tuple[dict, list[dict]]:
    """Audit the material-option projection used by the object/material views.

    The option table is a first-class release input.  It may contain several
    mutually exclusive options for one object/component, but every option must
    point to an existing object/component pair and to a current material node
    (or an explicit historical exclusion).  This check never chooses among
    alternatives and never creates a Cartesian product.
    """
    errors: list[dict] = []
    excluded_material_ids = excluded_material_ids or set()
    relation_rows: list[dict] = []
    rows = 0
    assignments: set[str] = set()
    orphan_pairs: list[str] = []
    orphan_materials: list[str] = []
    invalid_positions: list[str] = []
    blank_ids: list[str] = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [c for c in OPTION_REQUIRED if c not in (reader.fieldnames or [])]
        if missing_columns:
            errors.append(_issue("OPTION_SCHEMA_MISSING_COLUMNS", "material option table schema is incomplete",
                                 len(missing_columns), missing_columns))
        for row in reader:
            relation_rows.append(row)
            rows += 1
            assignment_id = row.get("assignment_id", "").strip()
            if not assignment_id or assignment_id in assignments:
                blank_ids.append(f"row {rows}: {assignment_id or '<blank>'}")
            assignments.add(assignment_id)
            pair = (row.get("object_id", "").strip(), row.get("component_id", "").strip())
            if pair not in object_pairs:
                orphan_pairs.append(f"row {rows}: {pair[0]}|{pair[1]}")
            material_id = row.get("assigned_material_id", "").strip()
            if not material_id or material_id in UNRESOLVED_MATERIAL_IDS:
                orphan_materials.append(f"row {rows}: {material_id or '<blank>'}")
            elif (material_id not in known_material_ids and material_id not in excluded_material_ids
                  and material_id not in EXPLICIT_NON_MATERIAL_IDS):
                orphan_materials.append(f"row {rows}: {material_id}")
            position = row.get("option_position", "").strip()
            try:
                if int(position) < 1:
                    raise ValueError
            except (TypeError, ValueError):
                invalid_positions.append(f"row {rows}: {position or '<blank>'}")
    expected_rows = expected.get("current_material_option_rows")
    if expected_rows is not None and rows != expected_rows:
        errors.append(_issue("OPTION_ROW_COUNT_DRIFT",
                             f"actual rows {rows} != summary current_material_option_rows {expected_rows}"))
    if blank_ids:
        errors.append(_issue("DUPLICATE_OR_BLANK_OPTION_ASSIGNMENT_ID",
                             "assignment_id must be nonblank and unique", len(blank_ids), blank_ids))
    if orphan_pairs:
        errors.append(_issue("OPTION_ORPHAN_OBJECT_COMPONENT",
                             "material option references an object/component pair absent from the object table",
                             len(orphan_pairs), orphan_pairs))
    if orphan_materials:
        errors.append(_issue("OPTION_ORPHAN_MATERIAL_REFERENCE",
                             "material option references an unresolved or absent material node",
                             len(orphan_materials), orphan_materials))
    if invalid_positions:
        errors.append(_issue("OPTION_POSITION_INVALID",
                             "option_position must be a positive integer", len(invalid_positions), invalid_positions))
    relation_metrics, relation_errors = audit_option_relation_semantics(relation_rows)
    errors.extend(relation_errors)
    return {
        "rows": rows,
        "unique_assignment_ids": len(assignments - {""}),
        "orphan_object_component_rows": len(orphan_pairs),
        "orphan_material_rows": len(orphan_materials),
        "invalid_option_position_rows": len(invalid_positions),
        "relation_semantics": relation_metrics,
    }, errors


def audit_material_table(path: Path, expected: dict) -> tuple[dict, list[dict]]:
    errors: list[dict] = []
    ids: set[str] = set()
    rows = 0
    invalid_ranges = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows += 1
            mid = row.get("material_id", "").strip()
            if not mid:
                invalid_ranges.append(f"row {rows}: blank material_id")
            if mid in ids:
                invalid_ranges.append(f"row {rows}: duplicate material_id {mid}")
            ids.add(mid)
            for lo, hi in (("E_min_GPa", "E_max_GPa"), ("nu_min", "nu_max"), ("rho_min_kg_m3", "rho_max_kg_m3")):
                lo_value, hi_value = row.get(lo, "").strip(), row.get(hi, "").strip()
                parsed = {}
                for field, value in ((lo, lo_value), (hi, hi_value)):
                    if value:
                        try:
                            parsed[field] = float(value)
                            if not math.isfinite(parsed[field]):
                                raise ValueError("non-finite")
                        except ValueError:
                            invalid_ranges.append(f"row {rows}: nonnumeric {field}")
                if lo_value and hi_value and lo in parsed and hi in parsed and parsed[lo] > parsed[hi]:
                    invalid_ranges.append(f"row {rows}: {lo}>{hi}")
    if rows != expected.get("material_nodes"):
        errors.append(_issue("MATERIAL_ROW_COUNT_DRIFT", f"actual rows {rows} != summary material_nodes {expected.get('material_nodes')}"))
    if invalid_ranges:
        errors.append(_issue("MATERIAL_TABLE_INVALID", "material IDs or ranges are invalid",
                             len(invalid_ranges), invalid_ranges))
    return {"rows": rows, "unique_material_ids": len(ids), "invalid_range_rows": len(invalid_ranges)}, errors


def audit_evidence(path: Path, expected: dict) -> tuple[dict, list[dict]]:
    errors: list[dict] = []
    unique_keys: set[str] = set()
    rows = complete = partial = 0
    bad_complete_provenance = []
    bad_complete_origin = []
    bad_complete_numeric = []
    bad_partial_provenance = []
    bad_partial_origin = []
    bad_partial_numeric = []
    bad_empty_property = []
    partial_without_numeric_normalization = []
    bad_numeric = []
    numeric_warnings = []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing_columns = [c for c in EVIDENCE_REQUIRED + EVIDENCE_VALUES if c not in (reader.fieldnames or [])]
        if missing_columns:
            errors.append(_issue("EVIDENCE_SCHEMA_MISSING_COLUMNS", "evidence ledger schema is incomplete",
                                 len(missing_columns), missing_columns))
        for row in reader:
            rows += 1
            key = row.get("unique_record_key", "").strip()
            if key in unique_keys:
                errors.append(_issue("DUPLICATE_EVIDENCE_KEY", "unique_record_key repeats", 1, [key]))
            unique_keys.add(key)
            is_complete = all(row.get(k, "").strip() for k in EVIDENCE_VALUES)
            # Parse every populated bound, including partial rows.  A malformed
            # high bound must not be hidden by a valid low bound.
            parsed_bounds = {}
            row_numeric_bad = False
            for lo, hi in EVIDENCE_BOUND_PAIRS:
                for field in (lo, hi):
                    value = row.get(field, "").strip()
                    if not value:
                        continue
                    try:
                        parsed_bounds[field] = float(value)
                        if not math.isfinite(parsed_bounds[field]):
                            raise ValueError("non-finite")
                    except (TypeError, ValueError):
                        row_numeric_bad = True
                        bad_numeric.append(f"{key}: nonnumeric/nonfinite {field}")
                if lo in parsed_bounds and hi in parsed_bounds and parsed_bounds[hi] < parsed_bounds[lo]:
                    row_numeric_bad = True
                    bad_numeric.append(f"{key}: {hi}<{lo}")
            if "nu_low" in parsed_bounds and not (-1.0 <= parsed_bounds["nu_low"] <= 0.5):
                numeric_warnings.append(f"{key}: nu_low outside conventional isotropic range")
            if "nu_high" in parsed_bounds and not (-1.0 <= parsed_bounds["nu_high"] <= 0.5):
                numeric_warnings.append(f"{key}: nu_high outside conventional isotropic range")
            has_numeric_values = any(row.get(k, "").strip() for k in EVIDENCE_VALUES + tuple(
                bound for pair in EVIDENCE_BOUND_PAIRS for bound in pair
            ))
            has_source_values = any(
                row.get(k, "").strip().lower() not in {"", "[]", "{}", "null", "none"}
                for k in EVIDENCE_SOURCE_VALUE_FIELDS
            )
            has_values = has_numeric_values or has_source_values
            if not has_values:
                bad_empty_property.append(f"{key}: no normalized or source-reported property value")
            if not is_complete and has_values:
                if not has_numeric_values and has_source_values:
                    partial_without_numeric_normalization.append(key)
                missing = [k for k in EVIDENCE_REQUIRED if not row.get(k, "").strip()]
                if missing:
                    bad_partial_provenance.append(f"{key}: {','.join(missing)}")
                material_identity = row.get("material_identity", "").strip().lower()
                if not material_identity or material_identity in {"unknown", "unmapped", "not_mapped", "unassigned"}:
                    bad_partial_origin.append(f"{key}: blank/placeholder material_identity")
                for field in EVIDENCE_SOURCE_FLAGS:
                    value = row.get(field, "").strip()
                    if _is_disallowed_property_origin(value):
                        bad_partial_origin.append(f"{key}: {field}={value}")
                for field in ("source_is_model_or_solver_input", "simulation_numerical_assignment"):
                    value = row.get(field, "").strip().lower()
                    if value in {"yes", "true", "1", "model_input", "solver_input", "simulation_input"}:
                        bad_partial_origin.append(f"{key}: {field}={value}")
                for field in ("E_low_GPa", "E_high_GPa", "rho_low_kg_m3", "rho_high_kg_m3"):
                    if field in parsed_bounds and parsed_bounds[field] <= 0:
                        bad_partial_numeric.append(f"{key}: {field} must be positive")
            if is_complete:
                complete += 1
                if row_numeric_bad:
                    bad_complete_numeric.append(f"{key}: invalid bound encoding")
                missing = [k for k in EVIDENCE_REQUIRED if not row.get(k, "").strip()]
                if missing:
                    bad_complete_provenance.append(f"{key}: {','.join(missing)}")
                material_identity = row.get("material_identity", "").strip().lower()
                if not material_identity or material_identity in {"unknown", "unmapped", "not_mapped", "unassigned"}:
                    bad_complete_origin.append(f"{key}: blank/placeholder material_identity")
                for field in EVIDENCE_SOURCE_FLAGS:
                    value = row.get(field, "").strip()
                    if _is_disallowed_property_origin(value):
                        bad_complete_origin.append(f"{key}: {field}={value}")
                for field in ("source_is_model_or_solver_input", "simulation_numerical_assignment"):
                    value = row.get(field, "").strip().lower()
                    if value in {"yes", "true", "1", "model_input", "solver_input", "simulation_input"}:
                        bad_complete_origin.append(f"{key}: {field}={value}")
                try:
                    numeric = {field: float(row.get(field, "")) for field in EVIDENCE_VALUES}
                    if not all(math.isfinite(value) for value in numeric.values()):
                        raise ValueError("non-finite")
                    if numeric["E_low_GPa"] <= 0 or numeric["rho_low_kg_m3"] <= 0:
                        bad_complete_numeric.append(f"{key}: E/rho must be positive")
                except (TypeError, ValueError):
                    bad_complete_numeric.append(f"{key}: nonnumeric/nonfinite complete E/nu/rho")
            else:
                partial += 1
    if rows != expected.get("main_source_groups"):
        errors.append(_issue("EVIDENCE_ROW_COUNT_DRIFT", f"actual rows {rows} != summary main_source_groups {expected.get('main_source_groups')}"))
    if complete != expected.get("main_complete_groups"):
        errors.append(_issue("EVIDENCE_COMPLETE_COUNT_DRIFT", f"actual complete rows {complete} != summary main_complete_groups {expected.get('main_complete_groups')}"))
    if partial != expected.get("main_partial_groups"):
        errors.append(_issue("EVIDENCE_PARTIAL_COUNT_DRIFT", f"actual partial rows {partial} != summary main_partial_groups {expected.get('main_partial_groups')}"))
    if bad_complete_provenance:
        errors.append(_issue("COMPLETE_EVIDENCE_MISSING_PROVENANCE", "complete E/nu/rho row lacks source locator or file identity",
                             len(bad_complete_provenance), bad_complete_provenance))
    if bad_complete_origin:
        errors.append(_issue("COMPLETE_EVIDENCE_DISALLOWED_ORIGIN", "complete group is model/solver/AI derived or lacks a material identity",
                             len(bad_complete_origin), bad_complete_origin))
    if bad_partial_provenance:
        errors.append(_issue("PARTIAL_EVIDENCE_MISSING_PROVENANCE", "partial property row lacks material/source identity or locator",
                             len(bad_partial_provenance), bad_partial_provenance))
    if bad_partial_origin:
        errors.append(_issue("PARTIAL_EVIDENCE_DISALLOWED_ORIGIN", "partial property row is model/solver/AI derived or lacks a material identity",
                             len(bad_partial_origin), bad_partial_origin))
    if bad_partial_numeric:
        errors.append(_issue("PARTIAL_EVIDENCE_INVALID_NUMERIC", "partial property row contains nonpositive E or density",
                             len(bad_partial_numeric), bad_partial_numeric))
    if bad_empty_property:
        errors.append(_issue("EVIDENCE_GROUP_WITHOUT_PROPERTY_VALUE",
                             "evidence group contains no normalized or source-reported property value",
                             len(bad_empty_property), bad_empty_property))
    if bad_numeric:
        errors.append(_issue("EVIDENCE_INVALID_NUMERIC", "evidence ledger contains malformed numeric bounds",
                             len(bad_numeric), bad_numeric))
    if bad_complete_numeric:
        errors.append(_issue("COMPLETE_EVIDENCE_INVALID_NUMERIC", "complete group contains invalid E/nu/rho values or bounds",
                             len(bad_complete_numeric), bad_complete_numeric))
    return {"rows": rows, "unique_record_keys": len(unique_keys), "complete": complete, "partial": partial,
            "complete_missing_provenance": len(bad_complete_provenance),
            "complete_disallowed_origin": len(bad_complete_origin),
            "complete_invalid_numeric": len(bad_complete_numeric),
            "partial_missing_provenance": len(bad_partial_provenance),
            "partial_disallowed_origin": len(bad_partial_origin),
            "partial_invalid_numeric": len(bad_partial_numeric),
            "partial_without_numeric_normalization": len(partial_without_numeric_normalization),
            "partial_without_numeric_normalization_samples": partial_without_numeric_normalization[:10],
            "empty_property_rows": len(bad_empty_property),
            "numeric_warning_rows": len(numeric_warnings),
            "numeric_warning_samples": numeric_warnings[:10]}, errors


def verify_input_pins(root: Path, summary: dict) -> tuple[dict, list[dict]]:
    errors: list[dict] = []
    checked = missing = mismatched = unsafe = 0
    pins = summary.get("input_sha256", {})
    if not isinstance(pins, dict):
        return ({"checked": 0, "missing": 0, "mismatched": 0, "unsafe": 0, "undeclared": 10},
                [_issue("INPUT_PINS_INVALID", "summary input_sha256 must be a path-to-SHA256 object")])
    required_pin_files = (OBJECT_FILE, MATERIAL_FILE, OPTION_FILE, EVIDENCE_FILE, SCOPE_POLICY_FILE,
                          POINTER_FILE, SOURCE_COVERAGE_REL, TAXONOMY_REL, ROUTES_REL, POLICY_REL)
    undeclared = [str(path) for path in required_pin_files if str(path) not in pins]
    if undeclared:
        errors.append(_issue("INPUT_PIN_UNDECLARED",
                             "a release-gate input is not listed in summary input_sha256",
                             len(undeclared), undeclared))
    unsafe_paths: list[str] = []
    for rel, expected_hash in pins.items():
        path = resolve_project_input(root, rel)
        if path is None:
            unsafe += 1
            unsafe_paths.append(str(rel))
            continue
        if not path.is_file():
            missing += 1
            continue
        checked += 1
        if _sha256(path) != expected_hash:
            mismatched += 1
    if missing:
        errors.append(_issue("INPUT_PIN_MISSING", "summary input pin points to a missing file", missing))
    if mismatched:
        errors.append(_issue("INPUT_PIN_MISMATCH", "summary input pin does not match file bytes", mismatched))
    if unsafe:
        errors.append(_issue("INPUT_PIN_PATH_OUTSIDE_ROOT", "summary input pin must resolve to a file inside the release root", unsafe, unsafe_paths))
    return {"checked": checked, "missing": missing, "mismatched": mismatched, "unsafe": unsafe,
            "undeclared": len(undeclared)}, errors


def run_gate(root: Path, queue_path: Path | None = None) -> dict:
    root = root.resolve()
    errors: list[dict] = []
    workflow_contract = run_workflow_contract(root)
    if workflow_contract.get("status") != "PASS_RSI_WORKFLOW_CONTRACT":
        errors.append(_issue(
            "WORKFLOW_CONTRACT_BLOCKED",
            "object-first phase contract failed; inspect its detailed errors",
            len(workflow_contract.get("errors", [])) or 1,
            [e.get("code", "") for e in workflow_contract.get("errors", [])],
        ))
    summary_path, issues = _required_file(root, SUMMARY_FILE)
    errors.extend(issues)
    if summary_path is None:
        return {"status": "BLOCKED_RSI_V24_RELEASE_GATE", "errors": errors,
                "workflow_contract": workflow_contract, "rules_version": RULES_VERSION}
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    pointer_id = _pointer_release_id(root / POINTER_FILE)
    if not pointer_id:
        errors.append(_issue(
            "RELEASE_POINTER_MISSING_OR_INVALID",
            "current_release_pointer.md must contain one parseable release ID; a missing pointer cannot publish",
        ))
    pin_metrics, pin_errors = verify_input_pins(root, summary)
    errors.extend(pin_errors)
    if summary.get("status") != "PASS_CURRENT_TWO_TABLE_DELIVERY":
        errors.append(_issue("SUMMARY_STATUS_NOT_PASS", "summary status is not PASS_CURRENT_TWO_TABLE_DELIVERY"))
    for flag in ("geometry_content_deduplication_complete", "all_physical_components_enumerated",
                 "all_approximate_options_individually_verified"):
        if summary.get(flag) is not True:
            errors.append(_issue("RELEASE_COMPLETENESS_FLAG_FALSE", f"{flag} is false; release cannot claim complete coverage"))
    object_path, e = _required_file(root, OBJECT_FILE); errors.extend(e)
    material_path, e = _required_file(root, MATERIAL_FILE); errors.extend(e)
    option_path, e = _required_file(root, OPTION_FILE); errors.extend(e)
    evidence_path, e = _required_file(root, EVIDENCE_FILE); errors.extend(e)
    scope_path, e = _required_file(root, SCOPE_POLICY_FILE); errors.extend(e)
    metrics = {"input_pins": pin_metrics, "pointer_release_id": pointer_id}
    queue: list[dict] = []
    known_material_ids: set[str] | None = None
    excluded_material_ids: set[str] = set(summary.get("excluded_liquid_material_ids", []))
    if scope_path:
        try:
            scope = json.loads(scope_path.read_text(encoding="utf-8"))
            excluded_material_ids.update(scope.get("excluded_material_ids", []))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(_issue("SCOPE_POLICY_INVALID", f"cannot read material scope policy: {exc}"))
    if material_path:
        with material_path.open(encoding="utf-8-sig", newline="") as handle:
            known_material_ids = {
                row.get("material_id", "").strip()
                for row in csv.DictReader(handle)
                if row.get("material_id", "").strip()
            }
    identity_projection = None
    try:
        identity_projection = load_alias_projection(root, summary)
    except (AliasValidationError, OSError, ValueError, KeyError) as exc:
        errors.append(_issue("OBJECT_ALIAS_PROJECTION_INVALID", str(exc)))
    from current_object_inventory_v24 import iter_inventory
    object_pairs: set[tuple[str, str]] = set()
    if object_path:
        m, e, queue = audit_object_table(
            object_path, summary, queue_path, known_material_ids, excluded_material_ids, identity_projection,
            iter_inventory(root, summary)
        )
        metrics["objects"] = m; errors.extend(e)
        with object_path.open(encoding="utf-8-sig", newline="") as handle:
            object_pairs = {identity_projection.canonical_pair(row) if identity_projection is not None else
                            (row.get("object_id", "").strip(), row.get("component_id", "").strip())
                            for row in iter_inventory(root, summary)}
    if option_path and known_material_ids is not None:
        m, e = audit_option_table(option_path, summary, object_pairs, known_material_ids, excluded_material_ids)
        metrics["options"] = m; errors.extend(e)
    if material_path:
        m, e = audit_material_table(material_path, summary)
        metrics["materials"] = m; errors.extend(e)
    if evidence_path:
        m, e = audit_evidence(evidence_path, summary)
        metrics["evidence"] = m; errors.extend(e)
    if queue:
        errors.append(_issue("UNRESOLVED_MATERIAL_MAPPING_QUEUE", "object rows lack an accepted material node; release remains blocked",
                             len(queue), [x["reason_code"] for x in queue]))
    status = "PASS_RSI_V24_RELEASE_GATE" if not errors else "BLOCKED_RSI_V24_RELEASE_GATE"
    return {"status": status, "release_id": pointer_id, "errors": errors, "metrics": metrics,
            "queue_rows": len(queue), "rules_version": RULES_VERSION,
            "workflow_contract": workflow_contract}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--queue-out", type=Path)
    parser.add_argument("--report-out", type=Path)
    args = parser.parse_args()
    result = run_gate(args.root, args.queue_out)
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    print(encoded)
    if args.report_out:
        args.report_out.parent.mkdir(parents=True, exist_ok=True)
        args.report_out.write_text(encoded + "\n", encoding="utf-8")
    if result["status"] != "PASS_RSI_V24_RELEASE_GATE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
