"""Read current route permissions without admitting any source records."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def pinned_file(entry):
    path = (ROOT / entry['path']).resolve()
    if not path.is_relative_to(ROOT) or not path.is_file():
        raise ValueError('Route reference must be a project file')
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Route reference hash differs from the active pointer')
    return path


def lookup(route_id):
    pointer = json.loads((ROOT / 'data/current_site_snapshot.json').read_text())
    refs = pointer['current_evidence_routes']
    policy = json.loads(pinned_file(refs['policy']).read_text())
    with pinned_file(refs['routes']).open(encoding='utf-8-sig', newline='') as handle:
        routes = {row['route_id']: row for row in csv.DictReader(handle)}
    if set(routes) != set(policy['routes']):
        raise ValueError('Route table and policy identifiers differ')
    if route_id not in routes:
        raise ValueError('Unknown route: ' + route_id)
    kind = policy['routes'][route_id]
    return {
        'route_id': route_id,
        'route_class': kind,
        'source': routes[route_id],
        'permissions': policy['route_classes'][kind],
        'numerical_exclusions': policy['numerical_exclusions'],
        'source_rows_admitted': 0,
        'meaning': 'Route guidance only; actual records still require source review.',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--route', required=True)
    args = parser.parse_args()
    print(json.dumps(lookup(args.route), ensure_ascii=False, sort_keys=True, indent=2))
