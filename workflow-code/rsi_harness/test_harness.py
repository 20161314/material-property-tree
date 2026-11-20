"""Behavioral invariants for the two-subject research workflow; no production writes."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import tempfile
import time
import unittest

import harness as h


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'fixture.sqlite'
        self.db = h.connect(self.path)

    def tearDown(self):
        self.db.close()
        self.tmp.cleanup()

    def node(self, mid, kind='MATERIAL', family='test', flexible=0):
        self.db.execute('INSERT INTO nodes(id,name_cn,name_en,kind,family,flexible) VALUES(?,?,?,?,?,?)', (mid, mid, mid, kind, family, flexible))

    def edge(self, parent, child, kind='IS_A', accepted=1):
        up = int(kind == 'IS_A' and accepted == 1)
        self.db.execute('INSERT INTO edges VALUES(?,?,?,?,?,?,?,?)', (parent, child, kind, accepted, up, up, 'source-reviewed fixture', '{}'))

    def obj(self, mid, oid='object', component='part'):
        self.db.execute('INSERT OR IGNORE INTO objects VALUES(?,?,?,?,?,?,?,?,?,?)', (oid, 'fixture', oid, oid, oid, 'source', 'asset', None, 1, '{}'))
        self.db.execute('INSERT OR IGNORE INTO components VALUES(?,?,?,?,?,?)', (oid, component, 'SEMANTIC', 'source part', 'source', '{}'))
        self.db.execute('INSERT INTO material_links VALUES(?,?,?,?,?,?,?,?,?,?)', (oid + ':' + component + ':' + mid, oid, component, mid, 'source part', 'COEXISTING_SCOPES', '', 1, 'source', '{}'))

    def group(self, mid, gid=None, props=('E', 'nu', 'rho'), doc=None, verified=0, lineage=None, relation='DIRECT'):
        gid = gid or mid + '-group'
        doc = doc or gid + '-doc'
        self.db.execute('INSERT OR IGNORE INTO documents VALUES(?,?,?,?,?)', (doc, lineage, verified, 'source', '{}'))
        self.db.execute('INSERT INTO evidence_groups VALUES(?,?,?,?,?,?,?)', (gid, doc, mid, gid, 1, 'source-reported measurement', '{}'))
        for prop in props:
            value, unit = {'E': (1, 'GPa'), 'nu': (0, '1'), 'rho': (900, 'kg/m3')}[prop]
            self.db.execute('INSERT INTO observations VALUES(?,?,?,?,?,?,?)', (gid, prop, value, value, unit, 1, '{}'))
        self.db.execute('INSERT INTO group_material_refs VALUES(?,?,?,?,?)', (gid, mid, relation, 1, '{}'))

    def state(self, mid):
        return self.db.execute('SELECT state FROM material_state WHERE material_id=?', (mid,)).fetchone()[0]

    def test_four_states_and_reversible_transitions(self):
        for mid in 'abcd': self.node(mid)
        self.group('a'); self.obj('a'); self.group('b'); self.obj('c')
        h.recompute(self.db)
        self.assertEqual([self.state(x) for x in 'abcd'], [1, 2, 3, 4])
        self.obj('d', 'new-object')
        h.recompute(self.db); self.assertEqual(self.state('d'), 3)
        self.group('d'); h.recompute(self.db); self.assertEqual(self.state('d'), 1)
        self.db.execute("UPDATE evidence_groups SET accepted=0 WHERE source_material='d'")
        h.recompute(self.db); self.assertEqual(self.state('d'), 3)
        self.db.execute("UPDATE material_links SET accepted=0 WHERE material_id='d'")
        h.recompute(self.db); self.assertEqual(self.state('d'), 4)

    def test_only_true_subtype_rolls_up_and_objects_deduplicate(self):
        for mid in ('parent', 'child', 'sibling', 'part'): self.node(mid)
        self.edge('parent', 'child'); self.edge('parent', 'sibling'); self.edge('parent', 'part', 'PART_OF')
        self.obj('child'); self.obj('sibling'); self.group('child'); self.obj('part', 'part-object')
        h.recompute(self.db)
        row = self.db.execute("SELECT * FROM material_state WHERE material_id='parent'").fetchone()
        self.assertEqual((row['direct_objects'], row['effective_objects'], row['state']), (0, 1, 1))
        self.assertEqual(self.state('sibling'), 3)  # Parent data is never copied down.

    def test_unreviewed_edge_does_not_roll_up(self):
        self.node('parent'); self.node('child'); self.edge('parent', 'child', accepted=0); self.group('child'); self.obj('child')
        h.recompute(self.db); self.assertEqual(self.state('parent'), 4)

    def test_category_special_and_excluded_are_not_material_denominator(self):
        self.node('root', 'CATEGORY'); self.node('empty', 'SPECIAL'); self.node('liquid', 'EXCLUDED'); self.node('wood')
        h.recompute(self.db); self.assertEqual(h.summary(self.db)['material_count'], 1)

    def test_separate_sources_cover_but_do_not_create_complete_group(self):
        self.node('m')
        for p in h.PROPERTIES: self.group('m', 'g-' + p, (p,))
        h.recompute(self.db)
        stats = json.loads(self.db.execute('SELECT stats_json FROM material_state').fetchone()[0])
        self.assertEqual(self.state('m'), 2)
        self.assertEqual((stats['complete_groups'], stats['partial_groups']), (0, 3))
        self.assertEqual(stats['properties']['nu']['low'], 0)  # Zero is not missing.

    def test_same_document_many_groups_is_one_source(self):
        self.node('m')
        for i in range(5): self.group('m', 'g' + str(i), doc='one-paper', verified=1, lineage='one-experiment')
        h.recompute(self.db)
        p = json.loads(self.db.execute('SELECT stats_json FROM material_state').fetchone()[0])['properties']['E']
        self.assertEqual((p['value_groups'], p['document_keys'], p['verified_lineages']), (5, 1, 1))

    def test_family_only_reference_not_coverage(self):
        self.node('m'); self.group('m', relation='FAMILY_ONLY'); h.recompute(self.db); self.assertEqual(self.state('m'), 4)

    def test_cycle_is_rejected_but_nonsubtype_relationship_not_traversal(self):
        self.node('a'); self.node('b'); self.edge('a', 'b'); self.edge('b', 'a', 'PART_OF')
        h.recompute(self.db)
        self.db.execute("DELETE FROM edges WHERE kind='PART_OF'"); self.edge('b', 'a')
        with self.assertRaisesRegex(ValueError, 'cycle'): h.recompute(self.db)

    def test_dag_depth_uses_shortest_reviewed_path(self):
        for mid in ('root', 'a', 'b', 'c'): self.node(mid)
        self.edge('root', 'a'); self.edge('a', 'b'); self.edge('b', 'c'); self.edge('root', 'c')
        h.recompute(self.db)
        self.assertEqual(self.db.execute("SELECT depth FROM material_state WHERE material_id='c'").fetchone()[0], 1)

    def test_nonfinite_or_wrong_units_fail(self):
        self.node('m'); self.group('m')
        self.db.execute("UPDATE observations SET unit='Pa' WHERE property='E'")
        with self.assertRaisesRegex(ValueError, 'unit'): h.recompute(self.db)
        self.db.execute("UPDATE observations SET unit='GPa',high=? WHERE property='E'", (float('inf'),))
        with self.assertRaisesRegex(ValueError, 'finite'): h.recompute(self.db)

    def test_material_repair_priority_precedes_global_bfs(self):
        self.node('shallow4'); self.node('root', 'CATEGORY'); self.node('middle', 'CATEGORY'); self.node('deep3')
        self.edge('root', 'middle', 'DISPLAY'); self.edge('middle', 'deep3', 'DISPLAY'); self.obj('deep3')
        h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        self.assertEqual(h.claim(self.db, 'run', 'MATERIAL', 'worker')['subject_id'], 'deep3')

    def test_object_collectors_only_states_one_and_two(self):
        for mid in 'abcd': self.node(mid)
        self.group('a'); self.obj('a'); self.group('b'); self.obj('c'); h.recompute(self.db); h.plan(self.db)
        ids = {r[0] for r in self.db.execute("SELECT subject_id FROM tasks WHERE lane='OBJECT'")}
        self.assertEqual(ids, {'a', 'b'})

    def test_object_two_to_one_slots_and_bfs_within_tier(self):
        self.node('root', 'CATEGORY'); self.node('two-shallow'); self.node('two-deep'); self.node('one')
        self.edge('root', 'two-deep', 'IS_A')
        for mid in ('two-shallow', 'two-deep', 'one'): self.group(mid)
        self.obj('one'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        chosen = []
        for _ in range(3):
            t = h.claim(self.db, 'run', 'OBJECT', 'worker'); chosen.append(t['subject_id'])
            h.finish(self.db, t['id'], t['token'], 'DELIVERED', {'manifest': 'test'})
        self.assertEqual(chosen, ['two-shallow', 'two-deep', 'one'])

    def test_display_reparenting_does_not_change_scientific_bfs(self):
        for mid in ('root', 'child', 'ui'): self.node(mid)
        self.edge('root', 'child'); h.recompute(self.db)
        before = dict(self.db.execute('SELECT material_id,depth FROM material_state'))
        self.edge('ui', 'child', 'DISPLAY'); h.recompute(self.db)
        self.assertEqual(before, dict(self.db.execute('SELECT material_id,depth FROM material_state')))

    def test_five_documents_without_lineage_audit_finish_source_enhancement(self):
        self.node('m')
        for i in range(5): self.group('m', 'g' + str(i), doc='original-paper-' + str(i))
        h.recompute(self.db); h.plan(self.db)
        self.assertEqual(self.db.execute("SELECT count(*) FROM tasks WHERE task_type='ENHANCE_SOURCES'").fetchone()[0], 0)
        stats = json.loads(self.db.execute('SELECT stats_json FROM material_state').fetchone()[0])
        self.assertEqual(stats['properties']['E']['verified_lineages'], 0)

    def test_new_existing_object_gap_preempts_optional_work_in_active_run(self):
        self.node('a'); self.group('a'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        self.node('urgent'); self.obj('urgent'); h.recompute(self.db); h.plan(self.db)
        task = h.claim(self.db, 'run', 'MATERIAL', 'worker')
        self.assertEqual(task['subject_id'], 'urgent')
        self.assertEqual(self.db.execute("SELECT claims FROM runs WHERE id='run'").fetchone()[0], 1)

    def test_explicit_next_route_preserves_attempts_and_material_budget(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db)
        h.start_run(self.db, 'run', per_material=2)
        first = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, first['id'], first['token'], 'DELIVERED', {'manifest': 'first.json', 'next_route': 'official-catalog-2'})
        second = h.claim(self.db, 'run', 'OBJECT', 'worker')
        self.assertEqual(second['route_key'], 'official-catalog-2')
        with self.assertRaisesRegex(ValueError, 'previously uncompleted'):
            h.finish(self.db, second['id'], second['token'], 'DELIVERED', {'next_route': 'initial'})
        h.finish(self.db, second['id'], second['token'], 'DELIVERED', {'next_route': 'official-catalog-3'})
        self.assertEqual(h.claim(self.db, 'run', 'OBJECT', 'worker')['status'], 'NO_READY_TASK')
        history = [json.loads(r[0]) for r in self.db.execute("SELECT result_json FROM attempts WHERE outcome='DELIVERED' ORDER BY started")]
        self.assertEqual([x['route_key'] for x in history], ['initial', 'official-catalog-2'])
        h.start_run(self.db, 'next-run')
        self.assertEqual(h.claim(self.db, 'next-run', 'OBJECT', 'worker')['route_key'], 'official-catalog-3')

    def test_conflicting_accepted_identity_and_reviewed_alias_rejected(self):
        self.node('m'); self.obj('m', 'a'); self.obj('m', 'b')
        self.db.execute("INSERT INTO object_aliases VALUES('fixture','b','a','reviewed duplicate',1)")
        with self.assertRaisesRegex(ValueError, 'alias'): h.recompute(self.db)

    def test_next_route_survives_epoch_change_and_spaces_do_not_bypass_history(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        first = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, first['id'], first['token'], 'DELIVERED', {'next_route': ' catalog-2 '})
        self.node('unrelated'); h.recompute(self.db); h.plan(self.db)
        second = h.claim(self.db, 'run', 'OBJECT', 'worker')
        self.assertEqual(second['route_key'], 'catalog-2')
        with self.assertRaisesRegex(ValueError, 'previously uncompleted'):
            h.finish(self.db, second['id'], second['token'], 'DELIVERED', {'next_route': ' initial '})
        h.finish(self.db, second['id'], second['token'], 'DELIVERED', {})
        self.node('another'); h.recompute(self.db); h.plan(self.db)
        self.assertEqual(h.claim(self.db, 'run', 'OBJECT', 'worker')['status'], 'NO_READY_TASK')

    def test_review_feedback_resumes_done_task_without_resetting_budget(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db)
        h.start_run(self.db, 'run', max_claims=1)
        task = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, task['id'], task['token'], 'DELIVERED', {})
        with self.assertRaises(ValueError): h.schedule_route(self.db, task['id'], 'initial', 'repeat')
        with self.assertRaises(ValueError): h.schedule_route(self.db, task['id'], 'catalog', '')
        h.schedule_route(self.db, task['id'], 'review-feedback-catalog', 'Reviewer requested component-level scope')
        self.assertEqual(h.claim(self.db, 'run', 'OBJECT', 'worker')['status'], 'BUDGET_EXHAUSTED')
        h.start_run(self.db, 'next-run')
        self.assertEqual(h.claim(self.db, 'next-run', 'OBJECT', 'worker')['route_key'], 'review-feedback-catalog')

    def test_exact_fact_reversion_reactivates_pending_but_not_completed_routes(self):
        for mid in ('done', 'pending'):
            self.node(mid); self.group(mid)
        h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        first = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, first['id'], first['token'], 'DELIVERED', {})
        completed = first['subject_id']
        old_epoch = h.meta(self.db, 'epoch')
        self.db.execute("UPDATE observations SET accepted=0 WHERE property='nu'"); h.recompute(self.db); h.plan(self.db)
        self.db.execute("UPDATE observations SET accepted=1 WHERE property='nu'"); h.recompute(self.db); h.plan(self.db)
        self.assertEqual(h.meta(self.db, 'epoch'), old_epoch)
        second = h.claim(self.db, 'run', 'OBJECT', 'worker')
        self.assertEqual(second['status'], 'LEASED')
        self.assertNotEqual(second['subject_id'], completed)

    def test_active_reactivated_task_wins_over_newer_stale_history(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        self.db.execute("INSERT INTO documents(id) VALUES('temporary')"); h.recompute(self.db); h.plan(self.db)
        self.db.execute("DELETE FROM documents WHERE id='temporary'"); h.recompute(self.db); h.plan(self.db)
        task = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, task['id'], task['token'], 'DELIVERED', {})
        self.node('next-change'); h.recompute(self.db); h.plan(self.db)
        self.assertEqual(h.claim(self.db, 'run', 'OBJECT', 'worker')['status'], 'NO_READY_TASK')

    def test_claim_is_atomic_for_two_workers(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        def worker(i):
            db = h.connect(self.path)
            try: return h.claim(db, 'run', 'OBJECT', str(i))
            finally: db.close()
        with ThreadPoolExecutor(max_workers=2) as pool: results = list(pool.map(worker, range(2)))
        self.assertEqual(sum(r['status'] == 'LEASED' for r in results), 1)

    def test_expired_lease_token_cannot_complete(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run')
        now = time.time(); old = h.claim(self.db, 'run', 'OBJECT', 'w1', lease_seconds=1, now=now)
        new = h.claim(self.db, 'run', 'OBJECT', 'w2', now=now + 2)
        self.assertNotEqual(old['token'], new['token'])
        with self.assertRaisesRegex(ValueError, 'token'): h.finish(self.db, old['id'], old['token'], 'DELIVERED', {}, now=now + 2)

    def test_epoch_changes_invalidate_old_lease_and_preserve_run_budget(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'run', max_claims=1)
        t = h.claim(self.db, 'run', 'OBJECT', 'worker')
        self.db.execute("UPDATE nodes SET flexible=1 WHERE id='m'"); h.recompute(self.db); h.plan(self.db)
        with self.assertRaises(ValueError): h.finish(self.db, t['id'], t['token'], 'DELIVERED', {})
        self.assertEqual(h.claim(self.db, 'run', 'OBJECT', 'worker')['status'], 'BUDGET_EXHAUSTED')

    def test_summary_rejects_stale_state(self):
        self.node('m'); h.recompute(self.db); self.group('m')
        with self.assertRaisesRegex(ValueError, 'stale'): h.summary(self.db)

    def test_source_hash_change_invalidates_state(self):
        self.node('m'); self.group('m'); h.recompute(self.db)
        self.db.execute('UPDATE evidence_groups SET raw_json=?', ('{"source_sha256":"changed"}',))
        with self.assertRaisesRegex(ValueError, 'stale'): h.summary(self.db)

    def test_new_subject_waits_until_next_run(self):
        self.node('a'); self.group('a'); h.recompute(self.db); h.plan(self.db); h.start_run(self.db, 'r1')
        self.node('b'); self.group('b'); h.recompute(self.db); h.plan(self.db)
        t = h.claim(self.db, 'r1', 'OBJECT', 'worker')
        self.assertEqual(t['subject_id'], 'a')
        h.finish(self.db, t['id'], t['token'], 'DELIVERED', {})
        self.assertEqual(h.claim(self.db, 'r1', 'OBJECT', 'worker')['status'], 'NO_READY_TASK')
        h.start_run(self.db, 'r2')
        self.assertEqual(h.claim(self.db, 'r2', 'OBJECT', 'worker')['subject_id'], 'b')

    def test_review_guard_requires_exact_pin_and_independent_reviewer(self):
        pin = 'a' * 64
        h.register_proposal(self.db, 'batch', pin, 'collector')
        h.register_proposal(self.db, 'batch', pin, 'collector')
        with self.assertRaises(ValueError): h.register_review(self.db, 'batch', pin, 'collector', 'PASS', 'self')
        with self.assertRaises(ValueError): h.register_review(self.db, 'batch', 'b' * 64, 'reviewer', 'PASS', 'wrong pin')
        h.register_review(self.db, 'batch', pin, 'reviewer', 'HOLD', 'needs evidence')
        with self.assertRaises(ValueError): h.admission_guard(self.db, 'batch', pin)
        h.register_review(self.db, 'batch', pin, 'reviewer', 'PASS', 'fixed scope independently checked')
        self.assertTrue(h.admission_guard(self.db, 'batch', pin)['review_ready'])
        self.assertEqual(self.db.execute('SELECT count(*) FROM objects').fetchone()[0], 0)

    def test_plan_replay_is_idempotent_and_finish_never_promotes_facts(self):
        self.node('m'); self.group('m'); h.recompute(self.db); h.plan(self.db)
        count = self.db.execute('SELECT count(*) FROM tasks').fetchone()[0]; h.plan(self.db)
        self.assertEqual(count, self.db.execute('SELECT count(*) FROM tasks').fetchone()[0])
        h.start_run(self.db, 'run'); t = h.claim(self.db, 'run', 'OBJECT', 'worker')
        h.finish(self.db, t['id'], t['token'], 'DELIVERED', {'candidate_objects': 1000})
        self.assertEqual(self.db.execute('SELECT count(*) FROM objects').fetchone()[0], 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
