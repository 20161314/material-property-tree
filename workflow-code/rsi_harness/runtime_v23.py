"""Small transactional runtime for the additive RSI 2.3 shadow schema.

It records execution metadata and guards an eventual facts merger. It never
inserts objects, components, materials, observations, or relations on behalf
of a collector.
"""
import hashlib
import json
import math
import re
import sqlite3
import time
import uuid
from pathlib import Path

import harness


_MATERIAL_TASK_TYPES = {
    "MATERIAL_VALUE_REPAIR",
    "MATERIAL_OPTIONAL_RESEARCH",
    "SOURCE_ENHANCEMENT",
    "MATERIAL_SCOPE_OBLIGATION_REPAIR",
}
_OBJECT_TASK_TYPES = {
    "OBJECT_DISCOVERY",
    "OBJECT_COMPONENT_REPAIR",
    "OBJECT_SCOPE_REPAIR",
    "OBJECT_ASSET_REPAIR",
    "OBJECT_LABEL_REPAIR",
}


def apply_schema(db):
    db.executescript((Path(__file__).parent / "schema_v23.sql").read_text())


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _positive_int(value, name, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, int) or (value < 0 if allow_zero else value < 1):
        raise ValueError(name + " must be an integer")
    return value


def _finite(value, name, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or (value < 0 if allow_zero else value <= 0):
        raise ValueError(name + " must be finite")
    return float(value)


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + " is required")
    return value.strip()


def _sha256(value, name):
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(name + " must be a lowercase SHA256 hex digest")
    return value


def create_scan(db, scan_id, purpose, data_epoch, tree_epoch, claims_limit, seconds_limit, now=None):
    if not isinstance(scan_id, str) or not scan_id.strip():
        raise ValueError("scan_id is required")
    if purpose not in ("MATERIAL", "OBJECT", "MIXED"):
        raise ValueError("invalid scan purpose")
    claims_limit = _positive_int(claims_limit, "claims_limit", True)
    seconds_limit = _finite(seconds_limit, "seconds_limit", True)
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        if db.execute("SELECT 1 FROM scans WHERE scan_id=?", (scan_id,)).fetchone():
            raise ValueError("scan already exists")
        db.execute("""INSERT INTO scans(scan_id,purpose,data_epoch,tree_epoch,status,
                    claims_limit,seconds_limit,created_at,updated_at)
                    VALUES(?,?,?,?,?,?,?,?,?)""",
                   (scan_id.strip(), purpose, data_epoch, tree_epoch, "READY",
                    claims_limit, seconds_limit, now, now))
        harness.event(db, "SCAN_CREATED", {"scan_id": scan_id, "purpose": purpose,
                                             "data_epoch": data_epoch, "tree_epoch": tree_epoch})
    return {"scan_id": scan_id, "status": "READY", "claims_limit": claims_limit,
            "seconds_limit": seconds_limit}


