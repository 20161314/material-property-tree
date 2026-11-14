# 当前物体与材料表下载

发布：223c7f92c1；日期：2026-11-14。gzip 解压保留原文；物体 Markdown 每 10,000 个来源身份分片。

54,231 个来源对象身份；118,696 个对象组件对（含 WHOLE 占位）；3,903 个当前非流体材料节点。来源身份尚未完成跨源几何内容去重，真实部件尚未全枚举。

主账：2,429 完整＋3,048 缺项＝5,477 来源组。全库：6,186 完整＋94,899 缺项＝101,085 组，已包含主账，禁止重复相加。外库转录不等于逐篇回读原始论文。

当前材料节点中，1,667 个有完整组；1,697 个三项分别有来源值；32 个暂无值。粗细节点可能包含彼此，不是互斥材料种数。

官方接受绑定语句 13,472 条，隔离 186 条。语句数不等于非空面区数或机械部件数；不自动赋予物体 E/ν/ρ。

property_ranges_by_reported_definition.csv 按原文物性定义分组。不同拉伸、动态和有限应变定义分别保留；派生范围不新增证据组。同文多组可分记录，同组两项仍只计一条缺项组。

source_asset_material_semantic_holds.csv 单列资产级材料语义疑点，与组件绑定隔离分开。所有原始标签、来源与限制保留在对应 CSV。

| 文件 | 压缩字节 | 原文 SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 3347976 | 52b052e48c316235a46e131f1e7dbd55a9dd48fc78fe4917fd976f011b8d615a |
| [物体表_02.md.gz](物体表_02.md.gz) | 1350452 | 8bf3cb2f0aa16e155a20ab2b0b2d6f6271aa2c4ae00529f86681ff4dd3ea6dfb |
| [物体表_03.md.gz](物体表_03.md.gz) | 850537 | 2b21dc8f6b785553ecd6db6eb22ea83def023efdd9c13e44baae3005e8eb9a72 |
| [物体表_04.md.gz](物体表_04.md.gz) | 361185 | 18df3d1392d89da37657864ed0e227dd543d88054c189d717e531f686c61084f |
| [物体表_05.md.gz](物体表_05.md.gz) | 800742 | 493eb65afdd02dd46a26e8c05c99bebed520998782a110d31f8c48411672614e |
| [物体表_06.md.gz](物体表_06.md.gz) | 1297738 | fb7d8ada5ec210b472794441c9da807459e86e6a269e561955ebcde535012817 |
| [source_asset_material_semantic_holds.csv.gz](source_asset_material_semantic_holds.csv.gz) | 1542 | 59f0d9d8c9e4b6760f6e2fa57e91968138104a4c66b46ad94c34cb7911b37c18 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7512190 | c06dec4216f875e55ba23cee41a734efadcfaabb94c5367cf5da164545898c49 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 8501609 | 863ee997604fb201d47f4a2bfc17ab68b86f70eb86ca7fe144159e0c7e721976 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 79358 | e64cfe07fbe502f3d773654e538d88d1bab84e18616ff89af6cb4459932b27f5 |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 401513 | dd3b6578f79087127a1d0e4594caa8615f0746b3dd0aa9b27fd34f5e0b7eb6f9 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 323412 | 37be1e36124f15d5d3975e9fc6f128e9eea6c63ec2e9c351bfd06a01641bda31 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 1325400 | b328703da96d7a6f7bebb5c3d4bce1f760fa4010f794d099795312710feeb472 |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 1781621 | 69b93358818a243819ec2dcc5c4ee9c002bd8b9c5736f753086c69e6619a3615 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 1301208 | c2010b943e33e9e566b85d500896c74eb16ba49cdb9da04bd993cf3f1307995b |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 47357 | f4fb5eb12eff3eecf79abee6e8001e77cb4f5a5d73c8b65b5139f768a1a4aa34 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 95624 | dbcfec1f2fa28961612035a7b134ce0140b56b5a7181e4b01b30164d60a72047 |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |
| [reviewed_source_material_links.csv.gz](reviewed_source_material_links.csv.gz) | 8993571 | ffec726a54f0cf3f61bdb301d7c133eb1100e01ca8d5b8d1aa41d42715b97278 |
