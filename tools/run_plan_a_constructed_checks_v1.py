"""Bounded, source-identified constructed checks; no real assay ingestion."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import io
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"
TESTS = [
    "test_fsmol_headers_v1.py",
    "test_remote_preservation_v1.py",
    "test_feature_projection_v3.py",
    "test_queue_v3.py",
    "test_mixture_v3.py",
    "test_recourse_v3.py",
    "test_recourse_oracle_v3.py",
    "test_belief_v3.py",
    "test_controls_v3.py",
    "test_public_policy_v3.py",
    "test_plan_a_return_v1.py",
]


def identities():
    paths = list((ROOT / "research/planning_v3").glob("*.py"))
    paths += [ROOT / "tests/research" / name for name in TESTS]
    paths += [
        ROOT / name
        for name in (
            "research/event_time.py",
            "research/benchmark_v3/prepare_features.py",
            "tools/index_fsmol_archive_v1.py",
            "tools/remote_task_archive_v1.py",
            "tools/remote_plan_a_return_v1.py",
            "tools/verify_remote_return_v1.py",
            "tools/verify_remote_return_v2.py",
            "tools/resource_guard_v1.py",
            "tools/run_plan_a_constructed_checks_v1.py",
        )
    ]
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"v[1-9][0-9]*", args.attempt):
        raise ValueError("New numbered attempt required.")
    prefix = "constructed-all-" + args.attempt
    if any(PACKET.glob(prefix + "*")):
        raise FileExistsError("Keep existing evidence attempts.")
    # Capture Git identity before the single-process job forbids descendants.
    parent = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    guard = Guard(PACKET / (prefix + "-resources.json"), 600, 1073741824)
    before = identities()
    import pytest

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
        result = int(
            pytest.main(
                [
                    *["tests/research/" + name for name in TESTS],
                    "-q",
                    "--junitxml=" + str(PACKET / (prefix + "-tests.xml")),
                ]
            )
        )
    same = before == identities()
    if not same:
        result = 1
    report = {
        "status": "PASS" if result == 0 else "FAIL",
        "scope": "CONSTRUCTED_ONLY_NO_NEW_REAL_ASSAY_LABELS",
        "parent_commit": parent,
        "source_sha256": before,
        "source_unchanged_during_checks": same,
        "test_files": TESTS,
        "pytest_exit_code": result,
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {
            name: importlib.metadata.version(name)
            for name in ("numpy", "scipy", "scikit-learn", "rdkit", "threadpoolctl", "pytest")
        },
        "full_application_suites_rerun": False,
        "final_evaluation": False,
    }
    with (PACKET / (prefix + "-identity.json")).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    with (PACKET / (prefix + "-tests.txt")).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(buffer.getvalue())
    guard.finish(report["status"], pytest_exit_code=result, source_unchanged=same)
    print(buffer.getvalue())
    return result


if __name__ == "__main__":
    raise SystemExit(main())