def seed_scan_frontier(db, scan_id, tasks, data_epoch, tree_epoch, now=None):
    """Add eligible deterministic tasks without resetting completed routes or spend."""
    now = time.time() if now is None else float(now)
    tasks = list(tasks)
    prepared = []
    for item in tasks:
        lane = item.get("lane")
        task_type = item.get("task_type")
        state = item.get("state")
        if lane not in ("MATERIAL", "OBJECT") or not task_type:
            raise ValueError("task lane and type are required")
        allowed_types = _MATERIAL_TASK_TYPES if lane == "MATERIAL" else _OBJECT_TASK_TYPES
        if task_type not in allowed_types:
            raise ValueError("task type is not valid for lane: " + str(task_type))
        if lane == "OBJECT" and task_type == "OBJECT_DISCOVERY":
            if isinstance(state, bool) or not isinstance(state, int) or state not in (1, 2):
                raise ValueError("new object discovery is limited to material states 1 and 2")
        if lane == "OBJECT" and task_type != "OBJECT_DISCOVERY":
            if item.get("existing_object") is not True:
                raise ValueError("object repair task must identify an existing object")
            object_id = item.get("object_id")
            if not object_id or item.get("subject_id", object_id) != object_id:
                raise ValueError("object repair subject must match its object_id")
        scope = item.get("attribute_scope", "NONE")
        route_key = item.get("route_key", "initial")
        subject = item.get("subject_id") or item.get("material_id") or item.get("object_id")
        family = item.get("family", "unclassified")
        for value, label in ((subject, "subject_id"), (scope, "attribute_scope"),
                             (route_key, "route_key"), (family, "family")):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(label + " is required")
        priority = item.get("priority", 0)
        if isinstance(priority, bool) or not isinstance(priority, int):
            raise ValueError("priority must be an integer")
        depth = _positive_int(item.get("depth", 0), "depth", True)
        business_key_parts = [lane, task_type, subject, scope]
        if lane == "OBJECT" and task_type != "OBJECT_DISCOVERY":
            obligation_id = item.get("obligation_id")
            component_id = item.get("component_id")
            if not obligation_id and not component_id:
                raise ValueError("object repair task must have a component or obligation identity")
            business_key_parts.extend((str(component_id or ""), str(obligation_id or "")))
        business_key = "|".join(business_key_parts)
        prepared.append((business_key, lane, task_type, subject, scope, priority, depth,
                         family, int(bool(item.get("flexible", False))), route_key.strip()))
    with harness.transaction(db):
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not scan:
            raise ValueError("unknown scan")
        if scan["status"] == "CANCELLED":
            raise ValueError("cancelled scan cannot accept new routes")
        if (scan["data_epoch"], scan["tree_epoch"]) != (data_epoch, tree_epoch):
            raise ValueError("scan epoch mismatch; explicitly migrate the frontier")
        if scan["purpose"] != "MIXED" and any(row[1] != scan["purpose"] for row in prepared):
            raise ValueError("route lane is outside scan purpose")
        for item in tasks:
            lane, task_type = item["lane"], item["task_type"]
            if lane == "OBJECT" and task_type == "OBJECT_DISCOVERY":
                material_id = item.get("material_id") or item.get("subject_id")
                actual = db.execute("SELECT state,epoch FROM material_state WHERE material_id=?", (material_id,)).fetchone()
                if not actual or actual["epoch"] != data_epoch or actual["state"] != item["state"]:
                    raise ValueError("object discovery state must match current derived material state")
            elif lane == "MATERIAL" and task_type == "MATERIAL_SCOPE_OBLIGATION_REPAIR":
                obligation_id = item.get("obligation_id") or item.get("subject_id")
                if not obligation_id or item.get("subject_id", obligation_id) != obligation_id:
                    raise ValueError("material scope repair subject must match its obligation")
                obligation = db.execute("SELECT object_id,resolved FROM obligations WHERE id=?",
                                        (obligation_id,)).fetchone()
                if not obligation or obligation["resolved"] or obligation["object_id"] is not None:
                    raise ValueError("material scope repair must target an unresolved objectless obligation")
            elif lane == "OBJECT":
                object_id = item["object_id"]
                accepted = db.execute("SELECT accepted FROM objects WHERE id=?", (object_id,)).fetchone()
                if not accepted or accepted["accepted"] != 1:
                    raise ValueError("object repair must target an accepted existing object")
                component_id = item.get("component_id")
                obligation_id = item.get("obligation_id")
                if component_id and not db.execute(
                        "SELECT 1 FROM components WHERE object_id=? AND id=?", (object_id, component_id)).fetchone():
                    raise ValueError("object repair component does not exist on the target object")
                if obligation_id:
                    obligation = db.execute("SELECT object_id,component_id,resolved FROM obligations WHERE id=?",
                                             (obligation_id,)).fetchone()
                    if (not obligation or obligation["resolved"] or obligation["object_id"] != object_id
                            or (obligation["component_id"] and obligation["component_id"] != component_id)):
                        raise ValueError("object repair obligation is absent, resolved or targets another scope")
        for row in prepared:
            db.execute("""INSERT OR IGNORE INTO scan_routes(
              scan_id,business_key,lane,task_type,subject_id,attribute_scope,priority,depth,
              family,flexible,route_key,status,first_seen,updated_at)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,'PENDING',?,?)""", (scan_id, *row, now, now))
        pending = [dict(r) for r in db.execute("""SELECT business_key,route_key,lane,task_type,subject_id,
                            attribute_scope,priority,depth,family FROM scan_routes
                            WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')
                            ORDER BY priority,depth,family,subject_id,attribute_scope,route_key""", (scan_id,))]
        next_status = 'READY' if pending else 'COMPLETE'
        db.execute("UPDATE scans SET frontier_json=?,status=?,updated_at=? WHERE scan_id=?",
                   (_json(pending), next_status, now, scan_id))
    return {"scan_id": scan_id, "added_routes": len(prepared), "frontier_routes": len(pending)}


def start_scan_run(db, scan_id, run_id, max_claims, now=None):
    now = time.time() if now is None else float(now)
    max_claims = _positive_int(max_claims, "max_claims")
    with harness.transaction(db):
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not scan:
            raise ValueError("unknown scan")
        if scan["status"] == "CANCELLED":
            raise ValueError("cancelled scan cannot be restarted")
        if db.execute("SELECT 1 FROM scan_runs WHERE scan_id=? AND active=1", (scan_id,)).fetchone():
            raise ValueError("scan already has an active execution run")
        if scan["claims_spent"] >= scan["claims_limit"] or scan["seconds_spent"] >= scan["seconds_limit"]:
            db.execute("UPDATE scans SET status='PAUSED_BUDGET',updated_at=? WHERE scan_id=?", (now, scan_id))
            raise ValueError("scan budget exhausted; append an authorized budget event first")
        if not db.execute("SELECT 1 FROM scan_routes WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')", (scan_id,)).fetchone():
            db.execute("UPDATE scans SET status='COMPLETE',updated_at=? WHERE scan_id=?", (now, scan_id))
            raise ValueError("scan frontier is complete")
        db.execute("INSERT INTO scan_runs(run_id,scan_id,started_at,max_claims) VALUES(?,?,?,?)",
                   (run_id, scan_id, now, max_claims))
        db.execute("UPDATE scans SET status='RUNNING',updated_at=? WHERE scan_id=?", (now, scan_id))
    return {"run_id": run_id, "scan_id": scan_id, "started_at": now}


