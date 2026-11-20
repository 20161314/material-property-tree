"""Validate the frozen O4 alias and project IDs only, retaining every raw row."""
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path
from project_paths_v24 import resolve_project_input
ALIAS_FILE=Path('data/current_two_table_delivery_v1/object_identity_aliases.csv')
REVIEW_FILE=Path('audit/rsi_continuation_round4_2026-11-15/exact_alias_review/MANIFEST.json')
APPROVED_REVIEW_SHA='fd7d021bb73adbe6b98d1a21081117d804d9c89ce32f64f3992cbd80af317c31'
class AliasValidationError(ValueError): pass
def require(condition,message):
    if not condition: raise AliasValidationError(message)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def rid(row):return row.get('relation_id') or row.get('mapping_source_ids')
def pair(row):return row.get('object_id','').strip(),row.get('component_id','').strip()
def newline(value):return value.replace('\r\n','\n').replace('\r','\n')
class AliasProjection:
    def __init__(self,root,summary):
        self.root=root.resolve();self.inputs={};self.seen=set();self.preimage_seen=set();self.projected_rows=0
        pins=summary.get('input_sha256',{})
        def read_pinned(rel,expected=None):
            path=resolve_project_input(self.root,str(rel))
            require(path is not None and path.is_file(),f'Alias input missing or unsafe: {rel}')
            key=str(path.relative_to(self.root));actual=sha(path)
            require(pins.get(key)==actual,f'Alias input missing/mismatched summary pin: {key}')
            require(expected is None or expected==actual,f'Alias reviewed input changed: {key}')
            self.inputs[key]=actual;return path
        alias=read_pinned(ALIAS_FILE,summary.get('object_identity_aliases_sha256'))
        require(summary.get('object_identity_aliases_sha256')==sha(alias),'Dedicated alias SHA missing/mismatched')
        review_path=read_pinned(REVIEW_FILE,APPROVED_REVIEW_SHA)
        review=json.loads(review_path.read_text())
        require(review.get('status')=='PASS_EXACT_SOURCE_ASSET_ALIAS_REVIEW','Alias review not PASS')
        outputs={}
        for name,info in review['outputs'].items():
            require(not Path(name).is_absolute() and '..' not in Path(name).parts,'Unsafe alias output path')
            outputs[name]=read_pinned(REVIEW_FILE.parent/name,info['sha256'])
        for name,digest in review['input_pins'].items():
            p=Path(name)
            if p.is_absolute():
                try:p=p.resolve().relative_to(self.root)
                except ValueError:raise AliasValidationError('Alias source pin outside project root')
            if p==Path('data/scaling_release_v1/object_component_inventory.csv'):continue
            read_pinned(p,digest)
        def csvrows(path):
            with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
        operations=csvrows(outputs['PROPOSED_RELATION_ALIAS_PROJECTION.csv'])
        self.operations={r['relation_id']:r for r in operations}
        require(len(self.operations)==len(operations)>0,'Duplicate/empty alias relation operations')
        self.preimages={rid(r):r for r in json.loads(outputs['INVENTORY_ROWS.json'].read_text())}
        require(len(self.preimages)==len(json.loads(outputs['INVENTORY_ROWS.json'].read_text())),'Duplicate frozen alias preimage')
        expected_aliases={}
        for r in operations:
            before=r['from_object_id'],r['from_component_id'];after=r['to_object_id'],r['to_component_id']
            require(before!=after and all(before+after),'Empty/self alias')
            require(r.get('numerical_assignment')=='NONE' and r.get('action')=='RETAIN_ORIGINAL_ROW_AND_PROJECT_CANONICAL_ALIAS','Unapproved alias action')
            require(before not in expected_aliases or expected_aliases[before]==after,'Conflicting alias target')
            expected_aliases[before]=after
            require(r['relation_id'] in self.preimages and pair(self.preimages[r['relation_id']])==before,'Alias frozen preimage missing')
            require(self.preimages[r['relation_id']].get('material_node_id')==r['material_node_id'],'Alias frozen material changed')
        require(not set(expected_aliases)&set(expected_aliases.values()),'Alias chain/cycle is not an approved one-step projection')
        declared={}
        for r in csvrows(alias):
            before=r['alias_object_id'],r['alias_component_id'];after=r['canonical_object_id'],r['canonical_component_id']
            require(before not in declared,'Duplicate alias table row')
            require(r.get('basis')=='INDEPENDENTLY_REVIEWED_SAME_SOURCE_UID_AND_VERSIONED_ASSET_LOCATOR' and r.get('raw_history_retained')=='True' and r.get('verified_unique_shape_claim')=='False','Alias scope changed')
            declared[before]=after
        require(declared==expected_aliases,'Alias table does not exactly match reviewed relation projections')
        self.aliases=declared
        self.targets=set(declared.values());self.raw_pairs=set()
        require(all(any(pair(p)==t for p in self.preimages.values()) for t in self.targets),'Canonical target lacks frozen source preimage')
    def canonical_pair(self,row):
        op=self.operations.get(rid(row))
        return (op['to_object_id'],op['to_component_id']) if op else pair(row)
    def project(self,row):
        key=rid(row);before=pair(row);self.raw_pairs.add(before)
        if key in self.preimages:
            require(key not in self.preimage_seen,'Repeated alias/target preimage')
            self.preimage_seen.add(key)
            require(all(newline(row.get(k,''))==newline(v) for k,v in self.preimages[key].items() if v!=''),f'Alias/target row preimage differs: {key}')
        op=self.operations.get(key)
        if op is None:
            require(before not in self.aliases,'Unreviewed relation attached to alias source identity')
            return row
        require(key not in self.seen and before==(op['from_object_id'],op['from_component_id']),'Repeated/wrong alias relation preimage')
        self.seen.add(key);self.projected_rows+=1
        return dict(row,object_id=op['to_object_id'],component_id=op['to_component_id'])
    def finish(self,expected,raw_ids,canonical_ids):
        require(self.seen==set(self.operations),'Missing reviewed alias relation')
        require(self.preimage_seen==set(self.preimages),'Missing frozen alias/target source row')
        require(self.targets<=self.raw_pairs,'Canonical alias target not present in raw inventory')
        require(len(raw_ids)==expected.get('raw_inventory_source_identities'),'Raw identity summary mismatch')
        require(len(raw_ids)-len(canonical_ids)==expected.get('raw_inventory_object_id_aliases_collapsed'),'Alias collapse summary mismatch')
        return {'validated_alias_pairs':len(self.aliases),'projected_relation_rows':self.projected_rows,'raw_rows_retained':True,'verified_unique_shape_claim':False,'validated_input_sha256':self.inputs}
def load_alias_projection(root,summary):
    if summary.get('canonical_identity_projection_applied') is True:return AliasProjection(root,summary)
    require(not summary.get('raw_inventory_object_id_aliases_collapsed'),'Alias collapse declared without canonical projection')
    return None
