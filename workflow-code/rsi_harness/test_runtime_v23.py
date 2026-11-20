import tempfile
import sqlite3
import unittest
import json
from pathlib import Path

import harness
from runtime_v23 import (append_review, apply_schema, claim_scan_route, commit_proposal,
                         cancel_scan, create_scan, end_scan_run, extend_scan_budget, finish_scan_route,
                         register_proposal_v23, register_release_views, seed_scan_frontier,
                         start_scan_run, verify_release_views, inspect_runtime_consistency,
                         recover_stale_run)
from rsi_v23 import clone_shadow
from queries_v23 import material_queue


class RuntimeV23Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = harness.connect(Path(self.tmp.name) / 'db.sqlite')
        apply_schema(self.db)

    def tearDown(self):
        self.db.close(); self.tmp.cleanup()

    @staticmethod
    def receipt(manifest='a'*64, delta='x'*64, parent_release='r1', epoch='e1',
                parent='d'*64, before='d'*64, after='c'*64):
        return {'manifest_sha256': manifest, 'delta_sha256': delta,
                'parent_release_id': parent_release, 'parent_fact_epoch': epoch,
                'parent_data_sha256': parent, 'before_sha256': before,
                'after_sha256': after}

    def seed_material_state(self, material_id, state, epoch='d1'):
        self.db.execute("INSERT INTO nodes(id,name_cn,name_en,kind) VALUES(?,?,?,'MATERIAL')",
                        (material_id, material_id, material_id))
        self.db.execute("INSERT INTO material_state VALUES(?,?,?,?,?,?,?,?)",
                        (material_id, state, 0, 0, 0, '[]', '{}', epoch))

    def test_scan_extension_is_idempotent_and_keeps_spend(self):
        create_scan(self.db, 's1', 'MIXED', 'd1', 't1', 10, 60, now=1)
        self.db.execute("UPDATE scans SET claims_spent=10,seconds_spent=30,status='PAUSED_BUDGET' WHERE scan_id='s1'")
        event = dict(event_id='b1', actor='coord', reason='continue', authorization_scope='user',
                     expected_revision=0, new_claims_limit=20, new_seconds_limit=120)
        self.assertFalse(extend_scan_budget(self.db, 's1', event, now=2)['replayed'])
        self.assertTrue(extend_scan_budget(self.db, 's1', event, now=3)['replayed'])
        row = self.db.execute('SELECT claims_spent,seconds_spent,status FROM scans WHERE scan_id="s1"').fetchone()
        self.assertEqual(tuple(row), (10, 30, 'READY'))

    def test_proposal_review_and_parent_guard(self):
        register_proposal_v23(self.db, 'p1', 'a'*64, 'collector', 'r1', 'e1', 'd'*64, '1'*64)
        append_review(self.db, 'p1', 'a'*64, 'reviewer', 'PASS', 'checked', now=1)
        def apply(db):
            db.execute("INSERT INTO meta(key,value) VALUES('applied','true')")
            return 'c'*64
        out = commit_proposal(self.db, 'p1', 'a'*64, 'r1', 'e1', 'd'*64,
                              'merger', self.receipt(delta='1'*64), apply, now=2)
        self.assertEqual(out['status'], 'MERGED')
        with self.assertRaises(ValueError):
            commit_proposal(self.db, 'p1', 'a'*64, 'r1', 'e1', 'd'*64,
                            'merger', {'delta': 'x'}, apply, now=3)

    def test_hold_cannot_be_overridden_and_failed_delta_rolls_back(self):
        register_proposal_v23(self.db, 'p2', 'b'*64, 'collector', 'r1', 'e1', 'd'*64, '2'*64)
        append_review(self.db, 'p2', 'b'*64, 'reviewer', 'HOLD', 'needs evidence', now=1)
        append_review(self.db, 'p2', 'b'*64, 'reviewer2', 'PASS', 'reviewed later', now=2)
        def apply(db):
            db.execute("INSERT INTO meta(key,value) VALUES('should_rollback','true')")
            return 'c'*64
        with self.assertRaises(ValueError):
            commit_proposal(self.db, 'p2', 'b'*64, 'r1', 'e1', 'd'*64,
                            'merger', self.receipt(manifest='b'*64, delta='2'*64), apply, now=3)
        self.assertIsNone(self.db.execute("SELECT 1 FROM meta WHERE key='should_rollback'").fetchone())

    def test_delta_exception_rolls_back_facts_and_receipt(self):
        register_proposal_v23(self.db, 'p3', 'c'*64, 'collector', 'r1', 'e1', 'd'*64, '3'*64)
        append_review(self.db, 'p3', 'c'*64, 'reviewer', 'PASS', 'checked', now=1)
        def fail_after_write(db):
            db.execute("INSERT INTO meta(key,value) VALUES('partial_fact','true')")
            raise RuntimeError('adapter failure')
        with self.assertRaisesRegex(RuntimeError, 'adapter failure'):
            commit_proposal(self.db, 'p3', 'c'*64, 'r1', 'e1', 'd'*64,
                            'merger', self.receipt(manifest='c'*64, delta='3'*64), fail_after_write, now=2)
        self.assertIsNone(self.db.execute("SELECT 1 FROM meta WHERE key='partial_fact'").fetchone())
        self.assertEqual(self.db.execute("SELECT merge_status FROM proposal_lineage WHERE proposal_key='p3'").fetchone()[0], 'UNMERGED')

    def test_proposal_receipt_must_pin_delta_and_merger_must_be_independent(self):
        register_proposal_v23(self.db, 'p4', '4'*64, 'collector', 'r1', 'e1', 'd'*64, 'f'*64)
        append_review(self.db, 'p4', '4'*64, 'reviewer', 'PASS', 'checked', now=1)
        def apply(db):
            return 'c'*64
        receipt = self.receipt(manifest='4'*64, delta='0'*64)
        with self.assertRaisesRegex(ValueError, 'does not bind'):
            commit_proposal(self.db, 'p4', '4'*64, 'r1', 'e1', 'd'*64,
                            'merger', receipt, apply, now=2)
        with self.assertRaisesRegex(ValueError, 'independent'):
            commit_proposal(self.db, 'p4', '4'*64, 'r1', 'e1', 'd'*64,
                            'reviewer', self.receipt(manifest='4'*64, delta='f'*64), apply, now=2)
        self.assertEqual(self.db.execute("SELECT merge_status FROM proposal_lineage WHERE proposal_key='p4'").fetchone()[0], 'UNMERGED')

    def test_duplicate_review_is_idempotent_but_changed_decision_requires_new_manifest(self):
        register_proposal_v23(self.db, 'p-review', '5'*64, 'collector', 'r1', 'e1', 'd'*64, 'f'*64)
        first = append_review(self.db, 'p-review', '5'*64, 'reviewer', 'HOLD', 'needs locator', now=1)
        replay = append_review(self.db, 'p-review', '5'*64, 'reviewer', 'HOLD', 'needs locator', now=2)
        self.assertEqual(first['review_id'], replay['review_id'])
        self.assertTrue(replay['replayed'])
        with self.assertRaisesRegex(ValueError, 'revise the proposal'):
            append_review(self.db, 'p-review', '5'*64, 'reviewer', 'PASS', 'now convinced', now=3)

    def test_scan_claims_persist_budget_and_resume_frontier(self):
        self.seed_material_state('m1', 2)
        create_scan(self.db, 's1', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        tasks = [dict(lane='OBJECT', task_type='OBJECT_DISCOVERY', subject_id='m1',
                      state=2, attribute_scope='NONE', priority=0, depth=1, family='wood', route_key='official')]
        seed_scan_frontier(self.db, 's1', tasks, 'd1', 't1', now=1)
        start_scan_run(self.db, 's1', 'r1', 5, now=2)
        task = claim_scan_route(self.db, 's1', 'r1', 'OBJECT', 'worker', now=3)
        self.assertEqual(task['status'], 'LEASED')
        finish_scan_route(self.db, 's1', 'r1', task['business_key'], task['route_key'], task['token'],
                          'DELIVERED', now=4)
        result = end_scan_run(self.db, 's1', 'r1', now=5)
        self.assertEqual(result['status'], 'COMPLETE')
        row = self.db.execute("SELECT claims_spent,seconds_spent FROM scans WHERE scan_id='s1'").fetchone()
        self.assertEqual(tuple(row), (1, 3))

    def test_runtime_recovery_requires_pinned_diagnosis_and_preserves_budget(self):
        self.seed_material_state('m-recover', 2)
        create_scan(self.db, 's-recover', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        seed_scan_frontier(self.db, 's-recover', [dict(
            lane='OBJECT', task_type='OBJECT_DISCOVERY', subject_id='m-recover', state=2,
            attribute_scope='NONE', priority=0, depth=0, family='wood', route_key='official')],
            'd1', 't1', now=1)
        start_scan_run(self.db, 's-recover', 'r-recover', 5, now=2)
        task = claim_scan_route(self.db, 's-recover', 'r-recover', 'OBJECT', 'worker',
                                lease_seconds=1, now=3)
        diagnosis = inspect_runtime_consistency(self.db, 's-recover', now=5)
        self.assertEqual(diagnosis['status'], 'HOLD_RUNTIME_RECONCILIATION_REQUIRED')
        self.assertTrue(any(i['kind'] == 'EXPIRED_LEASE_LEFT_OPEN' for i in diagnosis['issues']))
        with self.assertRaisesRegex(ValueError, 'diagnosis changed'):
            recover_stale_run(self.db, 's-recover', 'r-recover', 'operator', 'stale worker',
                              '0' * 64, now=5)
        result = recover_stale_run(self.db, 's-recover', 'r-recover', 'operator', 'stale worker',
                                   diagnosis['issue_digest'], now=5)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['leases_revoked'], 1)
        scan = self.db.execute("SELECT claims_spent,seconds_spent,status FROM scans WHERE scan_id='s-recover'").fetchone()
        self.assertEqual(scan['claims_spent'], 1)
        self.assertEqual(scan['seconds_spent'], 3)
        self.assertEqual(scan['status'], 'READY')
        self.assertEqual(self.db.execute("SELECT active FROM scan_runs WHERE run_id='r-recover'").fetchone()[0], 0)
        event = self.db.execute("SELECT payload_json FROM events WHERE kind='SCAN_RUN_RECOVERED'").fetchone()
        self.assertIsNotNone(event)
        self.assertEqual(json.loads(event[0])['claims_spent_preserved'], 1)

    def test_runtime_consistency_detects_orphaned_active_run(self):
        self.seed_material_state('m-orphan', 4)
        create_scan(self.db, 's-orphan', 'MIXED', 'd1', 't1', 10, 100, now=1)
        seed_scan_frontier(self.db, 's-orphan', [dict(
            lane='MATERIAL', task_type='MATERIAL_OPTIONAL_RESEARCH', subject_id='m-orphan',
            state=4, attribute_scope='E', priority=0, depth=0, family='ceramic', route_key='official')],
            'd1', 't1', now=1)
        start_scan_run(self.db, 's-orphan', 'r-orphan', 1, now=2)
        self.db.execute("UPDATE scans SET status='READY' WHERE scan_id='s-orphan'")
        diagnosis = inspect_runtime_consistency(self.db, 's-orphan', now=3)
        self.assertTrue(any(i['kind'] == 'ACTIVE_RUN_WITH_NONRUNNING_SCAN' for i in diagnosis['issues']))

    def test_expired_and_revoked_leases_have_correlatable_terminal_events(self):
        self.seed_material_state('m-expiry', 2)
        create_scan(self.db, 's-expiry', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        seed_scan_frontier(self.db, 's-expiry', [dict(
            lane='OBJECT', task_type='OBJECT_DISCOVERY', subject_id='m-expiry', state=2,
            attribute_scope='NONE', priority=0, depth=0, family='wood', route_key='official')],
            'd1', 't1', now=1)
        start_scan_run(self.db, 's-expiry', 'r-expiry', 5, now=2)
        first = claim_scan_route(self.db, 's-expiry', 'r-expiry', 'OBJECT', 'worker-a',
                                 lease_seconds=1, now=3)
        second = claim_scan_route(self.db, 's-expiry', 'r-expiry', 'OBJECT', 'worker-b',
                                  lease_seconds=1, now=5)
        self.assertNotEqual(first['token'], second['token'])
        with self.assertRaisesRegex(ValueError, 'lease expired, replaced or token invalid'):
            finish_scan_route(self.db, 's-expiry', 'r-expiry', first['business_key'],
                              first['route_key'], first['token'], 'DELIVERED', now=5.1)
        expired = self.db.execute("SELECT payload_json FROM events WHERE kind='SCAN_ROUTE_LEASE_EXPIRED'").fetchone()
        self.assertIsNotNone(expired)
        expired_payload = json.loads(expired[0])
        self.assertEqual(expired_payload['lease_token'], first['token'])
        self.assertEqual(expired_payload['attempt'], 1)
        self.assertEqual(expired_payload['reason'], 'LEASE_EXPIRED')
        end_scan_run(self.db, 's-expiry', 'r-expiry', now=5.5)
        revoked = self.db.execute("SELECT payload_json FROM events WHERE kind='SCAN_ROUTE_LEASE_REVOKED'").fetchone()
        self.assertIsNotNone(revoked)
        revoked_payload = json.loads(revoked[0])
        self.assertEqual(revoked_payload['lease_token'], second['token'])
        self.assertEqual(revoked_payload['attempt'], 2)
        self.assertEqual(revoked_payload['reason'], 'RUN_ENDED')
        start_scan_run(self.db, 's-expiry', 'r-expiry-2', 2, now=6)
        third = claim_scan_route(self.db, 's-expiry', 'r-expiry-2', 'OBJECT', 'worker-c',
                                 lease_seconds=1, now=6)
        cancel_scan(self.db, 's-expiry', 'operator', 'source withdrawn', now=6.5)
        cancelled = self.db.execute("SELECT payload_json FROM events WHERE kind='SCAN_ROUTE_LEASE_REVOKED' ORDER BY id DESC LIMIT 1").fetchone()
        cancelled_payload = json.loads(cancelled[0])
        self.assertEqual(cancelled_payload['lease_token'], third['token'])
        self.assertEqual(cancelled_payload['reason'], 'SCAN_CANCELLED')

    def test_scan_rejects_ineligible_material_discovery(self):
        self.seed_material_state('m3', 3)
        create_scan(self.db, 's2', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        with self.assertRaises(ValueError):
            seed_scan_frontier(self.db, 's2', [dict(lane='OBJECT', task_type='OBJECT_DISCOVERY',
                subject_id='m3', state=3, attribute_scope='NONE')], 'd1', 't1', now=1)
        for invalid_state in (True, 1.0, '1'):
            with self.assertRaises(ValueError):
                seed_scan_frontier(self.db, 's2', [dict(lane='OBJECT', task_type='OBJECT_DISCOVERY',
                    subject_id='m3', state=invalid_state, attribute_scope='NONE')], 'd1', 't1', now=1)
        with self.assertRaisesRegex(ValueError, 'current derived material state'):
            seed_scan_frontier(self.db, 's2', [dict(lane='OBJECT', task_type='OBJECT_DISCOVERY',
                subject_id='m3', state=2, attribute_scope='NONE')], 'd1', 't1', now=1)

    def test_scan_rejects_unknown_or_cross_lane_task_type(self):
        create_scan(self.db, 's-types', 'MIXED', 'd1', 't1', 10, 100, now=1)
        with self.assertRaisesRegex(ValueError, 'not valid for lane'):
            seed_scan_frontier(self.db, 's-types', [dict(lane='MATERIAL', task_type='OBJECT_DISCOVERY',
                subject_id='m1', state=2, attribute_scope='NONE')], 'd1', 't1', now=1)
        with self.assertRaisesRegex(ValueError, 'not valid for lane'):
            seed_scan_frontier(self.db, 's-types', [dict(lane='OBJECT', task_type='OBJECT_GUESS_MATERIAL',
                subject_id='o1', state=1, attribute_scope='NONE', existing_object=True,
                component_id='part-1')], 'd1', 't1', now=1)

    def test_material_scope_obligation_is_queueable_only_when_database_backed(self):
        harness.set_meta(self.db, 'epoch', 'd1')
        self.db.execute("INSERT INTO obligations(id,kind,reason) VALUES('rel-1','SOURCE_RELATION','unresolved relation')")
        tasks = material_queue(self.db)
        task = next(row for row in tasks if row['task_type'] == 'MATERIAL_SCOPE_OBLIGATION_REPAIR')
        self.assertEqual(task['obligation_id'], 'rel-1')
        create_scan(self.db, 's-material-obligation', 'MATERIAL', 'd1', 't1', 5, 30, now=1)
        seeded = seed_scan_frontier(self.db, 's-material-obligation', [task], 'd1', 't1', now=1)
        self.assertEqual(seeded['added_routes'], 1)
        with self.assertRaisesRegex(ValueError, 'objectless obligation'):
            seed_scan_frontier(self.db, 's-material-obligation', [dict(
                lane='MATERIAL', task_type='MATERIAL_SCOPE_OBLIGATION_REPAIR',
                subject_id='invented', obligation_id='invented', attribute_scope='NONE')], 'd1', 't1', now=2)
        self.db.execute("UPDATE obligations SET resolved=1 WHERE id='rel-1'")
        with self.assertRaisesRegex(ValueError, 'objectless obligation'):
            seed_scan_frontier(self.db, 's-material-obligation', [task], 'd1', 't1', now=3)

    def test_scan_purpose_and_cancel_state_are_enforced(self):
        create_scan(self.db, 's-object', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        with self.assertRaisesRegex(ValueError, 'outside scan purpose'):
            seed_scan_frontier(self.db, 's-object', [dict(lane='MATERIAL', task_type='MATERIAL_OPTIONAL_RESEARCH',
                subject_id='m1', state=4, attribute_scope='E', family='wood')], 'd1', 't1', now=1)
        result = cancel_scan(self.db, 's-object', 'operator', 'source was withdrawn', now=2)
        self.assertEqual(result['status'], 'CANCELLED')
        self.assertTrue(cancel_scan(self.db, 's-object', 'operator', 'source was withdrawn', now=3)['replayed'])
        with self.assertRaisesRegex(ValueError, 'cancelled scan'):
            seed_scan_frontier(self.db, 's-object', [dict(lane='OBJECT', task_type='OBJECT_DISCOVERY',
                subject_id='m1', state=2, attribute_scope='NONE', family='wood')], 'd1', 't1', now=4)
        with self.assertRaisesRegex(ValueError, 'cancelled scan'):
            start_scan_run(self.db, 's-object', 'run-cancelled', 1, now=4)

    def test_seed_scan_preserves_component_repair_identity_and_urgent_priority(self):
        self.db.execute("INSERT INTO objects(id,namespace,source_uid,name_cn,name_en,source_url,asset_url) VALUES('o1','test','1','椅子','Chair','u','a')")
        self.db.executemany("INSERT INTO components(object_id,id,kind,scope,basis) VALUES('o1',?,'PHYSICAL',?,'source')",
                            [('seat', 'seat'), ('frame', 'frame')])
        self.db.executemany("INSERT INTO obligations(id,object_id,component_id,kind,reason) VALUES(?, 'o1', ?, 'COMPONENT_SCOPE', 'scope review')",
                            [('ob-seat', 'seat'), ('ob-frame', 'frame')])
        create_scan(self.db, 's-repairs', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        tasks = [
            dict(lane='OBJECT', task_type='OBJECT_SCOPE_REPAIR', subject_id='o1', object_id='o1',
                 component_id='seat', obligation_id='ob-seat', existing_object=True,
                 attribute_scope='NONE', priority=-1, depth=0, family='existing-object-repair'),
            dict(lane='OBJECT', task_type='OBJECT_SCOPE_REPAIR', subject_id='o1', object_id='o1',
                 component_id='frame', obligation_id='ob-frame', existing_object=True,
                 attribute_scope='NONE', priority=-1, depth=0, family='existing-object-repair'),
        ]
        result = seed_scan_frontier(self.db, 's-repairs', tasks, 'd1', 't1', now=1)
        self.assertEqual(result['added_routes'], 2)
        routes = list(self.db.execute("SELECT business_key,priority FROM scan_routes WHERE scan_id='s-repairs' ORDER BY priority,business_key"))
        self.assertEqual(len(routes), 2)
        self.assertTrue(all(row['priority'] == -1 for row in routes))

    def test_object_repair_cannot_invent_an_existing_object_or_component(self):
        create_scan(self.db, 's-invalid-repair', 'OBJECT', 'd1', 't1', 10, 100, now=1)
        task = dict(lane='OBJECT', task_type='OBJECT_COMPONENT_REPAIR', subject_id='fake', object_id='fake',
                    component_id='missing', existing_object=True, attribute_scope='NONE')
        with self.assertRaisesRegex(ValueError, 'accepted existing object'):
            seed_scan_frontier(self.db, 's-invalid-repair', [task], 'd1', 't1', now=1)

    def test_claim_budget_closes_run_but_preserves_scan_frontier(self):
        create_scan(self.db, 's3', 'MIXED', 'd1', 't1', 5, 100, now=1)
        seed_scan_frontier(self.db, 's3', [dict(lane='MATERIAL', task_type='MATERIAL_OPTIONAL_RESEARCH',
            subject_id='m1', state=4, attribute_scope='E,nu,rho', priority=1, depth=0, family='wood')], 'd1', 't1', now=1)
        start_scan_run(self.db, 's3', 'r3', 1, now=2)
        first = claim_scan_route(self.db, 's3', 'r3', 'MATERIAL', 'worker', now=3)
        finish_scan_route(self.db, 's3', 'r3', first['business_key'], first['route_key'], first['token'],
                          'NO_PROGRESS', next_route='catalog-2', now=4)
        result = claim_scan_route(self.db, 's3', 'r3', 'MATERIAL', 'worker', now=5)
        self.assertEqual(result['status'], 'RUN_BUDGET_EXHAUSTED')
        self.assertEqual(result['scan_status'], 'READY')
        self.assertEqual(self.db.execute("SELECT count(*) FROM scan_routes WHERE scan_id='s3' AND status='PENDING'").fetchone()[0], 1)

    def test_rejected_route_has_distinct_terminal_state(self):
        create_scan(self.db, 's-rejected', 'MATERIAL', 'd1', 't1', 10, 100, now=1)
        seed_scan_frontier(self.db, 's-rejected', [dict(lane='MATERIAL', task_type='MATERIAL_OPTIONAL_RESEARCH',
            subject_id='m1', attribute_scope='E', family='wood')], 'd1', 't1', now=1)
        start_scan_run(self.db, 's-rejected', 'r-rejected', 2, now=2)
        route = claim_scan_route(self.db, 's-rejected', 'r-rejected', 'MATERIAL', 'worker', now=3)
        finished = finish_scan_route(self.db, 's-rejected', 'r-rejected', route['business_key'], route['route_key'],
                                     route['token'], 'REJECTED', error='route is not authoritative', now=4)
        self.assertEqual(finished['status'], 'REJECTED')

    def test_release_views_start_unverified(self):
        outputs = {'overview':'a'*64,'material_tree':'b'*64,'evidence_matrix':'c'*64}
        input_sha = '1'*64
        out = register_release_views(self.db, 'r1', input_sha, outputs, now=1)
        self.assertEqual(out['status'], 'BUILT')
        self.assertEqual(self.db.execute("SELECT count(*) FROM release_views WHERE status='BUILT'").fetchone()[0], 3)
        self.assertEqual(register_release_views(self.db, 'r1', input_sha, outputs, now=2)['status'], 'BUILT')
        verify_release_views(self.db, 'r1', input_sha, outputs, now=3)
        self.assertEqual(self.db.execute("SELECT count(*) FROM release_views WHERE status='VERIFIED'").fetchone()[0], 3)
        with self.assertRaisesRegex(ValueError, 'frozen'):
            register_release_views(self.db, 'r1', input_sha, dict(outputs, overview='d'*64), now=4)
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'frozen'):
            self.db.execute("UPDATE release_views SET status='BUILT' WHERE release_id='r1'")
        with self.assertRaisesRegex(sqlite3.IntegrityError, 'append-only'):
            self.db.execute("DELETE FROM release_views WHERE release_id='r1'")

    def test_clone_shadow_requires_exact_release_and_preserves_source(self):
        source_path = Path(self.tmp.name) / 'legacy.sqlite'
        source_db = harness.connect(source_path)
        harness.set_meta(source_db, 'release_id', 'r1')
        source_db.close()
        dest = Path(self.tmp.name) / 'clone.sqlite'
        result = clone_shadow(source_path, dest, 'r1')
        self.assertEqual(result['status'], 'V23_SHADOW_READY')
        source = sqlite3.connect(source_path)
        target = sqlite3.connect(dest)
        self.assertIsNone(source.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='scans'").fetchone())
        self.assertIsNotNone(target.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='scans'").fetchone())
        self.assertEqual(target.execute("PRAGMA journal_mode").fetchone()[0].lower(), 'delete')
        source.close(); target.close()
        readonly = sqlite3.connect(dest.resolve().as_uri() + '?mode=ro', uri=True)
        readonly.execute('PRAGMA query_only=ON')
        self.assertIsNotNone(readonly.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='scans'").fetchone())
        readonly.close()
        with self.assertRaises(ValueError):
            clone_shadow(source_path, Path(self.tmp.name) / 'bad.sqlite', 'wrong-release')


if __name__ == '__main__':
    unittest.main()
