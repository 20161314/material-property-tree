(async () => { if (window.MATERIAL_PAYLOAD_READY) await window.MATERIAL_PAYLOAD_READY;
(function () {
  "use strict";

  const data = window.SITE_DATA;
  if (data?.meta?.researchMode && (!window.verifyDatasetView || !window.verifyDatasetView('materials', data))) return;
  const hasD3 = typeof window.d3 !== "undefined";
  if (!data || !hasD3) {
    document.body.innerHTML = '<div class="fatal-error" role="alert">网站资源未完整载入。请确认 data.js、vendor/d3.min.js 和 vendor/lucide.min.js 均已部署。</div>';
    return;
  }

  const d3 = window.d3;
  const fmt = (value) => value === null || value === undefined ? "待汇总" : Number(value).toLocaleString("zh-CN");
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

  let treeMode = data.meta.researchMode ? 'directory' : 'graph';
  const treePanel = document.querySelector('.tree-panel');
  const directory = document.createElement('div'); directory.className='site-directory';
  treePanel.append(directory);
  const modeSwitch = document.createElement('div'); modeSwitch.className='directory-modes';
  modeSwitch.innerHTML='<button type="button" data-mode="directory">分类目录</button><button type="button" data-mode="graph">树形画布</button>';
  if (data.meta.researchMode) treePanel.querySelector('.panel-heading').append(modeSwitch);
  function updateDirectory() {
    document.body.dataset.treeMode=treeMode;
    modeSwitch.querySelectorAll('button').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.mode===treeMode)));
    const node=nodesById.get(selectedId);
    const children=node.childIds.map(id=>nodesById.get(id));
    if(treeMode==='directory')document.getElementById('visible-summary').textContent='逐级浏览分类；材料节点 '+fmt(data.meta.canonicalCoverage.targetCount)+' 个，分类目录另计。';
    directory.innerHTML='<div class="directory-heading"><strong>'+escapeHtml(node.nameCn)+'</strong><span>'+children.length+' 个直属分类或材料</span></div><div class="directory-path">'+ancestorsOf(node.id).map(item=>'<button type="button" data-directory-id="'+escapeHtml(item.id)+'">'+escapeHtml(item.nameCn)+'</button>').join('')+'</div><div class="directory-grid">'+children.map(item=>'<button type="button" data-directory-id="'+escapeHtml(item.id)+'"><strong>'+escapeHtml(item.nameCn)+'</strong><small>'+escapeHtml(item.nameEn)+'</small><small>'+fmt(item.classifiedEvidenceCount ?? item.subtreeEvidenceCount)+' 条来源组'+(item.childIds.length ? ' · '+item.childIds.length+' 个子类' : '')+'</small></button>').join('')+'</div>'+(!children.length ? '<p class="site-caption">已到材料叶节点。右侧查看逐来源的原始数值，或进入物性覆盖页查看范围。</p>' : '');
    directory.querySelectorAll('[data-directory-id]').forEach(button=>button.onclick=()=>revealNode(button.dataset.directoryId));
  }
  modeSwitch.querySelectorAll('button').forEach(button=>button.onclick=()=>{treeMode=button.dataset.mode;updateDirectory();requestAnimationFrame(()=>fitTree(false));});
  const expanded = new Set([rootId]);
  let selectedId = rootId;
  let viewRootId = rootId;
  let visibleLayout = new Map();
  let lastTreeBounds = null;
  let nodeFocusActive = false;
  let focusedScale = null;
  let currentTransform = d3.zoomIdentity;
  let minimapProjection = null;
  let objectPageSize = 30;
  let objectFilter = "";

  const svg = d3.select("#tree-svg");
  const zoomLayer = svg.select(".zoom-layer");
  const canvas = document.getElementById("tree-canvas");
  const MIN_OVERVIEW_SCALE = 0.00025;
  const MIN_FOCUS_SCALE = 0.84;
  const zoom = d3.zoom().scaleExtent([MIN_OVERVIEW_SCALE, 2.4]).on("zoom", (event) => {
    currentTransform = event.transform;
    zoomLayer.attr("transform", event.transform);
    updateMinimapViewport(event.transform);
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
    const sameValue = normalized.every((value) => value === normalized[0] || (Number.isFinite(Number(value)) && Number(value) === Number(normalized[0])));
    const result = normalized.length === 1 || sameValue ? normalized[0] : `${normalized[0]}–${normalized[normalized.length - 1]}`;
    return `${escapeHtml(result)}${unit ? ` ${unit}` : ""}`;
  }

  function nodeKind(node) {
    if (node.childIds.length && node.subtreeEvidenceCount) return ["子树汇总", "aggregate"];
    if (data.meta.researchMode && node.id.startsWith("RESEARCH-FAMILY-")) return ["分类/材料族", "category"];
    if ((data.evidenceByNode[node.id] || []).length) return [data.meta.researchMode ? "存在来源记录" : "存在完整证据", "evidenced"];
    if (node.childIds.length) return ["分类/材料族", "category"];
    return ["材料身份", "identity"];
  }

  function setStats() {
    const meta = data.meta;
    document.getElementById("edition").textContent = meta.edition || "v3 双表发布版";
    if (meta.researchMode) {
      const canonical = meta.canonicalCoverage;
      const coverage = canonical || meta.propertyCoverage || {};
      const denominator = canonical ? (canonical.targetCount ?? canonical.material_nodes) : coverage.targetMaterialCount;
      const count = (canonicalKey, legacyKey) => canonical ? (coverage[legacyKey] ?? coverage[canonicalKey]) : coverage[legacyKey];
      const coveredText = (canonicalKey, legacyKey) => {
        const value = count(canonicalKey, legacyKey);
        return value === undefined || denominator === undefined ? "待汇总" : String(fmt(value)) + "/" + fmt(denominator) + (canonical ? " 规范材料" : " 历史目标");
      };
      const scopeLabel = document.getElementById("material-coverage-scope");
      if (scopeLabel) scopeLabel.textContent = canonical ? `覆盖分母：最新材料标签与已审来源身份的规范并集；其中有直接来源记录 ${fmt(meta.directEvidenceMaterialCount ?? meta.canonicalMaterialNodeCount)} 个。外部数据库组成身份分页另列，不与树节点直接相加。` : "历史 193 项目标覆盖（全库覆盖汇总尚未载入）；规范节点总量单列。";
      const values = {
        "stat-complete-records": meta.completeRecordCount ?? meta.evidenceCount,
        "stat-partial-records": meta.incompleteRecordCount,
        "stat-canonical-materials": meta.allMaterialNodeCount ?? meta.canonicalMaterialNodeCount,
        "stat-source-identities": meta.sourceDefinedIdentityCount,
        "stat-complete-materials": coveredText("nodes_with_complete_group", "materialsWithCompleteRecord"),
        "stat-e-materials": coveredText("nodes_with_E", "materialsWithE"),
        "stat-nu-materials": coveredText("nodes_with_nu", "materialsWithNu"),
        "stat-rho-materials": coveredText("nodes_with_rho", "materialsWithRho"),
        "stat-all-properties": coveredText("nodes_with_all_properties_any_sources", canonical ? "materialsWithAllThreeFromAnyGroup" : "materialsWithAllThreeProperties"),
        "stat-partial-materials": coveredText("nodes_with_incomplete_group", "materialsWithIncompleteRecord"),
        "stat-no-values": canonical && canonical.materialsWithoutAnyValue === undefined && canonical.nodes_without_any_value === undefined ? "未提供全库汇总" : coveredText("nodes_without_any_value", "materialsWithoutAnyValue"),
        "stat-source-documents": meta.combinedSourceDocumentKeys,
        "stat-simulation-presets": meta.isolatedSimulationPresetCount,
      };
      Object.entries(values).forEach(([id, value]) => {
        document.getElementById(id).textContent = typeof value === "string" ? value : fmt(value);
      });
      document.getElementById("scope-note-content").textContent = `每条记录对应一个来源材料定义和一个样品/条件组。完整组同组含 E、ν、ρ；不完整组同组含 1 或 2 项，跨来源不拼接。当前统计 ${fmt(meta.completeRecordCount)} 条完整组、${fmt(meta.incompleteRecordCount)} 条不完整组（含数据库转录），共 ${fmt(meta.reviewedRecordGroupCount)} / ${fmt(meta.allRecordCountTarget)} 组；主账与数据库转录批次分别保留来源核验层级，外部库可从玻璃分支进入分页目录。E、ν、ρ 的材料覆盖数计入完整组和已审不完整组，不要求三项出自同一组。当前有 ${fmt(meta.combinedSourceDocumentKeys)} 个主账文档/数据库引文键，未完成跨库谱系归并，不等于独立来源数；旧范围确认 ${fmt(meta.confirmedSourceLineagesInInheritedScope)} 个来源谱系，扩展范围的独立数仍待核，当前不报告扩展账独立来源上限。仿真预设 ${fmt(meta.isolatedSimulationPresetCount)} 组单独隔离，不计入研究记录。牌号、方向、方法及条件保留，不自动赋给对象。`;
      document.getElementById("audit-pill").textContent = meta.incompleteAuditStatus === "COMPLETE" ? "记录分类与覆盖统计已构建" : `不完整组 ${fmt(meta.incompleteRecordCount)} 条；含数据库转录层，原论文未逐篇重读`;
      return;
    }
    document.getElementById("stat-full-objects").textContent = fmt(meta.fullObjectCount);
    document.getElementById("stat-full-rows").textContent = fmt(meta.fullComponentRows);
    const coverage = meta.approximateCoverage || {};
    document.getElementById("stat-search-targets").textContent = fmt(meta.materialSearchTargetCount);
    document.getElementById("stat-source-grounded").textContent = fmt(meta.sourceGroundedMaterialNameCount);
    document.getElementById("stat-approx-labels").textContent = fmt(meta.approximateMaterialNameCount);
    document.getElementById("stat-dual-assignable").textContent = fmt((meta.dualSourceCoverage || {}).nodes_passing_two_source_gate);
    document.getElementById("stat-evidence").textContent = fmt(meta.evidenceCount);
    document.getElementById("stat-evidence-nodes").textContent = fmt(meta.materialNodesWithEvidence);
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
    if (data.meta.researchMode) return;
    const rows = data.meta.tripletPriorities || [];
    if (!rows.length) {
      target.innerHTML = '<p class="empty-inline">当前发布包没有三元组搜集排程。</p>';
      return;
    }
    target.innerHTML = rows.slice(0, 12).map((row) => `<article class="priority-item"><span class="priority-rank">${fmt(row.rank)}</span><div><h3>${escapeHtml(row.nameCn)}</h3><p>${escapeHtml(row.nameEn)}</p></div><dl><div><dt>覆盖组件</dt><dd>${fmt(row.coveredRows)}</dd></div><div><dt>覆盖对象</dt><dd>${fmt(row.coveredObjects)}</dd></div></dl><span class="priority-kind ${row.identityLevel === "FORMAL_SOURCE_GROUNDED_NODE" ? "formal" : "approx"}">${row.identityLevel === "FORMAL_SOURCE_GROUNDED_NODE" ? "正式节点" : "近似检索名"}</span></article>`).join("");
  }

  function renderSourceCoverage() {
    const target = document.getElementById("source-coverage");
    if (data.meta.researchMode) return;
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

  function descendantsOf(id) {
    const result = [];
    const pending = [id];
    const seen = new Set();
    while (pending.length) {
      const current = pending.pop();
      if (seen.has(current)) continue;
      seen.add(current);
      const node = nodesById.get(current);
      if (!node) continue;
      result.push(node);
      node.childIds.forEach((childId) => pending.push(childId));
    }
    return result;
  }

  function updateTreeContext() {
    const target = document.getElementById("tree-context");
    const path = ancestorsOf(viewRootId);
    target.innerHTML = path.map((node, index) => `<button type="button" data-node-id="${escapeHtml(node.id)}" ${index === path.length - 1 ? 'aria-current="page"' : ""}>${escapeHtml(node.nameCn)}</button>`).join("");
    target.querySelectorAll("button").forEach((button) => button.addEventListener("click", () => setViewRoot(button.dataset.nodeId)));
    const focusButton = document.getElementById("focus-branch");
    const selected = nodesById.get(selectedId);
    focusButton.disabled = !selected || !selected.childIds.length || selectedId === viewRootId;
  }

  function renderMinimap(root) {
    const minimap = d3.select("#tree-minimap");
    minimap.selectAll("*").remove();
    if (!lastTreeBounds) return;
    const inset = 7;
    const scale = Math.min((160 - inset * 2) / lastTreeBounds.width, (104 - inset * 2) / lastTreeBounds.height);
    const offsetX = (160 - lastTreeBounds.width * scale) / 2 - lastTreeBounds.x * scale;
    const offsetY = (104 - lastTreeBounds.height * scale) / 2 - lastTreeBounds.y * scale;
    const projectX = (value) => value * scale + offsetX;
    const projectY = (value) => value * scale + offsetY;
    minimapProjection = { scale, offsetX, offsetY };
    minimap.append("g").attr("aria-hidden", "true").selectAll("line")
      .data(root.links()).join("line")
      .attr("x1", (item) => projectX(item.source.x)).attr("y1", (item) => projectY(item.source.y))
      .attr("x2", (item) => projectX(item.target.x)).attr("y2", (item) => projectY(item.target.y))
      .attr("class", "minimap-link");
    minimap.append("g").attr("aria-hidden", "true").selectAll("circle")
      .data(root.descendants()).join("circle")
      .attr("cx", (item) => projectX(item.x)).attr("cy", (item) => projectY(item.y))
      .attr("r", (item) => item.data.id === selectedId ? 2.8 : 1.7)
      .attr("class", (item) => item.data.id === selectedId ? "minimap-node selected" : "minimap-node");
    minimap.append("rect").attr("class", "minimap-viewport");
    updateMinimapViewport(currentTransform);
  }

  function updateMinimapViewport(transform) {
    if (!minimapProjection || !canvas.clientWidth || !canvas.clientHeight) return;
    const { scale, offsetX, offsetY } = minimapProjection;
    const x = (-transform.x / transform.k) * scale + offsetX;
    const y = (-transform.y / transform.k) * scale + offsetY;
    const width = canvas.clientWidth / transform.k * scale;
    const height = canvas.clientHeight / transform.k * scale;
    d3.select("#tree-minimap .minimap-viewport").attr("x", x).attr("y", y).attr("width", width).attr("height", height);
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
    const rootData = nestedVisible(viewRootId);
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
      .attr("aria-label", (item) => `${item.data.nameCn}，${nodeKind(item.data)[0]}，${data.meta.researchMode ? `${fmt(item.data.sourceDocumentCount)} 个文档键` : `子树 ${fmt(item.data.subtreeObjectCount)} 个对象`}`)
      .on("click", (event, item) => { if (!event.defaultPrevented) activateNode(item.data.id, true); })
      .on("keydown", (event, item) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); activateNode(item.data.id, true); } });
    enableNodeDragging(groups, linkPaths);
    groups.append("rect").attr("class", "node-card").attr("x", -100).attr("y", -38).attr("width", 200).attr("height", 76).attr("rx", 5);
    groups.append("rect").attr("class", (item) => `node-accent ${nodeKind(item.data)[1]}`).attr("x", -100).attr("y", -38).attr("width", 5).attr("height", 76).attr("rx", 2);
    groups.append("text").attr("class", "node-title").attr("x", -86).attr("y", -13).text((item) => compactText(item.data.nameCn, 12));
    groups.append("text").attr("class", "node-subtitle").attr("x", -86).attr("y", 7).text((item) => compactText(item.data.nameEn, 28));
    groups.append("text").attr("class", "node-count").attr("x", -86).attr("y", 27).text((item) => {
      const count = item.data.classifiedEvidenceCount ?? (item.data.childIds.length ? item.data.subtreeEvidenceCount : item.data.directEvidenceCount);
      return data.meta.researchMode
        ? `${fmt(item.data.classifiedSourceDocumentCount ?? item.data.sourceDocumentCount)} 个文档键 · ${fmt(count)} 条记录`
        : `L${item.data.level} · ${fmt(item.data.subtreeObjectCount)} 对象 · ${fmt(count)} ${item.data.childIds.length ? "子树" : "直接"}证据`;
    });
    const toggles = groups.filter((item) => item.data.childIds.length > 0);
    toggles.append("circle").attr("class", "node-toggle").attr("cx", 0).attr("cy", 50).attr("r", 11);
    toggles.append("text").attr("class", "node-toggle-symbol").attr("x", 0).attr("y", 55).text((item) => expanded.has(item.data.id) ? "−" : "+");
    const scopeParents = descendantsOf(viewRootId).filter((node) => node.childIds.length);
    document.getElementById("visible-summary").textContent = `当前分支 ${items.length} / ${scopeParents.length + descendantsOf(viewRootId).filter((node) => !node.childIds.length).length} 个节点 · 全库 ${data.meta.materialNodeCount} 个节点`;
    document.getElementById("expand-all").querySelector("span").textContent = scopeParents.every((node) => expanded.has(node.id)) ? "收起分支" : "展开分支";
    updateTreeContext();
    renderMinimap(root);
    if (data.meta.researchMode) updateDirectory();
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
    const topPadding = width < 520 ? 72 : 58;
    const bottomPadding = width < 520 ? 34 : 46;
    const availableHeight = Math.max(1, height - topPadding - bottomPadding);
    const scale = Math.max(MIN_OVERVIEW_SCALE, Math.min(1.2, (width - padding * 2) / lastTreeBounds.width, availableHeight / lastTreeBounds.height));
    const centerX = lastTreeBounds.x + lastTreeBounds.width / 2;
    const centerY = lastTreeBounds.y + lastTreeBounds.height / 2;
    const transform = d3.zoomIdentity.translate(width / 2 - centerX * scale, topPadding + availableHeight / 2 - centerY * scale).scale(scale);
    if (animate) svg.transition().duration(260).call(zoom.transform, transform); else svg.call(zoom.transform, transform);
  }

  function centerNode(id) {
    const item = visibleLayout.get(id);
    if (!item) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const fitScale = Math.max(MIN_OVERVIEW_SCALE, Math.min(1.2, (width - 92) / lastTreeBounds.width, (height - 92) / lastTreeBounds.height));
    const densityScale = 1.16 - Math.max(0, Math.log2(Math.max(1, visibleLayout.size) / 6)) * 0.13;
    const scale = Math.max(MIN_FOCUS_SCALE, Math.min(width < 620 ? 0.96 : 1.12, Math.max(fitScale * 1.25, densityScale)));
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
    const path = ancestorsOf(id);
    if (!path.some((node) => node.id === viewRootId)) viewRootId = rootId;
    path.slice(0, -1).forEach((node) => expanded.add(node.id));
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
    if (node.externalCollection) {
      const url = String(node.externalCatalogUrl || "");
      const href = /^evidence-catalog\.html(?:[?].*)?$/.test(url) ? url : "evidence-catalog.html";
      return '<p class="boundary-note">数据库转录实验记录。已核结构、单位、引用连接与重复键；未逐篇人工回读原论文。完整组仅含唯一引文；多引文缺项组保留引用集合。</p><a class="source-link" href="' + escapeHtml(href) + '">打开完整与缺项物性分页目录</a>';
    }
    if (data.meta.researchMode && node.id.startsWith("RESEARCH-FAMILY-") && !node.childIds.length) {
      return '<p class="empty-inline">该材料家族目前尚无通过审核的完整来源。保留为检索缺口，未填入占位数值。</p>';
    }
    if (node.childIds.length && !(data.evidenceByNode[node.id] || []).length) {
      return `<p class="empty-inline">此节点当前没有直接 E、ν、ρ 来源记录；其 ${fmt(node.subtreeEvidenceCount)} 条记录均属于后代叶节点，请进入相应叶节点查看逐来源数值。</p>`;
    }
    if ((node.secondaryChildIds || []).length && !(data.evidenceByNode[node.id] || []).length) return `<p class="empty-inline">此节点没有直接物性组；已核包含关系支持 ${fmt(node.classifiedEvidenceCount ?? 0)} 条去重来源组。进入下方“其他已核包含关系”查看原始材料及数值。</p>`;
    const records = data.evidenceByNode[node.id] || [];
    if (!records.length) {
      return '<p class="empty-inline">直接证据记录为 0：该叶节点的 E、ν、ρ 仍待补；未填入任何占位数值。</p>';
    }
    const pageSize = data.meta.researchMode ? 30 : records.length;
    const visible = records.slice(0, pageSize);
    return `<div class="evidence-list">${visible.map((item, index) => {
      const url = safeUrl(item.url);
      const isIncomplete = item.recordType === "INCOMPLETE";
      const recordLabel = isIncomplete ? `不完整来源组 · ${[item.E, item.nu, item.rho].filter(values => values.length > 0).length} 项属性` : "完整来源组";
      return `<details class="evidence-item" ${index === 0 ? "open" : ""}><summary><span class="evidence-summary"><span><strong>${escapeHtml(item.title || item.id)}</strong><small>${recordLabel} · ${escapeHtml(item.sourceType)} · ${escapeHtml(item.sourceId)} · ${escapeHtml(item.id)}</small></span><i class="summary-chevron" data-lucide="chevron-down" aria-hidden="true"></i></span></summary><div class="evidence-content"><div class="evidence-values"><div><span>杨氏模量 E${isIncomplete ? "（来源原值）" : ""}</span><strong>${formatRange(item.E, isIncomplete ? "" : "GPa")}</strong></div><div><span>泊松比 ν${isIncomplete ? "（来源原值）" : ""}</span><strong>${formatRange(item.nu, "")}</strong></div><div><span>密度 ρ${isIncomplete ? "（来源原值）" : ""}</span><strong>${formatRange(item.rho, isIncomplete ? "" : "kg/m³")}</strong></div></div><dl class="evidence-meta">${detailPair("发布主体", item.publisher)}${detailPair("来源核验层", item.sourceVerificationLayer)}${detailPair("数值来源形式", item.propertyModel)}${detailPair("数值来源性质", item.propertyValueOrigin)}${detailPair("同一试样", item.sameSpecimen)}${detailPair("赋值材料范围", item.materialScope)}${detailPair("原文定位", item.locator)}${detailPair("冻结文件 SHA-256", item.sha256)}${detailPair("文档去重键", item.documentKey)}${detailPair("材料/牌号", item.grade)}${detailPair("温度与环境", item.environment)}${detailPair("方向/原值分组", item.orientation)}${detailPair("来源原值摘录", item.sourceValueExcerpt)}${detailPair("来源不确定度说明", item.sourceUncertaintyNotes)}${detailPair("单位换算说明", item.unitConversionNotes)}${detailPair("来源谱系键", item.sourceLineageKey)}${detailPair("统计量", item.sourceStatistic)}${detailPair("应变区间", item.sourceDeformationRange)}${detailPair("E 标准差（原单位）", item.EStandardDeviationOriginal)}${detailPair("E 下IQR（原文）", item.ELowerIQR)}${detailPair("E 上IQR（原文）", item.EUpperIQR)}${detailPair("密度标准差（原单位）", item.rhoStandardDeviationOriginal)}${detailPair("密度原文定义", item.densitySourceDefinition)}${detailPair("辅助原值（不替代三项）", item.ancillaryValues)}${detailPair("密度定义", item.densityType)}${detailPair("密度分项原值", item.densityTypeValues)}${detailPair("方法", item.method)}${detailPair("局限", item.limitations)}</dl>${propertyCitationsHtml(item.propertyCitations)}${url ? `<a class="source-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">打开原始来源 <i data-lucide="external-link" aria-hidden="true"></i></a>` : ""}</div></details>`;
    }).join("")}</div>${records.length > pageSize ? `<p class="node-note">本页显示前 ${fmt(pageSize)} 条；全部记录保留在来源总表中。</p>` : ""}`;
  }

  function propertyCitationsHtml(citations) {
    if (!citations) return "";
    let values = citations;
    if (typeof values === "string") {
      try { values = JSON.parse(values); } catch { return '<details class="property-citations"><summary>各属性原引用</summary><pre>' + escapeHtml(values) + '</pre></details>'; }
    }
    if (!values || (typeof values === "object" && !Object.keys(values).length)) return "";
    return '<details class="property-citations"><summary>各属性原引用</summary><pre>' + escapeHtml(JSON.stringify(values, null, 2)) + '</pre></details>';
  }

  function renderResearchDetail(node) {
    const content = document.getElementById("detail-content");
    const path = ancestorsOf(node.id);
    const aggregate = node.childIds.length > 0 || (node.secondaryChildIds || []).length > 0;
    const children = node.childIds.map((id) => nodesById.get(id));
    const title = aggregate ? "分类来源覆盖" : "逐来源物性数据组";
    content.innerHTML = `<div class="detail-header"><div class="detail-path">${path.map((item) => `<button type="button" class="crumb-button" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.nameCn)}</button>`).join("")}</div><h2 id="detail-heading">${escapeHtml(node.nameCn)}</h2><p class="detail-en">${escapeHtml(node.nameEn)}</p></div><div class="detail-body"><section class="detail-section"><h3>来源覆盖</h3><div class="metric-grid"><div class="metric"><span>文档文件键</span><strong>${fmt(node.classifiedSourceDocumentCount ?? node.sourceDocumentCount)}</strong></div><div class="metric"><span>发布主体</span><strong>${fmt(node.classifiedPublisherSubjectCount ?? node.publisherSubjectCount)}</strong></div><div class="metric"><span>${aggregate ? "分类去重" : "直接"}数据组</span><strong>${fmt(aggregate ? (node.classifiedEvidenceCount ?? node.subtreeEvidenceCount) : node.directEvidenceCount)}</strong></div><div class="metric"><span>本库新增对象赋值</span><strong>0</strong></div></div><p class="boundary-note">${escapeHtml(node.notes)}</p></section><section class="detail-section"><div class="section-heading-row"><h3>${title}</h3><p>${aggregate ? "仅汇总，不上推" : "原文条件，独立保留"}</p></div>${evidenceHtml(node)}</section><section class="detail-section"><h3>关联视图</h3><div class="object-links"><a href="references.html?material=${encodeURIComponent(node.id)}">查看此材料数值与覆盖</a><a href="scaling.html?material=${encodeURIComponent(node.id)}#material-linked-objects">查找已映射物体</a></div></section>${children.length ? `<section class="detail-section"><h3>进入材料分支</h3><div class="research-branch-list">${children.slice(0, 40).map((child) => `<button type="button" class="research-branch" data-node-id="${escapeHtml(child.id)}"><span>${escapeHtml(child.nameCn)}</span><small>${fmt(child.sourceDocumentCount)} 个文档键 · ${fmt(child.subtreeEvidenceCount)} 条数据组</small></button>`).join("")}</div>${children.length > 40 ? '<p class="node-note">分支较多，可用顶部搜索框定位完整材料名或牌号。</p>' : ""}</section>` : ""}</div>`;
    const relatedParents = (node.secondaryParentIds || []).map(id => nodesById.get(id)).filter(Boolean);
    const relatedChildren = (node.secondaryChildIds || []).map(id => nodesById.get(id)).filter(Boolean);
    if (relatedParents.length || relatedChildren.length) {
      const buttons = [...relatedParents.map(item => ({ item, prefix: "也属于" })), ...relatedChildren.map(item => ({ item, prefix: "也包含" }))];
      content.querySelector(".detail-body").insertAdjacentHTML("beforeend", `<section class="detail-section"><h3>其他已核包含关系</h3><p class="node-note">主树保留一个父类；这里记录化学与构造的交叉分类。同一证据全局只计一次。</p><div class="research-branch-list">${buttons.map(({ item, prefix }) => `<button type="button" class="research-branch" data-node-id="${escapeHtml(item.id)}"><span>${prefix}：${escapeHtml(item.nameCn)}</span><small>${escapeHtml(item.nameEn)}</small></button>`).join("")}</div></section>`);
    }
    content.querySelectorAll("[data-node-id]").forEach((button) => button.addEventListener("click", () => revealNode(button.dataset.nodeId)));
    iconRefresh();
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
    if (data.meta.researchMode) { renderResearchDetail(node); return; }
    const kind = nodeKind(node);
    const path = ancestorsOf(node.id);
    const aggregateOnly = node.childIds.length > 0;
    const directObjects = data.objectsByNode[node.id] || [];
    const content = document.getElementById("detail-content");
    const evidenceCount = aggregateOnly ? node.subtreeEvidenceCount : node.directEvidenceCount;
    const referenceLink = (data.meta.referenceTargetIds || []).includes(node.id) ? '<p class="node-note"><a href="references.html?material=' + encodeURIComponent(node.id) + '">查看此材料标签的研究来源与适用限制</a></p>' : "";
    content.innerHTML = `<div class="detail-header"><div class="detail-path">${path.map((item) => `<button type="button" class="crumb-button" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.nameCn)}</button>`).join("")}</div><div class="detail-title-row"><div><h2 id="detail-heading">${escapeHtml(node.nameCn)}</h2><p class="detail-en">${escapeHtml(node.nameEn)} · ${escapeHtml(node.id)}</p></div><span class="type-label ${kind[1]}">${kind[0]}</span></div></div><div class="detail-body"><section class="detail-section"><h3>节点范围</h3><div class="metric-grid"><div class="metric"><span>直接映射对象</span><strong>${fmt(node.directObjectCount)}</strong></div><div class="metric"><span>直接组件映射</span><strong>${fmt(node.directComponentCount)}</strong></div><div class="metric"><span>当前子树对象</span><strong>${fmt(node.subtreeObjectCount)}</strong></div><div class="metric"><span>${aggregateOnly ? "子树证据记录" : "直接证据记录"}</span><strong>${fmt(evidenceCount)}</strong></div></div>${node.childIds.length ? '<p class="boundary-note">子树数字只用于了解覆盖规模。子节点的材料和物性不会自动上推给此父节点。</p>' : ""}${node.notes ? `<p class="node-note">${escapeHtml(node.notes)}</p>` : ""}</section><section class="detail-section"><div class="section-heading-row"><h3>${aggregateOnly ? "子树证据边界" : "逐来源完整三元组证据"}</h3><p>${aggregateOnly ? "仅汇总，不上推" : "双源才达标，不平均"}</p></div>${evidenceHtml(node)}</section><section class="detail-section"><div class="section-heading-row"><h3>直接映射的对象与组件</h3><p id="object-count-note"></p></div><div class="object-tools"><input id="object-filter" type="search" placeholder="筛选当前节点的对象、组件或来源" aria-label="筛选当前节点对象"></div><div id="object-list" class="object-list"></div><button type="button" id="load-more" class="load-more">再显示 30 条</button>${directObjects.length > 200 ? '<p class="node-note">页面按需展示；完整记录保留在正式 CSV 中。</p>' : ""}</section></div>`;
    content.querySelectorAll(".crumb-button").forEach((button) => button.addEventListener("click", () => revealNode(button.dataset.nodeId)));
    content.querySelector(".detail-body").insertAdjacentHTML("afterbegin", referenceLink);
    document.getElementById("object-filter").addEventListener("input", (event) => { objectFilter = event.target.value; objectPageSize = 30; renderObjectList(node); });
    document.getElementById("load-more").addEventListener("click", () => { objectPageSize += 30; renderObjectList(node); });
    renderObjectList(node);
    iconRefresh();
  }

  function fullTreeOverview() {
    expanded.clear();
    descendantsOf(rootId).filter((node) => node.childIds.length).forEach((node) => expanded.add(node.id));
    selectedId = rootId;
    viewRootId = rootId;
    objectFilter = "";
    objectPageSize = 30;
    renderTree({ fit: true });
    renderDetail(nodesById.get(rootId));
  }

  function setViewRoot(id) {
    const node = nodesById.get(id);
    if (!node) return;
    viewRootId = id;
    selectedId = id;
    expanded.add(id);
    renderTree({ fit: true });
    renderDetail(node);
  }

  function focusSelectedBranch() {
    const node = nodesById.get(selectedId);
    if (!node || !node.childIds.length) return;
    setViewRoot(node.id);
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
    const parents = descendantsOf(viewRootId).filter((node) => node.childIds.length);
    const open = !parents.every((node) => expanded.has(node.id));
    if (open) parents.forEach((node) => expanded.add(node.id));
    else {
      parents.forEach((node) => expanded.delete(node.id));
      expanded.add(viewRootId);
    }
    renderTree({ focusId: visibleLayout.has(selectedId) ? selectedId : viewRootId });
  });
  document.getElementById("focus-branch").addEventListener("click", focusSelectedBranch);
  document.getElementById("global-view").addEventListener("click", fullTreeOverview);
  document.getElementById("fit-tree").addEventListener("click", () => fitTree(true));
  document.getElementById("zoom-in").addEventListener("click", () => svg.transition().duration(180).call(zoom.scaleBy, 1.22));
  document.getElementById("zoom-out").addEventListener("click", () => { nodeFocusActive = false; focusedScale = null; svg.transition().duration(180).call(zoom.scaleBy, 0.72); });
  d3.select("#tree-minimap").on("click", (event) => {
    if (!minimapProjection) return;
    const [x, y] = d3.pointer(event);
    const contentX = (x - minimapProjection.offsetX) / minimapProjection.scale;
    const contentY = (y - minimapProjection.offsetY) / minimapProjection.scale;
    const scale = currentTransform.k;
    svg.transition().duration(220).call(zoom.transform, d3.zoomIdentity.translate(canvas.clientWidth / 2 - contentX * scale, canvas.clientHeight / 2 - contentY * scale).scale(scale));
  });
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
  const requestedNode = new URLSearchParams(location.search).get("material") || new URLSearchParams(location.search).get("node");
  if (requestedNode && nodesById.has(requestedNode)) revealNode(requestedNode);
  iconRefresh();
})();

})().catch(() => {});
