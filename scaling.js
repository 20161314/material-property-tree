(async () => {
  const $ = (id) => document.getElementById(id);
  const data = window.SCALING_BOOTSTRAP || window.SCALING_DATA;
  if (!window.verifyDatasetView || !window.verifyDatasetView('objects', data)) return;
  if (!data?.summary) {
    $("load-error").hidden = false;
    $("load-error").textContent = "发布数据未载入，请刷新页面或检查 scaling-data.js。";
    return;
  }
  const summary = data.summary;
  const isDownloadedGlb = (item) => item.isDownloaded === true || String(item.downloadStatus || "").startsWith("DOWNLOADED_GLB") || item.downloadStatus === "DOWNLOADED_SHA256_AND_GLB_HEADER_VERIFIED";
  const fmt = (value) => value === undefined || value === null ? "待核" : Number(value).toLocaleString("en");
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[char]));
  const safeUrl = (value) => /^https?:\/\//i.test(String(value || "")) ? String(value) : "";
  const link = (url, text) => safeUrl(url) ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(text)} ↗</a>` : "";
  const materialId = new URLSearchParams(location.search).get('material');
  async function renderMaterialObjects() {
    const section = $('material-linked-objects');
    if (!materialId || !section) return;
    section.hidden = false;
    $('linked-material-tree').href = 'research.html?material=' + encodeURIComponent(materialId);
    $('linked-material-note').textContent = '正在读取当前版本的材料映射…';
    try {
      const indexPin = window.DATASET_RELEASE.object_material_index;
      const detailPin = indexPin.material_files?.[materialId];
      const pin = detailPin || indexPin;
      const response = await fetch(pin.file + '?v=' + pin.sha256.slice(0,12), {signal:AbortSignal.timeout(30000)});
      if (!response.ok) throw new Error('材料索引请求失败：' + response.status);
      const bytes = await response.arrayBuffer();
      const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256',bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
      if (hash !== pin.sha256) throw new Error('材料索引与当前发布版本不一致');
      const decoded = await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
      const index = JSON.parse(decoded);
      if (detailPin ? index.materialId !== materialId : index.releaseId !== window.DATASET_RELEASE.id) throw new Error('材料索引版本不一致');
      const entry = detailPin ? index.entry : index.materials[materialId];
      const rows = entry?.rows || [];
      $('linked-material-title').textContent = entry ? entry.nameCn : materialId;
      $('linked-material-note').textContent = rows.length ? new Set(rows.map(r=>r.object_id)).size.toLocaleString('en') + ' 个来源物体，' + rows.length.toLocaleString('en') + ' 条已有组件映射。保留原审核状态；物性证据不自动赋给这些商品。' : '此材料尚无以规范 ID 建立的物体映射；来源值仍可查看，不据名称猜测物体。';
      const navigationEvidence = (row) => (row.navigation_evidence || []).map(item => {
        const mode = /ALTERNATIVE/i.test(item.relation_mode || '') ? '备选材料，非同时组成' : item.relation_mode === 'COEXISTING_SCOPES' ? '并存材料，仅限注明部位' : item.relation_mode === 'WHOLE_CONSTRUCTION_WITH_COEXISTING_CONSTITUENTS' ? '整体构造，各组成材料并存' : item.relation_mode === 'CONSTITUENT_SCOPE_OF_KNOTTED_CONSTRUCTION' ? '结织构造的组成材料，仅限注明范围' : '来源材料关联';
        const partial = item.resolution === 'PARTIAL' ? '；原材料描述仍有未对齐部分' : '';
        return '<p><small>' + esc(mode + partial) + '</small><br>' + esc(item.status || '') + '<br>' + esc(item.basis || '') + '</p>';
      }).join('');
      let shown = 0;
      const append = () => {
        const next = rows.slice(shown, shown+24); shown += next.length;
        $('linked-material-rows').insertAdjacentHTML('beforeend', next.map(row=>'<article data-object-id="'+esc(row.object_id)+'"><h3>'+esc(row.object_name_cn || row.object_name_en)+'</h3><p>'+esc(row.object_name_en)+'</p><small>'+esc(row.object_id)+' · '+esc(row.component_id)+'</small><p><strong>'+esc(row.component_scope)+'</strong> · '+esc(row.material_label)+'</p><p>'+esc(row.material_identity_status)+'<br>'+esc(row.material_release_status)+'</p>'+navigationEvidence(row)+'<div class="scaling-asset-links">'+link(row.asset_url,'打开 3D 资产')+link(row.mapping_source_url,'查看材料依据')+'</div></article>').join(''));
        $('linked-material-more').hidden = shown >= rows.length;
        $('linked-material-more').textContent = '继续加载（'+shown+' / '+rows.length+'）';
      };
      $('linked-material-more').addEventListener('click',append); append();
    } catch(error) { $('linked-material-note').textContent = error.message + '，请重新载入。'; }
  }
  renderMaterialObjects();
  const sourceLabels = {
    "ABO-3D": ["Amazon Berkeley Objects", "https://amazon-berkeley-objects.s3.amazonaws.com/index.html"],
    "VOMP-GVM-PUBLIC": ["VoMP / GVM", "https://huggingface.co/datasets/nvidia/PhysicalAI-Robotics-PhysicalAssets-VoMP"],
    PIXIEVERSE: ["PIXIEVerse / SLAT-Phys 复用", "https://huggingface.co/datasets/vlongle/pixieverse"],
    "PHYSXNET-FINALINDEX": ["PhysX-3D", "https://huggingface.co/datasets/Caoza/PhysX-3D"],
    "NVIDIA-SIMREADY-HF": ["NVIDIA SimReady", "https://huggingface.co/datasets/nvidia/simready-assets"],
    "PHYSX-MOBILITY": ["PhysX-Mobility", "https://huggingface.co/datasets/Caoza/PhysX-Mobility"],
    "LEGACY-CURATED": ["既有人工整理对象", ""],
    "YCB-OFFICIAL": ["YCB Object and Model Set", "https://www.ycbbenchmarks.com/"],
    "SUPPLEMENTAL-OBJAVERSE-LVIS-FLEXIBLE": ["Objaverse-LVIS 柔性候选", "https://huggingface.co/datasets/allenai/objaverse"],
    "Objaverse-LVIS": ["Objaverse-LVIS 硬质候选", "https://huggingface.co/datasets/allenai/objaverse"],
    "SUPPLEMENTAL-GOOGLE-GSO": ["Google Scanned Objects", "https://fuel.gazebosim.org/1.0/GoogleResearch/models"],
  };
  const sourceAssetLinks = {
    "PHYSXNET-FINALINDEX": [["https://huggingface.co/datasets/Caoza/PhysX-3D/tree/main", "资产文件目录"], ["https://github.com/ziangcao0312/PhysX-3D", "项目说明 / 代码"]],
    "PHYSX-MOBILITY": [["https://huggingface.co/datasets/Caoza/PhysX-Mobility/resolve/d0768ee9e1415f6be8db78d6389ba018b85134c0/PhysX-Mobility.zip", "下载 3D 资产 ZIP"]],
  };
  const queueNames = {
    MATERIAL_WITHOUT_EXACT_OBJECT_LINK: "材料待精确关联对象", MATERIAL_FIRST_NUMERICAL_SOURCE: "材料待首个数值来源",
    OBJECT_AUTHORED_COMPONENT_ENUMERATION: "对象真实组件待枚举", MATERIAL_MISSING_PROPERTY: "材料待补齐缺失属性", OBJECT_MATERIAL_AND_PART_REVIEW: "新增对象待核材料与部件",
    REAL_COMPONENT_MATERIAL_BINDING: "真实组件待核材料绑定",
  };
  $("release-date").textContent = `扩充发布 · ${summary.date} · 按来源快照核验`;
  const counts = {
    "count-objects": summary.object_identities, "count-components": summary.distinct_object_component_pairs,
    "count-status-rows": summary.object_component_rows, "count-materials": summary.material_labels,
    "count-complete": summary.complete_records, "count-partial": summary.partial_records,
  };
  Object.entries(counts).forEach(([id, value]) => { $(id).textContent = fmt(value); });
  $("delta-objects").textContent = ["cycle8", "cycle9", "cycle10", "cycle11", "cycle12", "cycle13"].includes(summary.current_cycle) ? `+${fmt(summary.current_cycle_new_geometry_identities)}` : `+${fmt(Boolean(summary.current_cycle) ? 0 : summary.new_source_object_identities)}`;
  const cycle2 = Number.isFinite(summary.cycle2_real_components_added);
  const cycle3 = Boolean(summary.current_cycle);
  $("delta-components").textContent = `+${fmt(cycle3 ? summary.current_cycle_net_component_increment : cycle2 ? summary.cycle2_net_component_increment : summary.net_real_component_increment)}`;
  $("delta-components-note").textContent = ["cycle8", "cycle9", "cycle10", "cycle11", "cycle12", "cycle13"].includes(summary.current_cycle)
    ? `本轮新增 ${fmt(summary.current_cycle_new_whole_object_fallbacks)} 个 WHOLE 整件占位；新增真实分件 ${fmt(summary.current_cycle_real_components_added)}，累计展示 ${fmt(summary.featured_physical_component_count)} 张实体组件卡；其中上轮既有 ${fmt(summary.current_cycle_legacy_physical_cards || 3513)} 张原样保留。`
    : cycle3
    ? `本轮 ${fmt(summary.current_cycle_real_components_added)} 个实体替换 ${fmt(summary.current_cycle_fallbacks_replaced)} 个整件占位，净增 ${fmt(summary.current_cycle_net_component_increment)}；另补 ${fmt(summary.current_cycle_existing_component_material_updates)} 条既有组件材料回链`
    : cycle2
    ? `本轮新增 ${fmt(summary.cycle2_real_components_added)} 个实体组件；另更新既有 ${fmt(summary.cycle2_existing_component_material_updates)} 个组件的官方材料标签`
    : `${fmt(summary.real_components_added)} 个独立部件替换 ${fmt(summary.fallbacks_replaced)} 个整件占位`;
  const cycle2Note = cycle2 ? `其中软优先对象 ${fmt(summary.gso_soft_priority_objects_with_source_labels)}/${fmt(summary.gso_soft_priority_input_objects)}；${fmt(summary.source_text_semantic_component_proposals)} 个文本语义部件仅作来源范围，不计实体组件。` : "";
  $("delta-source-note").textContent = `${fmt(summary.source_reported_material_backlink_objects)} 个 GSO 对象有 ${fmt(summary.source_reported_material_backlinks)} 条官方文本材料回链，尚未证明网格部件绑定。${cycle2Note}已下载并哈希核对 ${fmt(summary.new_GSO_geometry_files_downloaded_and_hashed)} 个 GSO 样本；其余资产保留逐项核查状态。`;
  const objectCounts = data.sourceObjectCounts || {};
  const rowCounts = data.sourceRowCounts || data.sourceCounts || {};
  const sourceKeys = [...new Set([...Object.keys(objectCounts), ...Object.keys(rowCounts)])];
  $("source-rows").innerHTML = sourceKeys.map((id) => {
    const [label, url] = sourceLabels[id] || [id, ""];
    const assets = (sourceAssetLinks[id] || []).map(([href, text]) => link(href, text)).join(" · ");
    return `<tr data-source-id="${esc(id)}"><td>${link(url, label) || esc(label)}${assets ? `<div class="scaling-asset-links">${assets}</div>` : ""}</td><td>${fmt(objectCounts[id])}</td><td>${fmt(rowCounts[id])}</td></tr>`;
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
  try {
    if (window.MATERIAL_PAYLOAD_READY) await window.MATERIAL_PAYLOAD_READY;
    if (!window.SCALING_DATA) throw new Error("交互数据未载入，请重试。");
    Object.assign(data, window.SCALING_DATA);
    if (!window.verifyDatasetView('objects', data)) return;
  } catch (error) {
    $("load-error").hidden = false;
    $("load-error").textContent = "交互列表暂未载入：" + error.message + " 上方为已发布快照。";
    return;
  }
  const componentPageSize = 60;
  const flexibleMaterialNames = new Set(["rubber", "fabric", "leather"]);
  const sourceMaterialTokens = (value) => String(value || "").toLocaleLowerCase().split(/[|,;\/\s]+/).filter(Boolean);
  const componentEntries = (data.newPhysicalComponents || []).map((item, index) => {
    const acceptedRegions = (item.official_bound_material_regions || []).filter((region) =>
      !/REJECT|QUARANTIN|HOLD/i.test([region.plausibility_status, region.review_decision].join(" ")));
    const hasRegionReview = item.hasRegionReview ?? ((item.official_bound_material_regions?.length || 0) + (item.quarantined_bound_material_regions?.length || 0) > 0);
    const sourceLabels = hasRegionReview ? (item.acceptedMaterialTokens || acceptedRegions.flatMap((region) => [region.source_label_raw, region.source_label_normalized])) : [item.material_label_raw];
    const flexibleTags = new Set(["official", "approximate"].includes(item.material_status_kind) ? sourceLabels.flatMap(sourceMaterialTokens).filter((tag) => flexibleMaterialNames.has(tag)) : []);
    const searchText = [item.component_id, item.object_id, item.component_path,
      item.component_name_cn, item.component_name_en, item.component_scope,
      item.object_name_cn, item.object_name_en, item.material_label, item.material_label_raw,
      ...(item.acceptedMaterialLabels || acceptedRegions.flatMap((region) => [region.source_label_raw, region.source_label_normalized, region.source_label_cn]))].join(" ").toLocaleLowerCase();
    return { item, index, flexibleTags, searchText };
  }).sort((a, b) => Number(b.flexibleTags.size > 0) - Number(a.flexibleTags.size > 0) || a.index - b.index);
  let activeComponentPage = 0;
  const componentPageSelect = $("component-page");
  function componentCardHtml(item) {
    const kind = item.material_status_kind || "hold";
    const label = item.material_status_label || "组件材料待核";
    const note = item.material_status_note || "组件身份已核，材料对应关系仍待补证。";
    const material = kind === "hold" ? "材料尚未核定" : (item.material_label || item.material_label_raw || "来源标签见原文");
    const sourceStatementsOnly = item.bindingCountScope === "SOURCE_STATEMENTS_NOT_VERIFIED_NONEMPTY_FACE_REGIONS";
    const regionCount = item.authoredBindingStatementCount ?? item.officialBoundRegionCount ?? item.official_bound_material_regions?.length;
    const regionNote = regionCount ? (sourceStatementsOnly
      ? `<small>${fmt(regionCount)} 条源定义绑定语句（不是非空面区数量）；最终几何面区有效覆盖尚未核验，不新增组件数。</small>`
      : `<small>${fmt(regionCount)} 条来源材料绑定；几何面区有效覆盖尚未核验，不新增组件数。</small>`) : "";
    return `<article data-component-id="${esc(item.component_id)}">
    <h3>${esc(item.component_name_cn || item.component_scope || item.component_id)}</h3><p>${esc(item.object_name_cn || item.object_name_en)} · ${esc(item.object_name_en)}</p>
    <small>组件 ID：${esc(item.component_id)}</small><code>${esc(item.component_path)}</code><p>${esc(item.component_identity_note || "独立官方几何引用、质量/惯量及关节成员关系；通过组件身份审核。")}</p>
    <span class="scaling-badge ${kind === "official" ? "verified" : "pending"}">${esc(label)}</span>
    <p><strong>${esc(material)}</strong></p><p>${esc(note)}</p><small>${esc(item.material_scope_note || "")}</small>${regionNote}
    <p>原文定位：${esc(item.source_locator || "见官方结构文件")}</p>${link(item.source_url, "打开官方结构文件")}${link(item.source_manifest_url, "打开资产包")}
  </article>`;
  }

  function renderComponents(resetPage = false) {
    if (resetPage) activeComponentPage = 0;
    const query = $("component-search").value.trim().toLocaleLowerCase();
    const materialFilter = $("component-material").value;
    const matches = componentEntries.filter((entry) => (!query || entry.searchText.includes(query)) &&
      (materialFilter === "all" || (materialFilter === "flexible" ? entry.flexibleTags.size > 0 : entry.flexibleTags.has(materialFilter))));
    const pageCount = Math.ceil(matches.length / componentPageSize);
    activeComponentPage = Math.max(0, Math.min(activeComponentPage, pageCount - 1));
    componentPageSelect.innerHTML = pageCount ? Array.from({ length: pageCount }, (_, index) =>
      '<option value="' + index + '">第 ' + (index + 1) + ' / ' + pageCount + ' 页</option>').join("") : '<option value="0">无匹配页</option>';
    componentPageSelect.value = String(activeComponentPage);
    componentPageSelect.disabled = !pageCount;
    $("component-prev").disabled = !pageCount || activeComponentPage === 0;
    $("component-next").disabled = !pageCount || activeComponentPage === pageCount - 1;
    const start = activeComponentPage * componentPageSize;
    const visible = matches.slice(start, start + componentPageSize);
    $("component-page-status").textContent = '共 ' + fmt(componentEntries.length) + ' 张实体组件卡 · 筛选命中 ' + fmt(matches.length) + ' 张 · ' +
      (pageCount ? '第 ' + (activeComponentPage + 1) + '/' + pageCount + ' 页 · 本页第 ' + fmt(start + 1) + '–' + fmt(start + visible.length) + ' 张（每页最多 ' + componentPageSize + ' 张）' : '无匹配组件，请调整搜索或筛选');
    $("component-cards").innerHTML = visible.length ? visible.map((entry) => componentCardHtml(entry.item)).join("") : '<p class="scaling-note">没有匹配组件；可清空搜索并选择“全部材料”。</p>';
  }
  componentPageSelect.addEventListener("change", () => {
    activeComponentPage = Number(componentPageSelect.value);
    renderComponents();
  });
  $("component-prev").addEventListener("click", () => { activeComponentPage -= 1; renderComponents(); });
  $("component-next").addEventListener("click", () => { activeComponentPage += 1; renderComponents(); });
  $("component-search").addEventListener("input", () => renderComponents(true));
  $("component-material").addEventListener("change", () => renderComponents(true));
  renderComponents();
  const propertyNote = summary.current_cycle === "cycle13" ? "本轮新采集 " + fmt(summary.current_cycle_collection_complete_groups) + " 完整组、" + fmt(summary.current_cycle_collection_partial_groups) + " 缺项组；另复核35条旧完整组，修正7条，撤回或重分28条，并恢复25条缺项记录。来源纠错净完整组−27、缺项组+25；合计净完整组−26、缺项组+55。缺项不补值，来源预设及项目混合律不作实测证据。" : cycle3 ? `本轮新增 ${fmt(summary.current_cycle_complete_property_groups)} 完整组、${fmt(summary.current_cycle_incomplete_property_groups)} 缺项组（${fmt(summary.current_cycle_property_value_cells)} 个属性槽位），包含实测、实验推导及来源参考汇编；方向、统计量、密度与模量定义逐条保留，不等于商品实测。` : cycle2 ? `本轮另增加 ${fmt(summary.cycle2_incomplete_property_groups)} 条缺项组（${fmt(summary.cycle2_property_value_cells)} 个属性值格），不计入完整组或组件数。` : "";
  $("release-boundary").textContent = `研究完整与缺项共 ${fmt(summary.total_records)} 组，包含独立标记的数据库转录层。${propertyNote}正式材料映射 ${fmt(summary.formal_material_mapping_rows_unchanged)} 行未因本轮标签或组件新增而自动晋级。全库几何内容去重未完成。`;
  const hashes = { expanded_inventory_sha256: "扩充对象组件清单 SHA-256", feedback_queue_sha256: "待办队列 SHA-256", baseline_sha256: "原始对象表 SHA-256" };
  $("release-hashes").innerHTML = Object.entries(hashes).filter(([key]) => summary[key]).map(([key, label]) => `<dt>${label}</dt><dd>${esc(summary[key])}</dd>`).join("");


  // New WHOLE source objects remain separate from authored physical-component cards.
  const newItems = (data.newSourceObjects || data.cycle8NewSourceObjects || []).map((item, index) => ({item, index, search: [item.objectId, item.sourceId, item.nameCn, item.nameEn, item.category, item.materialLabel, item.sourceFamily].join(" ").toLowerCase()})).sort((a,b) => Number(b.item.flexiblePriority)-Number(a.item.flexiblePriority) || a.index-b.index);
  let newPage=0;
  const newSize=40, newSelect=$("new-source-page");
  function renderNew(reset=false) {
    if(reset)newPage=0;
    const q=$("new-source-search").value.trim().toLowerCase(), mode=$("new-source-filter").value;
    const hits=newItems.filter(({item,search}) => (!q || search.includes(q)) && (mode==="all" || (mode==="flexible" ? item.flexiblePriority : item.sourceFamily===mode)));
    const pages=Math.ceil(hits.length/newSize);newPage=Math.max(0,Math.min(newPage,pages-1));
    newSelect.innerHTML=pages?Array.from({length:pages},(_,i)=>`<option value="${i}">第 ${i+1}/${pages} 页</option>`).join(""):'<option value="0">无匹配页</option>';
    newSelect.value=String(newPage);newSelect.disabled=!pages;
    $("new-source-prev").disabled=!pages || newPage===0;$("new-source-next").disabled=!pages || newPage===pages-1;
    $("new-source-status").textContent=`累计新增来源对象 ${fmt(newItems.length)} 个 · 命中 ${fmt(hits.length)} 个 · 第 ${pages?newPage+1:0}/${pages} 页 · 每页最多 ${newSize} 个`;
    $("new-source-rows").innerHTML=hits.slice(newPage*newSize,(newPage+1)*newSize).map(({item})=>`<tr>
      <td data-label="物体与来源身份"><strong>${esc(item.nameCn || item.nameEn)}</strong><small>${esc(item.nameEn)}</small><small>${esc(item.objectId)}</small><small>${esc(item.sourceId)} · ${esc(item.sourceFamilyLabel || item.sourceFamily)}</small><small>${esc(item.category)}</small></td>
      <td data-label="组件 / 材料状态"><p>${esc(item.componentScope)}</p><span class="scaling-badge pending">${esc(item.materialStatusLabel)}</span><p>${esc(item.materialLabel)}</p><small>${esc(item.materialNote)}</small><small>WHOLE 整件占位；未枚举真实分件；本批无 E/ν/ρ 物性赋值。</small><small>${item.flexiblePriority?"柔性 / 混合候选优先，仅检索分类，不证明材料或软硬。":"来源身份与材料证据分层记录。"}</small></td>
      <td data-label="来源与 3D 资产"><div class="scaling-asset-links">${link(item.sourceUrl,"来源清单")}${link(item.mappingSourceUrl,"材料说明 / 候选依据")}${link(item.assetUrl,"下载 3D 资产包")}</div><span class="scaling-badge ${isDownloadedGlb(item) ? "verified" : "pending"}">${esc(item.assetStatusLabel)}</span><small>${esc(item.license)}</small><small>包内路径：${esc(item.archivePath)}</small><small>${esc(item.downloadStatus)}</small>${item.geometrySha256 ? `<small>GLB SHA-256：${esc(item.geometrySha256)}</small><small>负载顶点 / 三角形：${fmt(item.geometryVertices)} / ${fmt(item.geometryFaces)}；mesh / 材质槽 / 纹理：${fmt(item.geometryMeshes)} / ${fmt(item.materialSlots)} / ${fmt(item.textures)}</small>` : ""}<small>${esc(item.limitations)}</small></td></tr>`).join("") || '<tr><td colspan="3">没有匹配的新增对象。</td></tr>';
  }
  newSelect.addEventListener("change",()=>{newPage=Number(newSelect.value);renderNew();});
  $("new-source-prev").addEventListener("click",()=>{newPage--;renderNew();});
  $("new-source-next").addEventListener("click",()=>{newPage++;renderNew();});
  $("new-source-search").addEventListener("input",()=>renderNew(true));
  $("new-source-filter").innerHTML += [...new Set(newItems.map(({item})=>item.sourceFamily))].map(f=>`<option value="${esc(f)}">${esc(sourceLabels[f]?.[0] || f)}</option>`).join("");
  $("new-source-filter").addEventListener("change",()=>renderNew(true));
  renderNew();
  if ($("cycle13-payload-note")) $("cycle13-payload-note").textContent = "本轮新增 " + fmt(summary.current_cycle_new_geometry_identities) + " 个来源对象；" + fmt(summary.current_cycle_real_components_added) + " 个作者实体替换 " + fmt(summary.current_cycle_fallbacks_replaced) + " 个WHOLE。新增1个实际GLB及2个USDC主几何，外部依赖未全冻结。旧完整组纠错与新采集分别列示，不把净变化当新增。";
  if ($("cycle12-payload-note")) $("cycle12-payload-note").textContent = "Cycle12：304个新增来源对象，260个来源实体替63个WHOLE；未新增GLB。此条为已发布历史记录。";
  if ($("cycle11-payload-note")) $("cycle11-payload-note").textContent = "Cycle11 已核161个柔性/混合优先来源对象、185个来源实体替换44个WHOLE；该轮来源卡累计484，未新增GLB下载。";
  if ($("cycle10-payload-note")) $("cycle10-payload-note").textContent = "Cycle10 已收111个来源对象、164个源定义实体，替换97个WHOLE；该轮来源卡累计323。本行仅记录历史批次。";
  if ($("cycle9-payload-note")) $("cycle9-payload-note").textContent = `Cycle9 已核既有 ${fmt(summary.cycle9_verified_glb_payloads)} 个 GLB，共 ${fmt(summary.cycle9_verified_glb_bytes)} 字节；Cycle10、Cycle11 没有新增 GLB 下载事实。`;

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
      const downloaded = /^DOWNLOADED_OFFICIAL/.test(item.assetStatus || "");
      return `<tr><td data-label="物体与来源身份"><strong>${esc(item.nameCn || item.nameEn)}</strong><small>${esc(item.nameEn)}</small><small>${esc(item.id)}</small><small>${esc(item.category)} · ${esc(item.source)}</small></td>
      <td data-label="组件 / 材料状态"><p>${esc(item.componentScope)}</p><span class="scaling-badge pending">${item.sourceMaterialBacklinks?.length ? "有官方文本回链 · 模型绑定待核" : (item.materialReviewNote ? "元数据已筛查 · 尚无可接受材料回链" : "来源未报告材料 · 待核")}</span>${backlinksHtml(item.sourceMaterialBacklinks)}<small>无 E/ν/ρ 正式材料赋值</small></td>
      <td data-label="来源与 3D 资产"><div class="scaling-asset-links">${link(item.sourceUrl, "来源清单")}${link(item.assetUrl, "下载资产 ZIP")}</div><span class="scaling-badge ${downloaded ? "verified" : "pending"}">${downloaded ? "已下载并校验的样本" : "官方模式链接 · 待逐项验证"}</span><small>${esc(item.license)}</small>${item.geometrySha256 ? `<small>OBJ SHA-256：${esc(item.geometrySha256)}</small><small>包内路径：${esc(item.geometryArchiveEntryPath)}</small>` : ""}</td></tr>`;
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
        const response = await fetch(pages[index].url, {signal:AbortSignal.timeout(30000)});
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const bytes = await response.arrayBuffer();
        const hash = [...new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))].map(n=>n.toString(16).padStart(2,'0')).join('');
        if (!pages[index].sha256 || hash !== pages[index].sha256) throw new Error('资产分页与当前发布版本不一致');
        rows = JSON.parse(new TextDecoder().decode(bytes));
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
