#!/usr/bin/env python3
"""Immutable website and explicit publication adapters; never invent review or approval.

Research snapshot validation is deliberately distinct from the original full-release
contracts. Browser reports belong outside the site and bind its exact manifest.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import http.server
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from urllib.request import urlopen, Request
from urllib.parse import unquote, urlsplit
from html.parser import HTMLParser

PROJECT = Path(__file__).resolve().parents[1]
PAGES = ('scaling.html', 'research.html', 'references.html', 'workflow.html')
PUBLISHER = PROJECT / 'audit/rsi_bulk_mapping_review_2026-11-19/snapshot_publication_v2/publish_reviewed_export.py'


def sha(path):
    with Path(path).open('rb') as handle:
        digest = hashlib.sha256()
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
        return digest.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def contained(root, name):
    """Reject traversal, alternate separators and every symlink component."""
    require(isinstance(name, str) and name and '\\' not in name, 'Unsafe manifest path')
    root = Path(root).resolve()
    parts = PurePosixPath(name)
    require(not parts.is_absolute() and '..' not in parts.parts and str(parts) == name, 'Path escape: ' + name)
    target = root / name
    require(target.resolve().is_relative_to(root), 'Path escape: ' + name)
    require(not any(p.is_symlink() for p in [target, *target.parents] if p.is_relative_to(root)), 'Symlink: ' + name)
    return target


def verify_manifest(site):
    site = Path(site).resolve()
    manifest_path = contained(site, 'MANIFEST.json')
    manifest = read_json(manifest_path)
    files = manifest.get('files')
    require(isinstance(files, dict) and files, 'Empty or invalid manifest')
    require('MANIFEST.json' not in files, 'Manifest cannot hash itself')
    for name, digest in files.items():
        path = contained(site, name)
        require(isinstance(digest, str) and re.fullmatch('[0-9a-f]{64}', digest), 'Invalid digest: ' + name)
        require(path.is_file() and sha(path) == digest, 'Manifest hash mismatch: ' + name)
    return manifest


class Resources(HTMLParser):
    def __init__(self):
        super().__init__()
        self.resources = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for key in ('src', 'href'):
            if attrs.get(key):
                self.resources.append(attrs[key])


def validate_site(site, *, full_release_root=None, report_dir=None):
    site = Path(site).resolve()
    manifest = verify_manifest(site)
    files = manifest['files']
    required = {*PAGES, 'snapshot.json', 'research.json', 'coverage.json', 'bootstrap.js', 'snapshot.js'}
    require(required <= files.keys(), 'Missing four-page resources: ' + ', '.join(sorted(required - files.keys())))
    snapshot = read_json(site / 'snapshot.json')
    snapshot_id = manifest.get('snapshot_id')
    require(snapshot_id and snapshot.get('id') == snapshot_id, 'Snapshot ID mismatch: snapshot')
    require(read_json(site / 'research.json').get('meta', {}).get('releaseId') == snapshot_id, 'Snapshot ID mismatch: research')
    require(read_json(site / 'coverage.json').get('releaseId') == snapshot_id, 'Snapshot ID mismatch: coverage')
    bootstrap = (site / 'bootstrap.js').read_text(encoding='utf-8')
    require(snapshot_id in bootstrap and 'snapshot.json' in bootstrap, 'Bootstrap is not bound to snapshot')
    navigation = (site / 'snapshot.js').read_text(encoding='utf-8')
    require(all(page in navigation for page in PAGES), 'Missing four-page navigation')
    for page in PAGES:
        parser = Resources()
        parser.feed((site / page).read_text(encoding='utf-8'))
        local = []
        for resource in parser.resources:
            url = urlsplit(resource)
            if url.scheme or url.netloc or not url.path:
                continue
            name = unquote(url.path)
            require(name in files, page + ' references unpinned resource: ' + name)
            contained(site, name)
            local.append(name)
        require({'bootstrap.js', 'snapshot.js'} <= set(local), page + ' misses snapshot binding')
    publication_type = manifest.get('publication_type')
    require(publication_type in ('REVIEWED_RESEARCH_SNAPSHOT', 'FULL_RELEASE'), 'Unknown publication type')
    require(snapshot.get('kind') == publication_type, 'Snapshot kind differs from publication type')
    parent = manifest.get('workflow_parent')
    if parent:
        parent_site = Path(parent['source_site']).resolve()
        require(sha(parent_site / 'MANIFEST.json') == parent['manifest_sha256'], 'Pinned parent changed')
        old = verify_manifest(parent_site)
        require(read_json(parent_site / 'snapshot.json') == snapshot, 'Presentation build changed data snapshot/completion flags')
        overrides = manifest.get('workflow_presentation_overrides', {})
        require(set(overrides) <= {'workflow.html', 'workflow.js', 'workflow.css'}, 'Invalid workflow presentation override')
        for name, digest in old['files'].items():
            if name != 'workflow-data.json' and name not in overrides:
                require(files.get(name) == digest, 'Presentation build changed pinned source: ' + name)
        require(all(files.get(name) == digest for name, digest in overrides.items()), 'Workflow override is not pinned')
    result = dict(status='PASS_SITE_SNAPSHOT_STRUCTURE', snapshot_id=snapshot_id,
                  publication_type=publication_type, manifest_sha256=sha(site / 'MANIFEST.json'),
                  file_count=len(files), full_completion_claimed=publication_type == 'FULL_RELEASE',
                  original_full_release_gates='NOT_RUN_RESEARCH_SNAPSHOT' if publication_type != 'FULL_RELEASE' else 'REQUIRED')
    if publication_type == 'FULL_RELEASE':
        require(full_release_root is not None and report_dir is not None, 'Full release requires original validators and isolated report directory')
        result['original_full_release_gates'] = run_full_release_gates(full_release_root, report_dir)
        require(all(item['passed'] for item in result['original_full_release_gates']), 'Original full-release gates blocked')
    return result


def build_site(source_site, out_site, workflow_config=None, presentation_overrides=None, extra_files=None):
    """Copy only hash-verified files; publish a new directory with an atomic rename."""
    source = Path(source_site).resolve()
    output = Path(out_site).absolute()
    require(not output.exists() and not output.is_symlink(), 'Target already exists; candidates are immutable')
    require(not output.resolve().is_relative_to(source), 'Candidate must be outside source site')
    manifest = verify_manifest(source)
    config_bytes = None
    if workflow_config is not None:
        config_bytes = Path(workflow_config).read_bytes()
        require(isinstance(json.loads(config_bytes), dict), 'Invalid workflow config')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.' + output.name + '-', dir=output.parent))
    try:
        for name in manifest['files']:
            target = contained(staging, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source / name, target)
        candidate = dict(manifest)
        candidate['files'] = dict(manifest['files'])
        candidate.update(production_write=False, publication_authorized=False,
                         workflow_parent=dict(source_site=str(source), manifest_sha256=sha(source / 'MANIFEST.json')))
        if config_bytes is not None:
            digest = hashlib.sha256(config_bytes).hexdigest()
            for name in ('workflow-data.json', 'workflow-config/' + digest + '.json'):
                path = contained(staging, name)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(config_bytes)
                candidate['files'][name] = digest
            candidate['workflow_config_sha256'] = digest
        overrides = presentation_overrides or {}
        require(set(overrides) <= {'workflow.html', 'workflow.js', 'workflow.css'}, 'Only workflow presentation files may be replaced')
        candidate['workflow_presentation_overrides'] = {}
        for name, source_path in overrides.items():
            raw = Path(source_path).read_bytes()
            contained(staging, name).write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            candidate['files'][name] = digest
            candidate['workflow_presentation_overrides'][name] = digest
        for name, source_path in (extra_files or {}).items():
            require(name.startswith('workflow-code/') or name == 'workflow-code.zip', 'Extra file must belong to the workflow code package')
            require(name not in manifest['files'], 'Cannot replace data resources using extra_files')
            target = contained(staging, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_path, target)
            candidate['files'][name] = sha(target)
        write_json(staging / 'MANIFEST.json', candidate)
        validate_site(staging)
        # Source verification also detects changes while copying.
        require(sha(source / 'MANIFEST.json') == candidate['workflow_parent']['manifest_sha256'], 'Source manifest changed during build')
        verify_manifest(source)
        require(not output.exists(), 'Target appeared during build')
        os.rename(staging, output)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return validate_site(output)


def run_full_release_gates(root, report_dir):
    root, report_dir = Path(root).resolve(), Path(report_dir).resolve()
    require(not report_dir.is_relative_to(root), 'Gate reports must be outside frozen release')
    report_dir.mkdir(parents=True, exist_ok=True)
    commands = [
        ('workflow_contract_v24.py', ['--root', str(root), '--out', str(report_dir / 'workflow_contract.json')], 'workflow_contract.json', 'PASS'),
        ('evidence_route_contract_v24.py', ['--root', str(root), '--out', str(report_dir / 'evidence_route_contract.json')], 'evidence_route_contract.json', 'PASS'),
        ('publication_preflight_v24.py', ['--root', str(root), '--queue-out', str(report_dir / 'release_queue.csv'), '--gate-out', str(report_dir / 'gate.json'), '--site-out', str(report_dir / 'site.json'), '--result-out', str(report_dir / 'preflight.json')], 'preflight.json', 'PASS_RSI_V24_PUBLICATION_PREFLIGHT')]
    results = []
    for script, args, report, expected in commands:
        proc = subprocess.run([sys.executable, str(PROJECT / 'rsi_harness' / script), *args], capture_output=True, text=True, timeout=900)
        payload = read_json(report_dir / report) if (report_dir / report).is_file() else {}
        status = payload.get('status', '')
        results.append(dict(validator=script, returncode=proc.returncode, status=status,
                            passed=proc.returncode == 0 and (status == expected or (expected == 'PASS' and status.startswith('PASS_'))),
                            stderr=proc.stderr[-1000:]))
    return results


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def browser_check(site, report_dir, *, cli=None):
    """Run real Chromium through installed Playwright CLI; outputs stay outside site."""
    site, report_dir = Path(site).resolve(), Path(report_dir).resolve()
    validation = validate_site(site)
    require(not report_dir.is_relative_to(site), 'Browser outputs must be outside immutable site')
    require(not report_dir.exists(), 'Browser report directory already exists')
    cli = str(cli or Path.home() / '.codex/skills/playwright/scripts/playwright_cli.sh')
    require(Path(cli).is_file() or shutil.which(cli), 'Playwright CLI unavailable')
    require(shutil.which('npx'), 'npx unavailable')
    report_dir.mkdir(parents=True)
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(QuietHandler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    session = 'rsi-' + validation['manifest_sha256'][:12] + '-' + str(os.getpid())
    prefix = [cli, '-s=' + session]
    def command(*args):
        result = subprocess.run([*prefix, *args], cwd=report_dir, capture_output=True, text=True, timeout=240)
        require(result.returncode == 0, 'Playwright CLI failed: ' + result.stderr[-1500:] + result.stdout[-1500:])
        return result.stdout
    rows = []
    try:
        base = 'http://127.0.0.1:' + str(server.server_port)
        command('open', base + '/' + PAGES[0])
        # A single browser function collects runtime events before each navigation.
        code = '''async (page) => {
 const rows=[]; let errors=[];
 page.on('pageerror', e=>errors.push(String(e)));
 page.on('console', m=>{if(m.type()==='error') errors.push(m.text())});
 page.on('response', r=>{if(r.status()>=400) errors.push('HTTP '+r.status()+' '+r.url())});
 for(const width of [1440,390]) for(const name of PAGES){
  errors=[]; await page.setViewportSize({width,height:1000});
  await page.goto(BASE+'/'+name); await page.waitForLoadState('networkidle');
  await page.waitForFunction(()=>window.DATASET_RELEASE && document.querySelector('.site-main-links a[aria-current="page"]'));
  const state=await page.evaluate(()=>({id:window.DATASET_RELEASE.id,overflow:Math.max(0,document.documentElement.scrollWidth-innerWidth),current:[...document.querySelectorAll('.site-main-links a[aria-current="page"]')].map(a=>new URL(a.href).pathname.split('/').pop()),links:[...document.querySelectorAll('.site-main-links a')].map(a=>new URL(a.href).pathname.split('/').pop()),mismatch:!!document.querySelector('.release-mismatch')}));
  const screenshot=name.replace('.html','')+'-'+width+'.png';
  await page.screenshot({path:OUT+'/'+screenshot,fullPage:true});
  rows.push({page:name,width,...state,errors:[...errors],screenshot});
 }
 return 'RSI_BROWSER_RESULT='+JSON.stringify(rows);
}'''.replace('PAGES', json.dumps(PAGES)).replace('BASE', json.dumps(base)).replace('OUT', json.dumps(str(report_dir)))
        raw = command('run-code', code)
        (report_dir / 'cli-output.txt').write_text(raw, encoding='utf-8')
        match = re.search(r'RSI_BROWSER_RESULT=(\[.*\])', raw)
        require(match is not None, 'Browser runner returned no structured observations')
        # CLI wraps strings as JSON, so parse its Result section when escaped.
        try:
            rows = json.loads(match.group(1))
        except json.JSONDecodeError:
            result_section = raw.split('### Result', 1)[-1].split('\n###', 1)[0].strip()
            decoded = json.loads(result_section)
            rows = json.loads(decoded.split('RSI_BROWSER_RESULT=', 1)[1])
        passed = len(rows) == 8 and all(r['id'] == validation['snapshot_id'] and r['overflow'] == 0 and not r['errors'] and not r['mismatch'] and r['current'] == [r['page']] and set(PAGES) <= set(r['links']) for r in rows)
        receipt = dict(schema='rsi-workflow-browser-receipt-v3', status='PASS' if passed else 'FAIL',
                       manifest_sha256=validation['manifest_sha256'], snapshot_id=validation['snapshot_id'],
                       runner='playwright-cli', observations=rows,
                       screenshots={r['screenshot']: sha(report_dir / r['screenshot']) for r in rows})
        require(sha(site / 'MANIFEST.json') == validation['manifest_sha256'], 'Manifest changed during browser QA')
        verify_manifest(site)
        write_json(report_dir / 'BROWSER_RECEIPT.json', receipt)
        return receipt
    except BaseException as error:
        write_json(report_dir / 'BROWSER_RECEIPT.json', dict(schema='rsi-workflow-browser-receipt-v3', status='FAIL', manifest_sha256=validation['manifest_sha256'], snapshot_id=validation['snapshot_id'], observations=rows, reason=str(error)))
        raise
    finally:
        try:
            command('close')
        finally:
            server.shutdown()
            server.server_close()


def prepare_publication(site, approval_path, approval_sha256, browser_receipt_path, expected_remote_parent, *, publisher_path=PUBLISHER, full_release_root=None, report_dir=None):
    """Read-only checks for the existing publisher's exact approval contract."""
    require(approval_path is not None and approval_sha256, 'Exact publication approval required')
    site = Path(site).resolve()
    approval_path = Path(approval_path).resolve()
    require(sha(approval_path) == approval_sha256, 'Approval hash mismatch')
    approval = read_json(approval_path)
    require(approval.get('schema') == 'rsi-reviewed-research-snapshot-publication-approval-v1' and approval.get('decision') == 'APPROVE_EXACT_REVIEWED_EXPORT', 'Exact reviewed-export approval required')
    require(approval.get('working_research_snapshot_publication_authorized') is True, 'Research publication not authorized')
    validation = validate_site(site, full_release_root=full_release_root, report_dir=report_dir)
    require(validation['publication_type'] == 'REVIEWED_RESEARCH_SNAPSHOT', 'Existing publisher supports reviewed snapshots only; full release needs its own approval mechanism')
    require(Path(approval.get('export_root', '')).resolve() == site and Path(approval.get('export_manifest_path', '')).resolve() == site / 'MANIFEST.json', 'Approval targets another export')
    require(approval.get('export_manifest_sha256') == validation['manifest_sha256'] and approval.get('snapshot_id') == validation['snapshot_id'], 'Approval does not bind exact candidate')
    require(re.fullmatch('[0-9a-f]{40}', expected_remote_parent or '') and approval.get('expected_remote_commit') == expected_remote_parent, 'Expected remote parent mismatch')
    require(approval.get('manifest_upload_name') == 'MANIFEST.json', 'Unexpected manifest upload name')
    review_path = Path(approval.get('independent_review_manifest_path', '')).resolve()
    require(review_path.is_file() and sha(review_path) == approval.get('independent_review_manifest_sha256'), 'Independent review hash mismatch')
    review = read_json(review_path)
    require(review.get('status') == 'PASS' and review.get('actionable_findings') == 0 and review.get('reviewed_export_manifest_sha256') == validation['manifest_sha256'], 'Independent review missing or not bound to candidate')
    # Role attestations are supplied by the independent reviewer, never generated here.
    require(review.get('reviewer') and review.get('author') and review['reviewer'] != review['author'], 'Independent reviewer identity required')
    normalized_sha = read_json(site / 'MANIFEST.json').get('normalized_bundle_sha256')
    if normalized_sha:
        require(review.get('scope') == 'DATA_AND_PRESENTATION' and review.get('normalized_bundle_sha256') == normalized_sha,
                'New dataset projection needs independent data review; code/presentation approval is insufficient')
    browser_path = Path(browser_receipt_path).resolve()
    require(browser_path.is_file() and sha(browser_path) == approval.get('browser_qa_sha256') and Path(approval.get('browser_qa_path', '')).resolve() == browser_path, 'Browser receipt is not approved')
    browser = read_json(browser_path)
    require(browser.get('schema') == 'rsi-workflow-browser-receipt-v3' and browser.get('status') == 'PASS' and browser.get('manifest_sha256') == validation['manifest_sha256'] and browser.get('snapshot_id') == validation['snapshot_id'], 'Browser receipt stale or failed')
    require({(r.get('page'), r.get('width')) for r in browser.get('observations', [])} == {(p, w) for p in PAGES for w in (1440, 390)}, 'Incomplete browser coverage')
    for row in browser.get('observations', []):
        require(row.get('id') == validation['snapshot_id'] and row.get('overflow') == 0 and not row.get('errors') and row.get('mismatch') is False and row.get('current') == [row['page']] and set(PAGES) <= set(row.get('links', [])), 'Browser observation failed')
        screenshot = contained(browser_path.parent, row.get('screenshot'))
        require(screenshot.is_file() and sha(screenshot) == browser.get('screenshots', {}).get(row['screenshot']), 'Browser screenshot hash mismatch')
    publisher_path = Path(publisher_path).resolve()
    require(publisher_path.is_file() and sha(publisher_path) == approval.get('publisher_sha256'), 'Publisher is not exactly approved')
    return dict(status='READY_FOR_EXPLICIT_PUBLICATION', production_write=False,
                manifest_sha256=validation['manifest_sha256'], expected_remote_parent=expected_remote_parent,
                approval_path=str(approval_path), approval_sha256=approval_sha256,
                publisher_path=str(publisher_path), browser_receipt_sha256=sha(browser_path))


