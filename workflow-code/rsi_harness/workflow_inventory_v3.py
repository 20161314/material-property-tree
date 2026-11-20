#!/usr/bin/env python3
"""Export immutable review inputs from reviewed site chunks, without semantic review.

The supported snapshot uses object-cards (summaries) and objects (full detail)
arrays. Original compressed chunks stay in private-inputs. Review packets are
plain JSON arrays accepted by workflow_run_v3.py batch; they confer no approval.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile

try:
    from .workflow_publication_v3 import contained, read_json, require, sha, verify_manifest, write_json
except ImportError:
    from workflow_publication_v3 import contained, read_json, require, sha, verify_manifest, write_json

SENTINELS = {'', 'UNMAPPED', 'NOT_PROVIDED', 'NONE', 'UNKNOWN', 'NOT_APPLICABLE'}
MATERIAL_FIELDS = ('material_id', 'target_material_id', 'canonical_material_id', 'reviewed_label_material_id', 'assigned_material_id', 'material_node_id')


def identity(value):
    return value.strip() if isinstance(value, str) else ''


def material_id(row):
    return next((identity(row.get(key)) for key in MATERIAL_FIELDS if identity(row.get(key)) not in SENTINELS), '')


def stable_id(kind, *values):
    raw = json.dumps([kind, *values], ensure_ascii=False, separators=(',', ':')).encode()
    return 'SITE-' + kind.upper() + '-' + hashlib.sha256(raw).hexdigest()[:32]


def export_review_packets(site, out_dir, batch_size=100):
    """Read every pinned object chunk, emit bounded review arrays plus full audit.

    IDs, fields and source statuses are inherited, never upgraded. Counts describe
    source structure only. A source/link/label projection sharing a relation ID is
    one review unit; a conflicting material reference remains a separate variant.
    """
    require(type(batch_size) is int and 50 <= batch_size <= 200, 'batch_size must be 50–200')
    site, output = Path(site).resolve(), Path(out_dir).absolute()
    require(not output.exists() and not output.is_symlink(), 'Output already exists; export is immutable')
    require(not output.resolve().is_relative_to(site), 'Output must be outside reviewed source')
    manifest = verify_manifest(site)
    snapshot = read_json(site / 'snapshot.json')
    snapshot_id = snapshot.get('id')
    require(snapshot_id and snapshot_id == manifest.get('snapshot_id'), 'Mixed snapshot IDs')
    require(snapshot.get('kind') == 'REVIEWED_RESEARCH_SNAPSHOT' and manifest.get('publication_type') == snapshot['kind'], 'Reviewed research snapshot required')
    for required in ('snapshot.json', 'research.json'):
        require(required in manifest['files'], 'Unpinned input: ' + required)
    research = read_json(site / 'research.json')
    require(research.get('meta', {}).get('releaseId') == snapshot_id, 'Mixed research snapshot ID')
    require(isinstance(research.get('nodes'), list), 'Expected research.nodes array')
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix='.' + output.name + '-', dir=output.parent)).resolve()
    packets, inputs, pending = [], {}, []
    audit_counts = Counter()
    findings = Counter()
    issue_samples = {}
    db = None

    def issue(kind, locator):
        findings[kind] += 1
        sample = issue_samples.setdefault(kind, [])
        if len(sample) < 10:
            sample.append(locator)

    def preserve(name):
        require(name in manifest['files'], 'Unpinned input: ' + name)
        path = contained(site, name)
        require(sha(path) == manifest['files'][name], 'Input changed: ' + name)
        private_name = 'private-inputs/' + name
        if private_name not in inputs:
            target = contained(staging, private_name)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            inputs[private_name] = manifest['files'][name]
        return path

    def chunk(spec, expected_prefix):
        require(isinstance(spec, dict), 'Chunk specification must be an object')
        name = spec.get('url')
        require(isinstance(name, str) and name.startswith(expected_prefix) and name.endswith('.json.gz'), 'Unsupported chunk path: ' + str(name))
        raw = gzip.decompress(preserve(name).read_bytes())
        require(hashlib.sha256(raw).hexdigest() == spec.get('sha256'), 'Decompressed chunk hash mismatch: ' + name)
        rows = json.loads(raw)
        require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), 'Chunk must be an object array: ' + name)
        require(type(spec.get('records')) is int and len(rows) == spec['records'], 'Chunk record count mismatch: ' + name)
        return name, rows

    def flush():
        if not pending:
            return
        name = 'packets/packet-' + str(len(packets)).zfill(6) + '.json'
        write_json(staging / name, pending)
        packets.append(dict(path=name, sha256=sha(staging / name), records=len(pending),
                            partial_tail=len(pending) < 50, first_record_id=pending[0]['record_id'], last_record_id=pending[-1]['record_id']))
        pending.clear()

    def emit(record):
        pending.append(record)
        if len(pending) == batch_size:
            flush()

    try:
        (staging / 'packets').mkdir()
        (staging / 'ids').mkdir()
        (staging / 'private-inputs').mkdir()
        shutil.copyfile(site / 'MANIFEST.json', staging / 'private-inputs/SOURCE_MANIFEST.json')
        inputs['private-inputs/SOURCE_MANIFEST.json'] = sha(site / 'MANIFEST.json')
        preserve('snapshot.json')
        preserve('research.json')
        db = sqlite3.connect(str(staging / 'STRUCTURE.sqlite'))
        db.executescript('''
          CREATE TABLE objects(id TEXT PRIMARY KEY, shard INTEGER, locator TEXT);
          CREATE TABLE cards(id TEXT PRIMARY KEY, shard INTEGER, locator TEXT);
          CREATE TABLE components(id TEXT, object_id TEXT, PRIMARY KEY(id,object_id));
          CREATE TABLE relations(id TEXT, object_id TEXT, PRIMARY KEY(id,object_id));
          CREATE TABLE materials(id TEXT PRIMARY KEY);
          CREATE TABLE research_nodes(id TEXT PRIMARY KEY);
          CREATE TABLE references_material(id TEXT PRIMARY KEY);
          CREATE TABLE references_object(id TEXT PRIMARY KEY);
          CREATE TABLE packet_records(id TEXT PRIMARY KEY);
        ''')
        for node in research['nodes']:
            require(isinstance(node, dict) and identity(node.get('id')), 'Research node missing stable id')
            if db.execute('INSERT OR IGNORE INTO research_nodes VALUES(?)', (node['id'],)).rowcount == 0:
                issue('duplicate_material_ids', 'research.json#/nodes/' + node['id'])
            if node.get('nodeKind') not in ('CATEGORY', 'RESEARCH_CLASSIFICATION_CATEGORY', 'EXTERNAL_COLLECTION'):
                db.execute('INSERT OR IGNORE INTO materials VALUES(?)', (node['id'],))
        card_specs = snapshot.get('object_card_pages', [])
        detail_specs = snapshot.get('object_pages', [])
        require(isinstance(card_specs, list) and isinstance(detail_specs, list), 'Expected object page arrays')
        require({s.get('url') for s in card_specs} == {n for n in manifest['files'] if n.startswith('object-cards/') and n.endswith('.json.gz')}, 'Unlisted card chunks: snapshot index incomplete')
        require({s.get('url') for s in detail_specs} == {n for n in manifest['files'] if n.startswith('objects/') and n.endswith('.json.gz')}, 'Unlisted detail chunks: snapshot index incomplete')
        require(len({s.get('url') for s in card_specs}) == len(card_specs) and len({s.get('url') for s in detail_specs}) == len(detail_specs), 'Duplicate chunk specifications')
        for card_spec in card_specs:
            name, rows = chunk(card_spec, 'object-cards/')
            audit_counts['card_chunks_read'] += 1
            for position, row in enumerate(rows):
                audit_counts['card_rows'] += 1
                locator = name + '#/' + str(position)
                oid = identity(row.get('id'))
                require(oid, 'Card missing stable object id: ' + locator)
                shard = row.get('fullShard')
                if type(shard) is not int or not 0 <= shard < len(detail_specs):
                    issue('card_invalid_detail_shard', locator)
                    shard = -1
                if db.execute('INSERT OR IGNORE INTO cards VALUES(?,?,?)', (oid, shard, locator)).rowcount == 0:
                    issue('duplicate_card_object_ids', locator)
        for shard, detail_spec in enumerate(detail_specs):
            name, rows = chunk(detail_spec, 'objects/')
            audit_counts['detail_chunks_read'] += 1
            for position, obj in enumerate(rows):
                object_locator = name + '#/' + str(position)
                oid = identity(obj.get('id'))
                require(oid, 'Detail missing stable object id: ' + object_locator)
                audit_counts['detail_object_rows'] += 1
                if db.execute('INSERT OR IGNORE INTO objects VALUES(?,?,?)', (oid, shard, object_locator)).rowcount == 0:
                    issue('duplicate_detail_object_ids', object_locator)
                components = obj.get('components', [])
                require(isinstance(components, list), 'components must be an array: ' + object_locator)
                component_ids = set()
                fallback_materials = {}
                for index, component in enumerate(components):
                    require(isinstance(component, dict), 'Invalid component row')
                    locator = object_locator + '/components/' + str(index)
                    cid = identity(component.get('component_id'))
                    audit_counts['component_material_rows'] += 1
                    if not cid:
                        issue('missing_component_ids', locator)
                        continue
                    component_ids.add(cid)
                    db.execute('INSERT OR IGNORE INTO components VALUES(?,?)', (cid, oid))
                    mid = material_id(component)
                    if mid:
                        fallback_materials.setdefault(cid, set()).add(mid)
                        db.execute('INSERT OR IGNORE INTO references_material VALUES(?)', (mid,))
                component_keys = Counter((identity(c.get('component_id')), material_id(c)) for c in components)
                for key, count in component_keys.items():
                    if count > 1:
                        findings['duplicate_component_material_rows'] += count - 1
                groups = {}
                seen_stream = set()
                for field in ('relations', 'labels', 'options'):
                    source_rows = obj.get(field, [])
                    require(isinstance(source_rows, list), field + ' must be an array: ' + object_locator)
                    for index, row in enumerate(source_rows):
                        require(isinstance(row, dict), 'Invalid ' + field + ' row')
                        locator = object_locator + '/' + field + '/' + str(index)
                        audit_counts[field + '_rows'] += 1
                        roid, cid = identity(row.get('object_id')), identity(row.get('component_id'))
                        if roid:
                            db.execute('INSERT OR IGNORE INTO references_object VALUES(?)', (roid,))
                        if roid and roid != oid:
                            issue('relation_object_key_mismatch', locator)
                        if not cid or cid not in component_ids:
                            issue('orphan_component_keys', locator)
                        rid = identity(row.get('relation_id'))
                        if field == 'options':
                            rid = stable_id('option', oid, cid, row.get('assignment_option_group_id'), material_id(row), row.get('assignment_relation'))
                        if not rid:
                            issue('missing_relation_ids', locator)
                            rid = stable_id('source-row', oid, cid, field, index, row)
                        if field == 'relations':
                            db.execute('INSERT OR IGNORE INTO relations VALUES(?,?)', (rid, oid))
                            stream_key = (identity(row.get('stream')) or field, rid)
                            if stream_key in seen_stream:
                                issue('duplicate_relation_ids_within_stream', locator)
                            seen_stream.add(stream_key)
                        mid = material_id(row)
                        if mid:
                            db.execute('INSERT OR IGNORE INTO references_material VALUES(?)', (mid,))
                        source_locator = identity(row.get('source_locator')) or identity(row.get('mapping_source_locator')) or identity(row.get('source_record_locator'))
                        source_url = identity(row.get('source_url')) or identity(row.get('mapping_source_url'))
                        status = {k: v for k, v in row.items() if k in ('review_status', 'mapping_status', 'installation_status', 'label_status', 'admission_status', 'relation_type', 'assignment_relation', 'composition_status')}
                        groups.setdefault((field == 'options', rid, cid), []).append(dict(material_id=mid, source_locator=source_locator, source_url=source_url, source_sha256=identity(row.get('source_sha256')), input_locator='private-inputs/' + locator, status=status))
                covered_components = set()
                for (is_option, rid, cid), variants in sorted(groups.items()):
                    covered_components.add(cid)
                    mids = sorted({v['material_id'] for v in variants if v['material_id']})
                    if not mids:
                        mids = sorted(fallback_materials.get(cid, ())) or ['']
                    if len(mids) > 1:
                        issue('relation_multiple_material_references', object_locator + '/relation_id=' + rid)
                    for mid in mids:
                        applicable = [v for v in variants if not v['material_id'] or v['material_id'] == mid]
                        locators = sorted({v['source_locator'] for v in applicable if v['source_locator']})
                        if not locators:
                            issue('missing_original_source_locator', object_locator + '/relation_id=' + rid)
                        source_loc = locators[0] if locators else applicable[0]['input_locator']
                        record = dict(record_id=stable_id('review', snapshot_id, oid, cid, rid, mid), object_id=oid, component_id=cid,
                                      material_id=mid or None, relation_id=rid, source_locator=source_loc,
                                      allowed_source_locators=locators, source=dict(dataset=obj.get('dataset'), source_uid=obj.get('sourceId'),
                                      urls=sorted({v['source_url'] for v in applicable if v['source_url']}), sha256=sorted({v['source_sha256'] for v in applicable if v['source_sha256']}), inherited_statuses=[v['status'] for v in applicable]),
                                      input_locators=sorted({v['input_locator'] for v in applicable}))
                        if db.execute('INSERT OR IGNORE INTO packet_records VALUES(?)', (record['record_id'],)).rowcount == 0:
                            issue('duplicate_review_record_ids', object_locator)
                            continue
                        emit(record)
                # Preserve objects/components that have no relation as identity-review inputs.
                for cid in sorted(component_ids - covered_components) or ([''] if not component_ids and not groups else []):
                    record = dict(record_id=stable_id('identity', snapshot_id, oid, cid), object_id=oid, component_id=cid or None,
                                  material_id=None, relation_id=None, source_locator=object_locator,
                                  source=dict(dataset=obj.get('dataset'), source_uid=obj.get('sourceId')),
                                  input_locators=['private-inputs/' + object_locator])
                    if db.execute('INSERT OR IGNORE INTO packet_records VALUES(?)', (record['record_id'],)).rowcount:
                        emit(record)
        flush()
        # SQL performs full joins after every detail chunk has been traversed.
        checks = {
            'cards_without_expanded_details': 'SELECT c.id FROM cards c LEFT JOIN objects o ON o.id=c.id WHERE o.id IS NULL',
            'details_without_cards': 'SELECT o.id FROM objects o LEFT JOIN cards c ON c.id=o.id WHERE c.id IS NULL',
            'card_detail_shard_mismatch': 'SELECT c.id FROM cards c JOIN objects o ON c.id=o.id WHERE c.shard<>o.shard',
            'orphan_object_keys': 'SELECT r.id FROM references_object r LEFT JOIN objects o ON o.id=r.id WHERE o.id IS NULL',
            'orphan_material_keys': 'SELECT r.id FROM references_material r LEFT JOIN materials m ON m.id=r.id WHERE m.id IS NULL',
            'component_ids_owned_by_multiple_objects': 'SELECT id FROM components GROUP BY id HAVING COUNT(*)>1',
            'relation_ids_owned_by_multiple_objects': 'SELECT id FROM relations GROUP BY id HAVING COUNT(*)>1'}
        for kind, sql in checks.items():
            findings[kind] = db.execute('SELECT COUNT(*) FROM (' + sql + ')').fetchone()[0]
            issue_samples[kind] = [r[0] for r in db.execute(sql + ' LIMIT 10')]
        counts = {kind: db.execute('SELECT COUNT(DISTINCT id) FROM ' + table).fetchone()[0] for kind, table in [('objects', 'objects'), ('components', 'components'), ('relations', 'relations'), ('materials', 'materials'), ('referenced_materials', 'references_material'), ('research_nodes', 'research_nodes'), ('packet_records', 'packet_records')]}
        id_files = {}
        for kind, table in [('objects', 'objects'), ('components', 'components'), ('relations', 'relations'), ('materials', 'materials')]:
            path = staging / 'ids' / (kind + '.jsonl')
            with path.open('w', encoding='utf-8') as handle:
                for (value,) in db.execute('SELECT DISTINCT id FROM ' + table + ' ORDER BY id'):
                    handle.write(json.dumps(value, ensure_ascii=False) + '\n')
            id_files['ids/' + kind + '.jsonl'] = sha(path)
        expected = snapshot.get('objects', {}).get('total')
        if type(expected) is int and expected != counts['objects']:
            issue('snapshot_object_count_mismatch', 'snapshot.json#/objects/total')
        db.commit()
        db.close()
        db = None
        audit = dict(schema='rsi-site-structure-audit-v3', status='STRUCTURE_FINDINGS' if any(findings.values()) else 'STRUCTURE_CHECKS_PASSED',
                     semantic_review_executed=False, source_snapshot_id=snapshot_id, unique_ids=counts, rows=dict(audit_counts),
                     findings=dict(findings), finding_samples=issue_samples, id_files=id_files,
                     detail_coverage=dict(all_listed_detail_chunks_read=audit_counts['detail_chunks_read'] == len(detail_specs),
                                          listed_detail_chunks=len(detail_specs), expanded_objects=counts['objects'],
                                          unexpanded_card_objects=findings['cards_without_expanded_details']),
                     counting_scope='source/link/label projections sharing relation_id are one logical relation; options are separate review units; materials exclude explicit categories/external collections; components are source identities, not mechanical BOM claims')
        write_json(staging / 'STRUCTURE_AUDIT.json', audit)
        require(sha(site / 'MANIFEST.json') == inputs['private-inputs/SOURCE_MANIFEST.json'], 'Source manifest changed during export')
        verify_manifest(site)
        index = dict(schema='rsi-site-review-packet-index-v3', status='REVIEW_INPUTS_READY_NOT_EXECUTED',
                     source_snapshot_id=snapshot_id, source_site=str(site), source_manifest_sha256=sha(site / 'MANIFEST.json'),
                     batch_size=batch_size, record_count=counts['packet_records'], packet_count=len(packets), packets=packets,
                     private_inputs=inputs, audit_path='STRUCTURE_AUDIT.json', audit_sha256=sha(staging / 'STRUCTURE_AUDIT.json'),
                     structure_database_sha256=sha(staging / 'STRUCTURE.sqlite'), id_files=id_files,
                     input_locator_format='private-inputs gzip JSON filename followed by #/ RFC6901 array pointer; resolve from export root',
                     semantic_review_executed=False, source_modified=False, formal_relationships_admitted=0,
                     source_status_policy='Inherited statuses are source facts only; every output is unreviewed input, never a new PASS or formal assignment.')
        write_json(staging / 'INDEX.json', index)
        require(not output.exists(), 'Output appeared during export')
        os.rename(staging, output)
        return dict(status=index['status'], output=str(output), index_sha256=sha(output / 'INDEX.json'),
                    packet_count=len(packets), record_count=index['record_count'], structure_audit_status=audit['status'],
                    unique_ids=counts, findings=dict(findings), detail_coverage=audit['detail_coverage'], semantic_review_executed=False)
    except BaseException:
        if db:
            db.close()
        shutil.rmtree(staging, ignore_errors=True)
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--site', required=True, type=Path)
    parser.add_argument('--out-dir', required=True, type=Path)
    parser.add_argument('--batch-size', type=int, default=100)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(export_review_packets(args.site, args.out_dir, args.batch_size), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.exit(2, 'inventory export blocked: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
