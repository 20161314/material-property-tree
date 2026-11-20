"""Release-to-release conservation checks for accepted evidence rows.

This module validates the identity/locator layer of a migration ledger. Domain
adapters must separately verify that mapped values and source scope match.
"""

from collections import Counter


MAPPED = "MAPPED"
RETRACTED = "RETRACTED"
MAPPING_KINDS = {
    "EXACT_ID",
    "REKEYED_ROW",
    "AGGREGATED_SUBRESULT",
    "SPLIT_SUBRESULT",
}


class ReconciliationError(ValueError):
    pass


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def verify_delta_reconciliation(source_rows, target_rows, mappings):
    """Require every accepted source row to be mapped or explicitly retracted.

    A source row may map to several target rows when one record was split. Many
    source rows may map to different nested locators in one aggregated target.
    Reusing the same target locator is always rejected.
    """
    source_ids = [str(row.get("record_id", "")) for row in source_rows]
    if any(not item for item in source_ids):
        raise ReconciliationError("source record_id is empty")
    duplicate_sources = sorted(key for key, count in Counter(source_ids).items() if count > 1)
    if duplicate_sources:
        raise ReconciliationError("duplicate source record_id: " + ", ".join(duplicate_sources[:10]))

    target_ids = [str(row.get("record_id", "")) for row in target_rows]
    if any(not item for item in target_ids):
        raise ReconciliationError("target record_id is empty")
    duplicate_targets = sorted(key for key, count in Counter(target_ids).items() if count > 1)
    if duplicate_targets:
        raise ReconciliationError("duplicate target record_id: " + ", ".join(duplicate_targets[:10]))

    source_set, target_set = set(source_ids), set(target_ids)
    mapped_sources = set()
    dispositions = {}
    seen_retractions = set()
    used_targets = set()
    mapped_edges = 0
    retracted = 0

    for row in mappings:
        source_id = str(row.get("source_record_id", ""))
        status = str(row.get("mapping_status", ""))
        if source_id not in source_set:
            raise ReconciliationError("mapping references unknown source: " + source_id)
        prior = dispositions.setdefault(source_id, status)
        if prior != status:
            raise ReconciliationError("source has mixed dispositions: " + source_id)

        if status == MAPPED:
            kind = str(row.get("mapping_kind", ""))
            target_id = str(row.get("target_record_id", ""))
            locator = str(row.get("target_locator", ""))
            if kind not in MAPPING_KINDS:
                raise ReconciliationError("unsupported mapping_kind for " + source_id + ": " + kind)
            if target_id not in target_set:
                raise ReconciliationError("mapping references unknown target: " + target_id)
            if not _nonempty(locator):
                raise ReconciliationError("mapped row has no target locator: " + source_id)
            if row.get("content_match") != "PASS":
                raise ReconciliationError("mapped row lacks a passing content check: " + source_id)
            if not _nonempty(row.get("basis", "")):
                raise ReconciliationError("mapped row has no basis: " + source_id)
            if kind == "EXACT_ID" and (target_id != source_id or locator != "record"):
                raise ReconciliationError("EXACT_ID must retain ID and record locator: " + source_id)
            if kind == "AGGREGATED_SUBRESULT" and "#/" not in locator:
                raise ReconciliationError("aggregated mapping needs a nested target locator: " + source_id)
            target_locator = (target_id, locator)
            if target_locator in used_targets:
                raise ReconciliationError("target locator reused: " + target_id + " " + locator)
            used_targets.add(target_locator)
            mapped_sources.add(source_id)
            mapped_edges += 1
        elif status == RETRACTED:
            if source_id in seen_retractions:
                raise ReconciliationError("duplicate retraction disposition: " + source_id)
            seen_retractions.add(source_id)
            retracted += 1
            if row.get("target_record_id", "") or row.get("target_locator", ""):
                raise ReconciliationError("retracted source cannot also name a target: " + source_id)
            if not all(_nonempty(row.get(key, "")) for key in (
                "disposition_id", "reviewer_id", "rationale"
            )):
                raise ReconciliationError("retraction requires a reviewed disposition: " + source_id)
            if row.get("review_status") != "PASS":
                raise ReconciliationError("retraction is not independently approved: " + source_id)
        else:
            raise ReconciliationError("unknown mapping_status for " + source_id + ": " + status)

    missing = sorted(source_set - set(dispositions))
    if missing:
        raise ReconciliationError("unmapped accepted source rows: " + ", ".join(missing[:20]))

    for source_id in mapped_sources:
        edges = [row for row in mappings
                 if str(row.get("source_record_id", "")) == source_id
                 and row.get("mapping_status") == MAPPED]
        if len(edges) > 1 and any(row.get("mapping_kind") != "SPLIT_SUBRESULT"
                                  for row in edges):
            raise ReconciliationError(
                "multiple target rows require SPLIT_SUBRESULT mappings: " + source_id
            )

    return {
        "source_rows": len(source_rows),
        "target_rows": len(target_rows),
        "source_ids": len(source_set),
        "mapped_source_ids": len(mapped_sources),
        "mapping_edges": mapped_edges,
        "unique_target_rows_referenced": len({target for target, _ in used_targets}),
        "unique_target_locators": len(used_targets),
        "retracted_source_ids": retracted,
    }
