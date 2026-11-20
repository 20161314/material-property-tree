#!/usr/bin/env python3
"""Import one pinned release into a new shadow database; never mutate project ledgers."""
import argparse
import csv
import gzip
import importlib.util
import json
from pathlib import Path
import re
import sys
import zlib

from harness import connect, digest_file, encoded, set_meta, transaction, recompute, plan, export


def read_js(path):
    with gzip.open(path, 'rt') as f:
        text = f.read()
    return json.JSONDecoder().raw_decode(text[text.index('{'):])[0]


def read_csv(path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        yield from csv.DictReader(f)


def component_kind_from_inventory(row):
    """Classify representation only when the source explicitly supports WHOLE."""
    component_id = row.get('component_id', '')
    basis = row.get('component_basis', '').strip().casefold()
    if component_id.endswith('-WHOLE') or basis.startswith(
            'whole-object fallback from official 3d manifest; authored mesh/part structure not yet inspected'):
        return 'WHOLE'
    return 'UNCLASSIFIED'


ACCEPTED_CANONICAL_STATUSES = {
    'REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT',
    'ORIGINAL_REVIEWED_COARSE_NODE_PRESERVED_NO_PROPERTY_ASSIGNMENT',
}

SOURCE_ALIAS_COUNTS = {'SLATPHYS': 1533, 'NVIDIA-SIMREADY-LEGACY-PACKS': 1029}
SIMREADY_EXACT_ALIAS_STATUS = 'OFFICIAL_ZIP_ALIAS_CANONICAL_GVM_OBJECT'
SIMREADY_CANONICAL_ALIAS_STATUS = 'ALIAS_TO_GVM_CANONICAL_GEOMETRY'


def validate_alias_registry(rows):
    registry = {row['dataset_id']: row for row in rows}
    slat = registry.get('SLATPHYS')
    if not slat or slat['ingestion_status'] != 'alias_only_do_not_add' or slat['deduplication_key'] != 'Objaverse UID':
        raise ValueError('SLATPHYS registry must declare Objaverse-UID alias-only semantics')
    legacy = registry.get('NVIDIA-SIMREADY-LEGACY-PACKS')
    if (not legacy or legacy['deduplication_key'] != 'official pack URL plus canonical USD archive path'
            or legacy['ingested_unique_objects'] != str(SOURCE_ALIAS_COUNTS['NVIDIA-SIMREADY-LEGACY-PACKS'])):
        raise ValueError('Legacy SimReady registry must pin package-path alias identity and 1029 aliases')


def add_inventory_alias_claim(claims, row):
    memberships = set(filter(None, row.get('required_source_memberships', '').split(';')))
    oid = row.get('object_id', '')
    primary = row.get('required_source_primary', '')
    if 'SLATPHYS' in memberships:
        if primary != 'PIXIEVERSE' or not row.get('source_asset_id'):
            raise ValueError('SLATPHYS alias must resolve to an enumerated PIXIEVERSE Objaverse UID: ' + oid)
        key = ('SLATPHYS', row['source_asset_id'])
        claim = {'object_id': oid, 'reviewed': 1,
                 'basis': 'Official SLAT-Phys reuse declaration; exact PIXIEVerse/Objaverse source UID; alias-only, no additive geometry',
                 'raw': {'source_dataset': row.get('source_dataset', ''),
                         'required_source_primary': primary,
                         'source_asset_id': row['source_asset_id'],
                         'required_source_memberships': row.get('required_source_memberships', '')}}
        _merge_alias_claim(claims, key, claim)
    if 'NVIDIA-SIMREADY-LEGACY-PACKS' in memberships:
        if primary != 'VOMP-GVM-PUBLIC':
            raise ValueError('Legacy SimReady alias must resolve to a canonical GVM object: ' + oid)
        status = row.get('asset_alias_status', '')
        if status not in (SIMREADY_EXACT_ALIAS_STATUS, SIMREADY_CANONICAL_ALIAS_STATUS):
            raise ValueError('Unrecognized legacy SimReady alias status: ' + status)
        package_url = row.get('asset_package_url', '')
        archive_path = row.get('asset_archive_entry_path', '')
        if not package_url.startswith('https://') or not archive_path.startswith('Assets/'):
            raise ValueError('Legacy SimReady alias lacks an official package URL or USD archive path: ' + oid)
        alias_source_id = row.get('asset_alias_source_id', '')
        if status == SIMREADY_EXACT_ALIAS_STATUS and not alias_source_id.startswith('NVIDIA-SIMREADY::'):
            raise ValueError('Exact legacy SimReady alias lacks its source ID: ' + oid)
        if status == SIMREADY_CANONICAL_ALIAS_STATUS and alias_source_id != oid:
            raise ValueError('Canonical legacy SimReady alias does not point to this GVM object: ' + oid)
        # The registry defines identity by official ZIP URL plus canonical archive path.
        key = ('NVIDIA-SIMREADY-LEGACY-PACKS', package_url + '::' + archive_path)
        claim = {'object_id': oid, 'reviewed': int(status == SIMREADY_EXACT_ALIAS_STATUS),
                 'basis': status + '; official package URL plus exact USD archive path',
                 'raw': {'asset_alias_source_id': alias_source_id,
                         'asset_alias_status': status,
                         'asset_package_url': package_url,
                         'asset_archive_entry_path': archive_path}}
        _merge_alias_claim(claims, key, claim)


def _merge_alias_claim(claims, key, claim):
    previous = claims.get(key)
    if previous and previous['object_id'] != claim['object_id']:
        raise ValueError('Source alias maps to multiple canonical objects: ' + repr(key))
    if previous:
        previous['raw']['duplicate_claims'] = previous['raw'].get('duplicate_claims', 1) + 1
        previous['reviewed'] = max(previous['reviewed'], claim['reviewed'])
        if claim['basis'] not in previous['basis']:
            previous['basis'] += '; ' + claim['basis']
        return
    claims[key] = claim


def canonical_relation_accepted(row):
    return bool(row.get('canonical_material_id')) and row.get('canonical_mapping_status') in ACCEPTED_CANONICAL_STATUSES


def run(root, release_dir, out, export_dir, snapshot_id=None):
    out = out.resolve()
    if out.exists():
        raise ValueError('Output database already exists; use a new snapshot name')
    public = root / release_dir / 'public_export'
    files = {
        'phase1': public / 'phase1-ranges-data.js.gz',
        'tree': public / 'research-bootstrap.js.gz',
        'inventory': root / 'data/scaling_release_v1/object_component_inventory.csv',
        'options': root / 'data/current_two_table_delivery_v1/current_material_options.csv',
        'links': root / 'data/current_two_table_delivery_v1/reviewed_source_material_links.csv',
        'edges': root / 'audit/taxonomy_fine_leaf_adapter_2026-11-12/hierarchy_edges.csv',
        'secondary': root / 'audit/taxonomy_fine_leaf_adapter_2026-11-12/secondary_hierarchy_edges.csv',
        'source_nodes': root / 'audit/taxonomy_fine_leaf_adapter_2026-11-12/reviewed_material_nodes.csv',
        'scope_policy': root / 'data/material_scope_policy.json',
        'registry': root / 'dataset_registry.csv',
    }
    names = ['source_reported_material_relations.csv', 'official_bound_material_relations.csv',
             'approximate_component_material_relations.csv', 'intake_source_material_relations.csv']
    for name in names:
        files[name] = root / 'data/current_two_table_delivery_v1' / name
    inputs = {str(p.relative_to(root)): digest_file(p) for p in files.values()}
    validate_alias_registry(read_csv(files['registry']))
    phase, tree = read_js(files['phase1']), read_js(files['tree'])
    targets = {r['id']: r for r in phase['canonicalTargets']}
    active = set(targets)
    excluded_ids = set(json.loads(files['scope_policy'].read_text())['excluded_material_ids'])
    tree_nodes = {r['id']: r for r in tree['nodes']}
    source_nodes = {r['material_node_id']: r for r in read_csv(files['source_nodes'])}
    db = connect(out)
    diagnostics = {'unreviewed_material_parent_edges': [], 'source_uid_collisions': [],
                   'missing_group_references': [], 'granularity_pending': [], 'lineage_verification_pending': True}
    inventory_components = set()
    alias_claims = {}
    special_components = {}
    # Reuse the established source-cell interpreter. Some accepted partial rows only
    # store source strings, so reading numeric columns alone would create false gaps.
    parser_path = root / 'audit/material_range_phase1_v1/build_site_data.py'
    sys.path.insert(0, str(root / 'audit/material_property_record_accounting_v1'))
    spec = importlib.util.spec_from_file_location('rsi_pinned_source_parser', parser_path)
    parser = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(parser)
    files['numeric_parser'] = parser_path
    inputs[str(parser_path.relative_to(root))] = digest_file(parser_path)
    numeric_cache = {}
    def cached_review_csv(path):
        path = Path(path).resolve()
        if path not in numeric_cache:
            inputs[str(path.relative_to(root))] = digest_file(path)
            files['parser_dependency:' + str(path)] = path
            numeric_cache[path] = list(read_csv(path))
        return numeric_cache[path]
    parser.read_csv = cached_review_csv
    try:
        with transaction(db):
            evidence_release_id = phase.get('releaseId', 'FROZEN_RELEASE')
            set_meta(db, 'release_id', snapshot_id or evidence_release_id)
            set_meta(db, 'upstream_evidence_release_id', evidence_release_id)
            set_meta(db, 'inputs', inputs)
            set_meta(db, 'import_adapter', 'PINNED_EVIDENCE_AND_CURRENT_INVENTORY_SHADOW_NOT_PUBLICATION')
            # Display parents are traversal edges only. Reviewed subtype edges below grant rollup.
            nodes = {k: {**r, **targets.get(k, {})} for k, r in tree_nodes.items()}
            nodes.update({k: v for k, v in targets.items() if k not in nodes})
            for row in list(nodes.values()):
                parent = row.get('parentId')
                if parent and parent not in nodes:
                    nodes[parent] = {'id': parent, 'nameEn': parent, 'nameCn': parent, 'nodeKind': 'CATEGORY'}
            for mid, row in nodes.items():
                if mid in active:
                    kind = 'MATERIAL'
                    if mid.startswith('BUCKET-'):
                        granularity, identity_basis = 'BROAD', 'Existing explicitly unspecified identity bucket'
                    elif mid in source_nodes:
                        granularity, identity_basis = 'REFINED', source_nodes[mid].get('identity_basis', '')
                    else:
                        granularity, identity_basis = 'SOURCE_DEFINED_PENDING', 'Preserve published material identity; broad/fine review pending'
                        diagnostics['granularity_pending'].append(mid)
                else:
                    kind, granularity, identity_basis = 'CATEGORY', 'NOT_APPLICABLE', 'Published navigation container; not a material denominator'
                family = row.get('family', 'unclassified')
                flexible = int(family in ('rubber', 'foam', 'textile', 'leather', 'paper'))
                db.execute('INSERT INTO nodes(id,name_cn,name_en,kind,granularity,identity_basis,family,flexible,raw_json) VALUES(?,?,?,?,?,?,?,?,?)',
                           (mid, row.get('nameCn', mid), row.get('nameEn', mid), kind, granularity, identity_basis, family, flexible, encoded(row)))
            for mid, row in nodes.items():
                parent = row.get('parentId')
                if parent and parent in nodes and parent != mid:
                    db.execute("INSERT OR IGNORE INTO edges VALUES(?,?,'DISPLAY',1,0,0,?,?)", (parent, mid, 'Frozen display parent; grants no scientific inheritance', encoded(row)))
                    if parent in active and mid in active:
                        diagnostics['unreviewed_material_parent_edges'].append([parent, mid])
            reviewed_pairs = set()
            for key in ('edges', 'secondary'):
                for row in read_csv(files[key]):
                    a, b = row['parent_id'], row['child_id']
                    if a not in nodes or b not in nodes:
                        continue
                    accepted = row['range_rollup_permission'] == 'UPWARD_RESEARCH_RANGE_ONLY'
                    # An explicitly reviewed category inclusion can guide BFS
                    # without adding a material denominator or property rollup.
                    kind = 'IS_A' if accepted else 'DISPLAY'
                    up = int(kind == 'IS_A' and a in active and b in active)
                    db.execute('INSERT OR REPLACE INTO edges VALUES(?,?,?,?,?,?,?,?)', (a, b, kind, int(accepted), up, up, row['review_basis'], encoded(row)))
                    if up:
                        reviewed_pairs.add((a, b))
            diagnostics['unreviewed_material_parent_edges'] = [p for p in diagnostics['unreviewed_material_parent_edges'] if tuple(p) not in reviewed_pairs]
            source_uid_owner = {}
            object_seen = set()
            batch = []
            for index, row in enumerate(read_csv(files['inventory']), 2):
                oid, cid = row['object_id'], row['component_id']
                add_inventory_alias_claim(alias_claims, row)
                if oid not in object_seen:
                    namespace = row.get('required_source_primary') or row.get('source_family') or row['source_dataset']
                    uid = row.get('source_asset_id') or oid
                    unique = (namespace, uid)
                    if unique in source_uid_owner and source_uid_owner[unique] != oid:
                        diagnostics['source_uid_collisions'].append([namespace, uid, source_uid_owner[unique], oid])
                        raise ValueError('Conflicting source UID: ' + str(unique))
                    source_uid_owner[unique] = oid
                    sha = row.get('geometry_sha256', '')
                    sha = sha if re.fullmatch(r'[a-fA-F0-9]{64}', sha) else None
                    db.execute('INSERT INTO objects VALUES(?,?,?,?,?,?,?,?,?,?)', (oid, namespace, uid, row['object_name_cn'], row['object_name_en'],
                               row.get('source_manifest_url') or row.get('mapping_source_url') or '', row.get('geometry_download_url') or row.get('asset_url') or row.get('asset_package_url') or '', sha, 1, '{}'))
                    object_seen.add(oid)
                if (oid, cid) not in inventory_components:
                    # Unknown legacy component typing is explicit; never infer a real mechanical part from a mesh count.
                    kind = component_kind_from_inventory(row)
                    db.execute('INSERT INTO components VALUES(?,?,?,?,?,?)', (oid, cid, kind, row['component_scope'], row.get('component_basis', ''), encoded({'inventory_input': str(files['inventory'].relative_to(root)), 'row': index})))
                    inventory_components.add((oid, cid))
                    void = 'empty space' in (row.get('component_material_label_raw', '') + ' ' + row.get('candidate_material_label', '')).casefold()
                    if row.get('material_node_id') in excluded_ids or void or row.get('material_node_id') == 'SPECIAL-DOMAIN-VOID':
                        special_components[(oid, cid)] = 'EXCLUDED_LIQUID' if row.get('material_node_id') in excluded_ids else 'SPECIAL_NONMATERIAL_EMPTY_SPACE'
                batch.append((str(files['inventory'].relative_to(root)), index, zlib.compress(encoded(row).encode(), 1)))
                if len(batch) >= 500:
                    db.executemany('INSERT INTO raw_source_rows VALUES(?,?,?)', batch)
                    batch.clear()
            db.executemany('INSERT INTO raw_source_rows VALUES(?,?,?)', batch)
            alias_counts = {}
            reviewed_alias_counts = {}
            for (namespace, source_uid), claim in sorted(alias_claims.items()):
                db.execute('INSERT INTO object_aliases(namespace,source_uid,object_id,basis,reviewed) VALUES(?,?,?,?,?)',
                           (namespace, source_uid, claim['object_id'], claim['basis'], claim['reviewed']))
                alias_counts[namespace] = alias_counts.get(namespace, 0) + 1
                if claim['reviewed']:
                    reviewed_alias_counts[namespace] = reviewed_alias_counts.get(namespace, 0) + 1
            if alias_counts != SOURCE_ALIAS_COUNTS:
                raise ValueError('Imported source alias coverage mismatch: expected=' + repr(SOURCE_ALIAS_COUNTS) + ', got=' + repr(alias_counts))
            if reviewed_alias_counts != SOURCE_ALIAS_COUNTS:
                raise ValueError('Not all required source aliases are reviewed: ' + repr(reviewed_alias_counts))
            diagnostics['object_alias_counts'] = alias_counts
            diagnostics['reviewed_object_alias_counts'] = reviewed_alias_counts
            set_meta(db, 'object_alias_counts', alias_counts)
            print(encoded({'phase': 'inventory_imported', 'objects': len(object_seen), 'components': len(inventory_components)}), flush=True)

            def add(mid, oid, cid, scope, linkid, mode, option_group, basis, raw):
                if mid not in active:
                    return
                if (oid, cid) not in inventory_components:
                    raise ValueError('Material link references absent object/component: ' + linkid)
                db.execute('INSERT OR IGNORE INTO material_links VALUES(?,?,?,?,?,?,?,?,?,?)', (linkid, oid, cid, mid, scope, mode or 'SOURCE_REPORTED_SCOPE', option_group, 1, basis, encoded(raw)))

            for row in read_csv(files['options']):
                add(row['assigned_material_id'], row['object_id'], row['component_id'], row['component_scope'], 'OPT:' + row['assignment_id'],
                    row['assignment_relation'], row['assignment_option_group_id'], row['assignment_basis'], row)
            relations = {}
            for name in names:
                archive_rows = []
                for source_row_number, row in enumerate(read_csv(files[name]), 2):
                    relations[row['relation_id']] = row
                    archive_rows.append((str(files[name].relative_to(root)), source_row_number, zlib.compress(encoded(row).encode(), 1)))
                    if canonical_relation_accepted(row):
                        add(row['canonical_material_id'], row['object_id'], row['component_id'], row['component_scope'], 'REL:' + row['relation_id'],
                            row.get('label_relationship'), '', row['canonical_mapping_status'], row)
                db.executemany('INSERT INTO raw_source_rows VALUES(?,?,?)', archive_rows)
            resolved = set()
            for i, row in enumerate(read_csv(files['links'])):
                rid = row['relation_id']
                if rid not in relations:
                    raise ValueError('Reviewed link has no frozen source relation: ' + rid)
                add(row['target_material_id'], row['object_id'], row['component_id'], row['material_scope'], 'LINK:' + rid + ':' + str(i),
                    row['relation_mode'], row['option_group_id'], row['mapping_basis'], row)
                if row.get('relation_resolution') == 'COMPLETE':
                    resolved.add(rid)
            for rid, row in relations.items():
                if not canonical_relation_accepted(row) and rid not in resolved:
                    db.execute('INSERT INTO obligations VALUES(?,?,?,?,?,0,?)', ('REL:' + rid, row['object_id'], row['component_id'], 'SOURCE_RELATION', 'Source material relation unresolved or partial; not erased by material coverage', encoded(row)))
            covered_components = set(tuple(r) for r in db.execute('SELECT DISTINCT object_id,component_id FROM material_links WHERE accepted=1'))
            for oid, cid in inventory_components - covered_components:
                if (oid, cid) in special_components:
                    continue
                db.execute('INSERT INTO obligations VALUES(?,?,?,?,?,0,?)', ('CMP:' + oid + ':' + cid, oid, cid, 'COMPONENT_MATERIAL', 'No reviewed active nonfluid material label for this component', '{}'))

            for gid, row in phase['recordsById'].items():
                document = row.get('document_key') or 'UNRESOLVED-DOCUMENT:' + gid
                lineage = row.get('source_lineage_key') or row.get('source_lineage_id') or None
                db.execute('INSERT OR IGNORE INTO documents VALUES(?,?,0,?,?)', (document, lineage, row.get('url', ''), encoded(row)))
                # Freeze prior accepted ledger classification; not an assertion every paper was reread today.
                db.execute('INSERT INTO evidence_groups VALUES(?,?,?,?,1,?,?)', (gid, document, row.get('material_identity', ''), row.get('unique_record_key') or gid,
                           'FROZEN_ACCEPTED_MAIN_LEDGER_NOT_REAUDITED_BY_IMPORT', encoded(row)))
                for prop, lowkey, highkey, unit in [('E', 'E_low_GPa', 'E_high_GPa', 'GPa'), ('nu', 'nu_low', 'nu_high', '1'), ('rho', 'rho_low_kg_m3', 'rho_high_kg_m3', 'kg/m3')]:
                    lo, hi = row.get(lowkey), row.get(highkey)
                    if lo in ('', None) or hi in ('', None):
                        bounds = parser.record_property_bounds(row, prop) if row.get(prop + '_source_value') else None
                        if bounds:
                            lo, hi = bounds
                    if lo not in ('', None) and hi not in ('', None):
                        db.execute('INSERT INTO observations VALUES(?,?,?,?,?,1,?)', (gid, prop, float(lo), float(hi), unit, encoded({'source_record': gid, 'unit_E_original': row.get('unit_E_original', ''), 'raw_value': row.get(prop + '_source_value', '')})))
            direct_relations = {'DIRECT_CANONICAL_MATERIAL', 'REVIEWED_EXPLICIT_SOURCE_IDENTITY_AFTER_LABEL_CORRECTION', 'REVIEWED_EXPLICIT_SHARED_SOURCE_ROW_APPLIES_TO_TARGET'}
            for mid, target in targets.items():
                for ref in target['evidence']:
                    if ref['recordId'] not in phase['recordsById']:
                        diagnostics['missing_group_references'].append([mid, ref['recordId']])
                        raise ValueError('Target evidence record absent: ' + ref['recordId'])
                    relation = 'DIRECT' if ref['relationship'] in direct_relations else ref['relationship']
                    if relation not in ('DIRECT', 'REVIEWED_TRUE_CONTAINMENT', 'REVIEWED_TARGET_SUBTYPE_REFERENCE'):
                        raise ValueError('Unrecognized target relationship: ' + relation)
                    db.execute('INSERT OR IGNORE INTO group_material_refs VALUES(?,?,?,1,?)', (ref['recordId'], mid, relation, encoded(ref)))
            for module in list(sys.modules.values()):
                filename = getattr(module, '__file__', None)
                if filename:
                    module_path = Path(filename).resolve()
                    if module_path.is_relative_to(root / 'audit') and module_path.is_file():
                        key = str(module_path.relative_to(root))
                        inputs.setdefault(key, digest_file(module_path))
                        files['module:' + key] = module_path
            # Pin every input again before accepting the import; concurrent source writes invalidate the snapshot.
            after = {str(p.relative_to(root)): digest_file(p) for p in files.values()}
            if after != inputs:
                raise ValueError('Source inputs changed during import')
            set_meta(db, 'inputs', inputs)
            diagnostics['special_or_excluded_components'] = [{'object_id': oid, 'component_id': cid, 'reason': reason} for (oid, cid), reason in sorted(special_components.items())]
            set_meta(db, 'adapter_diagnostics', diagnostics)
        recalculated, planned = recompute(db), plan(db)
        products = export(db, export_dir)
        (export_dir / 'IMPORT_DIAGNOSTICS.json').write_text(encoded(diagnostics) + '\n')
        print(encoded({'status': 'SHADOW_IMPORTED', 'database': str(out), 'recomputed': recalculated, 'planned': planned, 'exports': products}), flush=True)
    finally:
        db.close()


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--release-dir', type=Path, required=True)
    p.add_argument('--db', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--snapshot-id', help='Execution snapshot ID; does not imply website publication')
    a = p.parse_args()
    run(a.root.resolve(), a.release_dir, a.db, a.out, a.snapshot_id)
