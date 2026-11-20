"""Pure RSI 2.2 contracts; no filesystem, database mutation or evidence inference.

Inputs are reviewed, canonical projections. These helpers cannot establish
geometry equivalence, source truth, part completeness or material identity.
"""
import hashlib
import json


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be a nonempty canonical string')
    return value.strip()


def configuration_key(row):
    """Key one source-confirmed, resolved configuration on canonical scopes."""
    geometry = _text(row['geometry_id'], 'geometry_id')
    kind = row.get('configuration_kind')
    if kind == 'BASE':
        return geometry, 'BASE'
    if kind != 'EXPLICIT' or row.get('configuration_reviewed') is not True:
        raise ValueError('Explicit configurations require review')
    _text(row.get('configuration_basis'), 'configuration_basis')
    if row.get('configuration_resolved') is not True:
        raise ValueError('Unresolved alternatives are not configurations')
    pairs = [(_text(v['scope_id'], 'scope_id'), _text(v['material_id'], 'material_id'))
             for v in row.get('configuration_materials', [])]
    if not pairs or len(set(pairs)) != len(pairs):
        raise ValueError('A configuration needs unique scoped material facts')
    payload = json.dumps(sorted(pairs), ensure_ascii=False, separators=(',', ':'))
    return geometry, hashlib.sha256(payload.encode()).hexdigest()


def _component_ready(row):
    if row.get('source_scope_complete') is not True or not row.get('component_readiness_basis'):
        return False
    if row.get('unresolved_component_obligations', 0) != 0:
        return False
    kinds = row.get('component_kinds', [])
    if not kinds or any(k not in ('PHYSICAL', 'SEMANTIC', 'MATERIAL_SCOPE', 'WHOLE') for k in kinds):
        return False
    return 'WHOLE' not in kinds or row.get('whole_scope_positive') is True


def _property_ready(row):
    def material_set(field):
        values = row.get(field, [])
        if not isinstance(values, (list, tuple)):
            raise ValueError(field + ' must be an explicit list of material IDs')
        return {_text(value, field) for value in values}
    required = material_set('required_material_ids')
    if row.get('configuration_kind') == 'EXPLICIT':
        required.update(v['material_id'].strip() for v in row['configuration_materials'])
    covered = material_set('covered_material_ids')
    return bool(required) and not row.get('unresolved_material_obligations', 0) and required <= covered


def delivery_summary(rows):
    """Count N/R/C/RC on one cohort; preserve incomplete duplicate obligations.

    Duplicate source/config projections combine conservatively. Generic base
    obligations also apply to its configurations until an upstream reviewed
    resolution closes them. This routine never creates material combinations.
    """
    rows = list(rows)
    sources = set()
    provisional = set()
    groups = {}
    releases = set()
    identity_geometry = {}
    required_fields = ('name_cn', 'name_en', 'source_url', 'asset_url',
                       'asset_member_locator', 'license_status', 'access_status')
    for row in rows:
        source = (_text(row['namespace'], 'namespace'), _text(row['source_uid'], 'source_uid'))
        sources.add(source)
        if row.get('accepted') is not True:
            continue
        releases.add(_text(row.get('release_id'), 'release_id'))
        if len(releases) > 1:
            raise ValueError('Delivery cohort contains mixed releases')
        if row.get('dedup_reviewed') is not True:
            provisional.add(source)
            continue
        geometry = _text(row.get('geometry_id'), 'geometry_id')
        if source in identity_geometry and identity_geometry[source] != geometry:
            raise ValueError('One source identity maps to conflicting canonical geometries')
        identity_geometry[source] = geometry
        for field in required_fields:
            _text(row.get(field), field)
        if row.get('asset_location_verified') is not True:
            raise ValueError('Asset location must be verified before delivery counting')
        key = configuration_key(row)
        groups.setdefault(key, []).append(row)
    bases = {g: items for (g, config), items in groups.items() if config == 'BASE'}
    configured = {g for g, config in groups if config != 'BASE'}
    selected = [(key, items + (bases.get(key[0], []) if key[1] != 'BASE' else []))
                for key, items in groups.items() if not (key[1] == 'BASE' and key[0] in configured)]
    ready = [(all(_component_ready(row) for row in items), all(_property_ready(row) for row in items))
             for key, items in selected]
    result = {'release_id': next(iter(releases)) if releases else None,
              'N': len(selected), 'G': len({key[0] for key, items in selected}),
              'S': len(sources), 'U_source_identities': len(provisional),
              'explicit_configurations': sum(key[1] != 'BASE' for key, items in selected),
              'R': sum(r for r, c in ready), 'C': sum(c for r, c in ready),
              'RC': sum(r and c for r, c in ready)}
    result['scale_100k'] = result['N'] >= 100000
    result['all_components_ready'] = bool(result['N']) and result['R'] == result['N']
    result['all_properties_ready'] = bool(result['N']) and result['C'] == result['N']
    return result