def _close_route_leases(db, scan_id, reason, now, expired_only=False):
    condition = " AND lease_until<=?" if expired_only else ""
    params = (scan_id, now) if expired_only else (scan_id,)
    routes = list(db.execute("""SELECT business_key,route_key,lease_token,lease_owner,lease_until,attempts
        FROM scan_routes WHERE scan_id=? AND status='LEASED'""" + condition, params))
    event_kind = "SCAN_ROUTE_LEASE_EXPIRED" if expired_only else "SCAN_ROUTE_LEASE_REVOKED"
    for route in routes:
        harness.event(db, event_kind, {
            "scan_id": scan_id,
            "business_key": route["business_key"],
            "route_key": route["route_key"],
            "lease_token": route["lease_token"],
            "lease_owner": route["lease_owner"],
            "lease_until": route["lease_until"],
            "attempt": route["attempts"],
            "reason": reason,
        })
        db.execute("""UPDATE scan_routes SET status='COOLDOWN',lease_token=NULL,lease_owner=NULL,
            lease_until=NULL,updated_at=? WHERE scan_id=? AND business_key=? AND route_key=?
            AND status='LEASED' AND lease_token=?""",
            (now, scan_id, route["business_key"], route["route_key"], route["lease_token"]))
    return len(routes)


def inspect_runtime_consistency(db, scan_id=None, now=None):
    """Return a read-only diagnosis of interrupted scan/run/lease state.

    The diagnostic digest is a recovery precondition.  It prevents an operator
    from closing a newer run using a stale crash report and never changes scan
    budgets, attempts, or route state.
    """
    now = time.time() if now is None else float(now)
    params = () if scan_id is None else (scan_id,)
    where = "" if scan_id is None else " WHERE scan_id=?"
    scans = list(db.execute("SELECT * FROM scans" + where + " ORDER BY scan_id", params))
    issues = []
    for scan in scans:
        sid = scan["scan_id"]
        active_runs = list(db.execute(
            "SELECT * FROM scan_runs WHERE scan_id=? AND active=1 ORDER BY run_id", (sid,)
        ))
        if scan["status"] == "RUNNING" and not active_runs:
            issues.append({"scan_id": sid, "kind": "RUNNING_WITHOUT_ACTIVE_RUN"})
        if scan["status"] != "RUNNING" and active_runs:
            issues.append({"scan_id": sid, "kind": "ACTIVE_RUN_WITH_NONRUNNING_SCAN",
                           "run_ids": [row["run_id"] for row in active_runs]})
        if len(active_runs) > 1:
            issues.append({"scan_id": sid, "kind": "MULTIPLE_ACTIVE_RUNS",
                           "run_ids": [row["run_id"] for row in active_runs]})
        active_by_id = {row["run_id"]: row for row in active_runs}
        leased = list(db.execute(
            "SELECT * FROM scan_routes WHERE scan_id=? AND status='LEASED' ORDER BY business_key,route_key",
            (sid,),
        ))
        claim_events = {}
        for event in db.execute("SELECT payload_json FROM events WHERE kind='SCAN_ROUTE_CLAIMED'"):
            try:
                payload = json.loads(event[0])
            except (TypeError, ValueError, json.JSONDecodeError):
                continue
            if payload.get("scan_id") == sid and payload.get("lease_token"):
                claim_events[payload["lease_token"]] = payload
        for route in leased:
            token = route["lease_token"]
            claim = claim_events.get(token)
            if not claim:
                issues.append({"scan_id": sid, "kind": "LEASE_WITHOUT_CLAIM_EVENT",
                               "business_key": route["business_key"], "route_key": route["route_key"],
                               "lease_token": token})
            elif claim.get("run_id") not in active_by_id:
                issues.append({"scan_id": sid, "kind": "LEASE_ON_INACTIVE_RUN",
                               "business_key": route["business_key"], "route_key": route["route_key"],
                               "lease_token": token, "run_id": claim.get("run_id")})
            if route["lease_until"] is None or route["lease_until"] <= now:
                issues.append({"scan_id": sid, "kind": "EXPIRED_LEASE_LEFT_OPEN",
                               "business_key": route["business_key"], "route_key": route["route_key"],
                               "lease_token": token, "lease_until": route["lease_until"]})
    canonical = _json(sorted(issues, key=lambda item: _json(item)))
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return {"status": "PASS_RUNTIME_CONSISTENT" if not issues else "HOLD_RUNTIME_RECONCILIATION_REQUIRED",
            "scan_id": scan_id, "now": now, "issues": issues, "issue_digest": digest}


