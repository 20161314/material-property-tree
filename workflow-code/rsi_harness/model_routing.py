"""Resolve RSI model dispatch arguments; does not invoke models or modify facts."""
import argparse
import hashlib
import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[1] / 'config/rsi_model_routing_v1.json'


def resolve_route(task_kind='ordinary', *, escalate=False, available_models=None):
    policy_bytes = POLICY_PATH.read_bytes()
    policy = json.loads(policy_bytes)
    if task_kind != 'bulk_review' and task_kind not in policy['ordinary_tasks']:
        raise ValueError('Unknown task kind: ' + task_kind)
    selected = policy['bulk_review'] if task_kind == 'bulk_review' and not escalate else policy['default']
    if available_models is not None and selected['model'] not in available_models:
        raise ValueError('Requested model unavailable; do not silently substitute: ' + selected['model'])
    return {
        'policy_id': policy['policy_id'],
        'policy_sha256': hashlib.sha256(policy_bytes).hexdigest(),
        'task_kind': task_kind,
        'escalated_to_default': bool(escalate),
        'model': selected['model'],
        'reasoning_effort': selected['reasoning_effort'],
        'fork_turns': policy['subagent_fork_turns'],
        'subagent_write_scope': policy['subagent_write_scope'],
        'silent_model_fallback_allowed': policy['silent_model_fallback_allowed'],
        'dispatch_executed': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', default='ordinary')
    parser.add_argument('--escalate', action='store_true', help='Send an ambiguous batch item to the Sol default')
    parser.add_argument('--available-model', action='append', dest='available_models')
    args = parser.parse_args()
    print(json.dumps(resolve_route(args.task, escalate=args.escalate, available_models=args.available_models), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
