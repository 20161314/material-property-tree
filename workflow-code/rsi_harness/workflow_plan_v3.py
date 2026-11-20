#!/usr/bin/env python3
"""Validate the v3 workflow and print bounded, unexecuted handoff plans as JSON.

This is a read-only planner. It neither runs step commands nor dispatches models.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config/rsi_workflow_v3.json"
ROUTING = ROOT / "config/rsi_model_routing_v1.json"
STATUSES = {"executable", "planned", "requires_model"}
STEP_FIELDS = {
    "id", "name", "phase", "summary", "actor", "model", "inputs", "actions",
    "outputs", "checks", "onFailure", "website", "command", "status", "route",
}
LIST_FIELDS = ("inputs", "actions", "outputs", "checks", "onFailure", "website")


def validate_workflow(config: dict, policy: dict) -> None:
    """Reject incomplete contracts and model routing drift before planning."""
    required = {"version", "title", "description", "phases", "steps", "links",
                "modelRoutes", "statusLegend", "executionPolicy", "principles", "invariants"}
    if not isinstance(config, dict) or not required <= config.keys():
        raise ValueError("Missing workflow top-level fields")
    for key in ("phases", "steps", "links", "modelRoutes", "statusLegend", "principles", "invariants"):
        if not isinstance(config[key], list) or not config[key]:
            raise ValueError("Expected nonempty array: " + key)
    for key in ("version", "title", "description"):
        if not isinstance(config[key], str) or not config[key].strip():
            raise ValueError("Expected text: " + key)
    phases = [phase.get("id") for phase in config["phases"]]
    if any(not isinstance(p, str) or not p for p in phases) or len(set(phases)) != len(phases):
        raise ValueError("Invalid or duplicate phases")
    legend = {item.get("id") for item in config["statusLegend"]}
    if legend != STATUSES:
        raise ValueError("Status legend must distinguish executable/planned/requires_model")
    expected = {"ordinary": ("gpt-6.1-sol", "high"), "bulk_review": ("gpt-6-luna", "max")}
    if (policy["default"]["model"], policy["default"]["reasoning_effort"]) != expected["ordinary"]:
        raise ValueError("Default model policy drift")
    if (policy["bulk_review"]["model"], policy["bulk_review"]["reasoning_effort"]) != expected["bulk_review"]:
        raise ValueError("Bulk review model policy drift")
    if policy["silent_model_fallback_allowed"] or policy["subagent_fork_turns"] != "none":
        raise ValueError("Routing must forbid silent fallback and use file handoffs")
    routes = {route.get("id"): route for route in config["modelRoutes"]}
    if len(routes) != len(config["modelRoutes"]) or set(routes) != set(expected):
        raise ValueError("Invalid model routes")
    for name, pair in expected.items():
        if (routes[name].get("model"), routes[name].get("reasoning_effort")) != pair:
            raise ValueError("Workflow model route drift: " + name)
    execution = config["executionPolicy"]
    if execution.get("batchSize") != {"min": 50, "default": 100, "max": 200}:
        raise ValueError("Batch bounds must be 50–200")
    if execution.get("maxAttempts") != 3 or execution.get("maxRetries") != 2 or execution.get("maxTasksPerPlan") != 8:
        raise ValueError("Retries and plans must be bounded")
    if execution.get("singleWriter") != "Release Merger" or execution.get("dispatchExecuted") is not False:
        raise ValueError("Single writer and unexecuted dispatch declaration required")
    ids = set()
    for step in config["steps"]:
        if not isinstance(step, dict) or not STEP_FIELDS <= step.keys():
            raise ValueError("Incomplete step contract")
        for field in STEP_FIELDS - set(LIST_FIELDS):
            if not isinstance(step[field], str) or not step[field].strip():
                raise ValueError("Expected step text: " + field)
        if step["id"] in ids:
            raise ValueError("Duplicate step: " + step["id"])
        ids.add(step["id"])
        if step["phase"] not in phases or step["status"] not in STATUSES:
            raise ValueError("Unknown phase or status: " + step["id"])
        for field in LIST_FIELDS:
            if not isinstance(step[field], list) or not step[field] or any(
                not isinstance(item, str) or not item.strip() for item in step[field]
            ):
                raise ValueError("Expected nonempty text array: " + field)
        if step["status"] == "requires_model":
            if step["route"] not in routes:
                raise ValueError("Model step needs a known route")
            route = routes[step["route"]]
            if step["model"] != route["model"] + "/" + route["reasoning_effort"]:
                raise ValueError("Step model mismatch: " + step["id"])
        elif step["route"] != "code" or step["model"] != "代码执行；监督 gpt-6.1-sol/high":
            raise ValueError("Code steps must not claim model execution")
    for step in config["steps"]:
        dependencies = step.get("dependsOn", [])
        if not isinstance(dependencies, list) or any(dep not in ids for dep in dependencies):
            raise ValueError("Unknown dependency: " + step["id"])
    # A stable topological order also rejects cycles and accidental forward dependencies.
    seen = set()
    for step in config["steps"]:
        if not set(step.get("dependsOn", [])) <= seen:
            raise ValueError("Steps must be in dependency order: " + step["id"])
        seen.add(step["id"])


def build_plan(config: dict, policy: dict, *, step_ids: list[str] | None = None,
               batch_size: int = 100, limit: int = 4, run_id: str = "preview",
               parent_release_id: str = "UNRESOLVED", config_sha256: str = "") -> dict:
    validate_workflow(config, policy)
    if not 50 <= batch_size <= 200:
        raise ValueError("batch-size must be between 50 and 200")
    if not 1 <= limit <= config["executionPolicy"]["maxTasksPerPlan"]:
        raise ValueError("limit must be between 1 and 8")
    if not run_id or any(c not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_" for c in run_id):
        raise ValueError("run-id may contain only ASCII letters, numbers, '-' and '_'")
    known = {step["id"] for step in config["steps"]}
    if step_ids and (len(set(step_ids)) != len(step_ids) or set(step_ids) - known):
        raise ValueError("Unknown or duplicate requested step")
    selected = [step for step in config["steps"] if not step_ids or step["id"] in step_ids]
    tasks = []
    for step in selected[:limit]:
        identity = json.dumps([config_sha256, parent_release_id, run_id, step["id"], batch_size], ensure_ascii=False)
        task_id = hashlib.sha256(identity.encode()).hexdigest()[:20]
        route = next((route for route in config["modelRoutes"] if route["id"] == step["route"]), None)
        tasks.append({
            "task_id": task_id, "step_id": step["id"], "name": step["name"],
            "implementation_status": step["status"], "execution_status": "NOT_EXECUTED",
            "actor": step["actor"], "route": route, "command_template": step["command"],
            "parent_release_id": parent_release_id, "run_id": run_id,
            "batch": {"capacity": batch_size, "records_assigned": 0, "partial_tail_allowed": True},
            "attempt": 0, "max_attempts": 3, "max_retries": 2, "timeout_seconds": 900,
            "depends_on": step.get("dependsOn", []),
            "inputs": step["inputs"], "required_input_pins": [],
            "handoff": {"directory_template": "candidates/{run_id}/{task_id}/",
                        "required_files": ["task.json", "input_manifest.json", "result.json", "review.json"],
                        "required_result_fields": ["parent_release_id", "epoch", "scan_id", "run_id", "route_id", "lease_id", "input_sha256", "candidate_sha256", "record_ids", "locators", "decisions", "attempt", "elapsed_seconds"],
                        "pin_status": "REQUIRES_INPUT_FREEZE", "collector_may_self_review": False},
            "dispatch_executed": False,
            "blocking_conditions": ["父快照和所有输入 SHA 必须冻结", "依赖步骤须有可验证回执", "有效 lease 与候选目录须由调度器领取"]
                                  + (["指定模型可用且实际调用回执存在；禁止静默替换"] if route else []),
        })
    return {"workflow_version": config["version"], "config_sha256": config_sha256,
            "mode": "PLAN_ONLY", "dispatch_executed": False, "commands_executed": False,
            "data_modified": False, "tasks": tasks, "remaining_step_ids": [s["id"] for s in selected[limit:]],
            "note": "容量为每个短任务上限；尚未分配记录、领取 lease、调用模型、合并或发布。"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=CONFIG)
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("--step", action="append", dest="step_ids")
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--limit", type=int, default=4)
    parser.add_argument("--run-id", default="preview")
    parser.add_argument("--parent-release-id", default="UNRESOLVED")
    args = parser.parse_args()
    try:
        raw = args.config.read_bytes()
        config = json.loads(raw)
        policy = json.loads(ROUTING.read_bytes())
        validate_workflow(config, policy)
        digest = hashlib.sha256(raw).hexdigest()
        if args.validate:
            result = {"valid": True, "workflow_version": config["version"], "steps": len(config["steps"]),
                      "config_sha256": digest, "dispatch_executed": False}
        else:
            result = build_plan(config, policy, step_ids=args.step_ids, batch_size=args.batch_size,
                                limit=args.limit, run_id=args.run_id,
                                parent_release_id=args.parent_release_id, config_sha256=digest)
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        parser.exit(2, "workflow plan error: " + str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
