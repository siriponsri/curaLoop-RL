"""Run source-identified metadata/constructed checks without new assay access."""

import argparse
import contextlib
import hashlib
import json
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"
FILES = [
    "research/benchmark_v3/prepare_features.py",
    "research/benchmark_v3/prepare_features_v2.py",
    "research/configs/goal3_feature_preparation_v1.json",
    "research/configs/goal3_feature_preparation_v2.json",
    "research/configs/goal3_feature_access_policy_v2.json",
    "tests/research/test_feature_projection_v3.py",
    "tests/research/test_feature_reserve_expansion_v3.py",
    "tools/run_goal3_revision_a_checks_v2.py",
    "tools/resource_guard_v1.py",
]


def identities():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in FILES}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", choices=["v2b", "v2c"], required=True)
    args = parser.parse_args()
    paths = {key: PACKET / f"revision-a-checks-{args.attempt}.{suffix}" for key, suffix in (
        ("log", "txt"), ("xml", "xml"), ("identity", "json"), ("resources", "resources.json")
    )}
    if any(path.exists() for path in paths.values()):
        raise FileExistsError("Preserve every check attempt.")
    guard = Guard(paths["resources"], 180, 1024**3, 120)
    before = identities()
    import pytest
    with paths["log"].open("x", encoding="utf-8", newline="\n") as handle:
        with contextlib.redirect_stdout(handle), contextlib.redirect_stderr(handle):
            result = pytest.main([
                "-q", "tests/research/test_feature_projection_v3.py",
                "tests/research/test_feature_reserve_expansion_v3.py",
                f"--junitxml={paths['xml']}",
            ])
    unchanged = before == identities()
    status = "PASS" if result == 0 and unchanged else "FAIL"
    paths["identity"].write_text(json.dumps({
        "status": status, "pytest_exit": int(result), "source_sha256": before,
        "sources_unchanged": unchanged, "new_assay_members_read": False,
        "metadata_only_real_inputs": True,
    }, indent=2) + "\n", encoding="utf-8", newline="\n")
    guard.finish(status)
    print(json.dumps({"status": status, "pytest_exit": int(result), "sources_unchanged": unchanged}))
    raise SystemExit(0 if status == "PASS" else 1)


if __name__ == "__main__":
    main()
