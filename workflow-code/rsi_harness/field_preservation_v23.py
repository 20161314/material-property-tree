"""Field-level evidence for release-to-release row migrations.

Identity/locator crosswalks alone do not prove that source row content was
preserved. This module records direct, aliased, numerically equivalent, nested,
archive-only, and unresolved field dispositions for a frozen source row.
"""

from __future__ import annotations

import hashlib
import json
import re
from decimal import Decimal, InvalidOperation


FIELD_ALIASES = {
    "conditions_or_group": ("conditions",),
    "publisher": ("publisher_subject_name",),
    "source_document_id": ("document_key",),
}

PROPERTY_JSON_ALIASES = {
    "unit_E_original": ("E", "unit_original"),
    "unit_nu_original": ("nu", "unit_original"),
    "unit_rho_original": ("rho", "unit_original"),
    "E_source_locator": ("E", "locator"),
    "nu_source_locator": ("nu", "locator"),
    "rho_source_locator": ("rho", "locator"),
}

# These are not inferred aliases.  They are only emitted by a validated,
# independently reviewed field-repair manifest.  Keeping them in the audit
# vocabulary makes canonical re-keying visible while allowing the row to pass
# once the repair's preimage and basis have been checked.
REVIEWED_REPAIR_STATUSES = {
    "REVIEWED_MATERIAL_MEMBERSHIP",
    "REVIEWED_CANONICAL_REKEY",
    "REVIEWED_CANONICAL_ALIAS",
}

CRITICAL_SOURCE_FIELDS = {
    "record_id", "material_identity", "source_id", "document_key",
    "source_title", "E_source_value", "nu_source_value", "rho_source_value",
    "target_material_id", "target_memberships", "url", "locator", "local_file",
    "sha256", "conditions_or_group", "method_or_basis", "limitations",
    "property_citations_json", "property_value_origin", "unit_E_original",
    "unit_nu_original", "unit_rho_original", "E_source_locator",
    "nu_source_locator", "rho_source_locator",
}


