# C13 硬体几何组件包独立交叉复核

日期：2026-11-13（Asia/Shanghai）。结论：**PASS_FINAL_AUTHOR_PIN_VERIFIED**。

- 作者冻结包：`/Users/hezekai/Documents/博士/上交CS博/项目1：静态场景物理化与实时交互仿真/建表/50_物体优先反向材料库_2026-11-08/audit/hard_geometry_components_cycle13_2026-11-13`
- 作者 FINAL_MANIFEST SHA-256：`0f83e6ff80639f03fbfc939dffd2f26df6940fabc0d0ae6fc67de52d22895a68`；506 个冻结文件核验通过。
- 来源官方固定提交：`7879e0e50423290300ac20ecd6e727325f680b60`。
- 独审：标准块 37,697 项、USDC alternate 块 1,221 项、合并块 527 项，合计 **39,445 项全部通过**。

## 可合并增量

|项|标准块|alternate 块|合计|
|---|---:|---:|---:|
|新组件|912|25|937|
|替换 WHOLE 占位|105|2|107|
|组件净增|807|23|830|
|材料绑定|2,888|65|2,953|
|接受绑定|2,861|65|2,926|
|隔离绑定|27|0|27|

**新增几何物体 0；新增 E/ν/ρ 数值记录 0。** 937 个组件替换 107 条 WHOLE，占位减少 107，不将区域、Joint、嵌套 Mesh 元数据再计为独立物体。

## 独立核验范围

1. 核 331 个来源文件的官方树路径、提交锁定URL、LFS SHA/大小与冻结字节。
2. 独立解析 own prim 信息，核父刚体 API、自身 mass/inertia、实际 Mesh、精确 collection 或 joint 所有权；不用作者构建器作为真值。
3. 两个 alternate 原文件核 `PXR-USDC` 魔数、官方LFS；核 usdcat 无 flatten 派生文本 SHA。座椅 5 实体/5 Mesh/16 材料区域，焊接站 20 实体/20 Mesh/49 区域。
4. 检查 GeomSubset face indices 唯一、合法、区域互斥并完整覆盖；嵌套 Mesh 的复制物理字段不增加计数。
5. 核材料语义/nonvisual 与原绑定的对应关系；显式 bronze 不被外观 gold/brass/copper 名字覆盖。洗手池源明确 marble，且类别合理；27 paper decal 继续隔离。
6. 标准及 alternate 集合不相交，合并输出恰为并集；旧 WHOLE 恰替换 107，旧对象集不变，未继承数值物性。

## 输入与预览

- 输入：`/Users/hezekai/Documents/博士/上交CS博/项目1：静态场景物理化与实时交互仿真/建表/50_物体优先反向材料库_2026-11-08/data/scaling_release_v1/object_component_inventory.csv`
- 独审输入 SHA-256：`21d5b56f1ad84f75ded31dc6daf62ab677c3bd1584908baea00523364adbf2ae`。
- 封包时当前输入 SHA-256：`21d5b56f1ad84f75ded31dc6daf62ab677c3bd1584908baea00523364adbf2ae`；与独审输入一致：`True`。
- 仅加本包的预览：70,851 状态行、70,802 唯一组件对、43,352 几何对象；SimReady WHOLE 516→409。此为固定基线预览，不宣称父代理并行合并后的发布总数。

## 限制与未扩项

- 材料绑定是官方来源标签及几何范围证据，不是实测 E/ν/ρ。塑料管上的多区域 wood 标签不得推广为整根管材质或细化为树种。
- 原 USDC 和转换 USDA 已冻结，但未冻结全部外链、纹理与运行依赖，不能宣称完整资产可离线运行。
- `prop_cleaning_barSoap_b01/c01` 缺可接受材料标签；`rack_composition_l10` 的 boxes 和 `serviceTool_greaseGun_lever_a01` 的 plungerHead 缺约定的精确 owner 支持，维持原 WHOLE。
- 本独审未改共享账、材料树或网站。父代理应按固定作者 pin 合并并重新校验发布计数。

复核明细：`STANDARD_REVIEW.json`、`ALTERNATE_REVIEW.json`、`COMBINED_REVIEW.json`。可复现脚本：`review_standard.py`、`review_alternate.py`、`review_combined.py`；独立USDA解析器：`independent_usda.py`。
