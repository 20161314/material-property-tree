/* Presentation only. All figures come from the same validated release. */
(() => {
  const mount = () => {
    const release = window.DATASET_RELEASE;
    const page = document.body.dataset.view;
    if (!release || !['objects','materials','coverage'].includes(page)) return;
    const fmt = n => Number(n).toLocaleString('en');
    const header = document.querySelector('.app-header');
    const disclosure = (label, className = 'reading-disclosure') => {
      const d = document.createElement('details'); d.className = className;
      const summary = document.createElement('summary'); summary.textContent = label; d.append(summary);
      return d;
    };
    // A closed, separate snapshot cannot be mistaken for the data being browsed.
    const progress = document.querySelector('.progress-notice');
    const version = document.createElement('p'); version.className = 'release-context';
    version.innerHTML = '<span class="release-indicator" aria-hidden="true"></span><strong>当前网站版本</strong><span>' + release.date + ' · 材料树、列表与下载使用同一版本数据</span>';
    header.after(version);
    const stats = document.createElement('dl'); stats.className = 'release-overview'; stats.setAttribute('aria-label','当前网站的数据统计');
    const values = [
      ['网站物体数量',release.objects.total,'按数据集编号统计；跨数据集可能有重复模型'],
      ['部件记录数量',release.objects.components,'包含未拆分整件，不代表已拆出的全部零件'],
      ['材料种类',release.materials.total,'不含液体；包含具体牌号和配方'],
      ['物性数据组数',release.records.total,'完整 ' + fmt(release.records.complete) + ' · 缺项 ' + fmt(release.records.partial)]
    ];
    stats.innerHTML = values.map(([label,value,note]) => '<div><dt>'+label+'</dt><dd>'+fmt(value)+'</dd><small>'+note+'</small></div>').join('');
    version.after(stats);
    const recordScope = disclosure('数据构成与统计说明');
    const m=release.records.main, db=release.records.database;
    recordScope.innerHTML += '<div class="record-scope"><div><h2>论文与厂商资料</h2><p>完整 '+fmt(m.complete)+' 组 · 缺项 '+fmt(m.incomplete)+' 组</p></div><div><h2>玻璃数据库资料</h2><p>完整 '+fmt(db.complete)+' 组 · 缺项 '+fmt(db.incomplete)+' 组</p><p>这些数值来自玻璃数据库，原论文尚未逐篇重新核查。</p></div></div><p>同一组资料同时给出 E、ν、ρ，记为“三项齐全”；只有一项或两项，记为“缺项数据”。一种材料的三项数值可以分别来自不同资料，但不拼成一组三项齐全的数据。</p><p>来源条目按文档或数据库中的引用编号统计，不等于已逐篇核查的论文数。</p>';
    stats.after(recordScope);
    const options=document.createElement('div'); options.className='release-options'; stats.after(options);options.append(recordScope);
    if (progress) {
      const work = disclosure('尚未上线的工作进度 · 2026-11-18', 'working-snapshot');
      options.append(work); work.append(progress);work.id='working-progress';
      const sync=document.createElement('p');sync.className='sync-status';sync.innerHTML='<strong>最新工作表：'+fmt(Number(progress.dataset.workingObjects))+' 个物体</strong><span>尚未全部上线，下方仍为网站当前版本。</span><a href="#working-progress">查看工作进度</a>';version.before(sync);sync.querySelector('a').addEventListener('click',()=>{work.open=true;});
      const progressHeading=progress.querySelector('.progress-notice-heading');if(progressHeading)progressHeading.hidden=true;
      progress.querySelector('.progress-notice-boundary').textContent = '这里是已核查、尚未上线的工作进度。下方材料树、列表和下载仍使用网站当前版本。';
    }
    // Retain every app-owned ID for updates, without repeating the global totals.
    const oldStats = document.querySelector(page==='objects' ? '.scaling-metrics' : page==='materials' ? '.header-data' : '.phase1-header-stats');
    if (oldStats) {
      const d=disclosure('详细统计与统计方法'); recordScope.append(d); d.append(oldStats);
    }
    document.querySelectorAll('.edition,.scaling-kicker').forEach(el=>el.hidden=true);
    const extra=document.querySelector('.site-auxiliary'); if(extra) recordScope.append(extra);
    const materialScope=document.querySelector('#material-coverage-scope'); if(materialScope) recordScope.append(materialScope);
    const priority=document.querySelector('.object-priority-coverage');
    if(priority){
      const c=release.object_priority_coverage.objectMaterials;
      const explain=disclosure('统计范围与未完成事项');
      while(priority.firstChild)explain.append(priority.firstChild);
      const line=document.createElement('div');line.className='priority-summary';
      line.innerHTML='<div><strong>物体材料覆盖率</strong><span>'+fmt(c.materialsWithAllThreeFromAnyGroup)+' / '+fmt(c.targetCount)+' · '+c.coveragePercent.toFixed(2)+'%</span></div><p>已对应到物体的材料中，E、ν、ρ 各有来源数值的比例。</p><a href="references.html?scope=object">查看缺少哪些数值</a>';
      priority.append(line,explain);
      // The compact line already contains the coverage count; keep limitations, not a second headline.
      const original=explain.querySelector(':scope > div:first-of-type');
      if(original){const boundary=original.querySelector('small');if(boundary)original.replaceChildren(boundary);else original.remove();}
      const action=explain.querySelector(':scope > div');
      if(action)action.querySelectorAll(':scope > a').forEach(a=>a.remove());
    }
    if(page==='objects'){
      const main=document.querySelector('.scaling-main');
      const downloads=disclosure('下载、统计说明与历史记录'); downloads.classList.add('overview-downloads');
      const oldNotes=[...main.children].filter(el=>el.matches('p:not([role="status"]),.overview-disclosure'));
      oldNotes.forEach(el=>downloads.append(el));
      const list=document.querySelector('[aria-labelledby="new-source-heading"]'); list.before(downloads);
      const history=list.querySelector('.scaling-history'); if(history)downloads.append(history);
      const heading=document.querySelector('#new-source-heading'); heading.closest('.scaling-section-heading').querySelector('.scaling-note').textContent='查看每个物体的部件、材料和 3D 资产。这里展示后续新增的物体，不是网站收录的全部物体。';
      // Source-specific subsets remain accessible, with no second expanded object list.
      for(const [selector,label] of [
        ['[aria-labelledby="gso-heading"]','Google Scanned Objects · 单独查看'],
        ['[aria-labelledby="parts-heading"]','已识别的部件 · 单独检索'],
        ['#counting-rules','扩充与审核规则'],
        ['[aria-labelledby="physxnet-source-parts-heading"]','PhysXNet · 部件附表']
      ]){
        const section=document.querySelector(selector); if(!section)continue;
        const d=disclosure(label,'source-disclosure'); section.before(d);d.append(section);
      }
    }
    if(page==='coverage'){
      if(priority){recordScope.append(priority);priority.querySelector('.priority-summary')?.remove();}
      const reading=document.querySelector('.coverage-reading');if(reading)recordScope.append(reading);
      const scopeNote=document.querySelector('#coverage-scope-note');if(scopeNote)recordScope.append(scopeNote);
      // These figures change with the selected material cohort, unlike the global overview.
      const metrics=document.querySelector('.phase1-metrics');
      const more=disclosure('查看三项属性各自的覆盖情况'); more.classList.add('coverage-breakdown');
      const keep=new Set(['stat-covered','stat-all-properties']);
      for(const item of [...metrics.children])if(![...keep].some(id=>item.querySelector('#'+id)))more.append(item);
      const previous=document.querySelector('.site-coverage-extra');
      if(previous){const grid=previous.querySelector('.phase1-metrics');if(grid)more.append(...grid.children);previous.remove();}
      metrics.after(more);
      const tableSection=document.querySelector('.phase1-table-section');const tableHeading=tableSection.querySelector('.phase1-table-heading');tableHeading.after(metrics);metrics.after(more);
      metrics.setAttribute('aria-label','当前筛选范围的材料覆盖');
      document.querySelectorAll('.phase1-footer p').forEach(p=>{if(p.textContent.includes('audit/'))p.hidden=true;});
      const headerStats=document.querySelector('.phase1-header-stats');
      headerStats.querySelectorAll('div>span').forEach((s,i)=>s.textContent=['全库三项齐全的数据','全库缺项数据','全库数据组合计'][i]);
    }
    const reset=(section,searchId,filterId)=>{
      const target=document.querySelector(section), input=document.getElementById(searchId), filter=document.getElementById(filterId);
      if(!target || !input || target.querySelector('.reset-filters'))return;
      const b=document.createElement('button');b.type='button';b.className='reset-filters';b.textContent='清空筛选';
      b.addEventListener('click',()=>{input.value=''; if(filter){filter.value='all';filter.dispatchEvent(new Event('change'));} input.dispatchEvent(new Event('input'));input.focus();});
      target.append(b);
    };
    reset('.scaling-asset-controls','new-source-search','new-source-filter');
    document.querySelectorAll('.scaling-asset-table table,.phase1-table-wrap table').forEach(table=>{
      const caption=document.createElement('caption');caption.className='sr-only';caption.textContent=table.id==='material-table'?'当前筛选材料、物性范围与来源':'物体、组件材料与来源资产';table.prepend(caption);
    });
  };
  if(document.readyState!=='complete')document.addEventListener('DOMContentLoaded',mount,{once:true});else mount();
})();
