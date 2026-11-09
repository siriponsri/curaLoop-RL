"""Polish current English spacing while preserving all numbers and link targets."""
# ruff: noqa: E402

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, finish, new, now, sha, start

FILES = ["README.md", "START_HERE.md", "GOAL.md", "PLAN.md", "HANDOFF.md", "AGENTS.md",
    "docs/03_research/LR_CF1_RESULTS_20261109.md", "docs/03_research/LR_CF1_NEXT_METHOD_DISPOSITION_20261109.md",
    "docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md", "docs/06_execution/LR_CF1_EXECUTION_STATUS_20261109.md",
    "docs/07_publication/LR_CF1_METHODS_RESULTS_INSERT_20261109.md",
    "docs/05_product/LR_CF1_OFFLINE_HANDOFF_CONTRACT_20261109.md",
    "docs/evidence/lr-cf1-20261109-v1/README.md", "research/product_handoffs/lr_cf1_v1/README.md"]


def polish(text):
    text = re.sub(r"\b(all|All|only|Only|at|At|below|Below|under|Under|predeclared|local|max|each|source|Source)(?=\d)", r"\1 ", text)
    text = re.sub(r"(?<=[A-Za-z]),(?=\d)", ", ", text)
    text = re.sub(r"(?<=[A-Za-z])/(?=\d)", " / ", text)
    text = re.sub(r"(?<=\d)(November|October)", r" \1", text)
    text = re.sub(r"(November|October)(?=\d)", r"\1 ", text)
    text = re.sub(r"(?<=\d)(CPU-hours|CPUh|CPU|GiB|MiB|workers|fits|cells|hours|h\b)", r" \1", text)
    text = text.replace("CPUh", "CPU-hours")
    text = re.sub(r"\b([HD])(?=\d+\.\d)", r"\1=", text)
    return text


def main():
    changed = {}
    for name in FILES:
        path = ROOT / name
        before = path.read_text(encoding="utf-8")
        prefix, history = before, ""
        marker = "## Owner chooses A and resumes" if name == "AGENTS.md" else "## Historical checkpoints" if name in ("START_HERE.md", "GOAL.md", "PLAN.md") else None
        if marker:
            at = before.index(marker)
            prefix, history = before[:at], before[at:]
        after = polish(prefix) + history
        assert re.findall(r"\d+(?:[.,]\d+)*", before) == re.findall(r"\d+(?:[.,]\d+)*", after), name
        assert re.findall(r"\]\(([^)]+)\)", before) == re.findall(r"\]\(([^)]+)\)", after), name
        old = sha(path)
        path.write_text(after, encoding="utf-8", newline="\n")
        changed[name] = {"before_sha256": old, "after_sha256": sha(path)}
    new(PUBLIC / "english-polish-v1.json", {"status": "PASS_CURRENT_ENGLISH_SPACING_AND_NUMERIC_FIDELITY",
        "utc": now().isoformat(), "number_tokens_and_link_targets_unchanged": True,
        "historical_status_sections_unchanged": True, "scientific_code_or_data_changed": False, "files": changed})
    print("PASS polished current English; all number tokens and link targets unchanged")


if __name__ == "__main__":
    guard = start("english-document-polish-v1", 120, 300, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("english-document-polish-v1", guard, "PASS_ENGLISH_DOCUMENT_POLISH")
    except BaseException:
        finish("english-document-polish-v1", guard, "FAIL")
        raise
