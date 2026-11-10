"""Reproduce the one legacy asynchronous route failure under the same limits."""

import os
import subprocess

from agent_rd_admin_v1 import PUBLIC, ROOT, write

command = ["npm.cmd", "run", "test", "--", "src/app.test.tsx", "-t", "preserves provenance", "--maxWorkers=1", "--no-file-parallelism"]
result = subprocess.run(command, cwd=ROOT / "frontend", env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=512"}, capture_output=True, text=True, encoding="utf-8")
write(PUBLIC / "frontend-route-reproduction-v1.json", {"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr}, True)
print(result.stdout[-2200:])
print(result.stderr[:2300])
raise SystemExit(result.returncode)
