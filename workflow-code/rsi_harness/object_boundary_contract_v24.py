"""Validate an explicit source-object boundary review without inferring visual facts.

This structural gate supplements source UID and material-scope review. Passing
it does not verify the reviewer’s observations, global geometry uniqueness, or
internal mechanical decomposition. The immutable source and visual locators
still require independent review before admission.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ACCEPTED_BOUNDARIES = {
    'SINGLE_PRIMARY_OBJECT',
    'SINGLE_PRIMARY_OBJECT_WITH_PACKAGING',
    'SINGLE_PRIMARY_OBJECT_WITH_DISPLAY_BACKGROUND',
    'SINGLE_PRIMARY_OBJECT_WITH_HOLDER_PROP',
    'SINGLE_FUNCTIONAL_ASSEMBLY',
    'SINGLE_FUNCTIONAL_ASSEMBLY_WITH_SCALE_PROP',
    'SINGLE_DECORATIVE_ASSEMBLY',
}
ACCEPTED_DECISIONS = {
    'APPROVE', 'PASS', 'APPROVE_SOURCE_IDENTITY',
    'APPROVE_SOURCE_IDENTITY_SCOPED_MATERIAL', 'PASS_BOUNDARY_REVIEW',
}
MISSING_LOCATOR_TOKENS = {'none', 'null', 'n/a', 'na', '-'}

REQUIRED = {
    'source_uid', 'boundary_class', 'primary_object_count',
    'source_metadata_locator', 'visual_locator', 'excluded_scope',
    'geometry_membership_verified', 'decision',
}

def text_field(value) -> str:
    return value.strip() if isinstance(value, str) else ''

def locator_present(value) -> bool:
    value = text_field(value)
    return bool(value) and value.lower() not in MISSING_LOCATOR_TOKENS

def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle))

def audit_boundaries(approved: list[dict], reviews: list[dict]) -> dict:
    errors = []
    approved_ids = [text_field(row.get('source_uid')) for row in approved]
    if not approved_ids or any(not uid for uid in approved_ids):
        errors.append('APPROVED_UIDS_MISSING')
    if len(set(approved_ids)) != len(approved_ids):
        errors.append('APPROVED_UID_DUPLICATE')
    indexed = {}
    for row in reviews:
        uid = text_field(row.get('source_uid'))
        if not uid or uid in indexed:
            errors.append('BOUNDARY_UID_MISSING_OR_DUPLICATE:' + uid)
        indexed[uid] = row
    for uid in approved_ids:
        row = indexed.get(uid)
        if row is None:
            errors.append('NO_BOUNDARY_REVIEW:' + uid)
            continue
        missing = sorted(key for key in REQUIRED if not text_field(row.get(key)))
        for locator in ('source_metadata_locator', 'visual_locator'):
            if locator not in missing and not locator_present(row.get(locator)):
                missing.append(locator)
        missing.sort()
        if missing:
            errors.append('BOUNDARY_FIELDS_MISSING:' + uid + ':' + ','.join(missing))
        if row.get('boundary_class') not in ACCEPTED_BOUNDARIES:
            errors.append('BOUNDARY_NOT_SINGLE_OBJECT_OR_ASSEMBLY:' + uid)
        if str(row.get('primary_object_count', '')) != '1':
            errors.append('PRIMARY_COUNT_NOT_ONE:' + uid)
        decision = text_field(row.get('decision')).upper()
        if decision not in ACCEPTED_DECISIONS:
            errors.append('BOUNDARY_NOT_APPROVED:' + uid)
        membership = str(row.get('geometry_membership_verified', '')).lower()
        if membership not in {'true', 'false'}:
            errors.append('GEOMETRY_MEMBERSHIP_FLAG_INVALID:' + uid)
        elif membership == 'true' and not locator_present(row.get('geometry_membership_evidence_locator')):
            errors.append('GEOMETRY_MEMBERSHIP_UNSUPPORTED:' + uid)
    return {
        'status': 'PASS_BOUNDARY_REVIEW_STRUCTURE_ONLY' if not errors else 'FAIL_BOUNDARY_REVIEW_STRUCTURE',
        'approved_objects': len(approved_ids),
        'review_rows': len(reviews),
        'errors': errors,
        'independent_visual_review_required': True,
        'global_geometry_deduplication_proved': False,
        'authored_mechanical_components_added': 0,
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--approved', type=Path, required=True)
    parser.add_argument('--boundaries', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = audit_boundaries(read_rows(args.approved), read_rows(args.boundaries))
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end='')
    return bool(result['errors'])

if __name__ == '__main__':
    raise SystemExit(main())
