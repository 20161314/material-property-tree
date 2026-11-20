#!/usr/bin/env python3
"""Validate the declared evidence routes and their admission policy."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROUTES_REL = Path("evidence_source_routes.csv")
POLICY_REL = Path("config/evidence_route_policy_v24.json")
RULES_VERSION = "2.4.2-H3"
REQUIRED_FIELDS = {
    "route_id", "domain", "source_name", "source_role", "authoritative_url",
    "local_evidence_path", "admission_use", "required_locator", "license_or_access",
    "known_limitations",
}


def _issue(code: str, message: str, count: int = 1, samples: list[str] | None = None) -> dict:
    return {"code": code, "message": message, "count": count, "samples": (samples or [])[:10]}


def run_route_contract(root: Path) -> dict:
    root = root.resolve()
    route_path = root / ROUTES_REL
    policy_path = root / POLICY_REL
    errors: list[dict] = []
    if not route_path.is_file() or not policy_path.is_file():
        missing = [str(p) for p in (route_path, policy_path) if not p.is_file()]
        return {"status": "BLOCKED_RSI_EVIDENCE_ROUTE_CONTRACT", "rules_version": RULES_VERSION,
                "errors": [_issue("EVIDENCE_ROUTE_REQUIRED_FILE_MISSING", "route policy file missing", len(missing), missing)]}
    with route_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fields = set(handle) if False else set(rows[0]) if rows else set()
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    missing_fields = sorted(REQUIRED_FIELDS - fields)
    if missing_fields:
        errors.append(_issue("EVIDENCE_ROUTE_SCHEMA_MISSING_COLUMNS", "route registry schema is incomplete", len(missing_fields), missing_fields))
    route_ids = [r.get("route_id", "").strip() for r in rows]
    duplicates = sorted({x for x in route_ids if x and route_ids.count(x) > 1})
    blanks = sum(not x for x in route_ids)
    if duplicates:
        errors.append(_issue("EVIDENCE_ROUTE_DUPLICATE_ID", "route_id repeats", len(duplicates), duplicates))
    if blanks:
        errors.append(_issue("EVIDENCE_ROUTE_BLANK_ID", "route_id is blank", blanks))
    declared = set(policy.get("routes", {}))
    actual = set(route_ids) - {""}
    missing_policy = sorted(actual - declared)
    extra_policy = sorted(declared - actual)
    if missing_policy:
        errors.append(_issue("EVIDENCE_ROUTE_POLICY_MISSING", "route has no explicit admission class", len(missing_policy), missing_policy))
    if extra_policy:
        errors.append(_issue("EVIDENCE_ROUTE_POLICY_ORPHAN", "policy refers to an absent route", len(extra_policy), extra_policy))
    classes = set(policy.get("route_classes", {}))
    bad_classes = sorted({v for v in policy.get("routes", {}).values() if v not in classes})
    if bad_classes:
        errors.append(_issue("EVIDENCE_ROUTE_UNKNOWN_CLASS", "route policy uses unknown class", len(bad_classes), bad_classes))
    missing_descriptions: list[str] = []
    for row in rows:
        rid = row.get("route_id", "").strip()
        for field in ("domain", "source_name", "source_role", "admission_use", "required_locator", "known_limitations"):
            if not row.get(field, "").strip():
                missing_descriptions.append(f"{rid}:{field}")
        if not row.get("authoritative_url", "").strip() and not row.get("local_evidence_path", "").strip():
            missing_descriptions.append(f"{rid}:authoritative_url_or_local_evidence_path")
    if missing_descriptions:
        errors.append(_issue("EVIDENCE_ROUTE_DESCRIPTION_INCOMPLETE", "route lacks source or admission description", len(missing_descriptions), missing_descriptions))
    metrics = {
        "route_rows": len(rows),
        "route_ids": len(actual),
        "route_classes": {k: sum(policy.get("routes", {}).get(rid) == k for rid in actual) for k in sorted(classes)},
        "property_formal_conditional_routes": sorted(rid for rid in actual if policy.get("routes", {}).get(rid) == "property_formal_conditional"),
        "candidate_only_routes": sorted(rid for rid in actual if policy.get("routes", {}).get(rid) == "candidate_only"),
    }
    return {"status": "PASS_RSI_EVIDENCE_ROUTE_CONTRACT" if not errors else "BLOCKED_RSI_EVIDENCE_ROUTE_CONTRACT",
            "rules_version": RULES_VERSION, "metrics": metrics, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = run_route_contract(args.root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "out": str(args.out)}, ensure_ascii=False))
    if result["status"] != "PASS_RSI_EVIDENCE_ROUTE_CONTRACT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
