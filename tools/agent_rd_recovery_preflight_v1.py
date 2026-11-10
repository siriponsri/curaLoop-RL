"""Check only unfrozen recovery/reporting helpers; no model or score change."""

import json
import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, read, sha, write

paths = ["tools/agent_rd_descriptive_report_v1.py", "tools/agent_rd_document_dispatch_v1.py",
         "tools/agent_rd_manuscript_v1.py", "tools/agent_rd_postrun_documents_v1.py", "tools/agent_rd_result_figures_v1.py",
         "tools/agent_rd_return_remote_program_v1.py", "tools/agent_rd_return_v1.py", "tools/agent_rd_verify_results_v1.py",
         "tools/agent_rd_closeout_v1.py", "tools/agent_rd_ssh_recovery_v1.py", "tools/agent_rd_supervisor_recovery_v1.py",
         "tools/agent_rd_recovery_preflight_v1.py", "tools/agent_rd_owner_resume_v1.py",
         "tools/agent_rd_supervisor_host_resume_v1.py"]
freeze = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
checks = []
for command in ([sys.executable, "-m", "ruff", "check", *paths], [sys.executable, "-m", "py_compile", *paths]):
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    checks.append({"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        break
value = {"status": "PASS" if all(c["exit_code"] == 0 for c in checks) else "FAIL", "checks": checks,
         "source_pins": {p: sha(ROOT / p) for p in paths}, "frozen_27_pins_preserved": True,
         "new_model_calls": 0, "phase_or_deadline_reset": False}
write(PUBLIC / ("recovery-preflight-" + sys.argv[1] + ".json"), value, True)
print(json.dumps({"status": value["status"]}))
raise SystemExit(0 if value["status"] == "PASS" else 1)
