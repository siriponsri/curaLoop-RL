"""Guarded constructed tests of reporting math, without actual campaign inputs."""

import contextlib
import argparse
import json
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", choices=["v2", "v3"], required=True)
    args = parser.parse_args()
    suffix = args.attempt
    guard = Guard(PACKET / f"analysis-checks-resources-{suffix}.json", 180, 1024**3, 180)
    from research.benchmark_v3.prepare_features_v2 import sha_file
    import pytest
    names = ["tools/analyze_goal4_v1.py", "tests/research/test_goal4_analysis_v1.py", "tools/check_goal4_analysis_v1.py"]
    before = {name: sha_file(ROOT / name) for name in names}
    with (PACKET / f"analysis-checks-{suffix}.txt").open("x", encoding="utf-8", newline="\n") as handle:
        with contextlib.redirect_stdout(handle), contextlib.redirect_stderr(handle):
            code = pytest.main(["-q", "tests/research/test_goal4_analysis_v1.py", f"--junitxml={PACKET / ('analysis-checks-' + suffix + '.xml')}"])
    same = all(sha_file(ROOT / name) == value for name, value in before.items())
    status = "PASS" if code == 0 and same else "FAIL"
    (PACKET / f"analysis-checks-{suffix}.json").open("x", encoding="utf-8").write(json.dumps({
        "status": status, "pytest_exit": int(code), "sources_unchanged": same,
        "source_sha256": before, "real_campaign_inputs_read": False}, indent=2) + "\n")
    guard.finish(status)
    print(json.dumps({"status": status, "pytest_exit": int(code)}))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