def migrate_frontier(scan, candidates, current_tree_epoch, aliases=None):
    """Migrate one persistent scan without replaying routes or resetting spend.

    Candidates carry current eligibility/depth/tier from a separately reviewed
    graph. Identity splits must be withheld as ineligible with an audit reason.
    Completed routes and pending subjects use canonical IDs after alias review.
    """
    aliases = aliases or {}
    old_epoch = _text(scan['tree_epoch'], 'old_tree_epoch')
    new_epoch = _text(current_tree_epoch, 'current_tree_epoch')
    def canonical(value):
        seen = set()
        while value in aliases:
            if value in seen:
                raise ValueError('Alias cycle')
            seen.add(value)
            value = aliases[value]
        return _text(value, 'material_id')
    def key(item):
        scope = _text(item.get('attribute_scope'), 'attribute_scope')
        if scope != 'NONE':
            properties = scope.split('+')
            if not properties or len(set(properties)) != len(properties) or not set(properties) <= {'E', 'nu', 'rho'}:
                raise ValueError('attribute_scope must name actual target properties')
            scope = '+'.join(p for p in ('E', 'nu', 'rho') if p in properties)
        return (canonical(item['material_id']), _text(item['task_type'], 'task_type'), scope,
                _text(item['route_key'], 'route_key'))
    previous = {key(item) for item in scan.get('pending', [])}
    completed = {key(item) for item in scan.get('completed', [])}
    frontier, deferred, audit = {}, {}, []
    for item in candidates:
        task_key = key(item)
        current = dict(item, material_id=task_key[0])
        if current.get('eligible') is not True:
            audit.append({'key': task_key, 'status': 'INELIGIBLE', 'reason': current.get('reason', 'CURRENT_STATE_INELIGIBLE')})
            continue
        if task_key in completed:
            audit.append({'key': task_key, 'status': 'COMPLETED_ROUTE_RETAINED'})
            continue
        current['attribute_scope'] = task_key[2]
        if (not isinstance(current.get('depth'), int) or isinstance(current['depth'], bool)
                or current['depth'] < 0 or not isinstance(current.get('tier'), int)
                or isinstance(current['tier'], bool) or current['tier'] < 0):
            raise ValueError('Current scientific depth/tier must be explicit integers')
        urgent = current.get('urgent_existing_object_gap') is True
        if urgent:
            _text(current.get('preemption_reason'), 'preemption_reason')
        use_frontier = task_key in previous or urgent or task_key in frontier
        if use_frontier and task_key in deferred:
            del deferred[task_key]
        target = frontier if use_frontier else deferred
        rank = lambda x: (x['tier'], x['depth'], x.get('family', ''), task_key)
        if task_key not in target or rank(current) < rank(target[task_key]):
            target[task_key] = current
    for removed in previous - set(frontier) - completed:
        audit.append({'key': removed, 'status': 'REMOVED_OR_DEFERRED', 'reason': 'NOT_ELIGIBLE_IN_CURRENT_INPUT'})
    order = lambda x: (x['tier'], x['depth'], x.get('family', ''), key(x))
    encode = lambda k: dict(zip(('material_id', 'task_type', 'attribute_scope', 'route_key'), k))
    return {'scan_id': _text(scan['scan_id'], 'scan_id'),
            'old_tree_epoch': old_epoch, 'tree_epoch': new_epoch,
            'spent': dict(scan['spent']), 'completed': [encode(k) for k in sorted(completed)],
            'pending': sorted(frontier.values(), key=order), 'next_scan': sorted(deferred.values(), key=order),
            'revoked_lease_tokens': sorted({item['token'] for item in scan.get('leases', [])}),
            'audit': audit}
