# 当前物体与材料表下载

日期：2026-11-13。物体Markdown每10,000来源身份分片；gzip解压保留原文。

42,564个来源对象身份；66,052个对象组件对（含WHOLE）；2,679个粗细材料身份节点。来源身份不等于内容去重几何，全部真实部件尚未全枚举。

主账2,415完整＋1,778缺项来源组；全库6,172完整＋93,630缺项组。二者是不同收录范围，禁止相加。

官方接受材料区域绑定422条；隔离3条；被官方绑定取代的近似12条保留历史。材料区域不增加机械部件，不自动给物体赋E/ν/ρ。

property_ranges_by_reported_definition.csv按原文物性定义分组。不同拉伸/动态/有限应变定义不混成通用值；范围派生视图不增加证据组。

| 文件 | 压缩字节 | 原文SHA-256 |
|---|---:|---|
| [物体表_01.md.gz](物体表_01.md.gz) | 1170596 | c4e346a663fe523a1ff7843e3efad9e0d622d61fe973a07620525ba41b6353cf |
| [物体表_02.md.gz](物体表_02.md.gz) | 538611 | 3438d470df7d8f67946d6373dc6f08ce90dc39c9dd200b7dc5ba1fd5dcac85ed |
| [物体表_03.md.gz](物体表_03.md.gz) | 360637 | 5f1cec042a3f23fd954671de9422ca264446b1c7eaf4302f43c6cf27bb979b10 |
| [物体表_04.md.gz](物体表_04.md.gz) | 905385 | 8115589a53e39bbe5760bdde8e8c6a6f28b3decf4b036a3c98e1882effdd114b |
| [物体表_05.md.gz](物体表_05.md.gz) | 209898 | b7d32332a6b317c0a98db19f0520e054fd4287d452119faa49765d281942db0c |
| [object_derived_material_table.csv.gz](object_derived_material_table.csv.gz) | 66265 | b294935d0fb3cafc7b0070b5fb5ffaf3012c65094189a4f99284be33d40d360a |
| [material_reverse_index_and_property_ranges.csv.gz](material_reverse_index_and_property_ranges.csv.gz) | 269868 | 2a6c0ad36f86910421842ee8f7adf614fc9e02669d9eed7e52a301980e359867 |
| [property_ranges_by_reported_definition.csv.gz](property_ranges_by_reported_definition.csv.gz) | 204768 | eef7e71a293c9d189ec09fbbb3a6650ccef2bb45ab06a8f062e29ff0fd05f105 |
| [main_property_source_groups.csv.gz](main_property_source_groups.csv.gz) | 685398 | c392ee88b6a6fe2a515e31b4aba541ddebf85e3d8e49d8675467ac8bfe35ce6e |
| [source_reported_material_label_index.csv.gz](source_reported_material_label_index.csv.gz) | 11943 | 9fb7af8a136abbe53d3da2481d6817ac68940abbcd5b4f1092704d37be05c495 |
| [source_semantic_components.csv.gz](source_semantic_components.csv.gz) | 13673 | 909a55a723b6baafd0739b9e57003b2943c74359cd6ae06e21ebee0afdee2081 |
| [source_reported_material_relations.csv.gz](source_reported_material_relations.csv.gz) | 22947 | f726c838d2937e5c643caebe203ac82efcfed14f7c8a255b3ad8d2c1b88ab612 |
| [official_bound_material_relations.csv.gz](official_bound_material_relations.csv.gz) | 49764 | 73ee044e263f2b4e5960085295c037be0c1980a0223525adee962156de2796db |
| [approximate_component_material_relations.csv.gz](approximate_component_material_relations.csv.gz) | 246 | 7d72338a3f90b8167ac8b75fb3acb4bc7dd587abd5f70823c205bad4e363949c |
| [superseded_approximate_component_material_relations.csv.gz](superseded_approximate_component_material_relations.csv.gz) | 2195 | d06d56c2fa92b25203562c4bd9600c79b53a41e3c9cd242b41433970dcff47e7 |
| [quarantined_official_bound_material_relations.csv.gz](quarantined_official_bound_material_relations.csv.gz) | 2203 | 29c8e7bf361bf274d3e8dda999763a591dc526d693e789631b314704d3730440 |
| [quarantined_legacy_options.csv.gz](quarantined_legacy_options.csv.gz) | 5847 | 1e304f07af09125f6c29bad28619f561efe1e45b14b402af2bab7006cc81ee6d |
| [physxnet_source_part_index.csv.gz](physxnet_source_part_index.csv.gz) | 6716758 | c7bfb56cdff787a91bfe76d441f481fbbf792eb8792cb3bc499fe291260288b7 |
| [physxnet_source_part_holds.csv.gz](physxnet_source_part_holds.csv.gz) | 472 | 23cdc84ea1bda64b78ea70da63082c0f54e39ce826b8101d70d86ea2ed62549b |

## 实际几何字节核验子集

24个既有对象、139个源分割OBJ（556,933 bytes）已核本地实际字节；不是新增对象或机械部件。

2个共面、14个含零面积面、41个至多8顶点、136个有反向重复面、8个开放。每个有非退化面；不保证高保真、闭合、流形或仿真就绪。

- [核验清单](../verified-geometry-payload-subset.csv)：含包下载URL及本地冻结路径；OBJ未作为GitHub单文件发布。
- [逐网格质量诊断](../verified-geometry-mesh-diagnostics.json)
- [独立核验报告](../verified-geometry-payload-review.md)
