#!/usr/bin/env python3
"""Run all v3 implementation suites and emit one reproducible code receipt."""
import contextlib
import io
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "rsi_harness"))
from workflow_plan_v3 import CONFIG, ROUTING, validate_workflow
from workflow_runtime_v3 import file_sha


def verify():
    config = json.loads(CONFIG.read_text())
    validate_workflow(config, json.loads(ROUTING.read_text()))
    planned = [s["id"] for s in config["steps"] if s["status"] == "planned"]
    missing = [name for name in config["implementationFiles"] if not (ROOT / "rsi_harness" / name).is_file()]
    suite = unittest.TestSuite()
    for directory in (ROOT / "rsi_harness/tests", ROOT / "tests"):
        if directory.is_dir():
            suite.addTests(unittest.TestLoader().discover(str(directory), pattern="*workflow*v3.py"))
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output, verbosity=1).run(suite)
    files = [CONFIG, ROUTING, *sorted((ROOT / "rsi_harness").glob("workflow*_v3.py")), ROOT / "rsi_harness/WORKFLOW_EXECUTION_V3.md"]
    files += list((ROOT / "rsi_harness/tests").glob("*workflow*v3.py"))
    files += list((ROOT / "tests").glob("*workflow*v3.py"))
    return {"schema": "rsi-workflow-implementation-verification-v3", "status": "PASS" if result.wasSuccessful() and not planned and not missing else "FAIL",
            "workflow_version": config["version"], "steps": len(config["steps"]), "not_implemented_steps": planned,
            "missing_implementation_files": missing, "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
            "test_log": output.getvalue(), "inputs": {str(p.relative_to(ROOT)): file_sha(p) for p in sorted(files)},
            "actual_scientific_model_review_executed": False, "production_tables_modified": False}


if __name__ == "__main__":
    receipt = verify()
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    raise SystemExit(0 if receipt["status"] == "PASS" else 1)
