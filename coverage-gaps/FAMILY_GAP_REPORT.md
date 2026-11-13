# 非流体材料三项覆盖缺口投影

PASS: 3067 canonical nodes audited individually. Exclude only 3 existing LIQUID_WAIVER identities from this campaign denominator; preserve source evidence history.

| 指标键 | 原全库 | 本次非流体范围 |
|---|---:|---:|
| materials | 3067 | 3064 |
| with_complete_group | 1622 | 1622 |
| with_incomplete_group | 1479 | 1479 |
| with_E | 2674 | 2674 |
| with_nu | 1730 | 1730 |
| with_rho | 2418 | 2418 |
| with_all_three_any_sources | 1626 | 1626 |
| without_any_value | 38 | 35 |
| missing_one | 541 | 541 |
| missing_two | 862 | 862 |
| missing_three | 38 | 35 |

完整来源组覆盖率：52.9373%；三项各有来源值覆盖率：53.0679%.

## 范围与保留规则

- Broad and fine canonical nodes coexist; 3064 is a node denominator, not disjoint material species.
- No other explicit fluid/gas identity was identified. Keyword candidates were retained individually in PHASE_TOKEN_REVIEW.csv.
- Ice, hydrogels, liquid-crystal fibers/elastomers, mud/soil, oil-containing solids and gas-pressure-sintered ceramics are retained.
- EmptySpace remains a special non-material domain and was already outside the 3067 denominator.
- Existing family labels are preserved without reclassification. Numerical coverage follows current canonical direct records plus reviewed exact/subtype/true-containment relations.
- No numerical values created, no cross-source complete-group fabrication, no shared files changed.

## 分族缺口汇总

| 家族 | 节点 | 三项都有值 | 仅缺1项 | 缺2项 | 无数值 | 缺E | 缺ν | 缺ρ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| biomaterial | 89 | 16 | 9 | 62 | 2 | 10 | 71 | 58 |
| ceramic | 144 | 121 | 5 | 17 | 1 | 17 | 22 | 3 |
| composite | 54 | 3 | 30 | 21 | 0 | 7 | 27 | 38 |
| foam | 122 | 26 | 26 | 70 | 0 | 71 | 83 | 12 |
| glass | 1015 | 982 | 2 | 31 | 0 | 31 | 30 | 3 |
| leather | 29 | 4 | 10 | 12 | 3 | 8 | 17 | 18 |
| metal | 175 | 149 | 19 | 6 | 1 | 6 | 25 | 3 |
| other_media | 67 | 26 | 3 | 29 | 9 | 37 | 39 | 12 |
| paper | 43 | 16 | 18 | 8 | 1 | 7 | 21 | 9 |
| polymer | 663 | 144 | 323 | 195 | 1 | 44 | 512 | 160 |
| rubber | 147 | 13 | 4 | 130 | 0 | 47 | 127 | 90 |
| stone | 59 | 42 | 7 | 9 | 1 | 2 | 9 | 17 |
| textile | 261 | 30 | 67 | 149 | 15 | 95 | 215 | 100 |
| wood | 196 | 54 | 18 | 123 | 1 | 8 | 136 | 123 |

## 冻结历史资料补项线索

扫描历史冻结交叉表/适配器 511 行；去重后候选补项线索 11 条，以精确节点ID或规范化后完全相同的材料标签定位。它们只是回源队列，尚未批准；旧版重复位置另列日志。

