(async () => { if (window.MATERIAL_PAYLOAD_READY) await window.MATERIAL_PAYLOAD_READY;
(() => {
  const data = window.PHASE1_RANGES;
  if (!window.verifyDatasetView || !window.verifyDatasetView('coverage', data)) return;
  if (!data) return;

  const familyNames = {
    biomaterial: "生物与食品材料", ceramic: "陶瓷", foam: "泡沫与多孔材料",
    glass: "玻璃与玻璃陶瓷", leather: "皮革", metal: "金属与合金",
    other_media: "复合材料与其他介质", paper: "纸与纸板", polymer: "聚合物与塑料",
    rubber: "橡胶与弹性体", stone: "石材与矿物", textile: "纤维与纺织材料", wood: "木材与工程木",
  };
  const relationshipNames = {
    DIRECT_CANONICAL_MATERIAL: "直接规范材料记录",
    REVIEWED_TARGET_SUBTYPE_REFERENCE: "已审细分材料参考",
    REVIEWED_TARGET_EXACT_REFERENCE: "已审目标材料参考",
    EXACT_IDENTITY: "精确材料身份",
    SOURCE_LABEL_MATCH: "原文标签匹配",
    CONDITIONAL_SUBTYPE_REFERENCE: "细分材料参考",
    SOURCE_DEFINED_SUBTYPE: "来源定义的细分材料",
    FAMILY_COVERAGE_ONLY: "材料家族参考",
  };
  const originNames = {
    FORMAL_EVIDENCE: "正式证据",
    REVIEWED_CANDIDATE: "审核候选",
    SUPPLEMENTAL_RESEARCH_CANDIDATE: "补充研究候选",
    HISTORICAL_OFFICIAL_COMPILATION_REVIEW: "回源官方材料汇编",
    REVIEWED_PARTIAL_CANDIDATE: "已审缺项候选",
    HISTORICAL_SOURCE_GROUP_REVIEW: "历史来源组回核",
    LEGACY_NEWLY_SOURCE_CHECKED: "旧版证据回核",
    WOOD_PARTIAL_SOURCE_REVIEW_2026_11_12: "木材缺项回核",
    "partial_gap_recovery_textile_2026-11-12": "纺织皮革缺项回核",
    POLYMER_PARTIAL_GAP_SOURCE_RECOVERY: "聚合物缺项回核",
  };
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[char]);
  const fmt = (value) => {
    if (value === "" || value === null || value === undefined || !Number.isFinite(Number(value))) return "—";
    return Number(value).toLocaleString("en", { maximumSignificantDigits: 5 });
  };
  const fmtRange = (range) => {
    if (!range || range[0] === "" || range[1] === "") return "—";
    const low = fmt(range[0]);
    const high = fmt(range[1]);
    return low === high ? low : `${low}–${high}`;
  };

  const scopeFilter = $("scope-filter");
  const hasCanonical = Array.isArray(data.canonicalTargets) && Boolean(data.canonicalSummary);
  const priority = window.DATASET_RELEASE.object_priority_coverage;
  const objectIds = new Set(priority?.objectMaterialIds || []);
  if (priority) {
    scopeFilter.innerHTML='<option value="object">物体关联材料（优先）</option><option value="canonical">全部研究材料</option><option value="retained">无物体且三项齐全</option><option value="candidate">无物体缺项候选</option>';
  }
  scopeFilter.value = "canonical"; // Current scope always follows the dynamic material union.
  if (!hasCanonical) throw new Error("当前材料覆盖数据缺失");
  let page = 0;
  const pageSize = 100;
  const isCanonical = () => true;
  const targets = () => {
    const rows=data.canonicalTargets;
    if (!priority || scopeFilter.value==='canonical') return rows;
    if (scopeFilter.value==='object') return rows.filter(row=>objectIds.has(row.id));
    const complete=row=>['E','nu','rho'].every(key=>row[key][0]!=='');
    return rows.filter(row=>!objectIds.has(row.id) && (scopeFilter.value==='retained' ? complete(row) : !complete(row)));
  };
  const summary = data.summary;
  const evidenceRequests = new Map();
  async function loadEvidenceChunk(index) {
    if (evidenceRequests.has(index)) return evidenceRequests.get(index);
    const task = (async () => {
      const spec = data.recordDetailChunks?.[index];
      if (!spec) throw new Error("证据分块索引缺失");
      const url = new URL(spec.url, location.href);
      if (url.origin !== location.origin || !url.pathname.includes('/coverage-details/')) throw new Error("证据路径无效");
      const controller = new AbortController();
      let idleTimer;
      const resetIdle = () => { clearTimeout(idleTimer); idleTimer = setTimeout(() => controller.abort(), 30000); };
      const totalTimer = setTimeout(() => controller.abort(), 180000);
      resetIdle();
      let bytes;
      try {
        const response = await fetch(url, {signal: controller.signal});
        if (!response.ok) throw new Error("HTTP " + response.status);
        resetIdle();
        if (response.body) {
          const reader = response.body.getReader(), chunks = [];
          let length = 0;
          try {
            while (true) {
              const {done, value} = await reader.read();
              if (done) break;
              if (!value.byteLength) continue;
              resetIdle(); chunks.push(value); length += value.byteLength;
            }
          } finally { reader.releaseLock(); }
          bytes = new Uint8Array(length);
          let offset = 0;
          for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
        } else bytes = new Uint8Array(await response.arrayBuffer());
      } finally { clearTimeout(idleTimer); clearTimeout(totalTimer); }
      if (bytes[0] === 31 && bytes[1] === 139) {
        bytes = new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).arrayBuffer());
      }
      const hash = Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256', bytes))).map(x => x.toString(16).padStart(2, '0')).join('');
      if (hash !== spec.sha256) throw new Error("证据校验失败");
      const chunk = JSON.parse(new TextDecoder().decode(bytes));
      if (chunk.releaseId !== data.releaseId || !chunk.recordsById || Object.keys(chunk.recordsById).length !== spec.records) throw new Error("证据版本或条数不一致");
      for (const [id, record] of Object.entries(chunk.recordsById)) {
        if (record.record_id !== id || data.recordDetails[id] !== index) throw new Error("证据身份索引不一致");
      }
      Object.assign(data.recordsById, chunk.recordsById);
    })();
    evidenceRequests.set(index, task);
    try { await task; } catch (error) { evidenceRequests.delete(index); throw error; }
  }
  async function ensureEvidence(entries) {
    if (!data.progressiveEvidence) return;
    const indexes = [...new Set(entries.filter(entry => !data.recordsById[entry.recordId]).map(entry => data.recordDetails[entry.recordId]))];
    // Bound each evidence batch; simultaneous material expansions share matching requests.
    for (let start = 0; start < indexes.length; start += 3) {
      await Promise.all(indexes.slice(start, start + 3).map(loadEvidenceChunk));
    }
    if (entries.some(entry => !data.recordsById[entry.recordId])) throw new Error("关联记录未完整载入");
  }

  function renderSummary() {
    const cohort = !priority || scopeFilter.value==='canonical' ? data.canonicalSummary : scopeFilter.value==='object' ? priority.objectMaterials : scopeFilter.value==='retained' ? priority.unlinkedComplete : priority.researchCandidates;
    const current = { ...data.summary, ...cohort };
    const coverage = (value) => value === undefined ? "待汇总" : value + "/" + current.targetCount + " 规范材料";
    const values = {
      "stat-records": fmt(current.tripletRecords),
      "stat-incomplete-records": fmt(current.incompleteRecords),
      "stat-reviewed": Number(current.reviewedRecords).toLocaleString("en"),
      "stat-covered": coverage(current.materialsWithCompleteRecord),
      "stat-partial-materials": coverage(current.materialsWithIncompleteRecord),
      "stat-no-values": coverage(current.materialsWithoutAnyValue),
      "stat-e-coverage": coverage(current.materialsWithE),
      "stat-nu-coverage": coverage(current.materialsWithNu),
      "stat-rho-coverage": coverage(current.materialsWithRho),
      "stat-all-properties": coverage(current.materialsWithAllThreeFromAnyGroup),
      "stat-doc-keys": fmt(window.DATASET_RELEASE.source_keys.document_or_database_citation_keys),
    };
    Object.entries(values).forEach(([id, value]) => { $(id).textContent = value; });
    $("unmapped-note").textContent = `这 ${fmt(data.summary.unmappedRecords)} 条主账完整记录尚未关联当前规范材料节点；仍保留在研究账中。`; 
    $("stage-progress-copy").textContent = `${Number(current.reviewedRecords).toLocaleString("en")} 条；持续扩充，不设数量上限`;
    $("unmapped-summary-count").textContent = fmt(data.summary.unmappedRecords);
    $("coverage-copy").textContent = "规范材料及已审细分参考覆盖；关联行不重复计为新来源组。";
    $("origin-copy").textContent = Object.entries(current.origins || {}).map(([key, count]) => `${originNames[key] || key} ${fmt(count)}`).join("；");
    $("coverage-scope-note").textContent = "覆盖分母：当前非液体规范材料并集。外库组成身份另列，不重复计入。";
    $("table-title").textContent = "当前规范材料全库";
    $("coverage-denominator-note").textContent = "分母随当前材料库更新；证据叶可以暂无对应物体";
    if (priority) {
      const label=scopeFilter.selectedOptions[0].textContent;
      $("table-title").textContent=label;
      $("coverage-scope-note").textContent='当前范围：'+label+'，共 '+current.targetCount+' 种。优先补齐物体关联材料；无物体且缺项仅列研究候选。';
      $("coverage-denominator-note").textContent='分母为当前选中范围；完整/缺项组总数仍是全库来源组数';
    }
  }

  if (summary.externalCatalogUrl) {
    const note = document.createElement("p");
    note.textContent = "主账完整 " + summary.mainCompleteRecords.toLocaleString("en") + "、缺项 " + summary.mainIncompleteRecords.toLocaleString("en") + "；另含玻璃数据库转录完整 " + summary.externalCompleteRecords.toLocaleString("en") + "、缺项 " + summary.externalIncompleteRecords.toLocaleString("en") + "。数据库未逐篇重读；引用不清的三项齐组另隔离。";
    document.querySelector(".phase1-policy").append(note);
  }
  const familyFilter = $("family-filter");
  [...new Set([...data.targets, ...(data.canonicalTargets || [])].map((target) => target.family))].sort().forEach((family) => {
    const option = document.createElement("option");
    option.value = family;
    option.textContent = familyNames[family] || family;
    familyFilter.append(option);
  });

  function statusLabel(target) {
    if (target.completeRecordCount > 0) return ["有完整组", ""];
    if (target.incompleteRecordCount > 0) return ["仅有不完整组", "partial"];
    return ["暂无来源组", "missing"];
  }

  function evidenceHtml(entries) {
    return entries.map((entry) => {
      const record = data.recordsById[entry.recordId];
      if (!record) return "";
      const incomplete = record.record_type === "INCOMPLETE";
      const values = incomplete
        ? esc(`E ${record.E_source_value || "—"} · ν ${record.nu_source_value || "—"} · ρ ${record.rho_source_value || "—"}`)
        : `E ${fmtRange([record.E_low_GPa, record.E_high_GPa])} GPa · ν ${fmtRange([record.nu_low, record.nu_high])} · ρ ${fmtRange([record.rho_low_kg_m3, record.rho_high_kg_m3])} kg/m³`;
      let directional = "";
      if (record.directional_values_json) {
        try {
          const detail = JSON.parse(record.directional_values_json);
          const labels = {
            strain_percent: "应变 %", E_parallel_GPa: "轴向 E|| GPa",
            E_parallel_uncertainty_GPa: "轴向 E 不确定度 GPa", E_perpendicular_GPa: "横向 E⊥ GPa",
            E_perpendicular_uncertainty_GPa: "横向 E 不确定度 GPa", nu_31_32: "ν31/32",
            nu_31_32_uncertainty: "ν31/32 不确定度", nu_12: "ν12",
            nu_12_uncertainty: "ν12 不确定度", rho_assumed_kg_m3: "采用密度 kg/m³",
          };
          const detailText = Object.entries(detail)
            .filter(([key]) => labels[key])
            .map(([key, value]) => `${labels[key]} ${value}`)
            .join("；");
          if (detailText) directional = `<p>方向化原始记录：${esc(detailText)}</p>`;
        } catch {
          directional = `<p>方向化原始记录：${esc(record.directional_values_json)}</p>`;
        }
      }
      const source = record.url ? `<a href="${esc(record.url)}" target="_blank" rel="noopener noreferrer">打开来源</a>` : "来源链接缺失";
      return `<article class="evidence-row">
        <strong>${esc(record.material_identity)} <span class="evidence-status">${incomplete ? "不完整来源组" : esc(relationshipNames[entry.relationship] || entry.relationship)}</span></strong>
        <small>${esc(record.record_id)} · ${esc(record.source_id)} · ${esc(record.publisher_subject_name)} · ${esc(record.document_key)}</small>
        <div class="evidence-values-inline">${values}</div>
        ${incomplete ? `<p>同组仅有 ${esc(record.property_count)} 项可计入属性；不与其他来源拼接。</p>` : ""}
        <p>${esc(record.locator || "未提供定位")} · ${source}</p>
        <p>${esc(record.conditions || "未报告条件")}</p>
        ${record.evidence_role ? `<p>${esc(record.evidence_role)}</p>` : ""}
        ${directional}
        ${record.property_model ? `<p>数据性质：${esc(record.property_model)}</p>` : ""}
        ${record.method_or_basis ? `<p>数值依据：${esc(record.method_or_basis)}</p>` : ""}
        ${record.density_type ? `<p>密度类型：${esc(record.density_type)}</p>` : ""}
        ${record.density_type_values_json ? `<details><summary>密度按定义分别报告</summary><pre>${esc(record.density_type_values_json)}</pre></details>` : ""}
        ${record.scope_notes ? `<p>形态范围：${esc(record.scope_notes)}</p>` : ""}
        ${record.source_uncertainty_notes ? `<p>不确定度：${esc(record.source_uncertainty_notes)}</p>` : ""}
        ${record.limitations ? `<p>限制：${esc(record.limitations)}</p>` : ""}
        ${record.local_file ? `<details><summary>冻结文件与校验</summary><p>${esc(record.local_file)}</p><p>SHA-256：${esc(record.sha256)}</p></details>` : ""}
        ${record.property_citations_json ? `<details><summary>各属性原引用</summary><pre>${esc(record.property_citations_json)}</pre></details>` : ""}
      </article>`;
    }).join("");
  }

  const selectedMaterial = new URLSearchParams(location.search).get("material");
  if (selectedMaterial) $("material-search").value = selectedMaterial;
  function render() {
    const query = $("material-search").value.trim().toLocaleLowerCase();
    const status = $("status-filter").value;
    const family = familyFilter.value;
    const sort = $("sort-order").value;
    const exactId = targets().some(item => item.id.toLocaleLowerCase() === query);
    let rows = targets().filter((target) => {
      if (status === "covered" && target.completeRecordCount === 0) return false;
      if (status === "partial" && target.incompleteRecordCount === 0) return false;
      if (status === "missing" && (target.completeRecordCount > 0 || target.incompleteRecordCount > 0)) return false;
      if (family !== "all" && target.family !== family) return false;
      const searchable = [target.id, target.nameCn, target.nameEn, target.sourceLabels, familyNames[target.family]].join(" ").toLocaleLowerCase();
      return !query || (exactId ? target.id.toLocaleLowerCase() === query : searchable.includes(query));
    });
    rows = [...rows].sort((a, b) => {
      if (sort === "name") return a.nameCn.localeCompare(b.nameCn, "zh-CN");
      if (sort === "family") return (familyNames[a.family] || a.family).localeCompare(familyNames[b.family] || b.family, "zh-CN") || a.nameCn.localeCompare(b.nameCn, "zh-CN");
      return b.recordCount - a.recordCount || a.nameCn.localeCompare(b.nameCn, "zh-CN");
    });

    page = Math.min(page, Math.max(0, Math.ceil(rows.length / pageSize) - 1));
    $("result-count").textContent = `匹配 ${rows.length} / ${targets().length} 项；同一来源可关联多个材料，关系行不计为新来源记录。`;
    $("materials-page").textContent = rows.length ? `第 ${page + 1} / ${Math.ceil(rows.length / pageSize)} 页 · 每页 ${pageSize} 项` : "无匹配材料";
    $("materials-prev").disabled = page === 0;
    $("materials-next").disabled = (page + 1) * pageSize >= rows.length;
    rows = rows.slice(page * pageSize, (page + 1) * pageSize);
    $("material-table-body").innerHTML = rows.map((target) => {
      const [label, badge] = statusLabel(target);
      const relationCount = `完整 ${target.completeRecordCount} · 不完整 ${target.incompleteRecordCount}`;
      const extCount = (target.externalCompleteRecordCount || 0) + (target.externalIncompleteRecordCount || 0);
      const detailSummary = target.recordCount ? `<details class="material-expand" data-target="${esc(target.id)}"><summary><strong>${esc(target.nameCn)}</strong><small>${esc(target.nameEn)} · ${esc(target.id)}</small><span>查看 ${target.recordCount} 条关联记录</span></summary><div class="evidence-list"></div></details>` : `<strong>${esc(target.nameCn)}</strong><small>${esc(target.nameEn)} · ${esc(target.id)}</small>`;
      const stage2 = "完整与缺项记录同步收集";
      return `<tr>
        <td>${detailSummary}<small class="family-label">${esc(familyNames[target.family] || target.family)}</small><div class="material-view-links"><a href="research.html?material=${encodeURIComponent(target.id)}">材料树</a><a href="scaling.html?material=${encodeURIComponent(target.id)}">关联物体</a></div></td>
        <td><strong>${relationCount}</strong><small>主账 ${target.recordCount.toLocaleString("en")} 组</small>${extCount ? `<small>另有数据库完整 ${target.externalCompleteRecordCount.toLocaleString("en")} · 缺项 ${target.externalIncompleteRecordCount.toLocaleString("en")}</small><a href="${esc(target.externalCollectionUrl)}">分页查看数据库原始来源组</a>` : ""}</td>
        <td>${target.documentKeyCount.toLocaleString("en")}<small>主账文档键（外库另列）</small></td>
        <td class="range-cell">${fmtRange(target.E)}<small>报告跨度</small></td>
        <td class="range-cell">${fmtRange(target.nu)}<small>报告跨度</small></td>
        <td class="range-cell">${fmtRange(target.rho)}<small>${esc(target.densityScopeNote ? '密度定义与条件见原始记录' : '报告跨度')}</small></td>
        <td><span class="status-badge ${badge}">${label}</span><small>${stage2}</small></td>
      </tr>`;
    }).join("");

    const cellLabels=['材料与来源','数据组','文档键','E（GPa）','ν','ρ（kg/m³）','覆盖状态'];
    $("material-table-body").querySelectorAll('tr').forEach(row => [...row.cells].forEach((cell,index)=>cell.dataset.label=cellLabels[index]));
    $("material-table-body").querySelectorAll("details[data-target]").forEach((details) => {
      details.addEventListener("toggle", () => {
        if (!details.open || details.dataset.loaded || details.dataset.loading) return;
        const target = targets().find((item) => item.id === details.dataset.target);
        const list = details.querySelector(".evidence-list");
        if (target) appendEvidenceBatch(target, list, 0);
      });
    });
  }

  async function appendEvidenceBatch(target, list, offset) {
    if (list.dataset.loading) return;
    const details = list.closest('details');
    list.dataset.loading = "true"; details.dataset.loading = "true";
    list.querySelector(".load-more-evidence")?.remove();
    const pageSize = 25;
    const next = target.evidence.slice(offset, offset + pageSize);
    list.querySelectorAll('.evidence-load-status').forEach(node => node.remove());
    const notice = document.createElement('p');
    notice.className = 'evidence-load-status';
    notice.setAttribute('role', 'status'); notice.textContent = '正在载入本组来源证据…'; list.append(notice);
    try {
      await ensureEvidence(next);
      if (!list.isConnected) return;
      notice.remove(); details.dataset.loaded = "true";
    list.insertAdjacentHTML("beforeend", evidenceHtml(next));
    const nextOffset = offset + next.length;
    list.dataset.offset = String(nextOffset);
    if (nextOffset < target.evidence.length) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "load-more-evidence";
      button.textContent = `加载后续 ${Math.min(pageSize, target.evidence.length - nextOffset)} 条（已显示 ${nextOffset}/${target.evidence.length}）`;
      button.addEventListener("click", () => appendEvidenceBatch(target, list, Number(list.dataset.offset)));
      list.append(button);
    }
    } catch (error) {
      if (!list.isConnected) return;
      notice.textContent = '来源证据载入失败：' + (error.name === 'AbortError' ? '网络超时' : error.message);
      const retry = document.createElement('button'); retry.type = 'button'; retry.className = 'load-more-evidence';
      retry.textContent = '重试载入'; retry.addEventListener('click', () => appendEvidenceBatch(target, list, offset));
      list.append(retry);
    } finally {
      delete list.dataset.loading; delete details.dataset.loading;
      if (!details.open) notice.remove();
    }
  }

  $("unmapped-table-body").innerHTML = data.unmapped.map((record) => {
    const values = `E ${fmtRange([record.E_low_GPa, record.E_high_GPa])} GPa · ν ${fmtRange([record.nu_low, record.nu_high])} · ρ ${fmtRange([record.rho_low_kg_m3, record.rho_high_kg_m3])} kg/m³`;
    const source = record.url ? `<a href="${esc(record.url)}" target="_blank" rel="noopener noreferrer">来源链接</a>` : "—";
    return `<tr><td>${esc(record.record_id)}</td><td>${esc(record.material_identity)}</td><td>${esc(familyNames[record.family_id] || record.family_id)}</td><td>${values}</td><td>${esc(record.source_id)}<br>${source}</td><td>${esc(record.locator)}</td></tr>`;
  }).join("");

  ["material-search", "status-filter", "family-filter", "sort-order"].forEach((id) => $(id).addEventListener("input", () => { page = 0; render(); }));
  scopeFilter.addEventListener("change", () => { page = 0; renderSummary(); render(); });
  $("materials-prev").addEventListener("click", () => { page -= 1; render(); });
  $("materials-next").addEventListener("click", () => { page += 1; render(); });
  if (priority) {
    const params=new URLSearchParams(location.search);
    const selected=params.get('scope');
    const material=params.get('material') || params.get('node') || params.get('q');
    scopeFilter.value=['canonical','retained','candidate','object'].includes(selected) ? selected : material && !objectIds.has(material) ? 'canonical' : 'object';
  }
  renderSummary();
  render();
})();

})().catch(() => {});
