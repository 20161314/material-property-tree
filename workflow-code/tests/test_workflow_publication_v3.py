"""Publication boundaries: immutable source, exact pins and no implicit approval."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

MODULE = Path(__file__).resolve().parents[1] / 'rsi_harness/workflow_publication_v3.py'
spec = importlib.util.spec_from_file_location('publication', MODULE)
pub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pub)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'approved'
        self.site.mkdir()
        snapshot = dict(id='REVIEWED-1', kind='REVIEWED_RESEARCH_SNAPSHOT', completion_flags={'global_geometry_deduplicated': False})
        for name, value in [('snapshot.json', snapshot), ('research.json', {'meta': {'releaseId': snapshot['id']}}), ('coverage.json', {'releaseId': snapshot['id']}), ('INPUT_PINS.json', {'five_core_inputs': 'unchanged'}), ('workflow-data.json', {'version': 'old'})]:
            pub.write_json(self.site / name, value)
        (self.site / 'bootstrap.js').write_text("const version='REVIEWED-1';fetch('snapshot.json');")
        (self.site / 'snapshot.js').write_text(json.dumps(pub.PAGES))
        for page in (*pub.PAGES, 'index.html'):
            (self.site / page).write_text('<script src="bootstrap.js?v=1"></script><script src="snapshot.js?v=1"></script>')
        self.repin()

    def repin(self):
        pub.write_json(self.site / 'MANIFEST.json', dict(snapshot_id='REVIEWED-1', publication_type='REVIEWED_RESEARCH_SNAPSHOT', files={p.name: pub.sha(p) for p in self.site.iterdir() if p.name != 'MANIFEST.json'}))

    def test_build_retains_snapshot_source_and_versioned_config(self):
        before = pub.sha(self.site / 'MANIFEST.json')
        config = self.root / 'config.json'
        pub.write_json(config, {'version': '3', 'steps': []})
        candidate = self.root / 'candidate'
        result = pub.build_site(self.site, candidate, config)
        self.assertEqual(result['status'], 'PASS_SITE_SNAPSHOT_STRUCTURE')
        self.assertEqual(pub.sha(self.site / 'MANIFEST.json'), before)
        self.assertEqual((candidate / 'snapshot.json').read_bytes(), (self.site / 'snapshot.json').read_bytes())
        self.assertEqual((candidate / 'INPUT_PINS.json').read_bytes(), (self.site / 'INPUT_PINS.json').read_bytes())
        self.assertTrue((candidate / ('workflow-config/' + pub.sha(config) + '.json')).is_file())
        self.assertEqual(result['original_full_release_gates'], 'NOT_RUN_RESEARCH_SNAPSHOT')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            pub.build_site(self.site, candidate)

    def test_manifest_tamper_blocks_before_target_creation(self):
        (self.site / 'coverage.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'hash mismatch'):
            pub.build_site(self.site, self.root / 'candidate')
        self.assertFalse((self.root / 'candidate').exists())

    def test_path_escape_and_symlinks_rejected(self):
        manifest = pub.read_json(self.site / 'MANIFEST.json')
        outside = self.root / 'outside.json'
        outside.write_text('{}')
        for name in ('../outside.json', '/outside.json', 'a\\b'):
            manifest['files'][name] = pub.sha(outside)
            pub.write_json(self.site / 'MANIFEST.json', manifest)
            with self.assertRaises(ValueError):
                pub.verify_manifest(self.site)
            del manifest['files'][name]
        (self.site / 'linked.json').symlink_to(outside)
        manifest['files']['linked.json'] = pub.sha(outside)
        pub.write_json(self.site / 'MANIFEST.json', manifest)
        with self.assertRaises(ValueError):
            pub.verify_manifest(self.site)

    def test_mixed_snapshot_ids_rejected_even_with_valid_hashes(self):
        pub.write_json(self.site / 'coverage.json', {'releaseId': 'OTHER'})
        self.repin()
        with self.assertRaisesRegex(ValueError, 'Snapshot ID mismatch: coverage'):
            pub.validate_site(self.site)

    def test_unpinned_resource_and_missing_four_page_navigation_rejected(self):
        (self.site / 'workflow.html').write_text('<script src="../escape.js"></script>')
        self.repin()
        with self.assertRaisesRegex(ValueError, 'unpinned resource'):
            pub.validate_site(self.site)
        (self.site / 'workflow.html').write_text('<script src="bootstrap.js"></script><script src="snapshot.js"></script>')
        (self.site / 'snapshot.js').write_text('scaling.html research.html references.html')
        self.repin()
        with self.assertRaisesRegex(ValueError, 'four-page navigation'):
            pub.validate_site(self.site)

    def test_no_approval_never_invokes_publisher(self):
        with patch.object(pub.subprocess, 'run') as runner:
            with self.assertRaisesRegex(ValueError, 'approval required'):
                pub.publish_site(self.site, None, None, None, None, execute=True)
            runner.assert_not_called()

    def test_full_release_does_not_bypass_original_gates(self):
        snapshot = pub.read_json(self.site / 'snapshot.json')
        snapshot['kind'] = 'FULL_RELEASE'
        pub.write_json(self.site / 'snapshot.json', snapshot)
        self.repin()
        manifest = pub.read_json(self.site / 'MANIFEST.json')
        manifest['publication_type'] = 'FULL_RELEASE'
        pub.write_json(self.site / 'MANIFEST.json', manifest)
        with self.assertRaisesRegex(ValueError, 'original validators'):
            pub.validate_site(self.site)
        with patch.object(pub, 'run_full_release_gates', return_value=[{'passed': False}]) as gates:
            with self.assertRaisesRegex(ValueError, 'gates blocked'):
                pub.validate_site(self.site, full_release_root=self.root, report_dir=self.root / 'reports')
            gates.assert_called_once()

    def test_browser_report_cannot_mutate_site(self):
        with self.assertRaisesRegex(ValueError, 'outside immutable'):
            pub.browser_check(self.site, self.site / 'screenshots')

    def test_snapshot_or_completion_change_from_parent_rejected(self):
        candidate = self.root / 'candidate'
        pub.build_site(self.site, candidate)
        snapshot = pub.read_json(candidate / 'snapshot.json')
        snapshot['completion_flags']['global_geometry_deduplicated'] = True
        pub.write_json(candidate / 'snapshot.json', snapshot)
        manifest = pub.read_json(candidate / 'MANIFEST.json')
        manifest['files']['snapshot.json'] = pub.sha(candidate / 'snapshot.json')
        pub.write_json(candidate / 'MANIFEST.json', manifest)
        with self.assertRaisesRegex(ValueError, 'changed data snapshot/completion'):
            pub.validate_site(candidate)


if __name__ == '__main__':
    unittest.main()
