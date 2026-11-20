#!/usr/bin/env python3
"""Recompute required-source coverage from the current object release.

This is read-only. It does not treat aliases as additive geometry and does not
turn reported paper totals into object rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


OBJECT_REL = Path("data/scaling_release_v1/object_component_inventory.csv")
SUMMARY_REL = Path("data/current_two_table_delivery_v1/summary.json")
MATERIAL_REL = Path("data/current_two_table_delivery_v1/material_reverse_index_and_property_ranges.csv")
SCOPE_POLICY_REL = Path("data/material_scope_policy.json")
REGISTRY_REL = Path("dataset_registry.csv")
MATRIX_REL = Path("audit/requested_source_completion_matrix_v3.csv")
EVIDENCE_REL = Path("data/current_two_table_delivery_v1/main_property_source_groups.csv")
COVERAGE_REL = Path("audit/rsi_framework_review_2026-11-15/rsi_v24_source_coverage.json")
SUMMARY_KEYS = ("object_identities", "distinct_component_pairs", "state_rows", "material_nodes",
                "main_source_groups", "main_complete_groups", "main_partial_groups")
COVERAGE_INPUTS = (OBJECT_REL, MATERIAL_REL, SCOPE_POLICY_REL, REGISTRY_REL, MATRIX_REL, EVIDENCE_REL)
SCHEMA_VERSION = "2.4.3-O71"

UNRESOLVED_MATERIAL_IDS = frozenset({"", "UNMAPPED", "NOT_MAPPED", "UNASSIGNED", "UNKNOWN"})

FAMILIES = (
    "VoMP_GVM", "PIXIEVerse", "PIXIEVerse_UPSTREAM", "OBJAVERSE_CONTEXT",
    "SLAT_Phys_ALIAS", "PhysX_3D", "PhysX_Mobility", "ABO",
    "NVIDIA_SimReady", "NVIDIA_SimReady_LEGACY_ALIAS", "PhysX_SDK_CONTEXT",
    "3DCoMPaT_PLUSPLUS", "GSO", "OBJAVERSE_SUPPLEMENTAL", "YCB",
    "CURRENT_BASELINE", "CATALOG_SUPPLEMENTAL", "OTHER",
)


def family_for(name: str) -> str:
    text = name.lower()
    if "vomp gvm" in text:
        return "VoMP_GVM"
    if "pixieverse public upstream" in text:
        return "PIXIEVerse_UPSTREAM"
    if "pixieverse" in text:
        return "PIXIEVerse"
    if "objaverse" in text and "lvis" in text:
        return "OBJAVERSE_SUPPLEMENTAL"
    if "objaverse" in text:
        return "OBJAVERSE_CONTEXT"
    if "physxnet" in text:
        return "PhysX_3D"
    if "3dcompat" in text:
        return "3DCoMPaT_PLUSPLUS"
    if "physx-mobility" in text:
        return "PhysX_Mobility"
    if "googleresearch scanned objects" in text:
        return "GSO"
    if "ycb object" in text:
        return "YCB"
    if "abo" in text or "amazon berkeley" in text:
        return "ABO"
    if "simready official packs" in text and "alias of vomp/gvm" in text:
        return "NVIDIA_SimReady_LEGACY_ALIAS"
    if "simready" in text:
        return "NVIDIA_SimReady"
    if "physx" in text:
        return "PhysX_SDK_CONTEXT"
    if "current" in text or "冻结原表" in name or "叶子覆盖扩充" in name:
        return "CURRENT_BASELINE"
    if "thorlabs" in text or "author-lab" in text:
        return "CATALOG_SUPPLEMENTAL"
    return "OTHER"


def _load_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_report(root: Path, report: dict, summary: dict) -> list[str]:
    """Reject historical counts, absent provenance and changed release inputs.

    The report does not hash summary.json: the delivery summary hashes this report.
    Selected counts bind the snapshot without a circular file dependency.
    """
    problems = []
    if report.get("rules_version") != SCHEMA_VERSION:
        problems.append("source coverage schema is stale")
    if report.get("status") != "PASS_SOURCE_COVERAGE_RECOMPUTED_READ_ONLY":
        problems.append("source coverage status is not PASS")
    if report.get("summary_counts") != {key: summary.get(key) for key in SUMMARY_KEYS}:
        problems.append("source coverage counts disagree with working summary")
    pins = report.get("input_sha256", {})
    if not isinstance(pins, dict):
        return problems + ["source coverage pins are not an object"]
    for rel in COVERAGE_INPUTS:
        if str(rel) not in pins:
            problems.append(f"source coverage input is unpinned: {rel}")
    for rel, expected in pins.items():
        path = (root / rel).resolve()
        if Path(rel).is_absolute() or not path.is_relative_to(root.resolve()):
            problems.append(f"unsafe source coverage input: {rel}")
        elif not path.is_file() or _sha(path) != expected:
            problems.append(f"source coverage input changed: {rel}")
    return problems


def build_report(root: Path, summary_override: dict | None = None) -> dict:
    root = root.resolve()
    for rel in COVERAGE_INPUTS:
        if not (root / rel).is_file():
            raise FileNotFoundError(root / rel)
    summary = summary_override if summary_override is not None else json.loads((root / SUMMARY_REL).read_text(encoding="utf-8"))
    material_ids = {row.get("material_id", "").strip() for row in _load_csv(root / MATERIAL_REL) if row.get("material_id", "").strip()}
    scope = json.loads((root / SCOPE_POLICY_REL).read_text(encoding="utf-8"))
    excluded = set(summary.get("excluded_liquid_material_ids", [])) | set(scope.get("excluded_material_ids", []))
    resolved_material_ids = material_ids | excluded
    alias = None
    if summary.get("canonical_identity_projection_applied") is True:
        from object_alias_projection_v24 import load_alias_projection
        alias = load_alias_projection(root, summary)
    elif summary.get("raw_inventory_object_id_aliases_collapsed", 0):
        raise ValueError("alias count declared without a validated alias projection")
    counts = defaultdict(Counter)
    raw_by_family, pairs_by_family = defaultdict(set), defaultdict(set)
    canonical_by_family, canonical_pairs_by_family = defaultdict(set), defaultdict(set)
    raw_objects, canonical_objects, canonical_pairs = set(), set(), set()
    unclassified = Counter()
    from current_object_inventory_v24 import iter_inventory, overlay as inventory_overlay
    sidecar_rows, sidecar_pins = inventory_overlay(root, summary)
    state_rows = 0
    with (root / OBJECT_REL).open(encoding="utf-8-sig", newline="") as handle:
        for row in iter_inventory(root, summary):
            state_rows += 1
            family = family_for(row.get("source_dataset", ""))
            counts[family]["inventory_rows"] += 1
            oid, cid = row.get("object_id", ""), row.get("component_id", "")
            raw_objects.add(oid); raw_by_family[family].add(oid); pairs_by_family[family].add((oid, cid))
            current = alias.project(row) if alias else row
            pair = current.get("object_id", ""), current.get("component_id", "")
            canonical_objects.add(pair[0]); canonical_pairs.add(pair)
            canonical_by_family[family].add(pair[0]); canonical_pairs_by_family[family].add(pair)
            mapped = row.get("material_node_id", "").strip() in resolved_material_ids
            counts[family]["rows_with_material_node"] += int(mapped)
            status = row.get("material_identity_status", "")
            formal = mapped and (status.startswith(("FORMAL_", "OFFICIAL_")) or "EXPLICIT_MATERIAL" in status)
            counts[family]["formal_or_official_rows"] += int(formal)
            if family == "OTHER":
                unclassified[row.get("source_dataset", "")] += 1
    raw_objects.discard(""); canonical_objects.discard(""); canonical_pairs.discard(("", ""))
    alias_metrics = alias.finish(summary, raw_objects, canonical_objects) if alias else {}
    records = []
    for family in FAMILIES:
        c = counts[family]
        records.append(dict(family=family, inventory_rows=c["inventory_rows"],
            source_object_identities=len(raw_by_family[family] - {""}),
            component_pairs=len(pairs_by_family[family] - {("", "")}),
            canonical_object_identities_within_family=len(canonical_by_family[family] - {""}),
            canonical_component_pairs_within_family=len(canonical_pairs_by_family[family] - {("", "")}),
            rows_with_material_node=c["rows_with_material_node"],
            rows_without_material_node=c["inventory_rows"]-c["rows_with_material_node"],
            formal_or_official_rows=c["formal_or_official_rows"],
            candidate_or_hold_rows=c["inventory_rows"]-c["formal_or_official_rows"]))
    evidence_rows = complete = 0
    with (root / EVIDENCE_REL).open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            evidence_rows += 1
            complete += all(row.get(key, "").strip() for key in ("E_low_GPa", "nu_low", "rho_low_kg_m3"))
    computed = dict(object_identities=len(canonical_objects), distinct_component_pairs=len(canonical_pairs),
        state_rows=state_rows, material_nodes=len(material_ids), main_source_groups=evidence_rows,
        main_complete_groups=complete, main_partial_groups=evidence_rows-complete)
    if computed != {key: summary.get(key) for key in SUMMARY_KEYS}:
        raise ValueError(f"source coverage recomputation disagrees with summary: {computed}")
    pins = {str(rel): _sha(root / rel) for rel in COVERAGE_INPUTS}
    pins.update(alias_metrics.get("validated_input_sha256", {}))
    pins.update(sidecar_pins)
    return dict(status="PASS_SOURCE_COVERAGE_RECOMPUTED_READ_ONLY", rules_version=SCHEMA_VERSION,
        summary_counts=computed, raw_inventory_source_identities=len(raw_objects), alias_projection=alias_metrics,
        source_identity_sidecar_rows=len(sidecar_rows), sidecar_verified_unique_geometry=0, sidecar_real_mechanical_parts=0,
        input_sha256=pins,
        count_definitions={
            "summary_counts": "Current canonical ID projection of frozen inventory plus authenticated source-identity sidecars; not globally verified unique geometry.",
            "families": "Non-additive source memberships; canonical counts can overlap between families.",
            "source_object_identities": "Raw identity IDs within a source family before reviewed alias projection.",
            "rows_with_material_node": "Raw inventory foreign-key resolution, not current reviewed-link acceptance or E/nu/rho coverage.",
            "formal_or_official_rows": "Raw inventory status only; later reviewed sidecars may alter accepted scope.",
            "candidate_or_hold_rows": "Remaining raw historical statuses; not a claim that current reviewed links are all HOLD.",
        }, families=records,
        aliases={
            "SLAT_Phys_ALIAS": dict(status="ALIAS_ONLY",note="SLAT-Phys reuses PIXIEVerse; no additive geometry"),
            "NVIDIA_SimReady_LEGACY_ALIAS": dict(status="ALIAS_ONLY",note="legacy five packs alias GVM SimReady memberships; do not add twice"),
        }, registry_rows=len({r.get("dataset_id", "") for r in _load_csv(root / REGISTRY_REL)}),
        completion_matrix_rows=len({r.get("source", "") for r in _load_csv(root / MATRIX_REL)}),
        unmapped_source_datasets=sorted(set(counts)-set(FAMILIES)),
        unclassified_source_dataset_rows=dict(sorted(unclassified.items())))

def write_outputs(root: Path, out_base: Path, summary_override: dict | None = None) -> dict:
    report = build_report(root, summary_override)
    out_base.parent.mkdir(parents=True, exist_ok=True)
    json_path = out_base.with_suffix(".json")
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    csv_path = out_base.with_name(out_base.name + "_families.csv")
    fields = list(report["families"][0]) if report["families"] else ["family"]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader(); writer.writerows(report["families"])
    md_path = out_base.with_suffix(".md")
    lines = [
        "# RSI 2.4 来源覆盖重算（只读）", "",
        "本报告从冻结 object_component_inventory.csv 与已认证的来源身份侧车逐条重算；逐项验证别名后投影规范身份，论文总数不补造对象；来源身份不等于已验证唯一几何。材料节点只在当前材料表或显式排除政策中命中时计为已解析，UNMAPPED 不计入。", "",
        "| 来源族 | 来源身份行 | 对象身份 | 组件对 | 有材料节点 | 无材料节点 | 正式/官方映射行 | 候选/HOLD 行 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in report["families"]:
        lines.append("| {family} | {inventory_rows:,} | {source_object_identities:,} | {component_pairs:,} | {rows_with_material_node:,} | {rows_without_material_node:,} | {formal_or_official_rows:,} | {candidate_or_hold_rows:,} |".format(**row))
    lines += ["", "## 别名", "", "- SLAT-Phys：PIXIEVerse 别名，不增加几何。", "- NVIDIA 旧 SimReady 五包：GVM SimReady 别名，不增加几何。", "", "## 说明", "", "`formal_or_official_rows` 是材料身份状态的结构性统计，不等于 E/ν/ρ 证据通过；材料证据仍由 complete/partial ledger 和 v2.4 release gate 单独核验。原清单状态与后续复核侧账分开，候选/HOLD 原状态数量不等于当前待办数量。各来源族的规范身份可能交叠，不能直接求和当作唯一几何。", ""]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": str(json_path), "csv": str(csv_path), "markdown": str(md_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    outputs = write_outputs(args.root.resolve(), args.out)
    print(json.dumps({"status": "PASS_SOURCE_COVERAGE_RECOMPUTED_READ_ONLY", "outputs": outputs}, ensure_ascii=False))


if __name__ == "__main__":
    main()
