# O72 阶段验收 · 2026-11-17

本轮工作库已独立复核；此页只发布进度汇总。正式树、表格与原下载仍为 C41。

| 指标 | 最新已核工作库 O72 | 正式网站数据 C41 |
|---|---:|---:|
| 来源对象身份 | 101,269 | 54,281 |
| 对象—组件键（含整件） | 165,734 | 118,746 |
| 活跃非液体材料/配方节点 | 4,219 | 3,916 |
| 主账完整来源组 | 2,443 | 2,429 |
| 主账缺项来源组 | 3,614 | 3,062 |
| 关联材料三项各有来源值 | 218/266（81.95%） | 173/231（74.89%） |
| 关联材料仍缺至少一项 | 48 | 58 |

## 本轮完成

- 新增 1,169 条有界近似材料关系，涉及现有物体；未新增几何或机械部件。
- 新增 8 组缺项记录：6 组藤颗粒板密度、2 组藤条层合复合材料拉伸弹性模量。新增完整组为 0。
- 新增 9 个材料/配方节点：8 个文献定义配方/处理身份、1 个 EcoForms 谷物纤维成型复合材料粗类。
- EcoForms 39 个现有物体获得厂家家族说明支持的近似标签；没有据此生成物性或声称逐 SKU 成分实测。
- 四条物体标题与图示冲突仍保留待核；11 条无依据的飞机纤维板关系未准入。
- 旧行非空字段、来源和数值经过守恒检查；未把弯曲 MOE 自动转为 Young E，未复制上级物性给下级。

