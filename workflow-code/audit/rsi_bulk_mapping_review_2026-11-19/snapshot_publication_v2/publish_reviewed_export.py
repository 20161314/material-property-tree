"""Publish an independently reviewed export using nonforce GitHub Git Data API."""
import argparse
import base64
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPOSITORY = 'repos/20161314/material-property-tree/'


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def api(route, method='GET', payload=None):
    command = ['gh', 'api', REPOSITORY + route, '--method', method]
    if payload is not None:
        command += ['--input', '-']
    result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                            capture_output=True, text=True, timeout=90)
    if result.returncode:
        raise RuntimeError('GitHub API failed: ' + route + ': ' + result.stderr[:400])
    return json.loads(result.stdout)


def publish(approval_path, approval_sha):
    assert sha(approval_path) == approval_sha
    approval = json.loads(approval_path.read_text())
    assert approval['schema'] == 'rsi-reviewed-research-snapshot-publication-approval-v1'
    assert approval['decision'] == 'APPROVE_EXACT_REVIEWED_EXPORT'
    export = Path(approval['export_root']).resolve()
    manifest_path = Path(approval['export_manifest_path'])
    review_path = Path(approval['independent_review_manifest_path'])
    assert sha(manifest_path) == approval['export_manifest_sha256']
    assert sha(review_path) == approval['independent_review_manifest_sha256']
    manifest = json.loads(manifest_path.read_text())
    review = json.loads(review_path.read_text())
    assert review['status'] == 'PASS' and review['actionable_findings'] == 0
    assert review['reviewed_export_manifest_sha256'] == approval['export_manifest_sha256']
    assert manifest['snapshot_id'] == approval['snapshot_id']
    assert manifest['files'], 'No export files'
    assert {'index.html', 'scaling.html', 'research.html', 'references.html'} <= set(manifest['files'])
    assert manifest_path.resolve() == export / 'MANIFEST.json'
    assert approval['manifest_upload_name'] == 'MANIFEST.json'
    # The externally approved manifest cannot hash itself. Upload its exact
    # approved bytes separately so the public manifest link remains usable.
    upload_pins = dict(manifest['files'])
    assert 'MANIFEST.json' not in upload_pins
    upload_pins['MANIFEST.json'] = approval['export_manifest_sha256']
    for name, digest in upload_pins.items():
        path = export / name
        assert path.resolve().is_relative_to(export) and not path.is_symlink(), name
        assert path.is_file() and sha(path) == digest, name
    snapshot = json.loads((export / 'snapshot.json').read_text())
    assert snapshot['id'] == manifest['snapshot_id']
    assert snapshot['kind'] == 'REVIEWED_RESEARCH_SNAPSHOT'
    base = api('git/ref/heads/main')['object']['sha']
    assert base == approval['expected_remote_commit'], 'Remote changed: review before publishing'
    parent = api('git/commits/' + base)
    tree = api('git/trees/' + parent['tree']['sha'] + '?recursive=1')
    assert not tree.get('truncated'), 'Cannot compare incomplete remote tree'
    existing = {entry['path']: entry['sha'] for entry in tree['tree'] if entry['type'] == 'blob'}

    def upload(name):
        path = export / name
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == upload_pins[name], name
        digest = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if existing.get(name) == digest:
            return None
        result = api('git/blobs', 'POST', dict(content=base64.b64encode(raw).decode(), encoding='base64'))
        assert result['sha'] == digest, name
        return dict(path=name, mode='100644', type='blob', sha=digest)

    with ThreadPoolExecutor(max_workers=3) as pool:
        changes = [entry for entry in pool.map(upload, sorted(upload_pins)) if entry]
    assert api('git/ref/heads/main')['object']['sha'] == base, 'Remote changed during blob upload'
    if changes:
        # Keep individual Git tree requests bounded; only the final commit moves main.
        new_tree = parent['tree']['sha']
        for start in range(0, len(changes), 100):
            new_tree = api('git/trees', 'POST', dict(base_tree=new_tree, tree=changes[start:start + 100]))['sha']
        commit = api('git/commits', 'POST', dict(message='Publish reviewed object and material research snapshot',
                                               tree=new_tree, parents=[base]))['sha']
        assert api('git/ref/heads/main')['object']['sha'] == base
        api('git/refs/heads/main', 'PATCH', dict(sha=commit, force=False))
    else:
        commit = base
    assert api('git/ref/heads/main')['object']['sha'] == commit
    receipt = dict(status='COMMITTED_PENDING_PAGES_VERIFICATION', snapshot_id=manifest['snapshot_id'],
                   commit=commit, previous_commit=base, changed_files=len(changes),
                   approval_sha256=approval_sha, export_manifest_sha256=approval['export_manifest_sha256'],
                   independent_review_manifest_sha256=approval['independent_review_manifest_sha256'],
                   force_push=False, fully_complete_release_claimed=False)
    (HERE / 'DEPLOYMENT.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(json.dumps(receipt), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approval', required=True, type=Path)
    parser.add_argument('--approval-sha256', required=True)
    args = parser.parse_args()
    publish(args.approval, args.approval_sha256)
