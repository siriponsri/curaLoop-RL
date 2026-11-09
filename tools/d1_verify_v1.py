"""Guarded local constructed tests; no molecular record access."""
# ruff: noqa: E402 -- repository-only CLI bootstraps the source import path.

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import PUBLIC, finish_job, new, start_job


def main():
    guard = start_job("verification")
    try:
        import pytest

        exit_code = pytest.main([
            "tests/research/test_d1_analysis_v1.py", "tests/research/test_m2_diagnostics_v1.py",
            "-q", "-p", "no:cacheprovider", "--junitxml=" + str(PUBLIC / "constructed-tests-v1.xml"),
        ])
        new(PUBLIC / "constructed-verification-v1.json", {
            "status": "PASS" if exit_code == 0 else "FAIL", "pytest_exit_code": int(exit_code),
            "molecular_outcomes_read": False, "linux_real_cpu_interrupt": "NOT_RUN",
        })
        finish_job("verification", guard, "PASS" if exit_code == 0 else "FAIL")
        return int(exit_code)
    except BaseException:
        finish_job("verification", guard, "FAIL")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
