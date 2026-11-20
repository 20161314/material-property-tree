"""Pure design contracts for RSI 2.3; not production scheduling or admission.

Callers supply reviewed material facts and authorization limits. These helpers
do not infer source truth, user permission, geometry equivalence or completeness.
"""
import copy
import hashlib
import json
import math


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(name + ' must be nonempty')
    return value.strip()


def _integer(value, name):
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(name + ' must be a nonnegative integer')
    return value


def _budget(value, name):
    if not isinstance(value, dict) or set(value) != {'claims', 'seconds'}:
        raise ValueError(name + ' requires claims and seconds')
    _integer(value['claims'], name + '.claims')
    seconds = value['seconds']
    if (isinstance(seconds, bool) or not isinstance(seconds, (int, float))
            or not math.isfinite(seconds) or seconds < 0):
        raise ValueError(name + '.seconds must be finite and nonnegative')
    return dict(value)


def coverage_counts(materials, unresolved_obligations=0):
    """Report both named denominators without hiding unknown obligations."""
    unresolved = _integer(unresolved_obligations, 'unresolved_obligations')
    counts = {state: 0 for state in range(1, 5)}
    seen = set()
    for item in materials:
        key = _text(item['material_id'], 'material_id')
        if key in seen:
            raise ValueError('Duplicate canonical material ID')
        seen.add(key)
        for field in ('active', 'is_liquid', 'property_covered', 'has_object'):
            if type(item.get(field)) is not bool:
                raise ValueError(field + ' must be an explicit boolean')
        if item.get('kind') not in ('MATERIAL', 'CATEGORY', 'SPECIAL', 'EXCLUDED'):
            raise ValueError('Unknown node kind')
        if not item['active'] or item['is_liquid'] or item['kind'] != 'MATERIAL':
            continue
        state = (1 if item['property_covered'] else 3) if item['has_object'] else (2 if item['property_covered'] else 4)
        counts[state] += 1
    def ratio(numerator, denominator):
        return {'covered': numerator, 'required': denominator,
                'ratio': numerator / denominator if denominator else None}
    main = ratio(counts[1], counts[1] + counts[3])
    all_materials = ratio(counts[1] + counts[2], sum(counts.values()))
    return {'states': counts, 'K_object': main, 'K_all': all_materials,
            'unresolved_obligations': unresolved,
            'all_required_material_obligations_satisfied': bool(main['required'])
            and main['covered'] == main['required'] and unresolved == 0}


def object_task_eligible(task_type, material_state=None, existing_object=False,
                         object_id=None, obligation_id=None):
    """Discovery needs P; existing-object factual repair does not."""
    if type(existing_object) is not bool:
        raise ValueError('existing_object must be boolean')
    if material_state is not None and (type(material_state) is not int or material_state not in (1, 2, 3, 4)):
        raise ValueError('Unknown material state')
    if task_type == 'OBJECT_DISCOVERY':
        return material_state in (1, 2)
    repairs = {'OBJECT_COMPONENT_REPAIR', 'OBJECT_SCOPE_REPAIR',
               'OBJECT_ASSET_REPAIR', 'OBJECT_LABEL_REPAIR'}
    if task_type not in repairs:
        raise ValueError('Unknown object task type')
    if not existing_object:
        return False
    _text(object_id, 'object_id')
    _text(obligation_id, 'obligation_id')
    return True


def scan_execution_status(scan, unfinished_count, run_active=False):
    """Unfinished includes pending and leased tasks, not only ready tasks."""
    _integer(unfinished_count, 'unfinished_count')
    if type(run_active) is not bool:
        raise ValueError('run_active must be boolean')
    limits = _budget(scan['limits'], 'limits')
    spent = _budget(scan['spent'], 'spent')
    if not unfinished_count:
        return 'COMPLETE'
    if any(spent[key] >= limits[key] for key in ('claims', 'seconds')):
        return 'PAUSED_BUDGET'
    return 'RUNNING' if run_active else 'READY_FOR_NEXT_RUN'


def extend_scan_budget(scan, event, hard_limits=None):
    """Append one checked budget extension; never reset spend or frontier.

    Authorization is an upstream reviewed fact. A nonempty scope string alone
    does not grant permission. Exact replay returns a copy with no new event.
    """
    scan_id = _text(scan['scan_id'], 'scan_id')
    revision = _integer(scan['budget_revision'], 'budget_revision')
    before = _budget(scan['limits'], 'limits')
    spent = _budget(scan['spent'], 'spent')
    if event.get('scan_id') != scan_id:
        raise ValueError('Budget event belongs to another scan')
    event_id = _text(event.get('event_id'), 'event_id')
    for field in ('actor', 'reason', 'authorization_scope', 'created_at', 'data_epoch', 'tree_epoch'):
        _text(event.get(field), field)
    if not _integer(event.get('unfinished_count'), 'unfinished_count'):
        raise ValueError('A finished frontier does not need a budget extension')
    encoded = json.dumps(event, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
    digest = hashlib.sha256(encoded.encode()).hexdigest()
    for old in scan.get('budget_events', []):
        if old['event_id'] == event_id:
            if old['event_sha256'] != digest:
                raise ValueError('Event ID reused with different content')
            return copy.deepcopy(scan)
    expected = _integer(event.get('expected_revision'), 'expected_revision')
    if expected != revision:
        raise ValueError('Stale budget revision')
    after = _budget(event.get('new_limits'), 'new_limits')
    ceiling = _budget(hard_limits, 'hard_limits') if hard_limits is not None else None
    if any(after[key] < before[key] or after[key] < spent[key] for key in before):
        raise ValueError('Extension cannot reduce limits or consumed budget')
    if not any(after[key] > before[key] for key in before):
        raise ValueError('Extension must increase at least one limit')
    if ceiling and any(after[key] > ceiling[key] for key in after):
        raise ValueError('Extension exceeds explicit authorization limit')
    result = copy.deepcopy(scan)
    result['limits'] = after
    result['budget_revision'] = revision + 1
    result.setdefault('budget_events', []).append({
        'event_id': event_id, 'event_sha256': digest, 'event': copy.deepcopy(event),
        'limits_before': before, 'spent_before': spent, 'limits_after': after,
        'revision_before': revision, 'revision_after': revision + 1})
    return result
