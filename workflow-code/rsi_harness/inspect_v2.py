#!/usr/bin/env python3
"""Read a pinned shadow snapshot and emit bounded RSI task context without writes."""
import argparse
import hashlib
import json
from pathlib import Path
import sqlite3

HERE = Path(__file__).resolve().parent


def sha(path):
    result = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def sealed_identity(database, expected_sha):
    """Verify a checkpointed, closed snapshot, including SQLite sidecars."""
    database = Path(database)
    for suffix in ('-wal', '-journal'):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise ValueError('Snapshot has a nonempty SQLite sidecar: ' + sidecar.name)
    before = database.stat()
    identity = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    if sha(database) != expected_sha:
        raise ValueError('Pinned database SHA does not match; do not overwrite the pointer')
    if identity(database.stat()) != identity(before):
        raise ValueError('Snapshot database changed during verification')
    for suffix in ('-wal', '-journal'):
        sidecar = Path(str(database) + suffix)
        if sidecar.exists() and sidecar.stat().st_size:
            raise ValueError('Snapshot acquired a nonempty SQLite sidecar: ' + sidecar.name)
    return identity(before)


def inspect(snapshot, limit=8, verify_inputs=False):
    if not 1 <= limit <= 50:
        raise ValueError('limit must be between 1 and 50')
    snapshot = Path(snapshot).resolve()
    pointer = json.loads(snapshot.read_text())
    database = (snapshot.parent / pointer['database']).resolve()
    if not database.is_relative_to(snapshot.parent) or not database.is_file():
        raise ValueError('Snapshot database must exist under its pointer directory')
    identity = sealed_identity(database, pointer['database_sha256'])
    # A frozen snapshot must not follow a concurrent writer's unpinned WAL.
    db = sqlite3.connect(database.as_uri() + '?mode=ro&immutable=1', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA query_only=ON')
    try:
        metadata = {row['key']: json.loads(row['value']) for row in db.execute('SELECT * FROM meta')}
        epoch = metadata.get('epoch')
        if epoch != pointer['epoch']:
            raise ValueError('Snapshot epoch mismatch')
        cache = metadata.get('fact_fingerprint_cache', {})
        generation = db.execute('SELECT generation FROM fact_revision WHERE id=1').fetchone()[0]
        if cache.get('epoch') != epoch or cache.get('generation') != generation:
            raise ValueError('Facts changed after state computation')
        if sha(snapshot.parent / 'SPEC.md') != cache.get('policy'):
            raise ValueError('Runtime SPEC changed; create a new validated snapshot')
        for name, expected in cache.get('implementation', {}).items():
            if sha(snapshot.parent / name) != expected:
                raise ValueError('Runtime implementation changed: ' + name)
        if not cache.get('implementation'):
            raise ValueError('Snapshot lacks runtime implementation pins')
        inputs = metadata.get('inputs', {})
        if hashlib.sha256(json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest() != cache.get('inputs_sha'):
            raise ValueError('Input pin map changed after state computation')
        stale = db.execute('SELECT count(*) FROM material_state WHERE epoch<>?', (epoch,)).fetchone()[0]
        if stale:
            raise ValueError('Mixed derived material epochs')
        if verify_inputs:
            root = snapshot.parent.parent
            for name, expected in inputs.items():
                source = (root / name).resolve()
                if not source.is_relative_to(root) or not source.is_file() or sha(source) != expected:
                    raise ValueError('Upstream input changed: ' + name)
        state_counts = {str(row['state']): row['n'] for row in db.execute('SELECT state,count(*) n FROM material_state GROUP BY state')}
        required = db.execute('SELECT count(*) FROM material_state WHERE effective_objects>0').fetchone()[0]
        covered = state_counts.get('1', 0)
        queues = {}
        for state, name in ((3, 'existing_object_material_gaps'), (2, 'covered_materials_without_objects'), (1, 'covered_material_object_expansion'), (4, 'optional_material_research')):
            rows = db.execute('SELECT s.*,n.name_cn,n.name_en,n.family,n.granularity FROM material_state s JOIN nodes n ON n.id=s.material_id WHERE s.state=? ORDER BY s.depth,n.family,s.material_id LIMIT ?', (state, limit))
            cards = []
            for row in rows:
                stats = json.loads(row['stats_json'])
                cards.append({'material_id': row['material_id'], 'name_cn': row['name_cn'], 'name_en': row['name_en'],
                              'state': state, 'scientific_bfs_depth': row['depth'], 'family': row['family'],
                              'granularity': row['granularity'], 'missing_properties': json.loads(row['missing_json']),
                              'direct_objects': row['direct_objects'], 'effective_objects': row['effective_objects'],
                              'properties': {key: {'value_groups': value['value_groups'],
                                                   'provisional_document_keys': value['document_keys']}
                                             for key, value in stats['properties'].items()}})
            queues[name] = cards
        obligations = [dict(row) for row in db.execute('SELECT id,object_id,component_id,kind,reason FROM obligations WHERE resolved=0 ORDER BY kind,id LIMIT ?', (limit,))]
        result = {'mode': 'READ_ONLY_PINNED_SHADOW_INSPECTION', 'snapshot_id': pointer['snapshot_id'], 'epoch': epoch,
                'upstream_files_checked': len(inputs) if verify_inputs else 0,
                'materials': sum(state_counts.values()), 'states': state_counts,
                'existing_object_material_coverage': {'covered': covered, 'required': required,
                                                     'percent': round(100 * covered / required, 2) if required else None},
                'source_object_identities': db.execute('SELECT count(*) FROM objects WHERE accepted=1').fetchone()[0],
                'component_keys': db.execute('SELECT count(*) FROM components').fetchone()[0],
                'unresolved_obligations': db.execute('SELECT count(*) FROM obligations WHERE resolved=0').fetchone()[0],
                'queue_samples': queues, 'obligation_sample': obligations,
                'limits': ['Samples are not claimed tasks; use the runtime claim protocol before collection.',
                           'Document keys are provisional, not verified original-document counts.',
                           'This shadow snapshot is not a production migration or a public website release.',
                           'Source identities and component keys are not globally deduplicated geometry or verified mechanical-part counts.']}
    finally:
        db.close()
    if sealed_identity(database, pointer['database_sha256']) != identity:
        raise ValueError('Snapshot database changed during inspection')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, default=HERE / 'CURRENT_SNAPSHOT.json')
    parser.add_argument('--limit', type=int, default=8)
    parser.add_argument('--verify-inputs', action='store_true')
    args = parser.parse_args()
    print(json.dumps(inspect(args.snapshot, args.limit, args.verify_inputs), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
