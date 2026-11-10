"""Local frontend checks under the current single-core resource job."""

import os
import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, write

tag = sys.argv[1]
rows = []
for script in ("typecheck", "lint", "test", "build"):
    command = ["npm.cmd", "run", script] + (["--", "--maxWorkers=1", "--no-file-parallelism"] if script == "test" else [])
    result = subprocess.run(command, cwd=ROOT / "frontend", env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=512"}, capture_output=True, text=True, encoding="utf-8")
    rows.append({"script": script, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    print(script + " exit=" + str(result.returncode))
    print(result.stdout[-2000:])
    if result.returncode:
        print(result.stderr[-2200:])
        break
write(PUBLIC / ("frontend-checks-" + tag + ".json"), {"status": "PASS" if all(r["exit_code"] == 0 for r in rows) else "FAIL", "checks": rows}, True)
raise SystemExit(rows[-1]["exit_code"])
