"""Prespecified group-weighted effects, crossed cells and reexecution checks."""

import csv
import json
import statistics
from collections import Counter, defaultdict
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]


def grouped_values(rows, getter):
    grouped = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[row["family_id"]][row["task_id"]].append(getter(row))
    return {group: statistics.mean(statistics.mean(values) for values in assays.values())
            for group, assays in sorted(grouped.items())}


def descriptive_interval(values):
    import numpy as np
    values = np.array(list(values), dtype=float)
    draws = np.random.default_rng(20261105).choice(values, size=(10000, len(values)), replace=True).mean(axis=1)
    return {"mean": float(values.mean()), "group_range": [float(values.min()), float(values.max())],
            "descriptive_group_bootstrap_95_interval": [float(x) for x in np.quantile(draws, [.025, .975])],
            "groups": len(values), "draws": 10000, "seed": 20261105,
            "independent_population_coverage_certified": False}


def paired_group_effects(planner_rows, reference_rows):
    def key(row):
        return row["task_id"], row["seed"], row["operation"]
    left = {key(row): row for row in planner_rows}
    right = {key(row): row for row in reference_rows}
    if len(left) != len(planner_rows) or len(right) != len(reference_rows) or set(left) != set(right):
        raise ValueError("Matched unique campaign pairs required.")
    differences = []
    for identifier, row in right.items():
        if row["family_id"] != left[identifier]["family_id"]:
            raise ValueError("Paired group identity mismatch.")
        differences.append({**row, "difference": left[identifier]["metrics"]["new_hits"] - row["metrics"]["new_hits"]})
    return grouped_values(differences, lambda row: row["difference"])


def compute_pair(screened, dense):
    equal = [d["public_state_sha256"] for d in screened["decisions"]] == [d["public_state_sha256"] for d in dense["decisions"]]
    signature_equal = screened["scientific_sha256"] == dense["scientific_sha256"]
    matched = equal and signature_equal
    wall_ratio = screened["policy_wall_seconds"] / dense["policy_wall_seconds"]
    cpu_ratio = screened["policy_cpu_seconds"] / dense["policy_cpu_seconds"]
    return {"pairing_status": "PASS" if matched else "FAIL_UNMATCHED_STATES_OR_RESULTS",
            "public_states_equal": equal, "scientific_signature_equal": signature_equal,
            "screened_policy_wall_seconds": screened["policy_wall_seconds"], "dense_policy_wall_seconds": dense["policy_wall_seconds"],
            "raw_unqualified_wall_ratio": wall_ratio, "raw_unqualified_cpu_ratio": cpu_ratio,
            "screened_over_dense_wall_ratio": wall_ratio if matched else None,
            "screened_over_dense_cpu_ratio": cpu_ratio if matched else None}


