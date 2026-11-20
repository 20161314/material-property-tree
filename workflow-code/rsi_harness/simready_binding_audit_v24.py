#!/usr/bin/env python3
"""Verify official SimReady material-binding rows without changing release data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from project_paths_v24 import resolve_project_input


RULES_VERSION = "2.4.2-H3"
OFFICIAL_RELATION = "OFFICIAL_BOUND_NONVISUAL_LABEL"
REVIEWED_MAPPING = "REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT"
ACCEPTED_PLAUSIBILITY = {
    "ACCEPTED_PLAUSIBLE_SOURCE_REPORTED_LABEL",
    "ACCEPT_PLAUSIBLE_OFFICIAL_COMPONENT_REGION_LABEL",
}
MATERIAL_LABEL_QUOTE = re.compile(
    r"semantics:labels:material\s*=\s*\[\s*[\"']([^\"']+)[\"']\s*\]",
    re.IGNORECASE,
)
LOCATOR_FILE_SEGMENT = re.compile(r"^(?P<path>.*?\.usd(?:a|c)?):(?P<markers>.*)$", re.IGNORECASE)
LOCATOR_LINE_MARKER = re.compile(
    r"(?P<kind>materialsemantic|semantics|materialref|nonvisual|binding|entity|mesh)?"
    r"(?:line|l)(?P<number>\d+)",
    re.IGNORECASE,
)
LOCATOR_BARE_LINE = re.compile(r"^(?:line)?(?P<number>\d+)$", re.IGNORECASE)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _evidence_path(root: Path, raw: str) -> Path | None:
    try:
        candidate = Path(raw)
        if not candidate.is_absolute():
            candidate = root / candidate
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
        return resolved
    except (OSError, RuntimeError, TypeError, ValueError):
        return None


def _parse_locator(locator: str) -> list[tuple[str, int]]:
    """Parse the two frozen USD locator forms used by the SimReady extracts."""
    references: list[tuple[str, int]] = []
    current_path = ""
    for raw_segment in locator.split(";"):
        segment = raw_segment.strip()
        if "via usdcat:" in segment.lower():
            segment = re.split(r"via usdcat:", segment, flags=re.IGNORECASE)[-1]
        match = LOCATOR_FILE_SEGMENT.match(segment)
        if match:
            current_path = match.group("path").strip()
            marker_text = match.group("markers")
        else:
            marker_text = segment
        if not current_path:
            continue
        bare_line = LOCATOR_BARE_LINE.fullmatch(marker_text.strip())
        if bare_line:
            references.append((current_path, int(bare_line.group("number"))))
            continue
        for marker in LOCATOR_LINE_MARKER.finditer(marker_text):
            references.append((current_path, int(marker.group("number"))))
    return references


def _locator_matches_quote(
    root: Path,
    locator: str,
    target: Path | None,
    quote: str,
    file_lines: dict[Path, list[str]],
) -> bool:
    if target is None or not quote:
        return False
    target = target.resolve()
    try:
        target_relative = target.relative_to(root.resolve()).as_posix()
    except ValueError:
        return False
    for locator_path, line_number in _parse_locator(locator):
        normalized = locator_path.replace("\\", "/").strip()
        parts = Path(normalized).parts
        if ".." in parts:
            continue
        if Path(normalized).is_absolute():
            try:
                points_to_target = Path(normalized).resolve() == target
            except (OSError, RuntimeError):
                points_to_target = False
        else:
            points_to_target = target_relative == normalized or target_relative.endswith("/" + normalized)
        if not points_to_target:
            continue
        lines = file_lines.get(target)
        if lines and 1 <= line_number <= len(lines) and quote in lines[line_number - 1]:
            return True
    return False


def audit_batch(
    root: Path,
    queue_rows: list[dict],
    relation_rows: list[dict],
    material_rows: list[dict],
) -> tuple[list[dict], list[dict], dict]:
    root = root.resolve()
    simready_pairs = {
        (row.get("object_id", "").strip(), row.get("component_id", "").strip())
        for row in queue_rows
        if "NVIDIA SimReady" in row.get("source_dataset", "")
        and row.get("object_id", "").strip() and row.get("component_id", "").strip()
    }
    material_ids = {row.get("material_id", "").strip() for row in material_rows}
    matched = [
        dict(row) for row in relation_rows
        if (row.get("object_id", "").strip(), row.get("component_id", "").strip()) in simready_pairs
    ]

    duplicate_ids = Counter(row.get("relation_id", "").strip() for row in matched)
    duplicate_ids = {key for key, count in duplicate_ids.items() if not key or count > 1}
    file_quotes: dict[Path, set[str]] = defaultdict(set)
    file_hashes: dict[Path, set[str]] = defaultdict(set)
    row_paths: dict[tuple[int, str], Path | None] = {}
    for index, row in enumerate(matched):
        for role, path_field, hash_field, quote_field in (
            ("semantic", "source_local_file", "source_sha256", "source_quote"),
            ("binding", "binding_source_file", "binding_source_sha256", "binding_quote"),
        ):
            path = _evidence_path(root, row.get(path_field, "").strip())
            row_paths[(index, role)] = path
            quote = row.get(quote_field, "").strip()
            expected_hash = row.get(hash_field, "").strip().lower()
            if path and quote and re.fullmatch(r"[0-9a-f]{64}", expected_hash):
                file_quotes[path].add(quote)
                file_hashes[path].add(expected_hash)

    file_results: dict[Path, tuple[str, bool, dict[str, bool]]] = {}
    file_lines: dict[Path, list[str]] = {}
    for path, quotes in file_quotes.items():
        try:
            content = path.read_bytes()
            actual_hash = hashlib.sha256(content).hexdigest()
            text = content.decode("utf-8", errors="replace")
            file_lines[path] = text.splitlines()
            expected = file_hashes[path]
            hash_ok = len(expected) == 1 and actual_hash in expected
            quote_results = {quote: quote in text for quote in quotes}
            file_results[path] = (actual_hash, hash_ok, quote_results)
        except OSError:
            file_results[path] = ("", False, {})

    candidates: list[dict] = []
    holds: list[dict] = []
    hold_reasons: Counter[str] = Counter()
    semantic_locator_misses = 0
    binding_locator_misses = 0
    for index, row in enumerate(matched):
        reasons: list[str] = []
        relation_id = row.get("relation_id", "").strip()
        if not relation_id or relation_id in duplicate_ids:
            reasons.append("RELATION_ID_BLANK_OR_DUPLICATE")
        if row.get("relation_type", "").strip() != OFFICIAL_RELATION:
            reasons.append("NOT_OFFICIAL_BOUND_RELATION")
        if row.get("canonical_mapping_status", "").strip() != REVIEWED_MAPPING:
            reasons.append("CANONICAL_MATERIAL_MAPPING_NOT_REVIEWED")
        if row.get("plausibility_status", "").strip() not in ACCEPTED_PLAUSIBILITY:
            reasons.append("SOURCE_LABEL_PLAUSIBILITY_NOT_ACCEPTED")
        if row.get("canonical_material_id", "").strip() not in material_ids:
            reasons.append("CANONICAL_MATERIAL_NODE_MISSING")
        if not row.get("source_locator", "").strip() or not row.get("source_url", "").strip():
            reasons.append("SOURCE_LOCATOR_OR_URL_MISSING")

        quote = row.get("source_quote", "").strip()
        label_match = MATERIAL_LABEL_QUOTE.search(quote)
        raw_label = row.get("source_label_raw", "").strip()
        normalized_label = row.get("source_label_normalized", "").strip()
        if not label_match or label_match.group(1).strip().casefold() != raw_label.casefold():
            reasons.append("SOURCE_QUOTE_LABEL_MISMATCH")
        if raw_label.casefold() != normalized_label.casefold():
            reasons.append("RAW_AND_NORMALIZED_LABEL_DIFFER")

        for role, path_field, hash_field, quote_field in (
            ("semantic", "source_local_file", "source_sha256", "source_quote"),
            ("binding", "binding_source_file", "binding_source_sha256", "binding_quote"),
        ):
            path = row_paths.get((index, role))
            expected_hash = row.get(hash_field, "").strip().lower()
            source_quote = row.get(quote_field, "").strip()
            if path is None:
                reasons.append(f"{role.upper()}_FILE_OUTSIDE_ROOT_OR_MISSING")
                continue
            if not re.fullmatch(r"[0-9a-f]{64}", expected_hash) or not source_quote:
                reasons.append(f"{role.upper()}_HASH_OR_QUOTE_MISSING")
                continue
            actual_hash, hash_ok, quote_results = file_results.get(path, ("", False, {}))
            if not hash_ok or actual_hash != expected_hash:
                reasons.append(f"{role.upper()}_FILE_HASH_MISMATCH")
            if not quote_results.get(source_quote, False):
                reasons.append(f"{role.upper()}_QUOTE_NOT_IN_FILE")

        semantic_locator = row.get("semantic_source_locator", "").strip() or row.get("source_locator", "").strip()
        binding_locator = row.get("binding_source_locator", "").strip() or row.get("source_locator", "").strip()
        semantic_path = row_paths.get((index, "semantic"))
        binding_path = row_paths.get((index, "binding"))
        if not _locator_matches_quote(root, semantic_locator, semantic_path, quote, file_lines):
            reasons.append("SEMANTIC_LOCATOR_DOES_NOT_POINT_TO_QUOTE")
            semantic_locator_misses += 1
        if not _locator_matches_quote(
            root, binding_locator, binding_path, row.get("binding_quote", "").strip(), file_lines
        ):
            reasons.append("BINDING_LOCATOR_DOES_NOT_POINT_TO_QUOTE")
            binding_locator_misses += 1

        if reasons:
            held = dict(row)
            held["hold_reason"] = ";".join(sorted(set(reasons)))
            holds.append(held)
            hold_reasons.update(set(reasons))
            continue

        candidate = dict(row)
        candidate["audit_status"] = "SOURCE_CHAIN_VERIFIED_LOGIC_REVIEW_REQUIRED"
        candidate["property_assignment"] = "NONE_NO_E_NU_RHO_INHERITANCE"
        candidates.append(candidate)

    candidate_pairs = {
        (row.get("object_id", "").strip(), row.get("component_id", "").strip())
        for row in candidates
    }
    metrics = {
        "queue_simready_component_pairs": len(simready_pairs),
        "matched_official_relation_rows": len(matched),
        "matched_component_pairs": len({(r.get("object_id", "").strip(), r.get("component_id", "").strip()) for r in matched}),
        "candidate_relation_rows": len(candidates),
        "verified_component_pairs": len(candidate_pairs),
        "held_relation_rows": len(holds),
        "source_files_verified": sum(result[1] for result in file_results.values()),
        "source_files_checked": len(file_results),
        "semantic_locator_misses": semantic_locator_misses,
        "binding_locator_misses": binding_locator_misses,
        "hold_reason_rows": dict(sorted(hold_reasons.items())),
    }
    return candidates, holds, metrics


def _read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict], fallback_fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else fallback_fields
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run_files(root: Path, queue_rel: Path, relations_rel: Path, materials_rel: Path,
              candidates_rel: Path, holds_rel: Path, report_rel: Path) -> dict:
    root = root.resolve()
    input_paths = {
        "queue": resolve_project_input(root, str(queue_rel)),
        "relations": resolve_project_input(root, str(relations_rel)),
        "materials": resolve_project_input(root, str(materials_rel)),
    }
    missing = [name for name, path in input_paths.items() if path is None or not path.is_file()]
    if missing:
        return {"status": "BLOCKED_SIMREADY_BINDING_AUDIT", "errors": [f"INPUT_MISSING:{name}" for name in missing]}
    queue = _read_csv(input_paths["queue"])
    relations = _read_csv(input_paths["relations"])
    materials = _read_csv(input_paths["materials"])
    candidates, holds, metrics = audit_batch(root, queue, relations, materials)
    report_path = root / report_rel
    candidates_path = root / candidates_rel
    holds_path = root / holds_rel
    _write_csv(candidates_path, candidates, list(relations[0]) + ["audit_status", "property_assignment"] if relations else [])
    _write_csv(holds_path, holds, list(relations[0]) + ["hold_reason"] if relations else [])
    report_path.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS_SIMREADY_BINDING_AUDIT_CANDIDATES_READY",
        "rules_version": RULES_VERSION,
        "inputs": {name: {"path": str(path.relative_to(root)), "sha256": _sha256(path)}
                   for name, path in input_paths.items()},
        "metrics": metrics,
        "outputs": {"candidates": str(candidates_rel), "holds": str(holds_rel)},
        "publication_effect": "NONE_CANDIDATES_ONLY",
    }
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--relations", type=Path, required=True)
    parser.add_argument("--materials", type=Path, required=True)
    parser.add_argument("--candidates-out", type=Path, required=True)
    parser.add_argument("--holds-out", type=Path, required=True)
    parser.add_argument("--report-out", type=Path, required=True)
    args = parser.parse_args()
    result = run_files(args.root, args.queue, args.relations, args.materials,
                       args.candidates_out, args.holds_out, args.report_out)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS_SIMREADY_BINDING_AUDIT_CANDIDATES_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
