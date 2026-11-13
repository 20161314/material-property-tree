# 当前物体与材料表下载

发布：4e950555c5；日期：2026-11-14。gzip 解压保留原文；物体 Markdown 每 10,000 个来源身份分片。

43,675 个来源对象身份；71,130 个对象组件对（含 WHOLE 占位）；3,860 个当前非流体材料节点。来源身份尚未完成跨源几何内容去重，真实部件尚未全枚举。

主账：2,431 完整＋3,000 缺项＝5,431 来源组。全库：6,188 完整＋94,851 缺项＝101,039 组，已包含主账，禁止重复相加。外库转录不等于逐篇回读原始论文。

当前材料节点中，1,666 个有完整组；1,690 个三项分别有来源值；25 个暂无值。粗细节点可能包含彼此，不是互斥材料种数。

官方接受绑定语句 13,472 条，隔离 186 条。语句数不等于非空面区数或机械部件数；不自动赋予物体 E/ν/ρ。

property_ranges_by_reported_definition.csv 按原文物性定义分组。不同拉伸、动态和有限应变定义分别保留；派生范围不新增证据组。同文多组可分记录，同组两项仍只计一条缺项组。

source_asset_material_semantic_holds.csv 单列资产级材料语义疑点，与组件绑定隔离分开。所有原始标签、来源与限制保留在对应 CSV。

| 文件 | 压缩字节 | 原文 SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 699210 | d4948f8f96303b7dfeb752280c661bb9d0e863a0432c9dfbe6d33ca8eeb45217 |
| [物体表_03.md.gz](物体表_03.md.gz) | 361107 | 6e4961091a92a544cedcb2ef5f7b4934e4c344254c8106eb5fa5e207be202d3a |
| [物体表_04.md.gz](物体表_04.md.gz) | 830155 | 17ddfc2d51cabf7004ef792ef5cf2ffe3cc362fa6751b516040df5ed4d57ec5f |
| [物体表_05.md.gz](物体表_05.md.gz) | 1013644 | fa2e2fe46293f080c669ccd8b644581d35210f7c94cec6bed59d06f067fe51fb |
| [source_asset_material_semantic_holds.csv.gz](source_asset_material_semantic_holds.csv.gz) | 1542 | 59f0d9d8c9e4b6760f6e2fa57e91968138104a4c66b46ad94c34cb7911b37c18 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7502831 | d144afdf10977bcfafe4b5950d7c668e4c7d3c0e5b0daecd9c2725f269c1c28d |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 323549 | 942a03fe08a8fe3830c329663b6b6c3a1941675b6b33a5f0baaf6081328aa093 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 76242 | 08773bdc5a5ad1c1d36913ecdab2cd1c3eb1087c841a8b531beb62beb756cd4e |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 395271 | d825f456f7864429505cc35b9143062fca19ff62c3ab2ad45b6eb1147c814233 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 318182 | 2ea6ca677fef44293f7597c76c8701add1cb9cb8ea258bfdf6a73081b3093277 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 1278620 | 827f042f998107015d314c3fb26ac8aac142c3509846fc49de73bf6a4ad6f219 |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 214439 | 449e8c42b5d9e12cc0628e1225e26044f07a368fc48412faffa4a9bb28965bac |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 1301208 | c2010b943e33e9e566b85d500896c74eb16ba49cdb9da04bd993cf3f1307995b |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 47357 | f4fb5eb12eff3eecf79abee6e8001e77cb4f5a5d73c8b65b5139f768a1a4aa34 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 95561 | d7acb6ee20b5857740e39cd56f5a3c954c55161f5889f464cb2c0047dc6959ff |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |
