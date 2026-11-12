# 当前物体与材料表下载

日期：2026-11-13。物体Markdown每10,000来源身份分片；gzip解压保留原文。

42,564个来源对象身份；68,779个对象组件对（含WHOLE）；2,741个粗细材料身份节点。来源身份不等于内容去重几何，全部真实部件尚未全枚举。

主账2,416完整＋1,810缺项来源组；全库6,173完整＋93,662缺项组。二者是不同收录范围，禁止相加。

官方接受材料区域绑定8,679条；隔离143条；被官方绑定取代的近似12条保留历史。材料区域不增加机械部件，不自动给物体赋E/ν/ρ。

property_ranges_by_reported_definition.csv按原文物性定义分组。不同拉伸/动态/有限应变定义不混成通用值；范围派生视图不增加证据组。

| 文件 | 压缩字节 | 原文SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 538611 | 3438d470df7d8f67946d6373dc6f08ce90dc39c9dd200b7dc5ba1fd5dcac85ed |
| [物体表_03.md.gz](物体表_03.md.gz) | 360637 | 5f1cec042a3f23fd954671de9422ca264446b1c7eaf4302f43c6cf27bb979b10 |
| [物体表_04.md.gz](物体表_04.md.gz) | 926402 | 252bd3c3f1dbe6b89ba4b14fddf79a81827f91efaa8ffef07fd67e94039d58bd |
| [物体表_05.md.gz](物体表_05.md.gz) | 626267 | 785580823a636329e2256580ef83a065ba4b69afc258999934c35141f853fc4b |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7545800 | 14bc0c7375679827df2181fe3b1eb7f1cc89ef70959348b3ae5eb0db0d6111b3 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 67055 | b215431fdedebe8159feb344e9fe44aee410ab64ef873651a6b6296bfae0d8b2 |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 278229 | 47413671284fe45c01a0d8104502ef868aabd52aef024520399050ccd54aebd1 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 213868 | 0f857ade6b23984f8d2bae8f9dc7430c83551c03e5529f362ee79c81b24b1fe6 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 736844 | 5d7a62882de7d2ecb23860264b7020e2bdd1e1c3604b082936c956adbe3d315f |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 126411 | 99ef50dfecb7bc070e789214ca952581f0f41897c077f189225630508baef2e2 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 899432 | 6f873d89d98ac527bcb05c2c9747b26eafdbf67ad982d1d2796d38190fc12d09 |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 41369 | a8f2a099086208043ac062203c9e910f4979ed2547af1a27a07957758ad03c97 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 52506 | f9163fa7825a2de0ffeb5ee3b3d000a9dc7dd196c304325fd040e44a15a50c81 |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |

## 实际几何字节核验子集

24个既有对象、139个源分割OBJ（556,933 bytes）已核本地实际字节；不是新增对象或机械部件。

2个共面、14个含零面积面、41个至多8顶点、136个有反向重复面、8个开放。每个有非退化面；不保证高保真、闭合、流形或仿真就绪。

- [核验清单](../verified-geometry-payload-subset.csv)：含包下载URL及本地冻结路径；OBJ未作为GitHub单文件发布。
- [逐网格质量诊断](../verified-geometry-mesh-diagnostics.json)
- [独立核验报告](../verified-geometry-payload-review.md)
