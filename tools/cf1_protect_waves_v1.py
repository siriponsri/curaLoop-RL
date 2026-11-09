"""Blinded checks in two waves, exactly one active job per assigned core."""
# ruff: noqa: E402

import ast
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import TASK, finish, new, read, start
from tools import cf1_remote_v1 as remote


def main():
    assert read(TASK / "jobs/smoke/result.json")["status"] == "PASS_ORIGINAL_VERSION_CPU_RUNTIME_SMOKE"
    new_sources = ["research/confirmation_v1/" + name + ".py" for name in ("features", "rankers", "portfolios", "scientific_worker")]
    check = subprocess.run(["rtk", "proxy", "ruff", "check", "--fix", *new_sources], capture_output=True, text=True, timeout=60)
    version = sys.argv[1] if len(sys.argv) == 2 else "1"
    new(TASK / ("scientific-code-preparation-lint-v" + version + ".json"), {"exit_code": check.returncode, "stdout": check.stdout, "stderr": check.stderr})
    assert check.returncode == 0, check.stdout
    for name in new_sources:
        ast.parse((ROOT / name).read_text(), feature_version=(3, 8))
    selected = read(TASK / "metadata-admission-v1.json")["selected"]
    names = []
    for i, row in enumerate(selected):
        key = row["campaign"].replace("/", "-")
        name = "protect-" + key
        remote.book(name, "protect", 600, "admission_and_calibration", processor=69 + i % 3,
                    extra={"campaign": row["campaign"], "output_name": key})
        names.append(name)
    for begin in range(0, len(names), 3):
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(remote.dispatch, name): name for name in names[begin:begin + 3]}
            for future in as_completed(futures):
                remote.settle(futures[future], future.result())


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) == 2 else "1"
    assert version in ("1", "2")
    attempt = "blinded-protection-waves-v" + version
    guard = start(attempt, 300, 4200,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish(attempt, guard, "PASS_BLINDED_CHECK_DISPATCH_COMPLETED")
    except BaseException:
        finish(attempt, guard, "FAIL")
        raise
