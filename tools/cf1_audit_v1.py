"""CF1 closure evidence: preservation, real jobs, independent counts and return."""
# ruff: noqa: E402

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, authority, finish, new, read, sha, start


def main():
    release, ledger = authority()
    active = [k for k, r in ledger["bookings"].items() if r["status"] == "RESERVED" and k != "final-audit-v1"]
    assert not active, active
    preserved = {}
    for relative, expected in release["prior_ledger_pins"].items():
        assert sha(ROOT / relative) == expected
        preserved[relative] = expected
    old = ROOT / ".local/lr-d23-20261109-v1"
    historical_pins = read(old / "preservation-pins-v1.json")["pins"]
    d23_source_pins = read(old / "execution-freeze-v1.json")["source_pins"]
    for relative, expected in {**historical_pins, **d23_source_pins}.items():
        assert sha(ROOT / relative) == expected
    source_pins = read(TASK / "code-pins-science-v2.json")
    returned = TASK / "remote-return/files"
    for relative, expected in source_pins.items():
        assert sha(ROOT / relative) == sha(returned / "code-v2" / relative) == expected
    transport_files = read(TASK / "transport-manifest-v1.json")["files"]
    for entry in transport_files:
        assert sha(returned / entry["path"]) == entry["sha256"]
    assert sha(returned / "utility/storage_probe_v1.py") == sha(ROOT / "research/confirmation_v1/storage_probe_v1.py")
    assert read(PUBLIC / "storage-compression-calibration-v1.json")["confirmation_values_analyzed"] is False
    counts = {"fit": 0, "features": 0, "portfolio": 0, "constructed": 0, "selection_calibration": 0}
    measured = dict.fromkeys(counts, 0.0)
    differences = []
    for name, booking in ledger["bookings"].items():
        if booking.get("handler") not in counts:
            continue
        assert booking["status"] == "PASS", name
        local = read(TASK / "jobs" / name / "result.json")
        assert local == read(returned / "jobs" / name / "result.json")
        assert read(TASK / "jobs" / name / "kernel-proof.json") == {"cpu.max": "100000 100000", "memory.max": "4294967296", "memory.swap.max": "0"}
        counts[booking["handler"]] += 1
        measured[booking["handler"]] += local["whole_cgroup_cpu_seconds_at_result"]
        if booking["handler"] == "fit":
            assert not local["confirmation_values_analyzed"] and local["model_fits"] == 1
            if local["ranker"] == "mvsa":
                assert local["details"]["source_reproduction"] == "PASS_FULL_PRIMARY_SCORE_CONCORDANCE"
                differences.append(local["details"]["maximum_absolute_difference"])
    assert counts == {"fit": 60, "features": 6, "portfolio": 6, "constructed": 1, "selection_calibration": 6}
    assert len(differences) == 30
    assert read(PUBLIC / "primary-score-validation-v1.json")["status"] == "PASS_ALL_SIX_PRIMARY_SCORE_AND_OPERATOR_CHECKS"
    assert read(PUBLIC / "results-summary-v1.json")["status"] == "PASS_INDEPENDENT_AGGREGATE_RECALCULATION"
    complete = read(TASK / "remote-return/verified-v1.json")
    assert complete["status"] == "PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD"
    assert read(PUBLIC / "fresh-absence-v1.json")["status"] == "PASS_FRESH_EXACT_ABSENCE"
    assert complete["total_bytes"] + complete["archive_bytes"] < 8 * 1024**3
    assert ledger["confirmation_values_analyzed"] and not ledger["final16_access"] and not ledger["new_selector_training"]
    assert all(ledger["retained_seconds"].get(k, 0) <= v for k, v in ledger["stage_caps_seconds"].items())
    assert sum(ledger["retained_seconds"].values()) <= 172800
    paths = sorted([p.relative_to(ROOT).as_posix() for p in (ROOT / "tools").glob("cf1_*.py")]
                   + [p.relative_to(ROOT).as_posix() for p in (ROOT / "research/confirmation_v1").glob("*.py")]
                   + ["tests/test_confirmation_v1_contracts.py"])
    lint = subprocess.run(["rtk", "proxy", "ruff", "check", *paths], capture_output=True, text=True, timeout=90)
    new(TASK / "final-lint-v1.json", {"exit_code": lint.returncode, "stdout": lint.stdout, "stderr": lint.stderr})
    assert lint.returncode == 0, lint.stdout
    documents = [ROOT / name for name in ("README.md", "START_HERE.md", "GOAL.md", "PLAN.md", "HANDOFF.md")]
    documents += list((ROOT / "docs/03_research").glob("LR_CF1*.md"))
    documents += list((ROOT / "docs/06_execution").glob("LR_CF1*.md"))
    documents += list((ROOT / "docs/07_publication").glob("LR_CF1*.md"))
    documents += [PUBLIC / "README.md", ROOT / "research/product_handoffs/lr_cf1_v1/README.md"]
    broken, links = [], 0
    for document in documents:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:", "codex:")):
                continue
            path = (document.parent / unquote(target.split("#")[0]).strip("<>")).resolve()
            links += 1
            if not path.is_relative_to(ROOT) or not path.exists():
                broken.append({"document": document.relative_to(ROOT).as_posix(), "target": target})
    assert not broken, broken
    check = subprocess.run(["rtk", "proxy", "git", "diff", "--check"], capture_output=True, text=True, timeout=30)
    assert check.returncode == 0, check.stdout
    value = {"status": "PASS_CF1_CLOSURE_AUDIT", "prior_ledger_count_unchanged": len(preserved),
        "historical_scientific_pin_count_unchanged": len(historical_pins),
        "lrd23_source_pin_count_unchanged": len(d23_source_pins),
        "scientific_code_pins_unchanged": len(source_pins), "real_job_counts": counts,
        "original_transport_files_unchanged": len(transport_files),
        "opaque_storage_probe_source_unchanged": True,
        "measured_whole_scientific_cgroup_cpu_seconds_by_handler": measured,
        "measurement_scope": "scientific handlers only, includes imports/hashes/serialization at result; excludes setup/return/untracked utilities and is not total project CPU",
        "retained_cpu_seconds": sum(ledger["retained_seconds"].values()), "stage_retained_seconds": ledger["retained_seconds"],
        "utility_bucket_fully_retained": True, "maximum_mvsa_recalculation_absolute_difference": max(differences),
        "independently_recalculated_portfolio_cells": 2700, "complete_return_files": complete["file_count"],
        "complete_return_bytes": complete["total_bytes"], "export_file_count": complete["export_file_count"],
        "exact_cleanup_and_fresh_absence": True, "scoped_lint": "PASS", "local_links_checked": links,
        "whitespace_check": "PASS", "final16_access": False, "new_selector_training": False,
        "actual_product_integration": False, "submission_or_commercial_clearance": False}
    new(PUBLIC / "closure-audit-v1.json", value)
    print(json.dumps(value, indent=2))


if __name__ == "__main__":
    guard = start("final-audit-v1", 180, 600, bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("final-audit-v1", guard, "PASS_CF1_CLOSURE_AUDIT")
    except BaseException:
        finish("final-audit-v1", guard, "FAIL")
        raise
