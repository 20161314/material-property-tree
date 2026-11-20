#!/usr/bin/env python3
"""Deterministic shadow database, coverage and leased RSI work queues. Standard library only."""
import argparse
from collections import defaultdict, deque, Counter
from contextlib import contextmanager
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import sqlite3
import time
import uuid

HERE = Path(__file__).resolve().parent
PROPERTIES = ('E', 'nu', 'rho')


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest_file(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def connect(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path, timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=WAL')
    db.executescript((HERE / 'schema.sql').read_text())
    for table in ('nodes', 'edges', 'objects', 'object_aliases', 'components', 'material_links',
                  'documents', 'evidence_groups', 'observations', 'group_material_refs', 'obligations'):
        for operation in ('INSERT', 'UPDATE', 'DELETE'):
            trigger = 'revision_' + table + '_' + operation.lower()
            db.execute(f'CREATE TRIGGER IF NOT EXISTS {trigger} AFTER {operation} ON {table} BEGIN UPDATE fact_revision SET generation=generation+1 WHERE id=1; END')
    return db


@contextmanager
def transaction(db):
    db.execute('BEGIN IMMEDIATE')
    try:
        yield
        db.execute('COMMIT')
    except Exception:
        db.execute('ROLLBACK')
        raise


def meta(db, key, default=None):
    row = db.execute('SELECT value FROM meta WHERE key=?', (key,)).fetchone()
    return json.loads(row[0]) if row else default


def set_meta(db, key, value):
    db.execute('INSERT OR REPLACE INTO meta VALUES(?,?)', (key, encoded(value)))


def event(db, kind, value):
    db.execute('INSERT INTO events(created,kind,payload_json) VALUES(?,?,?)', (time.time(), kind, encoded(value)))


def topology(db):
    nodes = {r['id']: dict(r) for r in db.execute('SELECT * FROM nodes WHERE active=1')}
    children, indegree = defaultdict(set), dict.fromkeys(nodes, 0)
    all_edges = [dict(r) for r in db.execute("SELECT * FROM edges WHERE accepted=1 AND kind IN('IS_A','DISPLAY')")]
    # Check display-tree integrity separately; UI navigation cannot change
    # scientific BFS depth or turn a missing subtype relation into one.
    def check_cycles(candidates):
        graph, degree = defaultdict(set), dict.fromkeys(nodes, 0)
        for e in candidates:
            a, b = e['parent_id'], e['child_id']
            if a in nodes and b in nodes and b not in graph[a]:
                graph[a].add(b)
                degree[b] += 1
        queue = deque(k for k, v in degree.items() if not v)
        visited = 0
        while queue:
            a = queue.popleft()
            visited += 1
            for b in graph[a]:
                degree[b] -= 1
                if not degree[b]:
                    queue.append(b)
        if visited != len(nodes):
            raise ValueError('Classification/display cycle')
    check_cycles(all_edges)
    edges = [e for e in all_edges if e['kind'] == 'IS_A']
    for e in edges:
        if e['parent_id'] not in nodes or e['child_id'] not in nodes:
            continue
        a, b = e['parent_id'], e['child_id']
        if b not in children[a]:
            children[a].add(b)
            indegree[b] += 1
    roots = sorted(k for k, v in indegree.items() if not v)
    q, order, depth = deque(roots), [], dict.fromkeys(roots, 0)
    while q:
        a = q.popleft()
        order.append(a)
        for b in sorted(children[a]):
            depth[b] = min(depth.get(b, 10**9), depth[a] + 1)
            indegree[b] -= 1
            if not indegree[b]:
                q.append(b)
    if len(order) != len(nodes):
        raise ValueError('Classification cycle: ' + ','.join(k for k, v in indegree.items() if v)[:500])
    return nodes, edges, order, depth


def fact_epoch(db):
    policy = digest_file(HERE / 'SPEC.md')
    implementation = {p: digest_file(HERE / p) for p in ('harness.py', 'schema.sql', 'import_snapshot.py')}
    inputs_sha = hashlib.sha256(encoded(meta(db, 'inputs', {})).encode()).hexdigest()
    generation = db.execute('SELECT generation FROM fact_revision WHERE id=1').fetchone()[0]
    cache = meta(db, 'fact_fingerprint_cache', {})
    if cache.get('generation') == generation and cache.get('policy') == policy and cache.get('implementation') == implementation and cache.get('inputs_sha') == inputs_sha:
        return cache['epoch']
    h = hashlib.sha256((HERE / 'SPEC.md').read_bytes())
    h.update(encoded(implementation).encode())
    queries = [
        'SELECT * FROM nodes ORDER BY id',
        'SELECT * FROM edges ORDER BY parent_id,child_id,kind',
        'SELECT * FROM objects ORDER BY id',
        'SELECT * FROM object_aliases ORDER BY namespace,source_uid',
        'SELECT * FROM components ORDER BY object_id,id',
        'SELECT * FROM material_links ORDER BY id',
        'SELECT * FROM documents ORDER BY id',
        'SELECT * FROM evidence_groups ORDER BY id',
        'SELECT * FROM observations ORDER BY group_id,property',
        'SELECT * FROM group_material_refs ORDER BY group_id,material_id,relation',
        'SELECT * FROM obligations ORDER BY id',
    ]
    h.update(encoded(meta(db, 'inputs', {})).encode())
    for sql in queries:
        for row in db.execute(sql):
            h.update(encoded(list(row)).encode())
            h.update(b'\n')
    epoch = h.hexdigest()
    set_meta(db, 'fact_fingerprint_cache', {'generation': generation, 'policy': policy, 'implementation': implementation, 'inputs_sha': inputs_sha, 'epoch': epoch})
    return epoch


def recompute(db):
    """Rebuild derived states. No numerical observation or object assignment is created."""
    with transaction(db):
        fk = list(db.execute('PRAGMA foreign_key_check'))
        if fk:
            raise ValueError('Foreign key violation: ' + str(fk[:3]))
        alias_conflicts = list(db.execute("SELECT o.id,a.object_id,o.namespace,o.source_uid FROM objects o JOIN object_aliases a ON a.namespace=o.namespace AND a.source_uid=o.source_uid WHERE o.accepted=1 AND a.reviewed=1 AND a.object_id<>o.id"))
        if alias_conflicts:
            raise ValueError('Accepted object conflicts with reviewed alias; resolve before counting: ' + str([tuple(r) for r in alias_conflicts[:3]]))
        nodes, edges, order, depths = topology(db)
        direct_objects, direct_groups, reference_groups = defaultdict(set), defaultdict(set), defaultdict(set)
        for r in db.execute('SELECT l.material_id,l.object_id FROM material_links l JOIN objects o ON o.id=l.object_id WHERE l.accepted=1 AND o.accepted=1'):
            direct_objects[r[0]].add(r[1])
        groups = {r['id']: dict(r) for r in db.execute('SELECT g.*,d.lineage_key,d.lineage_verified FROM evidence_groups g JOIN documents d ON d.id=g.document_id WHERE g.accepted=1')}
        observations = defaultdict(dict)
        for r in db.execute('SELECT * FROM observations WHERE accepted=1'):
            if not math.isfinite(r['low']) or not math.isfinite(r['high']):
                raise ValueError('Non-finite observation: ' + r['group_id'])
            expected_unit = {'E': 'GPa', 'nu': '1', 'rho': 'kg/m3'}[r['property']]
            if r['unit'] != expected_unit:
                raise ValueError('Noncanonical unit: ' + r['group_id'] + ' ' + r['unit'])
            if r['property'] in ('E', 'rho') and r['low'] < 0:
                raise ValueError('Negative E/density requires source-specific review: ' + r['group_id'])
            if r['group_id'] in groups:
                observations[r['group_id']][r['property']] = dict(r)
        for r in db.execute('SELECT * FROM group_material_refs WHERE accepted=1'):
            if r['group_id'] in groups and r['relation'] != 'FAMILY_ONLY':
                reference_groups[r['material_id']].add(r['group_id'])
                if r['relation'] == 'DIRECT':
                    direct_groups[r['material_id']].add(r['group_id'])
        effective_objects = {k: set(direct_objects[k]) for k in nodes}
        effective_groups = {k: set(reference_groups[k]) for k in nodes}
        outgoing = defaultdict(list)
        for edge in edges:
            if edge['kind'] == 'IS_A' and edge['parent_id'] in nodes and edge['child_id'] in nodes:
                outgoing[edge['parent_id']].append(edge)
        for a in reversed(order):
            for edge in outgoing[a]:
                if edge['object_up']:
                    effective_objects[a].update(effective_objects[edge['child_id']])
                if edge['property_up']:
                    effective_groups[a].update(effective_groups[edge['child_id']])
        epoch, rows, state_counts = fact_epoch(db), [], Counter()
        for mid in order:
            node = nodes[mid]
            if node['kind'] != 'MATERIAL':
                continue
            stats = {'properties': {}, 'direct_group_count': len(direct_groups[mid]),
                     'target_reference_group_count': len(reference_groups[mid] - direct_groups[mid]),
                     'effective_group_count': len(effective_groups[mid]),
                     'direct_objects': len(direct_objects[mid]), 'effective_objects': len(effective_objects[mid]),
                     'state_basis': 'EFFECTIVE_REVIEWED_ONLY', 'ranges_are_simulation_assignments': False}
            used = effective_groups[mid]
            stats['complete_groups'] = sum(len(observations[g]) == 3 for g in used)
            stats['partial_groups'] = sum(0 < len(observations[g]) < 3 for g in used)
            missing = []
            for prop in PROPERTIES:
                have = [g for g in used if prop in observations[g]]
                docs = {groups[g]['document_id'] for g in have}
                lineages = {groups[g]['lineage_key'] for g in have if groups[g]['lineage_verified'] and groups[g]['lineage_key']}
                stats['properties'][prop] = {
                    'value_groups': len(have), 'document_keys': len(docs), 'verified_lineages': len(lineages),
                    'low': min((observations[g][prop]['low'] for g in have), default=None),
                    'high': max((observations[g][prop]['high'] for g in have), default=None),
                    'group_ids': sorted(have), 'unit': 'GPa' if prop == 'E' else 'kg/m3' if prop == 'rho' else '1'}
                if not have:
                    missing.append(prop)
            state = (1 if effective_objects[mid] else 2) if not missing else (3 if effective_objects[mid] else 4)
            state_counts[state] += 1
            rows.append((mid, state, depths[mid], len(direct_objects[mid]), len(effective_objects[mid]), encoded(missing), encoded(stats), epoch))
        previous = {r[0]: r[1] for r in db.execute('SELECT material_id,state FROM material_state')}
        db.execute('DELETE FROM material_state')
        db.executemany('INSERT INTO material_state VALUES(?,?,?,?,?,?,?,?)', rows)
        transitions = Counter(str(previous[r[0]]) + '->' + str(r[1]) for r in rows if r[0] in previous and previous[r[0]] != r[1])
        set_meta(db, 'epoch', epoch)
        result = {'epoch': epoch, 'materials': len(rows), 'states': dict(state_counts), 'transitions': dict(transitions),
                  'objects': db.execute('SELECT COUNT(*) FROM objects WHERE accepted=1').fetchone()[0],
                  'components': db.execute('SELECT COUNT(*) FROM components').fetchone()[0],
                  'unresolved_obligations': db.execute('SELECT COUNT(*) FROM obligations WHERE resolved=0').fetchone()[0]}
        event(db, 'RECOMPUTE', result)
    return result


def plan(db):
    epoch = meta(db, 'epoch')
    if not epoch or fact_epoch(db) != epoch:
        raise ValueError('Facts/policy changed: run recompute first')
    now, desired = time.time(), []
    for r in db.execute('SELECT * FROM material_state'):
        mid, state = r['material_id'], r['state']
        if state in (3, 4):
            desired.append(('MATERIAL', mid, 'REPAIR_PROPERTIES' if state == 3 else 'DISCOVER_PROPERTIES', 0 if state == 3 else 1, r['depth']))
        else:
            desired.append(('OBJECT', mid, 'COLLECT_OBJECTS', 0 if state == 2 else 1, r['depth']))
            if any(v['document_keys'] < 5 for v in json.loads(r['stats_json'])['properties'].values()):
                desired.append(('MATERIAL', mid, 'ENHANCE_SOURCES', 2, r['depth']))
    for r in db.execute('SELECT * FROM obligations WHERE resolved=0'):
        desired.append(('MATERIAL', r['id'], 'RESOLVE_' + r['kind'], -1, 0))
    with transaction(db):
        previous_tasks = {r['business_key']: dict(r) for r in db.execute("SELECT * FROM tasks ORDER BY (status<>'STALE'),rowid")}
        stale_updates = []
        for old in db.execute("SELECT id,status,result_json FROM tasks WHERE epoch<>? AND status<>'STALE'", (epoch,)):
            old_result = json.loads(old['result_json']) if old['result_json'] else {}
            stale_updates.append((encoded({**old_result, '_pre_stale_status': old['status']}), old['id']))
        db.executemany("UPDATE tasks SET status='STALE',token=NULL,owner=NULL,lease_until=NULL,result_json=? WHERE id=?", stale_updates)
        for lane, subject, kind, tier, depth in desired:
            key = lane + ':' + subject + ':' + kind
            tid = hashlib.sha256((key + ':' + epoch).encode()).hexdigest()[:32]
            previous = previous_tasks.get(key, {})
            # A fact refresh changes leases, not the worker's source route.
            # Carry pending next-route and completed/cooldown state forward.
            status = previous.get('status', 'PENDING')
            previous_result = json.loads(previous['result_json']) if previous.get('result_json') else {}
            if status == 'STALE':
                status = previous_result.pop('_pre_stale_status', 'PENDING')
            if status not in ('DONE', 'COOLDOWN'):
                status = 'PENDING'
            result_json = encoded(previous_result) if previous_result else None
            db.execute('INSERT OR IGNORE INTO tasks(id,business_key,lane,subject_id,task_type,tier,depth,epoch,status,created,retry_at,result_json) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',
                       (tid, key, lane, subject, kind, tier, depth, epoch, status, now, previous.get('retry_at', 0), result_json))
            # Exact fact reversions can revisit an earlier content hash.
            # Restore its task without resetting route completion or budgets.
            db.execute("UPDATE tasks SET status=?,retry_at=?,result_json=? WHERE id=? AND status='STALE'", (status, previous.get('retry_at', 0), result_json, tid))
            # Existing-object safety repairs must preempt optional work even
            # when a new gap appears after the bounded run began.
            if lane == 'MATERIAL' and tier <= 0:
                db.execute('INSERT OR IGNORE INTO run_members SELECT id,? FROM runs WHERE deadline>? AND claims<max_claims', (subject, now))
        event(db, 'PLAN', {'epoch': epoch, 'desired_tasks': len(desired)})
    return {'epoch': epoch, 'desired_tasks': len(desired), 'by_lane': dict(Counter(x[0] for x in desired))}


def start_run(db, run_id, seconds=1800, max_claims=60, per_material=3):
    if seconds <= 0 or max_claims < 1 or per_material < 1:
        raise ValueError('Run budgets must be positive')
    with transaction(db):
        if db.execute('SELECT 1 FROM runs WHERE id=?', (run_id,)).fetchone():
            raise ValueError('Run exists; reuse it without resetting budget')
        now = time.time()
        db.execute('INSERT INTO runs(id,started,deadline,max_claims,per_material) VALUES(?,?,?,?,?)', (run_id, now, now + seconds, max_claims, per_material))
        db.execute('INSERT INTO run_members SELECT ?,subject_id FROM tasks WHERE epoch=? GROUP BY subject_id', (run_id, meta(db, 'epoch')))
    return {'run_id': run_id, 'max_claims': max_claims, 'seconds': seconds}


def register_proposal(db, proposal_key, manifest_sha256, collector):
    if len(manifest_sha256) != 64 or any(c not in '0123456789abcdef' for c in manifest_sha256) or not collector:
        raise ValueError('Exact SHA256 and collector required')
    with transaction(db):
        existing = db.execute('SELECT * FROM proposals WHERE proposal_key=?', (proposal_key,)).fetchone()
        if existing and (existing['manifest_sha256'] != manifest_sha256 or existing['collector'] != collector):
            raise ValueError('Proposal key is frozen to different inputs/collector')
        db.execute('INSERT OR IGNORE INTO proposals(proposal_key,manifest_sha256,collector) VALUES(?,?,?)', (proposal_key, manifest_sha256, collector))
    return {'proposal_key': proposal_key, 'manifest_sha256': manifest_sha256}


def register_review(db, proposal_key, manifest_sha256, reviewer, decision, basis):
    with transaction(db):
        proposal = db.execute('SELECT * FROM proposals WHERE proposal_key=?', (proposal_key,)).fetchone()
        if not proposal or proposal['manifest_sha256'] != manifest_sha256:
            raise ValueError('Review does not match frozen proposal manifest')
        if not reviewer or reviewer == proposal['collector'] or not basis:
            raise ValueError('Independent reviewer and review basis required')
        if decision not in ('PASS', 'HOLD', 'REJECT'):
            raise ValueError('Invalid review decision')
        key = hashlib.sha256(encoded([proposal_key, manifest_sha256, reviewer]).encode()).hexdigest()
        db.execute('INSERT OR REPLACE INTO reviews VALUES(?,?,?,?,?,?)', (key, proposal_key, manifest_sha256, reviewer, decision, basis))
        event(db, 'REVIEW', {'proposal': proposal_key, 'reviewer': reviewer, 'decision': decision})
    return {'review_id': key, 'accepted_fact_mutations': 0}


def admission_guard(db, proposal_key, manifest_sha256):
    proposal = db.execute('SELECT * FROM proposals WHERE proposal_key=?', (proposal_key,)).fetchone()
    if not proposal or proposal['manifest_sha256'] != manifest_sha256:
        raise ValueError('Manifest mismatch')
    reviews = list(db.execute('SELECT * FROM reviews WHERE proposal_key=?', (proposal_key,)))
    if not reviews or any(r['manifest_sha256'] != manifest_sha256 or r['reviewer'] == proposal['collector'] or r['decision'] != 'PASS' for r in reviews):
        raise ValueError('Missing, conflicting, nonindependent, or nonpassing review')
    return {'proposal_key': proposal_key, 'review_ready': True, 'accepted_fact_mutations': 0,
            'next_step': 'Existing schema-specific frozen delta merger; this guard does not apply facts'}


def claim(db, run_id, lane, owner, lease_seconds=300, now=None):
    if lease_seconds < 1 or lease_seconds > 3600 or lane not in ('MATERIAL', 'OBJECT') or not owner:
        raise ValueError('Invalid claim arguments')
    now = time.time() if now is None else now
    with transaction(db):
        run = db.execute('SELECT * FROM runs WHERE id=?', (run_id,)).fetchone()
        if not run:
            raise ValueError('Unknown run')
        if now >= run['deadline'] or run['claims'] >= run['max_claims']:
            return {'status': 'BUDGET_EXHAUSTED'}
        epoch = meta(db, 'epoch')
        if fact_epoch(db) != epoch:
            raise ValueError('Facts/policy changed: recompute and replan before claim')
        db.execute("UPDATE tasks SET status='COOLDOWN',retry_at=?,token=NULL,owner=NULL,lease_until=NULL WHERE status='LEASED' AND lease_until<=?", (now, now))
        candidates = [dict(r) for r in db.execute("SELECT t.*,COALESCE(n.family,'unclassified') family,COALESCE(n.flexible,0) flexible FROM tasks t LEFT JOIN nodes n ON n.id=t.subject_id JOIN run_members m ON m.subject_id=t.subject_id AND m.run_id=? WHERE t.lane=? AND t.epoch=? AND t.status IN('PENDING','COOLDOWN') AND t.retry_at<=?", (run_id, lane, epoch, now))]
        material_use = Counter(r[0] for r in db.execute('SELECT subject_id FROM attempts WHERE run_id=?', (run_id,)))
        candidates = [t for t in candidates if material_use[t['subject_id']] < run['per_material']]
        if not candidates:
            return {'status': 'NO_READY_TASK'}
        if lane == 'OBJECT':
            # Preserve slot across epochs. Two state-2 slots, then one state-1 slot.
            preferred_tier = 0 if run['object_slot'] % 3 < 2 else 1
            selected = [t for t in candidates if t['tier'] == preferred_tier]
            candidates = selected or candidates
        tier = min(t['tier'] for t in candidates)
        candidates = [t for t in candidates if t['tier'] == tier]
        depth = min(t['depth'] for t in candidates)
        candidates = [t for t in candidates if t['depth'] == depth]
        history = list(db.execute('SELECT a.subject_id,a.family,a.started FROM attempts a JOIN tasks t ON a.task_id=t.id WHERE a.run_id=? AND t.lane=? AND t.tier=? AND t.depth=? ORDER BY a.started', (run_id, lane, tier, depth)))
        family_use, family_last, subject_last = Counter(), {}, {}
        for subject, family, started in history:
            family_use[family] += 1
            family_last[family] = started
            subject_last[subject] = started
        task = min(candidates, key=lambda t: (family_use[t['family']], family_last.get(t['family'], 0),
                    material_use[t['subject_id']], subject_last.get(t['subject_id'], 0), -t['flexible'], t['created'], t['id']))
        previous_result = json.loads(task['result_json']) if task.get('result_json') else {}
        route_key = (previous_result.get('next_route') or 'initial').strip()
        if db.execute('SELECT 1 FROM task_routes WHERE business_key=? AND route_key=?', (task['business_key'], route_key)).fetchone():
            raise ValueError('Previously completed route requires explicit new route, not replay')
        token = uuid.uuid4().hex
        lease_until = min(now + lease_seconds, run['deadline'])
        db.execute("UPDATE tasks SET status='LEASED',owner=?,token=?,lease_until=?,attempts=attempts+1 WHERE id=?", (owner, token, lease_until, task['id']))
        db.execute('INSERT INTO attempts(token,task_id,run_id,subject_id,family,started) VALUES(?,?,?,?,?,?)', (token, task['id'], run_id, task['subject_id'], task['family'], now))
        db.execute('UPDATE runs SET claims=claims+1,object_slot=object_slot+? WHERE id=?', (int(lane == 'OBJECT'), run_id))
        event(db, 'CLAIM', {'task_id': task['id'], 'token': token, 'owner': owner, 'run_id': run_id})
        return {**task, 'status': 'LEASED', 'route_key': route_key, 'token': token, 'owner': owner, 'lease_until': lease_until}


def finish(db, task_id, token, outcome, result, cooldown_seconds=3600, now=None):
    now = time.time() if now is None else now
    if outcome not in ('DELIVERED', 'NO_PROGRESS', 'RETRY') or cooldown_seconds < 0 or not isinstance(result, dict):
        raise ValueError('Invalid outcome/cooldown')
    with transaction(db):
        task = db.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not task or task['status'] != 'LEASED' or task['token'] != token or task['lease_until'] <= now:
            raise ValueError('Lease expired, replaced, or token invalid')
        if task['epoch'] != meta(db, 'epoch') or fact_epoch(db) != task['epoch']:
            raise ValueError('Input epoch changed; preserve output and rebase for review')
        previous_result = json.loads(task['result_json']) if task['result_json'] else {}
        route_key = (previous_result.get('next_route') or 'initial').strip()
        next_route = result.get('next_route')
        if next_route is not None:
            if not isinstance(next_route, str) or not next_route.strip() or len(next_route) > 500:
                raise ValueError('next_route requires a concise nonempty route key')
            next_route = next_route.strip()
            result = {**result, 'next_route': next_route}
            if next_route == route_key or db.execute('SELECT 1 FROM task_routes WHERE business_key=? AND route_key=?', (task['business_key'], next_route)).fetchone():
                raise ValueError('next_route must name a different, previously uncompleted route')
        if outcome == 'DELIVERED':
            db.execute('INSERT INTO task_routes VALUES(?,?,?,?)', (task['business_key'], task['epoch'], route_key, token))
        status = ('PENDING' if next_route else 'DONE') if outcome == 'DELIVERED' else 'COOLDOWN'
        # Retry retains the current route unless the worker explicitly switches.
        task_result = dict(result)
        if outcome != 'DELIVERED' and not next_route:
            task_result['next_route'] = route_key
        db.execute('UPDATE tasks SET status=?,retry_at=?,result_json=?,owner=NULL,token=NULL,lease_until=NULL WHERE id=?', (status, now if status == 'PENDING' else now + cooldown_seconds, encoded(task_result), task_id))
        db.execute('UPDATE attempts SET finished=?,outcome=?,result_json=? WHERE token=?', (now, outcome, encoded({**result, 'route_key': route_key}), token))
        event(db, 'FINISH', {'task_id': task_id, 'outcome': outcome, 'accepted_fact_mutations': 0})
    return {'task_id': task_id, 'status': status, 'accepted_fact_mutations': 0}


def schedule_route(db, task_id, route_key, basis):
    """Resume a current task only for a distinct route or review-feedback task."""
    if not isinstance(route_key, str) or not route_key.strip() or len(route_key) > 500 or not basis.strip():
        raise ValueError('A distinct named route and explicit basis are required')
    route_key = route_key.strip()
    with transaction(db):
        task = db.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        if not task or task['status'] in ('LEASED', 'STALE'):
            raise ValueError('Cannot reschedule missing, leased, or stale task')
        if task['epoch'] != meta(db, 'epoch') or fact_epoch(db) != task['epoch']:
            raise ValueError('Recompute and replan before scheduling a new route')
        if db.execute('SELECT 1 FROM task_routes WHERE business_key=? AND route_key=?', (task['business_key'], route_key)).fetchone():
            raise ValueError('Previously delivered route; name a distinct follow-up scope')
        previous = json.loads(task['result_json']) if task['result_json'] else {}
        result = {**previous, 'next_route': route_key, 'route_basis': basis.strip()}
        db.execute("UPDATE tasks SET status='PENDING',retry_at=0,result_json=? WHERE id=?", (encoded(result), task_id))
        event(db, 'SCHEDULE_ROUTE', {'task_id': task_id, 'route_key': route_key, 'basis': basis.strip(), 'accepted_fact_mutations': 0})
    return {'task_id': task_id, 'route_key': route_key, 'status': 'PENDING', 'accepted_fact_mutations': 0}


def summary(db):
    if fact_epoch(db) != meta(db, 'epoch'):
        raise ValueError('Derived states stale: recompute before reporting/export')
    states = [dict(r) for r in db.execute('SELECT * FROM material_state')]
    direct_required = [r for r in states if r['direct_objects']]
    effective_required = [r for r in states if r['effective_objects']]
    return {'schema_version': 1, 'snapshot_release_id': meta(db, 'release_id'), 'upstream_evidence_release_id': meta(db, 'upstream_evidence_release_id'), 'epoch': meta(db, 'epoch'),
            'policy_sha256': digest_file(HERE / 'SPEC.md'), 'shadow_database': True,
            'material_state_basis': 'EFFECTIVE_REVIEWED_ONLY', 'material_states': dict(Counter(str(r['state']) for r in states)),
            'material_count': len(states), 'source_object_identities': db.execute('SELECT count(*) FROM objects WHERE accepted=1').fetchone()[0],
            'component_keys': db.execute('SELECT count(*) FROM components').fetchone()[0],
            'component_kinds': dict(db.execute('SELECT kind,count(*) FROM components GROUP BY kind')),
            'direct_required_materials': len(direct_required), 'direct_required_all_properties': sum(not json.loads(r['missing_json']) for r in direct_required),
            'effective_required_materials': len(effective_required), 'effective_required_all_properties': sum(not json.loads(r['missing_json']) for r in effective_required),
            'accepted_group_count': db.execute('SELECT count(*) FROM evidence_groups WHERE accepted=1').fetchone()[0],
            'unresolved_obligations': db.execute('SELECT count(*) FROM obligations WHERE resolved=0').fetchone()[0],
            'tasks': [dict(r) for r in db.execute('SELECT lane,status,count(*) count FROM tasks GROUP BY lane,status')],
            'input_manifest': meta(db, 'inputs', {}),
            'limitations': ['Shadow execution projection; not a published database migration.', 'Document keys are not verified independent source lineages.', 'Source object identities are not global content-deduplicated geometry.']}


def verify_inputs(db, root):
    changed = []
    for relative, expected in meta(db, 'inputs', {}).items():
        path = Path(root) / relative
        if not path.is_file() or digest_file(path) != expected:
            changed.append(relative)
    if changed:
        raise ValueError('Frozen inputs changed; new import/review required: ' + encoded(changed))
    return {'status': 'PINNED_INPUTS_MATCH', 'files': len(meta(db, 'inputs', {}))}


def export(db, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    result = summary(db)
    (out / 'summary.json').write_text(encoded(result) + '\n')
    material_rows = []
    for r in db.execute('SELECT s.*,n.name_cn,n.name_en,n.family,n.granularity FROM material_state s JOIN nodes n ON n.id=s.material_id ORDER BY s.state,s.depth,s.material_id'):
        v = dict(r)
        v['missing_properties'] = json.loads(v.pop('missing_json'))
        v['evidence'] = json.loads(v.pop('stats_json'))
        material_rows.append(v)
    (out / 'material_states.json').write_text(encoded(material_rows) + '\n')
    lines = ['# RSI 材料缺项与物体反馈队列', '', '当前查询结果；不代表任何材料在全网无法找到。', '']
    for state, title in [(3, '现有物体材料缺项（优先）'), (2, '三项齐全、暂无物体'), (4, '可选研究档案')]:
        selected = [r for r in material_rows if r['state'] == state]
        lines += [f'## {title}：{len(selected)}', '']
        lines += [f"- {r['name_cn']} / {r['name_en']}（{r['material_id']}）；缺项：{','.join(r['missing_properties']) or '无'}；直接/含子类对象：{r['direct_objects']}/{r['effective_objects']}。" for r in selected]
        lines.append('')
    (out / 'QUEUES.md').write_text('\n'.join(lines))
    files = {p.name: digest_file(p) for p in out.iterdir() if p.is_file() and p.name != 'manifest.json'}
    manifest = {'release_id': meta(db, 'release_id'), 'epoch': meta(db, 'epoch'), 'policy_sha256': digest_file(HERE / 'SPEC.md'), 'files': files, 'website_published': False}
    (out / 'manifest.json').write_text(encoded(manifest) + '\n')
    return {'output': str(out.resolve()), 'files': files}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db', type=Path, required=True)
    sub = p.add_subparsers(dest='command', required=True)
    for cmd in ('recompute', 'plan', 'status'):
        sub.add_parser(cmd)
    s = sub.add_parser('start-run')
    s.add_argument('--id', required=True)
    s.add_argument('--seconds', type=int, default=1800)
    s.add_argument('--max-claims', type=int, default=60)
    s.add_argument('--per-material', type=int, default=3)
    s = sub.add_parser('claim')
    s.add_argument('--run', required=True)
    s.add_argument('--lane', choices=['MATERIAL', 'OBJECT'], required=True)
    s.add_argument('--owner', required=True)
    s = sub.add_parser('finish')
    s.add_argument('--task', required=True)
    s.add_argument('--token', required=True)
    s.add_argument('--outcome', choices=['DELIVERED', 'NO_PROGRESS', 'RETRY'], required=True)
    s.add_argument('--result', type=Path, required=True)
    s = sub.add_parser('schedule-route')
    s.add_argument('--task', required=True)
    s.add_argument('--route', required=True)
    s.add_argument('--basis', required=True)
    s = sub.add_parser('export')
    s.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('verify-inputs')
    s.add_argument('--root', type=Path, required=True)
    a = p.parse_args()
    db = connect(a.db)
    if a.command == 'recompute': result = recompute(db)
    elif a.command == 'plan': result = plan(db)
    elif a.command == 'status': result = summary(db)
    elif a.command == 'start-run': result = start_run(db, a.id, a.seconds, a.max_claims, a.per_material)
    elif a.command == 'claim': result = claim(db, a.run, a.lane, a.owner)
    elif a.command == 'finish': result = finish(db, a.task, a.token, a.outcome, json.loads(a.result.read_text()))
    elif a.command == 'schedule-route': result = schedule_route(db, a.task, a.route, a.basis)
    elif a.command == 'verify-inputs': result = verify_inputs(db, a.root)
    else: result = export(db, a.out)
    print(encoded(result))
    db.close()


if __name__ == '__main__':
    main()
