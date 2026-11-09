# Append-only adaptation of preserved matrix-v1 source SHA256 266caaf4f3cf3a17133e53d9040b3b954593de14f90bf458cd4d87ae5d11432e
"""Cost-only release of the unchanged CF1 five-seed baseline/portfolio matrix."""
# ruff: noqa: E402

import itertools
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    PUBLIC,
    TASK,
    authority,
    finish,
    new,
    read,
    save,
    sha,
    start,
)
from tools import cf1_science_v1 as science
from tools.cf1_stage_v1 import stage

SEEDS = (90101, 90113, 90133, 90149, 90163)
RANKERS = ("random", "primary_score", "mvsa", "gbm", "rf", "nearest_primary")
OPERATORS = ("top_ranked", "cluster_round_robin", "classical_max_min")


def selection_calibration():
    rows = read(TASK / "feature-manifests-v1.json")["campaigns"]
    row = max(rows, key=lambda r: r["universe_size"])
    science.book("selection-cost-calibration-v1", "selection_calibration", 180,
                 "admission_and_calibration", extra={"campaign": row["campaign"]})
    assert science.remote.settle("selection-cost-calibration-v1", science.dispatch("selection-cost-calibration-v1")) == "PASS"


def plan():
    _, ledger = authority()
    features = read(TASK / "feature-manifests-v1.json")["campaigns"]
    calibration = read(TASK / "jobs/selection-cost-calibration-v1/result.json")
    assert calibration["status"] == "PASS_SELECTION_COST_CALIBRATION_NO_VALUES"
    fits, costs, cells = [], [], []
    for row in features:
        pair = row["campaign"].replace("/", "-")
        for method in ("mvsa", "rf"):
            name = "first-seed-" + pair + "-" + method + "-90101"
            result = read(TASK / "jobs" / name / "result.json")
            assert ledger["bookings"][name]["status"] == "PASS"
            assert result["status"] == "PASS_PRIMARY_ONLY_RANKER" and not result["confirmation_values_analyzed"]
            assert result["measured_cgroup_memory_peak_bytes"] < 4294967296
            if method == "mvsa":
                assert result["details"]["source_reproduction"] == "PASS_FULL_PRIMARY_SCORE_CONCORDANCE"
            cpu = math.ceil(max(60, 1.75 * result["whole_cgroup_cpu_seconds_at_result"] + 30))
            costs.append({"campaign": row["campaign"], "ranker": method,
                          "first_seed_cpu_seconds": result["whole_cgroup_cpu_seconds_at_result"],
                          "first_seed_memory_peak_bytes": result["measured_cgroup_memory_peak_bytes"],
                          "remaining_unit_cap_seconds": cpu})
            for seed in SEEDS[1:]:
                key = pair + "-" + method + "-" + str(seed)
                fits.append({"name": "matrix-fit-" + key, "handler": "fit", "cpu": cpu,
                    "bucket": "features_and_baseline_reproduction", "extra": {
                        "campaign": row["campaign"], "ranker": method, "seed": seed, "output_name": key}})
        for seed, ranker, operator, budget in itertools.product(SEEDS, RANKERS, OPERATORS, row["budgets"]):
            cells.append({"campaign": row["campaign"], "seed": seed, "ranker": ranker,
                          "operator": operator, "confirmation_count": budget})
    # Largest-U calibration evaluates all three operators for five seeds and one
    # ranker. Six times that cost, with 3x headroom and startup, bounds a campaign.
    portfolio_cap = math.ceil(max(180, 18 * calibration["whole_cgroup_cpu_seconds_at_result"] + 60))
    baseline_added = sum(r["cpu"] for r in fits)
    portfolio_added = len(features) * portfolio_cap
    retained = ledger["retained_seconds"]
    assert retained["features_and_baseline_reproduction"] + baseline_added <= ledger["stage_caps_seconds"]["features_and_baseline_reproduction"], "BASELINE_STAGE_RECOST_OWNER_REVIEW"
    assert retained.get("portfolio_comparison", 0) + portfolio_added <= ledger["stage_caps_seconds"]["portfolio_comparison"]
    assert sum(retained.values()) + baseline_added + portfolio_added <= ledger["cpu_cap_seconds"]
    storage = read(TASK / "live-readback-pre-matrix-v1.json")
    assert not storage["jobs"], "CALIBRATION_WORKER_STILL_ACTIVE"
    assert len(storage["model_directories"]) == 12
    # Preserve every first-seed artifact; allow 1.5x that measured size for each
    # remaining seed and a measured opaque gzip-size forecast for compressed export.
    # This is a measured compression-based forecast, not a future-size guarantee.
    # The complete-return writer separately enforces the actual combined 8GiB cap.
    projected_tree = storage["regular_file_bytes"] + 6 * sum(storage["model_directories"].values()) + 64 * 1024**2
    compression = read(TASK / "jobs/storage-compression-calibration-v1/result.json")
    assert compression["status"] == "PASS_OPAQUE_COMPRESSION_SIZE_CALIBRATION"
    assert not compression["confirmation_values_analyzed"] and not compression["archive_created"]
    assert compression["first_seed_model_bytes"] == sum(storage["model_directories"].values())
    projected_export = compression["independent_gzip_stream_bytes"] + 6 * compression["first_seed_model_gzip_bytes"] + 64 * 1024**2
    projected_with_export = projected_tree + projected_export
    assert projected_with_export < 8 * 1024**3, "MEASURED_STORAGE_PROFILE_REQUIRES_OWNER_RECOST"
    assert len(fits) == 48 and len(cells) <= 2700
    # Independent primary-only units are ordered by their cost envelope to keep
    # the three fixed-core waves balanced; no outcome/performance ordering.
    fits.sort(key=lambda r: (-r["cpu"], r["name"]))
    value = {"status": "PASS_PRIMARY_ONLY_COMPLETE_MATRIX_COST_RELEASE", "cost_rule": "ceil(max(60,1.75*campaign_method_first_seed_whole_cpu+30))",
             "execution_order": "descending pre-outcome CPU cap, then immutable job name; nonoverlapping three-core waves",
             "cost_observations": costs, "remaining_fits": fits, "remaining_fit_count": len(fits),
             "remaining_fit_cap_seconds": baseline_added, "portfolio_unit_cap_seconds": portfolio_cap,
             "portfolio_total_cap_seconds": portfolio_added,
             "projected_retained_cpu_seconds": sum(retained.values()) + baseline_added + portfolio_added,
             "projected_artifacts_and_compressed_return_bytes": projected_with_export,
             "storage_forecast_rule": "current tree + 1.5x first-seed model bytes per remaining seed + 64MiB metadata; measured level-1 gzip streams + 1.5x first-seed compressed model bytes per remaining seed + 64MiB export metadata; actual writer enforces 8GiB",
             "retained_utility_bucket_seconds": 43200, "cell_count": len(cells),
             "confirmation_values_analyzed": False, "source_or_scientific_parameters_changed": False}
    new(TASK / "complete-matrix-cost-release-v2.json", value)
    new(PUBLIC / "complete-matrix-cost-release-v2.json", value)
    matrix = {"status": "FROZEN_BEFORE_CONFIRMATION_VALUES", "cells": cells, "count": len(cells),
              "feature_manifest_sha256": sha(TASK / "feature-manifests-v1.json")}
    new(TASK / "cell-manifest-v1.json", matrix)
    new(PUBLIC / "cell-manifest-v1.json", matrix)
    print({k: v for k, v in value.items() if k not in ("cost_observations", "remaining_fits")})


