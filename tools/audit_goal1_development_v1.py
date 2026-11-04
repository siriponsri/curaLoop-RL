"""Post-hoc diagnostics from immutable public development logs; no campaigns."""

import argparse
import csv
import hashlib
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STUDIES = {
    "ncats-development-20261104-v1": (108, ("greedy", "pending_penalty")),
    "ncats-gaussian-development-20261104-v1": (54, ("gp_ucb_blind", "gp_ucb_pending")),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def inspect_run(study, run):
    identity = run["identity"]
    decisions = run["decisions"]
    pending = [d for d in decisions if d["pending_ids"]]
    fitted = [d for d in pending if d["fallback_reason"] is None and d["fit_successes_so_far"] > 0]
    chosen = [c for d in decisions for c in d["chosen"]]
    method = identity["method"]
    covariance_reductions = None
    score_penalties = None
    if method.startswith("gp_"):
        covariance_reductions = sum(
            c["gaussian_std"] is not None and c["blind_gaussian_std"] - c["gaussian_std"] > 1e-12
            for c in chosen
        )
    if method in ("greedy", "pending_penalty"):
        score_penalties = sum(
            c["predicted_probability"] is not None
            and c["predicted_probability"] - c["score"] > 1e-12
            for c in chosen
        )
    return {
        "study": study,
        "run_id": run["run_id"],
        **{k: identity[k] for k in ("assay", "seed", "condition", "method")},
        "decision_calls": len(decisions),
        "calls_with_pending": len(pending),
        "fitted_calls_with_pending": len(fitted),
        "fallback_calls_with_pending": sum(d["fallback_reason"] is not None for d in pending),
        "selected_requests": len(chosen),
        "selected_requests_with_reduced_GP_std": covariance_reductions,
        "selected_requests_with_probability_minus_score_positive": score_penalties,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    output = parser.parse_args().output
    if output.exists() or output.with_suffix(".csv").exists():
        raise ValueError("Retain the prior diagnostic; use a new output version.")
    rows, pairs, receipts = [], [], []
    for study, (expected, methods) in STUDIES.items():
        folder = ROOT / "docs/evidence" / study
        ledger_bytes = (folder / "runs/ledger.json").read_bytes()
        ledger = json.loads(ledger_bytes)
        assert len(ledger["attempts"]) == expected
        runs = {}
        for run_id, attempt in ledger["attempts"].items():
            raw = (folder / "runs" / (run_id + ".json")).read_bytes()
            assert sha(raw) == attempt["sha256"]
            run = json.loads(raw)
            assert run["status"] == attempt["status"] == "COMPLETE"
            assert run["identity"] == attempt["identity"]
            identity = run["identity"]
            if identity["method"] in methods:
                key = tuple(identity[k] for k in ("assay", "seed", "condition", "method"))
                assert key not in runs
                runs[key] = run
                rows.append(inspect_run(study, run))
        receipts.append(
            {"study": study, "verified_run_bytes": expected, "ledger_sha256": sha(ledger_bytes)}
        )
        recorded = list(csv.DictReader((folder / "results/pending-pairs.csv").open()))
        assert len(recorded) == 18
        for entry in recorded:
            key = (entry["assay"], int(entry["seed"]), entry["condition"])
            blind, aware = (runs[(*key, method)] for method in methods)
            assert blind["schedule_sha256"] == aware["schedule_sha256"]
            assert blind["initial_ids"] == aware["initial_ids"]
            delta = aware["metrics"]["new_hits"] - blind["metrics"]["new_hits"]
            same = aware["snapshot"]["events"] == blind["snapshot"]["events"]
            assert delta == int(entry["pending_minus_blind_hits"])
            assert same == (entry["same_event_trace"] == "True")
            if key[2] == "common":
                assert same and delta == 0
            pairs.append(
                {
                    "study": study,
                    "assay": key[0],
                    "seed": key[1],
                    "condition": key[2],
                    "delta_hits": delta,
                    "same_event_trace": same,
                }
            )
    groups = defaultdict(list)
    for row in rows:
        groups[(row["study"], row["condition"], row["method"])].append(row)
    counts = (
        "decision_calls",
        "calls_with_pending",
        "fitted_calls_with_pending",
        "fallback_calls_with_pending",
        "selected_requests",
        "selected_requests_with_reduced_GP_std",
        "selected_requests_with_probability_minus_score_positive",
    )
    aggregates = []
    for (study, condition, method), members in sorted(groups.items()):
        assert len(members) == 9
        aggregate = {"study": study, "condition": condition, "method": method, "runs": len(members)}
        for name in counts:
            values = [r[name] for r in members]
            aggregate[name] = sum(values) if all(v is not None for v in values) else None
        if condition == "common":
            assert aggregate["calls_with_pending"] == 0
        aggregates.append(aggregate)
    assert sum(r["selected_requests_with_reduced_GP_std"] or 0 for r in rows) == 89
    output.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "PASS_POST_HOC_DEVELOPMENT_DIAGNOSTIC",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit_before_analysis": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "analysis_source_sha256": sha(Path(__file__).read_bytes()),
        "verified_run_bytes": 162,
        "analyzed_matched_arm_runs": len(rows),
        "verified_pairs": len(pairs),
        "input_receipts": receipts,
        "aggregates": aggregates,
        "pairs": pairs,
        "new_campaigns_or_model_fits": 0,
        "final_assay_outcomes_read": False,
        "limits": "Exposed three-endpoint development logs only. Counts are within-run diagnostics, not independent biological replications. Opportunity counts can differ after trajectories diverge. A fitted call with pending is an opportunity, not proof of nonzero score effect or improved utility. Selected-score changes do not identify the full candidate ranking. No population CI, equivalence or new benefit claim.",
    }
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    with output.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(
        json.dumps(
            {
                "status": result["status"],
                "verified_runs": 162,
                "analyzed_runs": len(rows),
                "aggregates": aggregates,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