def publish_site(site, approval_path, approval_sha256, browser_receipt_path, expected_remote_parent, *, execute=False, publisher_path=PUBLISHER, **kwargs):
    receipt = prepare_publication(site, approval_path, approval_sha256, browser_receipt_path, expected_remote_parent, publisher_path=publisher_path, **kwargs)
    if not execute:
        return receipt
    # Existing mechanism checks remote parent again before any remote mutation,
    # and before moving main; it uses a nonforce Git Data API update.
    require(sys.version_info >= (3, 11), 'Existing publisher requires Python 3.11+; rerun with python3.12')
    require(Path(publisher_path).resolve().parent == Path(approval_path).resolve().parent, 'Copy the exactly approved publisher into the new publication receipt directory; do not overwrite historical deployment receipts')
    proc = subprocess.run([sys.executable, str(publisher_path), '--approval', str(approval_path), '--approval-sha256', approval_sha256], capture_output=True, text=True, timeout=1800)
    require(proc.returncode == 0, 'Existing publisher failed: ' + proc.stderr[-2000:])
    return dict(receipt, status='PUBLISHER_EXECUTED_PENDING_INDEPENDENT_REMOTE_VERIFICATION', production_write=True, publisher_output=proc.stdout[-4000:])


def verify_remote(site, commit, base_url, *, timeout_seconds=300):
    """Verify every committed blob plus the served four-page entry resources."""
    manifest = verify_manifest(site)
    site = Path(site).resolve()
    require(re.fullmatch('[0-9a-f]{40}', commit or ''), 'Exact commit required')
    require(base_url == 'https://20161314.github.io/material-property-tree/', 'Unexpected website target')
    route = 'repos/20161314/material-property-tree/git/trees/' + commit + '?recursive=1'
    proc = subprocess.run(['gh', 'api', route], capture_output=True, text=True, timeout=90)
    require(proc.returncode == 0, 'Remote Git tree unavailable')
    tree = json.loads(proc.stdout)
    require(not tree.get('truncated'), 'Truncated remote Git tree')
    blobs = {row['path']: row['sha'] for row in tree['tree'] if row['type'] == 'blob'}
    pins = dict(manifest['files'], **{'MANIFEST.json': sha(site / 'MANIFEST.json')})
    for name in pins:
        raw = (site / name).read_bytes()
        expected = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blobs.get(name) == expected, 'Remote blob differs: ' + name)
    names = ['MANIFEST.json', *PAGES, 'snapshot.json', 'research.json', 'coverage.json', 'bootstrap.js', 'snapshot.js', 'workflow-data.json', 'workflow.js', 'workflow.css', 'workflow-code.zip']
    pending = set(names)
    deadline = time.monotonic() + min(600, max(1, timeout_seconds))
    failures = {}
    while pending and time.monotonic() < deadline:
        for name in list(pending):
            try:
                with urlopen(Request(base_url + name + '?v=' + commit, headers={'User-Agent': 'RSI-release-verifier/3', 'Cache-Control': 'no-cache'}), timeout=20) as response:
                    raw = response.read()
                if hashlib.sha256(raw).hexdigest() == pins[name]:
                    pending.remove(name)
                    failures.pop(name, None)
                else:
                    failures[name] = 'stale or different bytes'
            except Exception as error:
                failures[name] = str(error)
        if pending:
            time.sleep(min(10, max(0, deadline - time.monotonic())))
    return dict(status='PASS' if not pending else 'PENDING_PAGES_VERIFICATION', commit=commit,
                snapshot_id=manifest['snapshot_id'], manifest_sha256=sha(site / 'MANIFEST.json'),
                git_files_verified=len(pins), http_files_verified=len(names) - len(pending), pending=sorted(pending), failures=failures)


