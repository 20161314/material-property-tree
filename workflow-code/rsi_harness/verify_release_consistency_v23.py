#!/usr/bin/env python3
"""Fail closed when site view summaries drift from a pinned release."""
import argparse
import hashlib
import json
from pathlib import Path


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def verify(release, download, summary, source_summary, deployment=None):
    errors = []
    release_id = release.get("id")
    if not release_id:
        errors.append("release manifest has no id")
    if download.get("release_id") != release_id:
        errors.append("download manifest release_id differs from release manifest")
    for label, document in (("summary", summary), ("source summary", source_summary)):
        embedded = document.get("release_id")
        if embedded is not None and embedded != release_id:
            errors.append(label + " release_id differs from release manifest")

    source_digest = hashlib.sha256(
        json.dumps(source_summary, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    # The release pins the exact source summary bytes; validate the published copy
    # against that pin separately in the CLI before calling this function.

    for section, keys in (("objects", ("total", "components", "rows")),
                          ("materials", ("total",)),
                          ("records", ("complete", "partial", "total"))):
        left, right = release.get(section, {}), download.get(section, {})
        if not isinstance(left, dict) or not isinstance(right, dict):
            errors.append("missing " + section + " section in release/download manifest")
            continue
        for key in keys:
            if key in left and key in right and left[key] != right[key]:
                errors.append(f"{section}.{key} differs between release and download manifest")

    expected_summary = {
        "objects.total": (download.get("objects", {}).get("total"), "object_identities"),
        "objects.components": (download.get("objects", {}).get("components"), "distinct_component_pairs"),
        "objects.rows": (download.get("objects", {}).get("rows"), "state_rows"),
        "materials.total": (download.get("materials", {}).get("total"), "material_nodes"),
        "records.main.complete": (download.get("records", {}).get("main", {}).get("complete"), "main_complete_groups"),
        "records.main.incomplete": (download.get("records", {}).get("main", {}).get("incomplete"), "main_partial_groups"),
    }
    for label, (expected, summary_key) in expected_summary.items():
        actual = summary.get(summary_key)
        if expected is None or actual is None:
            errors.append(f"summary missing pinned count for {label}")
        elif expected != actual:
            errors.append(f"summary.{summary_key}={actual} differs from {label}={expected}")

    main = download.get("records", {}).get("main", {})
    if main:
        group_count = summary.get("main_source_groups")
        expected_count = main.get("complete", 0) + main.get("incomplete", 0)
        if group_count is not None and group_count != expected_count:
            errors.append("summary.main_source_groups differs from main complete+incomplete")

    if deployment:
        if deployment.get("release_id") != release_id:
            errors.append("deployment release_id differs from release manifest")
        for key, count_key in (("objects", "total"), ("materials", "total")):
            deployed = deployment.get(key, {}).get(count_key)
            expected = download.get(key, {}).get(count_key)
            if deployed is not None and expected is not None and deployed != expected:
                errors.append(f"deployment {key}.{count_key} differs from download manifest")

    return {"status": "PASS_RELEASE_COUNTS_CONSISTENT" if not errors else "FAIL_RELEASE_COUNTS_INCONSISTENT",
            "release_id": release_id, "errors": errors,
            "source_summary_canonical_sha256": source_digest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release-manifest", type=Path, required=True)
    parser.add_argument("--download-manifest", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--source-summary", type=Path, required=True)
    parser.add_argument("--deployment", type=Path)
    args = parser.parse_args()
    release = read_json(args.release_manifest)
    download = read_json(args.download_manifest)
    summary = read_json(args.summary)
    source_summary = read_json(args.source_summary)
    expected_source_sha = release.get("inputs", {}).get("data/current_two_table_delivery_v1/summary.json")
    if not expected_source_sha:
        raise SystemExit("release manifest does not pin the canonical source summary")
    actual_source_sha = hashlib.sha256(args.source_summary.read_bytes()).hexdigest()
    if actual_source_sha != expected_source_sha:
        raise SystemExit("canonical source summary differs from the release input pin")
    if hashlib.sha256(args.summary.read_bytes()).digest() != hashlib.sha256(args.source_summary.read_bytes()).digest():
        print(json.dumps({"status": "FAIL_RELEASE_COUNTS_INCONSISTENT", "errors": [
            "published summary bytes differ from the release-pinned canonical summary"]}, ensure_ascii=False, indent=2))
        raise SystemExit(1)
    deployment = read_json(args.deployment) if args.deployment else None
    result = verify(release, download, summary, source_summary, deployment)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
