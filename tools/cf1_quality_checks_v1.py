"""Bounded preparation lint/link checks, not a scientific result or closeout."""
# ruff: noqa: E402

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, sha, start


def main():
    paths = sorted([p.relative_to(ROOT).as_posix() for p in (ROOT / "tools").glob("cf1_*.py")]
                   + [p.relative_to(ROOT).as_posix() for p in (ROOT / "research/confirmation_v1").glob("*.py")]
                   + ["tests/test_confirmation_v1_contracts.py"])
    result = subprocess.run(["rtk", "proxy", "ruff", "check", *paths], capture_output=True, text=True, timeout=90)
    new(TASK / "lint-response-v1.json", {"exit_code": result.returncode, "stdout": result.stdout,
                                        "stderr": result.stderr, "paths": paths})
    documents = [ROOT / p for p in (
        "docs/06_execution/LR_CF1_EXECUTION_STATUS_20261109.md",
        "docs/06_execution/LR_CF1_SOURCE_CONCORDANCE_DECISION_20261109.md",
        "docs/03_research/LR_CF1_METHODS_CHECKPOINT_20261109.md",
        "docs/evidence/lr-cf1-20261109-v1/README.md")]
    checked, broken = 0, []
    for document in documents:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if target.startswith(("https://", "http://", "#")):
                continue
            path = (document.parent / unquote(target.split("#")[0])).resolve()
            checked += 1
            if not path.is_relative_to(ROOT) or not path.exists():
                broken.append({"document": document.relative_to(ROOT).as_posix(), "target": target})
    check = subprocess.run(["rtk", "proxy", "git", "diff", "--check"], capture_output=True, text=True, timeout=30)
    summary = {"status": "PASS_PREPARATION_QUALITY" if result.returncode == 0 and check.returncode == 0 and not broken else "FAIL",
               "ruff_exit_code": result.returncode, "diff_check_exit_code": check.returncode,
               "local_links_checked": checked, "broken_links": broken,
               "code_pins": {p: sha(ROOT / p) for p in paths}, "scientific_gate_pass": False}
    new(PUBLIC / "preparation-quality-v1.json", summary)
    print({k: v for k, v in summary.items() if k != "code_pins"})
    print(result.stdout, result.stderr, check.stdout, check.stderr)
    return summary["status"]


if __name__ == "__main__":
    guard = start("preparation-quality", 180, 300, bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        status = main()
        finish("preparation-quality", guard, status)
        raise SystemExit(0 if status.startswith("PASS") else 1)
    except Exception:
        finish("preparation-quality", guard, "FAIL")
        raise