def rollback_publication(approval_path, approval_sha256, *, reason):
    """Restore the pinned prior tree with a new nonforce commit after a confirmed failure."""
    approval_path = Path(approval_path).resolve()
    require(sha(approval_path) == approval_sha256 and reason.strip(), 'Pinned approval and rollback reason required')
    approval = read_json(approval_path)
    require(approval.get('decision') == 'APPROVE_EXACT_REVIEWED_EXPORT', 'Publication approval required for rollback')
    target = approval_path.parent / 'ROLLBACK.json'
    require(not target.exists(), 'Rollback receipt already exists')
    deployment = read_json(approval_path.parent / 'DEPLOYMENT.json')
    require(deployment.get('approval_sha256') == approval_sha256, 'Deployment is not bound to this approval')
    current, previous = deployment.get('commit'), approval.get('expected_remote_commit')
    require(all(re.fullmatch('[0-9a-f]{40}', v or '') for v in (current, previous)), 'Pinned commits required')
    require(current != previous, 'No publication change to roll back')
    def api(route, method='GET', payload=None):
        command = ['gh', 'api', 'repos/20161314/material-property-tree/' + route, '--method', method]
        if payload is not None:
            command += ['--input', '-']
        result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None, capture_output=True, text=True, timeout=90)
        require(result.returncode == 0, 'Rollback API failed')
        return json.loads(result.stdout)
    require(api('git/ref/heads/main')['object']['sha'] == current, 'Remote advanced; rollback must be reviewed again')
    old = api('git/commits/' + previous)
    restored = api('git/commits', 'POST', dict(message='Restore last verified website: ' + reason, tree=old['tree']['sha'], parents=[current]))['sha']
    require(api('git/ref/heads/main')['object']['sha'] == current, 'Remote advanced during rollback')
    api('git/refs/heads/main', 'PATCH', dict(sha=restored, force=False))
    require(api('git/ref/heads/main')['object']['sha'] == restored, 'Rollback commit not visible')
    receipt = dict(status='RESTORED_PREVIOUS_TREE_PENDING_PAGES_VERIFICATION', previous_verified_commit=previous,
                   reverted_commit=current, rollback_commit=restored, force_push=False, reason=reason)
    write_json(target, receipt)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    build = sub.add_parser('build-site')
    build.add_argument('--source-site', required=True, type=Path)
    build.add_argument('--out-site', required=True, type=Path)
    build.add_argument('--workflow-config', type=Path)
    validate = sub.add_parser('validate-site')
    validate.add_argument('--site', required=True, type=Path)
    validate.add_argument('--full-release-root', type=Path)
    validate.add_argument('--report-dir', type=Path)
    browser = sub.add_parser('browser-check')
    browser.add_argument('--site', required=True, type=Path)
    browser.add_argument('--report-dir', required=True, type=Path)
    browser.add_argument('--cli')
    publish = sub.add_parser('publish-site')
    publish.add_argument('--site', required=True, type=Path)
    publish.add_argument('--approval', required=True, type=Path)
    publish.add_argument('--approval-sha256', required=True)
    publish.add_argument('--browser-receipt', required=True, type=Path)
    publish.add_argument('--expected-remote-parent', required=True)
    publish.add_argument('--execute', action='store_true')
    publish.add_argument('--publisher', type=Path, default=PUBLISHER)
    remote = sub.add_parser('verify-remote')
    remote.add_argument('--site', required=True, type=Path)
    remote.add_argument('--commit', required=True)
    remote.add_argument('--base-url', default='https://20161314.github.io/material-property-tree/')
    rollback = sub.add_parser('rollback-site')
    rollback.add_argument('--approval', type=Path, required=True)
    rollback.add_argument('--approval-sha256', required=True)
    rollback.add_argument('--reason', required=True)
    args = vars(parser.parse_args())
    action = args.pop('action')
    try:
        if action == 'build-site':
            result = build_site(**args)
        elif action == 'validate-site':
            result = validate_site(**args)
        elif action == 'browser-check':
            result = browser_check(**args)
        elif action == 'publish-site':
            args['approval_path'] = args.pop('approval')
            args['browser_receipt_path'] = args.pop('browser_receipt')
            args['publisher_path'] = args.pop('publisher')
            result = publish_site(**args)
        elif action == 'verify-remote':
            result = verify_remote(**args)
        else:
            result = rollback_publication(args['approval'], args['approval_sha256'], reason=args['reason'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('status') != 'FAIL' else 1
    except (ValueError, OSError, KeyError, subprocess.SubprocessError) as error:
        print(json.dumps(dict(status='BLOCKED', reason=str(error)), ensure_ascii=False))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
