"""Require primary-score/operator checks for every campaign before any C value."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, authority, finish, new, read, sha, start
from tools import cf1_matrix_v2 as matrix
from tools import cf1_science_v1 as science
from tools.cf1_stage_v1 import stage


def main():
    _, ledger = authority()
    expected_fits = read(TASK / "complete-matrix-cost-release-v2.json")["remaining_fits"]
    assert all(ledger["bookings"][row["name"]]["status"] == "PASS" for row in expected_fits)
    assert not ledger["confirmation_values_analyzed"]
    features = read(TASK / "feature-manifests-v1.json")["campaigns"]
    original = read(TASK / "jobs/selection-cost-calibration-v1/result.json")
    specs = [{"name": "primary-score-check-" + r["campaign"].replace("/", "-"),
        "handler": "selection_calibration", "cpu": 180, "bucket": "admission_and_calibration",
        "extra": {"campaign": r["campaign"]}} for r in features if r["campaign"] != original["campaign"]]
    assert len(specs) == 5
    science.waves(specs)
    checks = [original] + [read(TASK / "jobs" / r["name"] / "result.json") for r in specs]
    assert len({r["campaign"] for r in checks}) == 6
    assert all(r["status"] == "PASS_SELECTION_COST_CALIBRATION_NO_VALUES" and not r["confirmation_values_analyzed"] for r in checks)
    assert all(r["universe_size"] == next(f["universe_size"] for f in features if f["campaign"] == r["campaign"]) for r in checks)
    _, ledger = authority()
    plan = read(TASK / "complete-matrix-cost-release-v2.json")
    projected = sum(ledger["retained_seconds"].values()) + plan["portfolio_total_cap_seconds"]
    assert projected <= ledger["cpu_cap_seconds"]
    value = {"status": "PASS_ALL_SIX_PRIMARY_SCORE_AND_OPERATOR_CHECKS", "campaigns": checks,
        "source_score_direction": "HIGHER_FIRST_FROM_REVIEWED_SOURCE_SEMANTICS",
        "numeric_score_integrity": "ALL_FINITE_SHARED_RANKING_GATE", "checks": "five seeds and all three operators on every complete U",
        "additional_admission_reservation_seconds": 900, "projected_retained_cpu_seconds": projected,
        "scientific_matrix_changed": False, "confirmation_values_analyzed": False, "final16_access": False}
    new(TASK / "primary-score-validation-v1.json", value)
    new(PUBLIC / "primary-score-validation-v1.json", value)
    stage("primary-score-validation-v1", [(TASK / "primary-score-validation-v1.json", "inputs/primary-score-validation-v1.json")])
    new(TASK / "evaluator-wrapper-gate-v1.json", {"status": "PASS_ALL_REQUIRED_PRE_VALUE_GATES",
        "primary_score_gate_sha256": sha(TASK / "primary-score-validation-v1.json"),
        "matrix_controller_source_sha256": sha(ROOT / "tools/cf1_matrix_v2.py"), "confirmation_values_analyzed": False})
    matrix.freeze_evaluator()


if __name__ == "__main__":
    guard = start("all-campaign-evaluator-release-v1", 600, 3600,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("all-campaign-evaluator-release-v1", guard, "PASS_FROZEN_EVALUATOR_RELEASE")
    except BaseException:
        finish("all-campaign-evaluator-release-v1", guard, "FAIL")
        raise
