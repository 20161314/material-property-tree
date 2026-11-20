"""Mocked Git/HTTP boundaries only; these tests never publish anything."""
import hashlib
import io
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from rsi_harness import workflow_publication_v3 as pub


class RemoteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = self.root / 'site'
        self.site.mkdir()
        self.names = ['scaling.html', 'research.html', 'references.html', 'workflow.html', 'snapshot.json', 'research.json', 'coverage.json',
                      'bootstrap.js', 'snapshot.js', 'workflow-data.json', 'workflow.js', 'workflow.css', 'workflow-code.zip']
        for name in self.names:
            (self.site / name).write_text('synthetic ' + name)
        pub.write_json(self.site / 'MANIFEST.json', {'snapshot_id': 'SYNTHETIC', 'files': {n: pub.sha(self.site / n) for n in self.names}})
        self.blobs = [{'path': n, 'type': 'blob', 'sha': hashlib.sha1(b'blob ' + str(len((self.site / n).read_bytes())).encode() + b'\0' + (self.site / n).read_bytes()).hexdigest()} for n in [*self.names, 'MANIFEST.json']]

    def test_remote_verifies_committed_and_served_bytes(self):
        def served(request, **kwargs):
            name = request.full_url.split('/material-property-tree/', 1)[1].split('?', 1)[0]
            return io.BytesIO((self.site / name).read_bytes())
        result = SimpleNamespace(returncode=0, stdout=json.dumps({'tree': self.blobs, 'truncated': False}))
        with patch.object(pub.subprocess, 'run', return_value=result), patch.object(pub, 'urlopen', side_effect=served):
            receipt = pub.verify_remote(self.site, 'a' * 40, 'https://20161314.github.io/material-property-tree/')
        self.assertEqual(receipt['status'], 'PASS')
        self.assertEqual(receipt['git_files_verified'], 14)
        self.assertEqual(receipt['http_files_verified'], 14)

    def test_wrong_git_blob_blocks_before_http(self):
        self.blobs[0]['sha'] = '0' * 40
        result = SimpleNamespace(returncode=0, stdout=json.dumps({'tree': self.blobs}))
        with patch.object(pub.subprocess, 'run', return_value=result), patch.object(pub, 'urlopen') as http:
            with self.assertRaisesRegex(ValueError, 'blob differs'):
                pub.verify_remote(self.site, 'a' * 40, 'https://20161314.github.io/material-property-tree/')
            http.assert_not_called()

    def test_rollback_uses_new_nonforce_commit_and_stops_if_remote_advanced(self):
        approval = self.root / 'APPROVAL.json'
        pub.write_json(approval, {'decision': 'APPROVE_EXACT_REVIEWED_EXPORT', 'expected_remote_commit': 'b' * 40})
        digest = pub.sha(approval)
        pub.write_json(self.root / 'DEPLOYMENT.json', {'approval_sha256': digest, 'commit': 'a' * 40})
        calls = []
        responses = [{'object': {'sha': 'a' * 40}}, {'tree': {'sha': 'old-tree'}}, {'sha': 'c' * 40}, {'object': {'sha': 'a' * 40}}, {}, {'object': {'sha': 'c' * 40}}]
        def api(command, **kwargs):
            calls.append((command, kwargs.get('input')))
            return SimpleNamespace(returncode=0, stdout=json.dumps(responses.pop(0)))
        with patch.object(pub.subprocess, 'run', side_effect=api):
            receipt = pub.rollback_publication(approval, digest, reason='Synthetic test only')
        self.assertFalse(receipt['force_push'])
        payload = next(json.loads(value) for command, value in calls if 'PATCH' in command)
        self.assertEqual(payload, {'sha': 'c' * 40, 'force': False})
        with patch.object(pub.subprocess, 'run') as api_mock:
            with self.assertRaisesRegex(ValueError, 'receipt already'):
                pub.rollback_publication(approval, digest, reason='test')
            api_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
