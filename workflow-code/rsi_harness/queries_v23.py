"""Read-only RSI 2.3 projections.

These queries turn accepted facts into queues and coverage reports. They never
create objects, material values, or evidence. A collector must submit a frozen
candidate package; the existing review and merge gates remain authoritative.
"""
from collections import Counter, defaultdict
import json
import sqlite3

from contracts_v22 import configuration_key, delivery_summary

PROPERTIES = ("E", "nu", "rho")


def _rows(db, sql, args=()):
    return [dict(row) for row in db.execute(sql, args)]


def _state_rows(db):
    rows = _rows(db, """
        SELECT s.material_id, s.state, s.depth, s.direct_objects,
               s.effective_objects, s.missing_json, s.stats_json,
               n.name_cn, n.name_en, n.family, n.flexible, n.granularity
        FROM material_state s JOIN nodes n ON n.id=s.material_id
        WHERE n.active=1 AND n.kind='MATERIAL'
        ORDER BY s.depth, n.family, s.material_id
    """)
    for row in rows:
        row["missing"] = json.loads(row.pop("missing_json"))
        row["stats"] = json.loads(row.pop("stats_json"))
    return rows


def _require_derived_state(db):
    expected = db.execute("SELECT value FROM meta WHERE key='epoch'").fetchone()
    if not expected:
        raise ValueError("Run recompute before querying RSI projections")
    expected_epoch = json.loads(expected[0])
    stale = db.execute(
        "SELECT count(*) FROM material_state WHERE epoch<>?", (expected_epoch,)
    ).fetchone()[0]
    expected_count = db.execute("SELECT count(*) FROM nodes WHERE active=1 AND kind='MATERIAL'").fetchone()[0]
    actual_count = db.execute("SELECT count(*) FROM material_state").fetchone()[0]
    if stale or actual_count != expected_count:
        raise ValueError("Derived material state is stale")


def four_state_counts(db):
    """Return the four material states and both named denominators."""
    _require_derived_state(db)
    counts = {str(i): 0 for i in range(1, 5)}
    for row in _state_rows(db):
        counts[str(row["state"])] += 1
    object_den = counts["1"] + counts["3"]
    all_den = sum(counts.values())
    return {
        "states": counts,
        "K_object": {"covered": counts["1"], "required": object_den,
                      "ratio": counts["1"] / object_den if object_den else None},
        "K_all": {"covered": counts["1"] + counts["2"], "required": all_den,
                  "ratio": (counts["1"] + counts["2"]) / all_den if all_den else None},
    }


def material_queue(db):
    """Plan material work; existing-object gaps always precede optional work."""
    _require_derived_state(db)
    tasks = []
    for row in _state_rows(db):
        state = row["state"]
        if state == 3:
            for prop in row["missing"]:
                tasks.append({"lane": "MATERIAL", "task_type": "MATERIAL_VALUE_REPAIR",
                              "material_id": row["material_id"], "attribute_scope": prop,
                              "priority": 0, "depth": row["depth"], "family": row["family"]})
        elif state == 4:
            tasks.append({"lane": "MATERIAL", "task_type": "MATERIAL_OPTIONAL_RESEARCH",
                          "material_id": row["material_id"], "attribute_scope": "E,nu,rho",
                          "priority": 1, "depth": row["depth"], "family": row["family"]})
        stats = row["stats"]
        for prop in PROPERTIES:
            if stats.get("properties", {}).get(prop, {}).get("document_keys", 0) < 5:
                tasks.append({"lane": "MATERIAL", "task_type": "SOURCE_ENHANCEMENT",
                              "material_id": row["material_id"], "attribute_scope": prop,
                              "priority": 2, "depth": row["depth"], "family": row["family"]})
    for row in _rows(db, "SELECT id,reason FROM obligations WHERE resolved=0 AND object_id IS NULL ORDER BY id"):
        tasks.append({"lane": "MATERIAL", "task_type": "MATERIAL_SCOPE_OBLIGATION_REPAIR",
                      "subject_id": row["id"], "obligation_id": row["id"],
                      "attribute_scope": "NONE", "priority": 0,
                      "depth": 0, "family": "obligation", "reason": row["reason"]})
    return sorted(tasks, key=lambda t: (t["priority"], t["depth"], t["family"],
                                        t.get("material_id", t.get("subject_id", "")),
                                        t["attribute_scope"]))


