"""Source-identified constructed evaluation tests before semantic real labels."""

import argparse
import contextlib
import hashlib
import importlib.metadata
import json
import platform
import sys
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"


def source_files():
    names = [p.relative_to(ROOT).as_posix() for pattern in (
        "research/study_v1/*.py", "research/planning_v3/*.py"
    ) for p in ROOT.glob(pattern)]
    names += [
        "research/event_time.py", "research/benchmark_v3/prepare_features_v2.py",
        "research/configs/goal4_protocol_v1.json", "tools/resource_guard_v1.py",
        "tools/prepare_goal4_labels_v1.py", "tools/check_goal4_evaluator_v1.py",
        "tools/freeze_goal4_protocol_v1.py",
        "tests/research/test_goal4_boundary_v1.py",
        ".gitignore",
    ]
    return sorted(names)


def identities():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in source_files()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", choices=["v1", "v2", "v3"], required=True)
    args = parser.parse_args()
    PACKET.mkdir(exist_ok=True)
    stem = PACKET / f"evaluator-checks-{args.attempt}"
    paths = {key: stem.with_suffix(suffix) for key, suffix in (
        ("log", ".txt"), ("xml", ".xml"), ("identity", ".json"), ("resource", ".resources.json")
    )}
    if any(p.exists() for p in paths.values()):
        raise FileExistsError("Retain every attempt.")
    guard = Guard(paths["resource"], 600, 1024**3, 600)
    before = identities()
    import pytest
    with paths["log"].open("x", encoding="utf-8", newline="\n") as handle:
        with contextlib.redirect_stdout(handle), contextlib.redirect_stderr(handle):
            code = pytest.main(["-q", "tests/research/test_goal4_boundary_v1.py", f"--junitxml={paths['xml']}"])
    same = before == identities()
    result = {"status": "PASS" if code == 0 and same else "FAIL", "pytest_exit": int(code),
              "sources_unchanged": same, "source_sha256": before, "python": sys.version,
              "platform": platform.platform(), "packages": {name: importlib.metadata.version(name) for name in (
                  "numpy", "scipy", "scikit-learn", "rdkit", "pytest", "threadpoolctl")},
              "new_real_assay_outcomes_accessed": False}
    paths["identity"].write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    guard.finish(result["status"])
    print(json.dumps({k: result[k] for k in ("status", "pytest_exit", "sources_unchanged")}))
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
