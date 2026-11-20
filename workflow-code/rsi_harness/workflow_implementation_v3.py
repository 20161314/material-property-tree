"""Bind workflow documentation to real code entry points; emit, never execute."""
from copy import deepcopy
import json


def bind_implementation(config):
    config = deepcopy(config)
    config.update(version="3.1.0-2026-11-20", description="程序环节已实现；模型环节已接入固定批次交接。实现状态与实际执行结果分开记录。")
    commands = {
        "F0-freeze": "freeze --run {RUN_DIR} --bundle {BUNDLE_JSON} --run-id {RUN_ID} --parent-release-id {PARENT_RELEASE}",
        "F1-enumerate": "enumerate --run {RUN_DIR} --records {SOURCE_MANIFEST} --out {REPORT_DIR}/source_identities.json",
        "F2-dedup": "dedup --run {RUN_DIR} --records {SOURCE_MANIFEST} --aliases {REVIEWED_ALIASES} --out {REPORT_DIR}/geometry_audit.json",
        "F5-bfs": "bfs --run {RUN_DIR} --kind material --limit 100 --out {REPORT_DIR}/material_frontier.json",
        "F7-merge": "merge --run {RUN_DIR} --task {REVIEWED_TASK_ID} --actor {MERGER_ID} --expected-parent {PARENT_RELEASE}",
        "F7-state": "state --run {RUN_DIR} --out {REPORT_DIR}/material_states.json",
        "F7-reconcile": "reconcile --run {RUN_DIR} --out {REPORT_DIR}/reconciliation.json",
        "F9-frontier": "checkpoint --run {RUN_DIR} --out {REPORT_DIR}/checkpoint.json",
    }
    site_commands = {
        "F8-build": "build-site --source-site {APPROVED_SITE} --out-site {NEW_SITE} --workflow-config config/rsi_workflow_v3.json",
        "F8-browser": "browser-check --site {NEW_SITE} --report-dir {NEW_BROWSER_REPORT_DIR}",
        "F8-publish": "publish-site --site {NEW_SITE} --approval {APPROVAL_JSON} --approval-sha256 {APPROVAL_SHA} --browser-receipt {BROWSER_RECEIPT} --expected-remote-parent {REMOTE_PARENT} --publisher {NEW_PUBLICATION_DIR}/publish_reviewed_export.py --execute",
    }
    for step in config["steps"]:
        if step["status"] == "planned":
            step["status"] = "executable"
        if step["id"] in commands:
            step["command"] = "python3 rsi_harness/workflow_run_v3.py " + commands[step["id"]]
        if step["id"] in site_commands:
            step["command"] = "python3.12 rsi_harness/workflow_publication_v3.py " + site_commands[step["id"]]
        if step["id"] == "F8-build":
            step["command"] = "python3 rsi_harness/workflow_projection_v3.py --source-site {APPROVED_SITE} --out-site {NEW_SITE} --bundle {MERGED_EXPORT_JSON} --release-id {MERGED_RELEASE_ID} --workflow-config config/rsi_workflow_v3.json\n仅更新页面而不变更数据时，使用 workflow_publication_v3.py build-site。"
        if step["route"] != "code":
            step["command"] = ("python3 rsi_harness/workflow_run_v3.py batch --run {RUN_DIR} --step " + step["id"] + " --route " + step["route"] + " --records {PINNED_RECORDS_JSON} --collector {COLLECTOR_ID}\n"
                               "python3 rsi_harness/workflow_run_v3.py claim --run {RUN_DIR} --owner {WORKER_ID} --out {HANDOFF_JSON}\n"
                               "宿主按交接文件调用指定模型；记录真实调用回执后执行 dispatch / submit。")
            step["implementation"] = "implemented_host_handoff"
        else:
            step["implementation"] = "implemented_code"
        step["executionStatus"] = "本轮尚未运行；以执行回执为准"
        check = "输入、输出与实际执行回执分别保存；实现完成不代表当前数据审核完成。"
        if check not in step["checks"]:
            step["checks"].append(check)
        if step["id"] == "P0-plan":
            step["summary"] = "验证工作流规则与模型分工，生成有界短任务；计划与执行分开。"
        if step["id"] == "F0-freeze":
            step["actions"][1] = "固定标准化六表数据包、来源清单、模型路由与用户规则；数据包包含对象、部件、材料、关系、分类和证据。旧五核心输入仍由原发布门禁独立核验。"
            step["outputs"][0] = "不可变输入清单、隔离运行数据库、冻结来源登记"
        if step["id"] == "F2-dedup":
            step["actions"][0] = "按冻结SHA核验已有载荷；需要下载时使用有大小限制的HTTPS下载器，拒绝HTML/XML错误页。"
        if step["id"] == "F5-bfs":
            step["actions"][1] = "按树层逐层排序；同层先补S3，再查S2，再增强S1及探索S4；物体扩展仅领取S1/S2。"
            step["actions"][2] = "每批50–200条；按材料状态修订号保存前沿与完成位置，重复领取不清零进度。"
        if step["id"] == "F7-state":
            step["summary"] = "三项各有来源值与是否有关联物体决定四类状态；完整组另计。"
            step["actions"][0] = "按material_id分别汇总E、ν、ρ的批准来源值，三项可以来自不同文献。"
            step["actions"][1] = "S1三项有值且有物体；S2三项有值但无物体；S3缺项且有物体；S4缺项且无物体。"
        if step["id"] == "F8-browser":
            step["summary"] = "真实浏览器自动检查四页、两种屏宽、导航、载入错误和横向溢出。"
        if step["id"] == "F9-frontier":
            step["actor"] = "推进代理；代码调度"
        if step["id"] == "F8-preflight":
            rule = "全面完成版运行原双门禁；研究快照走已有独立批准的快照合同，保留未完成标志，不伪造全面完成。"
            if rule not in step["actions"]:
                step["actions"].append(rule)
    for item in config["principles"]:
        if item["id"] == "code":
            item["description"] = "解析、去重、计数、逐层任务、事务和发布核验均由代码处理。"
    for item in config["statusLegend"]:
        if item["id"] == "executable":
            item.update(name="程序已实现", description="已有可运行入口和测试；是否在当前数据上完成，以本轮执行回执为准。")
        elif item["id"] == "requires_model":
            item.update(name="模型已接入", description="分批、输入绑定、指定模型交接和回执校验已实现；实际调用由宿主执行。")
        else:
            item.update(name="尚未实现", description="仅用于未来新增环节；当前工作流没有此类步骤。")
    config["executionPolicy"]["runtime"] = "rsi_harness/workflow_run_v3.py"
    config["executionPolicy"]["taskStatuses"] = ["READY", "LEASED", "REVIEWED", "MERGED", "RETRY", "COOLDOWN", "STALE"]
    config["implementationFiles"] = ["workflow_run_v3.py", "workflow_runtime_v3.py", "workflow_data_v3.py", "workflow_sources_v3.py", "workflow_publication_v3.py", "workflow_inventory_v3.py", "workflow_projection_v3.py"]
    invariant = "三项分别有来源值即满足四态的属性条件；同一来源完整组另计，不跨文献拼组。"
    if invariant not in config["invariants"]:
        config["invariants"].append(invariant)
    return config


if __name__ == "__main__":
    from workflow_plan_v3 import CONFIG
    print(json.dumps(bind_implementation(json.loads(CONFIG.read_text())), ensure_ascii=False, indent=2))
