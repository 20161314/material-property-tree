#!/usr/bin/env python3
"""Verify a closed, immutable RSI 2.3 snapshot against its versioned pointer."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _meta(db):
    return {r["key"]: json.loads(r["value"]) for r in db.execute("SELECT key,value FROM meta")}


def verify(pointer_path, integrity_check=True):
    pointer_path = Path(pointer_path).resolve()
    pointer = json.loads(pointer_path.read_text(encoding="utf-8"))
    database = (pointer_path.parent / pointer["database"]).resolve()
    if not database.is_relative_to(pointer_path.parent) or not database.is_file():
        raise ValueError("snapshot DB must exist under its versioned pointer directory")
    for suffix in ("-wal", "-journal"):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise ValueError("snapshot has a nonempty SQLite sidecar: " + sidecar.name)
    before = database.stat()
    identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
    if sha(database) != pointer["database_sha256"]:
        raise ValueError("snapshot DB hash differs from pointer")
    db = sqlite3.connect(database.as_uri() + "?mode=ro&immutable=1", uri=True, timeout=30)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA query_only=ON")
    try:
        meta = _meta(db)
        if meta.get("rsi_shadow_schema") != "2.3":
            raise ValueError("snapshot is not RSI schema 2.3")
        if (pointer.get("snapshot_id") and meta.get("rsi_shadow_snapshot_id")
                and meta["rsi_shadow_snapshot_id"] != pointer["snapshot_id"]):
            raise ValueError("snapshot ID differs from pointer")
        if meta.get("rsi_shadow_parent_release_id") != pointer["source_release_id"]:
            raise ValueError("snapshot parent release differs from pointer")
        if meta.get("release_id") != pointer["source_release_id"]:
            raise ValueError("fact release differs from pointer")
        if meta.get("epoch") != pointer["data_epoch"]:
            raise ValueError("fact epoch differs from pointer")
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (pointer["scan"]["scan_id"],)).fetchone()
        if not scan:
            raise ValueError("pointer scan_id is absent from snapshot")
        if scan["data_epoch"] != pointer["data_epoch"] or scan["tree_epoch"] != pointer["tree_epoch"]:
            raise ValueError("scan epochs differ from pointer")
        stale = db.execute("SELECT count(*) FROM material_state WHERE epoch<>?", (pointer["data_epoch"],)).fetchone()[0]
        if stale:
            raise ValueError("derived material states are stale")
        if integrity_check and db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity_check failed")
        counts = {
            "source_identities": db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0],
            "components": db.execute("SELECT count(*) FROM components").fetchone()[0],
            "material_nodes": db.execute("SELECT count(*) FROM material_state").fetchone()[0],
            "delivery_audit_rows": db.execute("SELECT count(*) FROM object_delivery_audits").fetchone()[0],
            "scope_audit_rows": db.execute("SELECT count(*) FROM object_scope_audits").fetchone()[0],
            "scan_routes": db.execute("SELECT count(*) FROM scan_routes WHERE scan_id=?", (scan["scan_id"],)).fetchone()[0],
        }
        alias_counts = {r["namespace"]: r["n"] for r in db.execute(
            "SELECT namespace,count(*) n FROM object_aliases GROUP BY namespace")}
        reviewed_alias_counts = {r["namespace"]: r["n"] for r in db.execute(
            "SELECT namespace,count(*) n FROM object_aliases WHERE reviewed=1 GROUP BY namespace")}
        if "alias_counts" in pointer and alias_counts != pointer["alias_counts"]:
            raise ValueError("source alias counts differ from pointer")
        if "reviewed_alias_counts" in pointer and reviewed_alias_counts != pointer["reviewed_alias_counts"]:
            raise ValueError("reviewed source alias counts differ from pointer")
        if counts["source_identities"] != pointer["counts"]["source_identities"]:
            raise ValueError("source identity count differs from pointer")
        if counts["components"] != pointer["counts"]["components"]:
            raise ValueError("component count differs from pointer")
        if counts["material_nodes"] != pointer["counts"]["material_nodes"]:
            raise ValueError("material count differs from pointer")
        if counts["scan_routes"] != pointer["scan"]["routes"]:
            raise ValueError("scan route count differs from pointer")
        states = {str(r["state"]): r["n"] for r in db.execute(
            "SELECT state,count(*) n FROM material_state GROUP BY state")}
        if states != pointer["material_states"]:
            raise ValueError("material state counts differ from pointer")
    finally:
        db.close()
    after = database.stat()
    if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) != identity:
        raise ValueError("snapshot DB identity changed during verification")
    if sha(database) != pointer["database_sha256"]:
        raise ValueError("snapshot DB changed during verification")
    for suffix in ("-wal", "-journal"):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise ValueError("snapshot acquired a nonempty SQLite sidecar")
    return {"status": "PASS_V23_SNAPSHOT_PIN", "snapshot_id": pointer["snapshot_id"],
            "release_id": pointer["source_release_id"], "database_sha256": pointer["database_sha256"],
            "counts": counts, "material_states": states,
            "alias_counts": alias_counts, "reviewed_alias_counts": reviewed_alias_counts,
            "scan_status": scan["status"], "scan_claims_spent": scan["claims_spent"],
            "production_migration_complete": pointer.get("production_migration_complete", False)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pointer", type=Path, required=True)
    parser.add_argument("--skip-integrity-check", action="store_true")
    args = parser.parse_args()
    print(json.dumps(verify(args.pointer, not args.skip_integrity_check), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
