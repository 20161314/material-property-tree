"""One authenticated read-time object inventory for delivery and RSI audits.

The frozen CSV and O74 source-identity sidecar are additive source records.
Neither source identities nor WHOLE fallbacks establish unique geometry or real parts.
"""
from pathlib import Path
import csv,hashlib,sys
OBJECT_REL=Path('data/scaling_release_v1/object_component_inventory.csv')
PACKAGE_REL=Path('audit/rsi_continuation_round74_2026-11-17/integration_preparation_v1')
def sha(p):
 with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def overlay(root,summary):
 count=summary.get('source_identity_sidecar_additions',0)
 if not count:
  assert not summary.get('source_identity_sidecar_manifest_sha256'),'Undeclared source sidecar count'
  return [],{}
 assert type(count)is int and count==9,'Unsupported source sidecar count'
 sys.path.insert(0,str(root/'audit'))
 import round74_simready_object_overlay as provider
 assert provider.ROOT.resolve()==root.resolve(),'Object sidecar root differs'
 assert summary['source_identity_sidecar_manifest_sha256']==provider.PIN,'Object sidecar manifest authority differs'
 rows=provider.inventory_rows();assert len(rows)==count
 pins={}
 for path in provider.input_paths():
  if path.resolve()==Path(provider.__file__).resolve():rel=Path('audit/round74_simready_object_overlay.py')
  else:rel=PACKAGE_REL/path.relative_to(provider.PACKAGE)
  digest=sha(path);assert summary['input_sha256'].get(str(rel))==digest,('Undeclared/changed object sidecar dependency',str(rel))
  pins[str(rel)]=digest
 assert all(r['geometry_sha256']=='NOT_VERIFIED_PAYLOAD_GEOMETRY'and r['parts_completeness_status']=='NOT_CLAIMED_WHOLE_FALLBACK_ONLY'for r in rows)
 helper_pin=sha(Path(__file__));assert summary['input_sha256'].get('rsi_harness/current_object_inventory_v24.py')==helper_pin,'Undeclared/changed shared inventory reader'
 pins['rsi_harness/current_object_inventory_v24.py']=helper_pin
 return rows,pins

def iter_inventory(root,summary):
 """Stream raw rows, then append verified new UIDs; reject duplicate IDs/pairs/UIDs."""
 extra,_=overlay(root,summary)
 newids={r['object_id']for r in extra};newpairs={(r['object_id'],r['component_id'])for r in extra};newuids={(r['source_family'],r['source_asset_id'])for r in extra}
 with (root/OBJECT_REL).open(encoding='utf-8-sig',newline='')as f:
  for row in csv.DictReader(f):
   assert row['object_id']not in newids and(row['object_id'],row['component_id'])not in newpairs and(row['source_family'],row['source_asset_id'])not in newuids,'Registered source sidecar duplicates frozen inventory'
   yield row
 yield from extra
