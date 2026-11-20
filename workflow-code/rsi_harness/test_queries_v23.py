import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

import harness
from queries_v23 import (bfs_material_frontier, four_state_counts,
                         material_queue, object_delivery_summary, object_material_coverage, object_queue,
                         release_view_consistency)
from runtime_v23 import seed_scan_frontier, create_scan


class QueryProjectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = harness.connect(Path(self.tmp.name) / "rsi.sqlite")
        self.db.executescript((Path(harness.__file__).parent / "schema_v23.sql").read_text())
        self.db.execute("INSERT OR REPLACE INTO meta(key,value) VALUES('epoch',?)", (json.dumps('E1'),))
        self.db.executemany("INSERT INTO nodes(id,name_cn,name_en,kind,family,granularity) VALUES(?,?,?,?,?,?)", [
            ('wood', '木材', 'Wood', 'MATERIAL', 'wood', 'COARSE'),
            ('oak', '橡木', 'Oak', 'MATERIAL', 'wood', 'FINE'),
            ('foam', '泡沫', 'Foam', 'MATERIAL', 'foam', 'COARSE'),
            ('empty', '空白', 'Empty Space', 'SPECIAL', 'special', 'SPECIAL'),
        ])
        self.db.executemany("INSERT INTO material_state VALUES(?,?,?,?,?,?,?,?)", [
            ('wood', 2, 0, 0, 0, '[]', json.dumps({'properties': {p: {'document_keys': 1} for p in ('E','nu','rho')}}), 'E1'),
            ('oak', 1, 1, 1, 1, '[]', json.dumps({'properties': {p: {'document_keys': 5} for p in ('E','nu','rho')}}), 'E1'),
            ('foam', 3, 1, 1, 1, json.dumps(['nu']), json.dumps({'properties': {p: {'document_keys': 0} for p in ('E','nu','rho')}}), 'E1'),
        ])
        self.db.execute("INSERT INTO objects(id,namespace,source_uid,name_cn,name_en,source_url,asset_url) VALUES('o1','test','1','椅子','Chair','u','a')")
        harness.set_meta(self.db, 'release_id', 'r1')
        self.db.execute("INSERT INTO components(object_id,id,kind,scope,basis) VALUES('o1','seat','PHYSICAL','seat','source')")
        self.db.execute("INSERT INTO material_links(id,object_id,component_id,material_id,scope,mode,accepted,basis) VALUES('l1','o1','seat','foam','seat','COEXISTS',1,'source')")

    def tearDown(self):
        self.db.close(); self.tmp.cleanup()

    def test_four_states_and_bfs(self):
        counts = four_state_counts(self.db)
        self.assertEqual(counts['states'], {'1': 1, '2': 1, '3': 1, '4': 0})
        self.assertEqual([r['material_id'] for r in bfs_material_frontier(self.db)], ['wood', 'foam', 'oak'])
        self.assertEqual([t['material_id'] for t in object_queue(self.db)], ['wood', 'oak'])

    def test_material_queue_prioritizes_existing_object_gap(self):
        queue = material_queue(self.db)
        self.assertEqual(queue[0]['material_id'], 'foam')
        self.assertEqual(queue[0]['attribute_scope'], 'nu')

    def test_object_coverage_does_not_hide_missing_or_unknown_scope(self):
        row = object_material_coverage(self.db)[0]
        self.assertEqual(row['status'], 'MATERIAL_PROPERTIES_INCOMPLETE')
        self.db.execute("UPDATE material_links SET material_id='empty' WHERE id='l1'")
        row = object_material_coverage(self.db)[0]
        self.assertEqual(row['status'], 'SPECIAL_DOMAIN_ONLY')

    def test_unmapped_component_blocks_object_material_completion(self):
        self.db.execute("INSERT INTO components(object_id,id,kind,scope,basis) VALUES('o1','frame','PHYSICAL','frame','source')")
        row = object_material_coverage(self.db)[0]
        self.assertEqual(row['status'], 'UNKNOWN_MATERIAL_SCOPE')
        self.assertEqual(row['unmapped_components'], 1)

    def test_existing_object_obligations_enter_repair_queue(self):
        self.db.execute("INSERT INTO obligations(id,object_id,component_id,kind,reason) VALUES('ob1','o1','seat','COMPONENT_MATERIAL','material label missing')")
        repairs = [t for t in object_queue(self.db) if t.get('obligation_id') == 'ob1']
        self.assertEqual(len(repairs), 1)
        self.assertEqual(repairs[0]['task_type'], 'OBJECT_LABEL_REPAIR')

    def test_query_plan_can_seed_runtime_without_losing_state_gate(self):
        create_scan(self.db, 'seed', 'MIXED', 'E1', 't1', 20, 100, now=1)
        tasks = material_queue(self.db) + object_queue(self.db)
        result = seed_scan_frontier(self.db, 'seed', tasks, 'E1', 't1', now=2)
        self.assertGreater(result['frontier_routes'], 0)
        self.assertEqual(self.db.execute("SELECT count(*) FROM scan_routes WHERE scan_id='seed' AND lane='OBJECT' AND task_type='OBJECT_DISCOVERY' AND subject_id='foam'").fetchone()[0], 0)

    def test_unreviewed_object_is_not_in_delivery_N(self):
        result = object_delivery_summary(self.db)
        self.assertEqual(result['status'], 'RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED')
        self.assertIsNone(result['N'])
        self.assertIsNone(result['R'])
        self.assertIsNone(result['C'])
        self.assertIsNone(result['RC'])
        self.assertEqual(result['blocked_reasons'], {'RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED': 1})

    def test_old_shadow_without_v23_audit_schema_reports_unknown_not_zero(self):
        db = harness.connect(Path(self.tmp.name) / 'legacy.sqlite')
        db.execute("INSERT INTO meta(key,value) VALUES('epoch',?)", (json.dumps('e'),))
        db.execute("INSERT INTO nodes(id,name_cn,name_en,kind) VALUES('m','木','Wood','MATERIAL')")
        db.execute("INSERT INTO material_state VALUES('m',4,0,0,0,'[\"E\",\"nu\",\"rho\"]','{}','e')")
        db.execute("INSERT INTO objects(id,namespace,source_uid,name_cn,name_en,source_url,asset_url) VALUES('o','ns','id','物','Object','u','a')")
        result = object_delivery_summary(db)
        self.assertEqual(result['status'], 'RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED')
        self.assertIsNone(result['N'])
        db.close()

    def test_reviewed_object_needs_positive_scope_and_all_materials_for_RC(self):
        self.db.execute("""INSERT INTO object_delivery_audits VALUES
            ('o1','r1','g1',1,1,1,'pack/object.glb','CC-BY','PUBLIC','PASS','dedup+asset review','{}')""")
        self.db.execute("""INSERT INTO object_scope_audits VALUES
            ('o1',1,'source enumerates complete chair parts',0,'source locator','HOLD','{}')""")
        self.db.execute("INSERT INTO object_geometry_groups VALUES('g1',1,'o1','mesh fingerprint + reviewed source identity','same shape','{}')")
        self.db.execute("""UPDATE material_state SET missing_json='[]' WHERE material_id='foam'""")
        # one recorded material with complete properties does not establish source scope completeness alone
        result = object_delivery_summary(self.db)
        self.assertEqual((result['N'], result['C']), (1, 1))
        self.assertEqual(result['R'], 0)
        self.assertEqual(result['RC'], 0)
        self.db.execute("UPDATE object_scope_audits SET review_status='PASS' WHERE object_id='o1'")
        self.assertEqual(object_delivery_summary(self.db)['R'], 1)
        # A material-relation gap blocks C, but does not undo the independent scope audit for R.
        self.db.execute("INSERT INTO obligations(id,object_id,component_id,kind,reason) VALUES('open','o1','seat','SOURCE_RELATION','unresolved source/material mapping')")
        result = object_delivery_summary(self.db)
        self.assertEqual((result['N'], result['C'], result['R'], result['RC']), (1, 0, 1, 0))

    def test_scope_audit_must_pass_independently(self):
        self.db.execute("""INSERT INTO object_delivery_audits VALUES
            ('o1','r1','g1',1,1,1,'pack/object.glb','CC-BY','PUBLIC','PASS','dedup+asset review','{}')""")
        self.db.execute("INSERT INTO object_geometry_groups VALUES('g1',1,'o1','reviewed comparison','basis','{}')")
        self.db.execute("INSERT INTO object_scope_audits VALUES('o1',1,'scope basis',0,'locator','HOLD','{}')")
        result = object_delivery_summary(self.db)
        self.assertEqual(result['R'], 0)

    def test_release_views_must_share_verified_snapshot(self):
        rows = [dict(release_id='r1', input_sha256='i1', view_name=name, status='VERIFIED')
                for name in ('overview', 'material_tree', 'evidence_matrix')]
        self.assertEqual(release_view_consistency(rows)['views'], sorted({r['view_name'] for r in rows}))
        with self.assertRaises(ValueError):
            release_view_consistency(rows[:-1])


if __name__ == '__main__':
    unittest.main()
