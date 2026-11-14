(() => {
  'use strict';
  const cache = new Map();
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const urlLink = (url, label) => /^https?:\/\//i.test(url || '') ? '<a href="' + esc(url) + '" target="_blank" rel="noopener noreferrer">' + esc(label) + '</a>' : '';
  const kindLabel = {semantic_component:'作者语义组件（不是机械零件）',whole_fallback:'WHOLE整件回退（内部机械部件未枚举）',source_defined_component_scope:'来源定义组件／局部范围'};
  async function readPinned(pin) {
    const key = pin.file + '#' + pin.sha256;
    if (!cache.has(key)) cache.set(key, (async () => {
      const parsed = new URL(pin.file, location.href);
      if (parsed.origin !== location.origin) throw new Error('组件明细地址不属于本站');
      const response = await fetch(parsed.href + (parsed.search ? '&' : '?') + 'v=' + pin.sha256.slice(0, 12), {signal:AbortSignal.timeout(30000)});
      if (!response.ok) throw new Error('组件明细载入失败：HTTP ' + response.status);
      const bytes = new Uint8Array(await response.arrayBuffer());
      const digest = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(v => v.toString(16).padStart(2, '0')).join('');
      if (digest !== pin.sha256) throw new Error('组件明细与当前发布版本不一致');
      return JSON.parse(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text());
    })().catch(error => {cache.delete(key);throw error;}));
    return cache.get(key);
  }
  document.addEventListener('click', async event => {
    const button = event.target.closest('[data-c34-object-detail]');
    if (!button) return;
    const host = button.parentElement;
    let box = host.querySelector('[data-c34-detail-body]');
    if (box) {box.hidden = !box.hidden;return;}
    box = document.createElement('div');box.dataset.c34DetailBody = '';box.setAttribute('aria-live','polite');host.appendChild(box);
    button.disabled = true;box.textContent = '正在校验并载入所有组件…';
    try {
      const data = await readPinned({file:button.dataset.c34ObjectDetail,sha256:button.dataset.sha256});
      if (data.objectId !== button.dataset.objectId) throw new Error('组件详情对象身份不一致');
      const search = document.createElement('input');search.type='search';search.placeholder='搜索组件、材料或来源定位';search.setAttribute('aria-label','搜索当前对象全部组件');
      const status = document.createElement('p');const table = document.createElement('table');box.textContent='';box.append(search,status,table);
      const draw = () => {
        const q = search.value.trim().toLowerCase();
        const rows = data.components.filter(c => JSON.stringify([c.componentId,c.componentPath,c.scope,c.materialLabels,c.materialIds,(c.sourceRelations || []).map(r => r.sourceLocator)]).toLowerCase().includes(q));
        status.textContent = '来源组件范围 ' + rows.length + ' / ' + data.components.length + '；材料选项不是同时组成；无数值赋值。';
        table.innerHTML = '<thead><tr><th>组件与范围</th><th>材料关系</th><th>来源</th></tr></thead><tbody>' + rows.map(c => {
          const links = (c.reviewedMaterialLinks || []).map(r => '<p>' + esc(r.targetMaterialId) + ' · ' + esc(r.relationMode) + ' · ' + esc(r.relationResolution) + '<br>' + esc(r.materialScope) + '</p>').join('');
          const evidence = (c.sourceRelations || []).map(r => '<details><summary>' + esc(r.sourceLabelCn || r.sourceLabelRaw) + ' · ' + esc(r.relationType) + '</summary><p>' + esc(r.sourceQuote) + '</p><p>' + urlLink(r.sourceUrl,'证据来源') + ' ' + esc(r.sourceLocator) + '</p><small>SHA-256 ' + esc(r.sourceSha256) + '</small></details>').join('');
          return '<tr><td>' + esc(c.componentId) + '<br>' + esc(kindLabel[c.componentKind] || c.componentKind) + '<p>' + esc(c.scope) + '</p><small>状态行 ' + c.stateRows + '</small></td><td>' + esc(c.materialLabels.join('；')) + links + (c.heldGeometryOnly ? '<strong>全部选项暂缓，仅保留几何／范围身份</strong>' : '') + '</td><td>' + evidence + '</td></tr>';
        }).join('') + '</tbody>';
      };
      search.addEventListener('input',draw);draw();
    } catch(error) {box.textContent=error.message;box.removeAttribute('data-c34-detail-body');}
    finally {button.disabled=false;}
  });
})();