def recover_stale_run(db, scan_id, run_id, actor, reason, expected_issue_digest,
                      now=None):
    """Explicitly close an interrupted run after a pinned diagnosis.

    Recovery is append-only at the event layer and preserves claims spent,
    route attempts, the scan frontier, and all budget extensions.  A fresh
    diagnosis must still match inside the transaction; otherwise the caller
    must inspect again instead of closing a newer run.
    """
    actor = _text(actor, "actor")
    reason = _text(reason, "reason")
    expected_issue_digest = _sha256(expected_issue_digest, "expected_issue_digest")
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        diagnosis = inspect_runtime_consistency(db, scan_id=scan_id, now=now)
        if diagnosis["issue_digest"] != expected_issue_digest:
            raise ValueError("runtime diagnosis changed; inspect again before recovery")
        if diagnosis["status"] == "PASS_RUNTIME_CONSISTENT":
            raise ValueError("runtime is consistent; refusing recovery")
        run = db.execute("SELECT * FROM scan_runs WHERE scan_id=? AND run_id=? AND active=1",
                         (scan_id, run_id)).fetchone()
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not run or not scan:
            raise ValueError("stale active run is absent; inspect again")
        elapsed = max(0, now - run["started_at"])
        seconds = scan["seconds_spent"] + elapsed
        revoked = _close_route_leases(db, scan_id, "RUN_RECOVERED", now)
        unfinished = db.execute(
            "SELECT count(*) FROM scan_routes WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')",
            (scan_id,),
        ).fetchone()[0]
        if seconds >= scan["seconds_limit"] or scan["claims_spent"] >= scan["claims_limit"]:
            status = "PAUSED_BUDGET" if unfinished else "COMPLETE"
        else:
            status = "READY" if unfinished else "COMPLETE"
        pending = [dict(row) for row in db.execute(
            """SELECT business_key,route_key,lane,task_type,subject_id,attribute_scope,
                      priority,depth,family FROM scan_routes
               WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')
               ORDER BY priority,depth,family,subject_id,attribute_scope,route_key""", (scan_id,)
        )]
        db.execute("UPDATE scan_runs SET active=0,finished_at=? WHERE run_id=? AND active=1",
                   (now, run_id))
        db.execute("UPDATE scans SET seconds_spent=?,status=?,frontier_json=?,updated_at=? WHERE scan_id=?",
                   (seconds, status, _json(pending), now, scan_id))
        harness.event(db, "SCAN_RUN_RECOVERED", {
            "scan_id": scan_id, "run_id": run_id, "actor": actor, "reason": reason,
            "issue_digest": expected_issue_digest, "elapsed_seconds": elapsed,
            "leases_revoked": revoked, "claims_spent_preserved": scan["claims_spent"],
            "seconds_spent_before": scan["seconds_spent"], "seconds_spent_after": seconds,
        })
    return {"scan_id": scan_id, "run_id": run_id, "status": status,
            "seconds_spent": seconds, "leases_revoked": revoked,
            "issue_digest": expected_issue_digest, "replayed": False}


def claim_scan_route(db, scan_id, run_id, lane, owner, lease_seconds=300, now=None):
    now = time.time() if now is None else float(now)
    if lane not in ("MATERIAL", "OBJECT") or not owner or lease_seconds < 1 or lease_seconds > 3600:
        raise ValueError("invalid route claim")
    with harness.transaction(db):
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        run = db.execute("SELECT * FROM scan_runs WHERE scan_id=? AND run_id=? AND active=1", (scan_id, run_id)).fetchone()
        if not scan or not run:
            raise ValueError("scan run is not active")
        if scan["status"] != "RUNNING":
            raise ValueError("scan is not in RUNNING state")
        _close_route_leases(db, scan_id, "LEASE_EXPIRED", now, expired_only=True)
        elapsed = now - run["started_at"]
        if (run["claims"] >= run["max_claims"] or scan["claims_spent"] >= scan["claims_limit"]
                or scan["seconds_spent"] + elapsed >= scan["seconds_limit"]):
            seconds = scan["seconds_spent"] + max(0, elapsed)
            exhausted = scan["claims_spent"] >= scan["claims_limit"] or seconds >= scan["seconds_limit"]
            unfinished = db.execute("SELECT count(*) FROM scan_routes WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')", (scan_id,)).fetchone()[0]
            status = ('PAUSED_BUDGET' if unfinished else 'COMPLETE') if exhausted else ('READY' if unfinished else 'COMPLETE')
            db.execute("UPDATE scan_runs SET active=0,finished_at=? WHERE run_id=?", (now, run_id))
            db.execute("UPDATE scans SET seconds_spent=?,status=?,updated_at=? WHERE scan_id=?", (seconds, status, now, scan_id))
            _close_route_leases(db, scan_id, "RUN_BUDGET_EXHAUSTED", now)
            return {"status": "BUDGET_EXHAUSTED" if exhausted else "RUN_BUDGET_EXHAUSTED",
                    "scan_status": status, "seconds_spent": seconds}
        candidates = [dict(r) for r in db.execute("""SELECT * FROM scan_routes WHERE scan_id=? AND lane=?
            AND status IN('PENDING','COOLDOWN') AND retry_at<=? ORDER BY priority,depth,family,subject_id,attribute_scope,route_key""",
            (scan_id, lane, now))]
        if not candidates:
            return {"status": "NO_READY_ROUTE"}
        first_priority, first_depth = candidates[0]["priority"], candidates[0]["depth"]
        candidates = [r for r in candidates if r["priority"] == first_priority and r["depth"] == first_depth]
        family_use = {r[0]: r[1] for r in db.execute("""SELECT family,sum(attempts) FROM scan_routes
                      WHERE scan_id=? AND lane=? AND priority=? AND depth=? GROUP BY family""",
                      (scan_id, lane, first_priority, first_depth))}
        subject_use = {r[0]: r[1] for r in db.execute("""SELECT subject_id,sum(attempts) FROM scan_routes
                      WHERE scan_id=? AND lane=? GROUP BY subject_id""", (scan_id, lane))}
        selected = min(candidates, key=lambda r: (family_use.get(r["family"], 0),
                         subject_use.get(r["subject_id"], 0), -r["flexible"], r["subject_id"],
                         r["attribute_scope"], r["route_key"]))
        token = uuid.uuid4().hex
        until = min(now + lease_seconds, run["started_at"] + max(0, scan["seconds_limit"] - scan["seconds_spent"]))
        db.execute("""UPDATE scan_routes SET status='LEASED',attempts=attempts+1,lease_token=?,
                    lease_owner=?,lease_until=?,updated_at=? WHERE scan_id=? AND business_key=? AND route_key=?""",
                   (token, owner, until, now, scan_id, selected["business_key"], selected["route_key"]))
        db.execute("UPDATE scan_runs SET claims=claims+1 WHERE run_id=?", (run_id,))
        db.execute("UPDATE scans SET claims_spent=claims_spent+1,updated_at=? WHERE scan_id=?", (now, scan_id))
        harness.event(db, "SCAN_ROUTE_CLAIMED", {"scan_id": scan_id, "run_id": run_id,
                                                   "business_key": selected["business_key"],
                                                   "route_key": selected["route_key"], "owner": owner,
                                                   "lease_token": token, "lease_until": until,
                                                   "attempt": selected["attempts"] + 1})
        return {**selected, "status": "LEASED", "token": token, "owner": owner, "lease_until": until}