## biomaterial (73 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-FCDB9AFCCEE6E28EE31F | Bacterial cellulose sheet | nu | 0/2 | 1 |
| RESEARCH-MAT-225D98E414A900E09276 | Deacetylated Agaricus bisporus chitosan-beta-glucan sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-A81CF0897F398FF8CCA2 | Deproteinized Agaricus bisporus chitin-beta-glucan sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-49614D1F001656D198EE | Fomitella fraxinea mycelium-based leather, 20% PEG | nu | 0/3 | 1 |
| RESEARCH-MAT-FAD78673BF2BF87DE632 | Fomitella fraxinea mycelium-based leather, Control | nu | 0/3 | 1 |
| RESEARCH-MAT-B5A42698AE426763E4FD | Pleurotuseryngii mycelialnetwork16layer hotpressedfilm,randomhyphae | nu | 0/1 | 1 |
| RESEARCH-MAT-FAC74394C58BE44522C9 | Pleurotuseryngii mycelialnetwork16layer hotpressedfilm,unidirectionalhyphae | nu | 0/1 | 1 |
| RESEARCH-MAT-95629A336F6B9E1FA243 | Untreated human Caucasian scalp hair | nu | 0/1 | 1 |
| RESEARCH-MAT-318016C55F1F70D55754 | Yak belly hair, commercial source | nu | 0/1 | 1 |
| RESEARCH-MAT-F9E8C62B59E9092145A1 | Human scalp hair fibre | nu;rho | 0/5 | 3 |
| RESEARCH-MAT-E748B83CC8CEACD4343E | Agar3.6wt% gel in glycerol/water solvent 0/100 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-19EFE0DB706F2F9C8F60 | Agar3.6wt% gel in glycerol/water solvent 100/0 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DC3D1E5A8B79CDC1C81A | Agar3.6wt% gel in glycerol/water solvent 20/80 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-020714ACC286824EA7E4 | Agar3.6wt% gel in glycerol/water solvent 40/60 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5F156FE2A89961EFBCE4 | Agar3.6wt% gel in glycerol/water solvent 60/40 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1CBDE9C68950FC7482A4 | Agar3.6wt% gel in glycerol/water solvent 80/20 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6CD65B47AF1F02DA2EAF | Agar3.6wt%/talc8.3wt% gel in glycerol/water solvent 0/100 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A4833F411E745541657B | Agar3.6wt%/talc8.3wt% gel in glycerol/water solvent 20/80 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5574369C14DBD8431E0B | Agar3.6wt%/talc8.3wt% gel in glycerol/water solvent 40/60 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CA1ADB65EC31E5F012DF | Agar3.6wt%/talc8.3wt% gel in glycerol/water solvent 60/40 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D5595F052438D72D8219 | Agar3.6wt%/talc8.3wt% gel in glycerol/water solvent 80/20 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D935C414ADB658B2C4DA | Aldehyde-smoke-tanned microbial cellulose biotextile | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A8CA46EA162A1CDB15C9 | As-fabricated microbial cellulose biotextile | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AF7BF9263EAEE8D5A34E | Bleach-damaged human scalp hair fibre repaired with recombinant keratin K31 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-850F14A5BFCD7E0F4A84 | Chitosan-glycerol-keratin composite film | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-58775794ECD3390C365D | Chitosan-keratin composite film | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-13D437864F919648F1B7 | Compression-molded keratin film | nu;rho | 0/1 | 1 |
| MAT-NATURAL-DEAD-LEAF-GRASS-BROAD | Dead leaf/grass plant material, NVIDIA source broad label | E;nu | 0/6 | 1 |
| RESEARCH-MAT-1CAC8A9E6D6B23ACE70E | Dendropanax morbiferus air-dried leaf fragments | E;nu | 0/3 | 1 |
| RESEARCH-MAT-9E3828B67BF899365F0E | Deproteinized Agaricus bisporus chitin-beta-glucan paper yarn | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5C622EBDB6851FA1692D | Diafiltered Australian merino wool keratin film | nu;rho | 0/1 | 1 |
| MAT-NATURAL-DRIED-MOSS-SOURCE-BROAD | Dried moss, species/treatment unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-407457CDE24C0EFCE4F1 | Dry keratin film for ocular-surface reconstruction | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F8AE11151C3141A9999B | Fatsia japonica air-dried leaf fragments | E;nu | 0/3 | 1 |
| RESEARCH-MAT-159D7E6F399627A6DAEF | Fomitella fraxinea cheesecloth-overlayered mycelium-based leather, 15% EG | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C35F2E95A9D87B32245C | Fomitella fraxinea cheesecloth-overlayered mycelium-based leather, 15% G | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-20ADDD571AC160CC0DF9 | Fomitella fraxinea cheesecloth-overlayered mycelium-based leather, 20% PEG | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-557BC102D83A3637AAA1 | Fomitella fraxinea mycelium-based leather, 15% EG | nu;rho | 0/3 | 1 |
| RESEARCH-MAT-7EEFA805F1D9C33206E9 | Fomitella fraxinea mycelium-based leather, 15% EG + 20% corn zein | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5CE4C2B59BAEC67CF723 | Fomitella fraxinea mycelium-based leather, 15% EG + 5% tannic acid | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FA3AD3BDCD4C550D429E | Fomitella fraxinea mycelium-based leather, 15% G | nu;rho | 0/3 | 1 |
| RESEARCH-MAT-0004AACB126BE13BB683 | Fomitella fraxinea mycelium-based leather, 15% G + 5% tannic acid | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0B13451E60217ACE95EB | Ganoderma mycelium membrane, uncrosslinked freeze-thaw FM | E;nu | 0/4 | 1 |
| RESEARCH-MAT-5005F78C54C5C6BBB541 | Gibbon hair fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8E8E773BA7AC4A920601 | Gorilla hair fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-53609DAC23E3EF08BC3E | Human hair cortex intermediate-filament network at SAXS nanoscale | E;rho | 0/1 | 1 |
| RESEARCH-MAT-832B2330C728DB7218F6 | Human hair cuticle short-range ordered lamellar lipid microstructure | E;rho | 0/1 | 1 |
| RESEARCH-MAT-B0332628CD56BBBC4D4A | Lecithin-and-aldehyde-tanned microbial cellulose biotextile | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-71C3A0505774CD3B414A | Lecithin-tanned microbial cellulose biotextile | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3DB5B6EC7E67793F2147 | Loose dried Sphagnum peat-moss particles | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FE65FF96718B8AA3FD64 | Orangutan hair fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2B0EDF6B66C3497C37CD | Porcine aortic tissue | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7ED093E4BCD4EFA38CE1 | Porcine left ventricular myocardium | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7795818EB3359AF0DC14 | Porcine pulmonary artery tissue | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-31ADC3A434E7B1F7AD20 | Porcine right ventricular myocardium | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F011125D6D0E4D2FC3EF | Rhizopus delemar CBS145940 fungal sheet, Chestnut tanned sandwich composite with AIM | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1B64625032BF312E87E3 | Rhizopus delemar CBS145940 fungal sheet, Chestnut tanned sandwich composite with AIM post-treated with glycerol | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5CF0923D9EBFCE129FBD | Rhizopus delemar CBS145940 fungal sheet, Chestnut tanned sandwich composite with AIM post-treated with glycerol and bio-based binder (OrganoClick Lotus binder) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0603F0EF7537816E65CA | Rhizopus delemar CBS145940 fungal sheet, Chestnut tanned single layer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9AA5B1DB2334C4C42DB0 | Rhizopus delemar CBS145940 fungal sheet, Indusol ATO tanned sandwich composite with AIM | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D88CA59BB0CEE1DC5376 | Rhizopus delemar CBS145940 fungal sheet, Indusol ATO tanned sandwich composite with AIM post-treated with glycerol | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1C46CAA035057B1F6185 | Rhizopus delemar CBS145940 fungal sheet, Indusol ATO tanned sandwich composite with AIM post-treated with glycerol and bio-based binder (OrganoClick Lotus binder) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-02C3E78264A57EDD3924 | Rhizopus delemar CBS145940 fungal sheet, Indusol ATO tanned single layer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FB141C53E7F840059FA7 | Rhizopus delemar CBS145940 fungal sheet, Myrobalan tanned sandwich composite with AIM | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-28A687DD0C7EB2AE1DBA | Rhizopus delemar CBS145940 fungal sheet, Myrobalan tanned sandwich composite with AIM post-treated with glycerol | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7E79C2A57EA58E13F579 | Rhizopus delemar CBS145940 fungal sheet, Myrobalan tanned sandwich composite with AIM post-treated with glycerol and bio-based binder (OrganoClick Lotus binder) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-75E5B8E24C7567662D62 | Rhizopus delemar CBS145940 fungal sheet, Myrobalan tanned single layer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BFCE96CA864E435175E9 | Rhizopus delemar CBS145940 fungal sheet, Tara tanned sandwich composite with AIM | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7213F3714A800E398E2A | Rhizopus delemar CBS145940 fungal sheet, Tara tanned sandwich composite with AIM post-treated with glycerol | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A9CB6735EADA20DF9E8A | Rhizopus delemar CBS145940 fungal sheet, Tara tanned sandwich composite with AIM post-treated with glycerol and bio-based binder (OrganoClick Lotus binder) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-926D173F66B76E69E27F | Rhizopus delemar CBS145940 fungal sheet, Tara tanned single layer | nu;rho | 0/1 | 1 |
| SOURCE-MAT-4A827ED8F19132725B5D | Twinface sheepskin — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-60D9636AD9C377CDF07F | sheepskin — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## ceramic (23 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-6274C48DC53D7F9B31BC | Calcite CaCO3 | nu | 0/1 | 1 |
| RESEARCH-MAT-4415F1768AAFF655B466 | Crystal Quartz SiO2 | nu | 0/1 | 1 |
| RESEARCH-MAT-E0BD959ED6BA293D5639 | Potassium Iodide KI | nu | 0/1 | 1 |
| RESEARCH-MAT-85C23A3BD4DB22C53827 | Rutile TiO2 | E | 0/1 | 1 |
| RESEARCH-MAT-1531E718309E6F318114 | Silver Bromide AgBr | nu | 0/1 | 1 |
| MAT-EARTHENWARE-BROAD | Earthenware, composition/firing unspecified | E;nu | 0/24 | 1 |
| RESEARCH-MAT-A8D3B3B7756EE91F786B | Ferro Ground Coat A vitreous porcelain enamel | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-17FD11A5F08A454E76D6 | Fired Gashiga pit 1, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-2884C6995BA8FE22B4F8 | Fired Gashiga pit 2, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-8CEC063889C175842F0B | Fired Gashiga pit 3, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-051A7F1F21EF8144CAD8 | Fired Sekandé pit 1, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-5A1CCF5D28FF2E385805 | Fired Sekandé pit 1, clayey layer C3 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-960D4A55085686937032 | Fired Sekandé pit 2, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-BCD4696224DFB85A3453 | Fired Sekandé pit 3, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-F3E1717CE6ACA9AF2F73 | Fired Sekandé pit 4, clayey layer C2 earthenware | E;nu | 0/3 | 1 |
| RESEARCH-MAT-261C9644AB8846456C41 | Lanthanum Fluoride LaF3:Eu3+ | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8BB68E90D14FF2AF8BA2 | Lead Fluoride (PbF2) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C8A96240CB82F54703FB | PAROC Ultra mineral wool | E;nu | 0/1 | 1 |
| RESEARCH-MAT-729E355EAFF5815663BD | Rubidium Bromide RbBr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-699518E3D784FD3A5A19 | Rubidium Chloride RbCl | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B56F5D5540779725F223 | Rubidium Iodide RbI | E;nu | 0/1 | 1 |
| RESEARCH-MAT-455F20BDE34D35D918EB | Son2015 fired mixed-oxide porcelain enamel prepared from frit | nu;rho | 0/1 | 1 |
| SOURCE-MAT-A99EEA820F3B6552019A | ceramic coating — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## composite (51 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-44CC3DD28717CE9558F5 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0245) | rho | 0/1 | 1 |
| RESEARCH-MAT-28C8518316706FF92067 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0482) | rho | 0/1 | 1 |
| RESEARCH-MAT-27685E17A13557AED7DF | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0494) | rho | 0/1 | 1 |
| RESEARCH-MAT-59166C108DA08F9985AE | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0495) | rho | 0/1 | 1 |
| RESEARCH-MAT-29CFA2C3E27BA6055C51 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0498) | rho | 0/1 | 1 |
| RESEARCH-MAT-59EB1DC915369242C7CF | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0701) | rho | 0/1 | 1 |
| RESEARCH-MAT-5CD19F29B2EE980E0789 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0985) | rho | 0/1 | 1 |
| RESEARCH-MAT-556E462AE874DF6C5624 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.0993) | rho | 0/1 | 1 |
| RESEARCH-MAT-52B7EC3566AAA7E54722 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.1477) | rho | 0/1 | 1 |
| RESEARCH-MAT-C7FE800CE278F590FBEA | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.1494) | rho | 0/1 | 1 |
| RESEARCH-MAT-B127F9F693C35424614C | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.1965) | rho | 0/1 | 1 |
| RESEARCH-MAT-19A495E1E24482038BDE | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.1983) | rho | 0/1 | 1 |
| RESEARCH-MAT-FCB4D44983C1B1FFF0F1 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.1992) | rho | 0/1 | 1 |
| RESEARCH-MAT-E98194647652AA5E3A2A | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.2251) | rho | 0/1 | 1 |
| RESEARCH-MAT-90412B5139383284735F | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.2486) | rho | 0/1 | 1 |
| RESEARCH-MAT-27F4EF1D79E5B3748E97 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.2980) | rho | 0/1 | 1 |
| RESEARCH-MAT-2417DADE79936540D649 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.2988) | rho | 0/1 | 1 |
| RESEARCH-MAT-E198F6A6EF1C4BB11B5A | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.3025) | rho | 0/1 | 1 |
| RESEARCH-MAT-1AAFF44F31376AF64218 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.3480) | rho | 0/1 | 1 |
| RESEARCH-MAT-8CB78C137730D3E8E7DA | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.3960) | rho | 0/1 | 1 |
| RESEARCH-MAT-CCAE747222A607034CCE | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.4015) | rho | 0/1 | 1 |
| RESEARCH-MAT-68FC0E65AC406B2B209A | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.4513) | rho | 0/1 | 1 |
| RESEARCH-MAT-FA69585FC066CA4D10A0 | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.4960) | rho | 0/1 | 1 |
| RESEARCH-MAT-60535E7B8470F38E9B4F | DGEBA DER-332/TETA epoxy with Cataphote No. 4000 soda-lime optical-crown glass spheres (phi=.4981) | rho | 0/1 | 1 |
| RESEARCH-MAT-CF728D311739ABA7A28C | PVAc-bonded coffee-filter-paper/date-palm-surface-fibre composite board, dried mass 23.2/69.4/7.4 wt% (paper/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-5DC5CB1F80E4D580149A | PVAc-bonded coffee-filter-paper/date-palm-surface-fibre composite board, dried mass 46/46/8.0 wt% (paper/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-EE47A93750D8EFED3C28 | PVAc-bonded coffee-filter-paper/date-palm-surface-fibre composite board, dried mass 65.6/21.9/12.5 wt% (paper/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-1ACB9251BB97F624B4CD | PVAc-bonded polypropylene medical-isolation-gown/date-palm-surface-fibre composite board, dried mass 21.8/65.2/13 wt% (gown/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-AD7E742FFA88EF77AE32 | PVAc-bonded polypropylene medical-isolation-gown/date-palm-surface-fibre composite board, dried mass 45.9/45.9/8.2 wt% (gown/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-56BBAEE575CEFEEA335C | PVAc-bonded polypropylene medical-isolation-gown/date-palm-surface-fibre composite board, dried mass 58.3/19.4/22.3 wt% (gown/fibre/binder) | nu | 0/1 | 1 |
| RESEARCH-MAT-2A5DAB782A3940DCC5F9 | 08PS low-carbon steel with EUROPOLVERI epoxy-polyester powder coating | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-9D41109C8CEBB727E4DC | 50:50 PP/PET needle-punched thermoformed nonwoven composite laminate | nu;rho | 0/7 | 1 |
| RESEARCH-MAT-8D14C2F3924E9168E166 | 89wt%SasolWax0907 microcrystalline wax +10wt%SEBS-MA +1wt%carbon black fuel formulation | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FF97568BF0BDFCA1C4BE | 94wt%SasolWax0907 microcrystalline wax +5wt%SEBS-MA +1wt%carbon black fuel formulation | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4DA51BA0E32CF22D6461 | 99wt%SasolWax0907 microcrystalline wax +1wt%carbon black fuel formulation | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F602F095B94D1829157E | CF/PEEK honeycomb skeleton H22-t0.6-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E5A644ECF794F9426F1E | CF/PEEK honeycomb skeleton H26-t0.6-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EB35A466CBFF4B8A479D | CF/PEEK honeycomb skeleton H26-t0.8-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C00A363BA1C72A3E79F0 | CF/PEEK honeycomb skeleton with TPU skin MH22-t0.6-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8B59138A9F3404A8BB3A | CF/PEEK honeycomb skeleton with TPU skin MH26-t0.6-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BF62FED0CCDAE2DBEA50 | CF/PEEK honeycomb skeleton with TPU skin MH26-t0.8-T | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5D3A7A73F7F680E07A5D | Green kiwi peel/PVP/polyglycerol leather-like film | nu;rho | 0/10 | 1 |
| RESEARCH-MAT-73398C9F6A9716415462 | Orthotic interface layer: neoprene sheet with retained cotton surface and residual adhesive | nu;rho | 0/1 | 1 |
| MAT-STEEL-POWDER-COATED-BROAD | Powder-coated steel, steel/coating unspecified | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-0C1330924497A49B4F5A | Rigid-polyurethane-bonded agglomerated cork, 12wt% binder | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9DFD57B4AE2B627DB3E3 | Rigid-polyurethane-bonded agglomerated cork, 14wt% binder | E;nu | 0/1 | 1 |
| RESEARCH-MAT-46B9010E96377B0E2042 | Rigid-polyurethane-bonded agglomerated cork, 15wt% binder | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D54977E7D1943BB4D3D5 | Silicone-urethane hybrid foam SUF125 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-ADD363AFB7D42D448DBB | Silicone-urethane hybrid foam SUF137 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FCD2F80FF2B180B6F848 | Silicone-urethane hybrid foam SUF150 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F03659F82C3C343B06E7 | Silicone-urethane hybrid foam SUF200 | E;nu | 0/1 | 1 |

## foam (96 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| MAT-FOAM-MEMORY-BROAD | Memory foam, polymer/density unspecified | nu | 0/3 | 2 |
| RESEARCH-MAT-032B19B3F4B522FBE8D8 | Cardanol-Mannich GX9104/SUPRASEC2085 polyurethane foam, cellulose5wt% | nu | 0/1 | 1 |
| RESEARCH-MAT-EB5CE4C2EB07DB1BFD99 | Cardanol-Mannich GX9104/SUPRASEC2085 polyurethane foam, diatomite5wt% | nu | 0/1 | 1 |
| RESEARCH-MAT-BD2F11BD455A5D78F30D | Cardanol-Mannich GX9104/SUPRASEC2085 polyurethane foam, unfilled | nu | 0/1 | 1 |
| RESEARCH-MAT-F00A50F2C94323D8BE2D | Cardanol-Mannich GX9104/SUPRASEC2085 polyurethane foam, walnutshell5wt% | nu | 0/1 | 1 |
| RESEARCH-MAT-EA0B4613D6F605F4725D | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.50/0.20/0.30 | nu | 0/1 | 1 |
| RESEARCH-MAT-87A8ED5BA181E4800BD7 | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.50/0.30/0.20 | nu | 0/1 | 1 |
| RESEARCH-MAT-9C83D38CF34CA7C94E24 | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.50/0.40/0.10 | nu | 0/1 | 1 |
| RESEARCH-MAT-2F60FB9618AF9DB2E992 | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.55/0.30/0.15 | nu | 0/1 | 1 |
| RESEARCH-MAT-A2ED9B5E04F3D9198A76 | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.55/0.40/0.05 | nu | 0/1 | 1 |
| RESEARCH-MAT-CB8A94E8F7F7E9976610 | Castor-oil polyurethane foam Imperveg RD70A/RD70B/AGT1315B, mass fractions 0.60/0.40/0.00 | nu | 0/1 | 1 |
| RESEARCH-MAT-A944408A956133ACA2FB | MM2520 thermoplastic polyurethane/Ecoflex closed-cell foam,30wt%Ecoflex5wt%azodicarbonamide | nu | 0/1 | 1 |
| RESEARCH-MAT-BEF146034A2AC8123328 | Polyurethane foam PUR_A filled with titanium dioxide (9.78 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-05B1A49746F58152F8E9 | Polyurethane foam PUR_B filled with titanium dioxide (7.52 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-DCB371E293E7DC1014F3 | Polyurethane foam PUR_C filled with titanium dioxide (7.53 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-D2AC7864A4A6AD0BF83D | Polyurethane foam PUR_D filled with calcium carbonate (8.85 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-45AECE34611AF355D00B | Polyurethane foam PUR_E filled with calcium carbonate (7.78 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-AD8080CA36F8410623ED | Polyurethane foam PUR_F filled with calcium carbonate (7.52 wt% as reported) | nu | 0/1 | 1 |
| RESEARCH-MAT-B32B17E55E05DF040690 | Polyurethane foam formulation EP_01: {"Polyol POPE": 62.58, "PMDI": 32.29, "Glycerin GCO": 1.38, "Dichloromethane": 0.74, "Catalyst": 0.93, "Silicone HS": 0.83, "PEG": 1.25, "Bentonite": 0, "Alumina": 0} | E | 0/1 | 1 |
| RESEARCH-MAT-F9A062FEECE13EDEBF1D | Polyurethane foam formulation EP_03: {"Polyol POPE": 58.44, "PMDI": 26.26, "Glycerin GCO": 2.15, "Dichloromethane": 0, "Catalyst": 1.251, "Silicone HS": 1.469, "PEG": 0, "Bentonite": 10.43, "Alumina": 0} | E | 0/1 | 1 |
| RESEARCH-MAT-AF96A458655AA112248D | Polyurethane foam formulation EP_04: {"Polyol POPE": 62.17, "PMDI": 29.49, "Glycerin GCO": 2.29, "Dichloromethane": 0, "Catalyst": 0.97, "Silicone HS": 1.56, "PEG": 0, "Bentonite": 3.52, "Alumina": 0} | E | 0/1 | 1 |
| RESEARCH-MAT-319FD47A703396DF9D3C | Polyurethane foam formulation EP_06: {"Polyol POPE": 65.94, "PMDI": 26.61, "Glycerin GCO": 1.015, "Dichloromethane": 0.82, "Catalyst": 1.74, "Silicone HS": 2.765, "PEG": 1.11, "Bentonite": 0, "Alumina": 0} | E | 0/1 | 1 |
| RESEARCH-MAT-FC9156ABCEBD6E8F73E8 | Sawbones closed-cell rigid polyurethane foam PCF10 | nu | 0/1 | 1 |
| RESEARCH-MAT-87344072ACE3B6E6E2D8 | Sawbones closed-cell rigid polyurethane foam PCF25 | nu | 0/1 | 1 |
| RESEARCH-MAT-F09482207399BEBA84B5 | Sawbones closed-cell rigid polyurethane foam PCF40 | nu | 0/1 | 1 |
| RESEARCH-MAT-18089445AF935A4A855A | Vitafoam Vasco40 open-cell urethane memory foam | nu | 0/2 | 1 |
| RESEARCH-MAT-75F70A23724BE04B4C4B | Dunlop natural rubber latex cushion foam net with 10.0phr bamboo-leaf fibre | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CE7441279A3CA36A15E7 | Dunlop natural rubber latex cushion foam net with 2.5phr bamboo-leaf fibre | E;nu | 0/1 | 1 |
| RESEARCH-MAT-44E6DB5F914D8A40D9AD | Dunlop natural rubber latex cushion foam net with 5.0phr bamboo-leaf fibre | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F32F03BE81C0AFBEF4BF | Dunlop natural rubber latex cushion foam net with 7.5phr bamboo-leaf fibre | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C0273F8FEAE752D821A8 | Dunlop natural rubber latex cushion foam net without bamboo-leaf filler | E;nu | 0/1 | 1 |
| RESEARCH-MAT-393B3E6831DEA81E36EF | Expanded polyethylene cushion foam net | E;nu | 0/1 | 1 |
| RESEARCH-MAT-486E73A515819250698D | FlexFoam-iT III polyurethane foam | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7407C5F6E2C6DC5EE83C | FlexFoam-iT IIIV polyurethane foam (UF*) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8938E02D74A786278C0C | Flexible lignin/castoroil-reagent non-isocyanate polyurethane foam NIPU A | E;nu | 0/1 | 1 |
| RESEARCH-MAT-52D5771798AE6CD68244 | Flexible lignin/castoroil-reagent non-isocyanate polyurethane foam NIPU B | E;nu | 0/1 | 1 |
| RESEARCH-MAT-755E90A10BFAC5AB7988 | Flexible lignin/castoroil-reagent non-isocyanate polyurethane foam NIPU C | E;nu | 0/1 | 1 |
| RESEARCH-MAT-DDB4BAEF6F78D37E72F7 | Flexible one-shot pMDI/polyol reference foam sourceOH163.2/NCO29.8% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BEAE5A1FA812396AB7CB | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 0pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F3EF1E7B11FC55A8CCD4 | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 1pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-2871ED6513E208E1D4EC | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 2pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-26F8A6EF8C65B9AB0C6D | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 3pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BABED8D57C5675321414 | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 4pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CD770C3EBD3F52C0F60B | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 5pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C4F9F09C598E79A80CA7 | Flexible polyurethane foam KonixKE1990/TDI with sugarcane-bagasse 6pphp | E;nu | 0/1 | 1 |
| RESEARCH-MAT-86A7E6A5CE609F58D6CF | Flexible polyurethane foam from ethanol-opened waste-cooking-oil polyol PO1 and Desmodur CQ N7300, 133.2g isocyanate per100g polyol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CFA56E7996B8096E85FF | Flexible polyurethane foam from ethanol-opened waste-cooking-oil polyol PO2 and Desmodur CQ N7300, 123.5g isocyanate per100g polyol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-973D985101928557014C | Flexible polyurethane foam from ethanol-opened waste-cooking-oil polyol PO3 and Desmodur CQ N7300, 119.4g isocyanate per100g polyol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-199E2285B561B21B55C8 | Flexible polyurethane foam uncoatedsourcecontrol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9EB9BE395A575A972519 | Flexible polyurethane foam with poly(acrylic acid) coating recipe PUF/1P, no sepiolite | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1C1220E33C60F98915EC | Flexible polyurethane foam with poly(acrylicacid)/sepiolite coating recipe PUF/1P1S | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7141B9B8BCF26CE319A4 | Flexible polyurethane foam with poly(acrylicacid)/sepiolite coating recipe PUF/1P2S | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E05BAEA737A614A21AEF | Flexible polyurethane foam with poly(acrylicacid)/sepiolite coating recipe PUF/1P3S | E;nu | 0/1 | 1 |
| RESEARCH-MAT-00C3D1151158D8AB528E | Flexible polyurethane foam with poly(acrylicacid)/sepiolite coating recipe PUF/1P4S | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7B372A3B17DF11E92032 | Flexible polyurethane foam with poly(acrylicacid)/sepiolite coating recipe PUF/1P5S | E;nu | 0/1 | 1 |
| RESEARCH-MAT-A9241E7673EE1DCE3432 | Foam-formed driedcellulosefibrous cushion,eucalyptus bleachedhardwood | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F4675C1FB15607093BD7 | Foam-formed driedcellulosefibrous cushion,eucalyptus bleachedhardwood,guargum0.5% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1D313E9DEC2162787A37 | Foam-formed driedcellulosefibrous cushion,pine bleachedsoftwoodkraft | E;nu | 0/1 | 1 |
| RESEARCH-MAT-76FB4695BF76DDDF009E | Foam-formed driedcellulosefibrous cushion,pine bleachedsoftwoodkraft,guargum0.5% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-395005A3A8F0A47C5C31 | Foam-formed driedcellulosefibrous cushion,pine/eucalyptus50:50 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7CD8C80805B65C9936B8 | Foam-formed driedcellulosefibrous cushion,pine/eucalyptus50:50,carboxymethylcellulose0.5% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8FE0CDDBDE96423A675E | Foam-formed driedcellulosefibrous cushion,pine/eucalyptus50:50,carboxymethylcelluloseandcitricacid | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7AAEAB05024077934059 | Foam-formed driedcellulosefibrous cushion,pine/eucalyptus50:50,citricacid1% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C5277695574B9E519648 | Foam-formed driedcellulosefibrous cushion,pine/eucalyptus50:50,guargum0.5% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E266006E1EE482E18C63 | MM2520 TPU/Ecoflex closed-cell foam,30wt%Ecoflex5wt%azodicarbonamide,TPU/Ecoflex/carbonblack coating | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E015D6FA44EF0674DA93 | Natural rubber latex foam reinforced with eucalyptus microfibrillated cellulose | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D6E3C2E5E3C6850D287C | Natural rubber latex foam with20phr bacterial nanofibrillated cellulose | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7D525E918BF93C25BA8E | Natural-rubber latex foam with 2 phr Aerosil 200 hydrophilic fumed silica | E;nu | 0/1 | 1 |
| RESEARCH-MAT-46CFD4012D0E6163B608 | Natural-rubber latex foam with 2 phr Aerosil R972 hydrophobic silica | E;nu | 0/1 | 1 |
| RESEARCH-MAT-2C90144F97D98F72B45C | Natural-rubber latex foam with 2 phr Reolosil DM30 hydrophobic fumed silica | E;nu | 0/1 | 1 |
| RESEARCH-MAT-84F219D437669BB726D1 | Natural-rubber latex foam with 2 phr Sipernat 22S precipitated silica | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CD4CC3BE2F9565067465 | Natural-rubber latex foam with no silica | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7A976AA0CFA56C85F4F7 | PEG400/PAPI flexiblepolyurethanefoam,water1.5gper100gPEG400 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-A70FDE509662EB7E2CD7 | PEG400/PAPI flexiblepolyurethanefoam,water2.5gper100gPEG400 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8F3FF0207490FA438DBA | PEG400/PAPI flexiblepolyurethanefoam,water2gper100gPEG400 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B08ABAAD389C054B0D9F | PEG400/PAPI flexiblepolyurethanefoam,water2gper100gPEG400,MTMSchemicalvapordepositedsiloxanesurfacelayer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DFCEE1F8B034C66F68DF | Polyurethane foam formulation EP_02: {"Polyol POPE": 59.09, "PMDI": 24.87, "Glycerin GCO": 2.19, "Dichloromethane": 0, "Catalyst": 1.25, "Silicone HS": 2.08, "PEG": 0, "Bentonite": 10.52, "Alumina": 0} | E;nu | 0/1 | 1 |
| RESEARCH-MAT-DFAB64E9C150D8610B5B | Polyurethane foam formulation EP_05: {"Polyol POPE": 58.83, "PMDI": 24.09, "Glycerin GCO": 2.28, "Dichloromethane": 1.24, "Catalyst": 1.89, "Silicone HS": 1.14, "PEG": 0, "Bentonite": 0, "Alumina": 10.53} | E;nu | 0/1 | 1 |
| RESEARCH-MAT-070F74244137E5E5839E | Polyurethane polishing foam with 1wt% ammonium bicarbonate secondary blowing agent | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D5886FF16006995B8ADC | Polyurethane polishing foam with 3wt% sodium bicarbonate secondary blowing agent | E;nu | 0/1 | 1 |
| RESEARCH-MAT-4C9A9ABE33E7F0F0A777 | Polyurethane polishing foam without inorganic secondary blowing additive | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3D428D0C4714BBC0A370 | Recycled polyurethane foam | E;nu | 0/5 | 1 |
| RESEARCH-MAT-794EB91A398A57D93F4C | Reduced graphene oxide-polypyrrole-polyurethane dispersion aerogel | E;rho | 0/1 | 1 |
| RESEARCH-MAT-BBEBD725A0B278B5BBED | Reduced graphene oxide-polypyrrole-polyurethane dispersion aerogel,biaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-DECF07F64030CD02FC1B | Reduced graphene oxide-polypyrrole-polyurethane dispersion aerogel,triaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-E9B11BC393D57F5C7774 | Reduced graphene oxide-polypyrrole-polyurethane dispersion aerogel,uniaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-64955DEB7AB11222A2A0 | Reduced graphene oxide-polypyrrole-polyurethane foam1 aerogel | E;rho | 0/1 | 1 |
| RESEARCH-MAT-E68BAEB09C52DDD9D100 | Reduced graphene oxide-polypyrrole-polyurethane foam1 aerogel,biaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-5F8379F0BF21BA74EF2C | Reduced graphene oxide-polypyrrole-polyurethane foam1 aerogel,triaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-631A8B113DF29FDAD643 | Reduced graphene oxide-polypyrrole-polyurethane foam1 aerogel,uniaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-DAE15E95D905CC4D777A | Reduced graphene oxide-polypyrrole-polyurethane foam2 aerogel,uniaxially hot-pressed | E;rho | 0/1 | 1 |
| RESEARCH-MAT-A60936225216D10A7E99 | RokopolF3600/Ongronat1080 flexibleopen-cellpolyurethanefoam,halloysitenanofiller5php | E;nu | 0/1 | 1 |
| RESEARCH-MAT-31F14AD59B553F541042 | RokopolF3600/Ongronat1080 flexibleopen-cellpolyurethanefoam,unfilledcontrol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-DA0B405C5B5A80EDAD85 | Unfilled natural rubber latex foam | E;nu | 0/1 | 1 |
| RESEARCH-MAT-77C30E01E2BD1614B74B | Vacuum/mechanically processed Nylon6 closed-cell foam | E;nu | 0/8 | 1 |
| RESEARCH-MAT-9A6831B42C76955197CE | Viscoelastic polyurethane foam vPU-REF without biopolyol | E;nu | 0/1 | 1 |

## glass (33 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-E1B61A4878FF05350395 | Chelli SM005 fired vitreous enamel coating | rho | 0/1 | 1 |
| RESEARCH-MAT-40BDF446AD2BAA6F3410 | Chelli SM006 fired vitreous enamel coating | rho | 0/1 | 1 |
| RESEARCH-MAT-324381402B19C64CA97B | CDGM H-LaK72 optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-22D3E6A701986E001BB7 | CDGM H-TF21 optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-349C31B73C503E508FBE | CDGM H-TF29 optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-48BC792154F519D530BD | CDGM H-TF8B optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FCE7096104D03A7C52B3 | CDGM H-ZF86 optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EB344BB4A9A3C354E149 | CDGM H-ZLaF68NB optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BFA0378EF5BB22622CDC | CDGM H-ZLaF92A optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-ED0AFAEDB0CF0BBDAA2F | CDGM QF70GFi optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-5123AFD49EFF807626DC | CDGM QF71GTi optical glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6D4A480A8FF150268B93 | Chain acid-etched frosted decorative glass product family | E;nu | 0/1 | 1 |
| RESEARCH-MAT-0F5C07E94A749B1A7590 | Chain silver-reflective and protective-paint-backed float-glass mirror product family | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EE4BEC88226A5CB0DF73 | Chelli SM002 fired vitreous enamel coating, density-table identity | E;nu | 0/1 | 1 |
| RESEARCH-MAT-03C7CD20782C452A7B51 | Chelli SM003 fired vitreous enamel coating, density-table identity | E;nu | 0/1 | 1 |
| MAT-FROSTED-GLASS-BROAD | Frosted glass, composition/treatment unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-137E1373FFEC9FA044F9 | Matsunami 307 Borosilicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9F7C3410648BC23BAEBC | Matsunami 801 Borosilicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EE08B9D70A467621E907 | Matsunami BS12 Phosphoric glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E5DC3353691DC0FC49F2 | Matsunami BS12-4B Phosphate type glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BCDE185374DC0E1EDEDA | Matsunami BS4 Phosphoric glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-56FBCDBF8BB1568F44A9 | Matsunami BS7 Phosphoric glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B246AC64E4767D191235 | Matsunami BZ-5 Bismuth-Silicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-86452343E303BC602F77 | Matsunami BZ-5D Bismuth-Silicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-52C3C8FFD1F0E8148280 | Matsunami CT-6 SiO2-Al2O3-Y2O3 glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8FAE4E53474444DE03FE | Matsunami D150 Silicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F9E923CFEE660E2ECE26 | Matsunami IR584-13α Phosphoric glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3D4DF21A83167FF08557 | Matsunami IR585 Phosphoric glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-054C54594DF3178162FE | Matsunami LG1000 Silicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1DCC1E6219AC2F9643C9 | Matsunami M-360G Silicate glass | E;nu | 0/1 | 1 |
| RESEARCH-MAT-4D2B33C88FE70FDEE906 | Matsunami ND13-4 Silicate glass | E;nu | 0/1 | 1 |
| MAT-MIRROR-BROAD | Mirror material, substrate/reflective layer unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F4282B46D605771E34B4 | Soda glass, composition/production unspecified | E;rho | 0/1 | 1 |

## leather (25 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| MAT-LEATHER-PU-SYNTHETIC | Polyurethane synthetic leather, construction unspecified | rho | 0/2 | 2 |
| MAT-LEATHER-SYNTHETIC-BROAD | Synthetic leather, polymer/construction unspecified | rho | 0/3 | 2 |
| RESEARCH-MAT-D88C74F1F80CB00B399F | Calfskin leather and chrome-tanned sheep leather lining assembly | rho | 0/9 | 1 |
| RESEARCH-MAT-C52EF58D767C00795365 | Calfskin leather and polyester knitted lining assembly | rho | 0/9 | 1 |
| RESEARCH-MAT-F19135568423DDB50030 | Calfskin upper leather | rho | 0/9 | 1 |
| RESEARCH-MAT-71BDB1C0000C345F3331 | Dorsal goat-hide leather, chrome tanned | nu | 0/3 | 1 |
| RESEARCH-MAT-13F958F23CE7ECC0C726 | Dorsal goat-hide leather, vegetable tanned | nu | 0/3 | 1 |
| RESEARCH-MAT-3A460413C8C0545616D9 | Synthetic leather: 81.25% flexible PVC matrix + 13.75% polyester knitted fabric + 5% organic constituents | rho | 0/1 | 1 |
| RESEARCH-MAT-ACB9302D60CCC296E5F3 | Synthetic leather: 88.671% flexible polyurethane matrix + 11.328% polyester knitted fabric | rho | 0/1 | 1 |
| MAT-LEATHER-VINYL-SYNTHETIC-BROAD | Vinyl faux leather, substrate/construction unspecified | rho | 0/1 | 1 |
| RESEARCH-MAT-222F521A5A3FEC34486C | BLEDA Salpa pressed natural-leather-fibre and binder composite | E;nu | 0/1 | 1 |
| MAT-LEATHER-BONDED-BROAD | Bonded leather, composition unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-647973332A319859707E | Chrome-tanned cattle hide leather,pickling 2% pTsOH | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1F8BA92B0E91804975CB | Chrome-tanned cattle hide leather,pickling Control | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-01BE47359AC8A8879861 | Commercial synthetic polyurethane leather, construction unspecified | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-83E7E1CC3613C4ACD04E | Direct-dried camel rawhide | E;nu | 0/1 | 1 |
| RESEARCH-MAT-526AED933EC8C842A203 | Leather comparison specimen, tanning unspecified | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8A11CA01BBA33EDF5332 | Simmental bovine reticular-layer leather, metal-free vegetable tanned, non-dyed | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-D0DD7F3E8DCEA7E0AE0D | Synthetically tanned bovine reticular-layer leather | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-34B8BDF54465622799FB | Vegetable-tanned bovine reticular-layer leather collection, Simmental and zebu | E;nu | 0/1 | 1 |
| RESEARCH-MAT-5F41BA7F594BA436F91C | Wet-blue leather-waste fibres,source chromium-tanned batch | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D38CA42DD298FAD393DF | Zebu bovine reticular-layer leather, metal-free vegetable tanned, non-dyed | nu;rho | 0/3 | 1 |
| SOURCE-MAT-F634E6F2E8FA1662BFEA | full-grain leather — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-8A028E07CA77C88C6217 | nubuck leather — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-7D9FDA3D773C9610A031 | top-grain Italian leather — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## metal (26 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-928D4550E6CCB52CE392 | 304/304L/304H stainless steel source group | nu | 0/1 | 1 |
| RESEARCH-MAT-4E5B0321E3619D1B50E4 | Aluminum 6061-T6/T651 sheet coil and plate | nu | 0/1 | 1 |
| RESEARCH-MAT-D0D51D25B1EF006B4406 | Aurubis C11000 / Cu-ETP | nu | 0/1 | 1 |
| RESEARCH-MAT-40E12A8FAD8D6F684303 | Brenner1948 electrodeposited chromium | nu | 0/6 | 1 |
| RESEARCH-MAT-2C78F60762E7EC363BC3 | Cast iron, grade 20 | nu | 0/1 | 1 |
| RESEARCH-MAT-378125C089FBCDA8AC01 | EN-GJL-250 / KIPP cast iron | nu | 0/1 | 1 |
| RESEARCH-MAT-649E77408AA048BEBE08 | KME C11000 / Cu-ETP | nu | 0/1 | 1 |
| RESEARCH-MAT-AEE76768AB24D849B7AD | Outokumpu Core 304 / 1.4301 | nu | 0/1 | 1 |
| RESEARCH-MAT-7B34B392E7077F1729FA | Stainless steel 2205 | nu | 0/1 | 1 |
| RESEARCH-MAT-FABD02AA97599D2C8CB1 | Stainless steel 304 | nu | 0/2 | 1 |
| RESEARCH-MAT-684C319B51BDD22197BD | Stainless steel 316 | nu | 0/2 | 1 |
| RESEARCH-MAT-FF44631D7FB5B55B2821 | Stainless steel 410 | nu | 0/2 | 1 |
| RESEARCH-MAT-2C8564272982B35BD4A9 | Stainless steel 410S | nu | 0/2 | 1 |
| RESEARCH-MAT-46F8BBBF998F661011B4 | Stainless steel 430 | nu | 0/2 | 1 |
| RESEARCH-MAT-BE4FC6A8C4DF975C57B9 | Stainless steel 440 | nu | 0/2 | 1 |
| RESEARCH-MAT-709A432756971819F284 | Stainless steel 444 | nu | 0/2 | 1 |
| RESEARCH-MAT-73CAF21C8EB8F4273879 | Stainless steel 6%Mo | nu | 0/2 | 1 |
| RESEARCH-MAT-36A3AEBE18D967B4BD67 | Stainless steel 630 | nu | 0/2 | 1 |
| MAT-SS-304-ANNEALED | Type 304 stainless steel, annealed, room-temperature reference | nu | 0/1 | 1 |
| MAT-PEWTER-BROAD | Pewter, composition unspecified | E;nu | 0/2 | 2 |
| RESEARCH-MAT-1E779E0A8E5D9B9A73BB | 18-8 stainless steel | E;rho | 0/1 | 1 |
| RESEARCH-MAT-B9B527138B306205C7D4 | Belmont Britannia Alloy, Sn91.75-Sb8-Cu0.25wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-68E72E75A2D26DA5C39D | Electrodeposited hard chromium coating layer,unspecified bath | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0150237DD9EF5A6E5DBE | HYDC20MnV6 chrome-plated steel rod product | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8B71A036519261ACF1C4 | Nathan Trotter Britannia Pewter, Sn91.75-Sb8-Cu0.25wt% | E;nu | 0/1 | 1 |
| MAT-STEEL-ENAMELED-BROAD | Enameled steel, steel/coating unspecified | E;nu;rho | 0/0 | 0 |

## other_media (41 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| MAT-PAINT-SOURCE-BROAD | Paint material, chemistry unspecified | rho | 0/7 | 2 |
| RESEARCH-MAT-0C322945397B6A7D37E9 | Fundermax Max Compact Exterior F-quality NT-surface high-pressure laminate panel | nu | 0/1 | 1 |
| RESEARCH-MAT-8497198167753FC4A615 | Titanium White pigment / cold-pressed linseed-oil paint | rho | 0/4 | 1 |
| MAT-APPROX-WAX | Wax, unspecified | E;nu | 0/8 | 8 |
| MAT-LAMINATE-SURFACE-BROAD | Laminate surface material, composition unspecified | E;nu | 0/4 | 4 |
| RESEARCH-MAT-7CD50DAC0430840C1D3D | ArnoldN35 sinteredneodymium-iron-boronpermanentmagnet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-618E7BA73FAB4597D75B | Black paraffin wax, supplied ship-model stock | E;nu | 0/1 | 1 |
| RESEARCH-MAT-AFABB2EEFE341CC544A5 | Chikugo estuary mud | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1FCAEC8A63E62621D78D | Clariant Licowax C micro powder PM, amide wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-162A1A5A7BC51AEA665C | Clariant Licowax LP flakes, montanic-acid wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-83F538CFB135796656F3 | Clariant Licowax OP powder, partly saponified montanic-acid ester wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-AC2306572F8D5AD099F6 | Clariant Licowax PE 130 powder, non-polar high-density polyethylene wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-0F28B0EA0AE997317AE2 | Clariant Licowax PED 121, oxidized high-density polyethylene wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-903DF7B319E2CD87B657 | Clariant Licowax PED 153, oxidized high-density polyethylene wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7F51507B0ECEEC3B27F7 | Clariant Licowax PED 522 granules, oxidized copolymer wax | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7D328B59D9BDB16AA592 | Hangzhou bay mud | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FD17AEB846C8789C15F3 | Huangmaohai estuary mud | E;nu | 0/1 | 1 |
| MAT-INK-SOURCE-BROAD | Ink material, composition unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-AC841BF74F7F66C856DF | Kaolinite mud | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FB6A4467BBE27D108ED5 | Lianyungang port mud | E;nu | 0/1 | 1 |
| RESEARCH-MAT-38705AC3C402C9E60C86 | Lianyungang waterway mud | E;nu | 0/1 | 1 |
| MAT-MUD-BROAD | Mud-like material, composition/moisture unspecified | E;nu | 0/9 | 1 |
| RESEARCH-MAT-98E2098CC7B846BFA524 | Prussian Blue pigment / cold-pressed linseed-oil paint | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-324840F5C9CB4780A40A | Resopal Traceless fingerprint-resistant decorative laminate sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B28B18DB699B29ECAE7C | Rushil decorative HPL phenolic-kraft melamine-surface laminate sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3594919C2D6BA7C186C7 | Sprinter Grade18114 propylene-glycol-based UV-fluorescing marking ink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-47A18A12736A61A71AE5 | Tianjin new port mud | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F5506665DEA74DA037A0 | Wilsonart Traceless TP compact high-pressure laminate | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1F50D93F0FB384814122 | Wilsonart Traceless TP thin decorative high-pressure laminate sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-91D2EB65601642B2EBB5 | Wilsonart Traceless TS thin decorative high-pressure laminate sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-34889756CB6785DFAB63 | Zhejiang coastal mud | E;nu | 0/2 | 1 |
| SOURCE-MAT-F44B6EEC5034AF151549 | neodymium magnet — source-labelled material, finer composition unspecified | E;nu | 0/1 | 1 |
| SOURCE-MAT-97839AB86E352442295F | PlanWood — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-BD46CCABC4721F394E69 | Solyte branded material — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-A32FA74402C5069047F6 | enamelled aluminum — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-AD6A28340DD32D3F688A | nubuck — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-939686697864E247B482 | split suede — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-9D0A3AA2A4AC1BA88254 | synthetic material, chemistry unspecified — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-1FE70C971D491482EF79 | synthetic suede — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-2DDEB3646CFF4B123AA8 | water-resistant suede — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-D8A4EF9DB13DA86281BA | waterproof leather — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## paper (27 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-41E123C074403E4F7BC8 | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP -% w/v, SCNNP -% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-4DC5F8A7C98991DC3CC0 | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP -% w/v, SCNNP 0.5% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-0A9D875D92E478FCA70F | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 0.25% w/v, SCNNP -% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-B91BB4396437486BB74E | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 0.25% w/v, SCNNP 0.5% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-ABC3496BA1795B79706E | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 0.5% w/v, SCNNP -% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-1B5E6FA752DE26EC171A | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 0.5% w/v, SCNNP 0.5% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-6B982E0C1C10FDC014EF | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 1.00% w/v, SCNNP -% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-F3033978CD78ADB397D6 | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 1.00% w/v, SCNNP 0.5% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-8D545609431D25CEA9EB | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 3.00% w/v, SCNNP -% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-723E7309FE69E351E3D3 | Agro-waste pulp paper coated with CPAM 0.2% w/v, SiO2NP 3.00% w/v, SCNNP 0.5% w/v | nu | 0/1 | 1 |
| RESEARCH-MAT-0CE74CD370C10D086AAE | Agro-waste pulp paper, uncoated | nu | 0/1 | 1 |
| RESEARCH-MAT-165595EEEC03D1C48317 | Beech-pulp nanofibrillated-cellulose sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-72D7032F34542631F57D | Cellulose nanofibril film CNF-180 | E | 0/1 | 1 |
| RESEARCH-MAT-9E8D06BD85498371BC9C | Cellulose nanofibril film CNF-270 | E | 0/3 | 1 |
| RESEARCH-MAT-6E3BC664C5E6AB120797 | Cellulose nanofibril film CNF-360 | E | 0/1 | 1 |
| RESEARCH-MAT-843CF9649C5EBA687602 | Cellulose nanofibril film CNF-450 | E | 0/1 | 1 |
| RESEARCH-MAT-D1B4853A9868301EF0AD | Cellulose nanofibril film CNF-90 | E | 0/1 | 1 |
| RESEARCH-MAT-81F01B66766A20AF2286 | Two-liner / one-flute corrugated cardboard sandwich | rho | 0/1 | 1 |
| RESEARCH-MAT-D586B41652BCF8DB3F7A | 10 wt% lyocell / 90 wt% pine-spruce NBSK-pulp paper | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0BA6ECB84F4DDC0EE82B | 100% cotton-linter paper | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-52FD6655F164791BC147 | 100% eucalyptus bleached-kraft-pulp paper | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E46BD228E508062246C2 | 20-30% pine / 70-80% spruce NBSK-pulp paper | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DB9A55CBDEA89FF3D135 | 50-60% lodgepole-pine / 30-40% white-spruce / 5-10% subalpine-fir / 0-10% other NBSK-pulp paper | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5C31FC52EF6338C905EA | 70-100% pine / 0-30% spruce bleached-pulp paper | nu;rho | 0/1 | 1 |
| MAT-PAPER-COTTON-FIBER-BROAD | Cotton-fibre paper, formulation/basis weight unspecified | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-50F78EBF089C81E06F54 | GarnTec kraft-paper cord | E;nu | 0/1 | 1 |
| MAT-PAPER-RATTAN-WEAVE-BROAD | Paper-rope/rattan weave, construction unspecified | E;nu;rho | 0/0 | 0 |

## polymer (519 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-35865075888A5F437F75 | Ensinger TECAPEEK MT — PEEK (Polyetheretherketone) | nu | 0/5 | 5 |
| RESEARCH-MAT-0BA8E6C85264682CC9F3 | Ensinger TECASON P MT XRO — PPSU (Polyphenylsulfone) | nu | 0/4 | 4 |
| MAT-PLASTIC-CELLULOSE-ACETATE-BROAD | Cellulose-acetate-type plastic, grade unspecified | nu | 0/10 | 3 |
| RESEARCH-MAT-B0DE906C5387F1451EB5 | Ensinger TECAPEEK MT XRO — PEEK (Polyetheretherketone) | nu | 0/3 | 3 |
| RESEARCH-MAT-3FEA9AFF884B3547D241 | 92 wt.% of Bio-PE + 6 wt.% basalt fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/4 | 2 |
| RESEARCH-MAT-27290FA8AEB6FF259C59 | 92 wt.% of Bio-PE + 6 wt.% coconut shell fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/4 | 2 |
| RESEARCH-MAT-7DDDFDA0292013E861EE | 92 wt.% of Bio-PE + 6 wt.% wood flour + 2 wt.% Scona TPPP 9112 FA | nu | 0/4 | 2 |
| RESEARCH-MAT-AF1117EBAB29D75DD4D3 | Ensinger TECAFORM AD — POM-H (Polyacetal (Homopolymer)) | nu | 0/2 | 2 |
| RESEARCH-MAT-A4EF135D8C2A3C2056A3 | Ensinger TECAMID 6 FRT — PA 6 (Polyamide 6) | nu | 0/2 | 2 |
| RESEARCH-MAT-C02BE427DFB85A9D93AD | Ensinger TECAMID 66 GF35 — PA 66 (Polyamide 66) | nu | 0/2 | 2 |
| RESEARCH-MAT-113288EA1519326430BE | Ensinger TECAPEEK TF10 — PEEK (Polyetheretherketone) | nu | 0/2 | 2 |
| RESEARCH-MAT-D822D730A341C166863C | Ensinger TECAPEEK — PEEK (Polyetheretherketone) | nu | 0/2 | 2 |
| RESEARCH-MAT-45B380D27DEFBC2607AD | Ensinger TECAPET — PET (Polyethylene terephthalate) | nu | 0/2 | 2 |
| RESEARCH-MAT-6D27AAEA7E6AA16F801A | Ensinger TECAPRO MT — PP (Polypropylene) | nu | 0/2 | 2 |
| RESEARCH-MAT-041C93C083AB9A9EB85D | Ensinger TECASON P MT — PPSU (Polyphenylsulfone) | nu | 0/2 | 2 |
| RESEARCH-MAT-CFE8B2824F5103154301 | Ensinger TECAST L — PA 6 C (Cast polyamide 6) | nu | 0/2 | 2 |
| RESEARCH-MAT-58ED339E632AA5B7C3CD | Ensinger TECAST T — PA 6 C (Cast polyamide 6) | nu | 0/2 | 2 |
| MAT-PLASTIC-UREA-FORMALDEHYDE-BROAD | Urea-formaldehyde plastic, grade/filler unspecified | nu | 0/4 | 2 |
| RESEARCH-MAT-B278A8A4A4E2CE023371 | 10% Carbon Fibre Reinforced POM Copolymer Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-D7A8BCAC23D710ADAFA1 | 100 wt.% Green PE SHC7260 Braskem (Bio-PE) | nu | 0/3 | 1 |
| RESEARCH-MAT-2264EA17F81E9C259379 | 20% Carbon Fibre Reinforced PPS Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-8FB39C482CECCC8B2974 | 20% PTFE Fibre Filled POM Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-76442119A268D6E6F605 | 30% Carbon Fibre Reinforced Nylon 66 Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-68EC70028EA22D622BD6 | 30% Carbon Fibre Reinforced Polycarbonate Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-48A1DF71908B57B023EE | 30% Glass Fibre Filled Polycarbonate Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-2B059825CA0544F032D2 | 30% Glass Fibre Reinforced Modified PPO Rod | E | 0/1 | 1 |
| RESEARCH-MAT-99E6E858682A22EE5CEA | 30% Glass Fibre Reinforced Nylon 12 Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-B4B18C315A7CFFC70041 | 30% Glass Fibre Reinforced Nylon 6 Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-D339A0D2AF5170AD8CC0 | 30% Glass Fibre Reinforced PBT Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-292F8095F0209D692A51 | 35% Glass Fibre filled PPA Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-275FFCC08497F1F0EDDD | 40% Glass Fibre Reinforced PPS Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-3D7324CD61D7D4ECB71F | 50% Glass Fibre Filled PPA Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-DA747EDFB838547FD573 | 74 wt.% of Bio-PE + 12 wt.% coconut shell fibers + 12 wt.% basalt fibers+ 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-410A3C83D07D77785984 | 74 wt.% of Bio-PE + 12 wt.% wood flour + 12 wt.% basalt fibers+ 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-A403BD5EC27DDFDC350F | 74 wt.% of Bio-PE + 12 wt.% wood flour + 12 wt.% coconut shell fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-0C7CB5077C63BB3E8B8A | 86 wt.% of Bio-PE + 12 wt.% basalt fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-365C00B29858DEF1E76A | 86 wt.% of Bio-PE + 12 wt.% coconut shell fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-ADEEA444315A97BB65D9 | 86 wt.% of Bio-PE + 12 wt.% flax fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-4F781A8965E7F6E4B661 | 86 wt.% of Bio-PE + 12 wt.% wood flour + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-210BBC2D9E10CB5C9D4C | 86 wt.% of Bio-PE + 6 wt.% coconut shell fibers + 6 wt.% basalt fibers+ 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-BF6820F26CCC62B00131 | 86 wt.% of Bio-PE + 6 wt.% wood flour + 6 wt.% basalt fibers+ 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-F1274FB99F56A5DE6932 | 86 wt.% of Bio-PE + 6 wt.% wood flour + 6 wt.% coconut shell fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-CEE49BA8C1E9096B99ED | 92 wt.% of Bio-PE + 6 wt.% flax fibers + 2 wt.% Scona TPPP 9112 FA | nu | 0/3 | 1 |
| RESEARCH-MAT-9E8DF9ABC05F14C2CADB | Conductive Polystyrene Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-5C15D9B4665F240E4F6F | Covestro Makrolon 2405 | nu | 0/1 | 1 |
| RESEARCH-MAT-72A4ABDE9E430C02B553 | Cross-Linked Polystyrene Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-ACD3DA848EF3011E45A3 | DSM Bionate 75D polycarbonate urethane (PCU) | rho | 0/4 | 1 |
| RESEARCH-MAT-C2CFF3D48D1FEE5626B6 | DSM Bionate 80A polycarbonate urethane (PCU) | rho | 0/4 | 1 |
| RESEARCH-MAT-A4D87888241D41A8D62D | EMICO Bakelite / phenolic sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-A9EAC35715C59BD57673 | ETFE Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-73A7254FD63638A07E20 | Ensinger TECADUR MT TR — PCT-G (Poly Cyclohexylenedimethylene Terephthalate glycol-modified) | nu | 0/1 | 1 |
| RESEARCH-MAT-627E91DF9B4DD5E21E14 | Ensinger TECADUR PBT GF30 — PBT (Polybutylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-18A9E62182D68443310F | Ensinger TECADUR PBT UD — PBT (Polybutylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-6787E211F7A0ED262525 | Ensinger TECADUR PET CMP — PET (Polyethylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-F11AAE80BFD2E41FB4E2 | Ensinger TECADUR PET — PET (Polyethylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-A0E231D04D11F817AF2F | Ensinger TECAFINE PMP — PMP (Polymethylpentene) | nu | 0/1 | 1 |
| RESEARCH-MAT-63D1F18D958FF85E1C82 | Ensinger TECAFLON PVDF ELS — PVDF (Polyvinylidene fluoride) | nu | 0/1 | 1 |
| RESEARCH-MAT-F7F90E2A64177D40CB2C | Ensinger TECAFLON PVDF RP — PVDF (Polyvinylidene fluoride) | nu | 0/1 | 1 |
| RESEARCH-MAT-358169B602EE1618ED45 | Ensinger TECAFLON PVDF — PVDF (Polyvinylidene fluoride) | nu | 0/1 | 1 |
| RESEARCH-MAT-8DA8505230222DADAAAA | Ensinger TECAFORM AD AF — POM-H (Polyacetal (Homopolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-BEB668EE522F4DF9313B | Ensinger TECAFORM AD EF — POM-H (Polyacetal (Homopolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-4386AA2BEB263D325CBC | Ensinger TECAFORM AH EF — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-4D8C390992B38F90A523 | Ensinger TECAFORM AH ELS — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-147AF1B7625CE3C91A09 | Ensinger TECAFORM AH GF25 — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-E63BB064A58B1BFDCF72 | Ensinger TECAFORM AH ID — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-1EC1390A8E7A8E56B759 | Ensinger TECAFORM AH LA — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-6BAE914A8CF1F960B68D | Ensinger TECAFORM AH LM — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-E951FE91857EA73926AA | Ensinger TECAFORM AH RP — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-DF59996813E3D011BDE6 | Ensinger TECAFORM AH SD — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-50CAA3DD76F55F865D47 | Ensinger TECAFORM AH TF10 — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-34B2DD523CC950720C01 | Ensinger TECAFORM AH UD — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-552E59A794E1E6F06271 | Ensinger TECAFORM AH — POM-C (Polyacetal (Copolymer)) | nu | 0/1 | 1 |
| RESEARCH-MAT-ADD792EFFE4C0FD278ED | Ensinger TECAGLIDE — PA 6 C (Cast polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-7DF498A75C643FBF2EF3 | Ensinger TECAMID 12 — PA 12 (Polyamide 12) | nu | 0/1 | 1 |
| RESEARCH-MAT-1EB6F2EB541D0F04BF2E | Ensinger TECAMID 6 GF25 — PA 6 (Polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-D5D9C7B52526FDD1E5EB | Ensinger TECAMID 6 GF30 — PA 6 (Polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-BD6BAE7278FF4D055609 | Ensinger TECAMID 6 ID — PA 6 (Polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-5CB07BCE017022F047B2 | Ensinger TECAMID 6 MO — PA 6 (Polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-F9EED80117B88270F821 | Ensinger TECAMID 6 — PA 6 (Polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-84E8CE881C6A8E3A292B | Ensinger TECAMID 6/3 TR — PA 6-3-T (Polyamide 6-3-T) | nu | 0/1 | 1 |
| RESEARCH-MAT-47502A5965CB243AA7E1 | Ensinger TECAMID 66 CF20 — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-E628D69534E119AB24F8 | Ensinger TECAMID 66 GF30 — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-9D56FA270C1E85DC4F26 | Ensinger TECAMID 66 HI — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-870A235A79492C000275 | Ensinger TECAMID 66 LA — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-91BD2134DF5D961FC83A | Ensinger TECAMID 66 MO — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-4FACAE28E2E76830E634 | Ensinger TECAMID 66 — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-66AFB4EAB6E26306D2C6 | Ensinger TECAMID 66/X GF50 — PA 66 (Polyamide 66) | nu | 0/1 | 1 |
| RESEARCH-MAT-37C60AA6B568F3593117 | Ensinger TECANAT CMP — PC (Polycarbonate) | nu | 0/1 | 1 |
| RESEARCH-MAT-02FC7440AB45FFF65938 | Ensinger TECANAT GF30 — PC (Polycarbonate) | nu | 0/1 | 1 |
| RESEARCH-MAT-126399FBEF00E453A015 | Ensinger TECANAT — PC (Polycarbonate) | nu | 0/1 | 1 |
| RESEARCH-MAT-25881B871419FB890245 | Ensinger TECANYL 731 — PPE (Polyphenylene ether) | nu | 0/1 | 1 |
| RESEARCH-MAT-60CECD4FD607B00F7C4D | Ensinger TECANYL GF30 — PPE (Polyphenylene ether) | nu | 0/1 | 1 |
| RESEARCH-MAT-C1067D3C55A6D638CCBD | Ensinger TECAPAI CM XP403 — PAI (Polyamide-imide) | nu | 0/1 | 1 |
| RESEARCH-MAT-132F77349B2DA6A11612 | Ensinger TECAPAI CM XP440 — PAI (Polyamide-imide) | nu | 0/1 | 1 |
| RESEARCH-MAT-303482C966260B7D68D7 | Ensinger TECAPAI CM XP530 — PAI (Polyamide-imide) | nu | 0/1 | 1 |
| RESEARCH-MAT-CAC8BD158FA3E7FDEDE1 | Ensinger TECAPAI CM XP730 — PAI (Polyamide-imide) | nu | 0/1 | 1 |
| RESEARCH-MAT-93F24722AB311B801ED2 | Ensinger TECAPEEK CF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-5D2A1CE7398EB98FE1C3 | Ensinger TECAPEEK CM XP100 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-5F40B3D388D1DBC10268 | Ensinger TECAPEEK CM XP91 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-E9783171A3FD39F43CAF | Ensinger TECAPEEK CM XP96 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-D2004F1B8657314F25AF | Ensinger TECAPEEK CM XP98 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-77806D5BCCCEC616DCF9 | Ensinger TECAPEEK CMF — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-4FDC643A4BAE89AB93D8 | Ensinger TECAPEEK CMP — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-EE53A806D05918CA5B14 | Ensinger TECAPEEK ELS CF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-048B0EC768310003562C | Ensinger TECAPEEK ELS nano — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-3C8F92C0DFC866C2F4A9 | Ensinger TECAPEEK GF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-92455CF5D37694DE9B67 | Ensinger TECAPEEK HT — PEK (Polyetherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-22A7DA3A25CD49FD35A8 | Ensinger TECAPEEK ID — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-386A0B3791A21F0DE245 | Ensinger TECAPEEK IM CF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-53D7C4BF216BE8014E22 | Ensinger TECAPEEK IM PVX — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-E8E6AC214313E1133274 | Ensinger TECAPEEK MT CF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-D5FDC7E9EE0E52CBBFB4 | Ensinger TECAPEEK MT CLASSIX — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-4645A78A3533CF8E7214 | Ensinger TECAPEEK PVX — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-11F47D1F8B6C6FBAAFFE | Ensinger TECAPEEK RP — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-3E97E3DCAC1A74AB2956 | Ensinger TECAPEEK SD — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-A793F05AE4B616CED63F | Ensinger TECAPEEK SM CF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-995700DEA7018D6A6651 | Ensinger TECAPEEK SM GF30 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-4C9D723A4F41F6B5CF73 | Ensinger TECAPEEK SM PVX — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-9FAC5C738230CB31F4D5 | Ensinger TECAPEEK SM — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-36B01CE5082AACF0053C | Ensinger TECAPEEK ST — PEKEKK (Polyetherketoneetherketoneketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-04CC010A323078C49204 | Ensinger TECAPEEK SX — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-FB79F9ACF05CF67B339B | Ensinger TECAPEEK UD — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-50027F4C8075A480109C | Ensinger TECAPEI EF — PEI (Polyetherimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-9C4705CEB46CFC44EE88 | Ensinger TECAPEI GF30 — PEI (Polyetherimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-33B3CDE22F314DD0BBA5 | Ensinger TECAPEI — PEI (Polyetherimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-0CE00BA542BE18C82EFD | Ensinger TECAPET TF — PET (Polyethylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-36FBF7FB92A3E9E5A81E | Ensinger TECARIM 1500 — PA 6 C (Cast polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-203868FC166D4D28DABD | Ensinger TECASINT 1011 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-0C878B1AD00BA32D1EB3 | Ensinger TECASINT 1021 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-5C0C4BC0EE18F0C98F0E | Ensinger TECASINT 1031 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-2289EF1D4386629BA9AF | Ensinger TECASINT 1061 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-47ED828A52C1206A4246 | Ensinger TECASINT 2011 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-67909B6002F9EE93B753 | Ensinger TECASINT 2021 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-BC3191C0395761809CC8 | Ensinger TECASINT 2031 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-DE23AE7BEF6E74274FFC | Ensinger TECASINT 2061 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-D8C8E5E6D3666DDFE32F | Ensinger TECASINT 2391 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-58B5539743751E624778 | Ensinger TECASINT 4011 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-23AFFAAC22E7DB3466DF | Ensinger TECASINT 4021 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-9BA177E6965B13FA8889 | Ensinger TECASINT 4111 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-518C00DF9A134A633B1B | Ensinger TECASINT 4121 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-0BCA01A8DB21694415A9 | Ensinger TECASINT 5051 — base polymer not stated in source Facts | nu | 0/1 | 1 |
| RESEARCH-MAT-F1AB622E210E64A79E0E | Ensinger TECASINT 5111 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-98C2ACB7BF05735B14BB | Ensinger TECASINT 5501 ESD — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-04D12A5122DA3BB7EF78 | Ensinger TECASINT 5511 SD — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-AAA47EF75A20E48B89F2 | Ensinger TECASINT 6012 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-6C30028CA828CB25E2A8 | Ensinger TECASINT 6022 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-3E61B294AFFF567EB06D | Ensinger TECASINT 6032 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-E2314AC9631ABE6137B5 | Ensinger TECASINT 6062 — PI (Polyimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-3625B6B82DB5A70F0306 | Ensinger TECASINT 8591 — PTFE (Polytetrafluorethylene) | nu | 0/1 | 1 |
| RESEARCH-MAT-C144205EC7C4D62BE20D | Ensinger TECASON S — PSU (Polysulfone) | nu | 0/1 | 1 |
| RESEARCH-MAT-CC547DDF3603603DA98C | Ensinger TECAST T EF — PA 6 C (Cast polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-4E835F64C405D48A5685 | Ensinger TECAST T MO — PA 6 C (Cast polyamide 6) | nu | 0/1 | 1 |
| RESEARCH-MAT-A791F89D7F3290D4B591 | Ensinger TECATEC PC CW50 PL V01 — PC (Polycarbonate) | nu | 0/1 | 1 |
| RESEARCH-MAT-E858A9106F2784396918 | Ensinger TECATEC PEEK CW50 PL V01 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-3534A29000BE6A888132 | Ensinger TECATEC PEEK MT CW50 — PEEK (Polyetheretherketone) | nu | 0/1 | 1 |
| RESEARCH-MAT-52A80444DEA9EC65DD28 | Ensinger TECATEC PEI GW50 PL V01 — PEI (Polyetherimide) | nu | 0/1 | 1 |
| RESEARCH-MAT-84C7B14E804FA7B055DF | Ensinger TECATEC PPS CW50 PL V01 — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-25CE04D14823ADEF0D31 | Ensinger TECATEC PPS GW50 PL V01 — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-AEE6A05AEC6674E2CFA6 | Ensinger TECATRON CMP — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-034CEAF9E9E9068D31C9 | Ensinger TECATRON GF40 — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-B287DB6AB716E08C5F42 | Ensinger TECATRON PPS CM XP64 — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-F0C82E4592E1839B4466 | Ensinger TECATRON PVX — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-1A083AB5054996A0B40A | Ensinger TECATRON SX — PPS (Polyphenylensulfide) | nu | 0/1 | 1 |
| RESEARCH-MAT-70CDA83343D09F28BDFB | Glass-Filled PTFE Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-E427D754F16FD64885B1 | High-density polyethylene base polymer | nu | 0/1 | 1 |
| RESEARCH-MAT-F98995D4935FAF611DEA | LDPE Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-0B4B36A05EB1A411DE98 | LOCTITE 3D IND3380 BLACK photopolymer | nu | 0/2 | 1 |
| RESEARCH-MAT-35D0C7D5735A9051C098 | LOCTITE 3D IND3785 WHITE photopolymer | nu | 0/2 | 1 |
| RESEARCH-MAT-BE152DE2D3B67610DB7F | LOCTITE 3D IND403 NATURAL photopolymer | nu | 0/2 | 1 |
| RESEARCH-MAT-09411D7C9926678BE2F4 | LOCTITE 3D IND406 BLACK photopolymer | nu | 0/2 | 1 |
| RESEARCH-MAT-FD132A73445ED07F1B22 | LOCTITE 3D IND5714 GRAY photopolymer elastomer | nu | 0/1 | 1 |
| RESEARCH-MAT-F7C9BF98301695FAF491 | Mazzucchelli cellulose acetate formulation, 24% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-FC4EC0909DCE044E61AA | Mazzucchelli cellulose acetate formulation, 26% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-8E4FFB690E59BBFB9D5F | Mazzucchelli cellulose acetate formulation, 28% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-95EB0F2D38FD97AFF93D | Mazzucchelli cellulose acetate formulation, 30% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-CD3E2CBFDA8856E1368D | Mazzucchelli cellulose acetate formulation, 32% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-AD09049DBA532B45B9B3 | Mazzucchelli cellulose acetate formulation, 34% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-98E66AFD53C9BBD07C51 | Mazzucchelli cellulose acetate formulation, 36% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-E5427D915DD3DB8619A1 | Mazzucchelli cellulose acetate formulation, 38% DEP | nu | 0/1 | 1 |
| RESEARCH-MAT-E56CCC76E7A7D2D4F9BF | Nylon 46 Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-DD19973420A11384148E | PBT Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-F67E4F1AD29E6A816A56 | PCTFE Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-D1538934414C2DAA0134 | PEK Film | nu | 0/1 | 1 |
| RESEARCH-MAT-7C05DE4D34F49CFEAD4F | PEKK Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-DC66540C181511404896 | PEN Film | nu | 0/1 | 1 |
| RESEARCH-MAT-F68640DA28CD149AF464 | PPSU Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-8B8F3177C8BAC38A238D | PSU rod | nu | 0/1 | 1 |
| RESEARCH-MAT-2AC9614FB79C55459F8D | PVDF Film/Sheet | E | 0/1 | 1 |
| RESEARCH-MAT-5BA828AC996E8696E03B | Plenco 02000 series organic-filled phenolic molding materials | rho | 0/1 | 1 |
| RESEARCH-MAT-7013ADDFE4669FFAFB81 | Poly(hexamethylene terephthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-66A6ABA3BBC3BE9B092E | Poly(hexamethylene terephthalate)-block-poly(tetrahydrofuran)1000 copolyetherester,rigid/flexible feed50/50wt | nu | 0/1 | 1 |
| RESEARCH-MAT-D897D5576B04DDE2012E | Poly(hexamethylene2,5-furandicarboxylate) | nu | 0/1 | 1 |
| RESEARCH-MAT-146594A6DF91DFD0ABE6 | Poly(hexamethylene2,5-furandicarboxylate)-block-poly(tetrahydrofuran)1000 copolyetherester,rigid/flexible feed50/50wt | nu | 0/1 | 1 |
| RESEARCH-MAT-04BD86EB55CCA0F5CF3F | Poly(hexamethylene2,6-naphthalate) | nu | 0/1 | 1 |
| RESEARCH-MAT-E958104C8D68368979D8 | Poly(hexamethylene2,6-naphthalate)-block-poly(tetrahydrofuran)1000 copolyetherester,rigid/flexible feed50/50wt | nu | 0/1 | 1 |
| RESEARCH-MAT-BA9A3ABF7DD17F7056B0 | Polyethylene terephthalate (PET) base polymer | nu | 0/1 | 1 |
| RESEARCH-MAT-B11B60DE70747E39B58B | Polyimide Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-57901D9E8062C23CFF1C | Polypropylene Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-337FE880ACD2A407B2DB | Polypropylene base polymer | nu | 0/1 | 1 |
| RESEARCH-MAT-A85786698AD91A07C522 | Rilsan® BMN TLD Nylon 11 Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-D8C161EAF2178A3D88D1 | SABIC CYCOLOY FR RESIN CX2142ME | nu | 0/1 | 1 |
| RESEARCH-MAT-F4D05F368FE1EDF05195 | SABIC CYCOLOY FR RESIN CX2244ME | nu | 0/1 | 1 |
| RESEARCH-MAT-FCA764628AA2895BA1BE | SABIC CYCOLOY FR RESIN CX7110 | nu | 0/1 | 1 |
| RESEARCH-MAT-30CA90EA0916E5DB9EB3 | SABIC CYCOLOY FR RESIN CX7211 | nu | 0/1 | 1 |
| RESEARCH-MAT-DB48C028BF45933981CB | SABIC CYCOLOY FR RESIN CX7240 | nu | 0/1 | 1 |
| RESEARCH-MAT-858B933170E86F3A95D1 | SABIC CYCOLOY FR RESIN CX7240U | nu | 0/1 | 1 |
| RESEARCH-MAT-E206391EAC04A2D24AA0 | SABIC CYCOLOY FR RESIN CX7510 | nu | 0/1 | 1 |
| RESEARCH-MAT-40C34B34A6C62A6AEB6D | SABIC CYCOLOY FR RESIN CX7720 | nu | 0/1 | 1 |
| RESEARCH-MAT-4107619F2FFB37F9D390 | SABIC CYCOLOY FR Resin RCM6123 | nu | 0/1 | 1 |
| RESEARCH-MAT-4144B7A57D3A8EF803B4 | SABIC LEXAN COPOLYMER 123X | nu | 0/1 | 1 |
| RESEARCH-MAT-980202D06FA6ADAC2322 | SABIC LEXAN COPOLYMER 143X | nu | 0/1 | 1 |
| RESEARCH-MAT-096C83E27A05D68DF9C5 | SABIC LEXAN COPOLYMER 4251R | nu | 0/1 | 1 |
| RESEARCH-MAT-0AF83E7C99B67EB3078C | SABIC LEXAN COPOLYMER 4504 | nu | 0/1 | 1 |
| RESEARCH-MAT-71B817E623F40ADD3706 | SABIC LEXAN COPOLYMER 4704 | nu | 0/1 | 1 |
| RESEARCH-MAT-88DD36A8AC094DFA27E9 | SABIC LEXAN COPOLYMER 4795R | nu | 0/1 | 1 |
| RESEARCH-MAT-5BB40C714E8E451DB2D0 | SABIC LEXAN COPOLYMER 923X | nu | 0/1 | 1 |
| RESEARCH-MAT-6E36BE6DEE51BB44BC4B | SABIC LEXAN COPOLYMER CFR5630 | nu | 0/1 | 1 |
| RESEARCH-MAT-A3260DE20BDC909EB0BE | SABIC LEXAN COPOLYMER CFR5630D | nu | 0/1 | 1 |
| RESEARCH-MAT-50EC02D3EC30FF0C04A2 | SABIC LEXAN COPOLYMER CFR7431 | nu | 0/1 | 1 |
| RESEARCH-MAT-DA597BD21FB72CA6B03B | SABIC LEXAN COPOLYMER CFR7630 | nu | 0/1 | 1 |
| RESEARCH-MAT-5E15ECD73F170F79E4DA | SABIC LEXAN COPOLYMER CFR9111 | nu | 0/1 | 1 |
| RESEARCH-MAT-310F3C99FB3BBC7C9780 | SABIC LEXAN COPOLYMER CFR9131 | nu | 0/1 | 1 |
| RESEARCH-MAT-0A6B4EFEA8E78BF3B94C | SABIC LEXAN COPOLYMER CFR9712 | nu | 0/1 | 1 |
| RESEARCH-MAT-07A28B36C6098D1C7445 | SABIC LEXAN COPOLYMER DMX1435 | nu | 0/1 | 1 |
| RESEARCH-MAT-4B9D088AA2930609C8F3 | SABIC LEXAN COPOLYMER DMX2415 | nu | 0/1 | 1 |
| RESEARCH-MAT-EA7E0B29FD4B4E69FB19 | SABIC NORYL GTX RESIN GTX202 | nu | 0/1 | 1 |
| RESEARCH-MAT-DCCAC40BC21ADA72255F | SABIC NORYL GTX RESIN GTX6203 | nu | 0/1 | 1 |
| RESEARCH-MAT-0FBC02A45BBC1B2C47E0 | SABIC NORYL GTX RESIN GTX678 | nu | 0/1 | 1 |
| RESEARCH-MAT-A5527CD5092A211CDF66 | SABIC NORYL GTX RESIN GTX679 | nu | 0/1 | 1 |
| RESEARCH-MAT-DD473A6FF1192A4BD8C5 | SABIC NORYL GTX Resin 9F0051XT | nu | 0/1 | 1 |
| RESEARCH-MAT-B6A4ADF1B7513B46A679 | SABIC NORYL GTX Resin APS130 | nu | 0/1 | 1 |
| RESEARCH-MAT-10C2733242676526B468 | SABIC NORYL GTX Resin GTX1040A | nu | 0/1 | 1 |
| RESEARCH-MAT-9292F5D63F1527FAC889 | SABIC NORYL GTX Resin GTX1089 | nu | 0/1 | 1 |
| RESEARCH-MAT-630C899C5B71C39FAD66 | SABIC NORYL GTX Resin GTX3210 | nu | 0/1 | 1 |
| RESEARCH-MAT-5B1D8C1AC6A059503857 | SABIC NORYL GTX Resin GTX4610 | nu | 0/1 | 1 |
| RESEARCH-MAT-1E459BECADCD11938693 | SABIC NORYL GTX Resin GTX810 | nu | 0/1 | 1 |
| RESEARCH-MAT-8BCE49B7D8CEB8A4CB7F | SABIC ULTEM RESIN 1040P | nu | 0/1 | 1 |
| RESEARCH-MAT-5621F257910F9A10431D | SABIC ULTEM RESIN 3310TD | nu | 0/1 | 1 |
| RESEARCH-MAT-45AF947E5957487FBC2E | SABIC ULTEM RESIN 4002 | nu | 0/1 | 1 |
| RESEARCH-MAT-160638D617AC324A5FC1 | SABIC ULTEM RESIN 9076 | nu | 0/1 | 1 |
| RESEARCH-MAT-F0566E97536ACA79220C | SABIC ULTEM RESIN AUT210 | nu | 0/1 | 1 |
| RESEARCH-MAT-B53A951A9541358DCCED | SABIC ULTEM RESIN AUT230 | nu | 0/1 | 1 |
| RESEARCH-MAT-5A190B4E9058C42BCABE | SABIC ULTEM RESIN DH1004 | nu | 0/1 | 1 |
| RESEARCH-MAT-83E0CCE994B12541D337 | SABIC ULTEM RESIN DH1004A | nu | 0/1 | 1 |
| RESEARCH-MAT-1DEE50B13299E66F8F70 | SABIC ULTEM RESIN DT1810EV | nu | 0/1 | 1 |
| RESEARCH-MAT-D63078F41517C1C76664 | SABIC ULTEM RESIN DT1810EVUCL | nu | 0/1 | 1 |
| RESEARCH-MAT-92223732B1107CAF1C9B | SABIC ULTEM RESIN DU642 | nu | 0/1 | 1 |
| RESEARCH-MAT-1EF80199E246C54F2BB6 | SABIC ULTEM RESIN LTX300A | nu | 0/1 | 1 |
| RESEARCH-MAT-00F581EDDFE67DBB15DB | SABIC ULTEM RESIN MD256T | nu | 0/1 | 1 |
| RESEARCH-MAT-C730E6BD5A24E2BB46EC | SABIC ULTEM RESIN SF2250 | nu | 0/1 | 1 |
| RESEARCH-MAT-5816A617B2A081EB8797 | SABIC ULTEM RESIN SF2250EPR | nu | 0/1 | 1 |
| RESEARCH-MAT-CECAB342CA2DF1AC26AD | SABIC ULTEM RESIN SF2260 | nu | 0/1 | 1 |
| RESEARCH-MAT-6319501CD455ADAD3DDF | SABIC ULTEM RESIN SF2270 | nu | 0/1 | 1 |
| RESEARCH-MAT-7F199C59A9BC1C01097D | SABIC ULTEM RESIN SF2350 | nu | 0/1 | 1 |
| RESEARCH-MAT-205C18D491182A8D1AB5 | SABIC ULTEM RESIN SF2360 | nu | 0/1 | 1 |
| RESEARCH-MAT-BCE7A932F52A4B94FAE6 | SABIC ULTEM RESIN UF5011S | nu | 0/1 | 1 |
| RESEARCH-MAT-B4087533405A98FE02D6 | SABIC ULTEM Resin 1010GCR3 | nu | 0/1 | 1 |
| RESEARCH-MAT-3E47F05C6C089D021D9C | SABIC ULTEM Resin 1030 | nu | 0/1 | 1 |
| RESEARCH-MAT-E17A49AAFE6BD234352C | SABIC ULTEM Resin 2120 | nu | 0/1 | 1 |
| RESEARCH-MAT-E507CB3B375C0DB58BAF | SABIC ULTEM Resin 2200F | nu | 0/1 | 1 |
| RESEARCH-MAT-FDFE909A924FD0CDCA32 | SABIC ULTEM Resin 2210F | nu | 0/1 | 1 |
| RESEARCH-MAT-3FC08A41E8FB925B4DE4 | SABIC ULTEM Resin 2210GCR3 | nu | 0/1 | 1 |
| RESEARCH-MAT-F910D1E0295800111400 | SABIC ULTEM Resin 2220 | nu | 0/1 | 1 |
| RESEARCH-MAT-5AC3594A9EB19830EA9B | SABIC ULTEM Resin 2300 | nu | 0/1 | 1 |
| RESEARCH-MAT-63A72A35DED8C6EFA6F6 | SABIC ULTEM Resin 2300F | nu | 0/1 | 1 |
| RESEARCH-MAT-9842CEFFAF4D9399D35C | SABIC ULTEM Resin 2300R | nu | 0/1 | 1 |
| RESEARCH-MAT-C39745079B8AD1E30F96 | SABIC ULTEM Resin 2310 | nu | 0/1 | 1 |
| RESEARCH-MAT-E59290E641F4A79FA133 | SABIC ULTEM Resin 2310EPR | nu | 0/1 | 1 |
| RESEARCH-MAT-7BE9D848516549D4A9D7 | SABIC ULTEM Resin 2310F | nu | 0/1 | 1 |
| RESEARCH-MAT-5E6020AB490CFE006D06 | SABIC ULTEM Resin 2310R | nu | 0/1 | 1 |
| RESEARCH-MAT-67E4D3BC700579789E80 | SABIC ULTEM Resin 2312EPR | nu | 0/1 | 1 |
| RESEARCH-MAT-D1093F308FCB114C517B | SABIC ULTEM Resin 2320 | nu | 0/1 | 1 |
| RESEARCH-MAT-6F2A45ECE4C9C119BF4A | SABIC ULTEM Resin 2320G | nu | 0/1 | 1 |
| RESEARCH-MAT-652303945AB70BAE2C24 | SABIC ULTEM Resin 2400 | nu | 0/1 | 1 |
| RESEARCH-MAT-5E2D77420AE992EC90F4 | SABIC ULTEM Resin 2400F | nu | 0/1 | 1 |
| RESEARCH-MAT-A6ED4A5C1A431184DACB | SABIC ULTEM Resin 2410EPR | nu | 0/1 | 1 |
| RESEARCH-MAT-965595463BB800B78A4F | SABIC ULTEM Resin 3473 | nu | 0/1 | 1 |
| RESEARCH-MAT-029AD99F7FA69F2AA8B0 | SABIC ULTEM Resin 9011 | nu | 0/1 | 1 |
| RESEARCH-MAT-824749E27D0482CFFC69 | SABIC ULTEM Resin 9085 | nu | 0/1 | 1 |
| RESEARCH-MAT-B21F724A48C65B30BED1 | SABIC ULTEM Resin ATX3562R | nu | 0/1 | 1 |
| RESEARCH-MAT-2AB5CE52F05C3353CFEC | SABIC ULTEM Resin AUT195 | nu | 0/1 | 1 |
| RESEARCH-MAT-F062ED4490BA55EBA361 | SABIC ULTEM Resin AUT195M | nu | 0/1 | 1 |
| RESEARCH-MAT-5BA7283FC64E9B2FF96B | SABIC ULTEM Resin AUT200 | nu | 0/1 | 1 |
| RESEARCH-MAT-B1D346BB8786940C1771 | SABIC ULTEM Resin AUT200AR | nu | 0/1 | 1 |
| RESEARCH-MAT-98AFA4A03C568A47FA4B | SABIC ULTEM Resin AUT200G4 | nu | 0/1 | 1 |
| RESEARCH-MAT-5226238441A2C82FE6B8 | SABIC ULTEM Resin AUT200G6 | nu | 0/1 | 1 |
| RESEARCH-MAT-50FDDFFDB6258786856C | SABIC ULTEM Resin AUT200M | nu | 0/1 | 1 |
| RESEARCH-MAT-3942DC75AA0C117CB87B | SABIC ULTEM Resin CRS5011R | nu | 0/1 | 1 |
| RESEARCH-MAT-C4A0B5C55AD805B6B5ED | SABIC ULTEM Resin DT1820EV | nu | 0/1 | 1 |
| RESEARCH-MAT-EBC9AA178633E708274A | SABIC ULTEM Resin DT1820EVGCR3 | nu | 0/1 | 1 |
| RESEARCH-MAT-23F4C781DE079A103ABA | SABIC ULTEM Resin DU319 | nu | 0/1 | 1 |
| RESEARCH-MAT-01A94E5710DB443013B1 | SABIC ULTEM Resin DU762 | nu | 0/1 | 1 |
| RESEARCH-MAT-BD9D6D95752B18A18308 | SABIC ULTEM Resin HU1004 | nu | 0/1 | 1 |
| RESEARCH-MAT-11E1375C14EE7EFC076B | SABIC ULTEM Resin HU1100 | nu | 0/1 | 1 |
| RESEARCH-MAT-A971AEDD2468682F0524 | SABIC ULTEM Resin HU1110 | nu | 0/1 | 1 |
| RESEARCH-MAT-46706115F8273A8C810A | SABIC ULTEM Resin HU2100 | nu | 0/1 | 1 |
| RESEARCH-MAT-39769947565E43050CD6 | SABIC ULTEM Resin HU2110 | nu | 0/1 | 1 |
| RESEARCH-MAT-3E07F9E7EBC6996074BB | SABIC ULTEM Resin HU2200 | nu | 0/1 | 1 |
| RESEARCH-MAT-0DBE616D733C0E77F1B6 | SABIC ULTEM Resin HU2210 | nu | 0/1 | 1 |
| RESEARCH-MAT-F0DC8A6E595D14839B29 | SABIC ULTEM Resin HU2300 | nu | 0/1 | 1 |
| RESEARCH-MAT-01429F80982E0AA90CC6 | SABIC ULTEM Resin HU2310 | nu | 0/1 | 1 |
| RESEARCH-MAT-80DFBEB9C995FD8B433C | SABIC ULTEM Resin LTX300AG | nu | 0/1 | 1 |
| RESEARCH-MAT-76F165426C4172B873CC | SABIC ULTEM Resin NP2300 | nu | 0/1 | 1 |
| RESEARCH-MAT-C8F2862F65D7F75A0376 | SABIC ULTEM Resin PW2100 | nu | 0/1 | 1 |
| RESEARCH-MAT-C1E0634E8FA16153E61D | SABIC ULTEM Resin PW2200 | nu | 0/1 | 1 |
| RESEARCH-MAT-6AE7672F6DAAF9B37424 | SABIC ULTEM Resin PW2300 | nu | 0/1 | 1 |
| RESEARCH-MAT-2647EA7C325AAA90E2C6 | SABIC VALOX FR RESIN ENH3500 | nu | 0/1 | 1 |
| RESEARCH-MAT-F3C380F869D889DF0434 | SABIC VALOX FR RESIN ENH4530 | nu | 0/1 | 1 |
| RESEARCH-MAT-94EE2C50D28920CEFD63 | SABIC VALOX FR RESIN ENH4550 | nu | 0/1 | 1 |
| RESEARCH-MAT-71E1052BB7195380CBF7 | SABIC VALOX FR RESIN ENH4560 | nu | 0/1 | 1 |
| RESEARCH-MAT-756F8A9D7D9B01DFB779 | SABIC VALOX FR RESIN ENH4565 | nu | 0/1 | 1 |
| RESEARCH-MAT-8D08E98B132B3CA72C3A | SABIC VALOX FR RESIN ENH8530 | nu | 0/1 | 1 |
| RESEARCH-MAT-0EF472015F41E77EFAAB | SABIC VALOX FR RESIN ENH8560 | nu | 0/1 | 1 |
| RESEARCH-MAT-825DB9125B9F2D8B4F50 | SikaBond T8 polyurethane adhesive | rho | 0/4 | 1 |
| RESEARCH-MAT-AB4BCF6E79B3F9B37627 | TECAFINE PP natural stock shapes | nu | 0/1 | 1 |
| RESEARCH-MAT-5769BDC06062490A1987 | TECARAN ABS grey stock shapes | nu | 0/1 | 1 |
| RESEARCH-MAT-13A133A7C06EB543F72A | Unplasticised PVC Film/Sheet | nu | 0/1 | 1 |
| RESEARCH-MAT-CA37A6DF8DF370B097C4 | VICTREX® APTIV® 1102 20% mineral filled PEEK Film | nu | 0/1 | 1 |
| RESEARCH-MAT-57B042D412D8F082D659 | Vectra® A115 15% Reinforced Glass Fibre LCP Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-C71EE1DDF0C557E7A369 | Vectra® A130 30% Reinforced Glass Fibre LCP Granules | nu | 0/1 | 1 |
| RESEARCH-MAT-221354783E5A4719B6A9 | Vectra® A430 25% PTFE Filled Fibre LCP Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-3BF35374E29A3A8201BD | Vectra® B130 30% Reinforced Glass Fibre LCP Rod | nu | 0/1 | 1 |
| RESEARCH-MAT-152CA788FA623647C204 | Vestakeep® 4000GF30 30% Glass Fibre Reinforced PEEK Granules | E | 0/1 | 1 |
| RESEARCH-MAT-F8B0D9A23724974304FD | 100 wt% bio-polyethylene | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EA1FB2CCBEE274B16E8C | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane (without filler, as reference) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A18A48082EE0864A23DA | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 1 wt% LDH@GO | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6559DED3A6979B0F26A4 | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 1wt. % LDHGO@Si | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CE93F3E3C3C565573DCB | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 2 wt% LDH@GO | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9D500EE40F6FDFB9C429 | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 2wt. % LDHGO@Si | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C1D6A09FF6E64855F1F4 | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 3wt. % LDH@GO | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-37267B964009C622A4EF | AC753 acrylic-polyol/DesmodurN75 two-component polyurethane free film, 2k polyurethane + 3wt. % LDHGO@Si | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B29A7B5EB9AA91444EAD | APLA/MPF2 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DEA9B22531E18281E1C3 | APLA/NPF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EBAC63B842CE3C6EBA0B | BASF Elastollan1185A thermoplastic polyurethane with TRGO1000 1 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-331B10D478D8AA1B71D6 | BASF Elastollan1185A thermoplastic polyurethane with TRGO1000 3 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8F0568FB174646903E1D | BASF Elastollan1185A thermoplastic polyurethane with TRGO1000 5 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5E32D9C168447F77CEFB | BASF Elastollan1185A thermoplastic polyurethane with TRGO1000 7 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9622E2BD0CE35EF6BA6A | BASF Elastollan1185A thermoplastic polyurethane with TRGO600 1 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-41D1B6478D0A15C501F9 | BASF Elastollan1185A thermoplastic polyurethane with TRGO600 3 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FA123F536BD8C813D89A | BASF Elastollan1185A thermoplastic polyurethane with TRGO600 5 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CC17465F496685FCF994 | BASF Elastollan1185A thermoplastic polyurethane with TRGO600 7 wt.% thermally reduced graphene oxide | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9EA30A24B501B8602068 | BASF Elastollan1185A thermoplastic polyurethane, unfilled | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4D7378337750D27D0E32 | BAYER TPU1170A thermoplastic polyurethane,unfilled | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1B93030B34D2E38A9406 | Biobased thermoplastic polyurethane PearlbondEcoD590 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-28C52B190225BA91D0C5 | Carbon Filled Polyethylene Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8E3587A245998886216F | Cassava (30% glycerol) thermoplastic starch | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6ACDA8ACB3124052A0F6 | Cellulose acetate | E;nu | 0/1 | 1 |
| RESEARCH-MAT-915620585C12CD58D3C2 | Commercial nonbiobased RD27 polyether polyurethane film | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C977441A2FDD440C0364 | Commercial styrene copolymer containing10wt% ethylene glycol dimethacrylate (EGDMA) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-475894325177C84B136A | Commercial/recycled HIPS filament | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-E8A2FB987546A6D18B23 | Corn thermoplastic starch | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2DAC1CC47868B06B6A10 | Dense essential-oil varnish coating layer in Zhou2026 varnished spruce cross-section | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EFF903DE688ECBE954D2 | EDC/NHS-crosslinked hyaluronic acid hydrogel,1%w/v HA precursor | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-411E6DD5DF6713F9FB48 | Ensinger TECAFLON PTFE — PTFE (Polytetrafluorethylene) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6D27A4BC7A2226A55CA6 | Ensinger TECANYL VH2 — PPE (Polyphenylene ether) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D644E58D9CC9BFB273E2 | Ensinger TECAPEEK CM XP101 — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-2B2DE05442FC0F372EE7 | Ensinger TECAPEEK CM XP108 — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-59C9DD6BF88BC7858E03 | Ensinger TECAPEEK CM XP109 — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-DE7757CA05188BF45436 | Ensinger TECAPEEK CM XP92 — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E815002B5166FBD84F9E | Ensinger TECAPEEK IM GF30 — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C3EE488F818592D345BB | Ensinger TECAPEEK IM — PEEK (Polyetheretherketone) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9C4630CFF4388AED8A49 | Ensinger TECASINT 8001 — PTFE (Polytetrafluorethylene) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BCB893B41B3D17F1BD4F | Ensinger TECASINT 8061 — PTFE (Polytetrafluorethylene) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9EF88431BFA98F5C1F67 | Ensinger TECATRON PPS CM XP83 — PPS (Polyphenylensulfide) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CE38BD10DF6459F4655D | Epoxy/MBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C45D6F441B0CA4551F76 | Epoxy/NBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5C7D52AD06489B7CE356 | HDPE ethylene copolymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1599368AC679FE976658 | HDPE ethylene homopolymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E6BC10022EE7B2DDA947 | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 0:100 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A9A7D4DA7BFA7C184CE6 | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 100:0 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-085BEB182D96A594F350 | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 20:80 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2540464C221C0B133239 | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 40:60 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D7C12A1F9BD29A620DBC | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 60:40 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-23875BA86E6072CDC716 | HMDI/1,4butanediol polyurethane,1,6hexanediolpolycarbonatepolyolsCD1000:CD2000 80:20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E5628DDA42F8EC8316F2 | HMDI/polycarbonate-diol1000/1,4-butanediol polyurethane with halloysite 0.5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0D670726E0D143C79CC5 | HMDI/polycarbonate-diol1000/1,4-butanediol polyurethane with halloysite 0wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8A1767D78E7EE3EAA7A5 | HMDI/polycarbonate-diol1000/1,4-butanediol polyurethane with halloysite 10wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EEE28907664121F6ACC0 | HMDI/polycarbonate-diol1000/1,4-butanediol polyurethane with halloysite 1wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B23DF814E056942E3646 | HMDI/polycarbonate-diol1000/1,4-butanediol polyurethane with halloysite 3wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F50EA6804ED9CF9ACF53 | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-313AFD28C7D2E4FF46C5 | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-2 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1F1A2FEA0EF5A7D4DC5A | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-3PDO | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E9AD9A436D2445171A40 | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-3POSS | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B6F6459F7344C14EFE0B | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-7PDO | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-167EE0A525BB7041152B | IPDI-based Priplast3238 amorphous polyester polyurethane-urea film 3238-7POSS | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B2117419F22CAFB3CBD3 | IPDI-based polyester polyurethane-urea film derived from semicrystalline Priplast3294 polyol 3294IPDI-1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A51E977E941C1AF1D89F | IPDI-based polyester polyurethane-urea film derived from semicrystalline Priplast3294 polyol 3294IPDI-2 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DD21BC641663E233DD8C | IPDI-based polyester polyurethane-urea film derived from semicrystalline Priplast3294 polyol 3294IPDI-2/SWCNT 0.1 wt. % | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A8734217374265B3FCDE | IPDI-based polyester polyurethane-urea film derived from semicrystalline Priplast3294 polyol 3294IPDI-3 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-339EB2E620C788354A66 | IPDI-based polyester polyurethane-urea film derived from semicrystalline Priplast3294 polyol 3294IPDI-7 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-00BBCD35F918AE02868E | Kapton® 200RS100 Polyimide Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-A0B486F44DD381D94C48 | Kapton® CRC Polyimide Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-379EFF38EB242CEAECDF | Kapton® FN Polyimide Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-70D20EA0178F62B82E30 | Kapton® HN Polyimide Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3F5E62006B8280E3A3FD | LDPE/MBF1 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8F5333E0DD1C4E5A6403 | LDPE/MBF2 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D655BE5BD796AA745EFA | LDPE/NBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-46343CF72BC1FC510FA5 | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD1HMFlaurate/JeffamineD230;benzoicacid0mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-76FB3AA207EB9075F8B8 | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD1HMFlaurate/JeffamineD230;benzoicacid20mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B4DACD79A5B657DD1311 | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD2HMFlaurate/JeffamineT403;benzoicacid0mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-65B39D14BE56AEF0EEDE | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD2HMFlaurate/JeffamineT403;benzoicacid20mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3B870AAB1E1CE4633987 | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD3HMFlaurate/isophoronediamine;benzoicacid20mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7FAF276D0372E5375230 | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,ALD4HMFlaurate/1,5-diamino-2-methylpentane;benzoicacid20mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EF92C33773C269E3CF5A | Lupranol2095/1005-1 and4,4MDI moisturecuredpolyurethaneurea,IncozolBHcommercialaldimine;benzoicacid20mol%onimine | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3341E3B9FB974F4279D9 | MM2520 thermoplastic polyurethane/Ecoflex blend film,30wt%Ecoflex | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9C7A41A04C87725E13D5 | Nanodiamond-enhanced PLA filament | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FA7417019127FFEF2896 | Neat cellulose acetate film, source CA control formulation | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-235BFDE713F5B5102CE5 | Non-foamed HIPS reference molding | E;nu | 0/4 | 1 |
| RESEARCH-MAT-33B12B84B33D2953760F | Nylon 12 Rod | E;nu | 0/1 | 1 |
| RESEARCH-MAT-501915F44586E6553AB7 | P(styrene-co-furfuryl methacrylate)/TPU1170A semi-IPN,0%CPSFTPU1;BDB/DHPM-B dynamiccrosslinking | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D378CC2D5EAABA3CFDDF | P(styrene-co-furfuryl methacrylate)/TPU1170A semi-IPN,3%CPSFTPU1;BDB/DHPM-B dynamiccrosslinking | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3B14A97926442704C7E2 | P(styrene-co-furfuryl methacrylate)/TPU1170A semi-IPN,6%CPSFTPU0.5;BDB/DHPM-B dynamiccrosslinking | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-23449DB8125D45FCEF10 | P(styrene-co-furfuryl methacrylate)/TPU1170A semi-IPN,6%CPSFTPU1;BDB/DHPM-B dynamiccrosslinking | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C2DE798AFBFF4C5E1B98 | P(styrene-co-furfuryl methacrylate)/TPU1170A semi-IPN,6%CPSFTPU2;BDB/DHPM-B dynamiccrosslinking | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-29A6644CD0D05B65DE25 | PHB polymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4534B1E8CFD803228C33 | PHB/MBF10% composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DDDBE596E77741C7F0E7 | PHB/MBF5% composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EB0845B2385E8D817364 | PLA/MBF1 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-45730F67332D00FA936C | PLA/MBF3 + C30B composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5DEFC91E0BDEA76E16CE | PLA/MBF3 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-080A95A7909718F8A72A | PLA/NBF + C30B composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-80F0609B4F9507168F93 | PLA/NBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C9D084FD23895849570D | PLASTI-GRIT Type II thermoset urea-formaldehyde, antistatic-treated, no inorganic fillers | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6A28F1EC3A1DBA6CD5B4 | PPS Film | E;nu | 0/1 | 1 |
| RESEARCH-MAT-07152D69F8C2E64C3CC1 | PVDF-HFP Film/Sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B5679F8C54358201F7BE | PearlbondEcoD590 bTPU with graphene 0.5wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 0.5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-08181F51B860AEA57890 | PearlbondEcoD590 bTPU with graphene 1.5wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 1.5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3A73B039CB63F00A7C0C | PearlbondEcoD590 bTPU with graphene 1wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 1wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AF6C2A8A835DC421D6E2 | PearlbondEcoD590 bTPU with graphene 2wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 2wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4DDA5B900EAD57ACC66E | PearlbondEcoD590 bTPU with graphene 3wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 3wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-96DE6870D089444577CD | PearlbondEcoD590 bTPU with graphene 4wt% and 1-butyl-3-methylimidazolium tetrafluoroborate 4wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DA7CF4FD14A63D7235D2 | PearlbondEcoD590 bTPU with unmodified graphene 1wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E64D98FDFD1FE7C56DBB | PearlbondEcoD590 bTPU with unmodified graphene 2.5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-61CB4D5DDDEDE808CB75 | PearlbondEcoD590 bTPU with unmodified graphene 3.5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9F4BDE5572C0AF6FD9DE | PearlbondEcoD590 bTPU with unmodified graphene 3wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1C054202A6B56B090BD1 | PearlbondEcoD590 bTPU with unmodified graphene 4wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A7FB5AAD35C3B602987C | PearlbondEcoD590 bTPU with unmodified graphene 5wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3EB4D797DCC520939982 | PearlbondEcoD590 bTPU with unmodified graphene 6wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9253F1A8321B732E1B28 | PearlbondEcoD590 bTPU with unmodified graphene 7wt% | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A9D7F1AC1DAB913880EB | Plenco 02000 series organic-filled phenolic molding compound, granular bulk | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7ACD3C5490CF4BD1380B | Poly(lactic acid) Ingeo 4043D | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FA8052AF37B8C0A238FD | Poly(lactic acid) Ingeo 4043D with10wt% wet-blue leather-waste fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-575D034EE3C345313E62 | Poly(urea-formaldehyde) microcapsule shell wall, Keller-Sottos in-situ polymerized | nu;rho | 0/3 | 1 |
| RESEARCH-MAT-7F9E5C21314A659AAD12 | PolyJet Fullcure720 cured photopolymer resin | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3F3F03B611EA307BA983 | Polyamide12 Grilamid XE3982 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CD68EC08EED2E7628435 | Polyamide12 Grilamid XE3982 with10wt% wet-blue leather-waste fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3E526D51A20294D8F4D2 | Polyaramid Honeycomb Panel | E;nu | 0/1 | 1 |
| RESEARCH-MAT-680EFEA3A2F4413A6A1F | Polyester/MPF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-19496B71E866E1CDD839 | Polyester/NPF composite | nu;rho | 0/1 | 1 |
| MAT-POLYRESIN-BROAD | Polyresin, formulation unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-858F1E1BA491EC9E3821 | Polyurethane Rod | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F9559DD57FC1BB4E875A | Priplast3192/IPDI/DMPA/EDA polyurethaneurea freeze-driedprintedporousbody,2wt% carboxylatedhardwoodCNF inink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-ACC81E9BF0F4F81C9000 | Priplast3192/IPDI/DMPA/EDA polyurethaneurea freeze-driedprintedporousbody,2wt% unmodifiedhardwoodCNF inink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-ECC6A3D58B612E3D58B1 | Priplast3192/IPDI/DMPA/EDA polyurethaneurea freeze-driedprintedporousbody,3wt% carboxylatedhardwoodCNF inink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6755A759284A5B7FC8E0 | Priplast3192/IPDI/DMPA/EDA polyurethaneurea freeze-driedprintedporousbody,3wt% commercialMaineCNF inink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-557C2EBDB667F3053F91 | Priplast3192/IPDI/DMPA/EDA polyurethaneurea freeze-driedprintedporousbody,3wt% unmodifiedhardwoodCNF inink | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E4CF61414ECDC10E93F6 | RP806/19 polyacrylonitrile-based acrylic finishingfilm,metal-free retannedD2leatherpowder 10mg/mL | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CB75BCB45FCAF25A9D55 | RP806/19 polyacrylonitrile-based acrylic finishingfilm,metal-free retannedD2leatherpowder 30mg/mL | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-243EE89E5982191D2F91 | RP806/19 polyacrylonitrile-based acrylic finishingfilm,unfilled | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B96E78E44AC3F0085858 | SABIC CYCOLOY FR RESIN CS9610 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7D9823A3E44360CF1D51 | SABIC CYCOLOY FR Resin RCM6134 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C33458434DB9288E5555 | SABIC LEXAN COPOLYMER 4501 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B719609C53E49030E0CD | SABIC LEXAN COPOLYMER 4701R | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8E2D283EF1E9BC75D958 | SABIC NORYL GTX RESIN GTX674PC | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-70A61E09EC77B33DACCC | SABIC ULTEM RESIN 1040A | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A1DCF7A0E24863401993 | SABIC ULTEM RESIN 1285 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CCBA91D81B65F63BC487 | SABIC ULTEM RESIN DU242 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-80D6CFBAFB99DF010976 | SABIC ULTEM RESIN DU262 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AA849E8774D39676F1C4 | SABIC ULTEM RESIN DU442 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-961D1DBB2A030424187F | SABIC ULTEM RESIN SF2255 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9F8BBEBEF450076E7098 | SABIC ULTEM Resin 1100 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-94793F17547C4BD424CB | SABIC ULTEM Resin 1100F | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A41BD93DC91CCA525673 | SABIC ULTEM Resin 1110 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D91771BC63AA2230EBF5 | SABIC ULTEM Resin 1110F | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3DA5F2352B40F4B908A6 | SABIC ULTEM Resin 2100 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9D6CC1010992630614BB | SABIC ULTEM Resin 2100F | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5E14368A33307681305A | SABIC ULTEM Resin 2100R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C91DD19D8AA3718F969E | SABIC ULTEM Resin 2110 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-568EBB1293A3E2BD2D58 | SABIC ULTEM Resin 2110EPR | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8B14FA361DE806D6C22F | SABIC ULTEM Resin 2110G | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2280751739AA305563FF | SABIC ULTEM Resin 2110R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1F96B7EB677F15A2A925 | SABIC ULTEM Resin 2200 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D1EDEB00C59B801323FE | SABIC ULTEM Resin 2200R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FA3FC6306606D01C1210 | SABIC ULTEM Resin 2210 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0BF7A8AF96965F0F11D3 | SABIC ULTEM Resin 2210EPR | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D49F0613FA3CA9AB1AC7 | SABIC ULTEM Resin 2210R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-27C091F3ED4537610FB8 | SABIC ULTEM Resin 2212R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AD462F916892073AB733 | SABIC ULTEM Resin 2312 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3C66BABE4042978E4F5D | SABIC ULTEM Resin 2410 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C9FDBCDEE3A7C54977B4 | SABIC ULTEM Resin 2410R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-242DE9EA8B252C042657 | SABIC ULTEM Resin 4001 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-72D622E4A80EE5896C34 | SABIC ULTEM Resin 9075 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FC90F632CBF731E6F116 | SABIC ULTEM Resin AR9100 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-55627FB97EFD41B3146F | SABIC ULTEM Resin AR9110 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D956D7BBB42CECD26D34 | SABIC ULTEM Resin AR9200 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5E1428D21A17869970DF | SABIC ULTEM Resin AR9300 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4A10B5F46A89056C5457 | SABIC ULTEM Resin CRS5001 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D13A1C9AF55A19D8C454 | SABIC ULTEM Resin CRS5011 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EC9E0323199064CA5712 | SABIC ULTEM Resin CRS5111 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4BAF787776F31D42B73F | SABIC ULTEM Resin CRS5201 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D94183DCAD5E3993483F | SABIC ULTEM Resin CRS5201R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-75AB2ABCAD91E80CCC38 | SABIC ULTEM Resin CRS5211R | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-ABB55EC2943AF190FED6 | SABIC ULTEM Resin CRS5301 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7BBA773ABEB56D61E11C | SABIC ULTEM Resin CRS5311 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-70E9A82416652A459D82 | SABIC XENOY FR RESIN ENH2900 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5FEFC1E30B205C3A1853 | SABIC XENOY FR Resin ENH2901RC | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C3FBCAF581D53990B670 | SMP Technologies MM2520 thermoplastic polyurethane,unfilled | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B02245F3D29561065972 | SPLA/MPF2 composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AF5A26795BC1F4B56A9D | SPLA/NPF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E460F18C6AF6CB493076 | Silicone Elastomer Rod | E;nu | 0/1 | 1 |
| RESEARCH-MAT-4537AA8A8AB3CEEA2BEF | TBC cast polyresin matrix compounded with mineral flour | E;nu | 0/1 | 1 |
| RESEARCH-MAT-523D3FD0E653E91B4328 | TPS cassava/MBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-104D8C2C8F375761CAE8 | TPS cassava/NBF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6853156EBFFF35E0C072 | TPS corn/MPF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AB2B318E01C35AAA5F15 | TPS corn/NPF composite | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BB47E25EAC9307FF481D | Teflon PFA Copolymer Film/Sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CDF85F89BD66CA8B1E84 | Teknos Drywood Acrylic 2 wood-coating free films | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AD92AD77EEC951BCE557 | Teknos Drywood Alkyd 1 wood-coating free films | nu;rho | 0/1 | 1 |
| SOURCE-MAT-6A43880421CB826B4A9B | vinyl — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## rubber (134 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-E96F52CB2B06729181D4 | Bio-based TPU ESTANE ECO12T80E unfilled | nu | 0/1 | 1 |
| RESEARCH-MAT-D3A8C1221B1DD93A818F | Industrial latex rubber elastic sheet | rho | 0/2 | 1 |
| RESEARCH-MAT-E14C12936E6C3EC1AA68 | Monodomain side-chain acrylate liquid-crystal elastomer A6OCB-RM82-EHA | rho | 0/1 | 1 |
| RESEARCH-MAT-15F53258BA8B5176C265 | Sylgard 184 PDMS silicone elastomer | rho | 0/1 | 1 |
| RESEARCH-MAT-5B95857B678721B5D6D1 | Ecoflex00-10 silicone elastomer | nu;rho | 0/2 | 2 |
| RESEARCH-MAT-8AD77D2992AC3A4E1C09 | Ecoflex00-30 silicone elastomer | nu;rho | 0/2 | 2 |
| RESEARCH-MAT-1F148943E56957ED1FC6 | Sylgard 184 silicone elastomer | nu;rho | 0/2 | 2 |
| RESEARCH-MAT-88EEA50D993863A77B56 | 110-2 VMQ silicone rubber electrode with SCCB12phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D0305939B9823C9798E3 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP100phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D387E9E9A0FCF4A165A7 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP150phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-10AC622AB0471DEE1363 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP150phr/SWCNT1phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DCD5307C120A444DADE9 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP150phr/SWCNT2phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-401C33BB343D2B1EE311 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP150phr/SWCNT3phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-92AB33274B7FB8E46BAB | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP150phr/SWCNT4phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-15F50EC0F4CD021C6F83 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP200phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A9766D0A8C1DF91DF850 | 110-2 VMQ silicone rubber electrode with SCCB12phr/FMSP50phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-731D750FCB26AAAD82C7 | 110-2 VMQ silicone rubber electrode with SCCB14phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8DAD918A7019EC7F54A3 | 110-2 VMQ silicone rubber electrode with SCCB16phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F1FDD22AF945DBDD8176 | 110-2 VMQ silicone rubber electrode with SCCB18phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-07C4653EF9849A4569FE | 110-2 VMQ silicone rubber electrode with SCCB20phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-714B6C1B500DCD7F9E2B | 110-2 VMQ silicone rubber electrode with SWCNT2phr-only control | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2375C01785207EAAFD9D | 3Lnaturalrubber sulfurcuredcompound,unfoamedcontrol | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CD05F228798D61607A21 | 3Lnaturalrubber sulfurcuredfoam,azodicarbonamide20per100NR | E;nu | 0/1 | 1 |
| RESEARCH-MAT-798FD9A2E64C603BB8CD | 3Lnaturalrubber sulfurcuredfoam,bamboofibre20per80NR,AC20 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-A70010E1866BAD6A1C58 | 3Lnaturalrubber sulfurcuredfoam,distillersgrainfibre20per80NR,AC20 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6CA338DAD6B0370D1F47 | 3Lnaturalrubber sulfurcuredfoam,leathershavingcollagenfibre20per80NR,AC20 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3698FF3FDBF07AA710A4 | 90-degree woven polyester fabric cast in silicone elastomer layer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-60F292F4D1EBF95EDED1 | Ayache etal. laboratory-molded polychloroprene rubber | nu;rho | 0/3 | 1 |
| RESEARCH-MAT-3D1BD34511C6B9004A60 | Bio-based TPU ESTANE ECO12T80E with10wt% glutaraldehyde-tanned bovine leather fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-940ED76BD70585D5CF6B | Bio-based TPU ESTANE ECO12T80E with20wt% glutaraldehyde-tanned bovine leather fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-04E8844F12CD692FE103 | Bio-based TPU ESTANE ECO12T80E with30wt% glutaraldehyde-tanned bovine leather fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-CE480E573782AC76DBA2 | Commercial black 5 mm neoprene sheet supplied by Brammer UK | E;nu | 0/1 | 1 |
| RESEARCH-MAT-947F019411E4FCDB016C | Cured PDMS silicone rubber with 0wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-382918E87E45E23164E8 | Cured PDMS silicone rubber with 10wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-2333553F106744005507 | Cured PDMS silicone rubber with 20wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FF53F94300F9C752A3F1 | Cured PDMS silicone rubber with 30wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-BCEFF7729F77E9E9796F | Cured PDMS silicone rubber with 40wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FFBF16D463FA3D0A46D0 | Cured PDMS silicone rubber with 50wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D9702C58FED0128A2026 | Cured PDMS silicone rubber with 60wt% WO3 nanoparticles (40nm) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E7F0F4CA132D60E3557F | Cured silicone rubber radiation-shield compound, micro-Bi2O3 10wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1C4BF3B0797FDF7A1910 | Cured silicone rubber radiation-shield compound, micro-Bi2O3 20wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-17376206E5F415027814 | Cured silicone rubber radiation-shield compound, micro-Bi2O3 30wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-5B409E3690DB2433AF18 | Cured silicone rubber radiation-shield compound, micro-Bi2O3 5wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-36F3EEE2171A5AF2131F | Cured silicone rubber radiation-shield compound, nano-Bi2O3 30wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-58BC66820BEFBBD40A9C | Cured silicone rubber radiation-shield compound, nano-Bi2O3 5wt% | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3097D4A5ACCF4AE0842D | Cured silicone rubber radiation-shield compound, unfilled control | E;nu | 0/1 | 1 |
| RESEARCH-MAT-37B6E47082E635AA4326 | DCP-cured EPM J-0050/isoprene rubber2200 blend 0/100 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5828D52F145C41B81221 | DCP-cured EPM J-0050/isoprene rubber2200 blend 100/0 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-57DD6A4023D83DA4B6D5 | DCP-cured EPM J-0050/isoprene rubber2200 blend 20/80 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4D16B858ABC12EC3543D | DCP-cured EPM J-0050/isoprene rubber2200 blend 30/70 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5C1A4D3DA1EBD8D447C6 | DCP-cured EPM J-0050/isoprene rubber2200 blend 40/60 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EBA42281F511AD2C59CE | DCP-cured EPM J-0050/isoprene rubber2200 blend 50/50 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A0EE20A9FF6F4DC36605 | DCP-cured EPM J-0050/isoprene rubber2200 blend 60/40 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-98EA64DE94198A5C2A04 | DCP-cured EPM J-0050/isoprene rubber2200 blend 70/30 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C989520DF32E8320BA3D | DCP-cured EPM J-0050/isoprene rubber2200 blend 80/20 mass ratio | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D55CA3AFFD3FAEF29BE7 | DCP-cured EPM J-0050/isoprene rubber2200 blend40/60 with AerosilR974 silica 10phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EB335B758B021E203674 | DCP-cured EPM J-0050/isoprene rubber2200 blend40/60 with AerosilR974 silica 20phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9E60D2C15A3D2672A4BF | DCP-cured EPM J-0050/isoprene rubber2200 blend40/60 with AerosilR974 silica 30phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F0D74807E83ECFF85ABE | DCP-cured EPM J-0050/isoprene rubber2200 blend40/60 with AerosilR974 silica 40phr | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-802E186A099D8C678C04 | Diving neoprene sheet M1NO | E;nu | 0/3 | 1 |
| RESEARCH-MAT-E0A8842B3F1B6E39E08F | Diving neoprene sheet M1OSa | E;nu | 0/3 | 1 |
| RESEARCH-MAT-C70016C8D08CCDF5075A | Diving neoprene sheet M1OSb | E;nu | 0/3 | 1 |
| RESEARCH-MAT-29E8362DF269449F4C29 | Diving neoprene sheet M2BS | E;nu | 0/3 | 1 |
| RESEARCH-MAT-0C7EB09A4CB5B88FBF1E | Diving neoprene sheet M2NO | E;nu | 0/3 | 1 |
| RESEARCH-MAT-CD1DC211808EE00ECD5E | Diving neoprene sheet M2OS | E;nu | 0/3 | 1 |
| RESEARCH-MAT-0CA5F4B58BA697C1A842 | Diving neoprene sheet M3NOa | E;nu | 0/3 | 1 |
| RESEARCH-MAT-3751001061DB9F8F74EF | Diving neoprene sheet M3NOb | E;nu | 0/3 | 1 |
| RESEARCH-MAT-DAE5940167C902EB49ED | Diving neoprene sheet M3NOc | E;nu | 0/3 | 1 |
| RESEARCH-MAT-E23D4EE78914B47717EA | Diving neoprene sheet M4BS | E;nu | 0/3 | 1 |
| RESEARCH-MAT-986DC33519ED873901EA | Diving neoprene sheet M4OS | E;nu | 0/3 | 1 |
| RESEARCH-MAT-7B10E7AC3359007801A8 | Dow Sylgard184 PDMS layered bond,base:crosslinker10:1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FDA655E8BED96973DE9F | Dow Sylgard184 PDMS layered bond,base:crosslinker10:1,crosslinker adhesive interlayer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FB6D7D8C7462FBB50008 | Dow Sylgard184 PDMS layered bond,base:crosslinker20:1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-720905A8862EEC58EF56 | Dow Sylgard184 PDMS layered bond,base:crosslinker20:1,crosslinker adhesive interlayer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3816D8231195184C73D7 | Dow Sylgard184 PDMS layered bond,base:crosslinker30:1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0CBB26ACDA2338C4B061 | Dow Sylgard184 PDMS layered bond,base:crosslinker30:1,crosslinker adhesive interlayer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-76FB9F65E448EE815760 | Dow Sylgard184 PDMS layered bond,base:crosslinker40:1 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3562D25795A42E6BD938 | Dow Sylgard184 PDMS layered bond,base:crosslinker40:1,crosslinker adhesive interlayer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BE734C99710FC930AD58 | Dragon Skin10Slow silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-98254FE5017ECE8AFC0A | Dragon Skin20 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FB97F5252FF0F8298B1F | Dragon Skin30 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7BABD27D0CB6430E54A4 | Ecoflex 00-50 platinum-cured silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2E0FD942F288F689009B | Ecoflex00-20 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8E9009DF3D7AE39CA050 | Ecoflex00-50 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-727219DE0C7693D32482 | Elastosil M4511 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-24802F610C4DFB388299 | Elastosil RT601 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B84AF34243D4EB508306 | Elastosil RT620 A/B silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D6C5048FBC3BEDE96B14 | Elastosil RT625 A/B silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5E69FFF4EF51D3759FB5 | Elastosil Vario15 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-32F9794700F2E283C3BC | Gamma-crosslinked carboxymethylcellulose/polyacrylicacid/tannicacid elastomer,CMC2gAAc20mLTA0.5gper100mL | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-23862C38A1FCF5978004 | Homemade DMS-V31/HMS-301 PDMS elastomer with20phr treated silica | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DB0D4DF6D19195992AA9 | Homemade DMS-V31/HMS-301 platinum-cured unfilled PDMS elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-70A57E4DA03EF618CE93 | Latexco RG 65 latex rubber foam | E;nu | 0/1 | 1 |
| RESEARCH-MAT-A788A8DE8EE47BCF074D | Methyl vinyl silicone rubber VMQ,source vibration-isolation formulation | E;rho | 0/1 | 1 |
| RESEARCH-MAT-6E6A694E01F5FC4731DD | NR70/SBR30 tyre-tread rubber with N330 carbonblack23phr/MWCNT7phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-98DB00F2544FBB3AD47B | NR70/SBR30 tyre-tread rubber with N330 carbonblack27phr/MWCNT3phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EBCEA94AB713A713189D | NR70/SBR30 tyre-tread rubber with N330 carbonblack30phr/MWCNT0phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CFFF90DE663A24CB0779 | Nonvulcanized natural rubber McMaster-Carr strip | E;rho | 0/1 | 1 |
| RESEARCH-MAT-054BF05B137D89EEA9B6 | Phenolicresin-vulcanizedPP/EPDMthermoplasticvulcanizate,TPV1injectiongrade | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B104817EE979529A16C7 | Phenolicresin-vulcanizedPP/EPDMthermoplasticvulcanizate,TPV2extrusiongrade | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B1C5DAE49E462247FE5C | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 100:0 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4C2D60176971289109A1 | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 35:65 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-43CD6BCFCA74065E0DA8 | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 40:60 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DE739FCE696BAEECDD95 | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 45:55 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BCF71C6CB5DD1AB3B1A7 | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 80:20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-01D86B4D487856AB048D | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 85:15 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1D37EBC05905A106DA26 | PlatsilGel0030 silicone/PMX200 siliconeoil phantom,softgel:oil 90:10 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5511F88A6C0E4E0DF86F | PolyJet Agilus30 Black elastomeric photopolymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-8C15172CA5B12A8224B6 | PolyJet Agilus30 Clear elastomeric photopolymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-ACCE751F6B77BEE12F16 | PolyJet IORA Model Flex30A White elastomeric photopolymer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FEF69CFA40798B22801C | Polycraft GP3481-F RTV silicone rubber with RTC-10F/VF catalyst20:1 | E;rho | 0/1 | 1 |
| RESEARCH-MAT-72C1D258C6EB509F28E4 | Powersil XLR630 A/B silicone elastomer | nu;rho | 0/1 | 1 |
| MAT-RUBBERIZED-MATERIAL-SOURCE-BROAD | Rubberized material, substrate/construction unspecified | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-DD6CADDFED1DB61C41AA | SEBS-polyolefin thermoplastic elastomer Marfran KP330 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5A0E6FA0E43A25EB8BA6 | SEBS-polyolefin thermoplastic elastomer Marfran KP330 with10wt% wet-blue leather-waste fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E3855E85AA4911F0D08F | Silbione RTV4410QC A/B silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1F0E681D6B5A5C2B1BCB | Smooth-On silicone mixture Dragon Skin 10S - Ecoflex 00–30 40/60 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4A8340AE0E3B30367A55 | Smooth-On silicone mixture Dragon Skin 10S - Ecoflex 00–30 60/40 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-02A17590502D330B83F2 | Smooth-On silicone mixture Dragon Skin 10S - Ecoflex 00–30 80/20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E53E86C16B029A4B6874 | Smooth-On silicone mixture Dragon Skin 10S—Ecoflex 00–30 20/80 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-35113D834CCF6BECF867 | Smooth-On silicone mixture Dragon Skin 20 - Ecoflex 00–30 50/50 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-2B795AFB1E76A911A9D7 | Smooth-On silicone mixture Dragon Skin 30 - Ecoflex 00–10 50/50 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-ED2A286C2CDE3B51535B | Sulfur-cured natural rubber with finished leather residues 0phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-492F2AB323D54B7329CD | Sulfur-cured natural rubber with finished leather residues 10phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EE6C8ECDEA90B9E2585C | Sulfur-cured natural rubber with finished leather residues 20phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D6BB97D3B13870B01539 | Sulfur-cured natural rubber with finished leather residues 30phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FEDBEB954B2A38AA6082 | Sulfur-cured natural rubber with finished leather residues 40phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-818FB2CF150D9FA202D1 | Sulfur-cured natural rubber with finished leather residues 50phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-993F897B33B0E625BD51 | Sulfur-cured natural rubber with finished leather residues 60phr | E;nu | 0/1 | 1 |
| RESEARCH-MAT-4C2B13EC611694B72AF8 | Sylgard186 silicone elastomer | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F34617275D1557D75DB8 | Thermoplastic polyurethane Elastollane 11600 D50 (source spelling) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7698DE923DC290897A43 | Thermoplastic polyurethane Elastollane 11600 D50 (source spelling) with10wt% wet-blue leather-waste fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-BBDB54AB438CF0357407 | Trapped-rubber-processing silicone rubber | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B2F3512D13053AB8A1A9 | Unfilled polychloroprene rubber | E;rho | 0/1 | 1 |

## stone (17 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| RESEARCH-MAT-23C2AF0B944BCEE3C230 | Sandstone | rho | 0/63 | 8 |
| RESEARCH-MAT-7E94570B631441CCD06F | Strathbogie granite | rho | 0/29 | 2 |
| RESEARCH-MAT-87E2E8EBAEF474F3B410 | Australian granite | rho | 0/15 | 1 |
| RESEARCH-MAT-B17FB1BFE151495F4C4D | Indian sandstone | rho | 0/11 | 1 |
| RESEARCH-MAT-E6635D2BC476621BA787 | Prada limestone | rho | 0/12 | 1 |
| RESEARCH-MAT-D69DE28AC212D7C4FA58 | Stripa granite | rho | 0/14 | 1 |
| RESEARCH-MAT-B080BAD23EDED2D32CB3 | Valdieri marble | rho | 0/4 | 1 |
| RESEARCH-MAT-2D9F78BDBD0FB6FE9A49 | Basalt | nu;rho | 0/5 | 1 |
| RESEARCH-MAT-F33FEEE49D749288BDE6 | Beishan granite | nu;rho | 0/7 | 1 |
| RESEARCH-MAT-CA5A46AA6795ECF783E1 | Diorite | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-60E483EC73D410178EBB | Fine-grained marble | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-3EF1E40C0403EFE3159A | Hawkesbury sandstone | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-E07B7F90D4641B4A6D92 | Homogeneous sandstone | nu;rho | 0/11 | 1 |
| RESEARCH-MAT-FEFF81CC61F998F1F0CF | Indian Gondwana shale | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-BBEA249997DC6DF29170 | Qinling biotite granite | nu;rho | 0/7 | 1 |
| RESEARCH-MAT-7A6C8D7F77272123DAEB | San Julian's calcarenite | E;rho | 0/12 | 1 |
| MAT-MARBLE-CALCITE | Marble, calcite-based, grade unspecified | E;nu;rho | 0/0 | 0 |

## textile (231 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| MAT-TEXTILE-POLYPROPYLENE-BROAD | Polypropylene fibre/textile, construction unspecified | nu | 0/29 | 7 |
| MAT-TEXTILE-PET-BROAD | PET fibre/textile, construction unspecified | nu | 0/13 | 5 |
| MAT-TEXTILE-ACRYLIC-BROAD | Acrylic fibre/textile constituent, formulation/construction unspecified | nu | 0/4 | 3 |
| MAT-TEXTILE-OLEFIN-BROAD | Olefin textile fibre, polymer/construction unspecified | nu | 0/6 | 3 |
| MAT-TEXTILE-MESH-BROAD | Mesh textile, fibre/construction unspecified | nu | 0/5 | 2 |
| MAT-TEXTILE-RECYCLED-COTTON-BROAD | Recycled cotton fibre/textile, process/construction unspecified | nu | 0/6 | 2 |
| MAT-TEXTILE-SISAL-BROAD | Sisal fibre/textile, construction unspecified | nu | 0/2 | 2 |
| RESEARCH-MAT-CF923D04F6615FE966FA | Sisal natural fibre | nu | 0/2 | 2 |
| RESEARCH-MAT-3BA10CA3F121AE1E9189 | Spider silk natural fibre | nu | 0/2 | 2 |
| RESEARCH-MAT-CC7A0BE1811D4E34417A | Wool fibre | rho | 0/7 | 2 |
| RESEARCH-MAT-F58FEA8423126EF6C50A | Abaca (Manila hemp) rope | nu | 0/1 | 1 |
| RESEARCH-MAT-EC0723D7E6A8CB797412 | Aramid fibre | nu | 0/2 | 1 |
| RESEARCH-MAT-EC54D792E86F80B46EFC | Bundled polypropylene monofilament fibre, Jinan Shunjie Engineering Materials | nu | 0/1 | 1 |
| RESEARCH-MAT-550264960BB65229338D | Carbonised rayon-derived carbon felt, Beijing Great Wall RSF1 | nu | 0/1 | 1 |
| RESEARCH-MAT-3A77284693E2D5660A33 | Carbonised rayon-derived carbon felt, CeraMaterials | nu | 0/1 | 1 |
| RESEARCH-MAT-20C4D9A005BC52DAEDC0 | Carbonised rayon-derived carbon felt, SIGRATHERM KFA5 | nu | 0/1 | 1 |
| RESEARCH-MAT-FFE7D22A88EEC2988663 | Carbonised thick PAN-precursor carbon felt, Beijing Great Wall PSF1 | nu | 0/1 | 1 |
| RESEARCH-MAT-D845994170F7D09BFDBF | Carbonised thick PAN-precursor carbon felt, CeraMaterials | nu | 0/1 | 1 |
| RESEARCH-MAT-191330B041F7A18F3849 | Carbonised thin PAN-precursor carbon felt, Beijing Great Wall BESF | nu | 0/1 | 1 |
| RESEARCH-MAT-C9BBF10C4C7CF35D0772 | Carbonised thin PAN-precursor carbon felt, ZOLTEK PX35 | nu | 0/1 | 1 |
| RESEARCH-MAT-AD9FE1895E6C08FC4187 | Cellulose base material of cotton fibres | nu | 0/1 | 1 |
| RESEARCH-MAT-7B11CE4E5605B43198FD | Chemically rigidised carbonised PAN-derived carbon felt, CeraMaterials Carbon Board | nu | 0/1 | 1 |
| RESEARCH-MAT-BE42CA9355F21AEE4733 | Chemically rigidised graphitised PAN-derived carbon felt, Beijing Great Wall PRF3 | nu | 0/1 | 1 |
| RESEARCH-MAT-10D32B7CE33A343A675D | Coir natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-4E1831657FD762EE963D | Cotton 12.4wt%/TEOS-isoBTES silica aerogel composite — matrix precursor ratio 82-18 TEOS-isoBTES | nu | 0/1 | 1 |
| RESEARCH-MAT-279314A6F218FEE24532 | Cotton 13.5wt%/TEOS-isoBTES silica aerogel composite — matrix precursor ratio 82-18 TEOS-isoBTES | nu | 0/1 | 1 |
| RESEARCH-MAT-A1492BBE0D231EE15B66 | Cotton 8.5wt%/TEOS-isoBTES silica aerogel composite — matrix precursor ratio 82-18 TEOS-isoBTES | nu | 0/1 | 1 |
| RESEARCH-MAT-0CF6A52FCA6E2A11192A | Cotton Gossypium hirsutum/Gossypium barbadense fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-C816AD2C540A3E9849C6 | Cotton rope | nu | 0/1 | 1 |
| MAT-TEXTILE-FELT-SOURCE-BROAD | Felt material, fibre/process unspecified | nu | 0/15 | 1 |
| RESEARCH-MAT-1D8430B14C0A8171D9F5 | Flax Linum usitatissimum fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-C3C6B9242C1D26AE7C7D | Flax natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-B3F1B2E43B380069F500 | Flax rope | nu | 0/1 | 1 |
| RESEARCH-MAT-9E873DD4C6E2B9F6EB6C | Graphitised rayon-derived carbon felt, Beijing Great Wall RSF2 | nu | 0/1 | 1 |
| RESEARCH-MAT-3E378B078153DDE181CF | Graphitised rayon-derived carbon felt, CeraMaterials | nu | 0/1 | 1 |
| RESEARCH-MAT-AC486EDC27B08D197835 | Graphitised rayon-derived carbon felt, SIGRATHERM GFA10 | nu | 0/1 | 1 |
| RESEARCH-MAT-A84DE03C3DF0F4621918 | Graphitised rayon-derived carbon felt, Schunk GF2 | nu | 0/1 | 1 |
| RESEARCH-MAT-667859D9FD39EB809A4D | Graphitised thick PAN-precursor carbon felt, Beijing Great Wall PSF2 | nu | 0/1 | 1 |
| RESEARCH-MAT-B79E79AAF116F77432C1 | Graphitised thin PAN-precursor carbon felt, CeraMaterials GFE-1 | nu | 0/1 | 1 |
| RESEARCH-MAT-0BBE035E2E0DC9B41B96 | Hemp natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-3C30605680B21108410F | Hemp rope | nu | 0/1 | 1 |
| MAT-TEXTILE-HEMP-ROPE-SOURCE-BROAD | Hemp rope, fibre species/construction unspecified | nu | 0/1 | 1 |
| RESEARCH-MAT-CFA6B4B1B9B0A68C7637 | Jute natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-04B24D49A63D73D0FCE1 | Jute rope | nu | 0/1 | 1 |
| RESEARCH-MAT-9DA36259E79264EB1CFB | Liquid crystal aromatic polyester (LCP) fiber | nu | 0/1 | 1 |
| RESEARCH-MAT-821BA8DF6DE37CD38CBE | Mulberry silkworm fiber natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-1C673EA8D2723298971C | Needle-punched 30% post-consumer leather residue with recycled-polyester matrix (source percentage basis not explicit) nonwoven | nu | 0/1 | 1 |
| RESEARCH-MAT-4523E3152E03E3E7518D | Needle-punched 40% mixed post-consumer footwear residue with recycled-polyester matrix (source percentage basis not explicit) nonwoven | nu | 0/1 | 1 |
| RESEARCH-MAT-5CEBFD4D4F74A577878F | Needle-punched compression-molded 30% post-consumer leather residue with recycled-polyester matrix (source percentage basis not explicit) nonwoven | nu | 0/1 | 1 |
| RESEARCH-MAT-05EE6108AB64EE400F24 | Needle-punched compression-molded 40% mixed post-consumer footwear residue with recycled-polyester matrix (source percentage basis not explicit) nonwoven | nu | 0/1 | 1 |
| RESEARCH-MAT-4A153BA0D6115686CF2B | Nylon fiber | nu | 0/1 | 1 |
| RESEARCH-MAT-8EDFE6F8C252C6A6D09D | Nylon-6 monofilament (Nylon A) | E | 0/1 | 1 |
| RESEARCH-MAT-ACEC6FA19638E4587D13 | Pineapple natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-110C7788388CBE1E9E4A | Polybenzoxazole (PBO) fiber | nu | 0/1 | 1 |
| RESEARCH-MAT-DA2DCFBC6457E1998AD5 | Polyester 10.9wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 73-27 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-B03F6C6FB0996BC240E1 | Polyester 13.0wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 82-18 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-91BCD985EA1A56E00E1D | Polyester 16.0wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 73-27 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-A4773F68FDBE8CFB7FF8 | Polyester 17.1wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 82-18 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-9575733271B363F934AB | Polyester fiber | nu | 0/1 | 1 |
| RESEARCH-MAT-D524A97AD3BF6D63BC0C | Polypropylene chopped monofilament fibre, Hengshui Shengying | nu | 0/1 | 1 |
| RESEARCH-MAT-86BB42654A3138970117 | Silk (silkworm) | nu | 0/1 | 1 |
| RESEARCH-MAT-B564F010A71EE5EB646A | TPU-coated nylon actuator fabric | rho | 0/1 | 1 |
| RESEARCH-MAT-0CD68BC002A683A8444B | Wild (Tussah) silkworm fiber natural fibre | nu | 0/1 | 1 |
| RESEARCH-MAT-2704A3171E722B20A734 | Wool 10.2wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 73-27 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-2E9903F35F6E7D2386B5 | Wool 11.3wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 82-18 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-555D4F2E050699CD0789 | Wool 13.6wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 73-27 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-4BB7C69F13EE4BDFB51D | Wool 14.8wt%/TEOS-VTMS silica aerogel composite — matrix precursor ratio 82-18 TEOS-VTMS | nu | 0/1 | 1 |
| RESEARCH-MAT-A765ABBA73F088BE25B8 | Polyester (PET) fibre | nu;rho | 0/4 | 2 |
| RESEARCH-MAT-906E5C272CAD4E5C56A7 | 100% polyester fleece acoustic sheet | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7D1214D92DED90BD52CF | 100% polyester nonwoven upholstery/mattress batting | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FCEFAFC09196BCCDF3D5 | 100% rayon chamoix fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7115B5BD4682DCF108B8 | 100% woven cotton laparotomy sponge fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-E934B42AFC353E18F236 | 20% nylon / 80% polyester composite microfiber towel | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C9BF6EF6E9ACD835CA85 | 80% recycled hollow PET /20% bicomponent-PET thermo-bonded nonwoven | E;nu | 0/2 | 1 |
| RESEARCH-MAT-28AA2EBBF9AF3C00003A | 80% recycled solid PET /20% bicomponent-PET thermo-bonded nonwoven | E;nu | 0/1 | 1 |
| RESEARCH-MAT-08DB3DA6FF30E776B45D | AB Linas T561 plain linen-warp cotton-and-amber-weft fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-B59992E6B9736D209011 | Acrylic textile fibre (at least85% acrylonitrile units), reviewed broad fibre family | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7BF3B8A3D0ECCE383BE9 | Asahi Kasei Cupro B4615 regenerated cellulose fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D5B3F89B1DFCD9374FC4 | BNC Lyocell fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-45A2BFA3A52DAF452AB9 | Bacterial nanocellulose filament | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-35094C03C357C6E1AA5B | Banana lignocellulosic fibre | nu;rho | 0/3 | 1 |
| RESEARCH-MAT-2A76FE6013AA6E8E4260 | Banana natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6204AC92D551E7AD5CA7 | Boric acid treated cotton Needle punched barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-8D1EBDB48C66898D93F6 | Boric acid treated cotton/FR rayon/polyester Needle punched/Stratified barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C03FC8D6558EE1149241 | Camel hair natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D1CBA743D57CF16DF0BB | Cellulose nanofibre filament | nu;rho | 0/9 | 1 |
| RESEARCH-MAT-94ECF4E01D6A8372A14A | Clean washed sheep wool fibers (SWF), density basis unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-62BD15B74F7618D0F60B | Clean washed sheep wool single fibers (SWF) | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FDC028CDE152FA95C1DD | Coconut lignocellulosic fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F4A632739F2E9FA9EBD0 | Cotton fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-61F23246C8BAC94B7883 | Cotton lignocellulosic fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-EE81778A4CCF4FFD2AD1 | Cotton natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-737E34517FE5AD3912BB | Cotton textile comparison specimen | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AA6DA697DF824E949BAC | Cotton/glass fiber Knit/backcoated barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-16043AECEDCA4C39D822 | Cottonpile/cotton-Lycra ground weft-knitted loop-pile fabric | E;nu | 0/1 | 1 |
| MAT-DOWN-FILLING-BROAD | Down/feather filling, ratio unspecified | E;nu | 0/4 | 1 |
| RESEARCH-MAT-A485A61500971BC6FE41 | Duck down feather barb | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-75A10C43BCF8AB66C20A | Duck down feather material | E;nu | 0/2 | 1 |
| RESEARCH-MAT-9A9EB51F11DB4836A02E | Eider down feather barb | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D170BE6D148E577E34CA | Electrospun polyacrylonitrile nanofibre mat | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E45F6688EEC3D5839DF9 | ExxonMobil Achieve 6936G2 polypropylene meltblown nonwoven fabric | E;nu | 0/16 | 1 |
| RESEARCH-MAT-E4AAD2FC76C4AD4E7B03 | FDM SUNLU PLA cylindrical-link structured fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AE4EE1C76C00A64D04A7 | FDM SUNLU PLA prismatic-link structured fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7018BE4C12F869A3117B | FR polyester/FR rayon Stitchbond barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CCA06092AA975E5B059C | FR rayon/glass fiber/Poly Lactic Acid (PLA) fiber Nonwoven barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3F2088366A2BD66A43FD | FR-cotton knit / PET structured needle-bonded nonwoven / FR-cotton-PET warp-knit glove laminate | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D0CA65006F4CC9DA3DC3 | FR-cotton knit / PET structured needle-bonded nonwoven / FR-cotton-PET warp-knit glove laminate with PES microporous membrane | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-656A68029B3812C1039E | FR-cotton knit / PET/viscose/wool needle-bonded nonwoven / FR-cotton-PET warp-knit glove laminate | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-43EC441A86201AF52834 | FR-cotton knit / PET/viscose/wool needle-bonded nonwoven / FR-cotton-PET warp-knit glove laminate with PES microporous membrane | nu;rho | 0/1 | 1 |
| MAT-TEXTILE-FIBER-SOURCE-BROAD | Filling fibre, chemistry unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3B8CD205799DFF4A694F | Five-layer waterproof breathable textile laminate with coated cotton/polyester knit, polyester layers and acrylic-ester/polyester-PU membrane | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6A4D2CDB16DE97A38DD2 | Flame-retardant rayon/polyester highloft barrier fabric | E;nu | 0/2 | 1 |
| RESEARCH-MAT-EDC19DD7F7525FE1C5B3 | Flame-retardant rayon/polyester needle-punched nonwoven barrier fabric | E;nu | 0/3 | 1 |
| RESEARCH-MAT-6CCAFD4991A65D4878D4 | Flax fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-959F95DF836700590B20 | Flax warp / hemp weft blended panama2/2 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-AF1B9FDF96A892480D9A | Flax warp / hemp weft blended plain1/1 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-4AD291FA43BD4A190A59 | Flax warp / hemp weft blended twill2/2 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-35CE5FBBAF4F5DFAAACF | Flax warp and weft panama2/2 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7882E1D8D75CDCFC7F94 | Flax warp and weft plain1/1 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-50A16DCD485EC2A3A383 | Flax warp and weft twill2/2 woven fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CAE3DC4B8CFB281832B3 | Glass fiber core/FR acrylic fiber (core spun yarn) Knitted barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-0A8EDDB2896DE3BAF8C5 | Glass fiber core/FR acrylic fiber Woven barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-D0D44CA51FFAB9EE4526 | Glass filaments Woven barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F091077FC24B91DC9463 | Goose down feather barb | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-9030FCEAB18010A67F0A | Goose down feather material | E;nu | 0/2 | 1 |
| RESEARCH-MAT-18D29367A2424453168C | HC12 Ag-plated nylon conductive yarn235x2dtex | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3319A008A599420D112E | Hemp fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4A792ED927C35A63F70D | Industrial acrylic textile-waste single fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-162CD87A277D6E5C1D9B | Industrial yarn bundle composed of acrylic textile-waste fibres | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3A2BC7B88FD721ACC75A | Ioncell fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AB7029ACB03B2E8A54D6 | Jute fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-97358C01690480A4F4FB | Kenaf natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-6F81EAF51C160D108C3F | Kevlar 49 fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4E5D96E1E882AE71FF9B | Lyocell fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-426239816F9BDC79562C | Machine-embroidered polyester lace, re-entrant honeycomb | E;rho | 0/1 | 1 |
| RESEARCH-MAT-60EFEA337B1EBE08A2F1 | Machine-embroidered polyester lace, re-entrant triangles long sides | E;rho | 0/1 | 1 |
| RESEARCH-MAT-DDA2F9253E56A613B762 | Machine-embroidered polyester lace, re-entrant triangles short sides | E;rho | 0/1 | 1 |
| RESEARCH-MAT-6DB985E616DEA86EC914 | Machine-embroidered polyester lace, rotating semi-rigid squares | E;rho | 0/1 | 1 |
| RESEARCH-MAT-F011C3568AD3138D952F | Machine-embroidered polyester lace, square grid | E;rho | 0/1 | 1 |
| RESEARCH-MAT-9CA3CD2D1EE1E801CEDF | Mesh acoustic fibre sheet, chemistry unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-07B89ABC8EA60194C479 | Meta-aramid/Para-aramid Woven/non-woven composite barrier fabric | E;nu | 0/1 | 1 |
| MAT-TEXTILE-MICROFIBER-BROAD | Microfiber textile, fibre/construction unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9548A3BBA9B445E72B30 | Non-texturized PET multifilament yarn | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F568360F8F722B6F834F | Nonabsorbable polypropylene surgical mesh, Tricomed Optomesh Macropore | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-F0375D86667D0F332347 | Nonabsorbable polypropylene surgical mesh, Tricomed Optomesh Thinlight | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-67F0C5C123D776EEBC95 | Nonabsorbable polypropylene surgical mesh, Yavo Normal | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1F86E66BE786EA2132E9 | Nonabsorbable polypropylene surgical mesh, Yavo Soft | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-47782E78D99B149ACEAE | Nylon-6 monofilament (Nylon B) | E;rho | 0/1 | 1 |
| RESEARCH-MAT-71B9E7EB31F4677F0419 | Nylon-66 filament | E;rho | 0/1 | 1 |
| RESEARCH-MAT-28AF17DBF2A4E6546701 | Nylon/elastane 58/42 warp-knitted Tricot double face fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-7428C7EF2D3F3C398EFC | Nylon/elastane 65/35 warp-knitted Tricot with pillar stitch fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AC52493A7B0C913089B8 | Nylon/elastane 74/26 warp-knitted Tricot single face fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-99E26DA9FCB44AE9C255 | Nylon/elastane 75/25 warp-knitted Tricot (1 × 1) fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D64AB421B3F113FB5A8B | Nylon6 PA fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4DB14BB440344FCA4C43 | PA6.6 three-layer woven fabric, construction A1-16 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-AAB16A45DBFABED1D4CB | PA6.6 three-layer woven fabric, construction A2-20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C1E17763AABBB30E7338 | PA6.6 three-layer woven fabric, construction A3-24 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-983D24013CBBB5C4B711 | PA6.6 three-layer woven fabric, construction B1-20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0DD5F2DE3DD3A74C2ECD | PA6.6 three-layer woven fabric, construction B2-24 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-185650FB0C0349D8D41E | PA6.6 three-layer woven fabric, construction B3-16 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-099038E63BCEB9E3340E | PA6.6 three-layer woven fabric, construction C1-24 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-C6532F614A101B88DFC2 | PA6.6 three-layer woven fabric, construction C2-16 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-4B35A4F9385178CC10EE | PA6.6 three-layer woven fabric, construction C3-20 | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-90C2A1BD74773E6EB3CF | PAN-nanofibre glue-laminated T561 linen-cotton-amber fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-26E3A73D28BB1F0478BD | PTFE-Coated Glass Fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-09381E92EAD23F58673C | Para-aramid Nonwoven barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3D8FAE14683C4AFC6BD7 | Para-aramid/melamine Woven barrier fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-0939C4A271BD366C1F71 | Perlon filament, nylon subtype unspecified | E;rho | 0/1 | 1 |
| RESEARCH-MAT-37E04FEAE84F12632839 | Plain wool-polyester woven cloth | E;rho | 0/1 | 1 |
| RESEARCH-MAT-1129BF75C4C8A5666433 | Plain woven cotton Fabric 3 | E;rho | 0/1 | 1 |
| RESEARCH-MAT-CBCFE74D807FEFC48898 | Plain woven polyester Fabric 1 | E;rho | 0/1 | 1 |
| RESEARCH-MAT-7131E8993CAFE1C2FDD6 | Plain woven polyester Fabric 2 | E;rho | 0/1 | 1 |
| RESEARCH-MAT-14C0D2018CA0CDBC80D7 | Plain woven wool Fabric 4 | E;rho | 0/1 | 1 |
| RESEARCH-MAT-07EBF11B779F88FB8C3D | Polyamide6 multifilament yarn | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-576A12D03348EFFE7239 | Polybutylene terephthalate meltblown nonwoven | E;nu | 0/4 | 1 |
| MAT-TEXTILE-POLYESTER-NYLON-BLEND | Polyester/nylon textile blend, ratio/construction unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-B80E3CCFED4F192979F9 | Polypropylene / natural-cellulose CoForm thermally bonded nonwoven | E;nu | 0/2 | 1 |
| RESEARCH-MAT-B31D5E27F7B351DCB59B | Polypropylene / natural-cellulose carded hydroentangled thermally bonded nonwoven | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7D93BBD5502A5C28F22A | Polypropylene / natural-cellulose spunbond-woodpulp-spunbond hydroentangled thermally bonded nonwoven | E;nu | 0/2 | 1 |
| RESEARCH-MAT-38989A9B67F544DDE133 | Polypropylene fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9A21725FF125EDB40641 | Polypropylene meltblown nonwoven | E;nu | 0/4 | 1 |
| RESEARCH-MAT-4D6E593DE97443B1336D | Polypropylene monofilament warp-knitted circular mesh | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-36E4B1B332C571E032B1 | Polypropylene monofilament warp-knitted dimond mesh | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0B08D761108B70D6CE78 | Polypropylene monofilament warp-knitted rectangular mesh | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9881BB42A3BCF77D1C82 | Polypropylene monofilament warp-knitted square mesh | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-387D9992098387299EFA | Polypropylene multifilament yarn | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-0F4925AD8FDF4A8ACCDB | Polypropylene thermally bonded meltblown commercial nonwoven | E;nu | 0/1 | 1 |
| RESEARCH-MAT-7E72E9FE818F8F56F2B5 | Porous waterborne-polyurethane film with8wt% hydrophobic silica particles (WPU-SP8) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-97EA3EED564716922349 | Queenscord acoustic fibre sheet, chemistry unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-CF17A4BC5188C78D38C7 | Ramie natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E6A733B4F0A1C49BC760 | Rayon-polypropylene chamoix composite fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-EBCA499BCCA4CBFD0B21 | Reactive-dyed recycled cotton flock fibres recovered from spinning waste | nu;rho | 0/4 | 1 |
| RESEARCH-MAT-4C6CB73E13A9D1839808 | Reclaimed cotton industrial blanket | E;nu | 0/1 | 1 |
| RESEARCH-MAT-24B3AAABD457FAF0C9BC | Reclaimed cotton manually carded blanket | E;nu | 0/1 | 1 |
| RESEARCH-MAT-FC35C16841B27FCF00FD | Reclaimed polyester industrial blanket | E;nu | 0/1 | 1 |
| RESEARCH-MAT-3E6E43316C6F5D0674C5 | Reclaimed wool industrial blanket | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9DEF6176FE49C379B103 | Recycled cotton textile-waste / waterborne PVAc / cornstarch cold-pressed composite board, feed mass ratio 70/20/10 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-394DF501E2A543CD97D4 | Recycled cotton textile-waste / waterborne PVAc / cornstarch cold-pressed composite board, feed mass ratio 72/18/10 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-98869D0C28260C9095ED | Recycled cotton textile-waste / waterborne PVAc / cornstarch cold-pressed composite board, feed mass ratio 75/15/10 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-6A5C5A4F76A5432ED76A | Recycled cotton textile-waste / waterborne PVAc / cornstarch cold-pressed composite board, feed mass ratio 78/12/10 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-74E43318CC526F624961 | Recycled cotton textile-waste / waterborne PVAc / cornstarch cold-pressed composite board, feed mass ratio 80/10/10 | E;nu | 0/1 | 1 |
| RESEARCH-MAT-529491AF0B883E3B0AA4 | Regenerated-cellulose viscose carded hydroentangled nonwoven with chemical binder | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C74E891E29A42B716B39 | SLA ANYCUBIC UV-resin annular-link structured fabric | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1A8AD896412C6B614A5F | Silk fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-9B109911859F5624658C | Sprich Baft polyester hexagonal mesh spacer fabric | E;nu | 0/1 | 1 |
| RESEARCH-MAT-F5A64FB0314B3A0FAA9A | Suede acoustic fibre sheet, chemistry unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-C09B806376632E512632 | TEMPO-CNF-surface-treated Cupro B4615 regenerated cellulose fibre | nu;rho | 0/1 | 1 |
| MAT-TEXTILE-TETORON-SOURCE-BROAD | Tetoron source-label fibre, chemistry not independently confirmed | E;nu | 0/5 | 1 |
| RESEARCH-MAT-75E2210DFB548F98F0DF | Three-ply cotton yarn 2/67Ne | E;nu | 0/1 | 1 |
| RESEARCH-MAT-729339590D096B853627 | Toyo Rayon Tetoron polyethylene terephthalate filament | E;nu | 0/5 | 1 |
| RESEARCH-MAT-A263A59693243F5CB6EF | Twisted B. mori silk natural fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-97E66073840637D98C27 | Viscose fibre | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-363D1B4192446ECEE6A7 | Wood-pulp / regenerated-cellulose / polyethylene wetlaid nonwoven with hydroentangling and chemical binder | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9F86991BAFB539E0725D | Wood-pulp / regenerated-cellulose carded hydroentangled nonwoven | E;nu | 0/1 | 1 |
| RESEARCH-MAT-734F664683473E372E39 | Wool natural fibre | nu;rho | 0/1 | 1 |
| SOURCE-MAT-66DD06D9FFA9BF4AFC73 | suede — source-labelled material, finer composition unspecified | E;nu | 0/1 | 1 |
| MAT-TEXTILE-CHENILLE-YARN-SOURCE-BROAD | Chenille yarn, fibre chemistry unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-COTTON-LINEN-BLEND | Cotton/linen textile blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-COTTON-LINEN-VISCOSE-POLYESTER-BLEND | Cotton/linen/viscose/polyester blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-FLANNELETTE-SOURCE-BROAD | Flannelette material, fibre unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-POLYESTER-ACRYLIC-BLEND | Polyester/acrylic textile blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-POLYESTER-LINEN-BLEND | Polyester/linen textile blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-POLYESTER-LINEN-COTTON-BLEND | Polyester/linen/cotton textile blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-POLYESTER-LINEN-RAYON-BLEND | Polyester/linen/rayon textile blend, ratio/construction unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-POLYPROPYLENE-POLYESTER-BLEND | Polypropylene/polyester textile blend, ratio/construction source-conditioned | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-VELVET-BROAD | Velvet, fibre composition unspecified | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-WOOL-COTTON-BLEND | Wool/cotton textile blend, ratio/construction source-conditioned | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-WOOL-COTTON-POLYESTER-BLEND | Wool/cotton/polyester textile blend, ratio/construction source-conditioned | E;nu;rho | 0/0 | 0 |
| MAT-TEXTILE-WOOL-VISCOSE-BLEND | Wool/viscose textile blend, ratio/construction source-conditioned | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-154C9A0B0375CC4D8EE9 | hemp — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |
| SOURCE-MAT-05579D669DD1178BFA7B | recycled-plastic canvas — source-labelled material, finer composition unspecified | E;nu;rho | 0/0 | 0 |

## wood (142 gap nodes)

| 节点ID | 原文材料 | 缺项 | 完整/缺项组 | 文档键 |
|---|---|---|---:|---:|
| MAT-WOOD-PAINTED-BROAD | Painted wood, species/coating unspecified | nu | 0/4 | 2 |
| RESEARCH-MAT-21D60202D170E24E18B5 | Paulownia tomentosa wood | nu | 0/3 | 2 |
| MAT-WOOD-PAULOWNIA-BROAD | Paulownia wood, species/moisture unspecified | nu | 0/3 | 2 |
| RESEARCH-MAT-D40F38399C7E437DD567 | 18 mm Kronospan MDF | nu | 0/1 | 1 |
| RESEARCH-MAT-8BBF7A8B2BC9BCE7B86B | Acacia mangium wood | nu | 0/6 | 1 |
| MAT-WOOD-ACACIA-BROAD | Acacia wood, species/moisture unspecified | nu | 0/6 | 1 |
| RESEARCH-MAT-068F3384E5EB541AC0ED | CNF-surface-treated Scots pine sapwood (Pinus sylvestris) | nu | 0/3 | 1 |
| RESEARCH-MAT-16952BAFE9A9D809114D | Delignified and densified balsa transparent wood film (Ochroma pyramidale) | nu | 0/1 | 1 |
| RESEARCH-MAT-BDF31B0AE0B251F155C4 | HDF Express | nu | 0/1 | 1 |
| RESEARCH-MAT-3E990773C08F8B4C14DF | HDF Thin Board | nu | 0/1 | 1 |
| RESEARCH-MAT-1FB406940478F3BDB654 | Juglans nigra / Black walnut | rho | 0/1 | 1 |
| RESEARCH-MAT-2972006073A61102AEEA | Norway spruce (Picea abies) with multilayer essential-oil varnish system | nu | 0/2 | 1 |
| RESEARCH-MAT-65095713A8608A70F021 | Norway spruce (Picea abies) with nitrocellulose coating | nu | 0/1 | 1 |
| RESEARCH-MAT-B35A31146946598FC9F1 | Norway spruce (Picea abies) with two-component polyether-polyol/aliphatic-isocyanate polyurethane coating | nu | 0/1 | 1 |
| RESEARCH-MAT-9E993D9226ACFA04E8C2 | Thuja occidentalis / Northern white cedar | rho | 0/1 | 1 |
| RESEARCH-MAT-D06CCBD91AAA582C4480 | Thuja plicata / Western redcedar | rho | 0/1 | 1 |
| RESEARCH-MAT-6A8C5FEBE908F3B84562 | UF-bonded softwood-fiber MDF | E | 0/1 | 1 |
| RESEARCH-MAT-030C0CE58991AFB0BD77 | Untreated Scots pine sapwood (Pinus sylvestris) | nu | 0/1 | 1 |
| RESEARCH-MAT-740BEC01E4DFAD8E3467 | Alder, red | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-359E92ADE1A88A21D51B | American elm | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-F429D3010282F36E83D7 | Atlantic white cedar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-3F95E978EC90F9B3F19C | Baldcypress | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C24D54027BC353B6FDC6 | Balsam fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-7FB43586A069EEB8DD84 | Balsam poplar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A1C2D3DC9962F5C6E7FB | Basswood, American | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-2587F69D99EE3A8C361B | Beech, American | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-AEF54DD558E7D79D6E53 | Bigleaf maple | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-53FBCD349FA825B4BCD2 | Bigtooth aspen | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-EE520F420C6C655D39AA | Bitternut hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-892DB74C3624474920E0 | Black ash | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-4EA74D25308EBD3E6FF7 | Black cottonwood | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A98B086EE397E4D1F5EF | Black maple | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-4059C6FE162C6DF8FEC8 | Black oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-79021DD116D059C179A1 | Black spruce | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-D64ABDAA7B6573B5D92B | Black tupelo | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-292FAF84F432956A1888 | Blue ash | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-FB7FA4AC50E1C7645FB7 | Bur oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-6658152657348561774D | Butternut | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-555BC377546AFC039681 | California red fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-CCC8CB276B4BA382CCC4 | Cherry, black | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-62D954F18AF8BDBBB612 | Cherrybark oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C6E2532CEB9DB57058DE | Chestnut oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A4F4C24F972E71206E4F | Chestnut, American | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-13FC2C6E908915C98D13 | Coast Douglas-fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C8BE49B7124453E4D25C | Cucumbertree magnolia | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-93D63D2D080B3E4F50C9 | Douglas-fir plywood sheathing | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-D7E48BD452162D3444B8 | Eastern cottonwood | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-AA060430DFFED406EE34 | Eastern hemlock | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-DCF776E6D0B43AE58017 | Eastern redcedar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-6A5D43585E4FC1917D9B | Eastern white pine | nu;rho | 0/2 | 1 |
| MAT-WOOD-ELM-BROAD | Elm wood, species/moisture unspecified | nu;rho | 0/6 | 1 |
| RESEARCH-MAT-6E68F8A23AF4CA1DBD5B | Engelmann spruce | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-39F6E9454F7D637D2AB9 | Grand fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-5134F47441BAB1BF9AEC | Green ash | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-E71C570A1C2FAEB200DE | Hackberry | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-CF19539B95B0B5FA835B | Honeylocust | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-5F5341F7DE16E3DB681B | Incense cedar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A410699305BF513FDEF4 | Interior North Douglas-fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-0B8EBCF7DCB6BDF1219D | Interior South Douglas-fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-E4B99FC0059E992A676A | Interior West Douglas-fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-380200E4F6898D4EFE09 | Jack pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C9E6DE94ABC113CBF749 | Larch, western | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C666E3E289D75BD97614 | Laurel oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-94B1F5829B089FDD6893 | Live oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A3CCAB48E992F9F05172 | Loblolly pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-E62EB5B44E89A1C50F84 | Locust, black | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-72855DA8A850373D7199 | Lodgepole pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-3E7F075EBAB01CA679CC | Longleaf pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-13F6C472F45F728F7240 | Mockernut hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C8ABB1BA3108E560AF72 | Mountain hemlock | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-ABADB6787B33CE542AA1 | Natural balsa wood veneer (Ochroma pyramidale) | E;nu | 0/1 | 1 |
| RESEARCH-MAT-9DCED528D673121090A8 | Natural ester oil-impregnated partially delignified densified basswood veneer | E;nu | 0/1 | 1 |
| RESEARCH-MAT-0DB9324DA95B57D5B695 | Noble fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-987FE46846A2980CBC04 | Northern red oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C6FF01CD504B13ED8E44 | Northern white cedar | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5DF94E27E06CCAB9964E | Nutmeg hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-23683C8AA5369A88F34F | Old-growth redwood | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-F9B259B25EBB311B8263 | Oregon ash | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-2874A2CD063926518C14 | Overcup oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-834C6467AE036E2E3246 | Pacific silver fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-CB91E065731368EA9F57 | Paper birch | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-1D6A3E869B730E6CC5D2 | Pecan hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-41B15EB800D873AC238A | Pignut hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-8C70C646CC219590FE1A | Pin oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A64CC868877ECF9E4946 | Pitch pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-8403CB0FA9A383AB63B5 | Plywood/OSB/particleboard/MDF source panel collection | E;rho | 0/1 | 1 |
| RESEARCH-MAT-BB819795D504708913C5 | Pond pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-52D8B03F343F2F42BA6A | Ponderosa pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-150472A808587D010B6F | Port-Orford cedar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A4DCCAEE17D1E1AE62E1 | Post oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-3C6B397F76FA4E424504 | Quaking aspen | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-B74A8D648ADE0FB7417E | Rattan cane | nu;rho | 0/4 | 1 |
| MAT-RATTAN-BROAD | Rattan, species/construction unspecified | nu;rho | 0/4 | 1 |
| RESEARCH-MAT-B05CDDA4EAA7BAFEA5F5 | Red maple | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-FEBCC9A0AB25BAC74762 | Red oak group | E;rho | 0/1 | 1 |
| RESEARCH-MAT-1C31C134C4C887F14779 | Red pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-9E88C1F9408FB7F7068C | Red spruce | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-A8CBFF769B25FDF62092 | Rock elm | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C0CC007FDB173C0CD872 | Sand pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-3D9AC83D51EA88377E30 | Sassafras | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-98FD9C319AC63FBCC89B | Scarlet oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-568AA6989AEA9C8BE9E1 | Shagbark hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-2160E1B43601109C6396 | Shellbark hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-C81BBFA3E4AAF9069F3C | Shortleaf pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-EC1BDDBE4DDE89E3D565 | Silver maple | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-F07854DE920C1F631919 | Sitka spruce | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-761C248ACAF1E6E173C3 | Slash pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-57847D6B6C27E3D37878 | Slippery elm | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-798FD0346D6BFD8242EE | Southern magnolia | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-B9A96D18DBA3983AC4FC | Southern red oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-CDB87E3125F22A019606 | Spruce pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-5DCB6F7C4BC91807A046 | Subalpine fir | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-1D1BF3960ED5FFB3AEA1 | Sugar maple | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-0BE27CEC4E2EE99C864C | Sugar pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-560059D4508BF7B62E3E | Swamp chestnut oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-F66B10F023BC434F0558 | Swamp white oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-73461C8B311792835090 | Sweet birch | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-65DDCE19F55A242F8BEE | Sweetgum | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-EEC34D25A9B44136A75B | Sycamore, American | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-B4CD7CB1BD533A2FED19 | Tamarack | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-5F74A1FAE3DF9D0DB741 | Tanoak | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-E0E5BA98BE7A1CBAFC20 | Virginia pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-7381FBB692388EA97A9E | Walnut, black | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-5720EFBEB8B014AFE626 | Water hickory | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-DA00371764447AA48F29 | Water oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-405FD507C24F82D99E89 | Water tupelo | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-8C7E9768682BABF6EC2C | Western hemlock | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-2F796B7501AB91EDB84F | Western redcedar | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-3C9B192452802ED8E338 | Western white pine | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-292832720A97C2636AC7 | White agglomerated cork | E;nu | 0/2 | 1 |
| RESEARCH-MAT-7C36F460ED6AA5EE8636 | White ash | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-FE8874D1427354DE67BA | White fir | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-25F454B799E0E903B663 | White oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-1CC3F6CC53230C681A18 | White spruce | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-E8EF5F435125BE21AA45 | Willow oak | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-71AABA2E508C79E33069 | Willow, black | nu;rho | 0/2 | 1 |
| MAT-WOOD-VENEER-BROAD | Wood veneer, species/thickness unspecified | E;nu | 0/1 | 1 |
| RESEARCH-MAT-1640FFE53715930E2FC0 | Yellow birch | nu;rho | 0/1 | 1 |
| RESEARCH-MAT-A630716995AD5A38A7E1 | Yellow cedar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-91093992F88B3535949A | Yellow-poplar | nu;rho | 0/2 | 1 |
| RESEARCH-MAT-0BAD4795FCF717EEFD35 | Young-growth redwood | nu;rho | 0/2 | 1 |
| MAT-RATTAN-TWINE-SOURCE-BROAD | Rattan/twine composite weave, twine fibre unspecified | E;nu;rho | 0/0 | 0 |
