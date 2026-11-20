#!/usr/bin/env python3
"""Project an authoritative normalized six-table bundle into an isolated website.

The source supplies presentation assets only. This does not review, install,
update pointers or publish. Full inputs and non-PASS rows stay outside the site.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from copy import deepcopy
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

try:
    from .workflow_data_v3 import validate_bundle, recompute, TABLE_KEYS, PROPERTIES, _bounds
    from .workflow_publication_v3 import PAGES, contained, read_json, require, sha, verify_manifest, validate_site, write_json
except ImportError:
    from workflow_data_v3 import validate_bundle, recompute, TABLE_KEYS, PROPERTIES, _bounds
    from workflow_publication_v3 import PAGES, contained, read_json, require, sha, verify_manifest, validate_site, write_json


def text(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list)) else str(value or '')


def label(row, fallback):
    return row.get('name_zh') or row.get('name_cn') or row.get('nameCn') or row.get('name') or row.get('label') or fallback


def raw_json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def coverage(states):
    n = len(states)
    return dict(targetCount=n, materialsWithCompleteRecord=sum(s['complete_group_count'] > 0 for s in states),
                materialsWithIncompleteRecord=sum(s['partial_group_count'] > 0 for s in states),
                materialsWithE=sum('E' in s['covered_properties'] for s in states),
                materialsWithNu=sum('nu' in s['covered_properties'] for s in states),
                materialsWithRho=sum('rho' in s['covered_properties'] for s in states),
                materialsWithAllThreeFromAnyGroup=sum(len(s['covered_properties']) == 3 for s in states),
                materialsWithoutAnyValue=sum(not s['covered_properties'] for s in states),
                coveragePercent=round(100 * sum(len(s['covered_properties']) == 3 for s in states) / n, 4) if n else 0,
                missingMaterials=sum(len(s['covered_properties']) < 3 for s in states))


def project_bundle_site(source_site, out_site, bundle, release_id, workflow_config=None):
    """Build a new four-page candidate from all six supplied authoritative tables.

    ``bundle`` accepts a dictionary, JSON path, or Run export containing bundle.
    There is no production installation API. The sibling ``<out>.internal`` is
    deliberately outside the site's document root and its public manifest.
    """
    source, output = Path(source_site).resolve(), Path(out_site).absolute()
    private = output.with_name(output.name + '.internal')
    require(not output.exists() and not output.is_symlink() and not private.exists() and not private.is_symlink(), 'Output/internal directory exists; projection is immutable')
    require(not output.resolve().is_relative_to(source) and not private.resolve().is_relative_to(source), 'Projection must be outside source site')
    require(isinstance(release_id, str) and release_id.strip() and re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', release_id), 'Invalid release_id')
    parent = verify_manifest(source)
    require(release_id != parent.get('snapshot_id'), 'Changed authoritative data needs a new release ID')
    original = read_json(bundle) if isinstance(bundle, (str, Path)) else deepcopy(bundle)
    require(isinstance(original, dict), 'Expected normalized bundle or Run export')
    wrapped = 'bundle' in original and not set(TABLE_KEYS) <= original.keys()
    if wrapped and 'release_id' in original:
        require(original['release_id'] == release_id, 'Run export release_id must match requested release_id')
    data = original['bundle'] if wrapped else original
    validation = validate_bundle(data)
    full_state = recompute(data)
    active = {s['material_id'] for s in full_state['material_states'] if not s['excluded']}
    public = {k: deepcopy(data[k]) for k in TABLE_KEYS}
    public['objects'] = [r for r in public['objects'] if 'decision' not in r or r['decision'] == 'PASS']
    object_ids = {r['object_id'] for r in public['objects']}
    public['components'] = [r for r in public['components'] if ('decision' not in r or r['decision'] == 'PASS') and r['object_id'] in object_ids]
    component_ids = {r['component_id'] for r in public['components']}
    public['materials'] = [r for r in public['materials'] if r['material_id'] in active]
    public['relations'] = [r for r in public['relations'] if r['decision'] == 'PASS' and r['material_id'] in active and r['component_id'] in component_ids]
    public['taxonomy'] = [r for r in public['taxonomy'] if r['decision'] == 'PASS' and r['relation'] == 'IS_A' and r['child_id'] in active and r['parent_id'] in active]
    public['evidence'] = [r for r in public['evidence'] if r['decision'] == 'PASS' and r['material_id'] in active]
    state = recompute(public)
    states = {s['material_id']: s for s in state['material_states']}
    materials = {r['material_id']: r for r in public['materials']}
    components = {r['component_id']: r for r in public['components']}
    objects = {r['object_id']: r for r in public['objects']}
    evidence = {r['record_id']: r for r in public['evidence']}
    by_object, by_component, direct_evidence, direct_objects = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
    for row in public['components']:
        by_object[row['object_id']].append(row)
    for row in public['relations']:
        by_component[row['component_id']].append(row)
    for row in public['evidence']:
        direct_evidence[row['material_id']].append(row)
    parents, children = defaultdict(list), defaultdict(list)
    for edge in sorted(public['taxonomy'], key=lambda r: r['edge_id']):
        if edge['parent_id'] not in parents[edge['child_id']]:
            parents[edge['child_id']].append(edge['parent_id'])
            children[edge['parent_id']].append(edge['child_id'])
    root_id = 'V3-PROJECTION-ROOT'
    require(root_id not in materials, 'Reserved projection root ID collision')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.' + output.name + '-', dir=output.parent)).resolve()
    private_stage = Path(tempfile.mkdtemp(prefix='.' + private.name + '-', dir=output.parent)).resolve()
    installed_private = False

    def save(name, value):
        path = contained(stage, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, value)

    def chunk(name, value, records):
        raw = raw_json(value)
        path = contained(stage, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(gzip.compress(raw, mtime=0))
        return dict(url=name, sha256=hashlib.sha256(raw).hexdigest(), records=records)

    def property_range(row, prop):
        if prop not in row['properties']:
            return ['', '']
        low, high = _bounds(prop, row['properties'][prop])
        factor = 1e9 if prop == 'E' else 1
        return [str(low / factor), str(high / factor)]

    def original_value(row, prop):
        item = row['properties'].get(prop)
        if not item:
            return ''
        value = str(item['value']) if 'value' in item else str(item['lower']) + '–' + str(item['upper'])
        return value + ' ' + item['unit']

    try:
        # Never copy legacy payload JSON/gzip or JS that embeds the old data.
        for name in parent['files']:
            if name in PAGES or name == 'workflow-code.zip' or name.startswith('workflow-code/') or (Path(name).suffix in ('.css', '.js') and name not in ('bootstrap.js', 'release-data.js')):
                target = contained(stage, name)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(contained(source, name), target)
        require(all((stage / p).is_file() for p in PAGES), 'Source must provide the existing four pages')
        write_json(private_stage / 'NORMALIZED_INPUT.json', original)
        write_json(private_stage / 'VALIDATION.json', validation)
        write_json(private_stage / 'RECOMPUTED_INPUT.json', full_state)
        public_ids = {table: {r[key] for r in public[table]} for table, key in TABLE_KEYS.items()}
        write_json(private_stage / 'INTERNAL_ROWS.json', {table: [r for r in data[table] if r[key] not in public_ids[table]] for table, key in TABLE_KEYS.items()})
        bundle_sha = hashlib.sha256(raw_json(data)).hexdigest()
        save('INPUT_PINS.json', dict(schema='rsi-normalized-projection-pins-v3', normalized_bundle_sha256=bundle_sha,
                                    parent_manifest_sha256=sha(source / 'MANIFEST.json'), release_id=release_id))
        complete = sum(set(r['properties']) == set(PROPERTIES) for r in evidence.values())
        partial = len(evidence) - complete
        object_states = [s for s in states.values() if s['object_count']]
        unlinked_complete = [s for s in states.values() if not s['object_count'] and len(s['covered_properties']) == 3]
        unlinked_partial = [s for s in states.values() if not s['object_count'] and len(s['covered_properties']) != 3]
        all_coverage, object_coverage = coverage(list(states.values())), coverage(object_states)
        object_pages, card_pages, locator, search = [], [], {}, []
        detail_buffer, card_buffer = [], []
        state_rows = 0
        for oid, obj in sorted(objects.items()):
            detail = dict(id=oid, name=label(obj, '未命名物体'), nameEn=obj.get('name_en', obj.get('nameEn', '')),
                          dataset=text(obj.get('dataset') or obj.get('namespace') or '来源未提供'),
                          sourceId=text(obj.get('source_uid') or obj.get('sourceId') or oid), components=[], relations=[], review=[], options=[], labels=[])
            mids, source_links = set(), []
            for comp in sorted(by_object[oid], key=lambda r: r['component_id']):
                relations = sorted(by_component[comp['component_id']], key=lambda r: r['relation_id'])
                for relation in relations:
                    mid = relation['material_id']
                    mids.add(mid)
                    title = label(materials[mid], '未命名材料')
                    url = relation.get('source_url') or comp.get('source_url') or obj.get('source_url') or ''
                    loc = relation['source_locator']
                    projected_relation = dict(relation_id=relation['relation_id'], object_id=oid, component_id=comp['component_id'],
                                              target_material_id=mid, source_label_raw=title, source_label_cn=title,
                                              source_url=url, source_locator=loc, source_quote=text(relation.get('source_quote')),
                                              material_scope=comp['scope'], mapping_basis=relation['basis'],
                                              relation_type=relation.get('relation_type', relation.get('mode', '来源关联')),
                                              stream='working_links', numerical_property_assignment='NONE')
                    detail['relations'].append(projected_relation)
                    detail['components'].append(dict(component_id=comp['component_id'], component_path=comp.get('component_path', comp['scope']),
                                                     component_scope=comp['scope'], component_name=label(comp, '整件（未拆分）' if 'WHOLE' in comp['scope'].upper() else '来源部件'),
                                                     material_node_id=mid, material_label=title, mapping_source_url=url, mapping_source_locator=loc,
                                                     mapping_evidence_text=text(relation.get('source_quote') or relation['basis'])))
                    direct_objects[mid].append(dict(id=oid, componentId=comp['component_id'], nameCn=detail['name'], nameEn=detail['nameEn'],
                                                    scope=comp['scope'], sourceDataset=detail['dataset'], assetUrl=obj.get('asset_url', ''), sourceUrl=url))
                    if url:
                        source_links.append(dict(url=url, label='原始来源'))
                if not relations:
                    detail['components'].append(dict(component_id=comp['component_id'], component_name=label(comp, '整件（未拆分）' if 'WHOLE' in comp['scope'].upper() else '来源部件'), component_scope=comp['scope'],
                                                     material_node_id='UNMAPPED', material_label='材料未提供', mapping_source_locator=comp['source_locator']))
            if obj.get('asset_url'):
                source_links.append(dict(url=obj['asset_url'], label='3D 资产'))
            if obj.get('download_url'):
                source_links.append(dict(url=obj['download_url'], label='来源资产包'))
            source_links = [dict(url=u, label=l) for u, l in sorted({(r['url'], r['label']) for r in source_links})]
            pairs = [[mid, label(materials[mid], '未命名材料')] for mid in sorted(mids)]
            shard = len(object_pages)
            card = dict(id=oid, name=detail['name'], nameEn=detail['nameEn'], dataset=detail['dataset'], sourceId=detail['sourceId'], fullShard=shard,
                        componentPairs=len(by_object[oid]), stateRows=len(detail['components']), materialLabels=[p[1] for p in pairs], materials=pairs,
                        reviewedMaterials=pairs, reviewStatuses=['PASS'] if pairs else [], installedReviewCount=0, links=source_links)
            state_rows += len(detail['components'])
            locator[oid] = shard
            search.append([oid, detail['name'], detail['dataset'] + ' ' + detail['sourceId'], shard, card['reviewStatuses']])
            detail_buffer.append(detail)
            card_buffer.append(card)
            if len(detail_buffer) == 250:
                object_pages.append(chunk('objects/' + str(shard).zfill(4) + '.json.gz', detail_buffer, len(detail_buffer)))
                card_pages.append(chunk('object-cards/' + str(shard).zfill(4) + '.json.gz', card_buffer, len(card_buffer)))
                detail_buffer, card_buffer = [], []
        if detail_buffer or not object_pages:
            shard = len(object_pages)
            object_pages.append(chunk('objects/' + str(shard).zfill(4) + '.json.gz', detail_buffer, len(detail_buffer)))
            card_pages.append(chunk('object-cards/' + str(shard).zfill(4) + '.json.gz', card_buffer, len(card_buffer)))
        material_index = {}
        material_ids = [root_id, *sorted(materials)]
        for offset in range(0, len(material_ids), 250):
            mapping = {mid: (sorted(objects) if mid == root_id else states[mid]['object_ids']) for mid in material_ids[offset:offset + 250]}
            spec = chunk('material-objects/' + str(offset // 250).zfill(4) + '.json.gz', mapping, len(mapping))
            material_index.update({mid: spec for mid in mapping})
        snapshot = dict(id=release_id, kind='REVIEWED_RESEARCH_SNAPSHOT', date=text(data.get('date') or '未指定'),
                        data_cutoff_date=text(data.get('data_cutoff_date') or data.get('date') or '未指定'),
                        objects=dict(total=len(objects), rows=len(components), state_rows=state_rows), materials=dict(total=len(materials)),
                        records=dict(complete=complete, partial=partial, total=len(evidence)), main_ledger=dict(complete=complete, partial=partial),
                        database_transcribed=dict(complete=0, partial=0, original_papers_individually_rechecked=False),
                        source_keys=dict(document_or_database_citation_keys=len({r['document_id'] for r in evidence.values()}), independent_papers=None),
                        completion_flags=dict(global_geometry_deduplicated=False, all_mechanical_components_enumerated=False, all_approximate_materials_individually_verified=False),
                        final_review=dict(PASS=len(public['relations']), HOLD=0, REJECT=0), installed_reviewed_queue_items=0,
                        review_pass_without_installed_queue_items=len(public['relations']), normalized_installed_queue_items=0,
                        object_material_coverage=object_coverage, all_material_coverage=all_coverage,
                        object_priority_coverage=dict(objectMaterialIds=[s['material_id'] for s in object_states], objectMaterials=object_coverage,
                                                      unlinkedComplete=coverage(unlinked_complete), researchCandidates=coverage(unlinked_partial)),
                        object_pages=object_pages, object_card_pages=card_pages,
                        object_locator=chunk('object-locator.json.gz', locator, len(locator)),
                        object_search=chunk('object-search.json.gz', search, len(search)), material_object_index=material_index,
                        catalog_pages=[], production_write=False, publication_authorized=False, requires_independent_review=True,
                        projection_kind='NORMALIZED_AUTHORITATIVE_SIX_TABLE_CANDIDATE', normalized_bundle_sha256=bundle_sha)
        save('snapshot.json', snapshot)
        research_evidence, coverage_records = {}, {}
        for rid, row in sorted(evidence.items()):
            ranges = {p: property_range(row, p) for p in PROPERTIES}
            is_complete = set(row['properties']) == set(PROPERTIES)
            condition = text(row.get('conditions')) or '未报告条件'
            research_item = dict(id=rid, nodeId=row['material_id'], recordType='COMPLETE' if is_complete else 'INCOMPLETE', title=row.get('title', row['document_id']),
                                 sourceId=row['document_id'], sourceType=row['origin'], url=row['source_url'], locator=row['source_locator'],
                                 documentKey=row['document_id'], publisher=row.get('publisher', ''), grade=label(materials[row['material_id']], '未命名材料'),
                                 environment=condition, method=text(row.get('method')), limitations=text(row.get('limitations')),
                                 orientation=text(row.get('direction') or row.get('orientation')), sourceStatistic=text(row.get('statistic')),
                                 sourceUncertaintyNotes=text(row.get('uncertainty')), densitySourceDefinition=text(row.get('density_definition')),
                                 sourceValueExcerpt=row['source_quote'], sourceOriginalValues=row['properties'], sourceUnitsOriginal={p: v['unit'] for p, v in row['properties'].items()},
                                 sourceGroupId=row['source_group_id'], propertyModel='SOURCE_REPORTED_RESEARCH_GROUP', unitConversionNotes='E→GPa；ν→无量纲；ρ→kg/m³；原值与原单位另存。')
            for p in PROPERTIES:
                research_item[p] = ranges[p] if is_complete else ([original_value(row, p)] if p in row['properties'] else [])
            research_evidence[rid] = research_item
            coverage_item = dict(record_id=rid, record_type=research_item['recordType'], record_origin='REVIEWED_SOURCE_GROUP', source_id=row['document_id'],
                                 document_key=row['document_id'], material_identity=label(materials[row['material_id']], '未命名材料'),
                                 url=row['source_url'], locator=row['source_locator'], conditions=condition, source_group_id=row['source_group_id'],
                                 property_count=len(row['properties']), source_title=research_item['title'], property_model='SOURCE_REPORTED_RESEARCH_GROUP',
                                 method_or_basis=text(row.get('method')), limitations=text(row.get('limitations')), source_uncertainty_notes=text(row.get('uncertainty')),
                                 source_value_excerpt=row['source_quote'], property_citations_json=text(row.get('property_citations')))
            for p, lo, hi in [('E', 'E_low_GPa', 'E_high_GPa'), ('nu', 'nu_low', 'nu_high'), ('rho', 'rho_low_kg_m3', 'rho_high_kg_m3')]:
                coverage_item[lo], coverage_item[hi] = ranges[p]
                coverage_item[p + '_source_value'] = original_value(row, p)
            coverage_records[rid] = coverage_item
        nodes = []
        targets = []
        for mid, material in sorted(materials.items()):
            s = states[mid]
            direct = direct_evidence[mid]
            parent_ids = sorted(parents[mid])
            node = dict(id=mid, nameCn=label(material, '未命名材料'), nameEn=material.get('name_en', material.get('nameEn', '')),
                        nodeKind='MATERIAL_IDENTITY', parentId=parent_ids[0] if parent_ids else root_id, secondaryParentIds=parent_ids[1:],
                        secondaryChildIds=sorted(child for child in children[mid] if sorted(parents[child])[0] != mid),
                        directObjectCount=s['direct_object_count'], directComponentCount=len({r['componentId'] for r in direct_objects[mid]}),
                        evidenceCount=len(direct), directEvidenceCount=len(direct), subtreeEvidenceCount=s['record_count'],
                        completeEvidenceCount=sum(len(r['properties']) == 3 for r in direct), incompleteEvidenceCount=sum(len(r['properties']) != 3 for r in direct),
                        classifiedEvidenceCount=s['record_count'], classifiedCompleteEvidenceCount=s['complete_group_count'], classifiedIncompleteEvidenceCount=s['partial_group_count'],
                        sourceDocumentCount=s['document_count'], classifiedSourceDocumentCount=s['document_count'], publisherSubjectCount=s['document_count'],
                        classifiedPublisherSubjectCount=s['document_count'], evidenceIds=[r['record_id'] for r in direct],
                        directCompleteEvidenceCount=sum(len(r['properties']) == 3 for r in direct), directIncompleteEvidenceCount=sum(len(r['properties']) != 3 for r in direct),
                        notes='按批准 IS_A 向上去重汇总；不向子类继承数值，不自动赋予物体。')
            nodes.append(node)
            target = dict(id=mid, nameCn=node['nameCn'], nameEn=node['nameEn'], family=material.get('family', '未分类'), parentId=node['parentId'],
                          nodeKind='MATERIAL_IDENTITY', completeRecordCount=s['complete_group_count'], incompleteRecordCount=s['partial_group_count'],
                          recordCount=s['record_count'], documentKeyCount=s['document_count'], sourceLabels=node['nameCn'],
                          evidence=[dict(recordId=rid, relationship='DIRECT_CANONICAL_MATERIAL' if evidence[rid]['material_id'] == mid else 'REVIEWED_TARGET_SUBTYPE_REFERENCE') for rid in s['record_ids']])
            for p in PROPERTIES:
                r = s['ranges'].get(p)
                target[p] = [str(r['lower'] / (1e9 if p == 'E' else 1)), str(r['upper'] / (1e9 if p == 'E' else 1))] if r else ['', '']
            targets.append(target)
        root_node = dict(id=root_id, nameCn='材料分类', nameEn='Material classification', nodeKind='CATEGORY', parentId=None,
                         directEvidenceCount=0, directObjectCount=0, subtreeEvidenceCount=len(evidence), classifiedEvidenceCount=len(evidence),
                         classifiedSourceDocumentCount=snapshot['source_keys']['document_or_database_citation_keys'], sourceDocumentCount=snapshot['source_keys']['document_or_database_citation_keys'],
                         classifiedPublisherSubjectCount=0, publisherSubjectCount=0, evidenceIds=[])
        details, ev_by_node = {}, {}
        for offset in range(0, len(nodes), 50):
            group = nodes[offset:offset + 50]
            key = str(offset // 50)
            ev = {n['id']: [research_evidence[r['record_id']] for r in direct_evidence[n['id']]] for n in group}
            details[key] = chunk('research-details/' + key + '.json.gz', dict(nodes=[], evidenceByNode=ev), sum(len(v) for v in ev.values()))
            for node in group:
                node['detailChunk'] = key
        meta = dict(releaseId=release_id, researchMode=True, title='材料物性来源树', completeRecordCount=complete, incompleteRecordCount=partial,
                    evidenceCount=len(evidence), reviewedRecordGroupCount=len(evidence), allRecordCountTarget=len(evidence),
                    canonicalMaterialNodeCount=len(materials), allMaterialNodeCount=len(materials), sourceDefinedIdentityCount=len(materials), canonicalCoverage=all_coverage,
                    combinedSourceDocumentKeys=snapshot['source_keys']['document_or_database_citation_keys'], mainCompleteRecordCount=complete, mainIncompleteRecordCount=partial,
                    externalCompleteRecordCount=0, externalIncompleteRecordCount=0, isolatedSimulationPresetCount=0,
                    confirmedSourceLineagesInInheritedScope=0, incompleteAuditStatus='CANDIDATE_REQUIRES_INDEPENDENT_REVIEW')
        save('research.json', dict(meta=meta, nodes=[root_node, *nodes], evidenceByNode=ev_by_node, objectsByNode=dict(direct_objects),
                                   progressiveDetails=True, detailChunks=details, externalCollections=[]))
        record_details, record_chunks = {}, {}
        record_ids = sorted(coverage_records)
        for offset in range(0, len(record_ids), 500):
            key = str(offset // 500)
            group = {rid: coverage_records[rid] for rid in record_ids[offset:offset + 500]}
            record_chunks[key] = chunk('coverage-details/' + key.zfill(3) + '.json.gz', dict(releaseId=release_id, recordsById=group), len(group))
            record_details.update({rid: key for rid in group})
        save('coverage.json', dict(releaseId=release_id, summary=dict(reviewedRecords=len(evidence), unmappedRecords=0), targets=[], canonicalTargets=targets,
                                   canonicalSummary=all_coverage, recordsById={}, unmapped=[], progressiveEvidence=True, recordDetails=record_details, recordDetailChunks=record_chunks))
        bootstrap = "window.MATERIAL_PAYLOAD_READY=(async()=>{const get=async p=>{const r=await fetch(p);if(!r.ok)throw Error(p+' HTTP '+r.status);return r.json()};const version=RELEASE;const release=window.DATASET_RELEASE=await get('snapshot.json?v='+version);if(release.id!==version)throw Error('快照版本不一致');window.verifyDatasetView=(kind,data)=>{const id=kind==='materials'?data?.meta?.releaseId:data?.releaseId;if(id!==release.id)throw Error('页面数据快照不一致');return true};if(location.pathname.endsWith('research.html'))window.SITE_DATA=await get('research.json?v='+version);if(location.pathname.endsWith('references.html'))window.PHASE1_RANGES=await get('coverage.json?v='+version)})().catch(e=>{document.addEventListener('DOMContentLoaded',()=>{document.body.prepend(Object.assign(document.createElement('p'),{className:'release-mismatch',textContent:'数据载入失败：'+e.message}))});throw e});\n"
        (stage / 'bootstrap.js').write_text(bootstrap.replace('RELEASE', json.dumps(release_id), 1), encoding='utf-8')
        js = (stage / 'snapshot.js').read_text(encoding='utf-8')
        js = js.replace('已审核研究工作快照', '候选研究快照，等待独立验收').replace('来源关联（含候选）', '来源关联').replace('全部关联（含原始候选）', '全部关联')
        js = js.replace('href="evidence-catalog.html"', 'href="references.html"').replace('数据库转录逐条记录', '全部物性来源')
        (stage / 'snapshot.js').write_text(js, encoding='utf-8')
        if workflow_config is not None:
            config = read_json(workflow_config) if isinstance(workflow_config, (str, Path)) else workflow_config
        else:
            config = read_json(source / 'workflow-data.json')
        save('workflow-data.json', config)
        (stage / 'index.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta http-equiv="refresh" content="0;url=scaling.html"><title>物体与材料库</title><a href="scaling.html">物体与材料总览</a></html>\n', encoding='utf-8')
        # Bind changed script URLs to candidate bytes while keeping layout/styles.
        for page in PAGES:
            html = (stage / page).read_text(encoding='utf-8')
            for resource in ('bootstrap.js', 'snapshot.js'):
                html = re.sub(re.escape(resource) + r'(?:\?[^"\s<>]*)?', resource + '?v=' + sha(stage / resource)[:16], html)
            (stage / page).write_text(html, encoding='utf-8')
        save('PROJECTION.json', dict(schema='rsi-normalized-site-projection-v3', release_id=release_id, normalized_bundle_sha256=bundle_sha,
                                     requires_independent_review=True, production_write=False, publication_authorized=False,
                                     accepted_relation_rows=len(public['relations']), accepted_evidence_groups=len(evidence),
                                     parent_manifest_sha256=sha(source / 'MANIFEST.json'), completion_claimed=False))
        manifest = dict(snapshot_id=release_id, publication_type='REVIEWED_RESEARCH_SNAPSHOT', production_write=False, publication_authorized=False,
                        requires_independent_review=True, normalized_bundle_sha256=bundle_sha, parent_manifest_sha256=sha(source / 'MANIFEST.json'),
                        files={str(p.relative_to(stage)): sha(p) for p in sorted(stage.rglob('*')) if p.is_file()})
        write_json(stage / 'MANIFEST.json', manifest)
        result = validate_site(stage)
        require(sha(source / 'MANIFEST.json') == manifest['parent_manifest_sha256'], 'Source manifest changed during projection')
        verify_manifest(source)
        require(not private.exists() and not output.exists(), 'Output appeared during projection')
        os.rename(private_stage, private)
        installed_private = True
        os.rename(stage, output)
        return dict(result, site=str(output), internal=str(private), publication_authorized=False, requires_independent_review=True,
                    public_counts=state['counts'], normalized_bundle_sha256=bundle_sha)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        shutil.rmtree(private_stage, ignore_errors=True)
        if installed_private:
            shutil.rmtree(private, ignore_errors=True)
        raise


build_projected_site = project_bundle_site


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-site', required=True, type=Path)
    parser.add_argument('--out-site', required=True, type=Path)
    parser.add_argument('--bundle', required=True, type=Path)
    parser.add_argument('--release-id', required=True)
    parser.add_argument('--workflow-config', type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(project_bundle_site(**vars(args)), ensure_ascii=False, indent=2))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(2, 'projection blocked: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
