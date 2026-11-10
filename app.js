(function () {
  "use strict";

  const data = window.SITE_DATA;
  const hasD3 = typeof window.d3 !== "undefined";
  if (!data || !hasD3) {
    document.body.innerHTML = '<div class="fatal-error" role="alert">网站资源未完整载入。请确认 data.js、vendor/d3.min.js 和 vendor/lucide.min.js 均已部署。</div>';
    return;
  }

  const d3 = window.d3;
  const fmt = (value) => Number(value || 0).toLocaleString("zh-CN");
  const nodesById = new Map(data.nodes.map((node) => [node.id, { ...node, childIds: [], level: 0 }]));
  const parentless = [];
  nodesById.forEach((node) => {
    if (node.parentId && node.parentId !== node.id && nodesById.has(node.parentId)) nodesById.get(node.parentId).childIds.push(node.id);
    else parentless.push(node.id);
  });
  nodesById.forEach((node) => node.childIds.sort((a, b) => nodesById.get(a).nameCn.localeCompare(nodesById.get(b).nameCn, "zh-CN")));
  const rootId = nodesById.has("MATERIAL_TREE_ROOT") ? "MATERIAL_TREE_ROOT" : parentless[0];
  const levelQueue = [{ id: rootId, level: 0 }];
  const leveled = new Set();
  while (levelQueue.length) {
    const current = levelQueue.shift();
    if (leveled.has(current.id)) continue;
    leveled.add(current.id);
    const node = nodesById.get(current.id);
    node.level = current.level;
    node.childIds.forEach((id) => levelQueue.push({ id, level: current.level + 1 }));
  }

  const expanded = new Set([rootId]);
  let selectedId = rootId;
  let visibleLayout = new Map();
  let lastTreeBounds = null;
  let nodeFocusActive = false;
  let focusedScale = null;
  let objectPageSize = 30;
  let objectFilter = "";

  const svg = d3.select("#tree-svg");
  const zoomLayer = svg.select(".zoom-layer");
  const canvas = document.getElementById("tree-canvas");
  const zoom = d3.zoom().scaleExtent([0.1, 2.4]).on("zoom", (event) => {
    zoomLayer.attr("transform", event.transform);
  }).on("end", handleZoomEnd);
  svg.call(zoom).on("dblclick.zoom", null);

  function iconRefresh() {
    if (window.lucide) window.lucide.createIcons({ attrs: { "stroke-width": 1.8 } });
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char]));
  }

  function compactText(value, limit) {
    const text = String(value || "").trim();
    return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
  }

  function safeUrl(value) {
    const url = String(value || "").trim();
    return /^https?:\/\//i.test(url) ? url : "";
  }

  function formatRange(values, unit) {
    if (!Array.isArray(values) || !values.length) return "未提供";
    const normalized = values.map((value) => String(value).trim()).filter(Boolean);
    if (!normalized.length) return "未提供";
    const result = normalized.length === 1 || normalized.every((value) => value === normalized[0]) ? normalized[0] : `${normalized[0]}–${normalized[normalized.length - 1]}`;
    return `${escapeHtml(result)}${unit ? ` ${unit}` : ""}`;
  }

  function nodeKind(node) {
    if (node.propertyStatus === "AGGREGATE_ONLY_NO_PARENT_TRIPLET") return ["子树汇总", "aggregate"];
    if ((data.evidenceByNode[node.id] || []).length) return ["完整三元组", "evidenced"];
    if (node.childIds.length) return ["分类/材料族", "category"];
    return ["材料身份", "identity"];
  }

  function setStats() {
    const meta = data.meta;
    document.getElementById("edition").textContent = meta.edition || "v3 双表发布版";
    document.getElementById("stat-full-objects").textContent = fmt(meta.fullObjectCount);
    document.getElementById("stat-full-rows").textContent = fmt(meta.fullComponentRows);
    const coverage = meta.approximateCoverage || {};
    document.getElementById("stat-label-coverage").textContent = `${fmt(coverage.covered_source_status_rows)} / ${fmt(coverage.input_source_status_rows)}`;
    document.getElementById("stat-search-materials").textContent = fmt(coverage.unique_material_names_or_nodes);
    document.getElementById("stat-evidence-nodes").textContent = fmt(meta.materialNodesWithEvidence);
    document.getElementById("stat-evidence").textContent = fmt(meta.evidenceCount);
    document.getElementById("stat-covered-rows").textContent = fmt(coverage.covered_source_status_rows);
    document.getElementById("stat-uncovered-rows").textContent = fmt(coverage.uncovered_source_status_rows);
    document.getElementById("stat-assignment-rows").textContent = fmt(coverage.assignment_rows_after_option_expansion);
    document.getElementById("stat-approx-names").textContent = fmt(coverage.approximate_canonical_material_names);
    document.getElementById("stat-special-domains").textContent = fmt(coverage.special_non_material_domains);
    const audit = document.getElementById("audit-pill");
    const passed = meta.auditGate === "PASS_TWO_TABLE_V3_STRUCTURAL_GATE";
    audit.textContent = passed ? "结构审计通过 · 0 错误" : (meta.auditGate || "结构审计状态缺失");
    audit.classList.toggle("fail", !passed);
  }

  function renderTripletPriorities() {
    const target = document.getElementById("triplet-priorities");
    const rows = data.meta.tripletPriorities || [];
    if (!rows.length) {
      target.innerHTML = '<p class="empty-inline">当前发布包没有三元组搜集排程。</p>';
      return;
    }
    target.innerHTML = rows.slice(0, 12).map((row) => `<article class="priority-item"><span class="priority-rank">${fmt(row.rank)}</span><div><h3>${escapeHtml(row.nameCn)}</h3><p>${escapeHtml(row.nameEn)}</p></div><dl><div><dt>覆盖组件</dt><dd>${fmt(row.coveredRows)}</dd></div><div><dt>覆盖对象</dt><dd>${fmt(row.coveredObjects)}</dd></div></dl><span class="priority-kind ${row.identityLevel === "FORMAL_SOURCE_GROUNDED_NODE" ? "formal" : "approx"}">${row.identityLevel === "FORMAL_SOURCE_GROUNDED_NODE" ? "正式节点" : "近似检索名"}</span></article>`).join("");
  }

  function renderSourceCoverage() {
    const target = document.getElementById("source-coverage");
    const rows = data.meta.sourceCoverage || [];
    if (!rows.length) {
      target.innerHTML = '<p class="empty-inline">当前发布包没有来源对账表。</p>';
      return;
    }
    target.innerHTML = `<table><thead><tr><th>来源</th><th>报告/清单</th><th>入库对象</th><th>组件行</th><th>正式映射</th><th>资产状态</th><th>剩余问题</th></tr></thead><tbody>${rows.map((row) => `<tr><th scope="row">${escapeHtml(row.source)}</th><td>${escapeHtml(row.reported_or_manifest_count)}</td><td>${escapeHtml(row.ingested_unique_objects)}</td><td>${escapeHtml(row.component_rows)}</td><td>${escapeHtml(row.formal_mapping_rows)}</td><td><span class="coverage-status">${escapeHtml(row.asset_enumeration)}</span></td><td>${escapeHtml(row.remaining_issue)}</td></tr>`).join("")}</tbody></table>`;
  }

  function nestedVisible(id, ancestors = new Set()) {
    const node = nodesById.get(id);
    if (!node || ancestors.has(id)) return null;
    const next = new Set(ancestors);
    next.add(id);
    return { ...node, children: expanded.has(id) ? node.childIds.map((childId) => nestedVisible(childId, next)).filter(Boolean) : null };
  }

  function treeLinkPath(item) {
    const midY = (item.source.y + item.target.y) / 2;
    return `M${item.source.x},${item.source.y + 38} C${item.source.x},${midY} ${item.target.x},${midY} ${item.target.x},${item.target.y - 38}`;
  }

  function updateTreeBounds(items) {
    const xExtent = d3.extent(items, (item) => item.x);
    const yExtent = d3.extent(items, (item) => item.y);
    lastTreeBounds = { x: xExtent[0] - 110, y: yExtent[0] - 50, width: Math.max(220, xExtent[1] - xExtent[0] + 220), height: Math.max(150, yExtent[1] - yExtent[0] + 145) };
  }

  function enableNodeDragging(nodeGroups, linkPaths) {
    nodeGroups.call(d3.drag().clickDistance(4)
      .on("start", function (event) {
        event.sourceEvent?.stopPropagation();
        nodeFocusActive = false;
        focusedScale = null;
        d3.select(this).classed("dragging", true);
      })
      .on("drag", function (event, item) {
        item.x = event.x;
        item.y = event.y;
        d3.select(this).attr("transform", `translate(${item.x},${item.y})`);
        linkPaths.attr("d", treeLinkPath);
      })
      .on("end", function () {
        d3.select(this).classed("dragging", false);
        updateTreeBounds(Array.from(visibleLayout.values()));
      }));
  }

  function renderTree(options = {}) {
    const rootData = nestedVisible(rootId);
    if (!rootData) return;
    const root = d3.hierarchy(rootData);
    d3.tree().nodeSize([218, 150])(root);
    const items = root.descendants();
    visibleLayout = new Map(items.map((item) => [item.data.id, item]));
    updateTreeBounds(items);
    zoomLayer.selectAll("*").remove();
    const linkPaths = zoomLayer.append("g").attr("aria-hidden", "true").selectAll("path")
      .data(root.links()).join("path").attr("class", "tree-link").attr("d", treeLinkPath);
    const groups = zoomLayer.append("g").selectAll("g.node")
      .data(items, (item) => item.data.id).join("g")
      .attr("class", (item) => `node ${item.data.id === selectedId ? "selected" : ""}`)
      .attr("transform", (item) => `translate(${item.x},${item.y})`)
      .attr("role", "button").attr("tabindex", 0)
      .attr("aria-label", (item) => `${item.data.nameCn}，${nodeKind(item.data)[0]}，子树 ${fmt(item.data.subtreeObjectCount)} 个对象`)
      .on("click", (event, item) => { if (!event.defaultPrevented) activateNode(item.data.id, true); })
      .on("keydown", (event, item) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activateNode(item.data.id, true); } });
    enableNodeDragging(groups, linkPaths);
    groups.append("rect").attr("class", "node-card").attr("x", -100).attr("y", -38).attr("width", 200).attr("height", 76).attr("rx", 5);
    groups.append("rect").attr("class", (item) => `node-accent ${nodeKind(item.data)[1]}`).attr("x", -100).attr("y", -38).attr("width", 5).attr("height", 76).attr("rx", 2);
    groups.append("text").attr("class", "node-title").attr("x", -86).attr("y", -13).text((item) => compactText(item.data.nameCn, 12));
    groups.append("text").attr("class", "node-subtitle").attr("x", -86).attr("y", 7).text((item) => compactText(item.data.nameEn, 28));
    groups.append("text").attr("class", "node-count").attr("x", -86).attr("y", 27).text((item) => `L${item.data.level} · ${fmt(item.data.subtreeObjectCount)} 对象 · ${fmt(item.data.evidenceCount)} 证据`);
    const toggles = groups.filter((item) => item.data.childIds.length > 0);
    toggles.append("circle").attr("class", "node-toggle").attr("cx", 0).attr("cy", 50).attr("r", 11);
    toggles.append("text").attr("class", "node-toggle-symbol").attr("x", 0).attr("y", 55).text((item) => expanded.has(item.data.id) ? "−" : "+");
    document.getElementById("visible-summary").textContent = `当前显示 ${items.length} / ${data.meta.materialNodeCount} 个节点 · ${fmt(data.meta.formalObjectCount)} 个对象已有正式材料映射`;
    document.getElementById("expand-all").querySelector("span").textContent = [...nodesById.values()].filter((node) => node.childIds.length).every((node) => expanded.has(node.id)) ? "全部收起" : "展开全部";
    if (options.fit) requestAnimationFrame(() => fitTree(false));
    if (options.focusId) requestAnimationFrame(() => centerNode(options.focusId));
  }

  function fitTree(animate = true) {
    if (!lastTreeBounds) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    if (!width || !height) return;
    nodeFocusActive = false;
    focusedScale = null;
    const padding = width < 520 ? 24 : 46;
    const scale = Math.max(0.1, Math.min(1.2, (width - padding * 2) / lastTreeBounds.width, (height - padding * 2) / lastTreeBounds.height));
    const centerX = lastTreeBounds.x + lastTreeBounds.width / 2;
    const transform = d3.zoomIdentity.translate(width / 2 - centerX * scale, padding - lastTreeBounds.y * scale).scale(scale);
    if (animate) svg.transition().duration(260).call(zoom.transform, transform); else svg.call(zoom.transform, transform);
  }

  function centerNode(id) {
    const item = visibleLayout.get(id);
    if (!item) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const fitScale = Math.min(1.2, (width - 92) / lastTreeBounds.width, (height - 92) / lastTreeBounds.height);
    const densityScale = 1.16 - Math.max(0, Math.log2(Math.max(1, visibleLayout.size) / 6)) * 0.13;
    const scale = Math.max(width < 620 ? 0.5 : 0.58, Math.min(width < 620 ? 0.88 : 1.12, Math.max(fitScale * 1.45, densityScale)));
    nodeFocusActive = true;
    focusedScale = scale;
    svg.transition().duration(340).call(zoom.transform, d3.zoomIdentity.translate(width / 2 - item.x * scale, height / 2 - item.y * scale).scale(scale));
  }

  function handleZoomEnd(event) {
    if (!nodeFocusActive || !focusedScale || event.sourceEvent?.type !== "wheel") return;
    if (event.transform.k <= focusedScale * 0.88) fitTree(true);
  }

  function ancestorsOf(id) {
    const path = [];
    const seen = new Set();
    let current = nodesById.get(id);
    while (current && !seen.has(current.id)) {
      seen.add(current.id);
      path.unshift(current);
      current = current.parentId ? nodesById.get(current.parentId) : null;
    }
    return path;
  }

  function revealNode(id) {
    ancestorsOf(id).slice(0, -1).forEach((node) => expanded.add(node.id));
    selectedId = id;
    objectPageSize = 30;
    objectFilter = "";
    renderTree({ focusId: id });
    renderDetail(nodesById.get(id));
  }

  function activateNode(id, toggleChildren) {
    const node = nodesById.get(id);
    if (!node) return;
    const wasSelected = selectedId === id;
    selectedId = id;
    objectPageSize = 30;
    objectFilter = "";
    if (toggleChildren && node.childIds.length) {
      if (wasSelected && expanded.has(id)) expanded.delete(id); else expanded.add(id);
    }
    renderTree({ focusId: id });
    renderDetail(node);
  }

  function detailPair(label, value) {
    const text = String(value || "").trim();
    return text ? `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(text)}</dd></div>` : "";
  }

  function evidenceHtml(node) {
    const records = data.evidenceByNode[node.id] || [];
    if (!records.length) {
      const message = node.propertyStatus === "AGGREGATE_ONLY_NO_PARENT_TRIPLET" ? "此处显示的是当前子树的证据数量；父节点本身没有可直接赋值的 E、ν、ρ。" : "该节点目前只有材料身份映射，没有已放行的完整 E、ν、ρ 记录。";
      return `<p class="empty-inline">${message}</p>`;
    }
    return `<div class="evidence-list">${records.map((item, index) => {
      const url = safeUrl(item.url);
      return `<details class="evidence-item" ${index === 0 ? "open" : ""}><summary><span class="evidence-summary"><span><strong>${escapeHtml(item.title || item.id)}</strong><small>${escapeHtml(item.sourceType)} · ${escapeHtml(item.sourceId)} · ${escapeHtml(item.id)}</small></span><i class="summary-chevron" data-lucide="chevron-down" aria-hidden="true"></i></span></summary><div class="evidence-content"><div class="evidence-values"><div><span>杨氏模量 E</span><strong>${formatRange(item.E, "GPa")}</strong></div><div><span>泊松比 ν</span><strong>${formatRange(item.nu, "")}</strong></div><div><span>密度 ρ</span><strong>${formatRange(item.rho, "kg/m³")}</strong></div></div><dl class="evidence-meta">${detailPair("原文定位", item.locator)}${detailPair("材料/牌号", item.grade)}${detailPair("温度与环境", item.environment)}${detailPair("方向", item.orientation)}${detailPair("方法", item.method)}${detailPair("局限", item.limitations)}</dl>${url ? `<a class="source-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">打开原始来源 <i data-lucide="external-link" aria-hidden="true"></i></a>` : ""}</div></details>`;
    }).join("")}</div>`;
  }

  function filteredObjects(node) {
    const query = objectFilter.trim().toLocaleLowerCase("zh-CN");
    return (data.objectsByNode[node.id] || []).filter((item) => !query || [item.id, item.componentId, item.nameCn, item.nameEn, item.scope, item.sourceDataset].join(" ").toLocaleLowerCase("zh-CN").includes(query));
  }

  function objectHtml(item) {
    const assetUrl = safeUrl(item.assetUrl);
    const sourceUrl = safeUrl(item.sourceUrl);
    return `<article class="object-item"><h4>${escapeHtml(item.nameCn || item.nameEn || item.id)}</h4><p class="object-en">${escapeHtml(item.nameEn)}</p><div class="object-tags"><span>${escapeHtml(item.id)}</span><span>${escapeHtml(item.componentId)}</span><span>${escapeHtml(item.scope || "整件/范围未写")}</span><span>${escapeHtml(item.sourceDataset)}</span>${assetUrl ? '<span class="asset-ok">有资产链接</span>' : ""}</div><div class="object-links">${assetUrl ? `<a href="${escapeHtml(assetUrl)}" target="_blank" rel="noopener noreferrer">打开 3D 资产</a>` : '<span class="empty-inline">无可点击资产链接</span>'}${sourceUrl ? `<a href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">打开材料/对象来源</a>` : ""}</div>${item.limitations ? `<p class="object-limitations">${escapeHtml(item.limitations)}</p>` : ""}</article>`;
  }

  function renderObjectList(node) {
    const items = filteredObjects(node);
    const target = document.getElementById("object-list");
    const button = document.getElementById("load-more");
    const note = document.getElementById("object-count-note");
    if (!target) return;
    target.innerHTML = items.slice(0, objectPageSize).map(objectHtml).join("") || '<p class="empty-inline">本节点没有符合当前搜索的直接组件映射。分类节点的对象位于其子节点中。</p>';
    note.textContent = `显示 ${fmt(Math.min(items.length, objectPageSize))} / ${fmt(items.length)} 条直接组件映射`;
    button.hidden = items.length <= objectPageSize;
  }

  function renderDetail(node) {
    if (!node) return;
    const kind = nodeKind(node);
    const path = ancestorsOf(node.id);
    const aggregateOnly = node.propertyStatus === "AGGREGATE_ONLY_NO_PARENT_TRIPLET";
    const directObjects = data.objectsByNode[node.id] || [];
    const content = document.getElementById("detail-content");
    content.innerHTML = `<div class="detail-header"><div class="detail-path">${path.map((item) => `<button type="button" class="crumb-button" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.nameCn)}</button>`).join("")}</div><div class="detail-title-row"><div><h2 id="detail-heading">${escapeHtml(node.nameCn)}</h2><p class="detail-en">${escapeHtml(node.nameEn)} · ${escapeHtml(node.id)}</p></div><span class="type-label ${kind[1]}">${kind[0]}</span></div></div><div class="detail-body"><section class="detail-section"><h3>节点范围</h3><div class="metric-grid"><div class="metric"><span>直接映射对象</span><strong>${fmt(node.directObjectCount)}</strong></div><div class="metric"><span>直接组件映射</span><strong>${fmt(node.directComponentCount)}</strong></div><div class="metric"><span>当前子树对象</span><strong>${fmt(node.subtreeObjectCount)}</strong></div><div class="metric"><span>${aggregateOnly ? "子树证据记录" : "直接证据记录"}</span><strong>${fmt(node.evidenceCount)}</strong></div></div>${node.childIds.length ? '<p class="boundary-note">子树数字只用于了解覆盖规模。子节点的材料和物性不会自动上推给此父节点。</p>' : ""}${node.notes ? `<p class="node-note">${escapeHtml(node.notes)}</p>` : ""}</section><section class="detail-section"><div class="section-heading-row"><h3>完整三元组证据</h3><p>逐来源并列，不平均</p></div>${evidenceHtml(node)}</section><section class="detail-section"><div class="section-heading-row"><h3>直接映射的对象与组件</h3><p id="object-count-note"></p></div><div class="object-tools"><input id="object-filter" type="search" placeholder="筛选当前节点的对象、组件或来源" aria-label="筛选当前节点对象"></div><div id="object-list" class="object-list"></div><button type="button" id="load-more" class="load-more">再显示 30 条</button>${directObjects.length > 200 ? '<p class="node-note">页面按需展示；完整记录保留在正式 CSV 中。</p>' : ""}</section></div>`;
    content.querySelectorAll(".crumb-button").forEach((button) => button.addEventListener("click", () => revealNode(button.dataset.nodeId)));
    document.getElementById("object-filter").addEventListener("input", (event) => { objectFilter = event.target.value; objectPageSize = 30; renderObjectList(node); });
    document.getElementById("load-more").addEventListener("click", () => { objectPageSize += 30; renderObjectList(node); });
    renderObjectList(node);
    iconRefresh();
  }

  function globalView() {
    expanded.clear();
    expanded.add(rootId);
    selectedId = rootId;
    objectFilter = "";
    objectPageSize = 30;
    renderTree({ fit: true });
    renderDetail(nodesById.get(rootId));
  }

  function updateSearch() {
    const input = document.getElementById("tree-search");
    const results = document.getElementById("search-results");
    const query = input.value.trim().toLocaleLowerCase("zh-CN");
    if (!query) { results.hidden = true; results.innerHTML = ""; return; }
    const matches = [...nodesById.values()].filter((node) => [node.id, node.nameCn, node.nameEn].join(" ").toLocaleLowerCase("zh-CN").includes(query)).slice(0, 20);
    results.innerHTML = matches.length ? matches.map((node) => `<button type="button" class="search-result" role="option" data-node-id="${escapeHtml(node.id)}"><span><strong>${escapeHtml(node.nameCn)}</strong><small>${escapeHtml(node.nameEn)} · ${escapeHtml(node.id)}</small></span></button>`).join("") : '<div class="search-empty">没有匹配的材料节点</div>';
    results.hidden = false;
    results.querySelectorAll(".search-result").forEach((button) => button.addEventListener("click", () => { results.hidden = true; revealNode(button.dataset.nodeId); }));
  }

  function setScopeCollapsed(collapsed) {
    const note = document.getElementById("scope-note");
    const content = document.getElementById("scope-note-content");
    const toggle = document.getElementById("scope-note-toggle");
    note.classList.toggle("collapsed", collapsed);
    content.hidden = collapsed;
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.innerHTML = `<i data-lucide="chevron-${collapsed ? "down" : "up"}" aria-hidden="true"></i><span>${collapsed ? "展开" : "收起"}</span>`;
    iconRefresh();
    requestAnimationFrame(() => fitTree(false));
  }

  function setHeaderCollapsed(collapsed) {
    const toggle = document.getElementById("toggle-header");
    document.body.classList.toggle("header-collapsed", collapsed);
    toggle.setAttribute("aria-pressed", String(collapsed));
    toggle.innerHTML = `<i data-lucide="panel-top-${collapsed ? "open" : "close"}" aria-hidden="true"></i><span>${collapsed ? "展开页头" : "收起页头"}</span>`;
    iconRefresh();
    requestAnimationFrame(() => fitTree(false));
  }

  document.getElementById("scope-note-toggle").addEventListener("click", () => setScopeCollapsed(!document.getElementById("scope-note-content").hidden));
  document.getElementById("release-details").addEventListener("toggle", () => requestAnimationFrame(() => fitTree(false)));
  document.getElementById("tree-search").addEventListener("input", updateSearch);
  document.getElementById("clear-search").addEventListener("click", () => { document.getElementById("tree-search").value = ""; updateSearch(); document.getElementById("tree-search").focus(); });
  document.addEventListener("click", (event) => { if (!event.target.closest(".search-wrap")) document.getElementById("search-results").hidden = true; });
  document.getElementById("expand-all").addEventListener("click", () => {
    const parents = [...nodesById.values()].filter((node) => node.childIds.length);
    const open = !parents.every((node) => expanded.has(node.id));
    expanded.clear();
    if (open) parents.forEach((node) => expanded.add(node.id)); else expanded.add(rootId);
    renderTree({ fit: true });
  });
  document.getElementById("global-view").addEventListener("click", globalView);
  document.getElementById("fit-tree").addEventListener("click", () => fitTree(true));
  document.getElementById("zoom-in").addEventListener("click", () => svg.transition().duration(180).call(zoom.scaleBy, 1.22));
  document.getElementById("zoom-out").addEventListener("click", () => { if (nodeFocusActive) fitTree(true); else svg.transition().duration(180).call(zoom.scaleBy, 0.8); });
  document.getElementById("toggle-header").addEventListener("click", () => setHeaderCollapsed(!document.body.classList.contains("header-collapsed")));
  document.getElementById("toggle-details").addEventListener("click", () => {
    const workspace = document.querySelector(".workspace");
    const hidden = !workspace.classList.contains("detail-hidden");
    workspace.classList.toggle("detail-hidden", hidden);
    const toggle = document.getElementById("toggle-details");
    toggle.setAttribute("aria-pressed", String(hidden));
    toggle.innerHTML = `<i data-lucide="panel-right-${hidden ? "open" : "close"}" aria-hidden="true"></i><span>${hidden ? "显示详情" : "隐藏详情"}</span>`;
    iconRefresh();
    requestAnimationFrame(() => fitTree(false));
  });

  let resizeTimer = null;
  window.addEventListener("resize", () => { clearTimeout(resizeTimer); resizeTimer = setTimeout(() => fitTree(false), 120); });
  setStats();
  renderTripletPriorities();
  renderSourceCoverage();
  setScopeCollapsed(true);
  renderTree({ fit: true });
  renderDetail(nodesById.get(rootId));
  iconRefresh();
})();
