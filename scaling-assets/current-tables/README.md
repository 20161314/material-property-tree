# 当前物体与材料表下载

发布：f61495694c；日期：2026-11-14。gzip 解压保留原文；物体 Markdown 每 10,000 个来源身份分片。

54,071 个来源对象身份；118,536 个对象组件对（含 WHOLE 占位）；3,902 个当前非流体材料节点。来源身份尚未完成跨源几何内容去重，真实部件尚未全枚举。

主账：2,429 完整＋3,046 缺项＝5,475 来源组。全库：6,186 完整＋94,897 缺项＝101,083 组，已包含主账，禁止重复相加。外库转录不等于逐篇回读原始论文。

当前材料节点中，1,667 个有完整组；1,695 个三项分别有来源值；32 个暂无值。粗细节点可能包含彼此，不是互斥材料种数。

官方接受绑定语句 13,472 条，隔离 186 条。语句数不等于非空面区数或机械部件数；不自动赋予物体 E/ν/ρ。

property_ranges_by_reported_definition.csv 按原文物性定义分组。不同拉伸、动态和有限应变定义分别保留；派生范围不新增证据组。同文多组可分记录，同组两项仍只计一条缺项组。

source_asset_material_semantic_holds.csv 单列资产级材料语义疑点，与组件绑定隔离分开。所有原始标签、来源与限制保留在对应 CSV。

| 文件 | 压缩字节 | 原文 SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 3347976 | 52b052e48c316235a46e131f1e7dbd55a9dd48fc78fe4917fd976f011b8d615a |
| [物体表_02.md.gz](物体表_02.md.gz) | 1349781 | efa339d344c49b5cdeae5d2604713a9b2ddb5897cf9e0ad7bf690ac5ca35a3be |
| [物体表_03.md.gz](物体表_03.md.gz) | 819695 | b9434979f73d551af88e32e3211591f1e1f91dac1212b7ad8f5686f0ef32c4d0 |
| [物体表_04.md.gz](物体表_04.md.gz) | 361179 | afe90a2aa688026281e237415567faa8c3d40a948329d69dd86ed3cd7a2b828f |
| [物体表_05.md.gz](物体表_05.md.gz) | 810349 | 2a584a3fb753f5c35eea2105628bae6dcf6b41991bcae0b361475eb668370ecd |
| [物体表_06.md.gz](物体表_06.md.gz) | 1282006 | 7f8e0976b19780561ce289c8a84f4a45df277ab9269a837b2395de7f84145908 |
| [source_asset_material_semantic_holds.csv.gz](source_asset_material_semantic_holds.csv.gz) | 1542 | 59f0d9d8c9e4b6760f6e2fa57e91968138104a4c66b46ad94c34cb7911b37c18 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7512190 | c06dec4216f875e55ba23cee41a734efadcfaabb94c5367cf5da164545898c49 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 8462605 | 47321543db69e0b0bd2c5e050c9dc9b0e32361aa2c7d16ab5e5a034c41a89266 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 79336 | 26ab2f58b6e490e2730d5bdfe18b5f612287785aa1caa7c4ba02dab1e9767e9e |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 401343 | d66e36bdc058cee63e52e94b00121014b162a6b0cb9f23944d83ee289cd08fde |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 323251 | 17643a2bb57f00c0fd3457b9a1620279dff06f096c7ba8497c7741aa51f1a4cc |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 1321577 | 7ccc07957bb07804f4d98ed254c017a2d1582fe06df7a20d654a3ab93a231d07 |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 1776397 | a5b91de042e8b258fdeadeea712626b4e2fa3ea314878be4396e9d52946a46d6 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 1301208 | c2010b943e33e9e566b85d500896c74eb16ba49cdb9da04bd993cf3f1307995b |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 47357 | f4fb5eb12eff3eecf79abee6e8001e77cb4f5a5d73c8b65b5139f768a1a4aa34 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 95624 | dbcfec1f2fa28961612035a7b134ce0140b56b5a7181e4b01b30164d60a72047 |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |
| [reviewed_source_material_links.csv.gz](reviewed_source_material_links.csv.gz) | 8954807 | c6999a840beac60138fede178993b0f4933fbfdc4cc23676ef267733828c5dea |
