(() => {
  const release = window.DATASET_RELEASE;
  if (!release) return;
  const fmt = n => Number(n).toLocaleString('en');
  // Define validation synchronously, before any view application executes.
  window.verifyDatasetView = (kind, data) => {
    const id = kind === 'materials' ? data?.meta?.releaseId : kind === 'objects' ? data?.summary?.release_id : data?.releaseId;
    const countsMatch = kind === 'materials' ? data?.meta?.canonicalCoverage?.targetCount === release.materials.total && data.meta.completeRecordCount === release.records.complete && data.meta.incompleteRecordCount === release.records.partial
      : kind === 'objects' ? data?.summary?.object_identities === release.objects.total && data.summary.object_component_rows === release.objects.rows && data.summary.material_labels === release.materials.total
      : data?.canonicalSummary?.targetCount === release.materials.total && data?.summary?.reviewedRecords === release.records.total;
    if (id === release.id && countsMatch) return true;
    const showError = () => {
      if (document.querySelector('.release-mismatch')) return;
      const alert = document.createElement('p'); alert.className = 'release-mismatch'; alert.setAttribute('role', 'alert');
      alert.innerHTML = '页面数据与当前发布版本不一致。<button type="button">重新载入</button>';
      alert.querySelector('button').onclick = () => location.reload();
      document.body.prepend(alert);
    };
    if (document.body) showError(); else document.addEventListener('DOMContentLoaded', showError, {once:true});
    return false;
  };
  function mount() {
  const page = document.body.dataset.view;
  const priority = release.object_priority_coverage;
  if (priority && ['objects','materials','coverage'].includes(page)) {
    const c=priority.objectMaterials;
    const panel=document.createElement('section'); panel.className='object-priority-coverage';
    panel.setAttribute('aria-label','物体关联材料覆盖');
    panel.innerHTML='<div><span>当前优先 · 物体关联材料</span><strong>'+fmt(c.materialsWithAllThreeFromAnyGroup)+' / '+fmt(c.targetCount)+' 三项有来源值 · '+c.coveragePercent.toFixed(2)+'%</strong><small>仍缺项 '+fmt(c.missingMaterials)+' 种；含已接受标签与合理近似选项，非商品实测。</small></div><div><a href="references.html?scope=object">查看物体材料</a><a href="'+priority.downloads.report+'">缺项名单</a><details><summary>研究材料范围</summary><p>无物体且三项齐全 '+fmt(priority.unlinkedComplete.targetCount)+' 种保留；无物体且缺项 '+fmt(priority.researchCandidates.targetCount)+' 种单列候选。全部研究材料 '+fmt(priority.allResearch.targetCount)+' 种。分组不算新增证据。</p><a href="references.html?scope=canonical">全部研究材料</a> · <a href="references.html?scope=candidate">研究候选</a></details></div>';
    const header=document.querySelector('.app-header');
    if (header) header.after(panel);
    if (page==='materials') {
      const note=document.createElement('p');note.className='priority-tree-scope-note';
      note.textContent='下方材料树包含全部研究材料；上方进度仅统计当前物体关联材料。无物体缺项节点单列研究候选，不计入优先补齐分母。';
      panel.after(note);
    }
    const prior=document.querySelector('.coverage-progress');
    if (prior) prior.hidden=true;
  }
  const current = {objects:'scaling.html',materials:'research.html',coverage:'references.html'};
  const title = {objects:'物体与材料总览',materials:'材料物性来源树',coverage:'材料标签与三元组来源对照',archive:'历史映射',references:'历史对照',catalog:'玻璃数据'};
  const shell = document.createElement('nav'); shell.className='site-navigation'; shell.setAttribute('aria-label','数据库导航');
  shell.innerHTML='<a class="site-brand" href="scaling.html">物体与材料库</a><div class="site-main-links">'+Object.entries(current).map(([key,url])=>'<a href="'+url+'"'+(page===key?' aria-current="page"':'')+'>'+title[key]+'</a>').join('')+'</div><details class="site-more"><summary>数据与说明</summary><div><a href="evidence-catalog.html?collection=sciglass">玻璃数据</a><a href="scaling-assets/current-tables/README.md">下载数据</a><a href="release-manifest.json">发布清单</a></div></details><span class="site-version" title="各视图共享此发布快照">'+release.date+' · '+release.id+'</span>';
  const skip = document.querySelector('.skip-link');
  if (skip) skip.after(shell); else document.body.prepend(shell);
  document.querySelectorAll('.dataset-views,.scaling-nav,.phase1-nav,.catalog-nav,.target-nav,.research-view-link').forEach(element=>element.remove());
  const menu = shell.querySelector('details');
  document.addEventListener('keydown', event => { if (event.key === 'Escape') { menu.open = false; menu.querySelector('summary').focus(); } });
  document.addEventListener('click', event => { if (!menu.contains(event.target)) menu.open = false; });
  document.querySelectorAll('[data-release-stat]').forEach(element=>{
    const value=element.dataset.releaseStat.split('.').reduce((value,key)=>value?.[key],release);
    if(value!==undefined)element.textContent=typeof value==='number'?fmt(value):String(value);
  });
  if (page === 'objects') {
    for (const [selector,label] of [['.scaling-delta','本轮更新'],['.scaling-two-columns','来源对账与待办']]) {
      const content=document.querySelector(selector);
      if (content && !content.closest('.overview-disclosure')) {
        const disclosure=document.createElement('details');disclosure.className='overview-disclosure';
        const summary=document.createElement('summary');summary.textContent=label;disclosure.append(summary);
        content.before(disclosure);disclosure.append(content);
      }
    }
    const section = document.querySelector('[aria-labelledby="new-source-heading"]');
    if (section && !section.querySelector('.scaling-history')) {
      const notes = [...section.querySelectorAll(':scope > p.scaling-note')].filter(p => p.id !== 'new-source-status');
      const history = document.createElement('details'); history.className='scaling-history';
      history.innerHTML='<summary>查看历次扩充清单与审核记录</summary>';
      notes.forEach(note=>history.append(note));
      section.querySelector('.scaling-asset-table').before(history);
    }
  }
  if (page === 'coverage') {
    const policy = document.querySelector('.phase1-policy');
    if (policy && !document.querySelector('.coverage-reading')) {
      const disclosure = document.createElement('details'); disclosure.className='scaling-history coverage-reading';
      disclosure.innerHTML='<summary>数据口径与来源层级</summary>';
      policy.before(disclosure); disclosure.append(policy);
      const origins=document.querySelector('.phase1-coverage-line'); if(origins)disclosure.append(origins);
    }
  }
  // Keep secondary coverage figures available without displacing the material list.
  if (page === 'coverage') {
    const metrics = document.querySelector('.phase1-metrics');
    if (metrics && !document.querySelector('.site-coverage-extra')) {
      const items = [...metrics.children];
      const extra = document.createElement('details'); extra.className = 'scaling-history site-coverage-extra';
      const summary = document.createElement('summary'); summary.textContent = '查看各项属性覆盖与来源统计';
      const grid = document.createElement('div'); grid.className = 'phase1-metrics';
      items.filter((item,index) => [2,3,4,7].includes(index)).forEach(item => grid.append(item));
      extra.append(summary,grid); metrics.after(extra);
    }
    document.querySelectorAll('.phase1-table-heading .phase1-filters label > .sr-only').forEach(label => { label.classList.remove('sr-only'); label.classList.add('filter-label'); });
  }
  if (page === 'materials') {
    const search = document.querySelector('#tree-search');
    if (search && !document.querySelector('label[for="tree-search"]')) {
      const label = document.createElement('label'); label.htmlFor = 'tree-search'; label.className = 'field-label'; label.textContent = '搜索材料';
      search.parentElement.prepend(label);
    }
  }
  const stats = document.querySelector('body[data-view="materials"] .dataset-stats');
  if (stats && !document.querySelector('.site-auxiliary')) {
    const extra = document.createElement('details'); extra.className = 'site-auxiliary';
    extra.innerHTML = '<summary>更多统计与阅读说明</summary><dl></dl><p>完整组同一来源组含 E、ν、ρ；缺项组有 1 或 2 项。三项覆盖允许分别来自不同组，不拼接为完整三元组。已审细分材料可计入上级覆盖，不自动赋给商品。</p>';
    const items = [...stats.children]; items.slice(4).forEach(item => extra.querySelector('dl').append(item));
    const boundary = document.getElementById('scope-note-content');
    if (boundary) extra.querySelector('p').textContent = boundary.textContent;
    document.querySelector('.coverage-progress').after(extra);
  }
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount, {once:true}); else mount();
})();
