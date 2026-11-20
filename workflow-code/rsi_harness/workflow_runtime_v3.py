"""Durable file handoffs and reviewed, atomic RSI candidate transactions.

This database belongs to one isolated run. It never writes legacy project tables.
Model dispatch is performed by the host; this module verifies its recorded handoff.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import secrets
import sqlite3
import time


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def file_sha(path):
    with Path(path).open("rb") as handle:
        result = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            result.update(block)
        return result.hexdigest()


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Missing " + field)
    return value


def safe_id(value):
    text(value, "identifier")
    if any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in value):
        raise ValueError("Unsafe identifier")
    return value


SCHEMA = """
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE tasks (
 id TEXT PRIMARY KEY, step TEXT NOT NULL, route TEXT NOT NULL,
 collector TEXT NOT NULL, input_sha TEXT NOT NULL, records TEXT NOT NULL,
 parent_id TEXT NOT NULL,
 status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,
 token TEXT, owner TEXT, lease_until REAL, started REAL, spent REAL NOT NULL DEFAULT 0,
 dispatch TEXT, review TEXT, candidate TEXT, error TEXT, cooldown_until REAL NOT NULL DEFAULT 0
);
CREATE TABLE events (seq INTEGER PRIMARY KEY, at REAL NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL);
CREATE TABLE releases (id TEXT PRIMARY KEY, parent_id TEXT, bundle TEXT NOT NULL, sha TEXT NOT NULL, transaction_key TEXT UNIQUE);
CREATE TABLE steps (id TEXT PRIMARY KEY, output TEXT NOT NULL, sha TEXT NOT NULL);
CREATE TABLE dispatch_calls (host_call_id TEXT PRIMARY KEY, task_id TEXT NOT NULL, attempt INTEGER NOT NULL);
CREATE TABLE frontier (kind TEXT NOT NULL, material_id TEXT NOT NULL, revision TEXT NOT NULL, rank INTEGER NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(kind,material_id,revision));
"""


class Run:
    def __init__(self, directory):
        self.directory = Path(directory).resolve()
        self.db = sqlite3.connect(self.directory / "run.sqlite", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self._indices = {}

    def _packet_indices(self):
        indexes = []
        for pin in self.meta("inputs"):
            path = Path(pin["path"])
            if path.suffix != ".json":
                continue
            if pin["sha256"] not in self._indices:
                value = json.loads(path.read_text(encoding="utf-8"))
                self._indices[pin["sha256"]] = value if isinstance(value, dict) and value.get("schema") == "rsi-site-review-packet-index-v3" else None
            value = self._indices[pin["sha256"]]
            if value is not None:
                indexes.append((pin, value))
        return indexes

    def close(self):
        self.db.close()

    def meta(self, key):
        row = self.db.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        if row is None:
            raise ValueError("Missing run metadata: " + key)
        return json.loads(row[0])

    def set_meta(self, key, value):
        self.db.execute("INSERT INTO meta VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, encoded(value)))

    def event(self, kind, payload, now=None):
        self.db.execute("INSERT INTO events(at,kind,payload) VALUES (?,?,?)", (time.time() if now is None else now, kind, encoded(payload)))

    def verify_inputs(self):
        pins = self.meta("inputs")
        for pin in pins:
            path = Path(pin["path"])
            if not path.is_file() or file_sha(path) != pin["sha256"]:
                raise ValueError("Frozen input changed: " + pin["name"])
        return {"status": "PASS", "input_count": len(pins), "input_sha256": self.meta("input_sha256")}

    def verify_path(self, requested):
        """Resolve an explicit frozen file or a packet in a pinned export index."""
        path = Path(requested).resolve()
        self.verify_inputs()
        for pin in self.meta("inputs"):
            frozen = Path(pin["path"])
            if path == frozen and file_sha(path) == pin["sha256"]:
                return pin
        for pin, index in self._packet_indices():
            frozen = Path(pin["path"])
            declared = {row["path"]: row["sha256"] for row in index["packets"]}
            declared.update(index["private_inputs"])
            for name, sha in declared.items():
                candidate = (frozen.parent / name).resolve()
                if not candidate.is_relative_to(frozen.parent):
                    raise ValueError("Declared packet path escapes export root")
                if candidate == path:
                    if not path.is_file() or file_sha(path) != sha:
                        raise ValueError("Declared source/packet SHA mismatch")
                    return {"path": str(path), "sha256": sha, "index_sha256": pin["sha256"]}
        raise ValueError("File is not declared in frozen run inputs")

    def verify_record_sources(self, records):
        verified = {}
        catalog = {}
        for pin, index in self._packet_indices():
            for name, sha in index["private_inputs"].items():
                path = (Path(pin["path"]).parent / name).resolve()
                if not path.is_relative_to(Path(pin["path"]).parent):
                    raise ValueError("Source path escapes export root")
                catalog.setdefault(name, []).append({"path": str(path), "sha256": sha, "index_sha256": pin["sha256"]})
        for record in records:
            for locator in record.get("input_locators", []):
                name = locator.split("#", 1)[0]
                if Path(name).is_absolute() or ".." in Path(name).parts:
                    raise ValueError("Invalid packet source locator")
                matches = catalog.get(name, [])
                if len(matches) != 1:
                    raise ValueError("Packet source locator needs exactly one frozen index")
                pin = matches[0]
                path = pin["path"]
                if path not in verified:
                    if file_sha(path) != pin["sha256"]:
                        raise ValueError("Packet source SHA mismatch")
                    verified[path] = pin
        return list(verified.values())

    def record_step(self, step, result):
        self.verify_inputs()
        value = encoded(result)
        with self.db:
            row = self.db.execute("SELECT sha FROM steps WHERE id=?", (step,)).fetchone()
            sha = digest(result)
            if row and row[0] != sha:
                raise ValueError("Step output differs; start a new run or use an explicit new step ID")
            self.db.execute("INSERT OR IGNORE INTO steps VALUES (?,?,?)", (step, value, sha))
            self.event("STEP_RESULT", {"step": step, "sha256": sha})
        return result

    def enqueue(self, step, records, collector, batch_size=100, route="bulk_review"):
        self.verify_inputs()
        self.verify_record_sources(records)
        text(collector, "collector")
        if type(batch_size) is not int or not 50 <= batch_size <= 200:
            raise ValueError("Batch size must be 50–200")
        config = self.meta("workflow")
        spec = next((s for s in config["steps"] if s["id"] == step), None)
        if spec is None or spec["route"] != route or route == "code":
            raise ValueError("Step/route mismatch")
        ids = [text(r.get("record_id"), "record_id") for r in records]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate task records")
        for record in records:
            text(record.get("source_locator"), "source_locator")
        tasks = []
        with self.db:
            for offset in range(0, len(records), batch_size):
                batch = records[offset:offset + batch_size]
                payload_sha = digest(batch)
                parent = self.meta("current_release")
                task_id = digest([self.meta("input_sha256"), parent, step, payload_sha, collector, route])[:24]
                self.db.execute("INSERT OR IGNORE INTO tasks(id,step,route,collector,input_sha,records,parent_id,status) VALUES (?,?,?,?,?,?,?,?)",
                                (task_id, step, route, collector, payload_sha, encoded(batch), parent, "READY"))
                tasks.append({"task_id": task_id, "records": len(batch), "tail_batch": len(batch) < 50})
            self.event("ENQUEUE", {"step": step, "tasks": tasks})
        return tasks

    def claim(self, owner, now=None):
        self.verify_inputs()
        text(owner, "owner")
        now = time.time() if now is None else now
        self.db.execute("BEGIN IMMEDIATE")
        try:
            budget = self.meta("max_task_attempts")
            used = self.db.execute("SELECT COALESCE(SUM(attempts),0) FROM tasks").fetchone()[0]
            spent = self.db.execute("SELECT COALESCE(SUM(spent),0) FROM tasks").fetchone()[0]
            reserved = self.db.execute("SELECT COALESCE(SUM(lease_until-started),0) FROM tasks WHERE status='LEASED'").fetchone()[0]
            remaining = self.meta("max_seconds") - spent - reserved
            if used >= budget or remaining <= 0:
                raise ValueError("Run budget exhausted")
            # One active host handoff per owner. Expiry requires explicit recovery.
            if self.db.execute("SELECT 1 FROM tasks WHERE owner=? AND status='LEASED'", (owner,)).fetchone():
                raise ValueError("Owner already has an active task")
            row = self.db.execute("SELECT * FROM tasks WHERE status IN ('READY','RETRY') AND attempts<3 AND cooldown_until<=? AND collector<>? AND parent_id=? ORDER BY rowid LIMIT 1", (now, owner, self.meta("current_release"))).fetchone()
            if row is None:
                self.db.rollback()
                return None
            token = secrets.token_hex(24)
            self.db.execute("UPDATE tasks SET status='LEASED',attempts=attempts+1,owner=?,token=?,started=?,lease_until=?,dispatch=NULL,review=NULL WHERE id=?",
                            (owner, token, now, now + min(900, remaining), row["id"]))
            self.event("CLAIM", {"task_id": row["id"], "owner": owner, "attempt": row["attempts"] + 1}, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return self.handoff(row["id"], token, now)

    def _leased(self, task_id, token, now=None):
        now = time.time() if now is None else now
        row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None or row["status"] != "LEASED" or not secrets.compare_digest(row["token"] or "", token or ""):
            raise ValueError("Invalid task lease")
        if now < row["started"] or now >= row["lease_until"]:
            raise ValueError("Task lease expired")
        if row["parent_id"] != self.meta("current_release"):
            raise ValueError("Task parent release is stale")
        return row

    def handoff(self, task_id, token, now=None):
        self.verify_inputs()
        row = self._leased(task_id, token, now)
        source_files = self.verify_record_sources(json.loads(row["records"]))
        routes = {r["id"]: r for r in self.meta("workflow")["modelRoutes"]}
        model = routes[row["route"]]
        collecting = row["step"] in {"F3-components", "F4-labels", "F5-normalize", "F6-search", "F6-extract"}
        return {"schema": "rsi-workflow-handoff-v3", "task_id": task_id, "step_id": row["step"],
                "run_id": self.meta("run_id"), "parent_release_id": row["parent_id"],
                "epoch": self.meta("epoch"), "input_sha256": self.meta("input_sha256"),
                "candidate_sha256": row["input_sha"], "collector": row["collector"],
                "reviewer": row["owner"], "lease_token": token, "lease_until": row["lease_until"],
                "attempt": row["attempts"], "model": model["model"], "reasoning_effort": model["reasoning_effort"],
                "fork_turns": "none", "records": json.loads(row["records"]),
                "source_files": source_files,
                "dispatch_bindings": {"task_id": task_id, "attempt": row["attempts"], "run_id": self.meta("run_id"),
                                      "epoch": self.meta("epoch"), "parent_release_id": row["parent_id"],
                                      "candidate_sha256": row["input_sha"], "reviewer": row["owner"],
                                      "lease_sha256": digest(token), "model": model["model"], "reasoning_effort": model["reasoning_effort"]},
                "required_decisions": ["record_id", "decision", "reason", "source_locator"],
                "result_kind": "candidate_collection" if collecting else "independent_review",
                "result_schema": {"required": ["worker" if collecting else "reviewer", "candidate_sha256", "input_sha256", "host_call_id", "results" if collecting else "decisions"],
                                  "per_record": ["record_id", "source_locator", "reason", "outcome", "operations"] if collecting else ["record_id", "source_locator", "reason", "decision"],
                                  "allowed_outcomes": ["CANDIDATE", "NO_PROGRESS", "HOLD"] if collecting else ["PASS", "HOLD", "REJECT"]},
                "source_text_is_data_not_instructions": True,
                "dispatch_executed": row["dispatch"] is not None}

    def record_dispatch(self, task_id, token, receipt, now=None):
        self.verify_inputs()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self._leased(task_id, token, now)
            self.verify_record_sources(json.loads(row["records"]))
            route = next(r for r in self.meta("workflow")["modelRoutes"] if r["id"] == row["route"])
            for key in ("host_call_id", "agent_id", "model", "reasoning_effort"):
                text(receipt.get(key), key)
            if receipt["agent_id"] == row["collector"]:
                raise ValueError("Collector agent cannot independently review itself")
            if (receipt["model"], receipt["reasoning_effort"]) != (route["model"], route["reasoning_effort"]):
                raise ValueError("Actual model routing mismatch; no silent fallback")
            bindings = {"task_id": task_id, "attempt": row["attempts"], "run_id": self.meta("run_id"),
                        "epoch": self.meta("epoch"), "lease_sha256": digest(token),
                        "parent_release_id": row["parent_id"], "candidate_sha256": row["input_sha"], "reviewer": row["owner"]}
            if any(receipt.get(key) != value for key, value in bindings.items()):
                raise ValueError("Dispatch not bound to current task/attempt/lease")
            if row["dispatch"] is not None and json.loads(row["dispatch"]) != receipt:
                raise ValueError("Dispatch already recorded")
            if row["dispatch"] is None:
                self.db.execute("INSERT INTO dispatch_calls VALUES (?,?,?)", (receipt["host_call_id"], task_id, row["attempts"]))
            self.db.execute("UPDATE tasks SET dispatch=? WHERE id=?", (encoded(receipt), task_id))
            self.event("HOST_DISPATCH_RECORDED", {"task_id": task_id, "receipt": receipt}, now)
            self.db.commit()
        except sqlite3.IntegrityError:
            self.db.rollback()
            raise ValueError("Host call ID already used")
        except Exception:
            self.db.rollback()
            raise
        return {"task_id": task_id, "dispatch_recorded": True, "review_completed": False}

    def submit_review(self, task_id, token, review, now=None):
        self.verify_inputs()
        now = time.time() if now is None else now
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self._leased(task_id, token, now)
            self.verify_record_sources(json.loads(row["records"]))
            if row["step"] in {"F3-components", "F4-labels", "F5-normalize", "F6-search", "F6-extract"}:
                raise ValueError("Collector result requires submit_candidate and independent review")
            if row["dispatch"] is None:
                raise ValueError("Missing actual host dispatch receipt")
            if review.get("candidate_sha256") != row["input_sha"] or review.get("input_sha256") != self.meta("input_sha256"):
                raise ValueError("Review input SHA mismatch")
            if review.get("reviewer") != row["owner"] or review.get("reviewer") == row["collector"]:
                raise ValueError("Independent reviewer required")
            dispatch = json.loads(row["dispatch"])
            if review.get("host_call_id") != dispatch["host_call_id"]:
                raise ValueError("Review call does not match dispatch")
            expected = {r["record_id"] for r in json.loads(row["records"])}
            locators = {r["record_id"]: {r["source_locator"], *r.get("allowed_source_locators", [])} for r in json.loads(row["records"])}
            decisions = review.get("decisions", [])
            actual = [d.get("record_id") for d in decisions]
            if set(actual) != expected or len(actual) != len(expected):
                raise ValueError("Review must cover every assigned record exactly once")
            for decision in decisions:
                if decision.get("decision") not in {"PASS", "HOLD", "REJECT"}:
                    raise ValueError("Unknown review decision")
                text(decision.get("reason"), "review reason")
                text(decision.get("source_locator"), "review source locator")
                if decision["source_locator"] not in locators[decision["record_id"]]:
                    raise ValueError("Review locator is outside frozen record sources")
            self.db.execute("UPDATE tasks SET status='REVIEWED',review=?,spent=spent+?,token=NULL,lease_until=NULL WHERE id=?", (encoded(review), now - row["started"], task_id))
            self.event("REVIEW_SUBMITTED", {"task_id": task_id, "review_sha256": digest(review)}, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"task_id": task_id, "status": "REVIEWED", "decisions": len(decisions), "merged": False}

    def submit_candidate(self, task_id, token, candidate, now=None):
        """Preserve model-collected results without giving them scientific approval."""
        self.verify_inputs()
        now = time.time() if now is None else now
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self._leased(task_id, token, now)
            self.verify_record_sources(json.loads(row["records"]))
            if row["step"] not in {"F3-components", "F4-labels", "F5-normalize", "F6-search", "F6-extract"} or row["dispatch"] is None:
                raise ValueError("Candidate collection requires an actual collector dispatch")
            dispatch = json.loads(row["dispatch"])
            required = {"candidate_sha256": row["input_sha"], "input_sha256": self.meta("input_sha256"),
                        "host_call_id": dispatch["host_call_id"], "worker": row["owner"]}
            if any(candidate.get(key) != value for key, value in required.items()):
                raise ValueError("Candidate result binding mismatch")
            inputs = {r["record_id"]: r for r in json.loads(row["records"])}
            results = candidate.get("results", [])
            if len(results) != len(inputs) or {r.get("record_id") for r in results} != set(inputs):
                raise ValueError("Candidate must report every input exactly once")
            for result in results:
                original = inputs[result["record_id"]]
                if result.get("source_locator") not in {original["source_locator"], *original.get("allowed_source_locators", [])}:
                    raise ValueError("Candidate source is not in frozen inputs")
                if result.get("outcome") not in {"CANDIDATE", "NO_PROGRESS", "HOLD"}:
                    raise ValueError("Collector cannot issue an approved decision")
                text(result.get("reason"), "candidate reason")
                if not isinstance(result.get("operations", []), list):
                    raise ValueError("Candidate operations must be a list")
            self.db.execute("UPDATE tasks SET status='CANDIDATE_READY',candidate=?,spent=spent+?,token=NULL,lease_until=NULL WHERE id=?", (encoded(candidate), now - row["started"], task_id))
            self.event("CANDIDATE_SUBMITTED", {"task_id": task_id, "sha256": digest(candidate), "approved": False}, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"task_id": task_id, "status": "CANDIDATE_READY", "approved": False}

    def enqueue_review(self, candidate_task_id, review_step):
        row = self.db.execute("SELECT * FROM tasks WHERE id=?", (candidate_task_id,)).fetchone()
        if row is None or row["status"] != "CANDIDATE_READY" or row["parent_id"] != self.meta("current_release"):
            raise ValueError("Current candidate result required")
        routes = {"F3-components": {"F4-review"}, "F4-labels": {"F4-review"}, "F5-normalize": {"F5-review"},
                  "F6-search": {"F6-review"}, "F6-extract": {"F6-review"}}
        if review_step not in routes[row["step"]]:
            raise ValueError("Wrong independent review stage")
        spec = next(s for s in self.meta("workflow")["steps"] if s["id"] == review_step)
        original = {r["record_id"]: r for r in json.loads(row["records"])}
        results = json.loads(row["candidate"])["results"]
        records = [dict(original[r["record_id"]], operations=r.get("operations", []), collector_result=r,
                        producer_task_id=candidate_task_id, producer_result_sha256=digest(json.loads(row["candidate"]))) for r in results if r["outcome"] == "CANDIDATE"]
        dispatch = json.loads(row["dispatch"])
        return self.enqueue(review_step, records, dispatch["agent_id"], route=spec["route"])

    def recover(self, task_id, reason, *, actor, now=None):
        text(reason, "recovery reason")
        text(actor, "recovery actor")
        now = time.time() if now is None else now
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
            if row is None or row["status"] != "LEASED" or now < row["lease_until"]:
                raise ValueError("Only expired leases may be recovered")
            state = "RETRY" if row["attempts"] < 3 else "COOLDOWN"
            self.db.execute("UPDATE tasks SET status=?,token=NULL,lease_until=NULL,spent=spent+?,error=?,cooldown_until=? WHERE id=?",
                            (state, max(0, row["lease_until"] - row["started"]), reason, now + (3600 if state == "COOLDOWN" else 0), task_id))
            self.event("EXPLICIT_RECOVERY", {"task_id": task_id, "actor": actor, "reason": reason, "status": state}, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"task_id": task_id, "status": state, "attempts_preserved": row["attempts"]}

    def finish_failure(self, task_id, token, outcome, reason, now=None):
        self.verify_inputs()
        text(reason, "failure reason")
        if outcome not in {"RETRY", "NO_PROGRESS", "REJECTED"}:
            raise ValueError("Unknown task failure outcome")
        now = time.time() if now is None else now
        self.db.execute("BEGIN IMMEDIATE")
        try:
            row = self._leased(task_id, token, now)
            status = "RETRY" if outcome == "RETRY" and row["attempts"] < 3 else "COOLDOWN"
            self.db.execute("UPDATE tasks SET status=?,spent=spent+?,token=NULL,lease_until=NULL,error=?,cooldown_until=? WHERE id=?",
                            (status, now - row["started"], reason, now + (3600 if status == "COOLDOWN" else 0), task_id))
            self.event("TASK_FAILURE", {"task_id": task_id, "outcome": outcome, "reason": reason}, now)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"task_id": task_id, "status": status, "scientific_decision_created": False}

    def bundle(self, release_id=None):
        release_id = release_id or self.meta("current_release")
        row = self.db.execute("SELECT bundle FROM releases WHERE id=?", (release_id,)).fetchone()
        if row is None:
            raise ValueError("Unknown release")
        return json.loads(row[0])

    def merge(self, task_ids, *, actor, expected_parent):
        from workflow_data_v3 import validate_bundle
        self.verify_inputs()
        text(actor, "merge actor")
        if not task_ids or len(task_ids) != len(set(task_ids)):
            raise ValueError("Unique task IDs required")
        transaction_key = digest([expected_parent, sorted(task_ids)])
        self.db.execute("BEGIN IMMEDIATE")
        try:
            previous = self.db.execute("SELECT id,sha FROM releases WHERE transaction_key=?", (transaction_key,)).fetchone()
            if previous:
                self.db.commit()
                return {"release_id": previous["id"], "sha256": previous["sha"], "idempotent": True}
            if self.meta("current_release") != expected_parent:
                raise ValueError("Parent release changed")
            bundle = self.bundle(expected_parent)
            keys = {"objects": "object_id", "components": "component_id", "materials": "material_id", "relations": "relation_id", "taxonomy": "edge_id", "evidence": "record_id"}
            applied = 0
            for task_id in sorted(task_ids):
                row = self.db.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
                if row is None or row["status"] != "REVIEWED":
                    raise ValueError("Task lacks completed review")
                self.verify_record_sources(json.loads(row["records"]))
                if row["parent_id"] != expected_parent:
                    raise ValueError("Task was reviewed against a different parent release")
                if actor in {row["collector"], row["owner"], json.loads(row["dispatch"])["agent_id"]}:
                    raise ValueError("Merger must be independent of collector and reviewer")
                review = json.loads(row["review"])
                decisions = {d["record_id"]: d for d in review["decisions"]}
                for record in json.loads(row["records"]):
                    decision = decisions[record["record_id"]]
                    if decision["decision"] != "PASS":
                        continue
                    # Read-only audits carry no delta. Accepted source data are
                    # changed only by explicit, reviewed exact-preimage operations.
                    for operation in record.get("operations", []):
                        table = operation["table"]
                        if table not in keys:
                            raise ValueError("Unknown delta table")
                        key = keys[table]
                        identity = operation["id"]
                        index = {r[key]: r for r in bundle[table]}
                        old = index.get(identity)
                        if operation.get("before_sha256") != (digest(old) if old is not None else None):
                            raise ValueError("Delta preimage mismatch")
                        if operation["action"] == "delete":
                            if old is None:
                                raise ValueError("Cannot withdraw absent record")
                            bundle[table] = [r for r in bundle[table] if r[key] != identity]
                        elif operation["action"] == "upsert":
                            value = dict(operation["value"])
                            if value.get(key) != identity:
                                raise ValueError("Delta identity mismatch")
                            value.update(collector=row["collector"], reviewer=json.loads(row["dispatch"])["agent_id"],
                                         decision="PASS", review_input_sha256=row["input_sha"], review_reason=decision["reason"])
                            bundle[table] = [r for r in bundle[table] if r[key] != identity] + [value]
                        else:
                            raise ValueError("Unknown delta action")
                        applied += 1
            validate_bundle(bundle)
            sha = digest(bundle)
            release_id = "RSI-V3-" + digest([expected_parent, transaction_key, sha])[:20]
            self.db.execute("INSERT INTO releases VALUES (?,?,?,?,?)", (release_id, expected_parent, encoded(bundle), sha, transaction_key))
            self.set_meta("current_release", release_id)
            for task_id in task_ids:
                self.db.execute("UPDATE tasks SET status='MERGED' WHERE id=?", (task_id,))
            now = time.time()
            for stale in self.db.execute("SELECT * FROM tasks WHERE parent_id=? AND status='LEASED'", (expected_parent,)).fetchall():
                self.db.execute("UPDATE tasks SET status='STALE',spent=spent+?,token=NULL,lease_until=NULL,error='parent advanced' WHERE id=?", (max(0, min(now, stale["lease_until"]) - stale["started"]), stale["id"]))
            self.db.execute("UPDATE tasks SET status='STALE',error='parent advanced; prior artifact retained' WHERE parent_id=? AND status IN ('READY','RETRY','REVIEWED','CANDIDATE_READY')", (expected_parent,))
            self.event("ATOMIC_MERGE", {"parent": expected_parent, "release_id": release_id, "operations": applied, "actor": actor})
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return {"release_id": release_id, "sha256": sha, "operations": applied, "idempotent": False, "published": False}

    def checkpoint(self):
        self.verify_inputs()
        rows = [dict(r) for r in self.db.execute("SELECT id,step,route,status,attempts,spent,error,cooldown_until FROM tasks ORDER BY rowid")]
        return {"run_id": self.meta("run_id"), "current_release": self.meta("current_release"), "input_sha256": self.meta("input_sha256"),
                "tasks": rows, "attempts_used": sum(r["attempts"] for r in rows), "seconds_spent": sum(r["spent"] for r in rows),
                "max_task_attempts": self.meta("max_task_attempts"), "max_seconds": self.meta("max_seconds"),
                "unresolved": [r["id"] for r in rows if r["status"] not in {"MERGED", "STALE"}],
                "stale_task_ids": [r["id"] for r in rows if r["status"] == "STALE"],
                "frontier": [dict(r) for r in self.db.execute("SELECT kind,material_id,revision,status,rank FROM frontier ORDER BY kind,rank")],
                "event_count": self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0]}

    def frontier(self, kind="material", limit=100, complete=()):
        from workflow_data_v3 import bfs_tasks, recompute
        self.verify_inputs()
        if type(limit) is not int or not 1 <= limit <= 200:
            raise ValueError("Frontier batch limit must be 1–200")
        candidates = bfs_tasks(self.bundle(), kind=kind, limit=max(1, len(self.bundle()["materials"])))
        states = {r["material_id"]: r for r in recompute(self.bundle())["material_states"]}
        with self.db:
            for rank, candidate in enumerate(candidates):
                revision = digest(states[candidate["material_id"]])
                self.db.execute("INSERT OR IGNORE INTO frontier VALUES (?,?,?,?,?,?)", (kind, candidate["material_id"], revision, rank, "READY", encoded(candidate)))
            for material_id, revision in complete:
                changed = self.db.execute("UPDATE frontier SET status='DONE' WHERE kind=? AND material_id=? AND revision=? AND status='READY'", (kind, material_id, revision)).rowcount
                if not changed:
                    raise ValueError("Unknown or completed frontier item")
            current = {(r["material_id"], digest(states[r["material_id"]])) for r in candidates}
            result = [dict(json.loads(r["payload"]), revision=r["revision"]) for r in self.db.execute("SELECT * FROM frontier WHERE kind=? AND status='READY' ORDER BY rank,material_id", (kind,)) if (r["material_id"], r["revision"]) in current][:limit]
            self.event("FRONTIER_CHECKPOINT", {"kind": kind, "completed": list(complete), "remaining": len(result)})
        return result


def freeze(directory, *, project_root, run_id, parent_release_id, inputs, workflow, bundle,
           max_task_attempts=100, max_seconds=3600):
    from workflow_data_v3 import validate_bundle
    from workflow_plan_v3 import validate_workflow, ROUTING
    validate_workflow(workflow, json.loads(ROUTING.read_text(encoding="utf-8")))
    validate_bundle(bundle)
    root = Path(project_root).resolve()
    out = Path(directory).resolve()
    safe_id(run_id)
    text(parent_release_id, "parent_release_id")
    if type(max_task_attempts) is not int or max_task_attempts <= 0 or not 0 < max_seconds <= 86400:
        raise ValueError("Positive bounded run budgets required")
    if out.exists():
        raise ValueError("Run directory already exists; resume explicitly")
    pins = []
    for name, raw in sorted(inputs.items()):
        path = Path(raw).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Input escapes project root or is missing")
        pins.append({"name": text(name, "input name"), "path": str(path), "sha256": file_sha(path)})
    if not pins:
        raise ValueError("Frozen inputs required")
    # Run directories must be separate from their own read-only inputs.
    if out == root or any(Path(pin["path"]).is_relative_to(out) for pin in pins):
        raise ValueError("Run directory contains an input")
    out.mkdir(parents=True)
    run = Run(out)
    try:
        run.db.executescript(SCHEMA)
        with run.db:
            for key, value in {"run_id": run_id, "inputs": pins, "input_sha256": digest(pins), "epoch": digest([pins, bundle]),
                               "workflow": workflow, "current_release": parent_release_id, "parent_release": parent_release_id,
                               "max_task_attempts": max_task_attempts, "max_seconds": max_seconds}.items():
                run.set_meta(key, value)
            run.db.execute("INSERT INTO releases VALUES (?,?,?,?,NULL)", (parent_release_id, None, encoded(bundle), digest(bundle)))
            run.event("INPUT_FREEZE", {"pins": pins, "parent_release_id": parent_release_id, "bundle_sha256": digest(bundle)})
        return run
    except Exception:
        run.close()
        raise
