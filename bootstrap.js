window.MATERIAL_PAYLOAD_READY=(async()=>{
 const get=async path=>{const r=await fetch(path);if(!r.ok)throw Error(path+' HTTP '+r.status);return r.json()};
 const version='RSI-CORRECTED-02d66743593774e4';const release=window.DATASET_RELEASE=await get('snapshot.json?v='+version);
 window.verifyDatasetView=(kind,data)=>{const id=kind==='materials'?data?.meta?.releaseId:data?.releaseId;const ok=id===release.id;if(!ok)throw Error('页面数据快照不一致');return ok};
 if(location.pathname.endsWith('research.html'))window.SITE_DATA=await get('research.json?v='+version);
 if(location.pathname.endsWith('references.html'))window.PHASE1_RANGES=await get('coverage.json?v='+version);
})().catch(error=>{document.addEventListener('DOMContentLoaded',()=>{document.body.prepend(Object.assign(document.createElement('p'),{className:'release-mismatch',textContent:'数据载入失败：'+error.message+'。请重新载入。'}))});throw error});
