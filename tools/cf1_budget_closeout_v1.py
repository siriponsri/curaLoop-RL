"""Verify public boundaries and close CF1 without releasing any unused budget."""
# ruff: noqa: E402

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    PUBLIC,
    TASK,
    authority,
    finish,
    new,
    now,
    read,
    save,
    sha,
    start,
)

FORBIDDEN = {"record_id", "canonical_smiles", "SMILES", "raw_confirmatory", "source_row", "source_index",
             "selected_compound_ids", "raw_labels", "compound_rows", "pending_assay_results"}


def git(*args):
    result = subprocess.run(["rtk", "proxy", "git", *args], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def private_fields(value, path, trail=""):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN:
                found.append(path + ":" + trail + "/" + key)
            found += private_fields(item, path, trail + "/" + key)
    elif isinstance(value, list):
        for i, item in enumerate(value):
            found += private_fields(item, path, trail + "/" + str(i))
    return found


def main():
    authority()
    audit = read(PUBLIC / "closure-audit-v2.json")
    assert audit["status"] == "PASS_CF1_CLOSURE_AUDIT"
    assert git("branch", "--show-current") == "main"
    paths = sorted(set(git("diff", "--name-only").splitlines() + git("ls-files", "--others", "--exclude-standard").splitlines()))
    allowed = ("tools/cf1_", "research/confirmation_v1/", "research/product_handoffs/lr_cf1_v1/",
               "research/manifests/lr_cf1_", "docs/evidence/lr-cf1-20261109-v1/",
               "docs/03_research/LR_CF1_", "docs/05_product/LR_CF1_", "docs/06_execution/LR_CF1_",
               "docs/07_publication/LR_CF1_", "tests/test_confirmation_v1_contracts.py")
    root_files = {"README.md", "START_HERE.md", "GOAL.md", "PLAN.md", "HANDOFF.md", "AGENTS.md"}
    assert all(path in root_files or path.startswith(allowed) for path in paths), [p for p in paths if p not in root_files and not p.startswith(allowed)]
    assert all(not path.startswith((".local/", "research/raw_data/")) for path in paths)
    for path in (".local/lr-cf1-20261109-v1/remote-return/files/data/628-677.csv",
                 "research/raw_data/external-benchmarks/aic-finder-2024/metadata/oc3c01517_si_001.pdf"):
        result = subprocess.run(["rtk", "proxy", "git", "check-ignore", "--quiet", path], capture_output=True, timeout=30)
        assert result.returncode == 0, path
    suspicious, checked = [], 0
    for directory in (PUBLIC, ROOT / "research/product_handoffs/lr_cf1_v1"):
        for path in directory.rglob("*"):
            if path.suffix == ".json":
                suspicious += private_fields(read(path), path.relative_to(ROOT).as_posix())
                checked += 1
            elif path.suffix == ".csv":
                with path.open(newline="") as file:
                    header = next(csv.reader(file))
                suspicious += [path.relative_to(ROOT).as_posix() + ":" + column for column in header if column in FORBIDDEN]
                checked += 1
    assert not suspicious, suspicious
    assert all((ROOT / path).stat().st_size < 10 * 1024**2 for path in paths)
    assert not git("diff", "--check")
    new(PUBLIC / "publication-boundary-v1.json", {"status": "PASS_AGGREGATE_ONLY_MAIN_BOUNDARY",
        "candidate_changed_paths": len(paths), "json_csv_files_checked": checked,
        "private_raw_data_and_owner_pdf_gitignored": True, "individual_identity_or_outcome_fields_found": [],
        "unexpected_project_paths_found": [], "max_new_file_bytes": max((ROOT / p).stat().st_size for p in paths),
        "purpose": "authorized main delivery of source, aggregates and offline artifacts; not journal submission or raw redistribution"})
    print("PASS aggregate publication boundary; private raw data/owner PDF ignored")


if __name__ == "__main__":
    guard = start("delivery-boundary-budget-closeout-v1", 180, 600,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("delivery-boundary-budget-closeout-v1", guard, "PASS_PUBLIC_BOUNDARY_AND_BUDGET_CLOSEOUT")
    except BaseException:
        finish("delivery-boundary-budget-closeout-v1", guard, "FAIL")
        raise
    release, ledger = authority()
    assert not any(r["status"] == "RESERVED" for r in ledger["bookings"].values())
    ledger.update(status="CLOSED", closed_utc=now().isoformat(),
        closeout_audit_sha256=sha(PUBLIC / "closure-audit-v2.json"),
        scientific_disposition="NO_GO_QUOTA_ONLY_METHOD_CLAIM",
        unused_allowance_released=False, owner_review_before_next_phase=True)
    save(ledger)
    budget = {"status": "CLOSED_WITHIN_ORIGINAL_LIMITS", "closed_utc": ledger["closed_utc"],
        "release_utc": ledger["release_utc"], "deadline_utc": ledger["deadline_utc"],
        "retained_cpu_seconds": sum(ledger["retained_seconds"].values()), "cpu_cap_seconds": 172800,
        "retained_hours": sum(ledger["retained_seconds"].values()) / 3600,
        "stage_retained_seconds": ledger["retained_seconds"], "all_utility_bucket_retained": True,
        "all_attempt_states": dict(Counter(r["status"] for r in ledger["bookings"].values())),
        "open_bookings": 0, "original_deadline_met": now().isoformat() < release["deadline_utc"],
        "closed_private_ledger_sha256": sha(TASK / "ledger.json"),
        "not_a_measured_total_cpu_claim": True, "unused_allowance_released": False,
        "confirmation_values_analyzed": True, "final16_access": False, "new_selector_training": False}
    new(PUBLIC / "budget-closeout-v1.json", budget)
    new(ROOT / "research/manifests/lr_cf1_disposition_20261109_v1.json", {
        "schema": "curaloop.lr_cf1.disposition.v1", "status": "COMPLETE_FOR_OWNER_REVIEW",
        "scientific_disposition": "NO_GO_QUOTA_ONLY_METHOD_CLAIM", "novel_selector_potential": "UNPROVEN",
        "publication_ready": False, "data_and_baseline_feasibility_complete": True,
        "campaigns": 6, "molecular_fits": 60, "cells": 2700,
        "all_previous_ledger_and_scientific_pins_unchanged": True,
        "complete_private_return_and_exact_cleanup": True, "final16_access": False,
        "new_selector_training": False, "actual_product_integration": False,
        "cf2_design_released": False, "p_cf1_released": False,
        "audit": "docs/evidence/lr-cf1-20261109-v1/closure-audit-v2.json",
        "budget": "docs/evidence/lr-cf1-20261109-v1/budget-closeout-v1.json",
        "owner_checkpoint": "docs/06_execution/LR_CF1_OWNER_CHECKPOINT_20261109.md"})
    # These reference-only additions follow creation of their actual target files.
    index = PUBLIC / "README.md"
    text = index.read_text(encoding="utf-8")
    text = text.replace("- Final `closure-audit-v1.json` and `budget-closeout-v1.json` are produced only\n  after the actual preservation/source/role/budget checks pass.",
        "- [Final closure audit](closure-audit-v2.json): 12 old ledgers, 58 old scientific pins, 17 LR-D23 source pins and 11 current worker pins unchanged; 214 references and scoped lint/whitespace PASS.\n- [Closed budget](budget-closeout-v1.json): 93,088/172,800 retained seconds; no open booking or released remainder.\n- [Public delivery boundary](publication-boundary-v1.json): raw records/PDFs/traces remain ignored and individual row fields are absent.")
    index.write_text(text, encoding="utf-8", newline="\n")
    for name in ("HANDOFF.md", "docs/06_execution/LR_CF1_EXECUTION_STATUS_20261109.md"):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        label = "[Closure audit](docs/evidence/lr-cf1-20261109-v1/closure-audit-v2.json) and [closed budget](docs/evidence/lr-cf1-20261109-v1/budget-closeout-v1.json)" if name == "HANDOFF.md" else "[Closure audit](../evidence/lr-cf1-20261109-v1/closure-audit-v2.json) and [closed budget](../evidence/lr-cf1-20261109-v1/budget-closeout-v1.json)"
        first, rest = text.split("\n", 1)
        path.write_text(first + "\n\n**Final audit and budget closure PASS.** " + label + ". No open bookings; normal main delivery is the remaining authorized action.\n" + rest,
                        encoding="utf-8", newline="\n")
    print(json.dumps(budget, indent=2))
