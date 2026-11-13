# Cycle11 柔性与混合物体候选审核包

日期：2026-11-13。状态：作者检查通过，待 root 独立复核及唯一合并；未改共享库存、材料树或网站。

## 结果

- 从 C10 留下的 1,073 个未读候选中，读取 40 个 metadata shard，逐条审查 417 个对象。
- 允许新增 161 个真实来源 UID、161 个 WHOLE 库存范围；其中 30 个保留作者材料原文，131 个为用户授权的合理宽材料选项。
- 共 160 个 CC BY、1 个 CC0；来源许可按冻结元数据记录，作者署名保留。
- 新增 E/ν/ρ 记录 0，未下载 GLB，未测本地几何哈希，未新增机械组件。
- 累计 1,530 个候选全部保留逐条去向。656 个仍处于未读 shard；不是已审核否定。
- 16,531 项作者检查通过，0 失败。作者检查不替代独立复核。

## 去重与边界

核对库存及别名 UID、库存实测几何哈希、旧柔性批次官方预期 LFS 哈希、同批预期哈希、名称、作者及点面统计。

- B9217 另一个摄影扫描 UID 与 C10 同博物馆编号对象对应，写入别名 crosswalk，不新增。
- Tshirts 与库存同作者、同点面数量，暂缓；Manoi 旅行包与已有同作者同面数藤包暂缓。
- portfel_lp 与 ABO 对象点面统计相同，暂缓内容核验，不把统计碰撞写成已证实重复。
- Still Life 和 Teddy 教学共享底模、多配色、女性外套同拓扑双上传均隔离。
- 通用同名但作者、拓扑计数、预期文件哈希不同的对象，可作为不同来源身份记录；内容级唯一性仍未证明。
- 专业/商用禁用正文与 CC BY 字段冲突的一只 Tory & Burch 包，未放行。
- 未核完整许可链的第三方 port/转载/采购模型，未放行。

## 材料与组件

WHOLE 仅代表库存范围，不能称“完成机械分件”。皮革包仅适用袋身；羊毛衣物仅适用衣身；鞋帮允许织物、皮革或合成革合理选项，鞋底橡胶同样明确标为近似。备选材料不是同时存在的多种实测材料。

消防水带保留复合构造，不推纯聚酯或纯橡胶。Apollo 手套保留作者的 Chromel-R、硅橡胶及橡胶层描述，注明复刻来源及层级未核。羊皮大衣保留皮革衣身、皮革包覆木纽扣的原文构造。没有适当既有节点的标签使用 UNMAPPED，不偷换精确节点。

## 文件

- new_inventory_rows.csv / inventory_delta.csv：当前库存 schema 兼容增量。
- new_objects.csv：161 个来源对象及双语名、许可、精确资产链接。
- object_material_evidence.csv：全作者原文、材料声明或合理选项、范围与限制。
- asset_license_download_registry.csv：官方固定 commit 路径、预期 LFS SHA-256、大小、许可与署名。
- candidate_reconciliation.csv：累计 1,530 UID 逐条去向。
- source_freeze_registry.csv / dedup_input_registry.json：输入路径、SHA、大小及 URL。
- collision_adjudication.json / source_alias_crosswalk.csv：碰撞裁决与已证实来源别名。
- validate_package.py / CHECKS.json：可重跑作者检查。
- FINAL_MANIFEST.json：冻结文件清单及 SHA-256。

库存基线 SHA-256：a87d577affbc95778d6887072112aeb49f893165462ccc58ff294466e093a987。合并前 root 必须复核当前基线、并检查并行包 UID/预期哈希交集。
