"""Explicit operator document tasks inside the existing local resource Job.

This module is not a model tool. It cannot launch inference, alter scientific
pins or accept arbitrary commands. Executed authoring sources are snapshotted.
"""

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
REQUEST = TASK / "document-next-action-v1.json"
BUNDLED = Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe"


def main():
    request = json.loads(REQUEST.read_text(encoding="utf-8"))
    assert set(request) == {"action", "request_id"}
    identity = request["request_id"]
    assert isinstance(identity, str) and identity and all(c.isalnum() or c == "-" for c in identity)
    reporting = ["tools/agent_rd_document_dispatch_v1.py", "tools/agent_rd_descriptive_report_v1.py",
                 "tools/agent_rd_result_figures_v1.py", "tools/agent_rd_manuscript_v1.py", "tools/agent_rd_return_remote_program_v1.py",
                 "tools/agent_rd_return_v1.py", "tools/agent_rd_verify_results_v1.py", "tools/agent_rd_postrun_documents_v1.py"]
    commands = {
        "check-reporting": [[sys.executable, "-m", "ruff", "check", *reporting],
                            [sys.executable, "-m", "py_compile", *reporting]],
        "analyze": [[sys.executable, "tools/agent_rd_analyze_v1.py"],
                    [sys.executable, "tools/agent_rd_descriptive_report_v1.py"]],
        "result-figures": [[str(BUNDLED), "tools/agent_rd_result_figures_v1.py"]],
        "manuscript": [[str(BUNDLED), "tools/agent_rd_documents_v1.py", "manuscript"]],
        "render-manuscript": [[str(BUNDLED), "tools/agent_rd_documents_v1.py", "render-manuscript"]],
        "wait-and-report": [[sys.executable, "tools/agent_rd_postrun_documents_v1.py"]],
    }
    assert request["action"] in commands
    freeze = json.loads((ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json").read_text())
    assert all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in freeze["pins"].items())
    destination = TASK / "document-actions-v1" / identity
    destination.mkdir(parents=True, exist_ok=False)
    os.replace(REQUEST, destination / "request.json")
    source_paths = {"tools/agent_rd_document_dispatch_v1.py", "tools/agent_rd_visual_spec_v1.py"}
    source_paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "tools").glob("agent_rd_*.py"))
    for command in commands[request["action"]]:
        source_paths.update(s for s in command if s.endswith(".py"))
    hashes = {}
    for name in sorted(source_paths):
        path = ROOT / name
        assert path.is_file()
        copy = destination / "sources" / name
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_bytes(path.read_bytes())
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    result_rows = []
    for index, command in enumerate(commands[request["action"]]):
        completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        (destination / f"step-{index}.stdout.txt").write_text(completed.stdout, encoding="utf-8")
        (destination / f"step-{index}.stderr.txt").write_text(completed.stderr, encoding="utf-8")
        result_rows.append({"command": command, "exit_code": completed.returncode})
        print(completed.stdout[-1800:])
        if completed.returncode:
            print(completed.stderr[-1800:])
            break
    receipt = {"request": request, "utc": datetime.now(timezone.utc).isoformat(),
               "status": "PASS" if all(r["exit_code"] == 0 for r in result_rows) else "FAIL",
               "steps": result_rows, "executed_source_sha256": hashes,
               "resource_scope": "All children inherit the existing one-core/1GiB supervisor Job; no new allowance",
               "model_inference": False, "scientific_protocol_changed": False}
    (destination / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt))
    raise SystemExit(0 if receipt["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
