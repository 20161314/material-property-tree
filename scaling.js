(() => {
  const $ = (id) => document.getElementById(id);
  const data = window.SCALING_DATA;
  if (!data?.summary) {
    $("load-error").hidden = false;
    $("load-error").textContent = "发布数据未载入，请刷新页面或检查 scaling-data.js。";
    return;
  }
  const summary = data.summary;
  const fmt = (value) => value === undefined || value === null ? "待核" : Number(value).toLocaleString("en");
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));
  const safeUrl = (value) => /^https?:\/\//i.test(String(value || "")) ? String(value) : "";
  const link = (url, text) => safeUrl(url) ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>` : "";
  const sourceLabels = {
    "ABO-3D": ["Amazon Berkeley Objects", "https://amazon-berkeley-objects.s3.amazonaws.com/index.html"],
    "VOMP-GVM-PUBLIC": ["VoMP / GVM", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP"],
    PIXIEVERSE: ["PIXIEVerse / SLAT-Phys 复用", "https://huggingface.co/datasets/vlongle/pixieverse"],
    "PHYSXNET-FINALINDEX": ["PhysX-3D", ""],
    "NVIDIA-SIMREADY-HF": ["NVIDIA SimReady", "https://huggingface.co/datasets/nvidia/simready-assets"],
    "PHYSX-MOBILITY": ["PhysX-Mobility", ""],
    "LEGACY-CURATED": ["既有人工整理对象", ""],
    "SUPPLEMENTAL-GOOGLE-GSO": ["Google Scanned Objects", "https://fuel.gazebosim.org/1.0/GoogleResearch/models"],
  };
  const queueNames = {
    MATERIAL_WITHOUT_EXACT_OBJECT_LINK: "材料待精确关联对象", MATERIAL_FIRST_NUMERICAL_SOURCE: "材料待首个数值来源",
    MATERIAL_MISSING_PROPERTY: "材料待补齐缺失属性", OBJECT_MATERIAL_AND_PART_REVIEW: "新增对象待核材料与部件",
    REAL_COMPONENT_MATERIAL_BINDING: "真实组件待核材料绑定",
  };
  $("release-date").textContent = `扩充发布 · ${summary.date} · 按来源快照核验`;
  const counts = {
    "count-objects": summary.object_identities, "count-components": summary.distinct_object_component_pairs,
    "count-status-rows": summary.object_component_rows, "count-materials": summary.material_labels,
    "count-complete": summary.complete_records, "count-partial": summary.partial_records,
  };
  Object.entries(counts).forEach(([id, value]) => { $(id).textContent = fmt(value); });
  $("delta-gso").textContent = `+${fmt(summary.new_source_object_identities)}`;
  const cycle2 = Number.isFinite(summary.cycle2_real_components_added);
  $("delta-components").textContent = `+${fmt(cycle2 ? summary.cycle2_net_component_increment : summary.net_real_component_increment)}`;
  $("delta-components-note").textContent = cycle2
    ? `本轮新增 ${fmt(summary.cycle2_real_components_added)} 个实体组件；另更新既有 ${fmt(summary.cycle2_existing_component_material_updates)} 个组件的官方材料标签`
    : `${fmt(summary.real_components_added)} 个独立部件替换 ${fmt(summary.fallbacks_replaced)} 个整件占位`;
  const cycle2Note = cycle2 ? `其中软优先对象 ${fmt(summary.gso_soft_priority_objects_with_source_labels)}/${fmt(summary.gso_soft_priority_input_objects)}；${fmt(summary.source_text_semantic_component_proposals)} 个文本语义部件仅作来源范围，不计实体组件。` : "";
  $("delta-source-note").textContent = `${fmt(summary.source_reported_material_backlink_objects)} 个 GSO 对象有 ${fmt(summary.source_reported_material_backlinks)} 条官方文本材料回链，尚未证明网格部件绑定。${cycle2Note}已下载并哈希核对 ${fmt(summary.new_GSO_geometry_files_downloaded_and_hashed)} 个 GSO 样本；其余资产保留逐项核查状态。`;
  const objectCounts = data.sourceObjectCounts || {};
  const rowCounts = data.sourceRowCounts || data.sourceCounts || {};
  const sourceKeys = [...new Set([...Object.keys(objectCounts), ...Object.keys(rowCounts)])];
  $("source-rows").innerHTML = sourceKeys.map((id) => {
    const [label, url] = sourceLabels[id] || [id, ""];
    return `<tr><td>${link(url, label) || esc(label)}</td><td>${fmt(objectCounts[id])}</td><td>${fmt(rowCounts[id])}</td></tr>`;
  }).join("");
  const sourceTotal = Object.values(objectCounts).reduce((sum, value) => sum + Number(value), 0);
  $("source-total").textContent = Object.keys(objectCounts).length ? `${fmt(sourceTotal)} 对象` : "对象分来源汇总待载入";
  if (Object.keys(objectCounts).length && sourceTotal !== summary.object_identities) {
    $("load-error").hidden = false;
    $("load-error").textContent = "主来源对象计数与发布总量不一致，待核对发布快照。";
  }
  $("queue-count").textContent = `${fmt(summary.queue_count)} 项`;
  $("queue-types").innerHTML = Object.entries(summary.queue_types || {}).map(([key, value]) => `<li><span>${esc(queueNames[key] || key)}</span><strong>${fmt(value)}</strong></li>`).join("");
  const priorities = summary.queue_priorities || data.priorityCounts || {};
  $("priority-note").textContent = `${fmt(priorities.FLEXIBLE_COMPONENT_SEARCH_FIRST)} 个新增对象优先检索柔性组件；${fmt(priorities.SOFT_MATERIAL_FIRST)} 项软材料任务优先；${fmt(priorities.CONTINUE_HARD_AND_OTHER_MATERIALS)} 项硬类与其他材料任务继续。`;
  const partsBadge = $("parts-heading")?.closest(".scaling-section-heading")?.querySelector(".scaling-badge");
  if (cycle2 && partsBadge) {
    const statuses = summary.featured_component_material_status_counts || {};
    partsBadge.textContent = `累计 ${fmt(summary.featured_physical_component_count)} 组件：${fmt(statuses.official)} 官方标签、${fmt(statuses.approximate)} 近似、${fmt(statuses.hold)} HOLD`;
  }
  if (cycle2) $("parts-heading").textContent = "已核实体组件与材料状态";
  $("component-cards").innerHTML = (data.newPhysicalComponents || []).map((item) => {
    const kind = item.material_status_kind || "hold";
    const label = item.material_status_label || "组件材料待核";
    const note = item.material_status_note || "组件身份已核，材料对应关系仍待补证。";
    const material = kind === "hold" ? "材料尚未核定" : (item.material_label || item.material_label_raw || "来源标签见原文");
    const regionNote = item.official_bound_material_regions?.length ? `<small>${fmt(item.official_bound_material_regions.length)} 个已核材料区域；不新增组件数。</small>` : "";
    return `<article>
    <h3>${esc(item.component_name_cn || item.component_scope || item.component_id)}</h3><p>${esc(item.object_name_cn || item.object_name_en)} · ${esc(item.object_name_en)}</p>
    <code>${esc(item.component_path)}</code><p>${esc(item.component_identity_note || "独立官方几何引用、质量/惯量及关节成员关系；通过组件身份审核。")}</p>
    <span class="scaling-badge ${kind === "official" ? "verified" : "pending"}">${esc(label)}</span>
    <p><strong>${esc(material)}</strong></p><p>${esc(note)}</p><small>${esc(item.material_scope_note || "")}</small>${regionNote}
    <p>原文定位：${esc(item.source_locator || "见官方结构文件")}</p>${link(item.source_url, "打开官方结构文件")}${link(item.source_manifest_url, "打开资产包")}
  </article>`;
  }).join("");
  const propertyNote = cycle2 ? `本轮另增加 ${fmt(summary.cycle2_incomplete_property_groups)} 条缺项组（${fmt(summary.cycle2_property_value_cells)} 个属性值格），不计入完整组或组件数。` : "";
  $("release-boundary").textContent = `研究完整与缺项共 ${fmt(summary.total_records)} 组，包含独立标记的数据库转录层。${propertyNote}正式材料映射 ${fmt(summary.formal_material_mapping_rows_unchanged)} 行未因本轮标签或组件新增而自动晋级。全库几何内容去重未完成。`;
  const hashes = { expanded_inventory_sha256: "扩充对象组件清单 SHA-256", feedback_queue_sha256: "待办队列 SHA-256", baseline_sha256: "原始对象表 SHA-256" };
  $("release-hashes").innerHTML = Object.entries(hashes).filter(([key]) => summary[key]).map(([key, label]) => `<dt>${label}</dt><dd>${esc(summary[key])}</dd>`).join("");

  const pages = data.gsoPages || [];
  const pageSelect = $("gso-page");
  pageSelect.innerHTML = pages.map((page, index) => `<option value="${index}">第 ${index + 1} / ${pages.length} 页（${page.count} 项）</option>`).join("");
  $("gso-count-note").textContent = `${fmt(summary.new_source_object_identities)} 个官方来源身份，按 100 项分页。材料未核不当作正式赋值；已下载校验 ${fmt(summary.new_GSO_geometry_files_downloaded_and_hashed)} 个样本。`;
  let activePage = 0;
  let currentRows = [];
  let requestVersion = 0;
  const cache = new Map();

  function backlinksHtml(backlinks) {
    if (!backlinks || !Object.keys(backlinks).length) return "";
    const entries = Array.isArray(backlinks) ? backlinks : [backlinks];
    return `<details class="scaling-backlinks"><summary>官方文本材料回链（${entries.length} 条）</summary><p>仅适用于原文描述范围；未证明模型部件绑定，未晋级正式材料赋值。</p>${entries.map((entry) => {
      const url = entry.source_url || entry.sourceUrl || entry.url;
      const text = entry.source_quote || entry.quote || entry.source_text || entry.evidence_text || entry.source_excerpt || entry.material_label_raw || entry.material_label || entry.material;
      return `<p><strong>${esc(entry.material_name_cn || entry.material_label_raw || "来源材料")}</strong> · ${esc(entry.component_scope_reported || "仅按来源文本范围")}</p><pre>${esc(text || JSON.stringify(entry, null, 2))}</pre><small>定位：${esc(entry.source_locator || "未提供")}</small>${link(url, "打开材料原文")}`;
    }).join("")}</details>`;
  }

  function renderAssets() {
    const query = $("gso-search").value.trim().toLocaleLowerCase();
    const rows = currentRows.filter((item) => !query || [item.id, item.nameCn, item.nameEn, item.category].join(" ").toLocaleLowerCase().includes(query));
    $("gso-page-status").textContent = `第 ${activePage + 1}/${pages.length} 页 · 当前页 ${currentRows.length} 项 · 筛选命中 ${rows.length} 项`;
    $("gso-rows").innerHTML = rows.length ? rows.map((item) => {
      const downloaded = item.assetStatus === "DOWNLOADED_OFFICIALZIP_SAMPLE";
      return `<tr><td data-label="物体与来源身份"><strong>${esc(item.nameCn || item.nameEn)}</strong><small>${esc(item.nameEn)}</small><small>${esc(item.id)}</small><small>${esc(item.category)} · ${esc(item.source)}</small></td>
      <td data-label="组件 / 材料状态"><p>${esc(item.componentScope)}</p><span class="scaling-badge pending">${item.sourceMaterialBacklinks?.length ? "有官方文本回链 · 模型绑定待核" : (item.materialReviewNote ? "元数据已筛查 · 尚无可接受材料回链" : "来源未报告材料 · 待核")}</span>${backlinksHtml(item.sourceMaterialBacklinks)}<small>无 E/ν/ρ 正式材料赋值</small></td>
      <td data-label="来源与 3D 资产"><div class="scaling-asset-links">${link(item.sourceUrl, "来源清单")}${link(item.assetUrl, "下载资产 ZIP")}</div><span class="scaling-badge ${downloaded ? "verified" : "pending"}">${downloaded ? "已下载并校验的样本" : "官方模式链接 · 待逐项验证"}</span><small>${esc(item.license)}</small></td></tr>`;
    }).join("") : '<tr><td colspan="3">当前页无匹配；可清空筛选或切换资产页。</td></tr>';
  }

  async function loadPage(index) {
    if (!pages[index]) return;
    const version = ++requestVersion;
    activePage = index;
    pageSelect.value = String(index);
    $("gso-prev").disabled = index === 0;
    $("gso-next").disabled = index === pages.length - 1;
    $("gso-page-status").textContent = "载入资产页…";
    $("gso-rows").innerHTML = "";
    try {
      let rows = cache.get(index);
      if (!rows) {
        const response = await fetch(pages[index].url);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        rows = await response.json();
        if (!Array.isArray(rows) || rows.length !== pages[index].count) throw new Error("分页条数与索引不一致");
        cache.set(index, rows);
      }
      if (version !== requestVersion) return;
      currentRows = rows;
      renderAssets();
    } catch (error) {
      if (version !== requestVersion) return;
      currentRows = [];
      $("gso-page-status").textContent = `资产页载入失败：${error.message}`;
    }
  }
  pageSelect.addEventListener("change", () => loadPage(Number(pageSelect.value)));
  $("gso-prev").addEventListener("click", () => loadPage(activePage - 1));
  $("gso-next").addEventListener("click", () => loadPage(activePage + 1));
  $("gso-search").addEventListener("input", renderAssets);
  loadPage(0);
})();
