(() => {
  "use strict";

  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[char]);
  const readable = (value) => String(value ?? "")
    .replaceAll("合同校验", "规则检查")
    .replaceAll("计划与合同", "规则与计划")
    .replaceAll("冻结输入", "固定输入")
    .replaceAll("来源枚举", "列出来源物体")
    .replaceAll("事务与四状态", "合并与四类状态")
    .replaceAll("枚举稳定对象身份", "列出可追踪的物体")
    .replaceAll("来源身份", "来源中的物体编号")
    .replaceAll("生成材料关系候选", "生成部件与材料候选关系")
    .replaceAll("来源方法性质", "标签原始来源和生成方式")
    .replaceAll("规范材料身份", "统一材料名称")
    .replaceAll("独立审核树边", "独立审核材料分类关系")
    .replaceAll("代码维护材料BFS前沿", "维护下一批材料任务")
    .replaceAll("提取完整与缺项来源组", "提取完整组与缺项组")
    .replaceAll("单写者幂等事务合并", "由唯一合并程序写入版本")
    .replaceAll("代码重算四状态与覆盖", "重新计算四类状态和覆盖率")
    .replaceAll("代码守恒对账", "核对新增、撤回与重复记录")
    .replaceAll("执行结构与路线合同", "检查工作流结构和模型分工")
    .replaceAll("交接下一轮与有界重试", "交接下一轮并限制重试")
    .replaceAll("同源完整组", "同一资料中的完整组")
    .replaceAll("跨资料覆盖", "三项分别有来源的覆盖")
    .replaceAll("NOT_EXECUTED", "未执行（NOT_EXECUTED）")
    .replaceAll("identified material/result group", "可辨认的材料与结果组")
    .replaceAll("Release Merger", "发布合并器")
    .replaceAll("release gate", "发布门禁")
    .replaceAll("新 release 目录", "新的发布版本目录")
    .replaceAll("候选 release", "候选发布版本")
    .replaceAll("同一 release", "同一发布版本")
    .replace(/\brelease\b/gi, "发布版本")
    .replace(/\bpin\b/gi, "固定清单")
    .replace(/\bgap\b/gi, "缺口")
    .replace(/\bdelta\b/gi, "增量记录")
    .replace(/\blease\b/gi, "任务锁")
    .replace(/\bcommand\b/gi, "命令")
    .replace(/\blineage\b/gi, "来源链")
    .replaceAll("part/prim/mesh group", "部件、prim 或网格组")
    .replaceAll("site consistency", "网站一致性检查")
    .replaceAll("Luna/max", "gpt-6-luna（最高推理）")
    .replace(/\bLuna\b/g, "gpt-6-luna")
    .replaceAll("Sol", "gpt-6.1-sol")
    .replaceAll("BFS", "逐层遍历")
    .replaceAll("Harness", "工作流框架")
    .replace(/\bAgent\b/g, "推进代理")
    .replace(/\bplanned\b/g, "计划中")
    .replace(/\bhash\b/gi, "校验值");
  const statusClass = (status) => ["executable", "planned", "requires_model"].includes(status) ? status : "planned";
  const actorName = (value) => readable(value)
    .replaceAll("Verifier", "校验器")
    .replaceAll("Supervisor", "推进代理")
    .replaceAll("Source Enumerator", "来源枚举器")
    .replaceAll("Geometry Auditor", "几何核验器")
    .replaceAll("Component Mapper", "部件与材料采集器")
    .replaceAll("Independent Reviewer", "独立审核器")
    .replaceAll("Material Normalizer", "材料规范化器")
    .replaceAll("Evidence Collector", "证据采集器")
    .replaceAll("Release Merger", "发布合并器")
    .replaceAll(" + ", "与");
  const listHtml = (items) => "<ul>" + (items || []).map((item) => "<li>" + esc(readable(item)) + "</li>").join("") + "</ul>";

  const NODE_W = 304;
  const NODE_H = 176;
  const GAP_X = 88;
  const GAP_Y = 44;
  const ORIGIN_X = 84;
  const ORIGIN_Y = 112;

  let data;
  let selectedId = "";
  let layout = { width: 1200, height: 760, nodes: new Map() };
  let zoomBehavior;
  let currentTransform;
  let activePhase = "";
  const filters = { query: "", phase: "all", status: "all" };

  function statusInfo(status) {
    return data.statusLegend.find((item) => item.id === status) || { id: status, name: status, description: "" };
  }

  function statusName(status) {
    return ({ executable: "程序已实现", planned: "尚未实现", requires_model: "模型已接入" })[status] || statusInfo(status).name;
  }

  function modelInfo(route, fallback) {
    if (route === "code") return { name: "固定程序处理", model: "确定性脚本", reasoning_effort: "不调用模型", purpose: "解析、校验、去重、计数、合并与发布检查。" };
    const matched = data.modelRoutes.find((item) => item.id === route || item.model === fallback);
    if (!matched) return { name: fallback || "不使用模型", model: fallback || "—", reasoning_effort: "—", purpose: "" };
    return { ...matched, name: route === "bulk_review" ? "批量独立审核" : "研究与歧义判断" };
  }

  function effortName(value) {
    return ({ high: "高", max: "最高" })[value] || value;
  }

  function modelLabel(model) {
    if (model.model === "确定性脚本") return "确定性脚本（不调用模型）";
    return model.model + "（推理强度：" + effortName(model.reasoning_effort) + "）";
  }

  function visibleSteps() {
    const query = filters.query.trim().toLowerCase();
    return data.steps.filter((step) => {
      if (filters.phase !== "all" && step.phase !== filters.phase) return false;
      if (filters.status !== "all" && step.status !== filters.status) return false;
      if (!query) return true;
      const text = [step.id, step.name, step.summary, step.actor, step.model]
        .concat(step.inputs || [], step.actions || [], step.outputs || [], step.checks || [])
        .join(" ").toLowerCase();
      return text.includes(query);
    });
  }

  function buildLayout(steps) {
    const visibleIds = new Set(steps.map((step) => step.id));
    const phases = data.phases.filter((phase) => steps.some((step) => step.phase === phase.id));
    const nodes = new Map();
    let maxRows = 1;
    phases.forEach((phase, phaseIndex) => {
      const phaseSteps = data.steps.filter((step) => visibleIds.has(step.id) && step.phase === phase.id);
      maxRows = Math.max(maxRows, phaseSteps.length);
      phaseSteps.forEach((step, rowIndex) => {
        nodes.set(step.id, {
          step,
          x: ORIGIN_X + phaseIndex * (NODE_W + GAP_X),
          y: ORIGIN_Y + rowIndex * (NODE_H + GAP_Y)
        });
      });
    });
    const width = Math.max(980, ORIGIN_X * 2 + phases.length * NODE_W + Math.max(0, phases.length - 1) * GAP_X);
    const height = Math.max(720, ORIGIN_Y + maxRows * NODE_H + Math.max(0, maxRows - 1) * GAP_Y + 100);
    return { width, height, nodes, phases };
  }

  function connectorPath(from, to) {
    if (from.x === to.x) {
      const sx = from.x + NODE_W / 2;
      const sy = from.y + NODE_H;
      const tx = to.x + NODE_W / 2;
      const ty = to.y;
      const mid = (sy + ty) / 2;
      return "M" + sx + "," + sy + " C" + sx + "," + mid + " " + tx + "," + mid + " " + tx + "," + ty;
    }
    const sx = from.x + NODE_W;
    const sy = from.y + NODE_H / 2;
    const tx = to.x;
    const ty = to.y + NODE_H / 2;
    const bend = Math.max(46, (tx - sx) * 0.46);
    return "M" + sx + "," + sy + " C" + (sx + bend) + "," + sy + " " + (tx - bend) + "," + ty + " " + tx + "," + ty;
  }

  function renderGraph() {
    const steps = visibleSteps();
    layout = buildLayout(steps);
    const visibleIds = new Set(steps.map((step) => step.id));
    const phaseLabels = layout.phases.map((phase, index) => {
      const count = steps.filter((step) => step.phase === phase.id).length;
      const x = ORIGIN_X + index * (NODE_W + GAP_X);
      return '<div class="workflow-phase-label" style="left:' + x + 'px;width:' + NODE_W + 'px">' + esc(readable(phase.name)) + "<span>" + count + " 步</span></div>";
    }).join("");
    $("workflow-phase-labels").innerHTML = phaseLabels;

    $("workflow-nodes").innerHTML = steps.map((step) => {
      const point = layout.nodes.get(step.id);
      const state = statusInfo(step.status);
      const model = modelInfo(step.route, step.model);
      const routeLabel = model.model === "确定性脚本" ? "确定性脚本" : model.model + " · " + effortName(model.reasoning_effort);
      return '<button type="button" class="workflow-node status-' + statusClass(step.status) + '" data-step-id="' + esc(step.id) + '" aria-pressed="' + (step.id === selectedId) + '" style="left:' + point.x + 'px;top:' + point.y + 'px">' +
        '<span class="workflow-node-head"><span class="workflow-node-phase">' + esc(step.phase) + "</span><span class=\"workflow-status " + statusClass(step.status) + '">' + esc(statusName(step.status)) + "</span></span>" +
        '<span class="workflow-node-body"><strong>' + esc(readable(step.name)) + "</strong><small>" + esc(readable(step.summary)) + '</small><span class="workflow-node-route"><span>' + esc(routeLabel) + "</span><span>" + esc(actorName(step.actor)) + "</span></span></span></button>";
    }).join("");

    const paths = [];
    steps.forEach((step) => {
      (step.dependsOn || []).forEach((dependency) => {
        if (!visibleIds.has(dependency)) return;
        const from = layout.nodes.get(dependency);
        const to = layout.nodes.get(step.id);
        paths.push('<path data-from="' + esc(dependency) + '" data-to="' + esc(step.id) + '" class="' + ((dependency === selectedId || step.id === selectedId) ? "selected" : "") + '" d="' + connectorPath(from, to) + '"></path>');
      });
    });
    const svg = $("workflow-connectors");
    svg.setAttribute("viewBox", "0 0 " + layout.width + " " + layout.height);
    svg.innerHTML = paths.join("");
    const stage = $("workflow-stage");
    stage.style.width = layout.width + "px";
    stage.style.height = layout.height + "px";
    $("workflow-result-note").textContent = "显示 " + steps.length + " / " + data.steps.length + " 个步骤。节点保持可读，不自动缩成小字。";
    $("workflow-phase-index").querySelectorAll("button").forEach((button) => button.setAttribute("aria-current", button.dataset.phaseJump === activePhase ? "true" : "false"));
    if (!steps.length) $("workflow-nodes").innerHTML = '<p class="workflow-empty">没有匹配步骤。请清除筛选或更换关键词。</p>';
    resetView(false);
  }

  function detailSection(title, items) {
    if (!items || !items.length) return "";
    return '<section class="workflow-detail-section"><h3>' + esc(title) + "</h3>" + listHtml(items) + "</section>";
  }

  function renderDetail(step) {
    if (!step) return;
    const phase = data.phases.find((item) => item.id === step.phase) || {};
    const state = statusInfo(step.status);
    const model = modelInfo(step.route, step.model);
    const command = step.command ? '<details class="workflow-detail-section"><summary>查看代码入口</summary><code>' + esc(step.command) + "</code></details>" : "";
    $("workflow-detail-content").innerHTML =
      '<div class="workflow-detail-header"><p>' + esc(readable(phase.name || step.phase)) + " · " + esc(step.id) + '</p><h2 id="workflow-detail-title">' + esc(readable(step.name)) + '</h2><p class="workflow-detail-summary">' + esc(readable(step.summary)) + "</p></div>" +
      '<dl class="workflow-detail-meta"><dt>负责环节</dt><dd>' + esc(actorName(step.actor)) + "</dd><dt>处理方式</dt><dd>" + esc(model.name) + "<br>" + esc(modelLabel(model)) + "</dd><dt>当前状态</dt><dd>" + esc(statusName(step.status)) + "：" + esc(readable(state.description)) + "</dd></dl>" +
      detailSection("输入", step.inputs) + detailSection("处理", step.actions) + detailSection("输出", step.outputs) +
      detailSection("必须通过", step.checks) + detailSection("失败去向", step.onFailure) + detailSection("网站只展示", step.website) + command;
    $("workflow-detail").classList.remove("closed");
    $("workflow-nodes").querySelectorAll(".workflow-node").forEach((node) => node.setAttribute("aria-pressed", node.dataset.stepId === step.id ? "true" : "false"));
    $("workflow-connectors").querySelectorAll("path").forEach((path) => path.classList.toggle("selected", path.dataset.from === step.id || path.dataset.to === step.id));
  }

  function selectStep(id, revealDetail) {
    const step = data.steps.find((item) => item.id === id);
    if (!step) return;
    const update = () => {
      selectedId = id;
      renderDetail(step);
    };
    if (document.startViewTransition && !matchMedia("(prefers-reduced-motion: reduce)").matches) document.startViewTransition(update);
    else update();
    if (revealDetail && innerWidth <= 620) $("workflow-detail").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function setTransform(transform, animate) {
    if (!zoomBehavior || innerWidth <= 620) return;
    const selection = d3.select($("workflow-canvas"));
    if (animate && !matchMedia("(prefers-reduced-motion: reduce)").matches) selection.transition().duration(220).call(zoomBehavior.transform, transform);
    else selection.call(zoomBehavior.transform, transform);
  }

  function resetView(animate = true) {
    activePhase = "";
    $("workflow-phase-index")?.querySelectorAll("button").forEach((button) => button.setAttribute("aria-current", "false"));
    setTransform(d3.zoomIdentity.translate(28, 12).scale(1), animate);
  }

  function jumpToPhase(phaseId) {
    const phase = layout.phases.find((item) => item.id === phaseId);
    if (!phase) return;
    const first = data.steps.find((step) => step.phase === phaseId && layout.nodes.has(step.id));
    if (!first) return;
    activePhase = phaseId;
    $("workflow-phase-index").querySelectorAll("button").forEach((button) => button.setAttribute("aria-current", button.dataset.phaseJump === phaseId ? "true" : "false"));
    const point = layout.nodes.get(first.id);
    const scale = Math.max(0.8, currentTransform?.k || 1);
    setTransform(d3.zoomIdentity.translate(28 - point.x * scale, 12).scale(scale), true);
    selectStep(first.id, false);
  }

  function fitView() {
    if (innerWidth <= 620) return;
    const canvas = $("workflow-canvas");
    const scale = Math.max(.06, Math.min(1, (canvas.clientWidth - 72) / layout.width, (canvas.clientHeight - 72) / layout.height));
    const x = Math.max(24, (canvas.clientWidth - layout.width * scale) / 2);
    const y = Math.max(24, (canvas.clientHeight - layout.height * scale) / 2);
    setTransform(d3.zoomIdentity.translate(x, y).scale(scale), true);
  }

  function renderSupportContent() {
    $("workflow-phase-filter").insertAdjacentHTML("beforeend", data.phases.map((phase) => '<option value="' + esc(phase.id) + '">' + esc(readable(phase.name)) + "</option>").join(""));
    $("workflow-status-filter").insertAdjacentHTML("beforeend", data.statusLegend.filter((item) => data.steps.some((step) => step.status === item.id)).map((item) => '<option value="' + esc(item.id) + '">' + esc(statusName(item.id)) + "</option>").join(""));
    $("workflow-phase-index").innerHTML = data.phases.map((phase) => {
      const count = data.steps.filter((step) => step.phase === phase.id).length;
      return '<button type="button" data-phase-jump="' + esc(phase.id) + '">' + esc(readable(phase.name)) + "<span>" + count + "</span></button>";
    }).join("");
    $("workflow-legend").innerHTML = data.statusLegend.filter((item) => data.steps.some((step) => step.status === item.id)).map((item) => '<span class="' + statusClass(item.id) + '"><i aria-hidden="true"></i>' + esc(statusName(item.id)) + "</span>").join("");
    $("workflow-principle-list").innerHTML = (data.principles || []).map((item) => '<div class="workflow-principle"><strong>' + esc(readable(item.name)) + "</strong><span>" + esc(readable(item.description)) + "</span></div>").join("");
    $("workflow-invariants").innerHTML = (data.invariants || []).map((item) => "<li>" + esc(readable(typeof item === "string" ? item : item.description || item.name)) + "</li>").join("");
    $("workflow-route-list").innerHTML = data.modelRoutes.map((route) => {
      const publicRoute = modelInfo(route.id, route.model);
      return '<article class="workflow-route"><h3>' + esc(publicRoute.name) + "</h3><p><code>" + esc(route.model) + "</code> · 推理强度：" + esc(effortName(route.reasoning_effort)) + "</p><p>" + esc(readable(route.purpose)) + "</p></article>";
    }).join("");
  }

  function bindZoom() {
    if (!window.d3) throw new Error("工作流缩放组件未载入");
    const canvas = $("workflow-canvas");
    zoomBehavior = d3.zoom()
      .scaleExtent([.06, 1.5])
      .filter((event) => {
        if (event.type === "wheel") return true;
        return !event.target.closest(".workflow-node,.workflow-detail,.workflow-zoom");
      })
      .on("start", () => canvas.classList.add("dragging"))
      .on("zoom", (event) => {
        currentTransform = event.transform;
        $("workflow-stage").style.transform = "translate(" + currentTransform.x + "px," + currentTransform.y + "px) scale(" + currentTransform.k + ")";
        $("workflow-zoom-level").value = Math.round(currentTransform.k * 100) + "%";
        $("workflow-zoom-level").textContent = Math.round(currentTransform.k * 100) + "%";
      })
      .on("end", () => canvas.classList.remove("dragging"));
    d3.select(canvas).call(zoomBehavior).on("dblclick.zoom", null);
  }

  function bindEvents() {
    $("workflow-nodes").addEventListener("click", (event) => {
      const node = event.target.closest("[data-step-id]");
      if (node) selectStep(node.dataset.stepId, true);
    });
    $("workflow-query").addEventListener("input", (event) => { filters.query = event.target.value; renderGraph(); });
    $("workflow-phase-filter").addEventListener("change", (event) => { filters.phase = event.target.value; activePhase = event.target.value === "all" ? "" : event.target.value; renderGraph(); });
    $("workflow-status-filter").addEventListener("change", (event) => { filters.status = event.target.value; renderGraph(); });
    $("workflow-reset").addEventListener("click", () => {
      filters.query = ""; filters.phase = "all"; filters.status = "all";
      activePhase = "";
      $("workflow-query").value = ""; $("workflow-phase-filter").value = "all"; $("workflow-status-filter").value = "all";
      renderGraph();
    });
    $("workflow-phase-index").addEventListener("click", (event) => {
      const button = event.target.closest("[data-phase-jump]");
      if (!button) return;
      jumpToPhase(button.dataset.phaseJump);
    });
    $("workflow-zoom-out").addEventListener("click", () => d3.select($("workflow-canvas")).transition().duration(160).call(zoomBehavior.scaleBy, .84));
    $("workflow-zoom-in").addEventListener("click", () => d3.select($("workflow-canvas")).transition().duration(160).call(zoomBehavior.scaleBy, 1.19));
    $("workflow-fit").addEventListener("click", fitView);
    $("workflow-reset-view").addEventListener("click", () => resetView(true));
    $("workflow-detail-close").addEventListener("click", () => $("workflow-detail").classList.add("closed"));
    $("workflow-present").addEventListener("click", () => {
      const enabled = document.body.classList.toggle("focus-view");
      $("workflow-present").setAttribute("aria-pressed", String(enabled));
      $("workflow-present").textContent = enabled ? "退出专注" : "专注画布";
      requestAnimationFrame(() => {
        const step = data.steps.find((item) => item.id === selectedId);
        if (step && layout.nodes.has(step.id)) jumpToPhase(step.phase);
        else resetView(false);
      });
    });
    $("workflow-canvas").addEventListener("keydown", (event) => {
      if (innerWidth <= 620 || !currentTransform) return;
      const delta = event.shiftKey ? 100 : 40;
      const moves = { ArrowLeft: [delta, 0], ArrowRight: [-delta, 0], ArrowUp: [0, delta], ArrowDown: [0, -delta] };
      if (!moves[event.key]) return;
      event.preventDefault();
      setTransform(currentTransform.translate(moves[event.key][0] / currentTransform.k, moves[event.key][1] / currentTransform.k), false);
    });
    document.addEventListener("keydown", (event) => {
      if (event.key !== "Escape" || !document.body.classList.contains("focus-view")) return;
      document.body.classList.remove("focus-view");
      $("workflow-present").setAttribute("aria-pressed", "false");
      $("workflow-present").textContent = "专注画布";
      requestAnimationFrame(() => {
        const step = data.steps.find((item) => item.id === selectedId);
        if (step && layout.nodes.has(step.id)) jumpToPhase(step.phase);
        else resetView(false);
      });
    });
  }

  async function init() {
    // The workflow has its own approved configuration; the 1 MB asset index
    // is unrelated to drawing the canvas and may finish in the background.
    const embedded = document.getElementById("workflow-embedded-data");
    if (embedded) {
      data = JSON.parse(embedded.textContent);
    } else {
      const response = await fetch("workflow-data.json");
      if (!response.ok) throw new Error("工作流载入失败 HTTP " + response.status);
      data = await response.json();
    }
    if (!Array.isArray(data.phases) || !Array.isArray(data.steps) || !Array.isArray(data.modelRoutes)) throw new Error("工作流数据结构不完整");
    $("workflow-phase-count").textContent = data.phases.length.toLocaleString("zh-CN");
    $("workflow-step-count").textContent = data.steps.length.toLocaleString("zh-CN");
    $("workflow-model-count").textContent = data.modelRoutes.length.toLocaleString("zh-CN");
    selectedId = data.steps[0]?.id || "";
    renderSupportContent();
    bindZoom();
    bindEvents();
    renderGraph();
    renderDetail(data.steps[0]);
  }

  init().catch((error) => {
    $("workflow-result-note").textContent = error.message;
    $("workflow-nodes").innerHTML = '<p class="workflow-empty" role="alert">' + esc(error.message) + "。请重新载入。</p>";
  });
})();