def object_queue(db):
    """Plan new-object discovery. Only state 1/2 can enter this queue."""
    _require_derived_state(db)
    tasks = []
    for row in _state_rows(db):
        if row["state"] not in (1, 2):
            continue
        tasks.append({"lane": "OBJECT", "task_type": "OBJECT_DISCOVERY",
                      "material_id": row["material_id"], "attribute_scope": "NONE",
                      "priority": 0 if row["state"] == 2 else 1,
                      "depth": row["depth"], "family": row["family"],
                      "flexible": bool(row["flexible"]), "state": row["state"]})
    for row in _rows(db, "SELECT id,kind,reason,object_id,component_id FROM obligations WHERE resolved=0 AND object_id IS NOT NULL ORDER BY id"):
        task_type = "OBJECT_LABEL_REPAIR" if row["kind"] == "COMPONENT_MATERIAL" else "OBJECT_SCOPE_REPAIR"
        tasks.append({"lane": "OBJECT", "task_type": task_type, "subject_id": row["object_id"],
                      "object_id": row["object_id"], "obligation_id": row["id"],
                      "component_id": row["component_id"], "attribute_scope": "NONE",
                      "priority": -1, "depth": 0, "family": "existing-object-repair",
                      "existing_object": True, "reason": row["reason"]})
    return sorted(tasks, key=lambda t: (t["priority"], t["depth"], t["family"],
                                        -int(t.get("flexible", False)),
                                        t.get("material_id", t.get("subject_id", t.get("object_id", "")))))


def object_material_coverage(db):
    """Check every accepted object's recorded material scopes.

    Alternatives remain required entries; an empty or unknown scope is an
    explicit failure. Special/excluded nodes are reported separately and do
    not create a false material pass.
    """
    _require_derived_state(db)
    state = {r["material_id"]: r for r in _state_rows(db)}
    objects = _rows(db, "SELECT id,name_cn,name_en,namespace,source_uid FROM objects WHERE accepted=1 ORDER BY id")
    links = defaultdict(list)
    for row in _rows(db, """
        SELECT l.object_id,l.component_id,l.material_id,l.mode,l.option_group,
               n.kind,n.active
        FROM material_links l LEFT JOIN nodes n ON n.id=l.material_id
        WHERE l.accepted=1 ORDER BY l.object_id,l.component_id,l.id
    """):
        links[row["object_id"]].append(row)
    components = defaultdict(set)
    for row in _rows(db, "SELECT object_id,id FROM components ORDER BY object_id,id"):
        components[row["object_id"]].add(row["id"])
    obligations = defaultdict(list)
    for row in _rows(db, """SELECT id,kind,reason,object_id,component_id FROM obligations
                          WHERE resolved=0 AND object_id IS NOT NULL ORDER BY object_id,id"""):
        obligations[row["object_id"]].append(row)
    output = []
    for obj in objects:
        rows = links.get(obj["id"], [])
        required = []
        unknown = []
        special = []
        for link in rows:
            material_id = link["material_id"]
            node = state.get(material_id)
            if not node:
                if link["kind"] in ("SPECIAL", "EXCLUDED"):
                    special.append(material_id)
                else:
                    unknown.append(material_id)
                continue
            required.append(material_id)
        required = sorted(set(required))
        missing = sorted(set(p for mid in required for p in state[mid]["missing"]))
        component_ids = components.get(obj["id"], set())
        component_count = len(component_ids)
        mapped_components = {link["component_id"] for link in rows}
        unmapped_components = max(0, component_count - len(mapped_components))
        open_obligations = obligations.get(obj["id"], [])
        if not rows or unmapped_components or open_obligations:
            status = "UNKNOWN_MATERIAL_SCOPE"
        elif unknown:
            status = "UNKNOWN_MATERIAL_LABEL"
        elif not required and special:
            status = "SPECIAL_DOMAIN_ONLY"
        elif missing:
            status = "MATERIAL_PROPERTIES_INCOMPLETE"
        else:
            status = "MATERIAL_PROPERTIES_COMPLETE"
        output.append({"object_id": obj["id"], "name_cn": obj["name_cn"],
                       "name_en": obj["name_en"], "required_materials": required,
                       "missing_properties": missing, "unknown_materials": sorted(set(unknown)),
                       "special_or_excluded": sorted(set(special)), "status": status,
                       "component_link_count": len(rows), "component_count": component_count,
                       "unmapped_components": unmapped_components, "open_obligations": open_obligations})
    return output


