"""Retain the first lint failure; rerun the same preparation checks after spacing fix."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, start
from tools import cf1_quality_checks_v1 as prior

if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) == 2 else "2"
    assert version in ("2", "3")
    attempt = "preparation-quality-v" + version
    guard = start(attempt, 180, 300, bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        # Retain v1 receipts; redirect only this repetition's newly emitted files.
        def versioned_new(path, value):
            path = Path(path)
            if path == TASK / "lint-response-v1.json":
                path = TASK / ("lint-response-v" + version + ".json")
            elif path == PUBLIC / "preparation-quality-v1.json":
                path = PUBLIC / ("preparation-quality-v" + version + ".json")
            return new(path, value)

        prior.new = versioned_new
        status = prior.main()
        finish(attempt, guard, status)
        raise SystemExit(0 if status.startswith("PASS") else 1)
    except Exception:
        finish(attempt, guard, "FAIL")
        raise
