"""Descriptive development summaries with explicit task/seed and failure denominators."""

import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path


def analyze(folder: Path, output: Path):
    ledger = json.loads((folder / "ledger.json").read_text())
    runs = []
    for run_id, entry in ledger["attempts"].items():
        path = folder / (run_id + ".json")
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise ValueError("Run artifact differs from its ledger: " + run_id)
        run = json.loads(path.read_text())
        if run["identity"] != entry["identity"] or run["status"] != entry["status"]:
            raise ValueError("Run identity/status differs from ledger.")
        runs.append(run)
    output.mkdir(parents=True, exist_ok=True)
    grouped = defaultdict(list)
    for run in runs:
        i = run["identity"]
        grouped[(i["assay"], i["condition"], i["method"])].append(run)
    rows = []
    for (assay, condition, method), points in sorted(grouped.items()):
        complete = [r for r in points if r["status"] == "COMPLETE"]
        rows.append(
            {
                "assay": assay,
                "condition": condition,
                "method": method,
                "n_complete": len(complete),
                "n_failed": len(points) - len(complete),
                "mean_new_hits": statistics.mean(r["metrics"]["new_hits"] for r in complete)
                if complete
                else None,
                "mean_delivered": statistics.mean(r["metrics"]["delivered"] for r in complete)
                if complete
                else None,
                "mean_spent": statistics.mean(r["metrics"]["spent"] for r in complete)
                if complete
                else None,
                "mean_reserved": statistics.mean(r["metrics"]["reserved"] for r in complete)
                if complete
                else None,
                "mean_time_area": statistics.mean(
                    r["metrics"]["time_discovery_area"] for r in complete
                )
                if complete
                else None,
                "selector_fallback_requests": sum(
                    r["selector"]["fallback_requests"] for r in complete
                ),
                "fit_successes": sum(r["selector"]["fit_successes"] for r in complete),
                "wall_seconds": sum(r["wall_seconds"] for r in complete),
            }
        )
    pairs = []
    index = {
        (r["identity"]["assay"], r["seed"], r["condition"], r["method"]): r
        for r in runs
        if r["status"] == "COMPLETE"
    }
    for (assay, seed, condition, method), a in sorted(index.items()):
        if method != "greedy" or (assay, seed, condition, "pending_penalty") not in index:
            continue
        b = index[(assay, seed, condition, "pending_penalty")]
        if a["initial_ids"] != b["initial_ids"] or a["schedule_sha256"] != b["schedule_sha256"]:
            raise ValueError("Pending comparison is not matched.")
        same = a["snapshot"]["events"] == b["snapshot"]["events"]
        if condition == "common" and not same:
            raise ValueError(
                "Common-delay exact negative control failed; do not interpret this batch."
            )
        pairs.append(
            {
                "assay": assay,
                "seed": seed,
                "condition": condition,
                "pending_minus_blind_hits": b["metrics"]["new_hits"] - a["metrics"]["new_hits"],
                "same_event_trace": same,
                "blind_hits": a["metrics"]["new_hits"],
                "pending_hits": b["metrics"]["new_hits"],
            }
        )
    summary = {
        "scope": "EXPLORATORY_DEVELOPMENT_ONLY; three correlated endpoints from one public panel, three repeated seeds; not final inference",
        "attempts": len(runs),
        "complete": sum(r["status"] == "COMPLETE" for r in runs),
        "failed": sum(r["status"] != "COMPLETE" for r in runs),
        "config_sha256": ledger["config_sha256"],
        "wall_seconds_including_restore_and_preparation_per_run": ledger["wall_seconds"],
        "process_cpu_seconds": ledger["cpu_seconds"],
        "peak_runner_working_set_bytes": ledger.get("peak_runner_working_set_bytes"),
        "actual_paid_compute_calls": 0,
        "gpu_jobs": 0,
        "monetary_electricity_and_labor_costs": "NOT_MEASURED",
        "task_method_rows": rows,
        "pending_pairs": pairs,
        "zero_initial_active_runs": sum(
            r.get("initial_active_count") == 0 for r in runs if r["status"] == "COMPLETE"
        ),
        "warnings": sum(len(r.get("warnings", [])) for r in runs),
        "final_evaluation": False,
        "learned_controller_evaluated": False,
    }
    for name, items in (("summary.csv", rows), ("pending-pairs.csv", pairs)):
        if items:
            with (output / name).open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(items[0]))
                writer.writeheader()
                writer.writerows(items)
    (output / "results.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: summary[k]
                for k in (
                    "attempts",
                    "complete",
                    "failed",
                    "wall_seconds_including_restore_and_preparation_per_run",
                    "peak_runner_working_set_bytes",
                    "zero_initial_active_runs",
                )
            },
            indent=2,
        )
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.runs, args.output)
