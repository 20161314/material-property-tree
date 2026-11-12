# 当前物体与材料表下载

日期：2026-11-13。物体Markdown每10,000来源身份分片；gzip解压保留原文。

42,693个来源对象身份；68,908个对象组件对（含WHOLE）；2,765个粗细材料身份节点。来源身份不等于内容去重几何，全部真实部件尚未全枚举。

主账2,416完整＋1,838缺项来源组；全库6,173完整＋93,690缺项组。二者是不同收录范围，禁止相加。

官方接受材料区域绑定8,679条；隔离143条；被官方绑定取代的近似12条保留历史。材料区域不增加机械部件，不自动给物体赋E/ν/ρ。

property_ranges_by_reported_definition.csv按原文物性定义分组。不同拉伸/动态/有限应变定义不混成通用值；范围派生视图不增加证据组。

| 文件 | 压缩字节 | 原文SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 543386 | 464a3db460e7ddaf754c2cdc67902cb43de2ba9986d64bb3ba344feb5e0ee4c4 |
| [物体表_03.md.gz](物体表_03.md.gz) | 360701 | ffee3f7b5885f49ee966ac73f9f061d9bc19fe73b8c49a0a8988af454c59a004 |
| [物体表_04.md.gz](物体表_04.md.gz) | 919139 | b26ce7c6b5461aa58c7d5304fce31c5b6d4bbad4367035b8e8b32788c35aad97 |
| [物体表_05.md.gz](物体表_05.md.gz) | 639913 | 250846a247900bf0271a3af24b81c23c66ef14a81a18b5b1af7520aab453b4c1 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7545800 | 14bc0c7375679827df2181fe3b1eb7f1cc89ef70959348b3ae5eb0db0d6111b3 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 21615 | ab2c588dfa70d4dc2ea3321d5d294f504b41d106bac21d6b80d927fa4ca39a60 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 67504 | 5542e0e04465a274a00e85b4d0f702addde3ead0c2ceea0917e306ed56021f9e |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 281009 | b13c69a898ab0c9ae44e8be641d992ee60e25fa536bcb7bea5d8f067637e95b7 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 216729 | 7a5afdde43e430a35646c95fa11228805fc6f2b21bd511295add7fa0c37c5a5a |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 752893 | 69e6e12323d778a3ccd13ad4161ceba9aa5caaa97cc1bd382beeab22a97078fd |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 129695 | 770a6b56a75521675984dea433ff1807eb5c63b5fa41b90a85b4b5bc7eb470e2 |
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
