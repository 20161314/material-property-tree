# 当前物体与材料表下载

发布：86e573821f；日期：2026-11-14。gzip 解压保留原文；物体 Markdown 每 10,000 个来源身份分片。

43,675 个来源对象身份；71,130 个对象组件对（含 WHOLE 占位）；3,900 个当前非流体材料节点。来源身份尚未完成跨源几何内容去重，真实部件尚未全枚举。

主账：2,427 完整＋3,046 缺项＝5,473 来源组。全库：6,184 完整＋94,897 缺项＝101,081 组，已包含主账，禁止重复相加。外库转录不等于逐篇回读原始论文。

当前材料节点中，1,663 个有完整组；1,691 个三项分别有来源值；32 个暂无值。粗细节点可能包含彼此，不是互斥材料种数。

官方接受绑定语句 13,472 条，隔离 186 条。语句数不等于非空面区数或机械部件数；不自动赋予物体 E/ν/ρ。

property_ranges_by_reported_definition.csv 按原文物性定义分组。不同拉伸、动态和有限应变定义分别保留；派生范围不新增证据组。同文多组可分记录，同组两项仍只计一条缺项组。

source_asset_material_semantic_holds.csv 单列资产级材料语义疑点，与组件绑定隔离分开。所有原始标签、来源与限制保留在对应 CSV。

| 文件 | 压缩字节 | 原文 SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1178683 | bcbf73d62d717f63421ebc907e77a856c0adac9c337178d359505bc444c915c0 |
| [物体表_02.md.gz](物体表_02.md.gz) | 722081 | 37e73f7333e8ea607f934d7facb10eaf8f4f1e802dfaf9b9c4131eafff8ac5a4 |
| [物体表_03.md.gz](物体表_03.md.gz) | 361107 | 6e4961091a92a544cedcb2ef5f7b4934e4c344254c8106eb5fa5e207be202d3a |
| [物体表_04.md.gz](物体表_04.md.gz) | 830155 | 17ddfc2d51cabf7004ef792ef5cf2ffe3cc362fa6751b516040df5ed4d57ec5f |
| [物体表_05.md.gz](物体表_05.md.gz) | 1015928 | 3846253e2f6f72881cb28a56d9f42c83d0d8b57304945aee3e27eb3cf05ac716 |
| [source_asset_material_semantic_holds.csv.gz](source_asset_material_semantic_holds.csv.gz) | 1542 | 59f0d9d8c9e4b6760f6e2fa57e91968138104a4c66b46ad94c34cb7911b37c18 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7512190 | c06dec4216f875e55ba23cee41a734efadcfaabb94c5367cf5da164545898c49 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 336814 | 8f959396d47f49b939edcf33a7e75a523de6c6a9dd01a5b0d6380b1861090a0a |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 78437 | b7e29de0d4648e29244e695916cfcfb302bdd6916503163313c6fedb880fbf5c |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 400870 | 8670ae10501d6e79f089770f2881d487e96b001ddd6c7a128a7e35caab5be609 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 322761 | edcaadde21a995cdb790cf3715699f95f24177fa165fe0f88edd7343b1315721 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 1314862 | de2719f1d175cc6e2cd76a25b2590203f0ffed8631c79ca2f14d609d49aadec0 |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 216290 | 0ea8b503e9d0706b0b354433a39597cc1a9a083a37a7625dda6af1d6a4853853 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 1301208 | c2010b943e33e9e566b85d500896c74eb16ba49cdb9da04bd993cf3f1307995b |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 47357 | f4fb5eb12eff3eecf79abee6e8001e77cb4f5a5d73c8b65b5139f768a1a4aa34 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 95624 | dbcfec1f2fa28961612035a7b134ce0140b56b5a7181e4b01b30164d60a72047 |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |
| [reviewed_source_material_links.csv.gz](reviewed_source_material_links.csv.gz) | 142402 | a5d23b4f66c953fe1591559f76548e7560a86759427347bd718470b53f73d118 |
