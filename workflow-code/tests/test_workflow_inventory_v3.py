"""Structural inventory tests use synthetic chunks, never scientific approvals."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from rsi_harness import workflow_inventory_v3 as inv


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'source'
        self.site.mkdir()
        self.detail_rows = []
        self.card_rows = []
        for index in range(55):
            oid, cid, rid = 'O' + str(index), 'C' + str(index), 'R' + str(index)
            self.card_rows.append(dict(id=oid, fullShard=0, private_field='card retained'))
            source = dict(relation_id=rid, object_id=oid, component_id=cid, source_locator='original.json#/' + str(index), source_url='https://example.test/data', stream='source', review_status='HOLD', source_quote='private original quote')
            link = dict(source, stream='links', target_material_id='M1')
            self.detail_rows.append(dict(id=oid, dataset='synthetic', sourceId=str(index), components=[dict(component_id=cid, material_node_id='M1', admission_status='HOLD')], relations=[source, link], labels=[], options=[], original_private_field='must stay'))
        self.write_source()

    def write_source(self):
        def chunk(name, rows):
            raw = json.dumps(rows, ensure_ascii=False).encode()
            path = self.site / name
            path.parent.mkdir(exist_ok=True)
            path.write_bytes(gzip.compress(raw, mtime=0))
            return dict(url=name, sha256=hashlib.sha256(raw).hexdigest(), records=len(rows))
        cards = chunk('object-cards/0000.json.gz', self.card_rows)
        objects = chunk('objects/0000.json.gz', self.detail_rows)
        inv.write_json(self.site / 'snapshot.json', dict(id='S1', kind='REVIEWED_RESEARCH_SNAPSHOT', objects={'total': 55}, object_card_pages=[cards], object_pages=[objects]))
        inv.write_json(self.site / 'research.json', dict(meta={'releaseId': 'S1'}, nodes=[{'id': 'M1'}]))
        self.repin()

    def repin(self):
        inv.write_json(self.site / 'MANIFEST.json', dict(snapshot_id='S1', publication_type='REVIEWED_RESEARCH_SNAPSHOT', files={str(p.relative_to(self.site)): inv.sha(p) for p in self.site.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}))

    def test_export_groups_projections_and_preserves_private_input(self):
        output = self.root / 'out'
        source_hash = inv.sha(self.site / 'MANIFEST.json')
        result = inv.export_review_packets(self.site, output, 50)
        self.assertEqual(result['record_count'], 55)
        self.assertEqual(result['packet_count'], 2)
        index = inv.read_json(output / 'INDEX.json')
        self.assertEqual([p['records'] for p in index['packets']], [50, 5])
        self.assertTrue(index['packets'][-1]['partial_tail'])
        packet = inv.read_json(output / index['packets'][0]['path'])
        self.assertEqual(len(packet[0]['input_locators']), 2)
        self.assertEqual(packet[0]['source_locator'], 'original.json#/0')
        self.assertEqual(packet[0]['material_id'], 'M1')
        self.assertEqual(packet[0]['source']['inherited_statuses'][0]['review_status'], 'HOLD')
        self.assertNotIn('decision', packet[0])
        self.assertFalse(index['semantic_review_executed'])
        self.assertEqual(index['formal_relationships_admitted'], 0)
        self.assertEqual((output / 'private-inputs/objects/0000.json.gz').read_bytes(), (self.site / 'objects/0000.json.gz').read_bytes())
        self.assertEqual(inv.sha(self.site / 'MANIFEST.json'), source_hash)
        self.assertEqual(result['unique_ids']['relations'], 55)
        self.assertEqual(result['findings']['cards_without_expanded_details'], 0)
        self.assertEqual(result['structure_audit_status'], 'STRUCTURE_CHECKS_PASSED')
        other = self.root / 'other'
        inv.export_review_packets(self.site, other, 50)
        self.assertEqual((output / 'packets/packet-000000.json').read_bytes(), (other / 'packets/packet-000000.json').read_bytes())

    def test_hash_tamper_count_mismatch_and_traversal_fail_closed(self):
        path = self.site / 'objects/0000.json.gz'
        path.write_bytes(path.read_bytes() + b'tamper')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            inv.export_review_packets(self.site, self.root / 'tampered')
        self.assertFalse((self.root / 'tampered').exists())
        self.write_source()
        snapshot = inv.read_json(self.site / 'snapshot.json')
        snapshot['object_pages'][0]['records'] = 99
        inv.write_json(self.site / 'snapshot.json', snapshot)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'record count mismatch'):
            inv.export_review_packets(self.site, self.root / 'count')
        snapshot['object_pages'][0]['url'] = '../escape.json.gz'
        inv.write_json(self.site / 'snapshot.json', snapshot)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'snapshot index incomplete'):
            inv.export_review_packets(self.site, self.root / 'escape')

    def test_mixed_id_unsupported_shape_and_overwrite_rejected(self):
        research = inv.read_json(self.site / 'research.json')
        research['meta']['releaseId'] = 'OTHER'
        inv.write_json(self.site / 'research.json', research)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Mixed research'):
            inv.export_review_packets(self.site, self.root / 'mixed')
        self.write_source()
        self.root.joinpath('existing').mkdir()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            inv.export_review_packets(self.site, self.root / 'existing')
        for size in (49, 201, True):
            with self.assertRaisesRegex(ValueError, '50–200'):
                inv.export_review_packets(self.site, self.root / 'size', size)

    def test_full_audit_retains_orphans_duplicates_and_unexpanded_coverage(self):
        self.detail_rows[0]['relations'].append(dict(self.detail_rows[0]['relations'][0], component_id='MISSING-C', object_id='MISSING-O', canonical_material_id='MISSING-M'))
        self.detail_rows.append(self.detail_rows[0])
        self.card_rows.append(dict(id='NO-DETAIL', fullShard=7))
        self.write_source()
        result = inv.export_review_packets(self.site, self.root / 'findings')
        findings = result['findings']
        for key in ('orphan_object_keys', 'orphan_component_keys', 'orphan_material_keys', 'duplicate_relation_ids_within_stream', 'duplicate_detail_object_ids', 'cards_without_expanded_details', 'card_invalid_detail_shard'):
            self.assertGreater(findings[key], 0, key)
        self.assertFalse(result['semantic_review_executed'])
        self.assertEqual(result['detail_coverage']['unexpanded_card_objects'], 1)

    def test_categories_are_not_materials_and_unlisted_details_fail(self):
        research = inv.read_json(self.site / 'research.json')
        research['nodes'].append({'id': 'CATEGORY', 'nodeKind': 'CATEGORY'})
        inv.write_json(self.site / 'research.json', research)
        self.repin()
        result = inv.export_review_packets(self.site, self.root / 'category')
        self.assertEqual(result['unique_ids']['materials'], 1)
        self.assertEqual(result['unique_ids']['research_nodes'], 2)
        snapshot = inv.read_json(self.site / 'snapshot.json')
        snapshot['object_pages'] = []
        inv.write_json(self.site / 'snapshot.json', snapshot)
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Unlisted detail chunks'):
            inv.export_review_packets(self.site, self.root / 'unlisted')

    def test_missing_relations_do_not_invent_components_or_materials(self):
        self.detail_rows[0]['components'] = []
        self.detail_rows[0]['relations'] = []
        self.write_source()
        inv.export_review_packets(self.site, self.root / 'identity')
        packet = inv.read_json(self.root / 'identity/packets/packet-000000.json')
        record = next(r for r in packet if r['object_id'] == 'O0')
        self.assertIsNone(record['component_id'])
        self.assertIsNone(record['material_id'])
        self.assertIsNone(record['relation_id'])


if __name__ == '__main__':
    unittest.main()