def finish_scan_route(db, scan_id, run_id, business_key, route_key, token, outcome,
                      error="", next_route=None, cooldown_seconds=3600, now=None):
    now = time.time() if now is None else float(now)
    if outcome not in ("DELIVERED", "NO_PROGRESS", "RETRY", "REJECTED"):
        raise ValueError("invalid route outcome")
    with harness.transaction(db):
        run = db.execute("SELECT * FROM scan_runs WHERE scan_id=? AND run_id=? AND active=1", (scan_id, run_id)).fetchone()
        scan = db.execute("SELECT status FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        route = db.execute("SELECT * FROM scan_routes WHERE scan_id=? AND business_key=? AND route_key=?",
                           (scan_id, business_key, route_key)).fetchone()
        if not run or not scan or scan["status"] != "RUNNING" or not route or route["status"] != "LEASED" or route["lease_token"] != token or route["lease_until"] <= now:
            raise ValueError("route lease expired, replaced or token invalid")
        status = {"DELIVERED": "DONE", "NO_PROGRESS": "DONE", "RETRY": "COOLDOWN",
                  "REJECTED": "REJECTED"}[outcome]
        db.execute("""UPDATE scan_routes SET status=?,last_outcome=?,last_error=?,retry_at=?,lease_token=NULL,
                    lease_owner=NULL,lease_until=NULL,updated_at=? WHERE scan_id=? AND business_key=? AND route_key=?""",
                   (status, outcome, error, now + cooldown_seconds if status == "COOLDOWN" else 0,
                    now, scan_id, business_key, route_key))
        if next_route:
            next_route = _text(next_route, "next_route")
            if next_route == route_key:
                raise ValueError("next route must be distinct")
            db.execute("""INSERT OR IGNORE INTO scan_routes(scan_id,business_key,lane,task_type,subject_id,
                attribute_scope,priority,depth,family,flexible,route_key,status,first_seen,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,'PENDING',?,?)""",
                (scan_id, business_key, route["lane"], route["task_type"], route["subject_id"],
                 route["attribute_scope"], route["priority"], route["depth"], route["family"],
                 route["flexible"], next_route, now, now))
        harness.event(db, "SCAN_ROUTE_FINISHED", {"scan_id": scan_id, "run_id": run_id,
                                                    "business_key": business_key, "route_key": route_key,
                                                    "lease_token": token, "attempt": route["attempts"],
                                                    "outcome": outcome, "next_route": next_route})
    return {"business_key": business_key, "route_key": route_key, "status": status,
            "next_route": next_route}


