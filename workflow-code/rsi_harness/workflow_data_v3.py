"""Pure, standard-library data operations for the RSI v3 workflow.

No function reads files, writes files, dispatches models or admits scientific
claims. PASS means a caller supplies an existing reviewed decision. See
``example_bundle()`` for the normalized, JSON-serializable input schema.

Required tables and keys:
  objects: object_id
  components: component_id, object_id, scope, source_locator
  materials: material_id (optional excluded: bool, scope: solid/liquid/void/...)
  relations: relation_id, component_id, material_id, decision
  taxonomy: edge_id, child_id, parent_id, relation, decision
  evidence: record_id, material_id, document_id, source_group_id, decision

PASS relations/edges additionally require basis, source_locator and reviewer.
PASS evidence requires origin, source_quote, source_locator, source_url,
reviewer and properties. Each evidence row represents one source-defined group;
its properties map E/nu/rho to {value, unit} or {lower, upper, unit}.
Conditions may be unknown. Unknown fields are preserved, never interpreted as
numeric evidence. Counts describe supplied data, never project completion.
"""
from __future__ import annotations

from collections import Counter, deque
from copy import deepcopy
import hashlib
import json
import math
import re


TABLE_KEYS = {"objects": "object_id", "components": "component_id",
              "materials": "material_id", "relations": "relation_id",
              "taxonomy": "edge_id", "evidence": "record_id"}
PROPERTIES = ("E", "nu", "rho")
DECISIONS = {"PASS", "HOLD", "REJECT", "EXCLUDE", "WITHDRAWN"}
EXCLUDED_SCOPES = {"liquid", "void", "empty_space", "organizational", "special_domain"}
ORIGINS = {"source_reported", "experiment", "measured", "literature", "compilation", "handbook"}
NON_ASSETS = {"headline", "paper_headline", "scene", "image", "view", "voxel", "gaussian",
              "augmentation", "prediction", "gap", "enumeration_gap"}
UNITS = {"E": {"Pa": 1, "kPa": 1e3, "MPa": 1e6, "GPa": 1e9},
         "nu": {"1": 1, "dimensionless": 1},
         "rho": {"kg/m3": 1, "kg/m³": 1, "g/cm3": 1e3, "g/cm³": 1e3}}


def _text(row, key):
    value = row.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected nonempty text: " + key)
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _digest(value, prefix):
    return prefix + hashlib.sha256(_canonical(value).encode()).hexdigest()


def source_identity(namespace: str, source_uid: str) -> str:
    """Unambiguous stable identity, including when either field contains ':'."""
    _text({"namespace": namespace}, "namespace")
    _text({"source_uid": source_uid}, "source_uid")
    return _digest([namespace, source_uid], "source:")


def enumerate_sources(rows) -> dict:
    """Enumerate actual assets; return sources, duplicates, conflicts and gaps.

    Input is an iterable of dictionaries with namespace/source_uid. Explicit
    non-asset record_type rows go to gaps and never form placeholder assets.
    Conflicting duplicate identities retain every original in conflicts; one
    deterministic representative is returned in sources for identity counting.
    """
    grouped, gaps = {}, []
    for original in rows:
        if not isinstance(original, dict):
            raise ValueError("Source rows must be dictionaries")
        row = deepcopy(original)
        if row.get("record_type", "asset") in NON_ASSETS:
            gaps.append(row)
            continue
        if row.get("record_type", "asset") != "asset":
            raise ValueError("Unknown source record_type")
        identity = source_identity(_text(row, "namespace"), _text(row, "source_uid"))
        if "source_id" in row and row["source_id"] != identity:
            raise ValueError("source_id disagrees with stable identity")
        row["source_id"] = identity
        grouped.setdefault(identity, []).append(row)
    sources, duplicates, conflicts = [], [], []
    for identity, group in sorted(grouped.items()):
        unique = {_canonical(row): row for row in group}
        sources.append(unique[min(unique)])
        if len(group) > len(unique):
            duplicates.append({"source_id": identity, "count": len(group) - len(unique)})
        if len(unique) > 1:
            conflicts.append({"code": "SOURCE_IDENTITY_CONFLICT", "source_id": identity,
                              "rows": [unique[key] for key in sorted(unique)]})
    return {"sources": sources, "duplicates": duplicates, "conflicts": conflicts,
            "gaps": sorted(gaps, key=_canonical)}


