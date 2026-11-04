"""Hierarchical paired-difference sensitivity, never reads candidate outcomes."""

import csv
import hashlib
import json
import math
import time
from datetime import datetime, timezone
from importlib.metadata import version
from itertools import product
from pathlib import Path

import numpy as np
from scipy.stats import t
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[2]
PACKET = ROOT / "docs/evidence/design-preparation-20261104-v1"
CONFIG = ROOT / "research/configs/design_sensitivity_v1.json"


def theoretical_variance(k, q, m, profile):
    return (
        profile["sd_family"] ** 2 / k
        + profile["sd_task"] ** 2 / (k * q)
        + profile["sd_paired_seed"] ** 2 / (k * q * m)
    )


def family_means(rng, n, k, q, m, profile, distribution):
    # Paired arm difference has its own SD; no spurious factor of two.
    f = (
        rng.normal(size=(n, k))
        if distribution == "gaussian"
        else rng.standard_t(4, size=(n, k)) / math.sqrt(2)
    )
    task = rng.normal(size=(n, k, q)).mean(axis=2)
    # Gaussian mean of q*m independent paired repeats, conditional on family/task.
    residual_mean = rng.normal(size=(n, k)) / math.sqrt(q * m)
    return (
        profile["sd_family"] * f
        + profile["sd_task"] * task
        + profile["sd_paired_seed"] * residual_mean
    )


def summarize(values, true_effect, alpha=0.05):
    n, k = values.shape
    mean = values.mean(axis=1) + true_effect
    se = values.std(axis=1, ddof=1) / math.sqrt(k)
    lcb = mean - t.ppf(1 - alpha, k - 1) * se
    half = t.ppf(0.975, k - 1) * se
    p = float(np.mean(lcb > 0))
    row = {
        "true_effect_hits_hypothetical": true_effect,
        "prob_one_sided_lcb_gt_zero": p,
        "monte_carlo_se_detection": math.sqrt(p * (1 - p) / n),
        "two_sided_95_coverage": float(np.mean(np.abs(mean - true_effect) <= half)),
        "median_95_halfwidth_hits": float(np.median(half)),
        "p90_95_halfwidth_hits": float(np.quantile(half, 0.9)),
    }
    for margin in (0.5, 1.0, 2.0):
        suffix = str(margin).replace(".", "_")
        row["prob_lcb_gt_margin_" + suffix] = float(np.mean(lcb > margin))
        row["prob_halfwidth_le_half_margin_" + suffix] = float(np.mean(half <= margin / 2))
    return row


