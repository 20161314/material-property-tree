#!/usr/bin/env python3
"""Verify that the local site and all three views use the current release.

Read-only.  It does not rebuild or mutate the website.  A site may have the
same counts as the current summary and still be stale if its release ID or
input pins differ.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from project_paths_v24 import resolve_project_input
from release_identity_v24 import parse_release_pointer


SUMMARY_REL = Path("data/current_two_table_delivery_v1/summary.json")
POINTER_REL = Path("current_release_pointer.md")
GATE_REL = Path("audit/rsi_framework_review_2026-11-15/rsi_v24_release_gate.json")
SITE_STATUS_REL = Path("site_v3/release-status.json")
SITE_MANIFEST_REL = Path("site_v3/release-manifest.json")
SITE_RELEASE_DATA_REL = Path("site_v3/release-data.js")
RULES_VERSION = "2.4.2-H3"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pointer_release_id(path: Path) -> str | None:
    return parse_release_pointer(path)


def read_embedded_release_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"window\.DATASET_RELEASE\s*=\s*(\{.*\});\s*$", text, re.S)
    if not match:
        raise ValueError("site release-data.js has no DATASET_RELEASE payload")
    return json.loads(match.group(1))


def run_preflight(root: Path, gate_path: Path | None = None) -> dict:
    root = root.resolve()
    gate_path = (gate_path if gate_path and gate_path.is_absolute() else root / gate_path) if gate_path else root / GATE_REL
    errors: list[dict] = []
    paths = {name: root / rel for name, rel in {
        "summary": SUMMARY_REL, "pointer": POINTER_REL,
        "site_status": SITE_STATUS_REL, "site_manifest": SITE_MANIFEST_REL,
        "site_release_data": SITE_RELEASE_DATA_REL,
    }.items()}
    paths["gate"] = gate_path
    for name, path in paths.items():
        if not path.is_file():
            errors.append({"code": "MISSING_SITE_RELEASE_FILE", "file": name, "path": str(path)})
    if errors:
        return {"status": "BLOCKED_SITE_RELEASE_CONSISTENCY", "errors": errors}

    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    gate = json.loads(paths["gate"].read_text(encoding="utf-8"))
    site_status = json.loads(paths["site_status"].read_text(encoding="utf-8"))
    site_manifest = json.loads(paths["site_manifest"].read_text(encoding="utf-8"))
    site_data = read_embedded_release_data(paths["site_release_data"])

    pointer_id = pointer_release_id(paths["pointer"])
    if not pointer_id:
        errors.append({"code": "RELEASE_POINTER_MISSING_OR_INVALID",
                       "message": "current_release_pointer.md does not contain one parseable release ID"})
    ids = {
        "pointer": pointer_id,
        "site_status": site_status.get("release_id"),
        "site_manifest": site_manifest.get("id"),
        "site_release_data": site_data.get("id"),
    }
    if len(set(x for x in ids.values() if x is not None)) != 1:
        errors.append({"code": "SITE_RELEASE_ID_MISMATCH", "release_ids": ids})

    expected_summary_sha = site_manifest.get("inputs", {}).get(str(SUMMARY_REL))
    actual_summary_sha = sha256(paths["summary"])
    if expected_summary_sha != actual_summary_sha:
        errors.append({"code": "SITE_SUMMARY_INPUT_PIN_MISMATCH",
                       "expected": expected_summary_sha, "actual": actual_summary_sha})

    # The site manifest is an input contract, not only a display manifest.
    # Every file it claims to use must still exist with the pinned bytes.  A
    # page can otherwise carry a correct release ID while silently serving a
    # mixed set of source files.
    manifest_inputs = site_manifest.get("inputs")
    if not isinstance(manifest_inputs, dict) or not manifest_inputs:
        errors.append({"code": "SITE_MANIFEST_INPUTS_MISSING",
                       "message": "site release manifest has no input hash map"})
    else:
        for rel, expected_hash in sorted(manifest_inputs.items()):
            input_path = resolve_project_input(root, rel)
            if input_path is None:
                errors.append({"code": "SITE_MANIFEST_INPUT_PATH_OUTSIDE_ROOT", "path": rel})
                continue
            if not input_path.is_file():
                errors.append({"code": "SITE_MANIFEST_INPUT_MISSING", "path": rel})
                continue
            actual_hash = sha256(input_path)
            if actual_hash != expected_hash:
                errors.append({"code": "SITE_MANIFEST_INPUT_PIN_MISMATCH",
                               "path": rel, "expected": expected_hash, "actual": actual_hash})

    count_pairs = {
        "object_identities": (summary.get("object_identities"), site_status.get("object_identities"), site_data.get("objects", {}).get("total")),
        "distinct_component_pairs": (summary.get("distinct_component_pairs"), site_status.get("distinct_object_component_pairs"), site_data.get("objects", {}).get("components")),
        "state_rows": (summary.get("state_rows"), site_status.get("component_status_rows"), site_data.get("objects", {}).get("rows")),
        "material_nodes": (summary.get("material_nodes"), site_status.get("material_labels"), site_data.get("materials", {}).get("total")),
        "main_complete_groups": (summary.get("main_complete_groups"), site_status.get("main_complete"), site_data.get("records", {}).get("main", {}).get("complete")),
        "main_partial_groups": (summary.get("main_partial_groups"), site_status.get("main_partial"), site_data.get("records", {}).get("main", {}).get("incomplete")),
    }
    for key, values in count_pairs.items():
        if len(set(value for value in values if value is not None)) != 1:
            errors.append({"code": "SITE_COUNT_MISMATCH", "metric": key, "values": values})

    # Check the manifest's own count projection too.  This catches a stale
    # release-manifest even when release-data.js and release-status.json agree
    # with one another.
    manifest_pairs = {
        "object_identities": (summary.get("object_identities"), site_manifest.get("objects", {}).get("total")),
        "distinct_component_pairs": (summary.get("distinct_component_pairs"), site_manifest.get("objects", {}).get("components")),
        "state_rows": (summary.get("state_rows"), site_manifest.get("objects", {}).get("rows")),
        "material_nodes": (summary.get("material_nodes"), site_manifest.get("materials", {}).get("total")),
        "main_complete_groups": (summary.get("main_complete_groups"), site_manifest.get("records", {}).get("main", {}).get("complete")),
        "main_partial_groups": (summary.get("main_partial_groups"), site_manifest.get("records", {}).get("main", {}).get("incomplete")),
    }
    for key, values in manifest_pairs.items():
        if len(set(value for value in values if value is not None)) != 1:
            errors.append({"code": "SITE_MANIFEST_COUNT_MISMATCH", "metric": key, "values": values})

    if gate.get("status") != "PASS_RSI_V24_RELEASE_GATE":
        errors.append({"code": "RSI_GATE_BLOCKED_SITE_PUBLICATION", "gate_status": gate.get("status")})
    return {
        "status": "PASS_SITE_RELEASE_CONSISTENCY" if not errors else "BLOCKED_SITE_RELEASE_CONSISTENCY",
        "rules_version": RULES_VERSION,
        "release_ids": ids,
        "summary_sha256": actual_summary_sha,
        "gate_status": gate.get("status"),
        "errors": errors,
        "counts": count_pairs,
    }


def write_report(root: Path, out: Path) -> dict:
    result = run_preflight(root)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = out.with_suffix(".md")
    lines = [f"# RSI v{RULES_VERSION} 站点 release 一致性预检", "", f"状态：`{result['status']}`", ""]
    if result.get("release_ids"):
        lines += ["| 位置 | release_id |", "|---|---|"]
        for key, value in result["release_ids"].items(): lines.append(f"| {key} | `{value}` |")
        lines += [""]
    if result.get("errors"):
        lines += ["## 阻断原因", ""]
        for error in result["errors"]: lines.append(f"- `{error['code']}`：{json.dumps(error, ensure_ascii=False)}")
    else:
        lines += ["三页视图、站点清单和当前摘要使用同一 release，且输入 pin 一致。", ""]
    md.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(out), "markdown": str(md), "status": result["status"]}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = write_report(args.root.resolve(), args.out)
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "PASS_SITE_RELEASE_CONSISTENCY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
