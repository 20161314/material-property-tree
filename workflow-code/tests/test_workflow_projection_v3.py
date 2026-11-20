"""Synthetic projection checks; no fixture can install or publish project data."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import tempfile
import unittest

from rsi_harness import workflow_projection_v3 as projection
from rsi_harness.workflow_data_v3 import example_bundle


def load_chunk(site, spec):
    return json.loads(gzip.decompress((site / spec['url']).read_bytes()))


class ProjectionTests(unittest.TestCase):
    def test_canonical_chinese_name_is_preserved(self):
        self.assertEqual(projection.label({'name_zh': '测试材料'}, '未命名材料'), '测试材料')

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / 'approved'
        self.source.mkdir()
        self.bundle = example_bundle()
        self.bundle['objects'][0].update(name_cn='测试物体', dataset='Synthetic fixture', source_uid='object1')
        self.bundle['materials'][0]['name_cn'] = '测试父材料'
        self.bundle['materials'][1]['name_cn'] = '测试子材料'
        for page in projection.PAGES:
            (self.source / page).write_text('<html><script src="bootstrap.js?v=old"></script><script src="snapshot.js?v=old"></script></html>')
        (self.source / 'bootstrap.js').write_text('OLD release')
        (self.source / 'snapshot.js').write_text(' '.join(projection.PAGES))
        (self.source / 'legacy.json').write_text('{"old_only_secret":"must not leak"}')
        projection.write_json(self.source / 'workflow-data.json', {'version': 'test', 'phases': [], 'steps': []})
        projection.write_json(self.source / 'MANIFEST.json', dict(snapshot_id='OLD', publication_type='REVIEWED_RESEARCH_SNAPSHOT', files={p.name: projection.sha(p) for p in self.source.iterdir() if p.name != 'MANIFEST.json'}))

    def build(self, bundle=None, name='candidate'):
        output = self.root / name
        result = projection.project_bundle_site(self.source, output, bundle or self.bundle, 'TEST-NEW')
        return output, result

    def test_run_export_projects_same_release_and_matching_counts(self):
        before = projection.sha(self.source / 'MANIFEST.json')
        site, result = self.build({'release_id': 'TEST-NEW', 'bundle': self.bundle, 'checkpoint': {'test': True}})
        snap, research, coverage = [projection.read_json(site / n) for n in ('snapshot.json', 'research.json', 'coverage.json')]
        self.assertEqual({snap['id'], research['meta']['releaseId'], coverage['releaseId']}, {'TEST-NEW'})
        self.assertEqual(snap['objects']['total'], 1)
        self.assertEqual(snap['materials']['total'], 2)
        self.assertEqual(snap['records'], {'complete': 1, 'partial': 0, 'total': 1})
        details = load_chunk(site, snap['object_pages'][0])
        cards = load_chunk(site, snap['object_card_pages'][0])
        self.assertEqual(len(details[0]['relations']), 1)
        self.assertEqual(cards[0]['reviewedMaterials'][0][0], self.bundle['relations'][0]['material_id'])
        self.assertEqual(details[0]['relations'][0]['target_material_id'], cards[0]['materials'][0][0])
        self.assertEqual(coverage['canonicalSummary'], snap['all_material_coverage'])
        self.assertFalse(any(snap['completion_flags'].values()))
        self.assertTrue(result['requires_independent_review'])
        self.assertFalse(result['publication_authorized'])
        self.assertEqual(projection.sha(self.source / 'MANIFEST.json'), before)
        self.assertFalse((site / 'legacy.json').exists())
        manifest = projection.verify_manifest(site)
        self.assertFalse(any('internal' in p.lower() for p in manifest['files']))
        self.assertTrue((self.root / 'candidate.internal/NORMALIZED_INPUT.json').is_file())
        self.assertNotIn('OLD release', (site / 'bootstrap.js').read_text())

    def test_hold_relations_and_evidence_remain_private(self):
        hold = dict(self.bundle['relations'][0], relation_id='PRIVATE-HOLD-REL', decision='HOLD', source_quote='PRIVATE-HOLD-QUOTE')
        self.bundle['relations'].append(hold)
        self.bundle['evidence'].append(dict(self.bundle['evidence'][0], record_id='PRIVATE-HOLD-EVD', source_group_id='private-group', decision='HOLD', source_quote='PRIVATE-HOLD-QUOTE'))
        site, _ = self.build()
        for name in projection.verify_manifest(site)['files']:
            path = site / name
            raw = gzip.decompress(path.read_bytes()) if name.endswith('.gz') else path.read_bytes()
            self.assertNotIn(b'PRIVATE-HOLD', raw, name)
        internal = projection.read_json(self.root / 'candidate.internal/INTERNAL_ROWS.json')
        self.assertEqual(internal['relations'][0]['relation_id'], 'PRIVATE-HOLD-REL')
        self.assertEqual(internal['evidence'][0]['record_id'], 'PRIVATE-HOLD-EVD')

    def test_three_properties_across_documents_never_form_complete_group(self):
        original = self.bundle['evidence'][0]
        self.bundle['evidence'] = [dict(original, record_id='PART-' + prop, document_id='DOC-' + prop, source_group_id='GROUP-' + prop, properties={prop: original['properties'][prop]}, conditions=None) for prop in ('E', 'nu', 'rho')]
        site, _ = self.build()
        snap = projection.read_json(site / 'snapshot.json')
        cov = projection.read_json(site / 'coverage.json')
        self.assertEqual(snap['records'], {'complete': 0, 'partial': 3, 'total': 3})
        target = next(t for t in cov['canonicalTargets'] if t['id'] == 'example-subtype')
        self.assertEqual(target['completeRecordCount'], 0)
        self.assertEqual(target['incompleteRecordCount'], 3)
        self.assertEqual(snap['object_material_coverage']['materialsWithAllThreeFromAnyGroup'], 2)
        records = load_chunk(site, next(iter(cov['recordDetailChunks'].values())))['recordsById']
        self.assertEqual({r['record_type'] for r in records.values()}, {'INCOMPLETE'})
        self.assertEqual({r['conditions'] for r in records.values()}, {'未报告条件'})
        self.assertEqual(target['E'], ['1.0', '1.0'])
        self.assertEqual(target['rho'], ['1000.0', '1000.0'])

    def test_parent_materials_do_not_inherit_downward_and_excluded_stays_private(self):
        self.bundle['evidence'][0]['material_id'] = 'example-solid'
        self.bundle['materials'].append({'material_id': 'EXCLUDED-LIQUID', 'scope': 'liquid', 'name_cn': 'private excluded'})
        site, _ = self.build()
        cov = projection.read_json(site / 'coverage.json')
        target = next(t for t in cov['canonicalTargets'] if t['id'] == 'example-subtype')
        self.assertEqual(target['recordCount'], 0)
        self.assertEqual(target['E'], ['', ''])
        self.assertNotIn('EXCLUDED-LIQUID', [t['id'] for t in cov['canonicalTargets']])

    def test_invalid_bundle_existing_output_and_source_reuse_are_rejected(self):
        bad = deepcopy(self.bundle)
        bad['relations'][0]['component_id'] = 'ORPHAN'
        with self.assertRaises(ValueError):
            self.build(bad)
        self.assertFalse((self.root / 'candidate').exists())
        self.assertFalse((self.root / 'candidate.internal').exists())
        self.build()
        with self.assertRaisesRegex(ValueError, 'exists'):
            self.build()
        with self.assertRaisesRegex(ValueError, 'new release ID'):
            projection.project_bundle_site(self.source, self.root / 'another', self.bundle, 'OLD')

    def test_export_version_mismatch_and_held_identity_filter(self):
        with self.assertRaisesRegex(ValueError, 'release_id must match'):
            self.build({'release_id': 'OTHER', 'bundle': self.bundle, 'checkpoint': {}})
        self.bundle['objects'].append({'object_id': 'PRIVATE-HELD-OBJECT', 'decision': 'HOLD', 'name': 'PRIVATE-IDENTITY'})
        self.bundle['objects'].append({'object_id': 'PRIVATE-CANDIDATE-OBJECT', 'decision': 'CANDIDATE', 'name': 'PRIVATE-CANDIDATE'})
        self.bundle['components'].append({'component_id': 'PRIVATE-HELD-COMP', 'object_id': 'PRIVATE-HELD-OBJECT', 'scope': 'WHOLE', 'source_locator': 'fixture:held'})
        self.bundle['components'].append({'component_id': 'PRIVATE-REJECTED-COMP', 'object_id': 'example-object', 'decision': 'REJECT', 'scope': 'WHOLE', 'source_locator': 'fixture:rejected'})
        for cid in ('PRIVATE-HELD-COMP', 'PRIVATE-REJECTED-COMP'):
            self.bundle['relations'].append(dict(self.bundle['relations'][0], relation_id='PRIVATE-REL-' + cid, component_id=cid))
        site, _ = self.build()
        snapshot = projection.read_json(site / 'snapshot.json')
        self.assertEqual(snapshot['objects']['total'], 1)
        self.assertEqual(snapshot['objects']['rows'], 1)
        detail = load_chunk(site, snapshot['object_pages'][0])[0]
        self.assertEqual(len(detail['relations']), 1)
        self.assertEqual(len(detail['components']), 1)
        for name in projection.verify_manifest(site)['files']:
            path = site / name
            raw = gzip.decompress(path.read_bytes()) if name.endswith('.gz') else path.read_bytes()
            self.assertNotIn(b'PRIVATE-HELD', raw, name)
            self.assertNotIn(b'PRIVATE-REJECTED', raw, name)
        internal = projection.read_json(self.root / 'candidate.internal/INTERNAL_ROWS.json')
        self.assertEqual(len(internal['objects']), 2)
        self.assertEqual(len(internal['components']), 2)
        self.assertEqual(len(internal['relations']), 2)

    def test_pinned_workflow_code_downloads_are_retained(self):
        downloads = self.source / 'workflow-code'
        downloads.mkdir()
        (downloads / 'workflow.py').write_text('# synthetic downloadable code\n')
        (downloads / 'contract.json').write_text('{"synthetic":true}')
        (self.source / 'workflow-code.zip').write_bytes(b'synthetic package fixture')
        html = (self.source / 'workflow.html').read_text()
        (self.source / 'workflow.html').write_text(html + '<a href="workflow-code.zip">Package</a><a href="workflow-code/workflow.py">Code</a><a href="workflow-code/contract.json">Contract</a>')
        manifest = projection.read_json(self.source / 'MANIFEST.json')
        for name in ('workflow.html', 'workflow-code/workflow.py', 'workflow-code/contract.json', 'workflow-code.zip'):
            manifest['files'][name] = projection.sha(self.source / name)
        projection.write_json(self.source / 'MANIFEST.json', manifest)
        site, _ = self.build()
        self.assertEqual((site / 'workflow-code/contract.json').read_bytes(), (downloads / 'contract.json').read_bytes())
        self.assertEqual((site / 'workflow-code/workflow.py').read_bytes(), (downloads / 'workflow.py').read_bytes())
        self.assertEqual((site / 'workflow-code.zip').read_bytes(), (self.source / 'workflow-code.zip').read_bytes())

    def test_empty_bundle_keeps_empty_object_chunks_and_reproducible_output(self):
        empty = {k: [] for k in projection.TABLE_KEYS}
        site, _ = self.build(empty)
        snapshot = projection.read_json(site / 'snapshot.json')
        self.assertEqual(load_chunk(site, snapshot['object_pages'][0]), [])
        self.assertEqual(snapshot['objects']['total'], 0)
        site2, _ = self.build(empty, 'candidate2')
        self.assertEqual((site / 'MANIFEST.json').read_bytes(), (site2 / 'MANIFEST.json').read_bytes())


if __name__ == '__main__':
    unittest.main()