def end_scan_run(db, scan_id, run_id, now=None):
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        run = db.execute("SELECT * FROM scan_runs WHERE scan_id=? AND run_id=? AND active=1", (scan_id, run_id)).fetchone()
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not run or not scan:
            raise ValueError("scan run is not active")
        elapsed = max(0, now - run["started_at"])
        seconds = scan["seconds_spent"] + elapsed
        _close_route_leases(db, scan_id, "LEASE_EXPIRED", now, expired_only=True)
        unfinished = db.execute("SELECT count(*) FROM scan_routes WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')", (scan_id,)).fetchone()[0]
        if seconds >= scan["seconds_limit"] or scan["claims_spent"] >= scan["claims_limit"]:
            status = "PAUSED_BUDGET" if unfinished else "COMPLETE"
        else:
            status = "READY" if unfinished else "COMPLETE"
        db.execute("UPDATE scan_runs SET active=0,finished_at=? WHERE run_id=?", (now, run_id))
        db.execute("UPDATE scans SET seconds_spent=?,status=?,updated_at=? WHERE scan_id=?", (seconds, status, now, scan_id))
        _close_route_leases(db, scan_id, "RUN_ENDED", now)
        pending = [dict(r) for r in db.execute("""SELECT business_key,route_key,lane,task_type,subject_id,
                            attribute_scope,priority,depth,family FROM scan_routes
                            WHERE scan_id=? AND status IN('PENDING','LEASED','COOLDOWN')
                            ORDER BY priority,depth,family,subject_id,attribute_scope,route_key""", (scan_id,))]
        db.execute("UPDATE scans SET frontier_json=? WHERE scan_id=?", (_json(pending), scan_id))
    return {"scan_id": scan_id, "run_id": run_id, "status": status,
            "seconds_spent": seconds, "unfinished_routes": unfinished}


def cancel_scan(db, scan_id, actor, reason, now=None):
    """Irreversibly cancel a scan and invalidate its active leases."""
    actor = _text(actor, "actor")
    reason = _text(reason, "reason")
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not scan:
            raise ValueError("unknown scan")
        if scan["status"] == "CANCELLED":
            return {"scan_id": scan_id, "status": "CANCELLED", "replayed": True}
        active_runs = list(db.execute("SELECT * FROM scan_runs WHERE scan_id=? AND active=1", (scan_id,)))
        spent_seconds = scan["seconds_spent"]
        for run in active_runs:
            spent_seconds += max(0, now - run["started_at"])
            db.execute("UPDATE scan_runs SET active=0,finished_at=? WHERE run_id=?", (now, run["run_id"]))
        _close_route_leases(db, scan_id, "LEASE_EXPIRED", now, expired_only=True)
        _close_route_leases(db, scan_id, "SCAN_CANCELLED", now)
        db.execute("UPDATE scans SET seconds_spent=?,status='CANCELLED',updated_at=? WHERE scan_id=?",
                   (spent_seconds, now, scan_id))
        harness.event(db, "SCAN_CANCELLED", {"scan_id": scan_id, "actor": actor, "reason": reason})
    return {"scan_id": scan_id, "status": "CANCELLED", "replayed": False}


