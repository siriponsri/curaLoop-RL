"""Source-identified constructed preservation checks; never access real remote data."""

import contextlib
import json
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"


def main():
    output = PACKET / "return-checks-v1.json"
    if output.exists():
        raise FileExistsError("Preserve check attempts.")
    guard = Guard(PACKET / "return-checks-resources-v1.json", 180, 1024**3, 180)
    from research.benchmark_v3.prepare_features_v2 import sha_file
    import pytest
    names = ["tools/remote_goal4_return_v1.py", "tools/remote_task_archive_v1.py",
             "tools/verify_remote_return_v1.py", "tools/verify_remote_return_v2.py",
             "tests/research/test_goal4_return_v1.py", "tools/check_goal4_return_v1.py"]
    before = {name: sha_file(ROOT / name) for name in names}
    with (PACKET / "return-checks-v1.txt").open("x", encoding="utf-8", newline="\n") as handle:
        with contextlib.redirect_stdout(handle), contextlib.redirect_stderr(handle):
            code = pytest.main(["-q", "tests/research/test_goal4_return_v1.py", f"--junitxml={PACKET / 'return-checks-v1.xml'}"])
    same = all(sha_file(ROOT / name) == digest for name, digest in before.items())
    status = "PASS" if code == 0 and same else "FAIL"
    output.write_text(json.dumps({"status": status, "pytest_exit": int(code), "source_sha256": before,
                      "sources_unchanged": same, "real_remote_data_accessed": False}, indent=2) + "\n", encoding="utf-8", newline="\n")
    guard.finish(status)
    print(json.dumps({"status": status, "pytest_exit": int(code), "sources_unchanged": same}))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
