"""Run existing frontend lint/build commands inside the admitted local Job."""

import json
import subprocess
import sys

from cf2p_admin_v1 import PUBLIC, ROOT, write


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else "v1"
    assert tag in ("v1", "v2", "v3", "v4", "v5")
    records = []
    for task in ("lint", "build"):
        command = ["rtk", "proxy", "npm", "--prefix", "frontend", "run", task]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        records.append({"task": task, "command": command, "exit_code": result.returncode,
                        "stdout": result.stdout, "stderr": result.stderr})
        if result.returncode:
            write(PUBLIC / f"frontend-build-attempt-{tag}.json", {"status": "FAIL", "checks": records}, True)
            print(json.dumps(records, indent=2))
            raise SystemExit(result.returncode)
    write(PUBLIC / f"frontend-build-{tag}.json", {"status": "PASS", "checks": records}, True)
    print(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
