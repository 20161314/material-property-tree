# Cycle9 柔性/混合优先资产增量包

日期：2026-11-13。状态：作者校验通过，待 root 独立复核；未并入主表/网站。

## 本轮结果

- 新增候选准入 **34 个来源对象 / 34 个 WHOLE fallback 对 / 34 行**；新增机械分件 **0**。
- 作者明示材料 **4**（藤编包、羊毛斜纹长衣、乳胶手套、皮革挎包）；合理宽标签候选 **30**。
- 全部 34 条许可元数据为 CC Attribution（官方许可定义 CC BY 4.0）；作者、链接、冻结许可定位逐条保留。
- **0** GLB下载，**0** 新 E/ν/ρ；不继承材料物性，不声称全局内容去重或完整部件分解。
- 六个新 metadata 分片共 **21,696,841 bytes**；30页 GLB目录 API 共 **9,889,240 bytes**；总取元数据 **31,586,081 bytes**。
- 35 条初选撤回 1 条 Top Pink：与同作者旧 Dress Red 完全相同 faces/vertices；属于疑同拓扑，待GLB内容核验，非证明已相同。

## 基线与去重

- 基线 42,693 来源对象 / 68,908 对象组件对 / 68,957 状态行。
- 基线 inventory SHA-256: f5a5b6da2b43d247f530970d7e80bc688a3ca926d27b9ea8bc4e49f61c264598
- 查当前所有 UID/alias、已记录几何摘要、前轮LFS expected摘要及同期硬资产摘要，34项无交集；面/顶点计数无当前库存碰撞。
- GLB LFS摘要仅为官方预期值；inventory geometry_sha256 一律 NOT_DOWNLOADED_HASH_NOT_AVAILABLE。
- 未验证归一化网格、跨库重建或视觉等价；来源对象数不能称为全库唯一几何数。
- 羊毛长衣裁片、成对手套、背包+垫子资产组、挎包两纹理都只计其源 UID 一次。
- 藤包属于柔性/混合优先选材，不代表整个物体可形变；包身标签不赋予五金。

## 1,530条候选状态（累计，非本轮新增总量）

- HOLD_REVIEW: 32
- DEFERRED_UNREVIEWED_METADATA_SHARD: 1330
- HOLD_CATEGORY_OR_OBJECT_SCOPE: 79
- ALREADY_ADMITTED_PRIOR_CYCLE: 34
- ADMITTED_SOURCE_OBJECT: 34
- HOLD_LICENSE_OR_SCOPE: 14
- DEFERRED_BOUNDED_REVIEW_PRIORITY: 6
- EXCLUDED_EXISTING_ALIAS: 1

前轮34项标 ALREADY_ADMITTED_PRIOR_CYCLE，严禁重放；本轮新取99个候选元数据；其余1330仍未取，不宣称完成全部柔性对象。6个鞋帽只是本轮优先级后置，不作为不合格或材料不合理。

## 来源冻结

- Objaverse官方 commit: 556637099bf4fa79ea7b239d0d9c328b8a2e9ac8
- 六 metadata gzip逐个匹配前轮冻结官方树 LFS SHA及字节；hf-mirror只为传输。
- GLB逐项链接按官方 object-paths manifest 与冻结目录逐项对应；作者原文来自官方发布元数据，不由 LVIS分类证明材料。
- 4条明确材料声明保留 literal 原文；30条近似清楚标来源非正式材料。
- 作者说 leather-ish 的风衣只记宽皮革近似，不升级天然皮声明；乳胶不推天然或合成配方；Songket/Batik不推棉丝。
- Reallusion metadata BY与作者限制文字冲突、Minecraft重纹理、人物/场景、课程共享熊袜、hoodie reload均未准入。

## 逐项新增

