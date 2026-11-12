(async () => { if (window.MATERIAL_PAYLOAD_READY) await window.MATERIAL_PAYLOAD_READY;
(function () {
  "use strict";
  const data = window.TARGET_REFERENCE_DATA;
  const fmt = (value) => Number(value || 0).toLocaleString("zh-CN");
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
  const labels = { EXACT_IDENTITY: "同材料身份 · 工况待核", CONDITIONAL_SUBTYPE_REFERENCE: "细材料条件参考", FAMILY_COVERAGE_ONLY: "仅家族覆盖", NO_MATCHED_COMPLETE_TRIPLET: "当前无匹配完整证据" };
  const families = { metal: "金属", glass: "玻璃", ceramic: "陶瓷", stone: "石材", polymer: "聚合物", rubber: "橡胶", foam: "泡沫", wood: "木材", textile: "纺织", paper: "纸材", leather: "皮革", biomaterial: "生物材料", other_media: "其他介质" };
  if (!data) { document.getElementById("target-content").textContent = "材料连接数据未载入。请检查 target-reference-data.js。"; return; }
  let selected = data.targets.find((item) => item.id === new URLSearchParams(location.search).get("material")) || data.targets[0];
  let limit = 30;
  const query = document.getElementById("target-search");
  const family = document.getElementById("target-family");
  const status = document.getElementById("target-status");
  const list = document.getElementById("target-list");
  const content = document.getElementById("target-content");
  document.getElementById("target-total").textContent = fmt(data.summary.target_count);
  document.getElementById("target-with-reference").textContent = fmt(data.summary.targets_with_any_reference);
  document.getElementById("target-without-reference").textContent = fmt(data.summary.targets_without_reference);
  document.getElementById("target-documents").textContent = fmt(data.summary.source_document_count);
  Object.entries(families).forEach(([key, value]) => family.add(new Option(value, key)));
  Object.entries(labels).forEach(([key, value]) => status.add(new Option(value, key)));

  function safeLink(value) { return /^https?:\/\//i.test(value || "") ? value : ""; }
  function value(values, unit) {
    const scalar = values.length === 1 || Number(values[0]) === Number(values[1]);
    return escapeHtml(scalar ? values[0] : values.join("–")) + (unit ? " " + unit : "");
  }
  function renderList() {
    const text = query.value.trim().toLowerCase();
    const rows = data.targets.filter((item) => (!family.value || item.family === family.value) && (!status.value || item.status === status.value) && (!text || [item.nameCn, item.nameEn, item.id].join(" ").toLowerCase().includes(text)));
    document.getElementById("target-list-count").textContent = fmt(rows.length) + " / " + fmt(data.targets.length) + " 个材料标签";
    list.innerHTML = rows.map((item) => '<button type="button" class="target-row' + (selected.id === item.id ? ' selected' : '') + '" data-target-id="' + escapeHtml(item.id) + '" aria-pressed="' + String(selected.id === item.id) + '"><strong>' + escapeHtml(item.nameCn) + '</strong><span>' + escapeHtml(item.nameEn) + '</span><small>' + escapeHtml(labels[item.status]) + ' · ' + fmt(item.references.length) + ' 条参考</small></button>').join("") || '<p class="empty-inline">没有匹配的材料标签。</p>';
    list.querySelectorAll("[data-target-id]").forEach((button) => button.addEventListener("click", () => {
      selected = data.targets.find((item) => item.id === button.dataset.targetId); limit = 30;
      history.replaceState(null, "", "?material=" + encodeURIComponent(selected.id)); renderList(); renderDetail();
    }));
  }
  function recordHtml(reference, index) {
    const record = data.records[reference.recordId];
    const url = safeLink(record.url);
    return '<details class="evidence-item"' + (index === 0 ? ' open' : '') + '><summary><span class="evidence-summary"><span><strong>' + escapeHtml(record.material) + '</strong><small>' + escapeHtml(labels[reference.kind]) + ' · ' + escapeHtml(record.id) + '</small></span></span></summary><div class="evidence-content"><p class="boundary-note">' + escapeHtml(reference.limits) + '</p><div class="evidence-values"><div><span>来源材料的杨氏模量 E</span><strong>' + value(record.E, 'GPa') + '</strong></div><div><span>来源材料的泊松比 ν</span><strong>' + value(record.nu, '') + '</strong></div><div><span>来源材料的密度 ρ</span><strong>' + value(record.rho, 'kg/m³') + '</strong></div></div><dl class="evidence-meta">' + [
      ['来源文档', record.title], ['发布主体', record.publisher], ['原文定位', record.locator],
      ['原始条件', record.conditions], ['方法/数值性质', record.method], ['来源限制', record.limitations],
      ['方向化数值', record.directionalValues],
      ['条件复核状态', reference.conditionStatus], ['关系规则', reference.rule], ['文档去重键', record.documentKey], ['冻结SHA-256', record.sha256]
    ].filter((pair) => pair[1]).map(([label, text]) => '<div><dt>' + escapeHtml(label) + '</dt><dd>' + escapeHtml(text) + '</dd></div>').join('') + '</dl><div class="object-links">' + (url ? '<a href="' + escapeHtml(url) + '" target="_blank" rel="noopener noreferrer">打开原始来源</a>' : '') + '<a href="research.html?node=' + encodeURIComponent(record.researchNodeId) + '">查看来源材料叶节点</a></div></div></details>';
  }
  function renderDetail() {
    const references = [...selected.references].sort((a, b) => Object.keys(labels).indexOf(a.kind) - Object.keys(labels).indexOf(b.kind));
    content.innerHTML = '<div class="detail-header"><p class="edition">' + escapeHtml(families[selected.family]) + ' · ' + escapeHtml(labels[selected.status]) + '</p><h2>' + escapeHtml(selected.nameCn) + '</h2><p class="detail-en">' + escapeHtml(selected.nameEn) + '</p><p class="target-id">' + escapeHtml(selected.id) + '</p></div><div class="detail-body"><section class="detail-section"><h3>材料标签与证据的关系</h3><div class="metric-grid"><div class="metric"><span>同身份记录</span><strong>' + fmt(selected.exact) + '</strong></div><div class="metric"><span>细材料参考</span><strong>' + fmt(selected.conditional) + '</strong></div><div class="metric"><span>仅家族覆盖</span><strong>' + fmt(selected.familyOnly) + '</strong></div><div class="metric"><span>关联文档文件键</span><strong>' + fmt(selected.documents) + '</strong></div></div><p class="boundary-note">数值属于下列来源材料，不是此宽标签的统一常数。材料关系与工况兼容性分开；没有自动新增对象赋值。</p><p class="node-note">' + escapeHtml(selected.note) + '</p><p class="node-note">对象材料表有 ' + fmt(selected.formalRows) + ' 条正式材料身份映射；近似标签层覆盖 ' + fmt(selected.coveredRows) + ' 条组件材料选项记录。该数量不表示它们已获得三元组赋值。</p></section><section class="detail-section"><h3>逐来源三元组与适用限制</h3><div class="evidence-list">' + (references.length ? references.slice(0, limit).map(recordHtml).join('') : '<p class="empty-inline">当前完整三元组库没有匹配此标签的来源。没有用零、默认值或其他材料补齐；这不表示全网不存在相关资料。</p>') + '</div>' + (references.length > limit ? '<button type="button" id="target-more" class="load-more">再显示30条（共' + fmt(references.length) + '条）</button>' : '') + '</section></div>';
    const more = document.getElementById("target-more");
    if (more) more.addEventListener("click", () => { limit += 30; renderDetail(); });
  }
  [query, family, status].forEach((input) => input.addEventListener("input", renderList));
  renderList(); renderDetail();
})();

})();