def main():
    from research.benchmark_v3.prepare_features_v2 import sha_file, write_new
    packet = ROOT / "docs/evidence/goal4-20261105-v1"
    output = packet / "results-v1.json"
    if output.exists():
        raise FileExistsError("Preserve all analysis attempts.")
    guard = Guard(packet / "analysis-resources-v1.json", 900, 4*1024**3, 900)
    try:
        from research.study_v1.identity import verify_frozen, verify_selection, RUN_RELATIVE
        from research.study_v1.admin import collect
        protocol = verify_frozen(ROOT)
        selection = verify_selection(ROOT, protocol)
        run = ROOT / RUN_RELATIVE
        allocation = json.loads((run / "allocation.json").read_text())
        seeds, m = allocation["seeds"], selection["selected_hypotheses"]
        development, development_ids = collect(ROOT, "development", protocol, seeds)
        selected = [r for r in development if r["hypotheses"] == m]
        del development
        crossed, crossed_ids = collect(ROOT, "crossed", protocol, seeds, m)
        selected += crossed
        del crossed
        benchmark, benchmark_ids = collect(ROOT, "benchmark", protocol, seeds, m)
        reexecution, reexecution_ids = collect(ROOT, "reexecution", protocol, seeds, m)
        calibration, calibration_ids = collect(ROOT, "calibration", protocol, seeds, m)
        indexed = {(r["task_id"], r["seed"], r["operation"], r["method"]): r for r in selected}
        if len(indexed) != len(selected) or any(r["role"] == "final" for r in selected):
            raise ValueError("Duplicate/forbidden crossed case.")
        if len(selected) != 8*4*len(seeds)*14:
            raise ValueError("Crossed allocation incomplete.")
        cells, contrasts, diagnostics = [], [], []
        for role in ("development", "validation"):
            for op_role in ("familiar", "held_out"):
                cell = [r for r in selected if r["role"] == role and r["operation_role"] == op_role]
                for method in protocol["methods"]:
                    rows = [r for r in cell if r["method"] == method]
                    values = grouped_values(rows, lambda r: r["metrics"]["new_hits"])
                    wall = grouped_values(rows, lambda r: r["policy_wall_seconds"])
                    cpu = grouped_values(rows, lambda r: r["policy_cpu_seconds"])
                    cells.append({"role": role, "operations": op_role, "method": method,
                                  "H_macro": statistics.mean(values.values()), "H_by_group": values,
                                  "policy_wall_seconds_macro": statistics.mean(wall.values()),
                                  "policy_cpu_seconds_macro": statistics.mean(cpu.values()), "campaigns": len(rows)})
                    if method != "event_screened":
                        differences = paired_group_effects([r for r in cell if r["method"] == "event_screened"], rows)
                        contrasts.append({"role": role, "operations": op_role, "contrast": f"event_screened minus {method}",
                                          "group_effects": differences, **descriptive_interval(differences.values())})
        for method in protocol["methods"]:
            rows = [r for r in selected if r["method"] == method]
            decisions = [d["trace"] for r in rows for d in r["decisions"]]
            branches = [b for d in decisions for b in d.get("planning", {}).get("branch_diagnostics", [])]
            reasons = Counter(d["fallback"] for d in decisions if d["fallback"])
            diagnostics.append({"method": method, "campaigns": len(rows), "decisions": len(decisions),
                                "optional_waits": sum(r["optional_waits"] for r in rows),
                                "forced_waits": sum(r["forced_waits"] for r in rows),
                                "fallback_reasons": dict(reasons),
                                "fallback_decision_share": sum(reasons.values())/len(decisions),
                                "branches": len(branches), "dense_fallback_branches": sum(b.get("dense_fallback", False) for b in branches),
                                "exact_refined_candidates": sum(b.get("exact_refined", 0) for b in branches),
                                "eligible_branch_candidates": sum(b.get("eligible", 0) for b in branches),
                                "zero_tail_skipped_branches": sum("kept_by_bounds" not in b for b in branches) if method == "event_screened" else None,
                                "zero_tail_skipped_candidates": sum(b["eligible"] for b in branches if "kept_by_bounds" not in b) if method == "event_screened" else None,
                                "positive_tail_branches": sum("kept_by_bounds" in b for b in branches) if method == "event_screened" else None,
                                "nontrivial_bound_refinements_saved": sum(b["eligible"]-b["exact_refined"] for b in branches if "kept_by_bounds" in b) if method == "event_screened" else None,
                                "maximum_reported_root_gap": max((d.get("planning", {}).get("gap", 0) for d in decisions), default=0),
                                "learned_action_share": 0})
        bench_pairs = []
        grouped_bench = defaultdict(dict)
        for r in benchmark:
            grouped_bench[(r["operation"], r["case"]["repetition"])][r["method"]] = r
        for (operation, repetition), pair in sorted(grouped_bench.items()):
            a, b = pair["event_screened"], pair["event_dense"]
            bench_pairs.append({"operation": operation, "repetition": repetition, **compute_pair(a, b)})
        replay = []
        for r in reexecution:
            original = indexed[(r["task_id"], r["seed"], r["operation"], r["method"])]
            replay.append({"task_id": r["task_id"], "operation": r["operation"], "method": r["method"],
                           "equal": r["scientific_sha256"] == original["scientific_sha256"]})
        calibration_summary = []
        for role in ("development", "validation"):
            rows = [r for r in calibration if r["role"] == role]
            calibration_summary.append({"role": role, "campaigns": len(rows), "initial_only_diagnostic": True,
                "brier_by_group": grouped_values(rows, lambda r: r["brier"]),
                "log_loss_by_group": grouped_values(rows, lambda r: r["log_loss"]),
                "not_calibration_proof_for_adaptive_histories": True})
        compute_matched = all(r["pairing_status"] == "PASS" for r in bench_pairs)
        replay_matched = all(r["equal"] for r in replay)
        integrity_ok = compute_matched and replay_matched
        report = {"status": "PASS_COMPLETE_GOAL4_ANALYSIS" if integrity_ok else "FAIL_SCIENTIFIC_INTEGRITY",
                  "scientific_integrity_gate": "PASS" if integrity_ok else "FAIL",
                  "selected_hypotheses": m, "seeds": seeds,
                  "campaign_counts": {"development_selection": len(development_ids), "crossed_additional": len(crossed_ids),
                    "selected_M_crossed_unique": len(selected), "benchmark": len(benchmark), "reexecution": len(reexecution), "calibration": len(calibration)},
                  "cells": cells, "paired_effects": contrasts, "diagnostics": diagnostics,
                  "matched_compute_pairs": bench_pairs,
                  "matched_compute_all_states_and_signatures_equal": compute_matched,
                  "median_screened_over_dense_wall_ratio": statistics.median(r["screened_over_dense_wall_ratio"] for r in bench_pairs) if compute_matched else None,
                  "reexecution_matches": sum(r["equal"] for r in replay), "reexecution_cases": replay,
                  "calibration": calibration_summary, "final_outcome_use": False,
                  "calibration_per_task_seed": [{k: r[k] for k in ("task_id", "role", "family_id", "seed", "audit_n", "brier", "log_loss", "bins")} for r in calibration],
                  "analysis_source_sha256": sha_file(Path(__file__)), "protocol_sha256": sha_file(ROOT / "research/configs/goal4_protocol_v1.json"),
                  "limitations": ["4development/2validation annotation-connected groups, not certified independent evolutionary families",
                    "Descriptive group bootstrap does not certify population coverage or confirmatory significance",
                    "Potency-derived source labels; simulated IID operations and negligible decision latency",
                    "Residual scaffold/analogue dependence; no chemical OOD claim",
                    "Frozen dense reference still computes zero-tail rows; zero-tail skips are not evidence of useful TV/chi-square bound pruning",
                    "No learned RL controller, clinical efficacy, novel theorem or journal-readiness claim"]}
        write_new(output, report)
        with (packet / "method-cells-v1.csv").open("x", encoding="utf-8", newline="") as handle:
            fields = ["role", "operations", "method", "H_macro", "policy_wall_seconds_macro", "policy_cpu_seconds_macro", "campaigns"]
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(cells)
        guard.finish("PASS" if integrity_ok else "FAIL", reexecution_mismatches=len(replay)-sum(r["equal"] for r in replay))
        print(json.dumps({k: report[k] for k in ("status", "selected_hypotheses", "campaign_counts", "matched_compute_all_states_and_signatures_equal", "median_screened_over_dense_wall_ratio", "reexecution_matches")}, indent=2))
        if not integrity_ok:
            raise SystemExit(2)
    except Exception as error:
        guard.finish("FAIL", sanitized_reason=type(error).__name__)
        print(json.dumps({"status": "FAIL", "exception_type": type(error).__name__}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
