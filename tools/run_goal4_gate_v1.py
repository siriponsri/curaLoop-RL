"""Bounded orchestration of the frozen selection gate, outside policy code."""

import json
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]


def main():
    guard = Guard(ROOT / ".local/plan-a-20261105-v2/selection-admin-resources-v1.json", 900, 4*1024**3, 900)
    try:
        from research.study_v1.admin import select
        select(ROOT)
        guard.finish("PASS")
    except Exception as error:
        guard.finish("FAIL", sanitized_reason=type(error).__name__)
        print(json.dumps({"status": "FAIL", "exception_type": type(error).__name__}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
