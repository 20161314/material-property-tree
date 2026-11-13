# 当前物体与材料表下载

日期：2026-11-13。物体Markdown每10,000来源身份分片；gzip解压保留原文。

42,776个来源对象身份；68,991个对象组件对（含WHOLE）；2,801个粗细材料身份节点。来源身份不等于内容去重几何，全部真实部件尚未全枚举。

主账2,416完整＋1,874缺项来源组；全库6,173完整＋93,726缺项组。二者是不同收录范围，禁止相加。

官方接受材料区域绑定8,679条；隔离143条；被官方绑定取代的近似12条保留历史。材料区域不增加机械部件，不自动给物体赋E/ν/ρ。

property_ranges_by_reported_definition.csv按原文物性定义分组。不同拉伸/动态/有限应变定义不混成通用值；范围派生视图不增加证据组。

| 文件 | 压缩字节 | 原文SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 553503 | 343114bea12f59158d844e5100b549493e4606bbd5a7ec86233bd526871bbab5 |
| [物体表_03.md.gz](物体表_03.md.gz) | 360655 | 17689a535c736f5ccc1a24311484acfca0c64f7fd30592cb0bb868076315dde9 |
| [物体表_04.md.gz](物体表_04.md.gz) | 887623 | 41c829208e0d12f03908de08bcfcdaa77a36f8aa092b018cf4cae22fbbfa17f8 |
| [物体表_05.md.gz](物体表_05.md.gz) | 674277 | cbcb7fbff38a2521f25fce003b8726d90443c3e69ee211ed4a3ce3743ee9caa8 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7545800 | 14bc0c7375679827df2181fe3b1eb7f1cc89ef70959348b3ae5eb0db0d6111b3 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 45608 | 2919dc92b0d8984adce7a449adee7d01327a83a0436a35899662494f7c5805d1 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 67972 | bfa12b062ce829758bd517f1b30d27dc15ffde6d0cbbd712b31493bf55968e78 |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 285534 | 1b54dd3d0d9f918b9071e75597a1a160c7d7ecea0b7a400e71ee226140bdb73c |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 221183 | d580c6dccf4e443302c6c52c63e8e645da7a6f9047b912af802ae380b6a3a477 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 770534 | 2d7b5d65085461682493a848d3e333ea788ecd07197eac82ec0f0f1c7a179c5c |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 131301 | 3de17fbb451691c9dc42649411b03fd0da69b4e3b552b67880ebb69334fd83a9 |
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