| 源UID | 物体 | 材料标签 | 身份层级 |
|---|---|---|---|
| 85ac889151324c24a9b696a7b905e185 | 背包 / Backpack | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 511d44e5693549ca9c4002752a35fcb2 | 围巾 / Scarf | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 90cbed27e8ce4b7a9202e996f816974b | 手套 / Glove | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 74fa123561744c32bff6d5ef60b88ad7 | HumAi俱乐部T恤 / HumAi Club T-Shirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 93fab0443ba44d55853a878826c4ca60 | 泰迪熊毛绒玩具 / Teddy Bear Plush Toy | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 4038cf88cd384c6f98ecfe670147fc5c | 绿色藤编包 / Green Rattan Bag | Rattan, species/construction unspecified | 作者原声明 |
| f1cb64be69af4f16b6a1a53ec8ce6411 | 军用背包与垫子资产组 / Army Backpack and Mat Asset Set | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 099f508befcd4ebe9930502b48978042 | 拳击手套 / Boxing Gloves | Leather, natural/synthetic/tanning type unspecified | 合理近似候选 |
| 2037d88dfee0496e8539eb91d4e22926 | 包 / Bag | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| e5f37c5f821948628c5645a1d41b2afc | Thorsberg羊毛斜纹长衣重建 / Thorsberg Wool Twill Tunic Reconstruction | Wool fibre/textile, construction unspecified | 作者原声明 |
| 111b45e33a8d4e39b1f37f269e8a2069 | 宋吉织物手提包 / Songket Handbag | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 6132c68594544694b753b305b50bf66b | Creeper图案靠枕 / Creeper Pillow | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| ccf2b1da93f84074b48270b7c8cdc78c | 包资产 / Bag Asset | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 6358dc2620ef463c95e346ed6928bfe2 | 衬衫 / Shirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 7228bad14d6b423a8624ef69e5446994 | 连衣裙 / Dress | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 9a5d683196224650b76181239d648d05 | 连体服 / Overall Garment | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 3d1cb9cf4e244dbca966463b31ab6d92 | 五十年代夏季衬衫 / 1950s Summer Blouse | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| dd108faff010488db0e4eebbaaa2cebe | 女士手提包 / Ladies Handbag | Leather, natural/synthetic/tanning type unspecified | 合理近似候选 |
| be001e04840847388221deed199d6ded | 连帽衫 / Hoodie | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| d51e89bfa33646ba8771ddf972dc1af2 | 休闲连帽卫衣 / Casual Hooded Sweatshirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| d6b2561de39f423f9c7a2e7944485beb | 背心 / Tank Top | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| f2d9d794171d46b89217bf01621b1e8d | 衬衫 / Shirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 6fcc25c69a754ab09ab08d75cce06279 | 黑色连衣裙 / Black Dress | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| bd695b3f7ecf48dab7898c0a8b9a9840 | 垂落乳胶手套 / Fallen Latex Gloves | Latex rubber, formulation unspecified | 作者原声明 |
| dcc5c73cce1744dfa4d1bb5232c39d56 | 粉色手提包 / Pink Handbag | Leather, natural/synthetic/tanning type unspecified | 合理近似候选 |
| 1e2b45735eb340588a4adecbb4bf5ef0 | 带金属配件的手袋 / Purse with Metal Details | Leather, natural/synthetic/tanning type unspecified | 合理近似候选 |
| d5b3a043a2f04aae8f56439cb8aa2f19 | 旅行袋 / Duffle Bag | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 2fbb8f56b1ba47bdb6746d95b6fc2242 | 悬挂毛巾 / Hanging Towel | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 6a049f880cb84d26933ddaaed1221329 | 男式长衫 / Men Kurta | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 8c03afd455304b8bae71c44b7005e694 | 皮革挎包 / Leather Satchel | Leather, natural/synthetic/tanning type unspecified | 作者原声明 |
| e66a171f9d8d4787bd6e40f378d42191 | Punisher图案T恤 / Punisher T-Shirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| dbf86a22865544c0b3e81d2a0b8cca55 | 衬衫 / Shirt | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 7245acbcd9404a10ae0e595705805d02 | 蜡染托特包 / Batik Tote Bag | Textile fabric, fibre/construction unspecified | 合理近似候选 |
| 6f1504578f9343d088643cdbce38903e | 皮革外观风衣 / Leather Appearance Coat | Leather, natural/synthetic/tanning type unspecified | 合理近似候选 |

## 交付与验证

- new_inventory_rows.csv：当前85列原schema增量；new_objects.csv：独立来源对象清单。
- object_material_evidence.csv：作者原名、原描述、原标签、literal声明/近似依据与范围。
- asset_license_download_registry.csv：作者/许可/直接GLB路径/官方expected SHA；未下载。
- candidate_reconciliation.csv：完整1530候选逐条决定，前轮历史保留。
- source_freeze_registry.csv：下载及复用输入的绝对路径、SHA、字节、原始URL。
- dedup_reconciliation.csv、count_collision_review.json：逐项去重边界。
- 作者检查 769 项，0失败；未替代独立审核。
- 主表不变；若仅合并本包：42,727来源对象 / 68,942对 / 68,991行。若同期合并其他包，需root重算联合计数。
