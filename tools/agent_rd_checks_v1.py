"""Real component checks; never presents them as model evaluation."""

import os
import subprocess
import sys

from agent_rd_admin_v1 import PUBLIC, ROOT, write


def main():
    tag = sys.argv[1]
    paths = ["src/curaloop_rd/agent_rd", "api/agent_rd_routes.py", "api/main.py", "tests/test_agent_rd.py", "tests/test_agent_rd_eval.py", "research/agent_rd_eval_v1"]
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT / "tools").glob("agent_rd_*.py"))]
    checks = []
    for command in [[sys.executable, "-m", "ruff", "check", "--fix", *paths],
                    [sys.executable, "-m", "pytest", "tests/test_agent_rd.py", "tests/test_agent_rd_eval.py", "tests/test_confirmation_study.py", "-q",
                     "--basetemp=.local/agent-rd-run-20261110-v1/pytest-" + tag]]:
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, "CURALOOP_AGENT_INFERENCE_DISABLED": "1"}, capture_output=True, text=True)
        checks.append({"command": command, "exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
        print(result.stdout[-7000:])
        if result.returncode:
            print(result.stderr[-2000:])
            break
    write(PUBLIC / ("component-checks-" + tag + ".json"), {"status": "PASS" if all(r["exit_code"] == 0 for r in checks) else "FAIL",
          "real_model_evaluation": False, "checks": checks}, True)
    raise SystemExit(checks[-1]["exit_code"])


if __name__ == "__main__":
    main()
