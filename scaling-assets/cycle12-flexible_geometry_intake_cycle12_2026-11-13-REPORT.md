# Cycle12 柔性与混合对象来源身份 intake

日期：2026-11-13（Asia/Shanghai）。状态：作者包待独立复核，未合并共享库存或网站。

## 结果

- 精确承接 C11 剩余 **656** 条未读 UID，逐条读取作者标题、完整描述、标签及许可。90/90 metadata 片的 SHA-256 和字节数均匹配固定官方 commit 的 LFS 元数据。
- 初选 324 条，10 条因底模、改色或版本线索撤回，7 条因未取得 GLB 预期文件摘要暂缓；最终 **307 个来源对象**。
- 28 条保留作者明确材料原句，279 条为用户授权、经过合理性审核的材料近似或选项。两者分别标记，不将 PBR 或类别标签写成官方组成证明。
- 307 行均为 WHOLE 库存范围；新增机械分件 0、GLB 下载 0、E/ν/ρ 数值 0。预期 LFS SHA 只表示官方预计文件，不冒充本地几何哈希。
- 307 条许可：306 CC BY、1 CC0。120 条多材料/构造/备选标签保持精确原意、暂为 UNMAPPED，未强挂不相符的纯材料节点。
- 作者校验 **53,974 项，0 失败**。原 C11 历史审定文字和决定保留；当前库存 SHA 未变。

如独审通过并合并：43,048 + 307 = **43,355 来源对象**，69,471 + 307 = **69,778 组件对（含 WHOLE）**，状态行 **69,827**。这些是来源身份库存量；未声称全库内容级几何去重或完整机械分件。

## 剩余 656 条逐条对账

| 决定 | 条数 |
| --- | ---: |
| HOLD_POSSIBLE_DUPLICATE | 24 |
| ADMITTED_SOURCE_OBJECT | 307 |
| HOLD_LICENSE_OR_SCOPE | 50 |
| HOLD_AUTHOR_IDENTITY_OR_SCOPE_UNRESOLVED | 84 |
| HOLD_OUTSIDE_FLEXIBLE_INTAKE | 36 |
| HOLD_GAME_ASSET_OR_VARIANT_LINEAGE | 8 |
| HOLD_CHARACTER_OR_BODY_SCOPE | 72 |
| HOLD_POSSIBLE_SHARED_TEACHING_BASE | 49 |
| HOLD_MISSING_EXPECTED_GEOMETRY_DIGEST | 7 |
| HOLD_SCENE_OR_BEDDING_SCOPE | 3 |
| HOLD_SPAM_OR_UNRESOLVED_OBJECT | 1 |
| HOLD_THIRD_PARTY_LINEAGE | 5 |
| HOLD_GEOMETRY_METADATA_ZERO_FACES | 2 |
| HOLD_LICENSE_TEXT_CONFLICT | 1 |
| HOLD_MATERIAL_SCOPE_UNRESOLVED | 1 |
| HOLD_MECHANICAL_CHARACTER_SCOPE | 6 |

全候选 candidate_reconciliation.csv 仍保留 1,530 个候选 UID；本轮范围单列 reviewed656_reconciliation.csv。剩余 metadata 未读条数为 **0**，不等于剩余候选全部可用。

## 重要隔离

- Still Life 教学场景、5552面/2817点泰迪熊教学底模、9328面/4890点袜/脚模板，均保留共享底模或身份不明的逐条理由。
- Abbey backpack 近似点面与同作者导出版本、Cushion27/Cushion24、棕/黄钓鱼帽、同作者红礼服、同拓扑蜡染衬衫等保留待核，不把颜色或文件导出算新几何。
- Sling Bag 的冻结 license=by 与作者正文“please do not use these models for commercial purpose”冲突，隔离。
- Google Poly备份、游戏移植/皮肤和明确他人模型，先保留原链待核。
- 木制熊雕像和铁护手按作者硬质材料声明收录，不称整件柔软。沙发/桌布套件只记录外覆面范围，硬框架不继承。桦树皮、动物皮未被擅自改写为实木或已鞣皮革。

## 网络缺口

89 个入选涉及的目录分片：85 个完整分页，4 个因 HTTP 429 或官方连接超时未读全。部分页仍保存并标注未完成。

7 条初选 GLB 缺官方预期摘要；另试官方/mirror paths-info 与 commit-pinned raw LFS pointer，均超时或503。因此这7条暂缓，**不表示模型不存在**。见 raw_pointer_registry.json、geometry_direct_path_registry.json 和逐UID理由。没有为绕过证据门而下载 GLB。

## 核验与交付

- new_inventory_rows.csv / inventory_delta.csv：307行，列名与当前权威库存完全一致，所有列非空。
- new_objects.csv、object_material_evidence.csv、asset_license_download_registry.csv：逐对象对应，保留英文/中文展示名、作者原名、原文、下载路径、许可、署名和预计LFS摘要。
- source_freeze_registry.csv：本轮metadata和官方分页、复用输入路径与SHA。
- collision_adjudication.json：名称、点面、作者、预期文件碰撞队列及审定。
- INPUT_SNAPSHOT.json、dedup_input_registry.json：基线和别名输入冻结。
- CHECKS.json、FINAL_MANIFEST.json：作者检查及交付快照。

此包只新增来源对象身份。全局几何内容唯一性、内部构件完整性和具体材料化学组成仍分别受限；作者材料声明不能作为数值物性来源。
