"""One local Windows Job for evaluation orchestration and bounded document work.

This is an internal operator queue, not an agent tool or network endpoint.
Every child inherits the parent's same one-core/1GiB aggregate Job limits.
"""

import json
import subprocess
import sys
import time

from agent_rd_admin_v1 import ROOT, TASK, read, write

WORK = TASK / "supervisor-v1"
BUNDLED = "C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"
NODE = "C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe"
MARKER = "C:/Users/User/.codex/plugins/cache/openai-primary-runtime/pdf/26.1104.22356/skills/pdf/container_tools/mark_artifact_operation_started.mjs"
COMMANDS = {
    "pdf-marker": [NODE, MARKER, "--operation-kind", "create", "--expected-output-count", "2", "--output-format", "pdf"],
    "manual": [BUNDLED, "tools/agent_rd_documents_v1.py", "manual"],
    "manual-render": [BUNDLED, "tools/agent_rd_documents_v1.py", "render-manual"],
    "visual-spec-check": [sys.executable, "tools/agent_rd_visual_spec_v1.py"],
}


def main():
    WORK.mkdir(exist_ok=False)
    (WORK / "inbox").mkdir()
    (WORK / "receipts").mkdir()
    out = (WORK / "evaluation.stdout.txt").open("wb")
    err = (WORK / "evaluation.stderr.txt").open("wb")
    evaluator = subprocess.Popen([sys.executable, "tools/agent_rd_evaluate_v1.py"], cwd=ROOT, stdout=out, stderr=err)
    helper = None
    request = None
    heartbeat = 0
    progress = {}
    while True:
        if helper is not None and helper.poll() is not None:
            receipt = {"request_id": request["request_id"], "task": request["task"], "exit_code": helper.returncode,
                       "scope": "Child of the same aggregate-limited local Job; no extra CPU or memory allowance"}
            write(WORK / "receipts" / (request["request_id"] + ".json"), receipt, True)
            print(json.dumps(receipt), flush=True)
            helper, request = None, None
        pending = sorted(p for p in (WORK / "inbox").glob("*.json") if not (WORK / "receipts" / p.name).exists())
        if helper is None and pending:
            request = read(pending[0])
            assert set(request) == {"request_id", "task"} and request["request_id"] == pending[0].stem
            assert request["task"] in COMMANDS
            name = request["request_id"]
            stdout = (WORK / (name + ".stdout.txt")).open("xb")
            stderr = (WORK / (name + ".stderr.txt")).open("xb")
            helper = subprocess.Popen(COMMANDS[request["task"]], cwd=ROOT, stdout=stdout, stderr=stderr)
        if evaluator.poll() is not None and helper is None and not pending:
            break
        if time.monotonic() >= heartbeat:
            progress_path = TASK / "locked-evaluation-v1/progress.json"
            try:
                progress = read(progress_path) if progress_path.exists() else progress
            except (OSError, ValueError):
                pass  # A concurrent progress-file write must not interrupt model work.
            print(json.dumps({"status": "SUPERVISING_SAME_LOCAL_JOB", "evaluation_process_running": evaluator.poll() is None,
                              "completed_units": progress.get("completed", 0), "planned_units": 408,
                              "document_task": request["task"] if request else None}), flush=True)
            heartbeat = time.monotonic() + 60
        time.sleep(1)
    write(WORK / "completion.json", {"evaluation_exit_code": evaluator.returncode, "scientific_disposition": "Read locked-progress-v1.json; process completion is not task or scientific success"}, True)
    raise SystemExit(evaluator.returncode)


if __name__ == "__main__":
    main()
