"""Wait for the fixed evaluator to end, then build only audited actual reports.

Runs inside the already reserved local Job. The optional current-product smoke
mission uses only headroom in the unchanged remote envelope after study exit.
No scientific changes, remote cleanup, account closure or publication occur.
Every step preserves failures and refuses existing one-time output paths.
"""

import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
BUNDLED = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    run_id = sys.argv[1] if len(sys.argv) == 2 else "v1"
    assert run_id and all(c.isalnum() or c == "-" for c in run_id)
    work = TASK / ("postrun-documents-" + run_id)
    work.mkdir(exist_ok=False)
    deadline = datetime.fromisoformat(read(TASK / "release.json")["deadline_utc"])
    progress = PUBLIC / "locked-progress-v1.json"
    print("Waiting inside the same local Job for the evaluator's final disposition; no inferred results", flush=True)
    while not progress.exists():
        assert datetime.now(timezone.utc) < deadline
        time.sleep(5)
    final = read(progress)
    assert final["status"] in ("COMPLETE", "INCOMPLETE") and final["stop_reason"] != "OPERATIONAL_BATCH_BOUNDARY"
    time.sleep(2)
    commands = [
        [sys.executable, "tools/agent_rd_recovery_preflight_v1.py", "postrun-v1"],
        [sys.executable, "tools/agent_rd_analyze_v1.py"],
        [sys.executable, "tools/agent_rd_descriptive_report_v1.py"],
        [sys.executable, "tools/agent_rd_verify_results_v1.py", "--write-receipt"],
        [sys.executable, "tools/agent_rd_product_checks_v1.py", "v1"],
        [sys.executable, "tools/agent_rd_product_real_model_v1.py"],
        [str(BUNDLED), "tools/agent_rd_documents_v1.py", "manual-v2"],
        [str(BUNDLED), "tools/agent_rd_documents_v1.py", "render-manual-v2"],
        [str(BUNDLED), "tools/agent_rd_result_figures_v1.py"],
        [str(BUNDLED), "tools/agent_rd_preview_reproduction_v1.py"],
        [str(BUNDLED), "tools/agent_rd_documents_v1.py", "manuscript"],
        [str(BUNDLED), "tools/agent_rd_documents_v1.py", "render-manuscript"],
    ]
    steps = []
    for index, command in enumerate(commands):
        freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
        assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in freeze["pins"].items())
        snapshots = work / f"step-{index}-sources"
        snapshots.mkdir()
        source_pins = {}
        for path in sorted((ROOT / "tools").glob("agent_rd_*.py")):
            (snapshots / path.name).write_bytes(path.read_bytes())
            source_pins[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        (snapshots / "source-pins.json").write_text(json.dumps(source_pins, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"stage": "STARTING_ACTUAL_POSTRUN_DOCUMENT_STEP", "index": index, "command": command}), flush=True)
        with (work / f"step-{index}.stdout.txt").open("xb") as out, (work / f"step-{index}.stderr.txt").open("xb") as err:
            result = subprocess.run(command, cwd=ROOT, stdout=out, stderr=err)
        steps.append({"command": command, "exit_code": result.returncode})
        (work / "progress.json").write_text(json.dumps({"steps": steps, "actual_matrix_status": final["status"]}, indent=2) + "\n", encoding="utf-8")
        if result.returncode:
            print((work / f"step-{index}.stderr.txt").read_text(encoding="utf-8", errors="replace")[-2500:])
            raise SystemExit(result.returncode)
    (work / "completion.json").write_text(json.dumps({"status": "ACTUAL_ANALYSIS_AND_REPORT_RENDERED_AWAITING_AUTHOR_VISUAL_REVIEW",
          "steps": steps, "manuscript_submitted": False, "remote_cleanup": "NOT_RUN", "ledger_closed": False}, indent=2) + "\n", encoding="utf-8")
    print("Actual report pipeline complete; rendered pages/figures still need visual review, return and closeout", flush=True)


if __name__ == "__main__":
    main()