def csv_write(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def measured_runtime():
    samples = []
    for name in ("ncats-reproduction-20261104-v1", "ncats-gaussian-development-20261104-v1"):
        folder = ROOT / "docs/evidence" / name / "runs"
        ledger = json.loads((folder / "ledger.json").read_text())
        for run_id, entry in ledger["attempts"].items():
            raw = (folder / (run_id + ".json")).read_bytes()
            assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
            run = json.loads(raw)
            if run["status"] == "COMPLETE":
                samples.append(run["attempt_wall_seconds"])
    return {
        "measured_runs": len(samples),
        "median_seconds": float(np.median(samples)),
        "p95_seconds": float(np.quantile(samples, 0.95)),
        "scope": "Same host, 600 compounds, observed methods; per-attempt time, not a future runtime guarantee",
    }


def development_uncertainty():
    old = json.loads(
        (ROOT / "docs/evidence/ncats-development-20261104-v1/results/results.json").read_text()
    )
    gp = json.loads(
        (
            ROOT / "docs/evidence/ncats-gaussian-development-20261104-v1/results/results.json"
        ).read_text()
    )
    rows = []
    for name, points in (
        ("similarity_penalty", old["pending_pairs"]),
        ("gaussian_covariance", gp["pairs"]),
    ):
        by_task = {
            a: [
                p["pending_minus_blind_hits"]
                for p in points
                if p["condition"] == "heterogeneous" and p["assay"] == a
            ]
            for a in ("ahr", "pparg", "p53")
        }
        means = [float(np.mean(v)) for v in by_task.values()]
        rows.append(
            {
                "contrast": name,
                "paired_values_by_development_endpoint": by_task,
                "distinct_endpoints": 3,
                "paired_seeds_each": 3,
                "source_panels": 1,
                "mean_of_endpoint_means": float(np.mean(means)),
                "sample_sd_endpoint_means": float(np.std(means, ddof=1)),
                "leave_one_endpoint_out_means": [
                    float(np.mean(means[:i] + means[i + 1 :])) for i in range(3)
                ],
                "population_confidence_interval": None,
                "reason": "Three correlated/exposed endpoints, one shared source panel; between-source variance unidentifiable. Zero sample variance is not practical equivalence or a zero variance prior.",
            }
        )
    return rows


def main():
    started, cpu = time.perf_counter(), time.process_time()
    cfg = json.loads(CONFIG.read_text())
    assert (
        cfg["primary_material_margin_selected"] is None
        and not cfg["new_outcome_values_permitted"]
        and not cfg["final_execution_permitted"]
    )
    out = PACKET / "simulation"
    if out.exists():
        raise ValueError("Keep all prior simulations; use a new version, not an overwrite.")
    out.mkdir(parents=True)
    rows, digests = [], []
    n = cfg["monte_carlo_replicates"]
    with threadpool_limits(1):
        for index, (k, q, m, profile_name, distribution) in enumerate(
            product(
                cfg["families"],
                cfg["tasks_per_family"],
                cfg["paired_seeds_per_task"],
                cfg["variance_profiles"],
                cfg["family_distributions"],
            )
        ):
            if time.perf_counter() - started > cfg["max_simulation_wall_seconds"]:
                raise RuntimeError(
                    "Simulation cap reached; preserve partial evidence rather than select successful scenarios."
                )
            profile = cfg["variance_profiles"][profile_name]
            rng = np.random.default_rng(np.random.SeedSequence([cfg["seed"], index]))
            values = family_means(rng, n, k, q, m, profile, distribution)
            base = {
                "families": k,
                "tasks_per_family": q,
                "independent_family_df": k - 1,
                "tasks": k * q,
                "paired_seeds_per_task": m,
                "profile": profile_name,
                "family_distribution": distribution,
                **profile,
                "replicates": n,
                "theoretical_design_se": math.sqrt(theoretical_variance(k, q, m, profile)),
            }
            digests.append(
                {
                    **base,
                    "rng_child_index": index,
                    "float64_zero_effect_family_mean_array_sha256": hashlib.sha256(
                        values.tobytes()
                    ).hexdigest(),
                }
            )
            for effect in cfg["true_mean_effects_hits"]:
                rows.append({**base, **summarize(values, effect, cfg["alpha_one_sided"])})
    csv_write(out / "all-sensitivity.csv", rows)
    runtime = measured_runtime()
    resource_rows = []
    for k, q, m, methods in product(
        cfg["families"],
        cfg["tasks_per_family"],
        cfg["paired_seeds_per_task"],
        cfg["method_counts_for_resource_sensitivity"],
    ):
        runs = k * q * m * methods * cfg["conditions_for_resource_sensitivity"]
        for label, seconds in (
            ("measured_median", runtime["median_seconds"]),
            ("measured_p95", runtime["p95_seconds"]),
            ("unmeasured_5s_stress", 5),
            ("unmeasured_15s_stress", 15),
        ):
            hours = runs * seconds * cfg["fixed_overhead_multiplier_assumption"] / 3600
            resource_rows.append(
                {
                    "families": k,
                    "tasks": k * q,
                    "paired_seeds": m,
                    "methods": methods,
                    "conditions": 2,
                    "runs": runs,
                    "runtime_assumption": label,
                    "seconds_per_attempt": seconds,
                    "overhead_multiplier_assumed": 1.2,
                    "estimated_serial_CPU_hours": hours,
                    **{
                        f"fits_hypothetical_{b}h_budget": hours <= b
                        for b in cfg["hypothetical_resource_budgets_cpu_hours"]
                    },
                }
            )
    csv_write(out / "resource-sensitivity.csv", resource_rows)
    summary = {
        "status": "PASS_PREPARATORY_SIMULATION_ONLY",
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": hashlib.sha256(CONFIG.read_bytes()).hexdigest(),
        "config": cfg,
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "versions": {p: version(p) for p in ("numpy", "scipy", "threadpoolctl")},
        "scenario_rows": len(rows),
        "design_variance_distribution_cells": len(digests),
        "runtime_evidence": runtime,
        "development_uncertainty": development_uncertainty(),
        "hypothesis": "D_fts=delta+family_offset+task_offset+paired_seed_error; equal family weights; family df K-1",
        "limitations": "Continuous difference approximation; not calibrated assay counts/prevalence. Heavy-family t4 sensitivity, no guaranteed population coverage. Profiles/margins/budgets hypothetical, not fitted/chosen from development outcomes.",
        "family_array_digests": digests,
        "wall_seconds": time.perf_counter() - started,
        "process_cpu_seconds": time.process_time() - cpu,
        "final_threshold_selected": None,
        "final_execution": False,
        "candidate_outcomes_read": False,
    }
    (out / "simulation-receipt.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in summary.items()
                if k not in ("config", "family_array_digests", "development_uncertainty")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
