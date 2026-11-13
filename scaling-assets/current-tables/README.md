# 当前物体与材料表下载

日期：2026-11-13。物体Markdown每10,000来源身份分片；gzip解压保留原文。

42,887个来源对象身份；69,169个对象组件对（含WHOLE）；2,875个粗细材料身份节点。来源身份不等于内容去重几何，全部真实部件尚未全枚举。

主账2,417完整＋1,947缺项来源组；全库6,174完整＋93,799缺项组。二者是不同收录范围，禁止相加。

官方接受材料区域绑定9,272条；隔离150条；被官方绑定取代的近似12条保留历史。材料区域不增加机械部件，不自动给物体赋E/ν/ρ。

property_ranges_by_reported_definition.csv按原文物性定义分组。不同拉伸/动态/有限应变定义不混成通用值；范围派生视图不增加证据组。

| 文件 | 压缩字节 | 原文SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 567546 | 8f73f554126b8d2d1d304b18d895448a3669bd09f00d78bab648e919aa0f0eef |
| [物体表_03.md.gz](物体表_03.md.gz) | 360539 | 1bb9f1da104082f76f3e6ae162cdd2844e2eb756fe43862dcb2e8d75d535e6f8 |
| [物体表_04.md.gz](物体表_04.md.gz) | 879205 | 08ff5a30005f303273cb4220ecfb380d03986e9b1615cfda79a75e12d8aa981d |
| [物体表_05.md.gz](物体表_05.md.gz) | 721973 | 5e275e47dee63629004088e9be5968986afddeca50b196f81bf3645bd908bdd9 |
| [current_material_options.csv.gz](current_material_options.csv.gz) | 7532578 | c3008c9bd0852e1de259706601516c2821b05ab2f8df7e7e719e6db842df2a04 |
| [intake_source_material_relations.csv.gz](intake_source_material_relations.csv.gz) | 77880 | 4e57b40d5a1fa8b7cdce9c9beff3875763e5844d58f3718e80b1f86e038bc2d1 |
| [quarantined_intake_source_material_relations.csv.gz](quarantined_intake_source_material_relations.csv.gz) | 1821 | ded123f11c4aeef55b93c6dd18aa9efeb7511e4e0f3ae5dbbf911d03dc800089 |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 69114 | 27650615d6a22e6cdf3f07a58b9081a8a5c7e77b65f35a8b85e98a57ee035c4f |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 294728 | a94e2985ccf994eb3f139088a2169e81d34079c5c703c36f2545b1616c893ab7 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 228961 | 5c5c35b8fec92e4fb270be10cd8d3edc8d1da46f2aaf2ac3abef746c6a7ad9e5 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 789432 | dd4c8c8c51701d683e8e62fa9b5a1525792697e5272691d80b8362f28b53208e |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 141287 | fc6b644a1ac611078387952b5d6ef1567fb97d8913df5d2bcfa8e1f3f836cbf1 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 953809 | 475ab647b2761bcb629333e229bfadf7fee5bf4da54508208c5462817c9b9951 |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 42588 | 38200b0fb8e02618018e2654f13ec6ad627b8c04b3e462f4fcda621706a57454 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 65139 | 6f7e7ee7207f3ebf004ec731d614f0886b655696ac5152d80ddb75268e92a17a |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |

## 实际几何字节核验子集

24个既有对象、139个源分割OBJ（556,933 bytes）已核本地实际字节；不是新增对象或机械部件。

2个共面、14个含零面积面、41个至多8顶点、136个有反向重复面、8个开放。每个有非退化面；不保证高保真、闭合、流形或仿真就绪。

- [核验清单](../verified-geometry-payload-subset.csv)：含包下载URL及本地冻结路径；OBJ未作为GitHub单文件发布。
- [逐网格质量诊断](../verified-geometry-mesh-diagnostics.json)
- [独立核验报告](../verified-geometry-payload-review.md)