def canonical_json(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def row_sha256(row: dict[str, str]) -> str:
    return hashlib.sha256(canonical_json(row).encode("utf-8")).hexdigest()


def value_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalized_json(value: str):
    try:
        return canonical_json(json.loads(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None


def _numeric_equal(left: str, right: str) -> bool:
    """Compare only plain numeric scalars; never extract a number from prose."""
    pattern = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
    if not re.fullmatch(pattern, left.strip()) or not re.fullmatch(pattern, right.strip()):
        return False
    try:
        return Decimal(left.strip()) == Decimal(right.strip())
    except InvalidOperation:
        return False


def _field_status(source_value: str, target_value: str):
    if source_value == target_value:
        return "DIRECT_EXACT"
    source_json, target_json = _normalized_json(source_value), _normalized_json(target_value)
    if source_json is not None and target_json is not None and source_json == target_json:
        return "DIRECT_JSON_EQUIVALENT"
    if _numeric_equal(source_value, target_value):
        return "DIRECT_NUMERIC_EQUIVALENT"
    return None


def audit_row_fields(
    source: dict[str, str],
    target: dict[str, str],
    *,
    source_archive_ref: str,
    source_file_sha256: str,
    target_record_id: str,
    target_locator: str = "record",
    critical_fields: set[str] | None = None,
    field_overrides: dict[str, tuple[str, str, str]] | None = None,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    """Audit every non-empty source field against target fields and frozen archive.

    Fields that are intentionally not projected remain explicitly `ARCHIVED_ONLY`
    and are reproducible from source_archive_ref + its hash + source_row_sha256.
    Critical fields with no active target representation make the row HOLD.
    """
    critical = CRITICAL_SOURCE_FIELDS if critical_fields is None else critical_fields
    overrides = field_overrides or {}
    source_hash = row_sha256(source)
    entries: list[dict[str, str]] = []

    for source_field, raw_value in source.items():
        value = str(raw_value or "")
        if not value.strip():
            continue

        status = None
        target_field = ""
        target_value = ""

        if source_field in overrides:
            status, target_field, target_value = overrides[source_field]
            entries.append({
                "source_record_id": str(source.get("record_id", "")),
                "target_record_id": target_record_id,
                "target_locator": target_locator,
                "source_field": source_field,
                "source_value_sha256": value_sha256(value),
                "target_field_or_locator": target_field,
                "target_value_sha256": value_sha256(target_value) if target_value else "",
                "field_status": status,
                "critical": "YES" if source_field in critical else "NO",
                "source_archive_ref": source_archive_ref,
                "source_file_sha256": source_file_sha256,
                "source_row_sha256": source_hash,
            })
            continue

        direct = str(target.get(source_field, "") or "")
        if direct:
            status = _field_status(value, direct)
            if status:
                target_field, target_value = source_field, direct
            else:
                target_field, target_value = source_field, direct

        if status is None:
            for alias in FIELD_ALIASES.get(source_field, ()):
                alias_value = str(target.get(alias, "") or "")
                if not alias_value:
                    continue
                status = _field_status(value, alias_value)
                target_field, target_value = alias, alias_value
                if status:
                    status = "ALIAS_EXACT" if status == "DIRECT_EXACT" else "ALIAS_EQUIVALENT"
                    break

        if status is None and source_field in PROPERTY_JSON_ALIASES:
            prop, member = PROPERTY_JSON_ALIASES[source_field]
            try:
                target_citations = json.loads(target.get("property_citations_json", "{}"))
                alias_value = target_citations.get(prop, {}).get(member, "")
            except (TypeError, ValueError, json.JSONDecodeError):
                alias_value = ""
            if alias_value != "":
                alias_value = str(alias_value)
                status = _field_status(value, alias_value)
                target_field = f"property_citations_json#/{prop}/{member}"
                target_value = alias_value
                if status:
                    status = "NESTED_JSON_EXACT" if status == "DIRECT_EXACT" else "NESTED_JSON_EQUIVALENT"

        if status is None:
            if target_field and target_value:
                status = "TARGET_VALUE_MISMATCH"
            else:
                status = "ARCHIVED_ONLY"

        entries.append({
            "source_record_id": str(source.get("record_id", "")),
            "target_record_id": target_record_id,
            "target_locator": target_locator,
            "source_field": source_field,
            "source_value_sha256": value_sha256(value),
            "target_field_or_locator": target_field,
            "target_value_sha256": value_sha256(target_value) if target_value else "",
            "field_status": status,
            "critical": "YES" if source_field in critical else "NO",
            "source_archive_ref": source_archive_ref,
            "source_file_sha256": source_file_sha256,
            "source_row_sha256": source_hash,
        })

    critical_unmapped = [
        row["source_field"] for row in entries
        if row["critical"] == "YES"
        and row["field_status"] not in {
            "DIRECT_EXACT", "DIRECT_JSON_EQUIVALENT", "DIRECT_NUMERIC_EQUIVALENT",
            "ALIAS_EXACT", "ALIAS_EQUIVALENT", "NESTED_JSON_EXACT",
            "NESTED_JSON_EQUIVALENT", "NESTED_OBSERVATION_VERIFIED",
            "NESTED_SOURCE_LOCATOR_VERIFIED", "AGGREGATED_SOURCE_ID_MAPPED",
            "CONDITION_GROUP_TRANSFORM_VERIFIED", "UNIT_NORMALIZATION_VERIFIED",
            "UNIT_EQUIVALENCE_VERIFIED", *REVIEWED_REPAIR_STATUSES,
        }
    ]
    mismatch_fields = [row["source_field"] for row in entries
                       if row["field_status"] == "TARGET_VALUE_MISMATCH"]
    summary = {
        "source_row_sha256": source_hash,
        "nonempty_source_fields": len(entries),
        "active_target_fields": sum(row["field_status"] not in {
            "ARCHIVED_ONLY", "AGGREGATED_SOURCE_FIELD_ARCHIVED", "TARGET_VALUE_MISMATCH"
        } for row in entries),
        "archived_only_fields": sum(row["field_status"] == "ARCHIVED_ONLY" for row in entries),
        "unresolved_mismatch_fields": mismatch_fields,
        "critical_unmapped_fields": critical_unmapped,
        "status": "PASS" if not critical_unmapped and not mismatch_fields else "HOLD_FIELD_PRESERVATION_REVIEW",
    }
    return entries, summary
