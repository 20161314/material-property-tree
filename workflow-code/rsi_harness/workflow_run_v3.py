#!/usr/bin/env python3
"""Execute isolated RSI workflow stages. Semantic decisions remain model tasks."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from workflow_plan_v3 import CONFIG, ROUTING, validate_workflow
from workflow_runtime_v3 import Run, freeze, file_sha

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def emit(value, path=None):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n"
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8") as handle:
            handle.write(raw)
    else:
        print(raw, end="")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("freeze", help="freeze an explicit normalized bundle and policy inputs")
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--bundle", type=Path, required=True)
    p.add_argument("--run-id", required=True)
    p.add_argument("--parent-release-id", required=True)
    p.add_argument("--input", action="append", default=[], help="name=project-relative-path")
    p.add_argument("--max-task-attempts", type=int, default=100)
    p.add_argument("--max-seconds", type=int, default=3600)
    for command in ("status", "verify-inputs", "checkpoint", "enumerate", "dedup", "components", "payload", "validate", "state", "bfs", "reconcile", "batch", "claim", "dispatch", "candidate", "review-batch", "submit", "finish", "recover", "merge", "export"):
        p = sub.add_parser(command)
        p.add_argument("--run", type=Path, required=True)
        p.add_argument("--out", type=Path)
        if command in {"enumerate", "dedup", "components", "batch"}:
            p.add_argument("--records", type=Path, required=True)
        if command in {"enumerate", "dedup"}:
            p.add_argument("--field-map", type=Path)
        if command == "payload":
            p.add_argument("--file", type=Path, required=True)
            p.add_argument("--sha256", required=True)
            p.add_argument("--format", choices=("glb", "zip"))
        if command == "dedup":
            p.add_argument("--aliases", type=Path)
        if command == "bfs":
            p.add_argument("--kind", choices=("material", "object"), default="material")
            p.add_argument("--limit", type=int, default=100)
            p.add_argument("--visited", type=Path)
            p.add_argument("--complete", type=Path, help="explicit [material_id, revision] pairs")
        if command == "batch":
            p.add_argument("--step", required=True)
            p.add_argument("--collector", required=True)
            p.add_argument("--batch-size", type=int, default=100)
            p.add_argument("--route", choices=("ordinary", "bulk_review"), default="bulk_review")
        if command == "claim":
            p.add_argument("--owner", required=True)
        if command in {"dispatch", "submit", "candidate"}:
            p.add_argument("--task", required=True)
            p.add_argument("--token", required=True)
            p.add_argument("--receipt", type=Path, required=True)
        if command == "review-batch":
            p.add_argument("--task", required=True)
            p.add_argument("--step", required=True)
        if command == "finish":
            p.add_argument("--task", required=True)
            p.add_argument("--token", required=True)
            p.add_argument("--outcome", choices=("RETRY", "NO_PROGRESS", "REJECTED"), required=True)
            p.add_argument("--reason", required=True)
        if command == "recover":
            p.add_argument("--task", required=True)
            p.add_argument("--actor", required=True)
            p.add_argument("--reason", required=True)
        if command == "merge":
            p.add_argument("--task", action="append", required=True)
            p.add_argument("--actor", required=True)
            p.add_argument("--expected-parent", required=True)
    args = parser.parse_args(argv)
    run = None
    try:
        config = read(CONFIG)
        validate_workflow(config, read(ROUTING))
        if args.command == "freeze":
            pins = {"workflow": CONFIG, "routing": ROUTING, "bundle": args.bundle,
                    "user_policy": ROOT / "rsi_harness/RSI_CURRENT_USER_OVERRIDES_2026_11_15.md",
                    "website_policy": ROOT / "rsi_harness/WEBSITE_CONTENT_POLICY.md"}
            for value in args.input:
                name, path = value.split("=", 1)
                if name in pins:
                    raise ValueError("Duplicate input name")
                pins[name] = ROOT / path
            run = freeze(args.run, project_root=ROOT, run_id=args.run_id, parent_release_id=args.parent_release_id,
                         inputs=pins, workflow=config, bundle=read(args.bundle), max_task_attempts=args.max_task_attempts,
                         max_seconds=args.max_seconds)
            result = run.verify_inputs()
        else:
            from workflow_data_v3 import enumerate_sources, deduplicate, validate_bundle, recompute, bfs_tasks, reconcile
            from workflow_sources_v3 import read_records, component_records, verify_payload
            run = Run(args.run)
            run.verify_inputs()
            for name in ("records", "aliases", "field_map"):
                path = getattr(args, name, None)
                if path is not None:
                    run.verify_path(path)
            if args.command in {"status", "checkpoint"}:
                result = run.checkpoint()
            elif args.command == "verify-inputs":
                result = run.verify_inputs()
            elif args.command == "enumerate":
                result = run.record_step("F1-enumerate", enumerate_sources(read_records(args.records, read(args.field_map) if args.field_map else None)))
            elif args.command == "dedup":
                result = run.record_step("F2-dedup", deduplicate(read_records(args.records, read(args.field_map) if args.field_map else None), read(args.aliases) if args.aliases else ()))
            elif args.command == "components":
                result = run.record_step("F3-components-structure", component_records(read(args.records)))
            elif args.command == "payload":
                result = run.record_step("F2-payload-" + args.sha256, verify_payload(args.file, args.sha256, args.format))
            elif args.command == "validate":
                result = run.record_step("bundle-validation", validate_bundle(run.bundle()))
            elif args.command == "state":
                result = run.record_step("F7-state-" + run.meta("current_release"), recompute(run.bundle()))
            elif args.command == "bfs":
                if args.visited:
                    raise ValueError("Use persisted frontier revisions; external visited lists cannot reset progress")
                result = run.frontier(kind=args.kind, limit=args.limit, complete=read(args.complete) if args.complete else ())
            elif args.command == "reconcile":
                result = reconcile(run.bundle(run.meta("parent_release")), run.bundle())
            elif args.command == "batch":
                result = run.enqueue(args.step, read(args.records), args.collector, args.batch_size, args.route)
            elif args.command == "claim":
                result = run.claim(args.owner)
            elif args.command == "dispatch":
                result = run.record_dispatch(args.task, args.token, read(args.receipt))
            elif args.command == "submit":
                result = run.submit_review(args.task, args.token, read(args.receipt))
            elif args.command == "candidate":
                result = run.submit_candidate(args.task, args.token, read(args.receipt))
            elif args.command == "review-batch":
                result = run.enqueue_review(args.task, args.step)
            elif args.command == "finish":
                result = run.finish_failure(args.task, args.token, args.outcome, args.reason)
            elif args.command == "recover":
                result = run.recover(args.task, args.reason, actor=args.actor)
            elif args.command == "merge":
                result = run.merge(args.task, actor=args.actor, expected_parent=args.expected_parent)
            elif args.command == "export":
                result = {"release_id": run.meta("current_release"), "bundle": run.bundle(), "checkpoint": run.checkpoint()}
            else:
                raise ValueError("Unsupported operation")
        emit(result, getattr(args, "out", None))
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(2, "workflow execution error: " + str(exc) + "\n")
    finally:
        if run:
            run.close()


if __name__ == "__main__":
    main()
