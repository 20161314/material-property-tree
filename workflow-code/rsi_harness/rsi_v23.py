#!/usr/bin/env python3
"""CLI for RSI 2.3 read-only planning and bounded shadow scans.

This runner only manages queue and execution metadata. Reviewed fact changes
must use the project-specific candidate adapter and independent merge review.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
import uuid

import harness
from queries_v23 import (four_state_counts, material_queue, object_delivery_summary,
                         object_material_coverage, object_queue)
from runtime_v23 import (apply_schema, claim_scan_route, create_scan, end_scan_run,
                         extend_scan_budget, finish_scan_route, seed_scan_frontier,
                         start_scan_run)


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _tree_epoch(db):
    nodes = [list(r) for r in db.execute("""SELECT id,family,granularity,active FROM nodes
                                          WHERE active=1 AND kind='MATERIAL' ORDER BY id""")]
    edges = [list(r) for r in db.execute("""SELECT parent_id,child_id,object_up,property_up FROM edges
                                          WHERE accepted=1 AND kind='IS_A' ORDER BY parent_id,child_id""")]
    return hashlib.sha256(_json({"nodes": nodes, "edges": edges}).encode()).hexdigest()


def _open_db(path, readonly=False, require_runtime=False):
    path = Path(path)
    if readonly:
        db = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True, timeout=30)
        db.execute("PRAGMA query_only=ON")
    else:
        db = sqlite3.connect(path, timeout=30, isolation_level=None)
        db.execute("PRAGMA foreign_keys=ON")
    db.row_factory = sqlite3.Row
    required = {"nodes", "material_state", "objects", "components", "material_links", "obligations"}
    if require_runtime:
        required |= {"scans", "scan_routes", "scan_runs"}
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if not required.issubset(tables):
        db.close()
        raise ValueError("database is not prepared for the requested RSI 2.3 command")
    return db


def _limit_rows(rows, limit):
    return {"total": len(rows), "shown": rows[:limit], "truncated": len(rows) > limit}


def clone_shadow(source_path, output_path, expected_release_id):
    """Clone a frozen release DB and add v2.3 tables without touching its source."""
    source_path, output_path = Path(source_path).resolve(), Path(output_path).resolve()
    if source_path == output_path or output_path.exists():
        raise ValueError("source and new shadow paths must differ; destination must not exist")
    if not isinstance(expected_release_id, str) or not expected_release_id.strip():
        raise ValueError("the current release ID from the release pointer is required")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + ".tmp-" + uuid.uuid4().hex)
    source = sqlite3.connect(source_path.as_uri() + "?mode=ro", uri=True, timeout=30)
    source.row_factory = sqlite3.Row
    release_row = source.execute("SELECT value FROM meta WHERE key='release_id'").fetchone()
    source_release_id = json.loads(release_row[0]) if release_row else None
    if source_release_id != expected_release_id:
        source.close()
        raise ValueError("source database release does not match the current release pointer")
    target = sqlite3.connect(temp_path, timeout=30, isolation_level=None)
    try:
        source.backup(target)
        target.execute("PRAGMA foreign_keys=ON")
        apply_schema(target)
        violations = list(target.execute("PRAGMA foreign_key_check"))
        if violations:
            raise ValueError("source snapshot has foreign key violations")
        harness.set_meta(target, "rsi_shadow_schema", "2.3")
        harness.set_meta(target, "rsi_shadow_parent_release_id", expected_release_id)
        checkpoint = target.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
        if checkpoint and checkpoint[0] != 0:
            raise ValueError("could not checkpoint cloned shadow database")
        journal_mode = target.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower()
        if journal_mode != "delete":
            raise ValueError("cloned shadow database must be self-contained before publication")
    except Exception:
        target.close()
        source.close()
        if temp_path.exists():
            temp_path.unlink()
        raise
    target.close()
    source.close()
    try:
        os.link(temp_path, output_path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise
    temp_path.unlink()
    return {"source": str(source_path), "database": str(output_path),
            "parent_release_id": expected_release_id, "status": "V23_SHADOW_READY"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init-shadow", help="create a new empty shadow database")
    p.add_argument("--db", type=Path, required=True)

    p = sub.add_parser("clone-shadow", help="clone an exact frozen release DB and add RSI 2.3 tables")
    p.add_argument("--source-db", type=Path, required=True)
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--expected-release-id", required=True)

    p = sub.add_parser("status", help="read-only coverage and queue summary")
    p.add_argument("--db", type=Path, required=True)

    p = sub.add_parser("delivery", help="read-only audited N/R/C/RC object counts")
    p.add_argument("--db", type=Path, required=True)

    p = sub.add_parser("plan", help="read-only queue preview")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--limit", type=int, default=100)

    p = sub.add_parser("create-scan", help="start a persistent, budgeted scan")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--purpose", choices=("MATERIAL", "OBJECT", "MIXED"), required=True)
    p.add_argument("--claims", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)

    p = sub.add_parser("seed-scan", help="freeze current eligible queues into a scan")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)

    p = sub.add_parser("start-run", help="open one bounded execution run")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--max-claims", type=int, required=True)

    p = sub.add_parser("claim", help="atomically claim one route and return its lease token")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--lane", choices=("MATERIAL", "OBJECT"), required=True)
    p.add_argument("--owner", required=True)
    p.add_argument("--lease-seconds", type=int, default=300)

    p = sub.add_parser("finish", help="finish a claimed route; does not admit facts")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--business-key", required=True)
    p.add_argument("--route-key", required=True)
    p.add_argument("--token", required=True)
    p.add_argument("--outcome", choices=("DELIVERED", "NO_PROGRESS", "RETRY", "REJECTED"), required=True)
    p.add_argument("--error", default="")
    p.add_argument("--next-route")

    p = sub.add_parser("end-run", help="close a run and persist elapsed scan budget")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--run-id", required=True)

    p = sub.add_parser("extend-budget", help="append an explicit budget extension event")
    p.add_argument("--db", type=Path, required=True)
    p.add_argument("--scan-id", required=True)
    p.add_argument("--event-json", required=True, help="JSON object containing id, actor, reason, scope, revision and new limits")

    args = parser.parse_args(argv)
    if args.command == "init-shadow":
        if args.db.exists():
            raise ValueError("refusing to overwrite an existing database")
        db = harness.connect(args.db)
        apply_schema(db)
        db.close()
        result = {"database": str(args.db.resolve()), "status": "EMPTY_SHADOW_READY"}
    elif args.command == "clone-shadow":
        result = clone_shadow(args.source_db, args.db, args.expected_release_id)
    elif args.command in ("status", "delivery", "plan"):
        db = _open_db(args.db, readonly=True)
        if harness.meta(db, "epoch") is None:
            db.close()
            raise ValueError("derive material state before querying")
        m_tasks, o_tasks = material_queue(db), object_queue(db)
        if args.command == "delivery":
            result = object_delivery_summary(db)
        elif args.command == "status":
            statuses = Counter(r["status"] for r in object_material_coverage(db))
            result = {"release_id": harness.meta(db, "release_id"), "epoch": harness.meta(db, "epoch"),
                      "coverage": four_state_counts(db), "material_tasks": len(m_tasks),
                      "object_tasks": len(o_tasks), "object_scope_status": dict(statuses),
                      "delivery_N_R_C_RC": object_delivery_summary(db)}
        else:
            if args.limit < 1 or args.limit > 10000:
                raise ValueError("limit must be between 1 and 10000")
            result = {"epoch": harness.meta(db, "epoch"), "material": _limit_rows(m_tasks, args.limit),
                      "object": _limit_rows(o_tasks, args.limit)}
        db.close()
    else:
        db = _open_db(args.db, require_runtime=args.command not in ("status", "delivery", "plan"))
        if args.command == "create-scan":
            data_epoch = harness.meta(db, "epoch")
            if not data_epoch:
                raise ValueError("recompute the shadow database before creating a scan")
            result = create_scan(db, args.scan_id, args.purpose, data_epoch, _tree_epoch(db), args.claims, args.seconds)
        elif args.command == "seed-scan":
            scan = db.execute("SELECT data_epoch,tree_epoch FROM scans WHERE scan_id=?", (args.scan_id,)).fetchone()
            if not scan:
                raise ValueError("unknown scan")
            if scan["data_epoch"] != harness.meta(db, "epoch") or scan["tree_epoch"] != _tree_epoch(db):
                raise ValueError("data/tree changed; explicitly migrate the scan frontier")
            tasks = material_queue(db) + object_queue(db)
            result = seed_scan_frontier(db, args.scan_id, tasks, scan["data_epoch"], scan["tree_epoch"])
        elif args.command == "start-run":
            result = start_scan_run(db, args.scan_id, args.run_id, args.max_claims)
        elif args.command == "claim":
            result = claim_scan_route(db, args.scan_id, args.run_id, args.lane, args.owner, args.lease_seconds)
        elif args.command == "finish":
            result = finish_scan_route(db, args.scan_id, args.run_id, args.business_key, args.route_key,
                                       args.token, args.outcome, args.error, args.next_route)
        elif args.command == "end-run":
            result = end_scan_run(db, args.scan_id, args.run_id)
        else:
            result = extend_scan_budget(db, args.scan_id, json.loads(args.event_json))
        db.close()
    print(_json(result))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, sqlite3.Error, OSError, json.JSONDecodeError) as exc:
        print(_json({"error": str(exc)}), file=sys.stderr)
        sys.exit(2)
