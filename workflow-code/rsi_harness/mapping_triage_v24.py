#!/usr/bin/env python3
"""Classify unresolved material mappings into deterministic next routes.

This module is diagnostic only.  It never assigns a material node and never
changes the object or material tables.  It consumes the v2.4.2 queue produced
by release_gate_v24.py and makes the source-specific work still required
visible.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from source_coverage_v24 import family_for

RULES_VERSION = "2.4.2-H3"


def classify_route(row: dict) -> tuple[str, str, str]:
    """Return (route_key, evidence_class, explanation) without inference."""
    source = row.get("source_dataset", "")
    family = family_for(source)
    reason = row.get("reason_code", "")
    raw = " ".join(
        row.get(k, "") for k in ("original_material_label", "material_node_id", "mapping_evidence")
    ).lower()

    if reason == "SOURCE_MANIFEST_NO_MATERIAL":
        return ("OFFICIAL_MANIFEST_MATERIAL_ROUTE", "NO_SOURCE_MATERIAL_FIELD",
                "官方清单未报告材料；只能查官方说明或保持 HOLD")
    if reason == "NO_ACCEPTED_SOURCE_OPTION":
        return ("SOURCE_OPTION_REVIEW_ROUTE", "SOURCE_OPTIONS_HELD",
                "保留作者选项并独立复核，不从纹理、标题、PBR、VLM 或常识补写")
    if reason.startswith("MATERIAL_NODE_SENTINEL"):
        if family == "PhysX_3D":
            return ("PHYSX_MANIFEST_MATERIAL_ROUTE", "NO_SOURCE_MATERIAL_FIELD",
                    "PhysXNet finalindex 未提供组件材料；不得从 ShapeNet 外观或模型预测补写")
        if family == "VoMP_GVM":
            return ("VOMP_INDEPENDENT_MATERIAL_REVIEW", "VLM_OR_SEGMENT_CANDIDATE",
                    "仅有 VLM/分割候选；需找到作者或独立材料来源后才能建立节点")
        if family in {"PIXIEVerse", "PIXIEVerse_UPSTREAM"}:
            return ("PIXIE_INDEPENDENT_MATERIAL_REVIEW", "VLM_OR_SEGMENT_CANDIDATE",
                    "仅有语义分割/CLIP 候选；需找到独立材料来源后才能建立节点")
        if family == "NVIDIA_SimReady":
            if "material_not_yet_parsed" in raw:
                return ("SIMREADY_USD_PARSE_ROUTE", "OFFICIAL_BINDING_UNPARSED",
                        "解析官方 authored USD 的 prim/material binding；解析前不得补写")
            return ("SIMREADY_USD_BINDING_REVIEW", "OFFICIAL_BINDING_REVIEW",
                    "核对官方 USD 绑定的 prim、标签和作用范围；官方标签不等于实测物性")
        if family == "ABO":
            return ("ABO_LISTING_SCOPE_REVIEW", "OFFICIAL_LISTING_UNRESOLVED",
                    "回到官方 listing 原文，确认材料和部件范围；不能把标题或颜色当材料")
        if family == "GSO":
            return ("GSO_MANIFEST_MATERIAL_ROUTE", "NO_SOURCE_MATERIAL_FIELD",
                    "Fuel manifest 未报告材料；查官方产品/扫描说明，找不到则 HOLD")
        if family == "3DCoMPaT_PLUSPLUS":
            return ("SOURCE_OPTION_REVIEW_ROUTE", "SOURCE_OPTIONS_HELD",
                    "作者选项尚未接受；逐对象保留选项，禁止生成笛卡尔积")
        if family in {"OBJAVERSE_SUPPLEMENTAL", "OBJAVERSE_CONTEXT"}:
            return ("OBJAVERSE_SOURCE_DECLARATION_REVIEW", "SOURCE_DECLARATION_OR_OPTION",
                    "只保留作者/官方声明或明确选项；标题和纹理不能独立证明材料")
        if family == "YCB":
            return ("YCB_SURFACE_CLASS_REVIEW", "SURFACE_CLASS_NOT_CHEMICAL_IDENTITY",
                    "表面类别不是化学材料身份；必须保留原类别并单独标注证据边界")
        return ("UNRESOLVED_SOURCE_ADAPTER_ROUTE", "UNRESOLVED",
                "按来源 adapter 查找原始材料说明；无证据保持 HOLD")
    return ("UNRESOLVED_SOURCE_ADAPTER_ROUTE", "UNRESOLVED",
            "按来源 adapter 查找原始材料说明；无证据保持 HOLD")


def build_triage(rows: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        family = family_for(row.get("source_dataset", ""))
        route, evidence, explanation = classify_route(row)
        grouped[(route, evidence, family, row.get("source_dataset", ""))].append(row)
    out = []
    for (route, evidence, family, source), members in sorted(grouped.items()):
        labels = [m.get("original_material_label", "").strip() for m in members if m.get("original_material_label", "").strip()]
        objects = [m.get("object_id", "").strip() for m in members if m.get("object_id", "").strip()]
        out.append({
            "route_key": route,
            "evidence_class": evidence,
            "source_family": family,
            "source_dataset": source,
            "row_count": len(members),
            "object_count": len(set(objects)),
            "reason_codes": ";".join(sorted({m.get("reason_code", "") for m in members})),
            "raw_label_examples": " | ".join(sorted(set(labels))[:5]),
            "object_id_examples": " | ".join(sorted(set(objects))[:5]),
            "explanation": classify_route(members[0])[2],
        })
    return out


def write_outputs(queue_path: Path, out_base: Path) -> dict:
    with queue_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    triage = build_triage(rows)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_base.with_suffix(".csv")
    fields = list(triage[0]) if triage else ["route_key", "evidence_class", "source_family", "source_dataset", "row_count"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(triage)
    summary = {
        "status": "PASS_MAPPING_TRIAGE_READ_ONLY",
        "rules_version": RULES_VERSION,
        "queue_rows": len(rows),
        "route_groups": len(triage),
        "route_totals": dict(Counter(x["route_key"] for x in triage for _ in range(int(x["row_count"])))),
        "groups": triage,
    }
    json_path = out_base.with_suffix(".json")
    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path = out_base.with_suffix(".md")
    lines = [
        f"# RSI v{RULES_VERSION} 未解析材料映射分流（只读）", "",
        f"队列行：{len(rows):,}；分流组：{len(triage):,}。本报告不创建材料节点、不修改正式表。", "",
        "| 路线 | 证据类别 | 来源族 | 行数 | 对象数 |", "|---|---|---|---:|---:|",
    ]
    for x in triage:
        lines.append(f"| {x['route_key']} | {x['evidence_class']} | {x['source_family']} | {int(x['row_count']):,} | {int(x['object_count']):,} |")
    lines += ["", "## 原则", "", "- 分流路线只说明下一步需要查什么，不代表材料身份已通过。", "- VLM/CLIP/LLM/PBR/颜色/纹理和标题仍不能单独生成正式材料节点。", "- 每条候选必须返回原始定位、来源哈希、作用范围和独立复核结果；失败则保持 HOLD。", ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path), "queue_rows": len(rows), "route_groups": len(triage)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_outputs(args.queue, args.out), ensure_ascii=False))


if __name__ == "__main__":
    main()
