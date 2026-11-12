# Cycle8 YCB 官方几何源新增候选

结论：95个新来源UID候选，全部为整件几何占位；等待独审与root合并。不是95个已下载/内容去重的网格。

## 枚举与差异

官方HTML共有103个有独立行和稳定ID的对象，包括字母后缀积木、套杯和飞机变体；按数字前缀归组是66组。论文的77组、历史估计92行和当前103行不是可互换统计；本包只认冻结HTML逐条103行。
- 96行有真实官方mesh压缩包链接，全部HTTP HEAD200；16行仅Berkeley mesh而无Google16k，不能只解析Google列。
- 7行源明确不能生成mesh（透明/尺寸限制），不增加对象：023_wine_glass, 046_plastic_bolt, 047_plastic_nut, 063-c_marbles, 063-d_marbles, 063-e_marbles, 063-f_marbles。
- 022_windex_bottle虽URL200，源脚注3明确largely distorted，暂缓。
- 余95个稳定UID各一行；多种mesh分辨率/两家扫描不是额外对象。

## 去重与下载

扫描全部当前来源UID、已声明alias、来源链接、archive locator；没有YCB的确切UID或声明别名。商品名相似只进复核提示，不能自动证明相同几何。本包没有下载任何3D payload，SHA明确NOT_DOWNLOADED，不把S3 ETag冒充SHA256，也不声称几何内容去重已完成。

## 材料

主要证据为Dimiccoli等2022原始论文p3人工视觉/触觉表面标注、p4 Fig3/4逐YCB数字ID。保持surface-only范围，复合物多标签为同时表面区域，不创造机械部件；数字组到字母变体的标签为明确标注的合理迁移。
- 76 timer及77 Rubiks不在论文75对象实验，plastic只作合理宽标签，不冒称作者测量。
- 55 baseball论文felt表面标签有合理性疑问，明确保为待复核源标签，不做canonical赋值。
- 不由wood推树种，不由plastic推树脂，不由surface label导出E/ν/ρ。所有canonical均留UNMAPPED供root审，不修改材料树。

## 扩展候选

BOP TLESS/HANDAL/LM官方固定提交API及license已freeze，可后续用ZIP中央目录枚举模型；本包未拿其论文数量造对象。OmniObject3D官方license CC BY4已核，但公开目录枚举需额外登录/取得manifest，6000摘要不计入。

未改共享库存、研究账或网站。
