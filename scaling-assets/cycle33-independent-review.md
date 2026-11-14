# C33 首批资产独立复核

首批允许并入 **6 个来源资产身份：1 个作者传感器 C4D + 5 个 Thorlabs 光学主体 STEP**。每项一行整件几何回退，不增加作者机械分件；不增加三元组，不给物体赋 E/ν/ρ。

## 逐项结论

- 传感器：独立重新下载原始C4D（769431字节）、核SHA/Git blob/native header；实际查看内嵌预览、作者爆炸示意和原型图。是传感器，不是PLA模具。README明确Sylgard184 10:1只用于PDMS封装基体与基底；PARTIAL及五类其他材料归一化义务保留。未解码C4D场景层级，未做网格拓扑或计量验证。
- WG30530 / LA5042 / WG61050 / WG91050 / WG81050：独立官方API将SKU/UUID绑定至相应STEP/PDF；文件SHA与作者冻结包一致；实际查看图纸第1页材料栏，分别为蓝宝石、氟化钙、氟化镁、锗、硅。每份文本实体图含1 MANIFOLD_SOLID_BREP、1 CLOSED_SHELL、0 OPEN_SHELL；未运行CAD内核，不能声称完整几何合法性。
- LA1509 / LA2024 / PL0145：对应N-BK7/N-SF11/N-SF6来源牌号明确，但不能推定SCHOTT供料。另列3个supplier-unspecified名义牌号候选，本首批不并节点或关系。
- LD4650：文件含0 solid /0 closed /1 OPEN_SHELL。保留原件和来源信息，暂缓作为封闭实体就绪资产。

## 去重、许可与边界

对照旧主表71179行/43675物体身份逐条检查对象ID、组件ID、原始URL和已有SHA；十项均无精确命中。作者镜像CdpLab内同一C4D Git blob仅保留别名。9份STEP去名称文本指纹不同，但这不是全球几何等价去重；三个直径25.4×5mm窗口即使名义外形接近也只报告来源身份数，不声称全球独特形状数。

无开源资产转载权获得证明。只发布原厂/作者原链接、SKU、SHA、事实定位；不公开重新分发冻结STEP、PDF、C4D、图纸渲染或作者照片。不把其他厂商材料参数写成Thorlabs商品实测。

IMPORT_links与IMPORT_source_material_relations内容相同，请按现有模型适配，禁止各算一遍。共享主表、树、站点由父agent负责，本包未编辑。其余7个软材料检索路线仍在OTHER_HELD_SOFT_ROUTES，不计新增资产。