def extend_scan_budget(db, scan_id, event, hard_limits=None, now=None):
    """Append an idempotent budget extension; never resets spend or frontier."""
    now = time.time() if now is None else float(now)
    required = ("event_id", "actor", "reason", "authorization_scope", "expected_revision",
                "new_claims_limit", "new_seconds_limit")
    if any(not event.get(k) and k != "expected_revision" for k in required):
        raise ValueError("budget event is incomplete")
    with harness.transaction(db):
        scan = db.execute("SELECT * FROM scans WHERE scan_id=?", (scan_id,)).fetchone()
        if not scan:
            raise ValueError("unknown scan")
        payload = dict(event, scan_id=scan_id)
        digest = hashlib.sha256(_json(payload).encode()).hexdigest()
        old = db.execute("SELECT event_sha256 FROM scan_budget_events WHERE scan_id=? AND event_id=?",
                         (scan_id, event["event_id"])).fetchone()
        if old:
            if old[0] != digest:
                raise ValueError("budget event replay has different content")
            return {"scan_id": scan_id, "status": scan["status"], "replayed": True}
        if event["expected_revision"] != scan["budget_revision"]:
            raise ValueError("stale budget revision")
        claims = _positive_int(event["new_claims_limit"], "new_claims_limit", True)
        seconds = _finite(event["new_seconds_limit"], "new_seconds_limit", True)
        if claims < scan["claims_limit"] or seconds < scan["seconds_limit"]:
            raise ValueError("budget extension cannot reduce limits")
        if claims == scan["claims_limit"] and seconds == scan["seconds_limit"]:
            raise ValueError("budget extension must increase at least one limit")
        if claims < scan["claims_spent"] or seconds < scan["seconds_spent"]:
            raise ValueError("budget limit is below spend")
        if hard_limits is not None and (claims > hard_limits["claims"] or seconds > hard_limits["seconds"]):
            raise ValueError("budget extension exceeds hard limit")
        before = {"claims": scan["claims_limit"], "seconds": scan["seconds_limit"]}
        spent = {"claims": scan["claims_spent"], "seconds": scan["seconds_spent"]}
        db.execute("""INSERT INTO scan_budget_events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                   (scan_id, event["event_id"], digest, scan["budget_revision"], scan["budget_revision"] + 1,
                    _json(before), _json({"claims": claims, "seconds": seconds}), _json(spent),
                    event["authorization_scope"], event["actor"], event["reason"], now))
        db.execute("""UPDATE scans SET claims_limit=?,seconds_limit=?,budget_revision=budget_revision+1,
                    status=CASE WHEN status='PAUSED_BUDGET' THEN 'READY' ELSE status END,updated_at=?
                    WHERE scan_id=?""", (claims, seconds, now, scan_id))
        harness.event(db, "SCAN_BUDGET_EXTENDED", {"scan_id": scan_id, "event_id": event["event_id"],
                                                     "event_sha256": digest, "revision": scan["budget_revision"] + 1})
    return {"scan_id": scan_id, "status": "READY", "replayed": False,
            "budget_revision": scan["budget_revision"] + 1}


def register_proposal_v23(db, proposal_key, manifest_sha256, collector, parent_release_id,
                          parent_fact_epoch, parent_data_sha256, delta_sha256):
    proposal_key = _text(proposal_key, "proposal_key")
    collector = _text(collector, "collector")
    parent_release_id = _text(parent_release_id, "parent_release_id")
    parent_fact_epoch = _text(parent_fact_epoch, "parent_fact_epoch")
    manifest_sha256 = _sha256(manifest_sha256, "manifest_sha256")
    parent_data_sha256 = _sha256(parent_data_sha256, "parent_data_sha256")
    delta_sha256 = _sha256(delta_sha256, "delta_sha256")
    with harness.transaction(db):
        existing_proposal = db.execute("SELECT * FROM proposals WHERE proposal_key=?", (proposal_key,)).fetchone()
        if existing_proposal and (existing_proposal["manifest_sha256"], existing_proposal["collector"]) != (manifest_sha256, collector):
            raise ValueError("proposal key is frozen to different inputs or collector")
        db.execute("INSERT OR IGNORE INTO proposals(proposal_key,manifest_sha256,collector) VALUES(?,?,?)",
                   (proposal_key, manifest_sha256, collector))
        existing = db.execute("SELECT * FROM proposal_lineage WHERE proposal_key=?", (proposal_key,)).fetchone()
        if existing:
            expected = (existing["parent_release_id"], existing["parent_fact_epoch"],
                        existing["parent_data_sha256"], existing["delta_sha256"])
            actual = (parent_release_id, parent_fact_epoch, parent_data_sha256, delta_sha256)
            if expected != actual:
                raise ValueError("proposal parent or delta is frozen")
        else:
            db.execute("""INSERT INTO proposal_lineage(proposal_key,parent_release_id,parent_fact_epoch,
                        parent_data_sha256,delta_sha256,merge_status)
                        VALUES(?,?,?,?,?,'UNMERGED')""",
                       (proposal_key, parent_release_id, parent_fact_epoch, parent_data_sha256, delta_sha256))
    return {"proposal_key": proposal_key, "status": "UNMERGED"}


def append_review(db, proposal_key, manifest_sha256, reviewer, decision, basis, now=None):
    reviewer = _text(reviewer, "reviewer")
    basis = _text(basis, "basis")
    manifest_sha256 = _sha256(manifest_sha256, "manifest_sha256")
    if decision not in ("PASS", "HOLD", "REJECT"):
        raise ValueError("review requires independent reviewer, decision and basis")
    now = time.time() if now is None else float(now)
    review_id = hashlib.sha256(_json([proposal_key, manifest_sha256, reviewer, decision, basis]).encode()).hexdigest()
    with harness.transaction(db):
        proposal = db.execute("SELECT collector FROM proposals WHERE proposal_key=? AND manifest_sha256=?",
                              (proposal_key, manifest_sha256)).fetchone()
        if not proposal or proposal[0] == reviewer:
            raise ValueError("review is not independent or manifest does not match")
        existing = db.execute("SELECT review_id,decision,basis FROM review_history WHERE proposal_key=? AND manifest_sha256=? AND reviewer=?",
                              (proposal_key, manifest_sha256, reviewer)).fetchone()
        if existing:
            if (existing["decision"], existing["basis"]) == (decision, basis):
                return {"review_id": existing["review_id"], "decision": decision, "replayed": True}
            raise ValueError("reviewer already decided this frozen manifest; revise the proposal")
        db.execute("INSERT INTO review_history VALUES(?,?,?,?,?,?,?)",
                   (review_id, proposal_key, manifest_sha256, reviewer, decision, basis, now))
    return {"review_id": review_id, "decision": decision, "replayed": False}


def commit_proposal(db, proposal_key, manifest_sha256, current_release_id, current_fact_epoch,
                    current_data_sha256, merger, receipt, apply_delta, now=None):
    """Apply an already-reviewed delta and its receipt in one SQLite transaction."""
    merger = _text(merger, "merger")
    manifest_sha256 = _sha256(manifest_sha256, "manifest_sha256")
    current_data_sha256 = _sha256(current_data_sha256, "current_data_sha256")
    if not isinstance(receipt, dict):
        raise ValueError("merge receipt is incomplete")
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        row = db.execute("""SELECT p.collector,l.* FROM proposals p JOIN proposal_lineage l
                           ON l.proposal_key=p.proposal_key
                           WHERE p.proposal_key=? AND p.manifest_sha256=?""",
                         (proposal_key, manifest_sha256)).fetchone()
        if not row:
            raise ValueError("unknown proposal or manifest mismatch")
        if row["merge_status"] != "UNMERGED":
            raise ValueError("proposal has already been merged or closed")
        if (row["parent_release_id"], row["parent_fact_epoch"], row["parent_data_sha256"]) != (current_release_id, current_fact_epoch, current_data_sha256):
            raise ValueError("proposal parent is stale; rebase required")
        reviews = list(db.execute("SELECT reviewer,decision FROM review_history WHERE proposal_key=? AND manifest_sha256=?",
                                  (proposal_key, manifest_sha256)))
        if not reviews or any(r["decision"] != "PASS" for r in reviews):
            raise ValueError("all appended independent reviews must PASS; revise proposal after HOLD/REJECT")
        if len({r["reviewer"] for r in reviews}) != len(reviews):
            raise ValueError("duplicate reviewer history is invalid")
        if merger == row["collector"] or merger in {r["reviewer"] for r in reviews}:
            raise ValueError("merger must be independent from collector and reviewers")
        required_receipt = {
            "manifest_sha256": manifest_sha256,
            "delta_sha256": row["delta_sha256"],
            "parent_release_id": row["parent_release_id"],
            "parent_fact_epoch": row["parent_fact_epoch"],
            "parent_data_sha256": row["parent_data_sha256"],
        }
        if any(receipt.get(key) != value for key, value in required_receipt.items()):
            raise ValueError("merge receipt does not bind the reviewed manifest, delta and parent")
        if not callable(apply_delta):
            raise ValueError("apply_delta callback is required for an atomic merge")
        before_sha256 = current_data_sha256
        after_sha256 = apply_delta(db)
        after_sha256 = _sha256(after_sha256, "apply_delta result")
        if receipt.get("before_sha256") != current_data_sha256 or receipt.get("after_sha256") != after_sha256:
            raise ValueError("merge receipt before/after hashes differ from applied delta")
        db.execute("""UPDATE proposal_lineage SET merge_status='MERGED',before_sha256=?,after_sha256=?,
                    merged_by=?,merged_at=?,receipt_json=? WHERE proposal_key=?""",
                   (before_sha256, after_sha256, merger, now, _json(receipt), proposal_key))
        harness.event(db, "PROPOSAL_MERGED", {"proposal_key": proposal_key, "after_sha256": after_sha256,
                                               "merger": merger})
    return {"proposal_key": proposal_key, "status": "MERGED", "after_sha256": after_sha256}


def register_release_views(db, release_id, input_sha256, views, now=None):
    required = {"overview", "material_tree", "evidence_matrix"}
    if set(views) != required:
        raise ValueError("exactly three canonical views are required")
    release_id = _text(release_id, "release_id")
    input_sha256 = _sha256(input_sha256, "input_sha256")
    for output_sha256 in views.values():
        _sha256(output_sha256, "output_sha256")
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        for name, output_sha256 in views.items():
            existing = db.execute("SELECT * FROM release_views WHERE release_id=? AND view_name=?",
                                  (release_id, name)).fetchone()
            expected = (input_sha256, output_sha256)
            if existing:
                if (existing["input_sha256"], existing["output_sha256"]) != expected:
                    raise ValueError("release view is already frozen to different inputs or output")
                if existing["status"] == "FAILED":
                    raise ValueError("failed release view is terminal; build a new release")
                continue
            db.execute("INSERT INTO release_views VALUES(?,?,?,?,?,?)",
                       (release_id, name, input_sha256, output_sha256, "BUILT", now))
    return {"release_id": release_id, "views": sorted(required), "status": "BUILT"}


def verify_release_views(db, release_id, input_sha256, output_sha256s, now=None):
    required = {"overview", "material_tree", "evidence_matrix"}
    if set(output_sha256s) != required:
        raise ValueError("all three verified output SHA256 values are required")
    release_id = _text(release_id, "release_id")
    input_sha256 = _sha256(input_sha256, "input_sha256")
    for output_sha256 in output_sha256s.values():
        _sha256(output_sha256, "output_sha256")
    now = time.time() if now is None else float(now)
    with harness.transaction(db):
        rows = list(db.execute("SELECT * FROM release_views WHERE release_id=? ORDER BY view_name", (release_id,)))
        if {r["view_name"] for r in rows} != required:
            raise ValueError("release has incomplete view build set")
        if any(r["input_sha256"] != input_sha256 for r in rows):
            raise ValueError("view input snapshot mismatch")
        for row in rows:
            if row["output_sha256"] != output_sha256s[row["view_name"]]:
                raise ValueError("verified output differs from built output")
            if row["status"] == "BUILT":
                db.execute("UPDATE release_views SET status='VERIFIED',created_at=? WHERE release_id=? AND view_name=?",
                           (now, release_id, row["view_name"]))
            elif row["status"] != "VERIFIED":
                raise ValueError("release view is not in a verifiable state")
    return {"release_id": release_id, "status": "VERIFIED", "views": sorted(required)}
