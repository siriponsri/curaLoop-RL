"""Continue after the authenticated retained-root bootstrap repair."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import TASK, finish, read, start
from tools import cf1_remote_v1 as remote


def main():
    assert read(TASK / "jobs/bootstrap-retry-v2/result.json")["status"] == "PASS_AUTHENTICATED_STREAM_BOOTSTRAP"
    remote.book("environment", "environment", 600, "admission_and_calibration")
    assert remote.settle("environment", remote.dispatch("environment")) == "PASS"


if __name__ == "__main__":
    guard = start("transport-environment-v2", 180, 2200,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("transport-environment-v2", guard, "PASS_ENVIRONMENT_TRANSPORT")
    except BaseException:
        finish("transport-environment-v2", guard, "FAIL")
        raise
