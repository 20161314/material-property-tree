#!/usr/bin/env python3
"""Run the RSI v2.4 research and site publication gates as one transaction.

The preflight is fail-closed.  It writes diagnostics and a deterministic
mapping queue, but it never changes source tables, the release pointer, or the
website.  Publishing code should require this command to return a PASS status.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from release_gate_v24 import run_gate
from site_release_consistency_v24 import run_preflight as run_site_preflight

def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _rooted(root: Path, path: Path) -> Path:
    """Resolve CLI output paths relative to the release root, not cwd."""
    return path if path.is_absolute() else root / path


def run_publication_preflight(
    root: Path,
    queue_out: Path,
    gate_out: Path,
    site_out: Path,
) -> dict:
    root = root.resolve()
    queue_path = _rooted(root, queue_out)
    gate_path = _rooted(root, gate_out)
    site_path = _rooted(root, site_out)
    gate = run_gate(root, queue_path)
    _write_json(gate_path, gate)
    effective_gate_path = gate_path
    site = run_site_preflight(root, effective_gate_path)
    _write_json(site_path, site)
    status = (
        "PASS_RSI_V24_PUBLICATION_PREFLIGHT"
        if gate.get("status") == "PASS_RSI_V24_RELEASE_GATE"
        and site.get("status") == "PASS_SITE_RELEASE_CONSISTENCY"
        else "BLOCKED_RSI_V24_PUBLICATION_PREFLIGHT"
    )
    return {
        "status": status,
        "rules_version": gate.get("rules_version", "UNSPECIFIED"),
        "gate_status": gate.get("status"),
        "site_status": site.get("status"),
        "gate_report": str(gate_path),
        "site_report": str(site_path),
        "queue": str(queue_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--queue-out", type=Path, required=True)
    parser.add_argument("--gate-out", type=Path, required=True)
    parser.add_argument("--site-out", type=Path, required=True)
    parser.add_argument("--result-out", type=Path)
    args = parser.parse_args()
    result = run_publication_preflight(args.root, args.queue_out, args.gate_out, args.site_out)
    if args.result_out:
        _write_json(args.result_out, result)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result["status"] != "PASS_RSI_V24_PUBLICATION_PREFLIGHT":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
