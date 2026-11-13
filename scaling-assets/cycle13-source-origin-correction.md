# Cycle13 已应用的来源纠错边界

当前主账已按独立复核完成纠错：35条旧完整组中7条保留并修正来源，28条撤回或重分；另恢复25条缺项及1条来源内玻璃汇编完整组。下方为冻结方案原文，其中“尚未改共享表”描述的是方案建立时点，不代表当前状态。新采集1完整/30缺项单列；本轮合计净完整−26、缺项+55。

---

# Original source versus project-derived values

Two source documents inspected directly from frozen XML. No shared tables have yet changed.

PMC5291313 / 10.6028/jres.080A.008: source Tables1/2 report tensile E and nu, not mixture density. Source body reports neat matrix rho1.187g/cm3 and filler glass rho2.392g/cm3. Twenty-three existing filled-composite complete rows use project-calculated mixture densities, so they must become E+nu partials. One omitted source row (Table1 phi.0482) has actual E3.35GPa and nu.430 and should be recovered as partial. Seven neat-matrix rows can retain three source-reported properties with source body density explicitly non-paired, rather than calling the density mixture-derived. Preserve exact test age/storage observations; wrong broad composite identity for neat rows must be corrected with stable aliases. The filler glass body reports E76GPa (approximate manufacturer value), nu.23 (literature value), rho2392kg/m3 (measured); it qualifies as explicitly heterogeneous-origin source compilation, not same-experiment measurement.

PMC12030102 / 10.3390/polym17081008: Table1 reports lambda, mu and rho, not numerical E or nu. Five current complete rows obtained E/nu by project isotropic conversion. Preserve these transformations as separate non-counted calculations. Recover the directly reported rho1.06g/cm3 as one density-only source group with all five source-temperature observations, not five repeated independent densities.

Preserve all original rows and derived numbers in quarantine/observations. Do not delete underlying research; correct only what is counted as source-reported E/nu/rho. A scientific source reported calculation is distinct from a calculation performed by this project. Existing other derived-method records require per-source review; this inspection does not condemn all derived elastic constants.

Independent-review repair: all24 filled rows use composite family and sourcephi-defined composition identities. Prior generic/polymer-filled identity IDs and labels remain in typed record replacement history,not equivalence aliases. Table1 early-age samples do not inherit the later Table2 24C/54%RH storage statement; all source numericalE/nu/rho are unchanged.
