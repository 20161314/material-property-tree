(async () => { if (window.MATERIAL_PAYLOAD_READY) await window.MATERIAL_PAYLOAD_READY;
(() => {
  const data = window.PHASE1_RANGES;
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
  scopeFilter.value = new URLSearchParams(window.location.search).get("scope") === "historical" || !hasCanonical ? "historical" : "canonical";
  if (!hasCanonical) scopeFilter.options[0].disabled = true;
  let page = 0;
  const pageSize = 100;
  const isCanonical = () => scopeFilter.value === "canonical" && hasCanonical;
  const targets = () => isCanonical() ? data.canonicalTargets : data.targets;
  const summary = data.summary;

  function renderSummary() {
    const current = isCanonical() ? { ...data.summary, ...data.canonicalSummary } : data.summary;
    const coverage = (value) => value === undefined ? "待汇总" : value + "/" + current.targetCount + (isCanonical() ? " 规范材料" : " 历史目标");
    const values = {
      "stat-records": fmt(current.tripletRecords),
      "stat-incomplete-records": fmt(current.incompleteRecords),
      "stat-reviewed": fmt(current.reviewedRecords),
      "stat-covered": coverage(current.materialsWithCompleteRecord),
      "stat-partial-materials": coverage(current.materialsWithIncompleteRecord),
      "stat-no-values": coverage(current.materialsWithoutAnyValue),
      "stat-e-coverage": coverage(current.materialsWithE),
      "stat-nu-coverage": coverage(current.materialsWithNu),
      "stat-rho-coverage": coverage(current.materialsWithRho),
      "stat-all-properties": coverage(current.materialsWithAllThreeFromAnyGroup),
      "stat-doc-keys": fmt(current.sourceDocumentKeys),
    };
    Object.entries(values).forEach(([id, value]) => { $(id).textContent = value; });
    $("unmapped-note").textContent = `这 ${fmt(data.summary.unmappedRecords)} 条完整记录未关联到历史 193 项目标，仍计入研究总账；其中部分材料已在最新规范材料全库中单独建叶。`;
    $("stage-progress-copy").textContent = `${fmt(current.reviewedRecords)} 条；持续扩充，不设数量上限`;
    $("unmapped-summary-count").textContent = fmt(data.summary.unmappedRecords);
    $("coverage-copy").textContent = isCanonical() ? "规范材料及已审参考覆盖；子树汇总与外库组成身份不重复计为新材料。" : `精确身份/原文标签 ${current.exactTargets} 项 · 细分材料参考 ${current.subtypeTargets} 项 · 家族参考 ${current.familyReferenceTargets} 项`;
    $("origin-copy").textContent = Object.entries(current.origins || {}).map(([key, count]) => `${originNames[key] || key} ${fmt(count)}`).join("；");
    $("coverage-scope-note").textContent = isCanonical() ? "覆盖分母：最新规范材料全库。外部数据库组成身份单列分页，不与树节点直接相加。" : (hasCanonical ? "当前为历史 193 项目标追踪；最新规范材料全库可在筛选器切换。" : "当前为历史 193 项目标追踪；最新全库覆盖数据尚未载入。");
    $("table-title").textContent = isCanonical() ? "最新规范材料全库" : "历史 193 项材料目标";
    $("coverage-denominator-note").textContent = isCanonical() ? "分母为最新规范材料并集；细材料可无对应物体" : "分母为历史 193 项目标；保留原追踪口径";
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
    if (target.status === "LIQUID_WAIVER") return ["液体豁免", "liquid"];
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

  function render() {
    const query = $("material-search").value.trim().toLocaleLowerCase();
    const status = $("status-filter").value;
    const family = familyFilter.value;
    const sort = $("sort-order").value;
    let rows = targets().filter((target) => {
      if (status === "covered" && target.completeRecordCount === 0) return false;
      if (status === "partial" && target.incompleteRecordCount === 0) return false;
      if (status === "missing" && (target.status === "LIQUID_WAIVER" || target.completeRecordCount > 0 || target.incompleteRecordCount > 0)) return false;
      if (status === "liquid" && target.status !== "LIQUID_WAIVER") return false;
      if (family !== "all" && target.family !== family) return false;
      const searchable = [target.id, target.nameCn, target.nameEn, target.sourceLabels, familyNames[target.family]].join(" ").toLocaleLowerCase();
      return !query || searchable.includes(query);
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
      const stage2 = target.status === "LIQUID_WAIVER" ? "液体不作硬性要求" : "完整与缺项记录同步收集";
      return `<tr>
        <td>${detailSummary}<small class="family-label">${esc(familyNames[target.family] || target.family)}</small></td>
        <td><strong>${relationCount}</strong><small>主账 ${target.recordCount.toLocaleString("en")} 组</small>${extCount ? `<small>另有数据库完整 ${target.externalCompleteRecordCount.toLocaleString("en")} · 缺项 ${target.externalIncompleteRecordCount.toLocaleString("en")}</small><a href="${esc(target.externalCollectionUrl)}">分页查看数据库原始来源组</a>` : ""}</td>
        <td>${target.documentKeyCount.toLocaleString("en")}<small>主账文档键（外库另列）</small></td>
        <td class="range-cell">${fmtRange(target.E)}<small>报告跨度</small></td>
        <td class="range-cell">${fmtRange(target.nu)}<small>报告跨度</small></td>
        <td class="range-cell">${fmtRange(target.rho)}<small>${esc(target.densityScopeNote || '报告跨度')}</small></td>
        <td><span class="status-badge ${badge}">${label}</span><small>${stage2}</small></td>
      </tr>`;
    }).join("");

    $("material-table-body").querySelectorAll("details[data-target]").forEach((details) => {
      details.addEventListener("toggle", () => {
        if (!details.open || details.dataset.loaded) return;
        const target = targets().find((item) => item.id === details.dataset.target);
        const list = details.querySelector(".evidence-list");
        if (target) appendEvidenceBatch(target, list, 0);
        details.dataset.loaded = "true";
      });
    });
  }

  function appendEvidenceBatch(target, list, offset) {
    list.querySelector(".load-more-evidence")?.remove();
    const pageSize = 25;
    const next = target.evidence.slice(offset, offset + pageSize);
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
  renderSummary();
  render();
})();

})();
