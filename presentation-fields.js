/* Public projection only: never changes the evidence or its approval state. */
(function (root) {
  'use strict';
  const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const present = value => value !== '' && value !== null && value !== undefined;
  function safeUrl(value) {
    try { const u = new URL(String(value || '')); return /^https?:$/.test(u.protocol) && !u.username && !u.password ? u.href : ''; } catch { return ''; }
  }
  function text(value) {
    if (!present(value)) return '';
    return String(value)
      .replace(/(?:file:\/\/)?\/(?:Users|home|private|tmp|var|Volumes|mnt)\/[^\s<>"'，；]+/g, '')
      .replace(/\b[A-Za-z]:\\[^\s<>"']+/g, '')
      .replace(/\b[a-f\d]{64}\b/gi, '')
      .replace(/\b(?:MATERIAL-MAP|LOCAL-SCOPE|NPPR-REL)-[A-F\d]+\b/gi, '')
      .replace(/(^|[\s("'])(?:audit|rsi_harness|config)\/[^\s<>"'，；]+/g, '$1')
      .replace(/\b(?:ROOT|INDEPENDENT|APPROVED|INSTALLED|PENDING|HOLD|REJECT|PASS|NO_NUMERICAL|NO_E_NU_RHO|PLAUSIBLE_LOCAL|SOURCE_ENUMERATED|USER_AUTHORIZED)_[A-Z0-9_]+\b/g, '')
      .trim();
  }
  const link = (url, label) => { const href = safeUrl(url); return href ? `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer">${esc(label || '打开来源')}</a>` : ''; };
  const pair = (label, value) => present(value) ? `<div><dt>${esc(label)}</dt><dd>${esc(text(value))}</dd></div>` : '';
  const parse = value => { if (value && typeof value === 'object') return value; try { return JSON.parse(value || '{}'); } catch { return {}; } };
  const approvedReviews = new Set([
    'INDEPENDENT_SOURCE_ID_PART_OPTION_REVIEWED_NOT_PRODUCT_BOM',
    'INDEPENDENT_SHADOW_PACKET_REVIEWED', 'INDEPENDENT_REVIEW_PASS_SCOPED_APPROXIMATE',
    'INDEPENDENT_REVIEWED_SOURCE_IDENTITY_AND_SCOPED_MATERIAL_OPTION', 'ROOT_APPROVED',
    'INDEPENDENTLY_REVIEWED_O71_REBASED_APPROXIMATION', 'REVIEWED_SOURCE_LABEL_BROAD_MAPPING',
    'PASS_INDEPENDENT_SOURCE_IDENTITY_REVIEW_WITH_METADATA_CORRECTIONS',
    'REVIEWED_INDEPENDENT_RESTRICTED_NONEXCLUSIVE_C29', 'REVIEWED_PLAUSIBLE_APPROXIMATE',
    'INDEPENDENT_SOURCE_REVIEW_PASS_PARTIAL_LOCAL_SCOPE', 'INDEPENDENT_SOURCE_IDENTITY_REVIEWED_LINK_ONLY',
    'PASS_INDEPENDENT_C31_PARTIAL_WOOD_BODY_ONLY'
  ]);
  const approvedIndependent = new Set([
    'APPROVED', 'APPROVED_SOURCE_IDENTITY_AND_BOUNDED_MATERIAL_OPTIONS',
    'PASS_INDEPENDENT_SCOPED_APPROXIMATION', 'PASS_INDEPENDENT_C27_SCOPED_LABEL_LINK_NO_PROPERTY_ASSIGNMENT',
    'APPROVED_SOURCE_IDENTITY_AND_SCOPED_PLAUSIBLE_MATERIAL_ONLY', 'PASS_LINK_ONLY_NO_NUMERICAL_ASSIGNMENT',
    'APPROVE_SOURCE_DECLARED_PARTIAL_LOCAL_MATERIAL_SCOPE', 'PASS_SOURCE_PRODUCT_CLASS_WOOD_BODY_NONEXCLUSIVE'
  ]);
  function accepted(row, component = {}) {
    if (['source','native_source_view'].includes(row.stream)) {
      const sourceApproval = new Set(['REVIEWED_SOURCE_SCOPE_NOT_NUMERICAL_ASSIGNMENT','ORIGINAL_REVIEWED_COARSE_NODE_PRESERVED_NO_PROPERTY_ASSIGNMENT']);
      const states = [row.canonical_mapping_status,row.mapping_status,row.review_status,row.independent_review_status,component.admission_status,component.material_release_status,component.material_identity_status];
      return sourceApproval.has(row.canonical_mapping_status) && !/(?:PENDING|REJECT|HOLD|QUARANTINED|UNREVIEWED)/.test(states.join(' '));
    }
    if (!['links', 'working_links'].includes(row.stream)) return false;
    // Approval fields, not a substring such as REVIEWED in a pending mapping code, decide admission.
    if ([row.review_status, row.independent_review_status].some(v => /(?:PENDING|REJECT|HOLD|UNREVIEWED)/.test(v || ''))) return false;
    const legacyLocal = row.mapping_status === 'REVIEWED_PLAUSIBLE_LOCAL_OPTION_FROM_OFFICIAL_CONFIGURATION' && new Set(['PASS_OFFICIAL_BOUND_NONVISUAL_LABELS_USER_AUTHORIZED_LABEL_STANDARD','PASS_MATERIAL_IDENTITY_MAPPING','INDEPENDENT_REVIEW_PASS_SOURCE_AUTHORED_ENTITY']).has(component.admission_status);
    return approvedReviews.has(row.review_status) || approvedIndependent.has(row.independent_review_status) || legacyLocal;
  }
  function componentName(row) {
    const originalName = value => /[\u3400-\u9fff]/.test(value) ? text(value) : text(value) + '（原文）';
    for (const key of ['component_name_cn','component_name_zh','component_name','nameCn','part_name_cn']) if (row[key]) return originalName(row[key]);
    const scope = row.component_scope || row.material_scope || row.scope || '';
    const chinese = [...scope.matchAll(/[（(]([^（）()]*[\u3400-\u9fff][^（）()]*)[）)]/g)].map(m => m[1]);
    if (chinese.length) return text(chinese[0]);
    if (/(?:WHOLE|UNRESOLVED)(?:-|$)|whole[-_ ](?:object|asset|geometry)|整件/i.test(row.component_id || scope)) return '整件（未拆分）';
    if (/SOURCE_SEMANTIC_CLASS:/.test(row.component_path || '')) return originalName(row.component_path.split(':').slice(1).join(':'));
    const semantic = row.semantic_part_key || scope.match(/(?:semantic part class|physical component:|source-authored component:)\s*([^;(]+)/i)?.[1];
    if (semantic) return originalName(semantic);
    // Preserve the source's professional part name when it has no supplied Chinese name.
    const sourceName = row.component_path && !/^(?:WHOLE|UNRESOLVED|SOURCE_)/.test(row.component_path) ? row.component_path : '';
    const namedPart = /-SEM-|-RootNode__/.test(row.component_id || '') ? row.component_id.split(/-SEM-|-RootNode__/).pop().replace(/__/g, ' / ') : '';
    return sourceName || namedPart ? originalName(sourceName || namedPart) : '部件（来源未提供名称）';
  }
  function nature(row) {
    const mode = row.relation_mode || row.label_relationship || '';
    const basis = [row.adapter_basis_class, row.mapping_status, row.relation_type].join(' ');
    const tags = [];
    if (/STYLE|NATIVE_MATERIAL_OPTION/.test(mode+' '+basis)) tags.push('数据集材质选项');
    else if (row.relation_type === 'SOURCE_AUTHOR_ALLOWED_SEMANTIC_MATERIAL_OPTION') tags.push('来源标注');
    else if (/APPROXIMATE|APPROXIMATION|PLAUSIB|USER_AUTHORIZED/.test(basis)) tags.push('合理推定');
    else tags.push('来源标注');
    const alternativeModes = new Set(['ALTERNATIVE_NOT_SIMULTANEOUS','ALTERNATIVES','PLAUSIBLE_ALTERNATIVE_NOT_SIMULTANEOUS','MUTUALLY_EXCLUSIVE_ALTERNATIVES','MUTUALLY_EXCLUSIVE_OPTIONS']);
    if (/NONEXCLUSIVE|NOT_ALTERNATIVE/.test(mode)) tags.push(/LOCAL|PARTIAL|COMPONENT_SCOPE/.test(mode) ? '局部材料' : '共存材料范围');
    else if (alternativeModes.has(mode)) tags.push('互斥可选材料');
    else if (/LOCAL|PARTIAL/.test(mode) || /LOCAL/.test(row.adapter_scope_kind || '') || /LOCAL/.test(row.mapping_status || '')) tags.push('局部材料');
    else if (/COEXIST|CO_PRESENT|SIMULTANEOUS_MATERIAL|MULTIPLE_CONSTITUENTS/.test(mode)) tags.push('共存材料范围');
    else if (/SOURCE_AUTHOR_ALLOWED_SEMANTIC_MATERIAL_OPTION/.test(row.relation_type || '') || /SOURCE_AUTHOR_ALLOWED/.test(mode)) tags.push('可选材料');
    return tags.join(' · ');
  }
  function shortBasis(row) {
    const rationale = row.source_quote_kind === 'REVIEWER_RATIONALE_NOT_VERBATIM_SOURCE' ? row.source_quote : '';
    if (rationale && /[\u3400-\u9fff]/.test(rationale)) return text(rationale);
    const kind = nature(row);
    if (kind.includes('数据集材质选项')) return '数据集提供的材质或风格选项，不表示实物同时具有这些成分。';
    if (kind.includes('合理推定')) return kind.includes('局部') ? '依据来源物体类别与用途，保留局部可能使用的宽类材料；不代表整件组成。' : '依据来源物体类别、用途或说明保留合理的宽类材料选项。';
    if (kind.includes('可选')) return '来源为该部件列出的可选材料，不表示同时组成。';
    return '按来源记录保留该部件或材料区域的标签。';
  }
  function objectPresentation(object) {
    const materials = new Map([...(object.materials || []), ...(object.reviewedMaterials || [])]);
    const sourceRows = new Map();
    for (const row of object.relations || []) if (row.stream === 'source' || row.stream === 'native_source_view') {
      const key = row.relation_id + '\t' + row.component_id;
      sourceRows.set(key, row);
    }
    const result = [], seen = new Set();
    const vetoed = new Set((object.relations || []).filter(row => /(?:PENDING|REJECT|HOLD|QUARANTINED|UNREVIEWED)/.test([row.review_status,row.independent_review_status].join(' ')) || /ALL_RELATIONS_QUARANTINED/.test(row.canonical_mapping_status || '')).map(row => row.relation_id + '\t' + row.component_id));
    const linked = new Set((object.relations || []).filter(row => ['links','working_links'].includes(row.stream) && accepted(row, (object.components || []).find(c => c.component_id === row.component_id) || {})).map(row => row.relation_id + '\t' + row.component_id));
    for (const row of object.relations || []) {
      const originalComponent = (object.components || []).find(c => c.component_id === row.component_id) || {};
      if (vetoed.has(row.relation_id + '\t' + row.component_id) || !accepted(row, originalComponent)) continue;
      if (['source','native_source_view'].includes(row.stream) && linked.has(row.relation_id + '\t' + row.component_id)) continue;
      const source = sourceRows.get(row.relation_id + '\t' + row.component_id) || {};
      const merged = {...source, ...row};
      for (const key of ['source_url','source_label_cn','source_label_raw','component_scope','source_quote','source_locator','relation_type']) if (!merged[key]) merged[key] = source[key];
      const id = row.target_material_id || row.canonical_material_id || source.canonical_material_id;
      if (!id) continue;
      // Same source/link relation is shown once; different components or scopes remain distinct.
      const key = [row.relation_id, row.component_id, id, row.relation_mode || row.label_relationship, row.material_scope || row.component_scope].join('\t');
      if (seen.has(key)) continue;
      seen.add(key);
      const working = parse(row.working_relation_json);
      merged.materialId = id;
      merged.materialName = merged.source_label_cn || working.material_label_cn || materials.get(id) || merged.source_label_raw || '未提供';
      const component = (object.components || []).find(c => c.component_id === row.component_id) || row;
      merged.componentName = componentName(component);
      result.push(merged);
    }
    const components = [], componentKeys = new Set();
    for (const row of object.components || []) {
      if (componentKeys.has(row.component_id)) continue;
      componentKeys.add(row.component_id);
      components.push({row, name:componentName(row), relations:result.filter(r => r.component_id === row.component_id)});
    }
    for (const relation of result) if (!componentKeys.has(relation.component_id)) {
      componentKeys.add(relation.component_id); components.push({row:relation, name:relation.componentName, relations:result.filter(r => r.component_id === relation.component_id)});
    }
    return {relations:result, components, materials:[...new Map(result.map(r => [r.materialId,[r.materialId,r.materialName]])).values()]};
  }
  function relationHtml(row) {
    const href = `research.html?node=${encodeURIComponent(row.materialId)}`;
    return `<section class="source-raw"><p class="object-material-links"><a href="${href}">${esc(text(row.materialName))}</a> <span>${esc(nature(row))}</span></p><p>${esc(shortBasis(row))}</p>${row.source_quote && row.source_quote_kind !== 'REVIEWER_RATIONALE_NOT_VERBATIM_SOURCE' ? `<details><summary>来源原文</summary><p>${esc(text(row.source_quote))}</p></details>` : ''}${row.material_scope || row.component_scope ? `<details><summary>适用范围${/[\u3400-\u9fff]/.test(row.material_scope || row.component_scope) ? '' : '（原文）'}</summary><p>${esc(text(row.material_scope || row.component_scope))}</p></details>` : ''}${link(row.source_url,'打开材料来源')}</section>`;
  }
  const evidenceFields = [
    ['source_title','原文标题'],['publisher','发布主体'],['publisher_subject_name','发布主体'],['grade','材料/牌号'],['materialScope','材料范围'],['scope_notes','形态范围'],
    ['environment','温度与环境'],['conditions','条件'],['orientation','方向与原值分组'],['directional_values_json','方向与原值分组'],
    ['propertyModel','数值来源形式'],['property_model','数值来源形式'],['propertyValueOrigin','数值来源性质'],['evidence_role','证据用途'],
    ['sameSpecimen','试样关系'],['sourceValueExcerpt','来源原值摘录'],['sourceUncertaintyNotes','不确定度'],['source_uncertainty_notes','不确定度'],
    ['unitConversionNotes','单位换算'],['sourceStatistic','统计量'],['sourceDeformationRange','应变区间'],
    ['EStandardDeviationOriginal','E 标准差（原单位）'],['ELowerIQR','E 下四分位距（原文）'],['EUpperIQR','E 上四分位距（原文）'],
    ['rhoStandardDeviationOriginal','密度标准差（原单位）'],['densitySourceDefinition','密度原文定义'],['ancillaryValues','辅助原值'],
    ['densityType','密度定义'],['density_type','密度定义'],['densityTypeValues','密度分项原值'],['density_type_values_json','密度分项原值'],
    ['same_specimen','试样关系'],['source_value_excerpt','来源原值摘录'],['unit_conversion_notes','单位换算'],['material_scope','材料范围'],['source_statistic','统计量'],
    ['ancillary_values_json','辅助原值'],['source_deformation_range','应变区间'],['modulus_type','模量定义'],['modulusType','模量定义'],['property_value_origin','数值来源性质'],
    ['density_source_definition','密度原文定义'],['E_standard_deviation_original','E 标准差（原单位）'],['rho_standard_deviation_original','密度标准差（原单位）'],
    ['E_lower_IQR_original','E 下四分位距（原文）'],['E_upper_IQR_original','E 上四分位距（原文）'],['conditions_or_group','条件与分组'],
    ['source_sample_group_definition','来源样品组定义'],['source_value_precision_notes','数值精度说明'],['unit_E_original','E 原文单位'],['unit_nu_original','ν 原文单位'],['unit_rho_original','ρ 原文单位'],
    ['E_source_locator','E 原文位置'],['nu_source_locator','ν 原文位置'],['rho_source_locator','ρ 原文位置'],['source_material_excerpt','材料原文摘录'],
    ['temperature_C','温度（°C）'],['cooling_group','冷却条件'],['measurement_definition','测量定义'],['property_definition','属性定义'],['source_formulation_json','来源配方'],
    ['measured_values_json','测量原值'],['source_observations_json','原始观测'],['specific_gravity_as_reported','来源报告的比重'],['specific_gravity_basis','比重依据'],['supplemental_moduli_json','辅助模量'],
    ['method','方法'],['method_or_basis','方法与依据'],['limitations','局限'],['locator','原文位置']
  ];
  const valueLabels = {not_asserted:'未说明同一试样',NOT_ASSERTED:'未说明同一试样',not_reported:'未提供',unknown:'未提供',EXPERIMENTAL:'实验测量',SOURCE_REPORTED:'来源报告',COMPILED:'资料汇编',NOT_REPORTED:'未提供',UNKNOWN:'未提供',YES:'是',NO:'否',bulk:'体密度',apparent:'表观密度',true:'真密度',skeletal:'骨架密度',E:'杨氏模量 E',nu:'泊松比 ν',rho:'密度 ρ',url:'来源链接',doi:'DOI',title:'原文标题',citation:'原引用',locator:'原文位置',source_url:'来源链接',source_citation:'原引用',value:'原值',unit:'单位',units:'单位',definition:'定义',density_type:'密度定义',source_value:'来源原值',E_parallel_GPa:'轴向 E∥（GPa）',E_perpendicular_GPa:'横向 E⊥（GPa）',strain_percent:'应变（%）',nu_31_32:'ν31/32',nu_12:'ν12',rho_assumed_kg_m3:'采用密度（kg/m³）'};
  Object.assign(valueLabels, {
    unit_original:'原文单位',origin:'来源性质',value_origin:'数值来源性质',values_original:'原文数值',underlying_citation:'原始引文',value_original:'原文数值',
    statistics:'统计量',test_parameter:'试验参数',standard:'标准',not_range_endpoints:'并非范围端点',source_printed_uncertainty:'原文不确定度',uncertainty_original:'原文不确定度',
    method_or_basis:'方法与依据',source_material:'来源材料',strain_range:'应变区间',median_MPa:'中位数（MPa）',lower_IQR_MPa:'下四分位距（MPa）',upper_IQR_MPa:'上四分位距（MPa）',
    uncertainty_definition:'不确定度定义',ref_id:'原文引文编号',method:'方法',printed_uncertainty_MPa:'原文不确定度（MPa）',observations:'观测',modulus_type:'模量定义',
    attribution:'归属',CV_pct:'变异系数（%）',height_mm:'高度（mm）',shape_factor:'形状因子',sample_quantity:'试样数量',CI95:'95% 置信区间',
    source_printed_SD:'原文标准差',SE_original:'原文标准误',sampling_location:'取样位置',mean_kg_m3:'均值（kg/m³）',printed_uncertainty_kg_m3:'原文不确定度（kg/m³）',
    supporting_locator:'补充原文位置',direction:'方向',mean:'均值',sd_original:'原文标准差',sd_unit:'标准差单位',source_label:'来源标签',uncertainty_status:'不确定度说明',
    original_citations:'原始引文',source_printed_standard_error:'原文标准误',underlying_lab_report:'原始实验报告',uncertainty_type:'不确定度类型',same_underlying_experiment:'同一原始实验',
    source:'来源',min_original:'原文最小值',max_original:'原文最大值',underlying_reference:'原始参考文献',original_citation:'原始引文',value_as_reported:'来源报告值',
    reference_as_reported:'来源原引用',link_text_as_reported:'来源链接原文',printed_uncertainty_original:'原文不确定度',supplier_name:'供应商',age_days:'龄期（天）',phi:'φ',probable_error_cells:'可能误差原文单元格',table_footnotes:'原表脚注',
    warp:'经向',weft:'纬向',grouping:'分组',source_ref:'原文参考文献',directions:'方向',test_standard:'试验标准',source_definition_warning:'来源定义说明',
    component:'分量',reference:'参考文献',extension_percent:'伸长率（%）',Median:'中位数',LIQR:'下四分位距',UIQR:'上四分位距',sheet_row:'原工作表行',source_name:'来源名称',
    source_sample_size:'来源样本量',aliases_with_same_stats:'同统计量的原名',source_row_text:'原文记录行',source_areal_mass_g_m2:'来源面密度（g/m²）',source_thickness_mm:'来源厚度（mm）',
    rho_not_reported:'未报告密度',no_volume_density_inferred:'未推算体密度',minimum_replicates:'最少重复数',radial:'径向',axial:'轴向',tangential:'切向',reported_uncertainty:'报告不确定度',
    source_table:'来源表格',dynamic_storage_modulus_excluded:'动态储能模量不纳入',vibration_mode:'振动模态',reported_pm_uncertainty:'报告的正负不确定度',
    loading_angle_relative_to_warp_deg:'相对经向加载角（°）',measured_transverse_direction:'测量横向',source_as_printed:'原文报告',step_or_strain_window:'阶段或应变区间',
    standard_deviation:'标准差',parallel_to_backbone:'平行主链',perpendicular_to_backbone:'垂直主链',parallel_to_pressing:'平行压制方向',perpendicular_to_pressing:'垂直压制方向',
    measuring_error:'测量误差',areal_mass_g_m2:'面密度（g/m²）',thickness_mm:'厚度（mm）',density_not_source_reported:'来源未报告密度',
    E_original_value:'E 原值',E_original_unit:'E 原单位',value_kind:'数值定义',replicates:'重复数',type:'定义类型',reported:'是否报告',meaning:'含义',
    material_density_kg_m3:'材料密度（kg/m³）',bulk_packing_density_kg_m3:'堆积密度（kg/m³）',admitted_range_basis:'范围依据'
  });
  function readableCode(value) {
    if (valueLabels[value]) return valueLabels[value];
    if (typeof value !== 'string') return value;
    // Scientific definitions remain readable; process/state codes are never public fields.
    if ((/^[A-Z][A-Z0-9_ /;.,|()∥⊥=-]+$/.test(value) || /^[a-z][a-z0-9_]+$/.test(value)) && value.includes('_')) return value.replace(/_/g, ' ').toLowerCase();
    return value;
  }
  function scientificValue(value) {
    let parsed = value;
    if (typeof value === 'string' && /^[\[{]/.test(value.trim())) {
      try { parsed = JSON.parse(value); }
      catch { return esc(text(value)); }
    }
    if (!parsed || typeof parsed !== 'object') return esc(text(readableCode(value)));
    if (Array.isArray(parsed)) return parsed.map(scientificValue).join('；');
    return Object.entries(parsed).filter(([key]) => !/local|(?:^|_)file$|hash|sha256|review|queue|install|verification|directly_reread|^(?:source|record|component|relation|document)_id$|document_key/i.test(key)).map(([key,v]) => `${esc(valueLabels[key] || ('原文字段（' + text(key) + '）'))}：${scientificValue(v)}`).join('；');
  }
  function evidenceMeta(row) {
    const seen = new Set(), values = new Set(), fields = [];
    for (const [key,label] of evidenceFields) {
      if (!present(row[key]) || seen.has(label)) continue;
      const value = scientificValue(row[key]);
      if (!value || values.has(value)) continue;
      seen.add(label); values.add(value);
      fields.push(`<div><dt>${esc(label)}</dt><dd>${value}</dd></div>`);
    }
    return fields.join('');
  }
  function citationsHtml(value) {
    if (!present(value)) return '';
    return `<details class="property-citations"><summary>各属性原引用</summary><p>${scientificValue(value)}</p></details>`;
  }
  const api={esc,text,present,safeUrl,link,pair,accepted,componentName,nature,shortBasis,objectPresentation,relationHtml,evidenceMeta,scientificValue,citationsHtml};
  root.PresentationFields=api;
  if (typeof module !== 'undefined') module.exports=api;
})(typeof window === 'undefined' ? globalThis : window);