def remaining_fits():
    value = read(TASK / "complete-matrix-cost-release-v2.json")
    assert value["status"] == "PASS_PRIMARY_ONLY_COMPLETE_MATRIX_COST_RELEASE"
    science.waves(value["remaining_fits"])


def freeze_evaluator():
    _, ledger = authority()
    assert not ledger["confirmation_values_analyzed"]
    value = read(TASK / "complete-matrix-cost-release-v2.json")
    models = []
    for row in read(TASK / "feature-manifests-v1.json")["campaigns"]:
        for method, seed in itertools.product(("mvsa", "rf"), SEEDS):
            key = row["campaign"].replace("/", "-") + "-" + method + "-" + str(seed)
            name = ("first-seed-" if seed == 90101 else "matrix-fit-") + key
            assert ledger["bookings"][name]["status"] == "PASS"
            model = read(TASK / "jobs" / name / "result.json")
            assert model["status"] == "PASS_PRIMARY_ONLY_RANKER" and not model["confirmation_values_analyzed"]
            models.append(model)
    assert len(models) == 60
    ranks = {"status": "PASS_FROZEN_PRIMARY_ONLY_MODELS", "models": models, "model_count": 60,
             "confirmation_values_analyzed": False}
    new(TASK / "rank-manifests-v1.json", ranks)
    new(PUBLIC / "rank-manifests-v1.json", ranks)
    release = {"status": "RELEASE_FROZEN_DEVELOPMENT_EVALUATOR_ONLY", "confirmation_values_released": True,
        "final16_access": False, "new_selector_training": False, "frozen_code_pins": read(TASK / "code-pins-science-v2.json"),
        "feature_manifest_sha256": sha(TASK / "feature-manifests-v1.json"),
        "rank_manifest_sha256": sha(TASK / "rank-manifests-v1.json"),
        "cell_manifest_sha256": sha(TASK / "cell-manifest-v1.json"),
        "cost_release_sha256": sha(TASK / "complete-matrix-cost-release-v2.json"),
        "owner_choice_sha256": sha(TASK / "owner-source-a-v1.json"), "cell_count": value["cell_count"],
        "analysis_protocol_sha256": sha(ROOT / "docs/03_research/LR_CF1_ANALYSIS_FREEZE_V1.md"),
        "mandatory_source_reproduction": "PASS_SIX_CAMPAIGNS_FIVE_SEEDS", "model_count": len(models)}
    new(TASK / "evaluation-release-v1.json", release)
    new(PUBLIC / "evaluation-release-v1.json", release)
    files = [(TASK / (name + ".json"), "inputs/" + name + ".json")
        for name in ("rank-manifests-v1", "cell-manifest-v1", "evaluation-release-v1")]
    files.append((ROOT / "docs/03_research/LR_CF1_ANALYSIS_FREEZE_V1.md", "inputs/analysis-protocol-v1.md"))
    stage("evaluation-release-v1", files)


