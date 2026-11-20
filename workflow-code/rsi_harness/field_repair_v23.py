"""Validated, append-only field repairs for RSI 2.3 migrations.

Repairs are projections onto a shadow release.  They never mutate a published
ledger in place.  Every patch is protected by a target-row preimage hash and
by the source/target field hashes that were reviewed.  A repair can therefore
explain a canonical re-key or fill a missing material relation without making
the migration checker silently accept a changed row.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from field_preservation_v23 import canonical_json, row_sha256, value_sha256


class FieldRepairError(ValueError):
    """Raised when a repair manifest is stale, incomplete, or unauthorised."""


REPAIR_DISPOSITIONS = {
    "REVIEWED_MATERIAL_MEMBERSHIP",
    "REVIEWED_CANONICAL_REKEY",
    "REVIEWED_CANONICAL_ALIAS",
}


def file_sha256(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _require_text(value, label: str) -> str:
    value = str(value or "")
    if not value.strip():
        raise FieldRepairError(f"{label} is required")
    return value


def _parse_memberships(value: str, expected_material_id: str) -> list[dict]:
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise FieldRepairError("target_memberships must be valid JSON") from exc
    if not isinstance(parsed, list) or not parsed:
        raise FieldRepairError("target_memberships must be a non-empty JSON list")
    ids = {str(item.get("target_material_id", "")) for item in parsed
           if isinstance(item, dict)}
    if expected_material_id not in ids:
        raise FieldRepairError(
            "target_memberships does not contain target_material_id "
            + expected_material_id
        )
    return parsed


def _manifest_sha(manifest: dict) -> str:
    payload = dict(manifest)
    payload.pop("manifest_sha256", None)
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def validate_repair_manifest(
    manifest: dict,
    *,
    source_rows: list[dict[str, str]],
    target_rows: list[dict[str, str]],
    target_file_sha256: str,
    source_file_sha256s: dict[str, str] | None = None,
) -> dict:
    """Validate a repair manifest against the exact frozen source/target rows.

    The function returns a normalized copy.  It does not edit either input.
    """
    if manifest.get("schema_version") != "RSI_FIELD_REPAIR_V23_1":
        raise FieldRepairError("unsupported field repair schema")
    repair_id = _require_text(manifest.get("repair_id"), "repair_id")
    proposer = _require_text(manifest.get("proposer"), "proposer")
    reviewer = _require_text(manifest.get("reviewer"), "reviewer")
    if proposer == reviewer:
        raise FieldRepairError("proposer and reviewer must be different people")
    _require_text(manifest.get("review_basis"), "review_basis")
    if manifest.get("base_target_file_sha256") != target_file_sha256:
        raise FieldRepairError("repair manifest target file preimage differs")
    source_file_sha256s = source_file_sha256s or {}
    declared_sources = manifest.get("source_files", {})
    if not isinstance(declared_sources, dict):
        raise FieldRepairError("source_files must be an object")
    for path, expected in declared_sources.items():
        if source_file_sha256s.get(path) != expected:
            raise FieldRepairError(f"source file pin differs: {path}")

    source_ids = [str(row.get("record_id", "")) for row in source_rows]
    target_ids = [str(row.get("record_id", "")) for row in target_rows]
    if len(set(source_ids)) != len(source_ids):
        raise FieldRepairError("source rows contain duplicate record_id")
    if len(set(target_ids)) != len(target_ids):
        raise FieldRepairError("target rows contain duplicate record_id")
    source_by_id = dict(zip(source_ids, source_rows))
    target_by_id = dict(zip(target_ids, target_rows))
    if "" in source_by_id or "" in target_by_id:
        raise FieldRepairError("source and target rows require non-empty record_id")
    entries = manifest.get("repairs")
    if not isinstance(entries, list) or not entries:
        raise FieldRepairError("repairs must be a non-empty list")

    seen = set()
    normalized = []
    for entry in entries:
        source_id = _require_text(entry.get("source_record_id"), "source_record_id")
        target_id = _require_text(entry.get("target_record_id"), "target_record_id")
        if source_id in seen:
            raise FieldRepairError(f"duplicate repair source_record_id: {source_id}")
        seen.add(source_id)
        if source_id not in source_by_id or target_id not in target_by_id:
            raise FieldRepairError(f"repair references unknown row: {source_id} -> {target_id}")
        target = target_by_id[target_id]
        if entry.get("target_row_sha256_before") != row_sha256(target):
            raise FieldRepairError(f"target row preimage differs: {target_id}")
        patches = entry.get("patches")
        if not isinstance(patches, list) or not patches:
            raise FieldRepairError(f"repair has no patches: {source_id}")
        patch_fields = set()
        normalized_patches = []
        for patch in patches:
            source_field = _require_text(patch.get("source_field"), "source_field")
            target_field = _require_text(patch.get("target_field"), "target_field")
            disposition = _require_text(patch.get("disposition"), "disposition")
            basis = _require_text(patch.get("basis"), "basis")
            after_value = _require_text(patch.get("after_value"), "after_value")
            if disposition not in REPAIR_DISPOSITIONS:
                raise FieldRepairError(f"unsupported repair disposition: {disposition}")
            if source_field in patch_fields:
                raise FieldRepairError(f"duplicate patch field: {source_id}.{source_field}")
            patch_fields.add(source_field)
            if source_field not in source_by_id[source_id]:
                raise FieldRepairError(f"source field is absent from row: {source_id}.{source_field}")
            if target_field not in target:
                raise FieldRepairError(f"target field is absent from row schema: {target_id}.{target_field}")
            source_value = str(source_by_id[source_id].get(source_field, "") or "")
            before_value = str(target.get(target_field, "") or "")
            if not source_value.strip():
                raise FieldRepairError(f"source patch field is empty: {source_id}.{source_field}")
            if patch.get("source_value_sha256") != value_sha256(source_value):
                raise FieldRepairError(f"source field preimage differs: {source_id}.{source_field}")
            if patch.get("target_value_sha256_before") != value_sha256(before_value):
                raise FieldRepairError(f"target field preimage differs: {target_id}.{target_field}")
            if disposition == "REVIEWED_CANONICAL_REKEY" and after_value != before_value:
                raise FieldRepairError(
                    f"canonical re-key must point to the current canonical value: {target_id}.{target_field}"
                )
            if source_field == "target_material_id":
                _parse_memberships(
                    next((p["after_value"] for p in patches
                          if p.get("source_field") == "target_memberships"), ""),
                    after_value,
                )
            normalized_patches.append({
                "source_field": source_field,
                "target_field": target_field,
                "disposition": disposition,
                "basis": basis,
                "after_value": after_value,
                "source_value_sha256": patch["source_value_sha256"],
                "target_value_sha256_before": patch["target_value_sha256_before"],
                "target_locator": _require_text(patch.get("target_locator"), "target_locator"),
            })
        if "target_material_id" in patch_fields and "target_memberships" not in patch_fields:
            raise FieldRepairError(
                f"material-id repair must also repair target_memberships: {source_id}"
            )
        normalized.append({
            "source_record_id": source_id,
            "target_record_id": target_id,
            "target_row_sha256_before": entry["target_row_sha256_before"],
            "patches": normalized_patches,
        })

    normalized_manifest = dict(manifest)
    normalized_manifest["repairs"] = normalized
    expected_manifest_sha = manifest.get("manifest_sha256")
    normalized_manifest["manifest_sha256"] = _manifest_sha(normalized_manifest)
    if expected_manifest_sha and expected_manifest_sha != normalized_manifest["manifest_sha256"]:
        raise FieldRepairError("repair manifest hash differs from its normalized content")
    return normalized_manifest


def apply_repairs(target_rows: list[dict[str, str]], manifest: dict) -> list[dict[str, str]]:
    """Apply a validated manifest to a new in-memory target projection."""
    rows = [dict(row) for row in target_rows]
    by_id = {str(row.get("record_id", "")): row for row in rows}
    for entry in manifest["repairs"]:
        row = by_id[entry["target_record_id"]]
        if row_sha256(row) != entry["target_row_sha256_before"]:
            raise FieldRepairError("target changed after manifest validation")
        for patch in entry["patches"]:
            row[patch["target_field"]] = patch["after_value"]
    return rows


def build_field_overrides(manifest: dict) -> dict[str, dict[str, tuple[str, str, str]]]:
    """Return audit overrides for fields whose canonical value intentionally differs."""
    overrides: dict[str, dict[str, tuple[str, str, str]]] = {}
    for entry in manifest["repairs"]:
        per_row = overrides.setdefault(entry["source_record_id"], {})
        for patch in entry["patches"]:
            # Keep the reviewed disposition visible in the field audit,
            # including material-membership repairs.  The projected target
            # value is still written separately by apply_repairs().
            per_row[patch["source_field"]] = (
                patch["disposition"],
                patch["target_locator"],
                patch["after_value"],
            )
    return overrides
