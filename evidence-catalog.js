(() => {
  'use strict';
  const MANIFEST_PATH = 'evidence-catalog/sciglass/manifest.json';
  const $ = id => document.getElementById(id);
  const present = value => value !== null && value !== undefined && String(value).trim() !== '';
  const number = value => present(value) && Number.isFinite(Number(value)) ? Number(value) : null;
  const count = value => number(value) === null ? '—' : Number(value).toLocaleString('zh-CN');
  const naturalCompare = new Intl.Collator('en', { numeric: true, sensitivity: 'base' }).compare;
  const state = { manifest: null, type: 'COMPLETE', page: 0, records: [], query: '', loading: false, request: 0, lookup: 0, controller: null, focusedId: '', cache: new Map() };
  const typeButtons = [...document.querySelectorAll('[data-record-type]')];
  const params = new URLSearchParams(location.search);
  if (params.get('type') === 'INCOMPLETE') state.type = 'INCOMPLETE';
  state.page = Math.max(0, Number.parseInt(params.get('page') || '1', 10) - 1) || 0;
  const initialId = params.get('id') || '';
  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text !== undefined && text !== null) node.textContent = String(text);
    if (className) node.className = className;
    return node;
  }
  function status(message, notice = false) {
    $('catalog-status').textContent = message;
    $('catalog-status').classList.toggle('notice', notice);
  }
  function pages(type = state.type) { return state.manifest?.pages?.[type] || []; }
  function pretty(value) {
    if (!present(value)) return '—';
    try { return JSON.stringify(typeof value === 'string' ? JSON.parse(value) : value, null, 2); }
    catch { return String(value); }
  }
  function references(record) {
    const source = record.reference_ids;
    if (!present(source)) return [];
    if (Array.isArray(source)) return [...new Set(source.map(String))];
    try { const parsed = JSON.parse(source); if (Array.isArray(parsed)) return [...new Set(parsed.map(String))]; }
    catch { /* Original reference lists may be delimited text. */ }
    return [...new Set(String(source).replace(/^\[|\]$/g, '').split(/[;,|\s]+/).map(value => value.replace(/^['"]|['"]$/g, '').trim()).filter(Boolean))];
  }
  function sourceBoundary(record) {
    const ids = references(record);
    if (ids.length === 1) return { label: '单一引文', className: '', note: '数据库将本组关联到一条原文引用；尚未逐篇人工回查。' };
    if (ids.length > 1) return { label: '多引文组 · ' + ids.length + ' 条引用', className: 'multi', note: '本组关联多条引文；各属性的具体引用归属未逐篇回查，不能据此声称出自同一篇论文。三项齐全但归属不明的组应另行隔离。' };
    return { label: '引用归属待核', className: 'unknown', note: '本组没有可解析的引用 ID；应核对数据库原始引用字段。' };
  }
  function formatValue(normalized, original) {
    if (!present(original)) return { text: '—', missing: true };
    const parsed = number(normalized);
    if (parsed !== null) {
      if (parsed !== 0 && (Math.abs(parsed) < 0.0001 || Math.abs(parsed) >= 1e7)) return { text: parsed.toExponential(4), raw: false };
      return { text: new Intl.NumberFormat('en-US', { maximumSignificantDigits: 5 }).format(parsed), raw: false };
    }
    return present(original) ? { text: String(original), raw: true } : { text: '—', missing: true };
  }
  function safeSourceLink(url) {
    if (!present(url)) return null;
    try {
      const parsed = new URL(String(url), location.href);
      if (!['http:', 'https:'].includes(parsed.protocol)) return null;
      const a = el('a', String(url)); a.href = parsed.href; a.target = '_blank'; a.rel = 'noopener noreferrer'; return a;
    } catch { return null; }
  }
  function addDefinition(list, label, content) {
    const term = el('dt', label), definition = el('dd');
    if (content instanceof Node) definition.append(content);
    else definition.textContent = present(content) ? String(content) : '—';
    list.append(term, definition);
  }
  function detailsFor(record) {
    const detail = el('div', null, 'catalog-detail');
    detail.append(el('h3', '来源、成分与原始字段'));
    detail.append(el('p', sourceBoundary(record).note, 'boundary-note'));
    const list = el('dl');
    addDefinition(list, '记录 ID / 类型', (record.record_id || '—') + ' / ' + (record.record_type || '—'));
    addDefinition(list, '原文材料身份', record.material_identity);
    addDefinition(list, '原文引用 ID', references(record).join('；'));
    addDefinition(list, '引用状态', record.reference_status);
    addDefinition(list, '来源标题', record.source_title);
    addDefinition(list, '来源页面', safeSourceLink(record.url) || record.url);
    addDefinition(list, '原文定位', record.locator);
    addDefinition(list, '样品 / 条件组', record.conditions_or_group);
    addDefinition(list, 'E 原文字段', record.E_source_value);
    addDefinition(list, 'ν 原文字段', record.nu_source_value);
    addDefinition(list, 'ρ 原文字段', record.rho_source_value);
    addDefinition(list, '实际报告属性数', record.property_count);
    addDefinition(list, '成分（mol%）', pretty(record.composition_mol_percent_json));
    addDefinition(list, '引用元数据', pretty(record.citation_json));
    addDefinition(list, '保留源文件路径', record.local_file);
    addDefinition(list, '源文件 SHA-256', record.sha256);
    addDefinition(list, '条目限制', record.limitations);
    detail.append(list);
    const rawDetails = el('details');
    rawDetails.append(el('summary', '原文值与完整记录 JSON'), el('pre', JSON.stringify(record, null, 2)));
    detail.append(rawDetails);
    return detail;
  }
  function searchText(record) {
    return [record.record_id, record.material_identity, record.reference_ids, record.reference_status, record.source_title,
      record.composition_mol_percent_json, record.conditions_or_group, record.E_source_value, record.nu_source_value, record.rho_source_value]
      .map(value => typeof value === 'object' ? JSON.stringify(value) : String(value || '')).join(' ').toLocaleLowerCase();
  }
  function renderRecords() {
    const tbody = $('catalog-table-body'), fragment = document.createDocumentFragment();
    const query = state.query.trim().toLocaleLowerCase();
    const records = state.records.filter(record => !query || searchText(record).includes(query));
    if (!records.length) {
      const row = el('tr'), cell = el('td', state.loading ? '正在载入来源数据…' : (query ? '当前页没有匹配项。可清空搜索词或切换分页。' : '此类型暂无已接入记录。'), 'catalog-empty');
      cell.colSpan = 6; row.append(cell); fragment.append(row);
    }
    records.forEach((record, i) => {
      const row = el('tr', null, 'catalog-record'); row.dataset.recordId = record.record_id || '';
      if (record.record_id === state.focusedId) row.classList.add('focused');
      const identity = el('td'); identity.append(el('span', record.material_identity || '原文材料名未载入', 'catalog-material'), el('code', record.record_id || '—', 'catalog-record-id')); row.append(identity);
      [['E_GPa', 'E_source_value'], ['nu', 'nu_source_value'], ['rho_kg_m3', 'rho_source_value']].forEach(([normalized, original]) => {
        const cell = el('td'), formatted = formatValue(record[normalized], record[original]);
        cell.append(el('span', formatted.text, formatted.missing ? 'catalog-missing' : ''));
        if (formatted.raw) cell.append(el('small', '原文值；未转换单位', 'catalog-source-value'));
        row.append(cell);
      });
      const boundary = sourceBoundary(record), citation = el('td');
      citation.append(el('span', boundary.label, 'catalog-ref-badge ' + boundary.className), el('span', '引用 ID：' + (references(record).join('、') || '—'), 'catalog-reference-note')); row.append(citation);
      const action = el('td'), button = el('button', '展开来源 / 原文值', 'catalog-details-button');
      button.type = 'button'; button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', '展开 ' + (record.record_id || '该记录') + ' 的来源与原文值');
      const detailRow = el('tr'); detailRow.hidden = true;
      const detailId = 'record-detail-' + state.type.toLowerCase() + '-' + state.page + '-' + i;
      detailRow.id = detailId; button.setAttribute('aria-controls', detailId);
      button.addEventListener('click', () => {
        const opening = detailRow.hidden;
        if (opening && !detailRow.children.length) { const cell = el('td', null, 'catalog-detail-cell'); cell.colSpan = 6; cell.append(detailsFor(record)); detailRow.append(cell); }
        detailRow.hidden = !opening; button.setAttribute('aria-expanded', String(opening)); button.textContent = opening ? '收起来源详情' : '展开来源 / 原文值';
      });
      action.append(button); row.append(action); fragment.append(row, detailRow);
    });
    tbody.replaceChildren(fragment);
    if (!state.loading) status('当前页 ' + count(state.records.length) + ' 条，显示 ' + count(records.length) + ' 条' + (query ? '（仅搜索当前页）' : '') + '。');
  }
  function renderNavigation() {
    const allPages = pages();
    typeButtons.forEach(button => { button.setAttribute('aria-pressed', String(button.dataset.recordType === state.type)); button.disabled = !state.manifest; });
    $('previous-page').disabled = state.loading || !allPages.length || state.page === 0;
    $('next-page').disabled = state.loading || !allPages.length || state.page >= allPages.length - 1;
    $('page-jump-button').disabled = state.loading || !allPages.length;
    $('page-number').disabled = state.loading || !allPages.length;
    $('id-jump-button').disabled = !state.manifest;
    $('page-number').max = String(Math.max(1, allPages.length)); $('page-number').value = String(state.page + 1);
    $('page-position').textContent = allPages.length ? (state.page + 1) + ' / ' + allPages.length + ' 页' : '0 / 0 页';
    const spec = allPages[state.page];
    $('page-description').textContent = (state.type === 'COMPLETE' ? '完整来源组' : '不完整来源组') + ' · ' + allPages.length + ' 页' + (spec ? ' · 本页 ID ' + (spec.firstId || '—') + ' — ' + (spec.lastId || '—') : '');
  }
  function updateUrl() {
    const query = new URLSearchParams({ collection: 'sciglass', type: state.type, page: String(state.page + 1) });
    if (state.focusedId) query.set('id', state.focusedId);
    history.replaceState(null, '', location.pathname + '?' + query);
  }
  const bundleCache = new Map();
  async function fetchJson(path, signal) {
    const url = new URL(path, location.href);
    if (url.origin !== location.origin || path.startsWith('/') || path.split('/').includes('..')) throw new Error('分页路径必须位于本站目录。');
    const packed = url.pathname.endsWith('.json.gz');
    const pageKey = packed ? decodeURIComponent(url.hash.slice(1)) : '';
    if (packed && !pageKey) throw new Error('压缩分页路径缺少原始页文件名。');
    url.hash = '';
    const cacheKey = url.href;
    if (signal?.aborted) throw new DOMException('请求已取消。', 'AbortError');
    let result = packed ? bundleCache.get(cacheKey) : undefined;
    if (!result) {
      const response = await fetch(url, { signal });
      if (!response.ok) throw new Error('无法载入 ' + path + '（HTTP ' + response.status + '）');
      if (packed) {
        if (typeof DecompressionStream !== 'function') throw new Error('当前浏览器不支持 gzip 解压，请使用新版 Chrome、Edge、Firefox 或 Safari。');
        const bytes = new Uint8Array(await response.arrayBuffer());
        if (signal?.aborted) throw new DOMException('请求已取消。', 'AbortError');
        // Static hosts normally serve gzip files unchanged; also accept HTTP-decoded JSON.
        const compressed = bytes[0] === 0x1f && bytes[1] === 0x8b;
        result = compressed
          ? await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).json()
          : JSON.parse(new TextDecoder().decode(bytes));
        if (signal?.aborted) throw new DOMException('请求已取消。', 'AbortError');
        bundleCache.set(cacheKey, result);
        if (bundleCache.size > 3) bundleCache.delete(bundleCache.keys().next().value);
      } else return response.json();
    }
    if (!Object.prototype.hasOwnProperty.call(result, pageKey)) throw new Error('压缩包内缺少原始分页：' + pageKey);
    return result[pageKey];
  }
  async function loadPage(page = 0, { focusId = '', clearQuery = false } = {}) {
    if (!state.manifest) return;
    state.lookup += 1;
    const allPages = pages(), requestedPage = Math.min(Math.max(0, page), Math.max(0, allPages.length - 1));
    const serial = ++state.request;
    if (state.controller) state.controller.abort();
    state.controller = new AbortController(); state.page = requestedPage; state.focusedId = focusId;
    if (clearQuery) { state.query = ''; $('page-search').value = ''; }
    state.loading = true; state.records = []; $('catalog-error').hidden = true;
    renderNavigation(); renderRecords(); status('正在载入本页来源数据…'); updateUrl();
    if (!allPages.length) { state.loading = false; renderNavigation(); renderRecords(); return; }
    const spec = allPages[requestedPage];
    try {
      const pageData = state.cache.get(spec.path) || await fetchJson(spec.path, state.controller.signal);
      if (serial !== state.request) return;
      if (!Array.isArray(pageData.records)) throw new Error('分页文件缺少 records 数组。');
      if (Number(spec.count) !== pageData.records.length) throw new Error('分页清单条数与实际记录不一致。');
      if (pageData.records.some(record => record.record_type !== state.type)) throw new Error('分页记录类型与当前目录不一致。');
      if (pageData.records.length && ((spec.firstId && pageData.records[0].record_id !== spec.firstId) || (spec.lastId && pageData.records.at(-1).record_id !== spec.lastId))) throw new Error('分页首尾 ID 与清单不一致。');
      state.cache.set(spec.path, pageData); if (state.cache.size > 4) state.cache.delete(state.cache.keys().next().value);
      state.records = pageData.records; state.loading = false; renderNavigation(); renderRecords();
      if (focusId) {
        const found = state.records.find(record => record.record_id === focusId);
        if (found) { status('已定位 ' + focusId + '；当前为第 ' + (state.page + 1) + ' 页。'); requestAnimationFrame(() => [...$('catalog-table-body').querySelectorAll('[data-record-id]')].find(row => row.dataset.recordId === focusId)?.scrollIntoView({ block: 'nearest' })); }
        else status('已跳到 ID 范围对应页，但没有精确命中 ' + focusId + '。请核对完整 ID。', true);
      }
    } catch (error) {
      if (error.name === 'AbortError' || serial !== state.request) return;
      state.loading = false; state.records = []; renderNavigation(); renderRecords();
      $('catalog-error').hidden = false; $('error-message').textContent = error.message;
      status('本页载入失败；未显示其他分页的旧数据。', true);
    }
  }
  async function jumpToId(id) {
    const value = id.trim();
    if (!value) { status('请输入完整记录 ID。', true); $('record-id').focus(); return false; }
    const candidates = [];
    for (const type of [state.type, state.type === 'COMPLETE' ? 'INCOMPLETE' : 'COMPLETE']) {
      pages(type).forEach((page, index) => {
        if (present(page.firstId) && present(page.lastId) && naturalCompare(value, page.firstId) >= 0 && naturalCompare(value, page.lastId) <= 0) candidates.push({ type, index, spec: page });
      });
    }
    if (!candidates.length) { status('分页清单未找到 ' + value + ' 的 ID 范围；本操作不逐页搜索全文。请核对 ID。', true); return false; }
    const serial = ++state.lookup;
    state.request += 1;
    if (state.controller) state.controller.abort();
    state.controller = new AbortController(); state.loading = true;
    renderNavigation(); status('正在 ID 范围对应页中精确定位…');
    try {
      for (const candidate of candidates) {
        const data = state.cache.get(candidate.spec.path) || await fetchJson(candidate.spec.path, state.controller.signal);
        if (serial !== state.lookup) return false;
        if (!Array.isArray(data.records)) throw new Error('ID 定位分页缺少 records 数组。');
        state.cache.set(candidate.spec.path, data); if (state.cache.size > 4) state.cache.delete(state.cache.keys().next().value);
        if (data.records.some(record => record.record_id === value)) {
          state.type = candidate.type;
          await loadPage(candidate.index, { focusId: value, clearQuery: true });
          return true;
        }
      }
      state.loading = false; renderNavigation();
      status('已核对 ID 范围对应的完整 / 缺项分页，未精确命中 ' + value + '。请核对完整 ID。', true);
    } catch (error) {
      if (error.name === 'AbortError' || serial !== state.lookup) return false;
      state.loading = false; renderNavigation(); status('ID 定位失败：' + error.message, true);
    }
    return false;
  }
  function applyManifest(manifest) {
    if (manifest.collectionId !== 'sciglass' || !manifest.summary || !manifest.pages) throw new Error('目录清单不符合 SciGlass 数据接口。');
    for (const type of ['COMPLETE', 'INCOMPLETE']) if (!Array.isArray(manifest.pages[type])) throw new Error('目录缺少 ' + type + ' 分页清单。');
    for (const [type, field] of [['COMPLETE', 'completeRecords'], ['INCOMPLETE', 'incompleteRecords']]) {
      const summed = manifest.pages[type].reduce((total, page) => total + Number(page.count), 0);
      if (summed !== Number(manifest.summary[field])) throw new Error(type + ' 分页总数与目录统计不一致。');
    }
    if (Number(manifest.summary.completeRecords) + Number(manifest.summary.incompleteRecords) !== Number(manifest.summary.totalRecords)) throw new Error('完整 / 缺项 / 合计统计不一致。');
    state.manifest = manifest;
    $('catalog-title').textContent = manifest.label || 'SciGlass 来源数据组'; document.title = (manifest.label || 'SciGlass') + ' · 材料物性证据目录';
    for (const [id, field] of [['stat-complete', 'completeRecords'], ['stat-incomplete', 'incompleteRecords'], ['stat-total', 'totalRecords'], ['stat-citations', 'sourceCitationKeys'], ['stat-identities', 'sourceDefinedIdentities'], ['type-complete-count', 'completeRecords'], ['type-incomplete-count', 'incompleteRecords']]) $(id).textContent = count(manifest.summary[field]);
    const limitations = $('collection-limitations'); limitations.replaceChildren();
    if (Array.isArray(manifest.limitations)) manifest.limitations.forEach(value => limitations.append(el('li', typeof value === 'string' ? value : JSON.stringify(value))));
    limitations.hidden = !limitations.children.length;
  }
  async function init() {
    $('catalog-error').hidden = true; status('正在载入分页清单…');
    try {
      applyManifest(await fetchJson(MANIFEST_PATH));
      if (initialId) {
        $('record-id').value = initialId;
        if (!await jumpToId(initialId)) { await loadPage(state.page); status('未找到指定 ID，已显示当前类型首页。请核对完整 ID。', true); }
      }
      else await loadPage(state.page);
    } catch (error) {
      $('catalog-error').hidden = false; $('error-message').textContent = error.message; status('目录尚未成功载入。', true);
    }
  }
  typeButtons.forEach(button => button.addEventListener('click', () => { state.type = button.dataset.recordType; loadPage(0); }));
  $('previous-page').addEventListener('click', () => loadPage(state.page - 1));
  $('next-page').addEventListener('click', () => loadPage(state.page + 1));
  $('page-search').addEventListener('input', event => { state.query = event.target.value; state.focusedId = ''; renderRecords(); });
  $('id-jump-form').addEventListener('submit', event => { event.preventDefault(); if (state.manifest) jumpToId($('record-id').value); });
  $('page-jump-form').addEventListener('submit', event => { event.preventDefault(); const page = Number($('page-number').value); if (!Number.isInteger(page) || page < 1 || page > pages().length) { status('请输入有效页码。', true); return; } loadPage(page - 1); });
  $('retry-load').addEventListener('click', () => state.manifest ? loadPage(state.page) : init());
  renderNavigation(); init();
})();
