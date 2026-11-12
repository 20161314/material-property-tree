# Cycle8：新增柔性优先几何对象（独立包）

日期：2026-11-13，Asia/Shanghai。状态：作者检查通过，未并入共享表，待交叉审查。

## 本轮结果

- 34 个新来源几何对象身份，34 个 WHOLE_OBJECT 占位组件对；不是 34 个新发现机械组件。
- 来源为官方 Objaverse-LVIS 资产记录；33 个 CC BY 4.0、1 个 CC0。逐项保留 UID、作者、原文、许可、精确 GLB 路径和官方 LFS 预期摘要/大小。
- 6 个材料标签由资产作者明确声明，28 个为用户授权的合理宽材料选项。均单列证据类型、适用范围和局限；没有将近似说成官方声明。
- 0 个 E/ν/ρ 证据组，0 个 GLB 下载。官方预期 SHA 仅在下载注册表中，不写成已验证本地几何 SHA。
- 作者验证 681 项通过，0 失败。主库/共享文件未修改。

## 来源与冻结

官方仓库 allenai/objaverse；冻结提交 556637099bf4fa79ea7b239d0d9c328b8a2e9ac8。官方主域连接超时；hf-mirror.com 仅作传输。LVIS 压缩清单与 4 个 metadata 压缩分片均核对官方树 LFS SHA 和大小；GLB 官方树 4 个目录、20 页、20,000 文件元数据仅用于路径、预期摘要与大小，不计为新增对象。

复用 evidence_manifests/pixieverse/objaverse_object-paths.json.gz（19,803,736B），其 SHA 与当前冻结官方树 LFS 一致；未重复下载。新冻结元数据约 22.0MB，已清理本批次的 3MB 截断发现响应及两份相同树响应；没有删除原有证据。

## 逐项准入与排除

先枚举 38 个服装、包、鞋、玩偶等柔性优先类的 1,530 个 UID。当前 inventory 所有字段及既有 alias 表逐 UID 筛查发现 1 个已入库，排除；4 个小分片覆盖其中 100 条，逐条对照作者名称、描述、许可与物体范围。其余 1,429 条未取 metadata shard，明确保持待办，不计入新增。

官方类别可能误标：blanket 出现山地扫描，tote_bag 出现青铜钟，hat 出现 tree。它们不能按类别直接晋级。重贴图 RTFKT、作者声明镜像或底模不明、同作者同拓扑计数裙装、共享熊/袜子底模、角色/场景、已知坏扫描等均逐条暂缓。已入的 short dress 一 UID 包含三套纹理，仍只计一个源几何；服装套装/成对鞋资产同样只计一次，不按材质、衣件或视图拆成新几何。

本批 34 UID 与现库所有 UID/alias、已记录几何 hash、精确名称和顶点/面数均无匹配；本批官方预期文件摘要也互异。此结果是来源身份/已知重复筛查，不是全库归一化几何内容去重证明。GLB 未下载，不声称通过拓扑/仿真就绪审核。

## 材料边界

作者明确标签示例：The Muscle Bag 的 Artificial Leather；Italian Renaissance Zimarra 的 wool；博物馆 B9214 的 Cotton；HoodieBaseModel 的 terry；提手袋的 non tissé；Red and White Leather Purse 的 leather。保留来源支持的粒度，不从合成皮推成 PU/PVC，不从 terry 推成棉。

近似标签只适用于写明范围：鞋仅鞋面织物候选，靠垫/玩偶仅外覆织物候选，包仅包身候选；不把鞋底、填充、扣件或角色皮肤继承为织物。没有几何分件时依然一个 WHOLE fallback，组件范围文字不虚增机械部件。后续更精细材料或部件证据可替换这些近似，不自动继承物性数值。

## 合并交付

- new_objects.csv：34 物体及资产元数据。
- new_inventory_rows.csv：34 行，列名/顺序与当前 inventory 完全一致。
- object_material_evidence.csv：34 行作者原文及材料声明/近似依据。
- asset_license_download_registry.csv：34 行逐项许可、作者归属、精确下载链接及官方 LFS 预期摘要。
- candidate_reconciliation.csv：全部 1,530 UID 的准入/暂缓/未审/去重状态。
- source_freeze_registry.csv、dedup_input_registry.json：证据与基线指纹。
- CHECKS.json、validate_package.py：681 项作者检查。

基线 inventory SHA：4686ff1770b144108a0b6c86c9a36d09d11239af333b00fb5d64dc617ed7ab02；42,564 来源对象、68,779 组件对、68,828 状态行。仅合并本包后的预期为 42,598 来源对象、68,813 组件对、68,862 状态行；其他并行增量须由主合并者另算。禁止把候选清单 1,530、目录树 20,000 文件或材质选项计作本轮新增。