def portfolios():
    release = read(TASK / "evaluation-release-v1.json")
    assert release["mandatory_source_reproduction"] == "PASS_SIX_CAMPAIGNS_FIVE_SEEDS"
    plan_value = read(TASK / "complete-matrix-cost-release-v2.json")
    specs = [{"name": "portfolio-" + row["campaign"].replace("/", "-"), "handler": "portfolio",
              "cpu": plan_value["portfolio_unit_cap_seconds"], "bucket": "portfolio_comparison",
              "extra": {"campaign": row["campaign"], "output_name": row["campaign"].replace("/", "-")}}
             for row in read(TASK / "feature-manifests-v1.json")["campaigns"]]
    science.waves(specs)
    _, ledger = authority()
    ledger["confirmation_values_analyzed"] = True
    save(ledger)


if __name__ == "__main__":
    action = sys.argv[1]
    actions = {"selection-calibration": selection_calibration, "plan": plan, "remaining-fits": remaining_fits,
               "freeze-evaluator": freeze_evaluator, "portfolios": portfolios}
    assert action in actions
    guard = start("matrix-controller-v2-" + action, 600, 30000,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        actions[action]()
        finish("matrix-controller-v2-" + action, guard, "PASS_MATRIX_" + action.upper())
    except BaseException:
        finish("matrix-controller-v2-" + action, guard, "FAIL")
        raise
