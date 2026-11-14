# 当前物体与材料表下载

发布：8123b621d5；日期：2026-11-14。gzip 解压保留原文；物体 Markdown 每 10,000 个来源身份分片。

54,281 个来源对象身份；118,746 个对象组件对（含 WHOLE 占位）；3,910 个当前非流体材料节点。来源身份尚未完成跨源几何内容去重，真实部件尚未全枚举。

主账：2,429 完整＋3,055 缺项＝5,484 来源组。全库：6,186 完整＋94,906 缺项＝101,092 组，已包含主账，禁止重复相加。外库转录不等于逐篇回读原始论文。

当前材料节点中，1,667 个有完整组；1,697 个三项分别有来源值；32 个暂无值。粗细节点可能包含彼此，不是互斥材料种数。

官方接受绑定语句 13,472 条，隔离 186 条。语句数不等于非空面区数或机械部件数；不自动赋予物体 E/ν/ρ。

property_ranges_by_reported_definition.csv 按原文物性定义分组。不同拉伸、动态和有限应变定义分别保留；派生范围不新增证据组。同文多组可分记录，同组两项仍只计一条缺项组。

source_asset_material_semantic_holds.csv 单列资产级材料语义疑点，与组件绑定隔离分开。所有原始标签、来源与限制保留在对应 CSV。

| 文件 | 压缩字节 | 原文 SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 3347976 | 52b052e48c316235a46e131f1e7dbd55a9dd48fc78fe4917fd976f011b8d615a |
| [物体表_02.md.gz](物体表_02.md.gz) | 1351299 | 9378c9481875a85863410ec54df78a20bfbfaa85349a3430dbc9a733227a8ea2 |
| [物体表_03.md.gz](物体表_03.md.gz) | 861771 | e46fc23c5b4a31aad6755dca88614300098a6bb5a81d329225d95ed6595ebb59 |
| [物体表_04.md.gz](物体表_04.md.gz) | 361092 | c25093d31fb7685416f62e36a59fda946157f391caa45162c1c798e726a15bc5 |
| [物体表_05.md.gz](物体表_05.md.gz) | 797120 | b38421b767e69e68820a8f44ef5bd7d85cc2bcc96060e2b90f4432e137dbdec0 |
| [物体表_06.md.gz](物体表_06.md.gz) | 1302260 | a0f48760b23f2aa6772b62708d83e91530f54d2c89cbc910d3074b349655d1df |
| [source_asset_material_semantic_holds.csv.gz](source_asset_material_semantic_holds.csv.gz) | 1542 | 59f0d9d8c9e4b6760f6e2fa57e91968138104a4c66b46ad94c34cb7911b37c18 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7512190 | c06dec4216f875e55ba23cee41a734efadcfaabb94c5367cf5da164545898c49 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 8515473 | 6aaf6e3d667673f8ea4653fdaf6f613812257e9e1f7329159568ad0cefa4085e |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 79358 | 863893b7718787ea4f6154bce7f5aed64f1a1e529e644ce0bd916f28ff0ab65e |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 402358 | 43ab5477a416607feaa0635333992d5050ca394b0d0f9ec870b845042329c134 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 324141 | bff5bf712d48f62eb374f8a0c1dc8ea4e5d08b5e41dbf4e82086bfa3da57985f |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 1329565 | 936f87882986e6a1bec6f6b57aebc24aad6ce4440aef20ba53c8e49098ffa807 |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 1783051 | 71c22536bba8067705bea605a49c9fd396dbf17de12dab15c2774d1d5b45789d |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 1301208 | c2010b943e33e9e566b85d500896c74eb16ba49cdb9da04bd993cf3f1307995b |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 47357 | f4fb5eb12eff3eecf79abee6e8001e77cb4f5a5d73c8b65b5139f768a1a4aa34 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 95624 | dbcfec1f2fa28961612035a7b134ce0140b56b5a7181e4b01b30164d60a72047 |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |
| [reviewed_source_material_links.csv.gz](reviewed_source_material_links.csv.gz) | 9008242 | c7d5afc98dd8829017c28563090e5e65d5b88d400c58b0159db0fec0a2fc3632 |
