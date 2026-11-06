"""Bound local byte verification; no scientific outcome deserialization."""

import argparse
import json
from pathlib import Path

from tools.goal4r2a2_guard_v1 import GoalGuard


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--folder", type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    folder = args.folder.resolve(strict=True)
    allowed = (root / ".local/goal4r2a2-20261106-v1/remote-return").resolve()
    if not folder.is_relative_to(allowed):
        raise ValueError("Wrong local verification folder.")
    guard = GoalGuard(folder / "verification-resources.json", 1800, 300)
    try:
        from tools.verify_goal4r2a2_return_v2 import main as verify
        verify()
        guard.finish("PASS", scientific_contents_deserialized=False, preservation_utility_reserve_covers_process=True)
    except Exception as e:
        guard.finish("FAIL", exception_type=type(e).__name__)
        raise


if __name__ == "__main__":
    main()