def deduplicate(rows, reviewed_aliases=()) -> dict:
    """Merge only trusted exact asset hashes or explicit reviewed alias pairs.

    A trusted hash is asset_sha256 (64 hex digits) with
    asset_sha256_verified=True. Alias rows require left_source_id,
    right_source_id, decision and, for PASS, reviewer/source_locator. Conflicting
    source identities and conflicting PASS/REJECT alias pairs stay separate.
    Names, generic file hashes and unreviewed fingerprints never merge assets.
    """
    result = enumerate_sources(rows)
    sources = {row["source_id"]: row for row in result["sources"]}
    parent = {identity: identity for identity in sources}
    blocked = {item["source_id"] for item in result["conflicts"]}
    conflicts = deepcopy(result["conflicts"])

    def find(identity):
        while parent[identity] != identity:
            parent[identity] = parent[parent[identity]]
            identity = parent[identity]
        return identity

    def merge(left, right):
        if left in blocked or right in blocked:
            return
        a, b = sorted((find(left), find(right)))
        parent[b] = a

    pairs = {}
    for alias in reviewed_aliases:
        left, right = _text(alias, "left_source_id"), _text(alias, "right_source_id")
        if left not in sources or right not in sources:
            raise ValueError("Alias has an unknown source foreign key")
        decision = alias.get("decision")
        if decision not in DECISIONS:
            raise ValueError("Invalid alias decision")
        if decision == "PASS":
            _text(alias, "reviewer")
            _text(alias, "source_locator")
        pairs.setdefault(tuple(sorted((left, right))), []).append(deepcopy(alias))
    rejected = set()
    for pair, aliases in sorted(pairs.items()):
        decisions = {row["decision"] for row in aliases}
        if "REJECT" in decisions:
            rejected.add(pair)
        if "PASS" in decisions and "REJECT" in decisions:
            conflicts.append({"code": "ALIAS_DECISION_CONFLICT", "source_ids": list(pair), "rows": aliases})
    hashes = {}
    for identity, row in sorted(sources.items()):
        if row.get("asset_sha256_verified") is True:
            asset_hash = row.get("asset_sha256", "")
            if not isinstance(asset_hash, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", asset_hash):
                raise ValueError("Verified asset SHA must contain 64 hex digits")
            hashes.setdefault(asset_hash.lower(), []).append(identity)
    # A reviewed rejection blocks even indirect alias/hash joins of that pair.
    def safe_merge(left, right):
        a, b = find(left), find(right)
        if any({find(x), find(y)} == {a, b} for x, y in rejected):
            conflicts.append({"code": "MERGE_REJECTED", "source_ids": sorted((left, right))})
            return
        merge(left, right)
    for group in sorted(hashes.values()):
        for identity in group[1:]:
            safe_merge(group[0], identity)
    for pair, aliases in sorted(pairs.items()):
        if any(row["decision"] == "PASS" for row in aliases) and pair not in rejected:
            safe_merge(*pair)
    groups = {}
    for identity in sorted(sources):
        groups.setdefault(find(identity), []).append(identity)
    geometries = [{"geometry_id": _digest(min(members), "geometry:"), "source_ids": members}
                  for members in groups.values()]
    mapping = {identity: geometry["geometry_id"] for geometry in geometries for identity in geometry["source_ids"]}
    return {**result, "conflicts": conflicts, "geometries": geometries,
            "source_to_geometry": mapping, "source_count": len(sources),
            "geometry_count": len(geometries)}


def _index(bundle, table):
    if table not in bundle or not isinstance(bundle[table], list):
        raise ValueError("Missing normalized table: " + table)
    result = {}
    for row in bundle[table]:
        if not isinstance(row, dict):
            raise ValueError("Expected dictionary row: " + table)
        identity = _text(row, TABLE_KEYS[table])
        if identity in result:
            raise ValueError("Duplicate " + TABLE_KEYS[table] + ": " + identity)
        result[identity] = row
    return result


def _review(row):
    if row.get("decision") not in DECISIONS:
        raise ValueError("Invalid or missing decision")
    if row["decision"] == "PASS":
        _text(row, "reviewer")
        if row.get("collector") == row["reviewer"]:
            raise ValueError("Collector cannot independently review own record")


def _fk(row, field, index):
    if _text(row, field) not in index:
        raise ValueError("Unknown foreign key: " + field)


def _bounds(prop, value):
    if not isinstance(value, dict):
        raise ValueError("Property observation must be a dictionary: " + prop)
    unit = _text(value, "unit")
    if unit not in UNITS[prop]:
        raise ValueError("Unsupported property unit: " + prop + "/" + unit)
    if "value" in value:
        if "lower" in value or "upper" in value:
            raise ValueError("Use a value or a bound pair, not both")
        lower = upper = value["value"]
    else:
        if "lower" not in value or "upper" not in value:
            raise ValueError("Both property bounds are required")
        lower, upper = value["lower"], value["upper"]
    for number in (lower, upper):
        try:
            finite = math.isfinite(number)
        except (TypeError, OverflowError):
            finite = False
        if isinstance(number, bool) or not isinstance(number, (int, float)) or not finite:
            raise ValueError("Property value must be finite and numeric")
    if lower > upper or (prop in {"E", "rho"} and lower <= 0):
        raise ValueError("Inverted bounds or nonpositive E/rho")
    factor = UNITS[prop][unit]
    converted = lower * factor, upper * factor
    if not all(math.isfinite(number) for number in converted):
        raise ValueError("Property bounds overflow in SI units")
    return converted


def _numeric_provenance(row):
    if "origin" in row and row["origin"] not in ORIGINS:
        raise ValueError("Numerical origin is not source evidence")
    for key in ("is_model_value", "is_simulation_input", "is_solver_default", "is_generated"):
        if row.get(key, False) is not False:
            raise ValueError("Forbidden numerical provenance: " + key)


def _parents(indexes):
    parents = {identity: set() for identity in indexes["materials"]}
    for row in indexes["taxonomy"].values():
        if row["decision"] == "PASS" and row["relation"] == "IS_A":
            parents[row["child_id"]].add(row["parent_id"])
    return parents


def _depths(parents):
    children = {identity: set() for identity in parents}
    for child, group in parents.items():
        for parent in group:
            children[parent].add(child)
    roots = sorted(identity for identity, group in parents.items() if not group)
    depth, queue = {}, deque((identity, 0) for identity in roots)
    while queue:
        identity, level = queue.popleft()
        if identity in depth:
            continue
        depth[identity] = level
        queue.extend((child, level + 1) for child in sorted(children[identity]))
    if len(depth) != len(parents):
        raise ValueError("Accepted IS_A graph contains a cycle")
    # Root reachability alone does not detect a cycle that also has a root path.
    remaining = {identity: len(group) for identity, group in parents.items()}
    queue = deque(roots)
    seen = 0
    while queue:
        identity = queue.popleft()
        seen += 1
        for child in sorted(children[identity]):
            remaining[child] -= 1
            if remaining[child] == 0:
                queue.append(child)
    if seen != len(parents):
        raise ValueError("Accepted IS_A graph contains a cycle")
    return depth


def validate_bundle(bundle: dict) -> dict:
    """Raise ValueError at schema/provenance/FK boundaries; return counts.

    HOLD/REJECT rows retain their identity and foreign keys but contribute no
    accepted links, tree edges or numeric values. Complete and partial groups
    are admitted concurrently. Validation neither alters nor reviews rows.
    """
    if not isinstance(bundle, dict):
        raise ValueError("Bundle must be a dictionary")
    indexes = {table: _index(bundle, table) for table in TABLE_KEYS}
    for row in indexes["materials"].values():
        if "excluded" in row and not isinstance(row["excluded"], bool):
            raise ValueError("Material excluded must be boolean")
    for row in indexes["components"].values():
        _fk(row, "object_id", indexes["objects"])
        _text(row, "scope")
        _text(row, "source_locator")
    for row in indexes["relations"].values():
        _review(row)
        _fk(row, "component_id", indexes["components"])
        _fk(row, "material_id", indexes["materials"])
        if row["decision"] == "PASS":
            _text(row, "basis")
            _text(row, "source_locator")
    for row in indexes["taxonomy"].values():
        _review(row)
        _fk(row, "child_id", indexes["materials"])
        _fk(row, "parent_id", indexes["materials"])
        _text(row, "relation")
        if row["decision"] == "PASS":
            _text(row, "basis")
            _text(row, "source_locator")
    _depths(_parents(indexes))
    groups, complete, partial = set(), 0, 0
    for row in indexes["evidence"].values():
        _review(row)
        _fk(row, "material_id", indexes["materials"])
        _text(row, "document_id")
        _text(row, "source_group_id")
        if row["decision"] != "PASS":
            continue
        for key in ("source_quote", "source_locator", "source_url"):
            _text(row, key)
        if row.get("origin") not in ORIGINS:
            raise ValueError("Numerical origin is not source evidence")
        _numeric_provenance(row)
        properties = row.get("properties")
        if not isinstance(properties, dict) or not properties or set(properties) - set(PROPERTIES):
            raise ValueError("Evidence needs a nonempty E/nu/rho property map")
        for prop, value in properties.items():
            _bounds(prop, value)
            _numeric_provenance(value)
        group = row["material_id"], row["document_id"], row["source_group_id"]
        if group in groups:
            raise ValueError("Duplicate source-defined evidence group")
        groups.add(group)
        complete += set(properties) == set(PROPERTIES)
        partial += set(properties) != set(PROPERTIES)
    return {"valid": True, "row_counts": {table: len(rows) for table, rows in indexes.items()},
            "complete_group_count": complete, "partial_group_count": partial}


def recompute(bundle: dict) -> dict:
    """Recompute upward-only material coverage and the four disjoint states.

    All rolled-up sets deduplicate IDs, including diamond IS_A graphs. Property
    ranges are SI research ranges with source definitions/conditions retained
    in the original evidence rows; they are never simulation assignments.
    """
    validation = validate_bundle(bundle)
    indexes = {table: _index(bundle, table) for table in TABLE_KEYS}
    parents = _parents(indexes)
    depths = _depths(parents)
    active = {identity for identity, row in indexes["materials"].items()
              if not row.get("excluded", False) and row.get("scope", "solid") not in EXCLUDED_SCOPES}
    direct_objects = {identity: set() for identity in parents}
    direct_records = {identity: set() for identity in parents}
    for relation in indexes["relations"].values():
        if relation["decision"] == "PASS":
            component = indexes["components"][relation["component_id"]]
            direct_objects[relation["material_id"]].add(component["object_id"])
    for record in indexes["evidence"].values():
        if record["decision"] == "PASS":
            direct_records[record["material_id"]].add(record["record_id"])
    objects, records = deepcopy(direct_objects), deepcopy(direct_records)
    # Iterative ancestor traversal handles arbitrary DAG depth without recursion.
    for identity in sorted(active):
        ancestors, queue = set(), deque(sorted(parents[identity]))
        while queue:
            ancestor = queue.popleft()
            if ancestor in ancestors:
                continue
            ancestors.add(ancestor)
            queue.extend(sorted(parents[ancestor]))
        for ancestor in ancestors & active:
            objects[ancestor].update(direct_objects[identity])
            records[ancestor].update(direct_records[identity])
    states, material_states = Counter({state: 0 for state in ("S1", "S2", "S3", "S4")}), []
    for identity in sorted(parents):
        evidence = [indexes["evidence"][key] for key in sorted(records[identity])]
        by_property = {prop: [row for row in evidence if prop in row["properties"]] for prop in PROPERTIES}
        covered = [prop for prop in PROPERTIES if by_property[prop]]
        complete_count = sum(set(row["properties"]) == set(PROPERTIES) for row in evidence)
        has_objects = bool(objects[identity])
        state = ("S1" if has_objects else "S2") if len(covered) == 3 else ("S3" if has_objects else "S4")
        excluded = identity not in active
        if not excluded:
            states[state] += 1
        ranges = {}
        for prop, source_rows in by_property.items():
            bounds = [_bounds(prop, row["properties"][prop]) for row in source_rows]
            if bounds:
                ranges[prop] = {"lower": min(pair[0] for pair in bounds), "upper": max(pair[1] for pair in bounds),
                                "unit": {"E": "Pa", "nu": "1", "rho": "kg/m3"}[prop],
                                "record_ids": [row["record_id"] for row in source_rows],
                                "document_count": len({row["document_id"] for row in source_rows})}
        material_states.append({"material_id": identity, "depth": depths[identity], "excluded": excluded,
                                "state": None if excluded else state, "covered_properties": covered,
                                "missing_properties": [prop for prop in PROPERTIES if prop not in covered],
                                "direct_object_count": len(direct_objects[identity]),
                                "rolled_up_object_count": len(objects[identity] - direct_objects[identity]),
                                "object_count": len(objects[identity]), "object_ids": sorted(objects[identity]),
                                "direct_record_count": len(direct_records[identity]),
                                "record_count": len(evidence), "record_ids": sorted(records[identity]),
                                "complete_group_count": complete_count,
                                "partial_group_count": len(evidence) - complete_count,
                                "document_count": len({row["document_id"] for row in evidence}),
                                "lineage_count": len({row["lineage_id"] for row in evidence if row.get("lineage_id")}),
                                "ranges": ranges})
    accepted = [row for row in indexes["evidence"].values() if row["decision"] == "PASS"]
    counts = {**validation["row_counts"], "active_material_count": len(active),
              "excluded_material_count": len(parents) - len(active),
              "complete_group_count": validation["complete_group_count"],
              "partial_group_count": validation["partial_group_count"],
              "document_count": len({row["document_id"] for row in accepted}),
              "lineage_count": len({row["lineage_id"] for row in accepted if row.get("lineage_id")}),
              "accepted_relation_count": sum(row["decision"] == "PASS" for row in indexes["relations"].values()),
              "states": dict(states)}
    return {"material_states": material_states, "counts": counts}


def bfs_tasks(bundle: dict, *, kind: str = "material", limit: int = 100,
              visited=(), soft_weights: dict | None = None) -> list[dict]:
    """Return deterministic tasks, ordered by depth, state priority, then weight.

    kind='object' schedules only S1/S2 material nodes for object expansion.
    Material research prioritizes S3, S2, then S1/S4 within each BFS layer.
    Soft weights break ties within a layer and state tier, never either order.
    This pure projection does not claim leases, mark visited or reset budgets.
    """
    if kind not in {"material", "object"} or isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("Expected material/object kind and positive integer limit")
    soft_weights = {} if soft_weights is None else soft_weights
    if not isinstance(soft_weights, dict):
        raise ValueError("soft_weights must map material IDs to finite numbers")
    for weight in soft_weights.values():
        if isinstance(weight, bool) or not isinstance(weight, (int, float)) or not math.isfinite(weight):
            raise ValueError("Soft weights must be finite numbers")
    seen = set(visited)
    priority = {"S3": 0, "S2": 1, "S1": 2, "S4": 2}
    rows = [row for row in recompute(bundle)["material_states"]
            if not row["excluded"] and row["material_id"] not in seen
            and (kind != "object" or row["state"] in {"S1", "S2"})]
    rows.sort(key=lambda row: (row["depth"], priority[row["state"]],
                               -soft_weights.get(row["material_id"], 0), row["material_id"]))
    return [{"material_id": row["material_id"], "depth": row["depth"], "state": row["state"],
             "kind": kind, "priority": priority[row["state"]],
             "soft_weight": soft_weights.get(row["material_id"], 0),
             "missing_properties": row["missing_properties"], "execution_status": "NOT_EXECUTED"}
            for row in rows[:limit]]


def reconcile(parent: dict, bundle: dict) -> dict:
    """Independent per-table identity reconciliation, including duplicate rows.

    Unlike validate_bundle, this diagnostic accepts duplicate IDs so they can
    be counted. added/withdrawn concern identity presence, changed/unchanged
    compare complete row payloads, and duplicate counts are excess rows on
    each side. No category is silently netted against another.
    """
    tables = {}
    for table, key in TABLE_KEYS.items():
        groups = []
        for data in (parent, bundle):
            if not isinstance(data, dict) or not isinstance(data.get(table), list):
                raise ValueError("Missing normalized table: " + table)
            group = {}
            for row in data[table]:
                if not isinstance(row, dict):
                    raise ValueError("Expected dictionary row: " + table)
                group.setdefault(_text(row, key), []).append(_canonical(row))
            groups.append(group)
        old, new = groups
        common = old.keys() & new.keys()
        added, withdrawn = sorted(new.keys() - old.keys()), sorted(old.keys() - new.keys())
        changed = sorted(identity for identity in common if set(old[identity]) != set(new[identity]))
        tables[table] = {"parent_unique_count": len(old), "current_unique_count": len(new),
                         "added": len(added), "withdrawn": len(withdrawn), "changed": len(changed),
                         "unchanged": len(common) - len(changed),
                         "duplicates": sum(len(rows) - 1 for rows in new.values()),
                         "parent_duplicates": sum(len(rows) - 1 for rows in old.values()),
                         "added_ids": added, "withdrawn_ids": withdrawn, "changed_ids": changed,
                         "duplicate_ids": sorted(identity for identity in new if len(new[identity]) > 1)}
        if len(old) + len(added) - len(withdrawn) != len(new):
            raise ValueError("Identity reconciliation failed")
    return {"tables": tables, "totals": {key: sum(row[key] for row in tables.values())
            for key in ("added", "withdrawn", "changed", "unchanged", "duplicates", "parent_duplicates")}}


def example_bundle() -> dict:
    """Return a fresh synthetic schema example; it is not source evidence."""
    return {"schema_version": "rsi-workflow-data-v3", "objects": [{"object_id": "example-object"}],
            "components": [{"component_id": "example-whole", "object_id": "example-object",
                            "scope": "WHOLE_OBJECT_FALLBACK", "source_locator": "fixture:asset/whole"}],
            "materials": [{"material_id": "example-solid", "scope": "solid"},
                          {"material_id": "example-subtype", "scope": "solid"}],
            "relations": [{"relation_id": "example-relation", "component_id": "example-whole",
                           "material_id": "example-subtype", "decision": "PASS", "reviewer": "fixture-reviewer",
                           "basis": "Synthetic schema example only", "source_locator": "fixture:asset/label"}],
            "taxonomy": [{"edge_id": "example-edge", "child_id": "example-subtype", "parent_id": "example-solid",
                          "relation": "IS_A", "decision": "PASS", "reviewer": "fixture-reviewer",
                          "basis": "Synthetic schema example only", "source_locator": "fixture:taxonomy"}],
            "evidence": [{"record_id": "example-group", "material_id": "example-subtype",
                          "document_id": "example-document", "source_group_id": "example-group",
                          "decision": "PASS", "reviewer": "fixture-reviewer", "origin": "source_reported",
                          "source_quote": "Synthetic test numbers, not scientific evidence", "source_locator": "fixture:table-1",
                          "source_url": "https://example.invalid/schema", "conditions": None,
                          "properties": {"E": {"value": 1, "unit": "GPa"}, "nu": {"value": 0.3, "unit": "1"},
                                         "rho": {"value": 1000, "unit": "kg/m3"}}}]}
