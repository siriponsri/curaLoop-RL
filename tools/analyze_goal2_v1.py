"""Audit immutable Goal2 runs and publish derived descriptive evidence."""

import argparse
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from pathlib import Path

from research.event_time import Event, reconcile
from research.planning_v2.runner import METHODS, ROOT, write


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--canary", action="store_true")
    args = parser.parse_args()
    cfg = json.loads((ROOT / "research/configs/goal_02_real_data_v1.json").read_text())
    rows, ledger = [], []
    for path in sorted((args.input / "runs").glob("*.json")):
        data = path.read_bytes()
        run = json.loads(data)
        if run["status"] != "COMPLETE":
            raise ValueError("Retained incomplete/failed run: " + path.name)
        events = tuple(Event(**e) for e in run["snapshot"]["events"])
        calculated = reconcile(events, cfg["budget"], cfg["deadline"])
        if calculated != run["metrics"]:
            raise ValueError("Event-to-metric mismatch: " + path.name)
        if not run["restoration_verified"]:
            raise ValueError("Restore failure.")
        attempts = args.input / "attempts" / path.name
        marker = json.loads(attempts.read_text())
        if (
            marker["config_sha256"]
            != hashlib.sha256(
                (ROOT / "research/configs/goal_02_real_data_v1.json").read_bytes()
            ).hexdigest()
        ):
            raise ValueError("Attempt config mismatch.")
        decision = run["decisions"]
        row = {
            "run_id": path.stem,
            "assay": run["assay"],
            "seed": run["seed"],
            "condition": run["condition"],
            "method": run["method"],
            **calculated,
            "initial_active_count": run["initial_active_count"],
            "decisions": len(decision),
            "waits": sum(not d["chosen"] for d in decision),
            "fallback_decisions": sum(d["fallback_reason"] is not None for d in decision),
            "wall_seconds": run["wall_seconds"],
            "cpu_seconds": run["cpu_seconds"],
            "policy_seconds": sum(d["policy_seconds"] for d in decision),
            "model_seconds": sum(d["model_seconds"] for d in decision),
            "bound_seconds": sum(d.get("bound_seconds", 0) for d in decision),
            "rollout_seconds": sum(d.get("rollout_seconds", 0) for d in decision),
            "nodes": sum(d.get("nodes", 0) for d in decision),
            "root_actions": sum(len(d.get("actions", [])) for d in decision),
            "pruned_actions": sum(d.get("pruned", 0) for d in decision),
            "schedule_sha256": run["schedule_sha256"],
        }
        rows.append((row, run))
        ledger.append(
            {
                "file": path.name,
                "sha256": hashlib.sha256(data).hexdigest(),
                "attempt_sha256": hashlib.sha256(attempts.read_bytes()).hexdigest(),
                "bytes": len(data),
            }
        )
    expected = len(METHODS) if args.canary else cfg["expected_runs"]
    if len(rows) != expected:
        raise ValueError(f"Expected {expected} runs, found {len(rows)}.")
    groups = defaultdict(dict)
    for row, run in rows:
        groups[(row["assay"], row["seed"], row["condition"])][row["method"]] = (row, run)
    pairs, matched = [], 0
    for key, arms in groups.items():
        if set(arms) != set(METHODS):
            raise ValueError("Missing/duplicate matched arm.")
        if len({r[0]["schedule_sha256"] for r in arms.values()}) != 1:
            raise ValueError("Unmatched operational realization.")
        if len({tuple(r[1]["initial_ids"]) for r in arms.values()}) != 1:
            raise ValueError("Unmatched initial labels.")
        reference = arms["rollout"]
        for method in ("cardinality_pruned", "content_pruned"):
            row, run = arms[method]
            if run["snapshot"] != reference[1]["snapshot"] or [
                d["chosen"] for d in run["decisions"]
            ] != [d["chosen"] for d in reference[1]["decisions"]]:
                raise ValueError("Pruning changed a scientific decision/outcome.")
            matched += 1
        base = arms["posterior_mean"][0]
        for method, (row, _) in arms.items():
            pairs.append(
                {
                    "assay": key[0],
                    "seed": key[1],
                    "condition": key[2],
                    "method": method,
                    "new_hit_difference_vs_posterior_mean": row["new_hits"] - base["new_hits"],
                }
            )
    summaries = []
    for method, condition in ((m, c) for m in METHODS for c in cfg["conditions"]):
        selected = [r for r, _ in rows if r["method"] == method and r["condition"] == condition]
        if not selected:
            continue
        deltas = [
            p["new_hit_difference_vs_posterior_mean"]
            for p in pairs
            if p["method"] == method and p["condition"] == condition
        ]
        summaries.append(
            {
                "method": method,
                "condition": condition,
                "runs": len(selected),
                "mean_new_hits": statistics.mean(r["new_hits"] for r in selected),
                "mean_paired_difference_vs_posterior_mean": statistics.mean(deltas),
                "paired_difference_min": min(deltas),
                "paired_difference_max": max(deltas),
                "wins": sum(d > 0 for d in deltas),
                "ties": deltas.count(0),
                "losses": sum(d < 0 for d in deltas),
                **{
                    k: sum(r[k] for r in selected)
                    for k in (
                        "wall_seconds",
                        "cpu_seconds",
                        "policy_seconds",
                        "model_seconds",
                        "bound_seconds",
                        "rollout_seconds",
                        "nodes",
                        "root_actions",
                        "pruned_actions",
                        "waits",
                        "fallback_decisions",
                    )
                },
            }
        )
    args.output.mkdir(parents=True, exist_ok=True)
    for name, values in (
        ("metrics.csv", [r for r, _ in rows]),
        ("paired-effects.csv", pairs),
        ("method-summary.csv", summaries),
    ):
        path = args.output / name
        if path.exists():
            raise FileExistsError(path)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(values[0]))
            writer.writeheader()
            writer.writerows(values)
    write(args.output / "run-ledger.json", ledger)
    write(
        args.output / "analysis.json",
        {
            "status": "PASS",
            "complete_runs": len(rows),
            "failed_runs": 0,
            "matched_groups": len(groups),
            "exact_pruning_pair_checks": matched,
            "zero_active_initial_groups": sum(
                arms["rollout"][0]["initial_active_count"] == 0 for arms in groups.values()
            ),
            "total_run_wall_seconds": sum(r["wall_seconds"] for r, _ in rows),
            "total_cpu_seconds": sum(r["cpu_seconds"] for r, _ in rows),
            "summaries": summaries,
            "uncertainty": "Descriptive paired ranges and task/seed rows; three exposed correlated endpoints do not justify population confidence intervals or equivalence",
            "final_evaluation": False,
        },
    )
    print(json.dumps({"runs": len(rows), "matched_groups": len(groups), "pruning_checks": matched}))


if __name__ == "__main__":
    main()
