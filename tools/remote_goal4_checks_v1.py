"""Bounded Linux portability check of the frozen constructed evaluator."""

import contextlib
import json
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "remote-constructed-checks-v1.json"
    if output.exists():
        raise FileExistsError("Keep every check attempt.")
    guard = Guard(ROOT / "remote-constructed-resources-v1.json", 900, 1024**3, 600)
    try:
        from research.study_v1.identity import verify_frozen
        from research.benchmark_v3.prepare_features_v2 import sha_file
        protocol = verify_frozen(ROOT)
        proof = json.loads((ROOT / "docs/evidence/goal4-20261105-v1/protocol-freeze-v1.json").read_text())
        before = {name: sha_file(ROOT / name) for name in proof["source_sha256"]}
        import pytest
        with (ROOT / "remote-constructed-checks-v1.txt").open("x") as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                code = pytest.main(["-q", "tests/research/test_goal4_boundary_v1.py",
                                    f"--junitxml={ROOT / 'remote-constructed-checks-v1.xml'}"])
        same = all(sha_file(ROOT / name) == digest for name, digest in before.items())
        status = "PASS" if code == 0 and same else "FAIL"
        output.write_text(json.dumps({"status": status, "pytest_exit": int(code), "sources_unchanged": same,
                          "source_sha256": before, "helper_sha256": sha_file(Path(__file__)),
                          "protocol_sha256": sha_file(ROOT / "research/configs/goal4_protocol_v1.json"),
                          "real_labels_used_by_tests": False}, indent=2) + "\n")
        guard.finish(status)
        print(json.dumps({"status": status, "pytest_exit": int(code), "sources_unchanged": same}))
        raise SystemExit(0 if status == "PASS" else 1)
    except Exception as error:
        guard.finish("FAIL", sanitized_reason=type(error).__name__)
        print(json.dumps({"status": "FAIL", "exception_type": type(error).__name__}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
