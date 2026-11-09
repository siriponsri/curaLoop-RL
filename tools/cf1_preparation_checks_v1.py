"""Constructed contract tests under the fresh local one-worker envelope."""
# ruff: noqa: E402

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, sha, start

if __name__ == "__main__":
    guard = start("constructed-contract-checks", 180, 300, bucket="utilities_return_handoff_delivery")
    try:
        import pytest

        code = pytest.main(["tests/test_confirmation_v1_contracts.py", "-q", "-o", "addopts=",
                            "-p", "no:cacheprovider"])
        result = {"status": "PASS_CONSTRUCTED_CONTRACT_TESTS" if code == 0 else "FAIL",
                  "pytest_exit_code": int(code), "biological_inputs_used": False,
                  "confirmation_values_analyzed": False, "final16_access": False,
                  "not_a_baseline_reproduction": True,
                  "code_pins": {p: sha(ROOT / p) for p in ["research/confirmation_v1/contracts.py",
                                                                         "tests/test_confirmation_v1_contracts.py"]}}
        new(TASK / "constructed-checks-v1.json", result)
        new(PUBLIC / "constructed-checks-v1.json", result)
        finish("constructed-contract-checks", guard, result["status"])
        raise SystemExit(code)
    except Exception:
        finish("constructed-contract-checks", guard, "FAIL")
        raise
