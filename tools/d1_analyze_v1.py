"""Analyze only authenticated frozen D1 reuse entries, never raw/final payloads."""
# ruff: noqa: E402 -- repository-only CLI bootstraps the source import path.

import csv
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.analysis import balanced, pair, summarize
from research.d1_v1.common import (
    OLD,
    PUBLIC,
    TASK,
    finish_job,
    new,
    read,
    save_ledger,
    sha,
    start_job,
)


def main():
    guard = start_job("analysis")
    try:
        freeze = read(TASK / "reuse-freeze-v1.json")
        support = read(PUBLIC / "support-admission-v1.json")
        assert sha(TASK / "reuse-freeze-v1.json") == support["freeze_sha256"]
        assert all(sha(ROOT / name) == expected for name, expected in freeze["pins"].items())
        assert all(sha(ROOT / item["path"]) == item["sha256"] for item in freeze["analysis_sources"])
        ledger = read(TASK / "ledger.json")
        ledger["scientific_outcome_analysis_started"] = True
        ledger["reuse_freeze_sha256"] = sha(TASK / "reuse-freeze-v1.json")
        save_ledger(ledger)
        groups = defaultdict(dict)
        controls = []
        for entry in freeze["entries"]:
            job = entry["job"]
            folder = OLD / "remote-return/files/jobs" / job
            result, trace, resource = (read(folder / name) for name in ("result.json", "trace-private.json", "resource.json"))
            assert result["status"].startswith("PASS") and resource["status"] == "PASS"
            assert not result["cpu_violation"] and result["assigned_B"] == 32
            assert all(result["spec"][k] == v for k, v in entry["arguments"].items())
            if entry["handler"] == "branch":
                spec = result["spec"]
                key = (spec["prefix_job"], spec["snapshot"], spec["regime"])
                assert spec["forced"] not in groups[key], "DUPLICATE_BRANCH"
                groups[key][spec["forced"]] = {"result": result, "trace": trace, "resource": resource}
            else:
                controls.append({"component": result["component"], "task_id": result["task_id"],
                                 "n0": result["spec"]["n0"], "seed": result["spec"]["seed"],
                                 "arm": result["spec"]["policy"], "hits": result["new_positives"],
                                 "cpu": result["scientific_cpu_seconds"],
                                 "parameter": result["spec"].get("parameter")})
        rows = []
        for (prefix, snapshot, regime), branches in sorted(groups.items()):
            first = pair(branches, snapshot)
            base = branches["REUSE"]["result"]
            assert all(row["result"]["branch_features"] == base["branch_features"] for row in branches.values())
            features = base["branch_features"]
            for left, right in (("UPDATE", "REUSE"), ("PLAN", "UPDATE"), ("PLAN", "REUSE")):
                a, b = branches[left], branches[right]
                fa, fb = first[left], first[right]
                supported = bool(fa and fb and fa["actual_operation"] == left and fb["actual_operation"] == right)
                reason = "SUPPORTED" if supported else ("NO_FIRST_DELIVERY" if not (fa and fb) else
                            "FIRST_ACTUAL_" + fa["actual_operation"] + "_VS_" + fb["actual_operation"])
                rows.append({
                    "component": base["component"], "task_id": base["task_id"], "prefix": prefix,
                    "snapshot": snapshot, "n0": base["spec"]["n0"], "regime": regime,
                    "contrast": left + "-" + right, "assigned_C": base["assigned_C"],
                    "hit_delta": a["result"]["new_positives"] - b["result"]["new_positives"],
                    "cpu_delta": a["result"]["scientific_cpu_seconds"] - b["result"]["scientific_cpu_seconds"],
                    "process_cpu_delta": a["resource"]["cpu_seconds"] - b["resource"]["cpu_seconds"],
                    "delivery_delta": a["result"]["new_deliveries"] - b["result"]["new_deliveries"],
                    "executed_support": supported, "support_reason": reason,
                    "choice_changed": bool(supported and fa["candidate_index"] != fb["candidate_index"]),
                    "stale_labels": round(features[7] * (base["spec"]["n0"] + 32)),
                    "remaining_assays": 32 - snapshot, "cached_margin": features[8],
                    "recent_brier": features[12],
                })
        assert len(groups) == 48 and len(rows) == 144
        # Aggregate-only public outputs never include candidate IDs/labels/traces.
        summary = summarize(rows)
        context = []
        for variable, predicates in {
            "stale_labels": [("<4", lambda row: row["stale_labels"] < 4), (">=4", lambda row: row["stale_labels"] >= 4)],
            "remaining_assays": [("16", lambda row: row["remaining_assays"] == 16), ("24", lambda row: row["remaining_assays"] == 24)],
            "cached_margin": [("<=0.05", lambda row: row["cached_margin"] <= .05), (">0.05", lambda row: row["cached_margin"] > .05)],
            "recent_brier": [("<=0.25", lambda row: row["recent_brier"] <= .25), (">0.25", lambda row: row["recent_brier"] > .25)],
        }.items():
            for label, predicate in predicates:
                selected = [row for row in rows if row["executed_support"] and predicate(row)]
                context.append({"variable": variable, "bin": label, "summary": summarize(selected)})
        control_summary = {}
        index = {(r["component"], r["task_id"], r["n0"], r["seed"], r["arm"]): r for r in controls}
        assert len(index) == len(controls) == 180
        for arm in ("G1", "Gk", "T"):
            selected = [r for r in controls if r["arm"] == arm]
            contrasts = []
            for row in selected:
                g1 = index[row["component"], row["task_id"], row["n0"], row["seed"], "G1"]
                contrasts.append(dict(row, delta_hits=row["hits"] - g1["hits"], delta_cpu=row["cpu"] - g1["cpu"]))
            hit, cpu = balanced(selected, "hits"), balanced(selected, "cpu")
            g1_cpu = balanced([r for r in controls if r["arm"] == "G1"], "cpu")["mean"]
            delta = balanced(contrasts, "delta_hits")
            control_summary[arm] = {"hits": hit, "cpu_seconds": cpu, "hit_delta_vs_G1": delta,
                                    "cpu_saving_vs_G1": 1 - cpu["mean"] / g1_cpu,
                                    "parameters": sorted({str(r["parameter"]) for r in selected})}
        new(TASK / "paired-state-rows-v1.json", {"rows": rows})
        result = {
            "schema": "curaloop.d1.reuse_results.v1", "status": "PASS_COMPLETE_REUSE_ANALYSIS",
            "scope": freeze["estimates_scope"], "new_independent_replications": 0,
            "states": 24, "components": len({r["component"] for r in rows}),
            "paired_contexts": 48, "branch_units_reused": 144, "main_controls_reused": 180,
            "paired": summary, "context_bins": context, "inherited_controls": control_summary,
            "inherited_controls_are_not_new_fixed_k4_or_frozen_nearest_hit": True,
            "full_proposed_H3_catalogue": "NOT_RUN",
            "ranking_change": "NOT_IDENTIFIED_FROM_TRACE",
            "new_molecular_units": 0, "final_outcomes_open": False,
            "uncertainty": "descriptive fixed-cohort ranges; one MIX seed; no population CI or independent confirmation",
        }
        new(PUBLIC / "reuse-results-v1.json", result)
        with (PUBLIC / "paired-summary-v1.csv").open("x", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["regime", "contrast", "assigned_states", "supported_states", "mean_delta_hits", "mean_delta_cpu", "changed_first_choices"])
            for regime, contrasts in summary.items():
                for contrast, row in contrasts.items():
                    writer.writerow([regime, contrast, row["assigned_states"], row["supported_states"],
                                     row["assigned_hit_effect"]["mean"], row["assigned_cpu_effect_seconds"]["mean"], row["action_changes"]])
        finish_job("analysis", guard, "PASS")
        print({"status": result["status"], "paired": summary, "inherited_controls": control_summary})
    except BaseException:
        finish_job("analysis", guard, "FAIL")
        raise


if __name__ == "__main__":
    main()