def object_delivery_summary(db):
    """Compute N/R/C/RC only from same-release, independently audited rows.

    Existing source identities without delivery/scope audits remain visible in
    the blocked counts; they are never promoted by accepted=1 alone.
    """
    _require_derived_state(db)
    tables = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    required_audit_tables = {"object_delivery_audits", "object_scope_audits", "object_geometry_groups", "object_configurations"}
    if not required_audit_tables <= tables:
        return {"status": "RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED",
                "N": None, "R": None, "C": None, "RC": None,
                "source_identities_total": db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0],
                "blocked_source_identities": db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0],
                "blocked_reasons": {"RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED":
                                    db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0]},
                "migration_required": sorted(required_audit_tables - tables)}
    release_row = db.execute("SELECT value FROM meta WHERE key='release_id'").fetchone()
    release_id = json.loads(release_row[0]) if release_row else None
    accepted_count = db.execute("SELECT count(*) FROM objects WHERE accepted=1").fetchone()[0]
    delivery_audit_count = db.execute("SELECT count(*) FROM object_delivery_audits").fetchone()[0]
    scope_audit_count = db.execute("SELECT count(*) FROM object_scope_audits").fetchone()[0]
    if accepted_count and delivery_audit_count == 0 and scope_audit_count == 0:
        return {
            "status": "RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED",
            "N": None, "R": None, "C": None, "RC": None,
            "source_identities_total": accepted_count,
            "blocked_source_identities": accepted_count,
            "delivery_audited_rows": 0,
            "scope_audited_rows": 0,
            "blocked_reasons": {"RSI_V23_DELIVERY_AUDIT_NOT_MIGRATED": accepted_count},
            "migration_required": [],
        }
    material_state = {r["material_id"]: r for r in _state_rows(db)}
    objects = _rows(db, """SELECT id,namespace,source_uid,name_cn,name_en,source_url,asset_url
                            FROM objects WHERE accepted=1 ORDER BY id""")
    delivery = {r["object_id"]: r for r in _rows(db, "SELECT * FROM object_delivery_audits")}
    scope = {r["object_id"]: r for r in _rows(db, "SELECT * FROM object_scope_audits")}
    geometry_groups = {r["geometry_id"]: r for r in _rows(db, "SELECT * FROM object_geometry_groups")}
    components = defaultdict(list)
    for row in _rows(db, "SELECT object_id,id,kind FROM components ORDER BY object_id,id"):
        components[row["object_id"]].append(row)
    links = defaultdict(set)
    linked_components = defaultdict(set)
    for row in _rows(db, """SELECT object_id,component_id,material_id FROM material_links
                            WHERE accepted=1 ORDER BY object_id,material_id"""):
        links[row["object_id"]].add(row["material_id"])
        linked_components[row["object_id"]].add(row["component_id"])
    open_obligations = Counter(r["object_id"] for r in _rows(db, "SELECT object_id FROM obligations WHERE resolved=0 AND object_id IS NOT NULL"))
    config_rows = _rows(db, "SELECT * FROM object_configurations WHERE accepted=1 ORDER BY geometry_key,config_signature")
    configs_by_object = defaultdict(list)
    for row in config_rows:
        configs_by_object[row["object_id"]].append(row)

    eligible_rows, blocked_reasons = [], Counter()
    for obj in objects:
        audit = delivery.get(obj["id"])
        if not audit:
            blocked_reasons["DELIVERY_AUDIT_MISSING"] += 1
            continue
        if not release_id or audit["release_id"] != release_id:
            blocked_reasons["RELEASE_MISMATCH"] += 1
            continue
        if audit["review_status"] != "PASS":
            blocked_reasons["DELIVERY_REVIEW_NOT_PASS"] += 1
            continue
        if not audit["dedup_reviewed"] or not audit["source_link_verified"] or not audit["asset_location_verified"]:
            blocked_reasons["IDENTITY_OR_LINK_NOT_VERIFIED"] += 1
            continue
        geometry_group = geometry_groups.get(audit["geometry_id"])
        if (not geometry_group or not geometry_group["reviewed"]
                or not geometry_group["comparison_method"].strip() or not geometry_group["basis"].strip()):
            blocked_reasons["GEOMETRY_GROUP_UNREVIEWED"] += 1
            continue
        if geometry_group["canonical_object_id"] != obj["id"]:
            blocked_reasons["GEOMETRY_ALIAS_NOT_CANONICAL"] += 1
            continue
        if (not audit["geometry_id"].strip() or not audit["asset_member_locator"].strip()
                or not audit["license_status"].strip() or not audit["access_status"].strip()
                or audit["license_status"].strip().upper() == "UNKNOWN"
                or audit["access_status"].strip().upper() == "UNKNOWN"):
            blocked_reasons["DELIVERY_FIELDS_INCOMPLETE"] += 1
            continue
        if any(not str(obj[field]).strip() for field in ("name_cn", "name_en", "source_url", "asset_url")):
            blocked_reasons["OBJECT_FIELDS_INCOMPLETE"] += 1
            continue

        parts = components.get(obj["id"], [])
        node_scope = scope.get(obj["id"], {})
        object_links = sorted(links.get(obj["id"], set()))
        covered = sorted(mid for mid in object_links
                         if mid in material_state and not material_state[mid]["missing"])
        unmapped_components = len(set(p["id"] for p in parts) - linked_components.get(obj["id"], set()))
        scope_review_missing = node_scope.get("review_status") != "PASS" or not node_scope.get("source_locator", "").strip()
        unresolved = open_obligations[obj["id"]]
        unresolved_component = unmapped_components + int(scope_review_missing)
        unresolved_material = unresolved + unmapped_components
        base = {"release_id": release_id, "namespace": obj["namespace"], "source_uid": obj["source_uid"],
                "accepted": True, "dedup_reviewed": True, "geometry_id": audit["geometry_id"],
                "name_cn": obj["name_cn"], "name_en": obj["name_en"], "source_url": obj["source_url"],
                "asset_url": obj["asset_url"], "asset_member_locator": audit["asset_member_locator"],
                "license_status": audit["license_status"], "access_status": audit["access_status"],
                "asset_location_verified": True, "source_link_verified": True,
                "configuration_kind": "BASE", "component_kinds": sorted({p["kind"] for p in parts}),
                "source_scope_complete": (node_scope.get("source_scope_complete") == 1
                                           and node_scope.get("review_status") == "PASS"
                                           and bool(node_scope.get("source_locator", "").strip())),
                "component_readiness_basis": (node_scope.get("component_readiness_basis", "")
                                               if node_scope.get("review_status") == "PASS" else ""),
                "whole_scope_positive": (node_scope.get("whole_scope_positive") == 1
                                          if node_scope.get("review_status") == "PASS" else False),
                "unresolved_component_obligations": unresolved_component,
                "unresolved_material_obligations": unresolved_material,
                "required_material_ids": object_links, "covered_material_ids": covered}
        eligible_rows.append(base)
        for cfg in configs_by_object.get(obj["id"], []):
            raw = json.loads(cfg["raw_json"])
            configuration_materials = raw.get("configuration_materials")
            if not isinstance(configuration_materials, list) or not configuration_materials:
                raise ValueError("Accepted configuration lacks scoped material mappings: " + cfg["configuration_key"])
            config = {**base, "configuration_kind": "EXPLICIT", "configuration_reviewed": True,
                      "configuration_resolved": True, "configuration_basis": cfg["basis"],
                      "configuration_materials": configuration_materials}
            key = configuration_key(config)
            if key != (cfg["geometry_key"], cfg["config_signature"]):
                raise ValueError("Configuration signature does not match reviewed component/material mapping: " + cfg["configuration_key"])
            config["required_material_ids"] = sorted(set(object_links) |
                {m["material_id"] for m in configuration_materials})
            config["covered_material_ids"] = sorted(mid for mid in config["required_material_ids"]
                if mid in material_state and not material_state[mid]["missing"])
            config["unresolved_material_obligations"] = (unresolved + int(any(
                mid not in material_state or material_state[mid]["missing"]
                for mid in config["required_material_ids"])))
            eligible_rows.append(config)

    metrics = delivery_summary(eligible_rows)
    metrics.update({"source_identities_total": len(objects),
                    "delivery_audited_rows": len({(r["namespace"], r["source_uid"]) for r in eligible_rows}),
                    "blocked_source_identities": sum(blocked_reasons.values()),
                    "blocked_reasons": dict(blocked_reasons),
                    "N_definition": "reviewed geometry/configuration rows only; same-release, source/link/asset checked, canonical geometry deduplicated",
                    "R_definition": "source component scope independently reviewed complete, component keys represented with allowed kinds, and WHOLE positively supported; unresolved material-label/relation obligations affect C, not R",
                    "C_definition": "all recorded component materials and alternatives have E/nu/rho sources; no unresolved object obligations"})
    return metrics


def bfs_material_frontier(db):
    """Return scientific BFS order; display edges never affect this order."""
    _require_derived_state(db)
    return sorted(_state_rows(db), key=lambda r: (r["depth"], r["family"], r["material_id"]))


def release_view_consistency(view_rows):
    """Validate that overview/tree/evidence views consume one release/input."""
    rows = list(view_rows)
    if not rows:
        raise ValueError("At least one release view is required")
    releases = {r["release_id"] for r in rows}
    inputs = {r["input_sha256"] for r in rows}
    if len(releases) != 1 or len(inputs) != 1:
        raise ValueError("Release views do not share one release or input snapshot")
    required = {"overview", "material_tree", "evidence_matrix"}
    names = {r["view_name"] for r in rows}
    if names != required:
        raise ValueError("Exactly the three canonical release views are required")
    if any(r.get("status") != "VERIFIED" for r in rows):
        raise ValueError("All release views must be independently verified")
    return {"release_id": rows[0]["release_id"], "input_sha256": rows[0]["input_sha256"],
            "views": sorted(names)}
