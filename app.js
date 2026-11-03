(function () {
  "use strict";

  const data = window.MATERIAL_TREE_DATA;
  const hasD3 = typeof window.d3 !== "undefined";
  if (!data || !hasD3) {
    document.body.innerHTML = '<div class="fatal-error" role="alert">网站资源未完整载入。请先运行 build_site_data.py，并确认 vendor/d3.min.js 存在。</div>';
    return;
  }

  const d3 = window.d3;
  const nodesById = new Map(data.nodes.map((node) => [node.id, node]));
  const sourcesById = new Map(data.sources.map((source) => [source.id, source]));
  const evidenceByNode = d3.group(data.evidence, (item) => item.nodeId);
  const rootId = data.meta.rootId;
  const expanded = new Set([rootId]);
  let selectedId = rootId;
  let visibleLayout = new Map();
  let objectPageSize = 20;
  let objectFilter = "";
  let objectPropertyFilter = "complete";
  let lastTreeBounds = null;
  let nodeFocusActive = false;
  let focusedScale = null;
  let manualLayoutActive = false;

  const TYPE_INFO = {
    material_category: ["材料分类", "category"],
    family: ["材料族", "category"],
    material_leaf: ["材料叶子", "leaf"],
    material_process_leaf: ["工艺状态叶子", "leaf"],
    species_leaf: ["树种叶子", "leaf"],
    experimental_material_leaf: ["实验材料", "experimental"],
    broad_material_collection: ["宽粒度材料集合", "uncertain"],
    classification_placeholder: ["待细化材料集合", "uncertain"],
  };

  const svg = d3.select("#tree-svg");
  const zoomLayer = svg.select(".zoom-layer");
  const canvas = document.getElementById("tree-canvas");
  const zoom = d3.zoom().scaleExtent([0.12, 2.4]).on("zoom", (event) => {
    zoomLayer.attr("transform", event.transform);
  }).on("end", handleZoomEnd);
  svg.call(zoom).on("dblclick.zoom", null);

  function iconRefresh() {
    if (window.lucide) window.lucide.createIcons({ attrs: { "stroke-width": 1.8 } });
  }

  function setScopeNoteCollapsed(collapsed, persist = true) {
    const note = document.getElementById("scope-note");
    const content = document.getElementById("scope-note-content");
    const toggle = document.getElementById("scope-note-toggle");
    note.classList.toggle("collapsed", collapsed);
    content.hidden = collapsed;
    toggle.setAttribute("aria-expanded", String(!collapsed));
    toggle.title = `${collapsed ? "展开" : "收起"}阅读边界`;
    toggle.innerHTML = `<i data-lucide="chevron-${collapsed ? "down" : "up"}" aria-hidden="true"></i><span>${collapsed ? "展开" : "收起"}</span>`;
    if (persist) {
      try { sessionStorage.setItem("material-tree-scope-note", collapsed ? "collapsed" : "expanded"); } catch (_) { /* Storage may be unavailable in strict privacy modes. */ }
    }
    iconRefresh();
    requestAnimationFrame(() => fitTree(false));
  }

  function setHeaderCollapsed(collapsed, persist = true) {
    const toggle = document.getElementById("toggle-header");
    document.body.classList.toggle("header-collapsed", collapsed);
    toggle.setAttribute("aria-pressed", String(collapsed));
    toggle.title = `${collapsed ? "展开" : "收起"}标题、统计和阅读边界`;
    toggle.innerHTML = `<i data-lucide="panel-top-${collapsed ? "open" : "close"}" aria-hidden="true"></i><span>${collapsed ? "展开页头" : "收起页头"}</span>`;
    if (persist) {
      try { sessionStorage.setItem("material-tree-header", collapsed ? "collapsed" : "expanded"); } catch (_) { /* Keep the current in-memory state. */ }
    }
    iconRefresh();
    requestAnimationFrame(() => fitTree(false));
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>'"]/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
    }[char]));
  }

  function cleanText(value, fallback = "未提供") {
    const text = String(value ?? "").trim();
    return text || fallback;
  }

  function typeInfo(node) {
    return TYPE_INFO[node.type] || [node.type || "未分类", "category"];
  }

  function confidenceClass(value) {
    if (value === "高") return "high";
    if (value === "中") return "medium";
    return "low";
  }

  function formatNumber(value, property) {
    if (value === 62.76256 && property === "E") return "约 63";
    if (Math.abs(value) >= 1000) return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 0 }).format(value);
    if (Math.abs(value) >= 10) return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 2 }).format(value);
    return new Intl.NumberFormat("zh-CN", { maximumFractionDigits: 5 }).format(value);
  }

  function formatRange(range, unit, property) {
    if (!Array.isArray(range) || range.length !== 2) return '<span class="value-missing">无可用值</span>';
    const first = formatNumber(range[0], property);
    const second = formatNumber(range[1], property);
    const value = range[0] === range[1] ? first : `${first}–${second}`;
    return `${value}${unit && unit !== "1" ? ` ${escapeHtml(unit)}` : ""}`;
  }

  function compactEnglish(value, limit = 27) {
    const text = cleanText(value, "");
    return text.length > limit ? `${text.slice(0, limit - 1)}…` : text;
  }

  function nestedVisible(id) {
    const node = nodesById.get(id);
    return {
      ...node,
      children: expanded.has(id) ? node.childIds.map(nestedVisible) : null,
    };
  }

  function treeLinkPath(item) {
    const midY = (item.source.y + item.target.y) / 2;
    return `M${item.source.x},${item.source.y + 37} C${item.source.x},${midY} ${item.target.x},${midY} ${item.target.x},${item.target.y - 37}`;
  }

  function updateTreeBounds(items) {
    const xExtent = d3.extent(items, (item) => item.x);
    const yExtent = d3.extent(items, (item) => item.y);
    lastTreeBounds = {
      x: xExtent[0] - 105,
      y: yExtent[0] - 48,
      width: Math.max(210, xExtent[1] - xExtent[0] + 210),
      height: Math.max(146, yExtent[1] - yExtent[0] + 140),
    };
  }

  function enableNodeDragging(nodeGroups, linkPaths) {
    nodeGroups.call(d3.drag()
      .clickDistance(4)
      .on("start", function (event) {
        event.sourceEvent?.stopPropagation();
        nodeFocusActive = false;
        focusedScale = null;
        manualLayoutActive = true;
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
    const root = d3.hierarchy(nestedVisible(rootId));
    const layout = d3.tree().nodeSize([206, 148]);
    layout(root);
    visibleLayout = new Map(root.descendants().map((item) => [item.data.id, item]));
    manualLayoutActive = false;
    updateTreeBounds(root.descendants());

    zoomLayer.selectAll("*").remove();
    const links = zoomLayer.append("g").attr("aria-hidden", "true");
    const linkPaths = links.selectAll("path")
      .data(root.links())
      .join("path")
      .attr("class", "tree-link")
      .attr("d", treeLinkPath);

    const nodeGroups = zoomLayer.append("g")
      .selectAll("g.node")
      .data(root.descendants(), (item) => item.data.id)
      .join("g")
      .attr("class", (item) => `node ${item.data.id === selectedId ? "selected" : ""}`)
      .attr("transform", (item) => `translate(${item.x},${item.y})`)
      .attr("role", "button")
      .attr("tabindex", 0)
      .attr("aria-label", (item) => `${item.data.nameCn}，${typeInfo(item.data)[0]}，包含 ${item.data.objectCount} 个物体`)
      .on("click", (event, item) => {
        if (!event.defaultPrevented) activateNode(item.data.id, true);
      })
      .on("keydown", (event, item) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          activateNode(item.data.id, true);
        }
      });

    enableNodeDragging(nodeGroups, linkPaths);

    nodeGroups.append("rect")
      .attr("class", "node-card")
      .attr("x", -96)
      .attr("y", -37)
      .attr("width", 192)
      .attr("height", 74)
      .attr("rx", 5);
    nodeGroups.append("rect")
      .attr("class", (item) => `node-accent ${typeInfo(item.data)[1]}`)
      .attr("x", -96)
      .attr("y", -37)
      .attr("width", 5)
      .attr("height", 74)
      .attr("rx", 2);
    nodeGroups.append("text")
      .attr("class", "node-title")
      .attr("x", -82)
      .attr("y", -12)
      .text((item) => compactEnglish(item.data.nameCn, 10));
    nodeGroups.append("text")
      .attr("class", "node-subtitle")
      .attr("x", -82)
      .attr("y", 8)
      .text((item) => compactEnglish(item.data.nameEn));
    nodeGroups.append("text")
      .attr("class", "node-count")
      .attr("x", -82)
      .attr("y", 27)
      .text((item) => `L${item.data.level} · ${item.data.objectCount.toLocaleString("zh-CN")} 个物体`);

    const toggles = nodeGroups.filter((item) => item.data.childIds.length > 0);
    toggles.append("circle")
      .attr("class", "node-toggle")
      .attr("cx", 0)
      .attr("cy", 49)
      .attr("r", 11);
    toggles.append("text")
      .attr("class", "node-toggle-symbol")
      .attr("x", 0)
      .attr("y", 54)
      .text((item) => expanded.has(item.data.id) ? "−" : "+");

    document.getElementById("visible-summary").textContent = `当前显示 ${root.descendants().length} / ${data.meta.nodeCount} 个节点 · 最深层级 ${d3.max(root.descendants(), (item) => item.data.level)}`;
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
    const padding = 46;
    const minimumReadableScale = width < 600 ? 0.68 : 0.12;
    const scale = Math.max(minimumReadableScale, Math.min(1.2, (width - padding * 2) / lastTreeBounds.width, (height - padding * 2) / lastTreeBounds.height));
    const centerX = lastTreeBounds.x + lastTreeBounds.width / 2;
    const transform = d3.zoomIdentity.translate(width / 2 - centerX * scale, padding - lastTreeBounds.y * scale).scale(scale);
    if (animate) svg.transition().duration(260).call(zoom.transform, transform);
    else svg.call(zoom.transform, transform);
  }

  function adaptiveFocusScale(item, width, height) {
    const padding = 46;
    const fitScale = Math.min(1.2, (width - padding * 2) / lastTreeBounds.width, (height - padding * 2) / lastTreeBounds.height);
    const visibleCount = Math.max(1, visibleLayout.size);
    const densityScale = 1.18 - Math.max(0, Math.log2(visibleCount / 6)) * 0.14;
    const compactViewport = width < 620;
    const focusCap = compactViewport ? 0.9 : (item.data.level <= 2 ? 1.05 : 1.15);
    const minimumScale = compactViewport ? 0.48 : 0.55;
    return Math.max(minimumScale, Math.min(focusCap, Math.max(fitScale * 1.45, densityScale)));
  }

  function centerNode(id) {
    const item = visibleLayout.get(id);
    if (!item) return;
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    const scale = adaptiveFocusScale(item, width, height);
    nodeFocusActive = true;
    focusedScale = scale;
    const transform = d3.zoomIdentity.translate(width / 2 - item.x * scale, height / 2 - item.y * scale).scale(scale);
    svg.transition().duration(360).call(zoom.transform, transform);
  }

  function handleZoomEnd(event) {
    if (!nodeFocusActive || !focusedScale || event.sourceEvent?.type !== "wheel") return;
    if (event.transform.k <= focusedScale * 0.88) fitTree(true);
  }

  function activateNode(id, toggleChildren) {
    const node = nodesById.get(id);
    selectedId = id;
    objectPageSize = 20;
    objectFilter = "";
    if (toggleChildren && node.childIds.length) {
      if (expanded.has(id)) expanded.delete(id); else expanded.add(id);
    }
    renderTree({ focusId: id });
    renderDetail(node);
  }

  function ancestorsOf(id) {
    const path = [];
    let current = nodesById.get(id);
    while (current) {
      path.unshift(current);
      current = current.parentId ? nodesById.get(current.parentId) : null;
    }
    return path;
  }

  function revealNode(id) {
    ancestorsOf(id).slice(0, -1).forEach((node) => expanded.add(node.id));
    selectedId = id;
    objectPageSize = 20;
    objectFilter = "";
    renderTree({ focusId: id });
    renderDetail(nodesById.get(id));
  }

  function propertyRows(node) {
    const labels = { E: "杨氏模量 E", nu: "泊松比 ν", rho: "密度 ρ" };
    return Object.entries(labels).map(([key, label]) => {
      const property = node.properties[key] || {};
      return `<tr><td>${label}</td><td>${formatRange(property.literature_supported, property.unit, key)}</td><td>${formatRange(property.dataset_child_aggregate, property.unit, key)}</td></tr>`;
    }).join("");
  }

  function evidenceHtml(node) {
    const records = evidenceByNode.get(node.id) || [];
    if (!records.length) return '<p class="empty-inline">该节点没有直接物性证据记录。分类节点的来源通常来自其当前子树，请结合下方“关联来源”查看。</p>';
    return `<div class="evidence-list">${records.map((item, index) => {
      const source = sourcesById.get(item.sourceId);
      const sourceName = source ? source.name : item.sourceName;
      const sourceUrl = item.url || (source && source.url);
      return `<details class="evidence-item" ${index === 0 ? "open" : ""}>
        <summary><span class="evidence-summary"><span><strong>${escapeHtml(item.sourceType || item.nature || "物性证据")}</strong><small>${escapeHtml(sourceName)} · ${escapeHtml(item.id)}</small></span><i class="summary-chevron" data-lucide="chevron-down" aria-hidden="true"></i></span></summary>
        <div class="evidence-content">
          <div class="evidence-values">
            <div><span>杨氏模量 E</span><strong>${formatRange(item.E, "GPa", "E")}</strong></div>
            <div><span>泊松比 ν</span><strong>${formatRange(item.nu, "1", "nu")}</strong></div>
            <div><span>密度 ρ</span><strong>${formatRange(item.rho, "kg/m3", "rho")}</strong></div>
          </div>
          <dl>
            ${detailPair("证据性质", item.nature)}
            ${detailPair("方法", item.method)}
            ${detailPair("适用对象", item.applicability || item.gradeComposition)}
            ${detailPair("温度/环境", item.environment)}
            ${detailPair("制造/状态", item.manufacturing)}
            ${detailPair("原始单位", item.originalUnits)}
            ${detailPair("原文定位", item.locator)}
            ${detailPair("局限", item.limitation)}
            ${detailPair("置信度", `身份 ${cleanText(item.identityConfidence)} · 物性 ${cleanText(item.propertyConfidence)} · 适用性 ${cleanText(item.applicabilityConfidence)}`)}
          </dl>
          ${sourceUrl ? `<a class="source-link" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noopener noreferrer">打开原始来源 <i data-lucide="external-link" aria-hidden="true"></i></a>` : ""}
        </div>
      </details>`;
    }).join("")}</div>`;
  }

  function independentSourceCount(node) {
    const groups = node.sourceIds
      .map((id) => sourcesById.get(id))
      .filter(Boolean)
      .map((source) => source.independentGroup || source.id);
    return new Set(groups).size;
  }

  function evidenceSourceStatus(node) {
    const count = independentSourceCount(node);
    if (count >= 2) return `多源证据（${count} 个独立来源组）`;
    if (count === 1) return "单一来源证据（1 个独立来源组）";
    return "未关联来源";
  }

  function propertyCoverageStatus(node) {
    const direct = ["E", "nu", "rho"].filter((key) => Array.isArray(node.properties[key]?.literature_supported));
    const aggregate = ["E", "nu", "rho"].filter((key) => Array.isArray(node.properties[key]?.dataset_child_aggregate));
    if (direct.length === 3) return "三项物性均有节点直接证据";
    if (direct.length) return `部分物性有节点直接证据（${direct.join("、")}）`;
    if (aggregate.length === 3) return "无节点直接值；子树三项汇总均可用";
    if (aggregate.length) return `无节点直接值；子树部分汇总可用（${aggregate.join("、")}）`;
    return "仅有身份/分类证据，三项物性缺失";
  }

  function detailPair(label, value) {
    const text = cleanText(value, "");
    return text ? `<div><dt>${escapeHtml(label)}</dt><dd>${escapeHtml(text)}</dd></div>` : "";
  }

  function sourcesHtml(node) {
    const sourceItems = node.sourceIds.map((id) => sourcesById.get(id)).filter(Boolean);
    if (!sourceItems.length) return '<p class="empty-inline">该节点没有关联来源记录。</p>';
    return `<div class="source-list">${sourceItems.map((source) => `<details class="source-item">
      <summary><span class="evidence-summary"><span><strong>${escapeHtml(source.name || source.title || source.id)}</strong><small>${escapeHtml(source.type)} · ${escapeHtml(source.verificationStatus)} · ${escapeHtml(source.id)}</small></span><i class="summary-chevron" data-lucide="chevron-down" aria-hidden="true"></i></span></summary>
      <div class="source-content">
        <dl>
          ${detailPair("题名", source.title)}
          ${detailPair("作者/厂商", source.authorsOrManufacturer)}
          ${detailPair("支持内容", source.supports)}
          ${detailPair("独立来源组", source.independentGroup)}
          ${detailPair("本地文件", source.localFile)}
          ${detailPair("SHA-256", source.sha256)}
          ${detailPair("核验日期", source.retrievalDate)}
          ${detailPair("说明与局限", source.notes)}
        </dl>
        ${source.url ? `<a class="source-link" href="${escapeHtml(source.url)}" target="_blank" rel="noopener noreferrer">打开来源网页 <i data-lucide="external-link" aria-hidden="true"></i></a>` : ""}
      </div>
    </details>`).join("")}</div>`;
  }

  function filteredObjects(node) {
    const items = data.objectsByNode[node.id] || [];
    const query = objectFilter.trim().toLocaleLowerCase("zh-CN");
    return items.filter((item) => {
      const statusMatch = objectPropertyFilter === "all"
        || (objectPropertyFilter === "complete" && item.propertyComplete)
        || (objectPropertyFilter === "direct" && item.directPropertyComplete)
        || (objectPropertyFilter === "proxy" && item.proxyPropertyComplete)
        || (objectPropertyFilter === "incomplete" && !item.propertyComplete);
      const queryMatch = !query || [item.nameCn, item.nameEn, item.identifier, item.id].join(" ").toLocaleLowerCase("zh-CN").includes(query);
      return statusMatch && queryMatch;
    });
  }

  function objectItemHtml(item) {
    const sourceNames = item.sourceIds.map((id) => sourcesById.get(id)?.name || id).join("；");
    const asset = item.asset || {};
    const assetStatus = {
      exact_online_asset: ["精确在线资产", "asset-exact"],
      same_family_geometry: ["同系列几何", "asset-family"],
      category_geometry_proxy: ["类别几何代理", "asset-proxy"],
      procedural_geometry_recommended: ["建议程序化生成", "asset-procedural"],
      no_verified_asset: ["无可信公共资产", "asset-missing"],
    }[asset.asset_status] || ["3D 状态未记录", "asset-missing"];
    const auditStatus = {
      PASS_EXACT: ["资产判定 · 精确模型", "audit-pass"],
      PASS_PROXY: ["资产判定 · 类别代理", "audit-proxy"],
      HOLD_ASSET: ["资产判定 · 待补模型", "audit-hold"],
    }[item.auditDecision] || ["资产尚未审计", "audit-unknown"];
    const propertyStatus = {
      "保留": ["物性判定 · 保留", "audit-pass"],
      "保留（材料级条件化代理）": ["物性判定 · 材料级条件化代理", "audit-proxy"],
      "保留（节点证据）": ["物性判定 · 节点证据", "audit-pass"],
      "保留（需加条件/降级）": ["物性判定 · 需加条件/降级", "audit-proxy"],
      "保留（资产待解决）": ["物性判定 · 保留，资产待解决", "audit-proxy"],
      "修正 rho 后保留": ["物性判定 · 修正密度后保留", "audit-fail"],
      "保留但需部件级拆分": ["物性判定 · 需拆分部件", "audit-proxy"],
      "保留待补映射证据": ["物性判定 · 待补映射证据", "audit-hold"],
      "退回（物性归属错误）": ["物性判定 · 退回，归属错误", "audit-fail"],
      "退回（材料赋值错误）": ["物性判定 · 退回，材料错误", "audit-fail"],
    }[item.propertyVerdict] || ["物性尚未独立复核", "audit-unknown"];
    const auditFlagLabels = {
      proxy_property_evidence_split: "三项来自同一材料节点的多条证据，未由单条资料同时给出",
    };
    const auditFlags = (item.auditFlags || []).map((flag) => auditFlagLabels[flag] || flag);
    const propertyEvidence = item.propertyEvidence || [];
    const propertyEvidenceHtml = propertyEvidence.length ? `<div class="object-property-evidence"><div class="evidence-section-heading"><strong>文献/资料逐条物性</strong><span>各来源并列，不做平均</span></div>${propertyEvidence.map((ev) => `<details class="object-evidence-item"><summary><span class="evidence-source-title">${escapeHtml(ev.sourceName || ev.sourceId)}</span><span class="evidence-source-type">${escapeHtml(ev.sourceType || "物性来源")}</span></summary><div class="object-evidence-values"><div><span>E · 杨氏模量</span><strong>${formatRange(ev.E, "GPa", "E")}</strong></div><div><span>ν · 泊松比</span><strong>${formatRange(ev.nu, "1", "nu")}</strong></div><div><span>ρ · 密度</span><strong>${formatRange(ev.rho, "kg/m3", "rho")}</strong></div></div><div class="evidence-meta">${ev.locator ? `<span>${escapeHtml(ev.locator)}</span>` : ""}${ev.url ? `<a class="source-link" href="${escapeHtml(ev.url)}" target="_blank" rel="noopener noreferrer">打开来源 <i data-lucide="external-link" aria-hidden="true"></i></a>` : ""}</div></details>`).join("")}</div>` : "";
    const assetLinks = (asset.sources || []).map((source) => `<div class="asset-source">
      <a href="${escapeHtml(source.asset_page_url)}" download target="_blank" rel="noopener noreferrer">${escapeHtml(source.title)} · ${source.asset_page_url?.toLowerCase().endsWith(".glb") ? "下载 GLB" : "打开资产页面"} <i data-lucide="external-link" aria-hidden="true"></i></a>
      <span>${escapeHtml(source.author_or_publisher)} · ${escapeHtml(source.canonical_license)} · UID ${escapeHtml(source.asset_uid)}</span>
      <span>${source.vertex_count ? `${source.vertex_count.toLocaleString("zh-CN")} 顶点 · ${source.face_count.toLocaleString("zh-CN")} 面 · ` : ""}${source.is_downloadable ? "平台标记可下载" : "平台未标记可下载"} · ${escapeHtml(source.download_status)}</span>
    </div>`).join("");
    return `<article class="object-item">
      <h4>${escapeHtml(cleanText(item.nameCn, item.nameEn))}</h4>
      <p class="object-en">${escapeHtml(item.nameEn)}</p>
      <div class="object-tags">
        <span>${escapeHtml(item.identifier || item.id)}</span>
        ${item.dataset ? `<span>${escapeHtml(item.dataset)}</span>` : ""}
        <span>身份置信度 ${escapeHtml(cleanText(item.identityConfidence))}</span>
        <span>适用性 ${escapeHtml(cleanText(item.applicabilityConfidence))}</span>
        ${item.propertyStatus === "exact_complete" ? '<span class="status-complete">精确节点三项齐全</span>' : ""}
        ${item.propertyStatus === "direct_complete" ? '<span class="status-reference">对象/试样直接有三项证据</span>' : ""}
        ${item.propertyStatus === "proxy_complete" ? '<span class="status-proxy">三项完整（材料级参数）</span>' : ""}
        ${item.propertyStatus === "incomplete" ? '<span class="status-incomplete">待补三项证据</span>' : ""}
        ${item.isProxy && item.propertyStatus !== "proxy_complete" ? '<span>材料级参数</span>' : ""}
        ${item.simulationApplicabilityLabel ? `<span class="status-reference">${escapeHtml(item.simulationApplicabilityLabel)}</span>` : ""}
        <span class="${propertyStatus[1]}">${propertyStatus[0]}</span>
        <span class="${auditStatus[1]}">${auditStatus[0]}</span>
        <span class="${item.multiIndependentSource ? "status-multisource" : "status-single-source"}">${item.multiIndependentSource ? "三项各有至少两个独立主体" : "至少一项只有单一主体"}</span>
        <span class="${assetStatus[1]}">${assetStatus[0]}</span>
      </div>
      ${propertyEvidenceHtml}
      <details><summary>查看映射依据</summary><div class="object-detail">
        ${item.scope ? `<strong>部件/材料范围：</strong>${escapeHtml(item.scope)}<br>` : ""}
        ${item.mappingEvidence ? `<strong>映射证据：</strong>${escapeHtml(item.mappingEvidence)}<br>` : ""}
        ${item.rawMaterial ? `<strong>原始 material：</strong>${escapeHtml(item.rawMaterial)}<br>` : ""}
        ${item.sourceLocator ? `<strong>原始定位：</strong>${escapeHtml(item.sourceLocator)}<br>` : ""}
        ${item.auditRule ? `<strong>审核规则：</strong>${escapeHtml(item.auditRule)}<br>` : ""}
        ${item.simulationWarning ? `<strong>仿真适用性：</strong>${escapeHtml(item.simulationWarning)}<br>` : ""}
        <strong>物性判定：</strong>${escapeHtml(item.propertyVerdict || "尚未独立复核")}<br>
        <strong>资产判定：</strong>${escapeHtml(auditStatus[0])}<br>
        <strong>三项证据覆盖：</strong>${item.propertyEvidenceCoverage ? "E、ν、ρ 均有来源覆盖" : "证据覆盖不完整"}<br>
        <strong>各属性证据来源主体数（不是物性数值）：</strong>E=${item.publishersByProperty?.E ?? 0}；ν=${item.publishersByProperty?.nu ?? 0}；ρ=${item.publishersByProperty?.rho ?? 0}<br>
        <small class="object-detail-note">真实的 E、ν、ρ 数值请展开上方“文献/资料逐条物性”；这里的数字只表示该属性有几个独立发布主体。</small><br>
        ${item.evidenceGrade ? `<strong>证据等级：</strong>${escapeHtml(item.evidenceGrade)}<br>` : ""}
        ${item.compositeScope ? `<strong>复合件范围：</strong>${escapeHtml(item.compositeScope)}<br>` : ""}
        ${item.propertyIssues?.length ? `<strong>物性问题码：</strong>${item.propertyIssues.map(escapeHtml).join("；")}<br>` : ""}
        ${item.nodeFinding ? `<strong>节点复核结论：</strong>${escapeHtml(item.nodeFinding)}<br>` : ""}
        ${auditFlags.length ? `<strong>审计警告：</strong>${auditFlags.map(escapeHtml).join("；")}<br>` : ""}
        ${sourceNames ? `<strong>来源：</strong>${escapeHtml(sourceNames)}<br>` : ""}
        ${item.notes ? `<strong>说明：</strong>${escapeHtml(item.notes)}` : ""}
      </div></details>
      <details class="asset-details"><summary>查看 3D 资产与几何处置</summary><div class="object-detail">
        <strong>处置：</strong>${escapeHtml(assetStatus[0])}<br>
        ${asset.geometry_strategy ? `<strong>几何方案：</strong>${escapeHtml(asset.geometry_strategy)}<br>` : ""}
        ${asset.dimension_basis ? `<strong>尺寸依据：</strong>${escapeHtml(asset.dimension_basis)}<br>` : ""}
        ${asset.format_or_generation ? `<strong>格式/生成：</strong>${escapeHtml(asset.format_or_generation)}<br>` : ""}
        ${asset.limitations ? `<strong>局限：</strong>${escapeHtml(asset.limitations)}<br>` : ""}
        ${asset.negative_evidence ? `<strong>负证据：</strong>${escapeHtml(asset.negative_evidence)}<br>` : ""}
        ${assetLinks || '<span class="asset-none">没有通过审核的现成公共模型链接。</span>'}
      </div></details>
    </article>`;
  }

  function updateObjectList(node) {
    const items = filteredObjects(node);
    const list = document.getElementById("object-list");
    const summary = document.getElementById("object-match-summary");
    if (!list || !summary) return;
    const total = (data.objectsByNode[node.id] || []).length;
    const modeLabel = objectPropertyFilter === "complete" ? "三项完整" : objectPropertyFilter === "direct" ? "对象/试样直接有证据" : objectPropertyFilter === "proxy" ? "材料级参数" : "全部";
    summary.textContent = `${modeLabel} ${items.length} / ${total} 条${objectFilter ? "（已搜索）" : ""}`;
    list.innerHTML = items.slice(0, objectPageSize).map(objectItemHtml).join("") || '<p class="empty-inline">没有匹配的物体。</p>';
    const more = document.getElementById("load-more-objects");
    if (more) {
      const remaining = Math.max(0, items.length - objectPageSize);
      more.hidden = remaining === 0;
      more.style.display = remaining === 0 ? "none" : "";
      more.setAttribute("aria-hidden", remaining === 0 ? "true" : "false");
      more.disabled = remaining === 0;
      more.textContent = `再显示 ${Math.min(20, remaining)} 条`;
    }
  }

  function objectsSectionHtml(node) {
    const items = data.objectsByNode[node.id] || [];
    const count = items.length;
    const completeCount = items.filter((item) => item.propertyComplete).length;
    return `<div class="section-heading-row"><h3>直接挂载物体</h3><p id="object-match-summary">三项完整 ${completeCount} / ${count} 条</p></div>
      ${count ? `<div class="object-property-filter" role="group" aria-label="物性完整性筛选">
        <button type="button" data-property-filter="complete" aria-pressed="${objectPropertyFilter === "complete"}">三项完整</button>
        <button type="button" data-property-filter="direct" aria-pressed="${objectPropertyFilter === "direct"}">对象/试样直接有证据</button>
        <button type="button" data-property-filter="proxy" aria-pressed="${objectPropertyFilter === "proxy"}">材料级参数</button>
        <button type="button" data-property-filter="all" aria-pressed="${objectPropertyFilter === "all"}">全部</button>
      </div><p class="object-filter-note">全部保留对象均有 E、ν、ρ。“对象/试样直接有证据”表示论文或资料直接点名了该对象、试样或具体工艺，并给出了三项参数；“材料级参数”表示对象材料身份明确，但数值来自对应牌号、厂商或论文材料节点。前者也不自动等于每件商品都做过实测。</p><div class="object-tools"><input id="object-search" type="search" placeholder="在本节点物体中搜索" aria-label="在本节点物体中搜索"></div><div class="object-list" id="object-list"></div><button class="load-more" id="load-more-objects" type="button">再显示 20 条</button>` : '<p class="empty-inline">该节点没有直接挂载物体；“子树物体数”来自其后代节点。</p>'}`;
  }

  function renderDetail(node) {
    const type = typeInfo(node);
    const path = ancestorsOf(node.id);
    const aliases = cleanText(node.aliases, "无");
    const content = document.getElementById("detail-content");
    content.innerHTML = `
      <header class="detail-header">
        <nav class="detail-path" aria-label="节点路径">${path.map((item) => `<button type="button" class="crumb-button" data-node-id="${escapeHtml(item.id)}">${escapeHtml(item.nameCn)}</button>`).join("")}</nav>
        <div class="detail-title-row"><div><h2 id="detail-heading">${escapeHtml(node.nameCn)}</h2><p class="detail-en">${escapeHtml(node.nameEn)}</p></div><span class="type-label ${type[1]}">${type[0]}</span></div>
      </header>
      <div class="detail-body">
        <section class="detail-section">
          <h3>节点属性</h3>
          <dl class="meta-grid">
            <div><dt>节点 ID</dt><dd>${escapeHtml(node.id)}</dd></div>
            <div><dt>层级</dt><dd>第 ${node.level} 级</dd></div>
            <div><dt>材料 Key</dt><dd>${escapeHtml(node.key)}</dd></div>
            <div><dt>节点置信度</dt><dd class="confidence ${confidenceClass(node.confidence)}">${escapeHtml(node.confidence)}</dd></div>
            <div><dt>直接物体</dt><dd>${node.directObjectCount.toLocaleString("zh-CN")}</dd></div>
            <div><dt>子树物体</dt><dd>${node.objectCount.toLocaleString("zh-CN")}</dd></div>
            <div class="wide"><dt>证据来源状态</dt><dd>${escapeHtml(evidenceSourceStatus(node))}</dd></div>
            <div class="wide"><dt>物性覆盖状态</dt><dd>${escapeHtml(propertyCoverageStatus(node))}</dd></div>
            <div class="wide"><dt>别名</dt><dd>${escapeHtml(aliases)}</dd></div>
            ${node.definition ? `<div class="wide"><dt>材料定义</dt><dd>${escapeHtml(node.definition)}</dd></div>` : ""}
            <div class="wide"><dt>分类依据</dt><dd>${escapeHtml(cleanText(node.classificationBasis))}</dd></div>
          </dl>
          ${node.remarks ? `<p class="boundary-note">${escapeHtml(node.remarks)}</p>` : ""}
        </section>
        <section class="detail-section">
          <h3>三项物理属性</h3>
          <table class="property-table"><thead><tr><th>属性</th><th>节点直接证据</th><th>当前子树汇总</th></tr></thead><tbody>${propertyRows(node)}</tbody></table>
          <p class="property-footnote">“节点直接证据”来自该节点的文献或厂商记录；“当前子树汇总”仅聚合已收录后代证据。二者都不等同于当前商品逐件实测。</p>
        </section>
        <section class="detail-section"><div class="section-heading-row"><h3>直接物性证据</h3><p>${(evidenceByNode.get(node.id) || []).length} 条</p></div>${evidenceHtml(node)}</section>
        <section class="detail-section"><div class="section-heading-row"><h3>关联来源</h3><p>${node.sourceIds.length} 条来源记录 · ${independentSourceCount(node)} 个独立来源组</p></div>${sourcesHtml(node)}</section>
        <section class="detail-section">${objectsSectionHtml(node)}</section>
      </div>`;

    content.querySelectorAll(".crumb-button").forEach((button) => button.addEventListener("click", () => revealNode(button.dataset.nodeId)));
    const objectSearch = document.getElementById("object-search");
    if (objectSearch) objectSearch.addEventListener("input", (event) => {
      objectFilter = event.target.value;
      objectPageSize = 20;
      updateObjectList(node);
    });
    content.querySelectorAll("[data-property-filter]").forEach((button) => button.addEventListener("click", () => {
      objectPropertyFilter = button.dataset.propertyFilter;
      objectPageSize = 20;
      content.querySelectorAll("[data-property-filter]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      updateObjectList(node);
    }));
    const loadMore = document.getElementById("load-more-objects");
    if (loadMore) loadMore.addEventListener("click", () => {
      objectPageSize += 20;
      updateObjectList(node);
    });
    updateObjectList(node);
    iconRefresh();
  }

  function searchNodes(query) {
    const normalized = query.trim().toLocaleLowerCase("zh-CN");
    if (!normalized) return [];
    return data.nodes
      .map((node) => {
        const fields = [node.nameCn, node.nameEn, node.id, node.aliases, node.key].map((value) => String(value || "").toLocaleLowerCase("zh-CN"));
        let score = 99;
        fields.forEach((field, index) => {
          if (field === normalized) score = Math.min(score, index);
          else if (field.startsWith(normalized)) score = Math.min(score, 6 + index);
          else if (field.includes(normalized)) score = Math.min(score, 12 + index);
        });
        return { node, score };
      })
      .filter((item) => item.score < 99)
      .sort((a, b) => a.score - b.score || a.node.level - b.node.level || a.node.nameCn.localeCompare(b.node.nameCn, "zh-CN"))
      .slice(0, 14)
      .map((item) => item.node);
  }

  function updateSearchResults(query) {
    const panel = document.getElementById("search-results");
    if (!query.trim()) {
      panel.hidden = true;
      panel.innerHTML = "";
      return [];
    }
    const matches = searchNodes(query);
    panel.hidden = false;
    panel.innerHTML = matches.length ? matches.map((node) => `<button type="button" class="search-result" role="option" data-node-id="${escapeHtml(node.id)}"><span><strong>${escapeHtml(node.nameCn)}</strong><small>${escapeHtml(node.nameEn)} · ${escapeHtml(node.id)}</small></span></button>`).join("") : '<div class="search-empty">没有匹配的节点</div>';
    panel.querySelectorAll(".search-result").forEach((button) => button.addEventListener("click", () => {
      revealNode(button.dataset.nodeId);
      document.getElementById("tree-search").value = nodesById.get(button.dataset.nodeId).nameCn;
      panel.hidden = true;
    }));
    return matches;
  }

  function bindControls() {
    let savedScopeState = null;
    let savedHeaderState = null;
    try { savedScopeState = sessionStorage.getItem("material-tree-scope-note"); } catch (_) { /* Use the compact default. */ }
    try { savedHeaderState = sessionStorage.getItem("material-tree-header"); } catch (_) { /* Use the expanded default. */ }
    setScopeNoteCollapsed(savedScopeState !== "expanded", false);
    setHeaderCollapsed(savedHeaderState === "collapsed", false);
    document.getElementById("scope-note-toggle").addEventListener("click", (event) => {
      setScopeNoteCollapsed(event.currentTarget.getAttribute("aria-expanded") === "true");
    });
    document.getElementById("toggle-header").addEventListener("click", (event) => {
      setHeaderCollapsed(event.currentTarget.getAttribute("aria-pressed") !== "true");
    });
    const search = document.getElementById("tree-search");
    search.addEventListener("input", (event) => updateSearchResults(event.target.value));
    search.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        const matches = searchNodes(search.value);
        if (matches.length) {
          event.preventDefault();
          revealNode(matches[0].id);
          document.getElementById("search-results").hidden = true;
        }
      }
      if (event.key === "Escape") document.getElementById("search-results").hidden = true;
    });
    document.getElementById("clear-search").addEventListener("click", () => {
      search.value = "";
      document.getElementById("search-results").hidden = true;
      search.focus();
    });
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".search-wrap")) document.getElementById("search-results").hidden = true;
    });
    document.getElementById("expand-all").addEventListener("click", () => {
      data.nodes.filter((node) => node.childIds.length).forEach((node) => expanded.add(node.id));
      renderTree({ fit: true });
    });
    document.getElementById("global-view").addEventListener("click", () => {
      document.getElementById("tree-search").value = "";
      document.getElementById("search-results").hidden = true;
      expanded.clear();
      expanded.add(rootId);
      selectedId = rootId;
      renderTree({ fit: true });
      renderDetail(nodesById.get(rootId));
    });
    document.getElementById("fit-tree").addEventListener("click", () => {
      if (manualLayoutActive) renderTree({ fit: true }); else fitTree(true);
    });
    document.getElementById("toggle-details").addEventListener("click", (event) => {
      const workspace = document.querySelector(".workspace");
      const isHidden = workspace.classList.toggle("detail-hidden");
      event.currentTarget.setAttribute("aria-pressed", String(isHidden));
      event.currentTarget.innerHTML = `<i data-lucide="${isHidden ? "panel-right-open" : "panel-right-close"}" aria-hidden="true"></i><span>${isHidden ? "显示详情" : "隐藏详情"}</span>`;
      iconRefresh();
      requestAnimationFrame(() => fitTree(false));
    });
    document.getElementById("zoom-in").addEventListener("click", () => svg.transition().duration(180).call(zoom.scaleBy, 1.3));
    document.getElementById("zoom-out").addEventListener("click", () => {
      if (nodeFocusActive) {
        fitTree(true);
        return;
      }
      svg.transition().duration(180).call(zoom.scaleBy, 0.77);
    });
    new ResizeObserver(() => fitTree(false)).observe(canvas);
  }

  function initialize() {
    document.getElementById("edition").textContent = data.meta.edition;
    document.getElementById("stat-nodes").textContent = data.meta.nodeCount.toLocaleString("zh-CN");
    document.getElementById("stat-objects").textContent = data.meta.objectCount.toLocaleString("zh-CN");
    document.getElementById("stat-complete-objects").textContent = data.meta.completePropertyObjectCount.toLocaleString("zh-CN");
    document.getElementById("stat-strict-multisource").textContent = data.meta.strictMultiSourceObjectCount.toLocaleString("zh-CN");
    document.getElementById("stat-evidence-complete-objects").textContent = data.meta.directPropertyObjectCount.toLocaleString("zh-CN");
    document.getElementById("stat-evidence").textContent = data.meta.evidenceCount.toLocaleString("zh-CN");
    document.getElementById("stat-sources").textContent = data.meta.sourceCount.toLocaleString("zh-CN");
    document.getElementById("stat-exact-assets").textContent = data.meta.exactAssetCount.toLocaleString("zh-CN");
    document.getElementById("stat-category-assets").textContent = data.meta.categoryAssetCount.toLocaleString("zh-CN");
    document.getElementById("stat-procedural-assets").textContent = data.meta.proceduralAssetCount.toLocaleString("zh-CN");
    document.getElementById("stat-missing-assets").textContent = data.meta.noVerifiedAssetCount.toLocaleString("zh-CN");
    bindControls();
    renderTree({ fit: true });
    renderDetail(nodesById.get(rootId));
    iconRefresh();
  }

  initialize();
})();
