"""Read-only lint before the one-time lock; never edits a frozen implementation."""

import subprocess
import sys

from agent_rd_admin_v1 import ROOT

command = [sys.executable, "-m", "ruff", "check", "src/curaloop_rd/agent_rd", "research/agent_rd_eval_v1",
           "api/agent_rd_routes.py", "api/main.py", "tests/test_agent_rd.py", "tests/test_agent_rd_eval.py"]
command += [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "tools").glob("agent_rd_*.py"))]
result = subprocess.run(command, cwd=ROOT)
if result.returncode:
    raise SystemExit(result.returncode)
raise SystemExit(subprocess.run([sys.executable, "tools/agent_rd_freeze_v1.py"], cwd=ROOT).returncode)