本轮数值来源：藤颗粒板密度见 [Polymers，10.3390/polym18091031](https://doi.org/10.3390/polym18091031)；藤条/环氧与玻纤混杂层合材料的拉伸弹性模量见 [Polymers，10.3390/polym14245562](https://doi.org/10.3390/polym14245562)。论文条件、材料构造和数值定义保存在工作库；此公告不把研究结果直接赋给商品。

## 仍需完成

- 物体关联材料中 48 种缺少 E、ν、ρ 的至少一项，见[逐材料缺项名单](MATERIAL_PROPERTY_GAPS.csv)。这表示当前未收录，不能断言文献不存在。
- 与 O71 的 218/265 相比，本轮加入缺物性的 EcoForms 材料后分母变为 266。原有覆盖未丢失；优先补齐新增及原有缺项。
- 正式全量发布仍受三个真实未完成项约束：全局几何内容去重、全部机械部件枚举、全部近似材料选项逐项核验。
- 原始审核口径另有 38,516 条材料映射义务；它是待办行数，包含原始未映射记录，不能解释为相同数量的缺材料物体，也不能与上述材料数相加。
- 下一批软材料的 7 条密度候选已核原文：6 条待材料身份、父边与注册处理；1 条只适合保留来源总体范围，暂不计单材料组。均未计入本轮。

## 数量如何理解

- 来源对象身份按来源 UID 与已审别名计数，尚未证明全部是内容唯一的几何。
- 对象—组件键包含 WHOLE 整件占位；它不是全部真实内部机械部件数量。
- 材料节点含粗类、细类与配方；9 个新增节点不代表 9 种独立化学材料。
- 完整组在同一来源组同时给出 E、ν、ρ；缺项组只给出一项或两项。跨论文可形成逐属性范围，不能拼成同源完整组。
- 全研究账另含 SciGlass 数据库转录：完整 6,200 组、缺项 95,465 组，共 101,665 组。数据库记录未逐篇人工重读原论文，记录数不等于独立文献数。
- 四类节点：三项齐且有关联物体 218；三项齐且无关联物体 1,507；缺项且有关联物体 48；缺项且无关联物体 2,446。

## 验收与后续

网站三个页面共享同一份 O72 进度快照；下方正式数据仍使用 C41，不混用分子、分母。正式发布门禁保持 BLOCKED；进度公告验收不代表全量数据已发布或总任务完成。

继续并行补充真实完整/缺项来源，优先现有物体关联材料与软材料；O73 候选复核后再独立入账。物体扩充继续依照材料树状态和 BFS 队列执行。

核验标识与 SHA 见[统计 JSON](working-progress.json)。

## 当前关联材料缺项名单

以下表示尚未收录相应来源值，不表示已经证明无法找到。

| 材料 | 英文名 | 尚缺物性 |
|---|---|---|
| 羽绒/羽毛填充物（比例未详） | Down/feather filling, ratio unspecified | 杨氏模量 E、泊松比 ν |
| 稻壳/谷物纤维成型复合材料（配方未详） | Rice-hull / grain-fibre formed composite, formulation unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 再生/复合皮革（组成未详） | Bonded leather, composition unspecified | 泊松比 ν |
| 干燥苔藓（种类/处理未详） | Dried moss, species/treatment unspecified | 杨氏模量 E、泊松比 ν |
| 纸绳及纸绳编织用材料 | Paper cord and materials used for paper-cord weaving | 泊松比 ν |
| 藤材/藤编（种类/结构未详） | Rattan, species/construction unspecified | 泊松比 ν |
| 藤/绳复合编织（绳纤维未详） | Rattan/twine composite weave, twine fibre unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 固体皂/清洁块（配方未详） | Solid bar soap / cleansing bar, formulation unspecified | 泊松比 ν |
| 桦树皮 | Birch bark | 泊松比 ν |
| 沥青类屋面材料（来源标为asphalt；构造未详） | Bituminous roofing material, source-labelled asphalt; construction unspecified | 泊松比 ν |
| 羊毛纱与棉结接织物构造（比例未详） | Knotted wool-yarn and cotton textile construction, ratio unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 来源标为Leatherite的软包表面（组成未详） | Leatherite-labelled upholstery, composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 漆皮（涂层与基底未详） | Patent leather, coating and substrate unspecified | 杨氏模量 E、泊松比 ν |
| 植物编织材料（种属与构造未详） | Plant weaving material, species and construction unspecified | 泊松比 ν |
| 回收消防水带复合构造（组分层构未详） | Recycled fire-hose composite, construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 雪尼尔纱（纤维化学未详） | Chenille yarn, fibre chemistry unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 棉/亚麻混纺（比例/结构未详） | Cotton/linen textile blend, ratio/construction unspecified | 泊松比 ν |
| 棉/亚麻/粘胶/聚酯混纺（比例/结构未详） | Cotton/linen/viscose/polyester blend, ratio/construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 填充纤维（化学组成未详） | Filling fibre, chemistry unspecified | 杨氏模量 E、泊松比 ν |
| 起绒/法兰绒类织物（纤维未详） | Napped/flannel-like textile, fibre unspecified | 杨氏模量 E、泊松比 ν |
| 麻绳（纤维种/结构未详） | Hemp rope, fibre species/construction unspecified | 泊松比 ν |
| 聚酯/腈纶混纺（比例/结构未详） | Polyester/acrylic textile blend, ratio/construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 聚酯/亚麻混纺（比例/结构未详） | Polyester/linen textile blend, ratio/construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 聚酯/亚麻/棉混纺（比例/结构未详） | Polyester/linen/cotton textile blend, ratio/construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 聚酯/亚麻/人造丝混纺（比例/结构未详） | Polyester/linen/rayon textile blend, ratio/construction unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 聚酯/尼龙混纺（比例/结构未详） | Polyester/nylon textile blend, ratio/construction unspecified | 泊松比 ν |
| 聚丙烯/聚酯混纺（比例/结构见原文） | Polypropylene/polyester textile blend, ratio/construction source-conditioned | 泊松比 ν、密度 ρ |
| 再生棉纤维/织物（工艺/结构未详） | Recycled cotton fibre/textile, process/construction unspecified | 泊松比 ν |
| Tetoron源标签纤维（化学组成未独立确认） | Tetoron source-label fibre, chemistry not independently confirmed | 泊松比 ν |
| 天鹅绒/丝绒（纤维组成未详） | Velvet, fibre composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 羊毛/棉混纺（比例/结构见原文） | Wool/cotton textile blend, ratio/construction source-conditioned | 杨氏模量 E、泊松比 ν、密度 ρ |
| 羊毛/棉/聚酯混纺（比例/结构见原文） | Wool/cotton/polyester textile blend, ratio/construction source-conditioned | 杨氏模量 E、泊松比 ν、密度 ρ |
| 羊毛/粘胶混纺（比例/结构见原文） | Wool/viscose textile blend, ratio/construction source-conditioned | 杨氏模量 E、泊松比 ν |
| 涂装木材（木种/涂层未详） | Painted wood, species/coating unspecified | 泊松比 ν |
| 合成绒面材料（来源构造标签） | synthetic suede — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν |
| 防泼水绒面材料（来源构造标签） | water-resistant suede — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| Twinface 双面羊皮（来源构造标签） | Twinface sheepskin — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 羊皮（来源构造标签） | sheepskin — source-labelled material, finer composition unspecified | 泊松比 ν |
| PlanWood（源商品材料名）（来源构造标签） | PlanWood — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 搪瓷/珐琅涂层铝（来源构造标签） | enamelled aluminum — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 磨砂材料（源标签 nubuck，基材未进一步确认） | nubuck — source-labelled material, finer composition unspecified | 泊松比 ν、密度 ρ |
| Solyte 中底材料（源商品名）（来源构造标签） | Solyte branded material — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν |
| 防水皮革（来源构造标签） | waterproof leather — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν |
| 粉末涂层钢（钢种/涂层未详） | Powder-coated steel, steel/coating unspecified | 泊松比 ν、密度 ρ |
| 再生塑料帆布（来源构造标签） | recycled-plastic canvas — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 意大利头层皮革（来源构造标签） | top-grain Italian leather — source-labelled material, finer composition unspecified | 杨氏模量 E、泊松比 ν、密度 ρ |
| 磨砂皮革（来源构造标签） | nubuck leather — source-labelled material, finer composition unspecified | 泊松比 ν、密度 ρ |
| 全粒面皮革（来源构造标签） | full-grain leather — source-labelled material, finer composition unspecified | 泊松比 ν |
