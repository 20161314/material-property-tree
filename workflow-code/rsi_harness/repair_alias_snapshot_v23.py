#!/usr/bin/env python3
"""Fork a frozen RSI 2.3 snapshot and reconcile declared source aliases."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sqlite3

import harness
from import_snapshot import (
    SOURCE_ALIAS_COUNTS,
    add_inventory_alias_claim,
    read_csv,
    validate_alias_registry,
)
from queries_v23 import material_queue, object_queue
from rsi_v23 import _tree_epoch, clone_shadow
from runtime_v23 import create_scan, seed_scan_frontier
from verify_snapshot_v23 import verify


INVENTORY_KEY = "data/scaling_release_v1/object_component_inventory.csv"
REGISTRY_KEY = "dataset_registry.csv"


def task_signature(item):
    lane = item["lane"]
    task_type = item["task_type"]
    scope = item.get("attribute_scope", "NONE")
    subject = item.get("subject_id") or item.get("material_id") or item.get("object_id")
    parts = [lane, task_type, subject, scope]
    if lane == "OBJECT" and task_type != "OBJECT_DISCOVERY":
        parts.extend((str(item.get("component_id") or ""), str(item.get("obligation_id") or "")))
    return (
        "|".join(parts), str(item.get("route_key", "initial")).strip(), lane,
        task_type, subject, scope, item.get("priority", 0), item.get("depth", 0),
        item.get("family", "unclassified"), int(bool(item.get("flexible", False))),
    )


def stored_route_signatures(db, scan_id):
    return {tuple(row) for row in db.execute("""SELECT business_key,route_key,lane,task_type,
        subject_id,attribute_scope,priority,depth,family,flexible FROM scan_routes WHERE scan_id=?""",
        (scan_id,))}


def material_state_signature(db):
    return [tuple(row) for row in db.execute("""SELECT material_id,state,depth,direct_objects,
        effective_objects,missing_json,stats_json FROM material_state ORDER BY material_id""")]


def require_unstarted_scan(scan, route_states, active_runs):
    if not scan or scan["status"] != "READY":
        raise ValueError("parent scan must be READY before the alias-only fork")
    if scan["claims_spent"] != 0 or scan["seconds_spent"] != 0 or scan["budget_revision"] != 0:
        raise ValueError("parent scan has spend or budget history; use the reviewed scan migration path")
    if active_runs:
        raise ValueError("parent scan has an active run")
    if route_states and (set(route_states) != {"PENDING"}):
        raise ValueError("parent scan has route history; refusing to reset or discard it")


def _snapshot_pointer(db_path, pointer_path, export_path, parent, scan_id, alias_counts):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        meta = {r["key"]: json.loads(r["value"]) for r in db.execute("SELECT key,value FROM meta")}
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not scan:
            raise ValueError("new scan missing while preparing snapshot pointer")
        states = {str(r["state"]): r["n"] for r in db.execute(
            "SELECT state,count(*) n FROM material_state GROUP BY state")}
        counts = {
            "source_identities": db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0],
            "components": db.execute("SELECT count(*) FROM components").fetchone()[0],
            "material_nodes": db.execute("SELECT count(*) FROM material_state").fetchone()[0],
            "delivery_audit_rows": db.execute("SELECT count(*) FROM object_delivery_audits").fetchone()[0],
            "scope_audit_rows": db.execute("SELECT count(*) FROM object_scope_audits").fetchone()[0],
        }
        route_count = db.execute("SELECT count(*) FROM scan_routes WHERE scan_id=?", (scan_id,)).fetchone()[0]
    finally:
        db.close()
    database_relative = db_path.resolve().relative_to(pointer_path.parent.resolve())
    export_relative = export_path.resolve().relative_to(pointer_path.parent.resolve())
    return {
        "schema_version": 1,
        "snapshot_id": meta["rsi_shadow_snapshot_id"],
        "parent_snapshot_id": parent["snapshot_id"],
        "database": str(database_relative),
        "database_sha256": harness.digest_file(db_path),
        "export": str(export_relative),
        "source_release_id": parent["source_release_id"],
        "upstream_evidence_release_id": parent["upstream_evidence_release_id"],
        "data_epoch": meta["epoch"],
        "tree_epoch": scan["tree_epoch"],
        "rsi_schema": "2.3",
        "published": False,
        "production_migration_complete": False,
        "validation": {"integrity_check": "ok", "readonly_snapshot": True,
                       "derived_epoch_consistent": True},
        "counts": counts,
        "material_states": states,
        "alias_counts": alias_counts,
        "reviewed_alias_counts": alias_counts,
        "scan": {
            "scan_id": scan_id, "status": scan["status"], "routes": route_count,
            "claims_limit": scan["claims_limit"], "claims_spent": scan["claims_spent"],
            "seconds_limit": scan["seconds_limit"], "seconds_spent": scan["seconds_spent"],
            "budget_revision": scan["budget_revision"],
        },
        "alias_migration": {"revision": "source-alias-repair-v1",
                             "identity_counts_additive": False},
    }


def repair(parent_pointer, root, output_db, output_pointer, output_export, snapshot_id):
    parent_pointer = Path(parent_pointer).resolve()
    root = Path(root).resolve()
    output_db = Path(output_db).resolve()
    output_pointer = Path(output_pointer).resolve()
    output_export = Path(output_export).resolve()
    if output_db.exists() or output_pointer.exists() or output_export.exists():
        raise ValueError("all output paths must be new; refusing to overwrite")
    if not output_db.is_relative_to(root / "rsi_harness"):
        raise ValueError("new shadow database must stay under rsi_harness")
    if not output_pointer.is_relative_to(root / "rsi_harness"):
        raise ValueError("new snapshot pointer must stay under rsi_harness")
    if not output_export.is_relative_to(root / "rsi_harness"):
        raise ValueError("new export must stay under rsi_harness")

    verify(parent_pointer)
    parent = json.loads(parent_pointer.read_text(encoding="utf-8"))
    source_db = (parent_pointer.parent / parent["database"]).resolve()
    inventory_path = root / INVENTORY_KEY
    registry_path = root / REGISTRY_KEY
    parent_db = sqlite3.connect(source_db.as_uri() + "?mode=ro&immutable=1", uri=True)
    parent_db.row_factory = sqlite3.Row
    try:
        pinned_inputs = harness.meta(parent_db, "inputs", {})
        if pinned_inputs.get(INVENTORY_KEY) != harness.digest_file(inventory_path):
            raise ValueError("current component inventory differs from the frozen parent snapshot")
        old_scan = parent_db.execute("SELECT * FROM scans WHERE scan_id=?",
                                     (parent["scan"]["scan_id"],)).fetchone()
        route_count = parent_db.execute("SELECT count(*) FROM scan_routes WHERE scan_id=?",
                                        (old_scan["scan_id"],)).fetchone()[0] if old_scan else 0
        route_states = Counter(r["status"] for r in parent_db.execute(
            "SELECT status FROM scan_routes WHERE scan_id=?", (old_scan["scan_id"],)))
        active_runs = bool(parent_db.execute("SELECT 1 FROM scan_runs WHERE scan_id=? AND active=1",
                                             (old_scan["scan_id"],)).fetchone()) if old_scan else False
        require_unstarted_scan(old_scan, route_states, active_runs)
        if route_count and route_states != Counter({"PENDING": route_count}):
            raise ValueError("parent scan route counts are inconsistent")
        if old_scan["tree_epoch"] != _tree_epoch(parent_db):
            raise ValueError("parent scan tree epoch is stale")
        expected_routes = {task_signature(task) for task in material_queue(parent_db) + object_queue(parent_db)}
        if expected_routes != stored_route_signatures(parent_db, old_scan["scan_id"]):
            raise ValueError("parent scan routes differ from the current deterministic task queues")
        old_states = material_state_signature(parent_db)
        old_queue_count = len(expected_routes)
        claims_limit, seconds_limit = old_scan["claims_limit"], old_scan["seconds_limit"]
        purpose, old_scan_id = old_scan["purpose"], old_scan["scan_id"]
    finally:
        parent_db.close()

    registry_rows = list(read_csv(registry_path))
    validate_alias_registry(registry_rows)
    claims = {}
    for row in read_csv(inventory_path):
        add_inventory_alias_claim(claims, row)
    alias_counts = dict(Counter(namespace for namespace, _ in claims))
    if alias_counts != SOURCE_ALIAS_COUNTS:
        raise ValueError("source alias counts mismatch: " + repr(alias_counts))
    if any(not claim["reviewed"] for claim in claims.values()):
        raise ValueError("source alias set contains an unreviewed mapping")

    clone_shadow(source_db, output_db, parent["source_release_id"])
    db = sqlite3.connect(output_db, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    try:
        if db.execute("SELECT count(*) FROM object_aliases").fetchone()[0]:
            raise ValueError("parent clone already has aliases; refusing duplicate migration")
        for (namespace, source_uid), claim in sorted(claims.items()):
            canonical = db.execute("SELECT namespace,source_uid FROM objects WHERE id=?",
                                   (claim["object_id"],)).fetchone()
            if not canonical:
                raise ValueError("source alias points to missing canonical object: " + claim["object_id"])
            if namespace == "SLATPHYS" and (canonical["namespace"] != "PIXIEVERSE"
                                               or canonical["source_uid"] != source_uid):
                raise ValueError("SLATPHYS alias does not match the canonical PIXIEVerse UID")
            if namespace == "NVIDIA-SIMREADY-LEGACY-PACKS" and canonical["namespace"] != "VOMP-GVM-PUBLIC":
                raise ValueError("legacy SimReady alias target is not a GVM object")
        input_hashes = harness.meta(db, "inputs", {})
        input_hashes[REGISTRY_KEY] = harness.digest_file(registry_path)
        harness.set_meta(db, "inputs", input_hashes)
        harness.set_meta(db, "rsi_shadow_snapshot_id", snapshot_id)
        harness.set_meta(db, "rsi_shadow_parent_snapshot_id", parent["snapshot_id"])
        harness.set_meta(db, "rsi_shadow_alias_migration", "source-alias-repair-v1")
        with harness.transaction(db):
            for (namespace, source_uid), claim in sorted(claims.items()):
                db.execute("INSERT INTO object_aliases(namespace,source_uid,object_id,basis,reviewed) VALUES(?,?,?,?,?)",
                           (namespace, source_uid, claim["object_id"], claim["basis"], claim["reviewed"]))
            harness.set_meta(db, "object_alias_counts", alias_counts)
            harness.event(db, "SOURCE_ALIASES_IMPORTED", {
                "revision": "source-alias-repair-v1", "alias_counts": alias_counts,
                "source_registry_sha256": input_hashes[REGISTRY_KEY],
                "inventory_sha256": input_hashes[INVENTORY_KEY],
                "identity_counts_additive": False,
            })
        harness.recompute(db)
        if material_state_signature(db) != old_states:
            raise ValueError("alias-only import changed material coverage/state facts")
        if _tree_epoch(db) != old_scan["tree_epoch"]:
            raise ValueError("alias-only import unexpectedly changed the material tree")
        tasks = material_queue(db) + object_queue(db)
        if {task_signature(task) for task in tasks} != expected_routes:
            raise ValueError("alias-only import changed the deterministic task frontier")

        scan_id = old_scan_id + "-ALIAS-REPAIRED"
        data_epoch = harness.meta(db, "epoch")
        tree_epoch = _tree_epoch(db)
        create_scan(db, scan_id, purpose, data_epoch, tree_epoch, claims_limit, seconds_limit)
        seeded = seed_scan_frontier(db, scan_id, tasks, data_epoch, tree_epoch)
        if seeded["frontier_routes"] != old_queue_count:
            raise ValueError("new scan frontier count differs from the parent snapshot")
        harness.export(db, output_export)
        db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        if db.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower() != "delete":
            raise ValueError("new snapshot database must be self-contained")
        if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("new snapshot integrity check failed")
    except Exception:
        db.close()
        raise
    db.close()

    pointer = _snapshot_pointer(output_db, output_pointer, output_export, parent, scan_id, alias_counts)
    output_pointer.write_text(json.dumps(pointer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verified = verify(output_pointer)
    pointer["validation"] = {"integrity_check": "ok", "readonly_snapshot": True,
                             "derived_epoch_consistent": True,
                             "status": verified["status"],
                             "database_sha256": verified["database_sha256"]}
    output_pointer.write_text(json.dumps(pointer, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    verified = verify(output_pointer)
    return {"status": verified["status"], "snapshot_id": verified["snapshot_id"],
            "database": str(output_db), "pointer": str(output_pointer),
            "alias_counts": verified["alias_counts"], "scan_routes": verified["counts"]["scan_routes"],
            "material_states": verified["material_states"], "database_sha256": verified["database_sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--parent-pointer", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--pointer-out", type=Path, required=True)
    parser.add_argument("--export", type=Path, required=True)
    parser.add_argument("--snapshot-id", required=True)
    args = parser.parse_args()
    result = repair(args.parent_pointer, args.root, args.db, args.pointer_out,
                    args.export, args.snapshot_id)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, sqlite3.Error, OSError, json.JSONDecodeError) as error:
        raise SystemExit(str(error))
