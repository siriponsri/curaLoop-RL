"""ENG-01: reconcile preserved replay and run a tiny unchanged-engine regression."""

import argparse
import json
import platform
import time
from pathlib import Path

from curaloop.domain import Event, Scenario
from curaloop.evaluation import metrics_from_events
from curaloop.learning import load_checkpoint
from curaloop.service import compare


def verify() -> dict:
    root = Path(__file__).resolve().parents[1]
    original = json.loads((root / "docs/evidence/hiv-benchmark/benchmark.json").read_text())
    recorded = {}
    for run in original["runs"]:
        cfg = run["manifest"]["scenario_config"]
        recomputed = metrics_from_events(
            tuple(Event(**e) for e in run["events"]), cfg["budget_units"], cfg["assay_cost_units"]
        )
        assert recomputed == run["metrics"], run["manifest"]["run_id"]
        policy = run["manifest"]["policy_id"]
        if policy in ("q_learning", "contextual_bandit"):
            stats = recorded.setdefault(policy, {"requests": 0, "fallback_requests": 0, "runs": 0})
            stats["runs"] += 1
            stats["requests"] += recomputed["controller_requests"]
            stats["fallback_requests"] += recomputed["controller_fallback_requests"]
    assert len(original["runs"]) == 50
    assert all(
        s == {"runs": 10, "requests": 300, "fallback_requests": 300} for s in recorded.values()
    )
    hashes = {policy: load_checkpoint(policy)["checkpoint_sha256"] for policy in recorded}
    started = time.perf_counter()
    scenario = Scenario(
        dataset="hiv_moleculenet_replay_v1",
        seed=42,
        candidate_count=1200,
        initial_count=48,
        budget_units=2,
        batch_size=2,
        delay_steps=2,
    )
    fresh = compare(scenario, ("greedy", "q_learning", "contextual_bandit"))
    for run in fresh:
        metrics = run["metrics"]
        assert (
            metrics["spent_units"] == 2
            and metrics["reserved_units"] == metrics["pending_assays"] == 0
        )
        assert metrics["confirmed_hits"] <= metrics["delivered_assays"] == 2
    return {
        "status": "PASS",
        "scope": "Recorded historical ledger reconciliation plus a fresh two-assay regression; not a new multi-target study",
        "python": platform.python_version(),
        "recorded_runs_reconciled": len(original["runs"]),
        "recorded_controller_usage": recorded,
        "checkpoint_hashes": hashes,
        "fresh_smoke_compute_seconds": time.perf_counter() - started,
        "fresh_runs": fresh,
        "interpretation": "Historical all-fallback evidence is retained. Fresh usage counts are in each run; no transfer claim follows.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        "PASS: 50 preserved ledgers reconciled; 3 fresh independent two-assay campaigns completed."
    )
    for run in result["fresh_runs"]:
        m = run["metrics"]
        print(
            f"{run['manifest']['policy_id']}: hits={m['confirmed_hits']}; requests={m['controller_requests']}; fallback={m['controller_fallback_requests']}"
        )


if __name__ == "__main__":
    main()
