"""Audit and summarize the separate Gaussian development amendment, without fitting."""

import csv
import hashlib
import json
import statistics
from collections import defaultdict
from datetime import datetime, timezone

from research.event_time import Event, reconcile

from .gaussian_runner_v1 import CONFIG, PACKET, source_identity
from .prepare_cohort import ROOT
from .runner import digest, plan, write


def main():
    cfg = json.loads(CONFIG.read_text())
    folder = ROOT / "research/runs/ncats-gaussian-development-20261104-v1"
    ledger = json.loads((folder / "ledger.json").read_text())
    assert (
        ledger["config_sha256"] == digest(cfg)
        and source_identity() == cfg["execution_source_sha256"]
    )
    expected = {}
    for assay, seed, condition, method in plan(cfg):
        i = dict(
            config_sha256=digest(cfg), assay=assay, seed=seed, condition=condition, method=method
        )
        expected[digest(i)[:24]] = i
    assert len(expected) == 54 and set(expected) == set(ledger["attempts"]), (
        "Incomplete/extra allocation"
    )
    runs, artifacts = [], {}
    for run_id, entry in ledger["attempts"].items():
        raw = (folder / (run_id + ".json")).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        r = json.loads(raw)
        assert r["identity"] == entry["identity"] == expected[run_id]
        assert r["status"] == entry["status"] and r["status"] in ("COMPLETE", "FAILED")
        assert r["execution"]["execution_source_sha256"] == source_identity()
        if r["status"] == "COMPLETE":
            events = [Event(**e) for e in r["snapshot"]["events"]]
            m = reconcile(tuple(events), cfg["budget"], cfg["deadline"])
            assert m == r["snapshot"]["metrics"] and all(r["metrics"][k] == v for k, v in m.items())
            assert r["restoration_verified"]
            accepted = [e.candidate_id for e in events if e.kind == "REQUEST_ACCEPTED"]
            assert len(accepted) == len(set(accepted)) == r["selector"]["selected_requests"]
            assert not set(accepted) & set(r["initial_ids"])
            assert (
                sum(r["selector"]["fallback_reasons"].values())
                == r["selector"]["fallback_requests"]
            )
            for trace in r["decisions"]:
                known = [
                    e
                    for e in events
                    if e.time <= trace["time"] and e.kind in ("INITIAL_LABEL", "RESULT_DELIVERED")
                ]
                requested = {
                    e.candidate_id
                    for e in events
                    if e.kind == "REQUEST_ACCEPTED" and e.time < trace["time"]
                }
                settled = {
                    e.candidate_id
                    for e in events
                    if e.kind == "RESULT_DELIVERED" and e.time <= trace["time"]
                }
                assert trace["known_labels"] == len(known) and trace["known_actives"] == sum(
                    e.active for e in known
                )
                assert set(trace["pending_ids"]) == requested - settled
                for c in trace["chosen"]:
                    assert c["predicted_probability"] is None
                    if c["gaussian_std"] is not None:
                        assert c["gaussian_std"] <= c["blind_gaussian_std"] + 1e-8
        runs.append(r)
        artifacts[run_id + ".json"] = raw
    complete = [r for r in runs if r["status"] == "COMPLETE"]
    index = {
        tuple(r["identity"][k] for k in ("assay", "seed", "condition", "method")): r
        for r in complete
    }
    old_folder = ROOT / "docs/evidence/ncats-development-20261104-v1/runs"
    old_ledger = json.loads((old_folder / "ledger.json").read_text())
    old_index = {}
    for run_id, entry in old_ledger["attempts"].items():
        raw = (old_folder / (run_id + ".json")).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == entry["sha256"]
        r = json.loads(raw)
        if r["identity"]["method"] == "greedy":
            old_index[tuple(r["identity"][k] for k in ("assay", "seed", "condition"))] = r
    comparisons, pairs = [], []
    groups = defaultdict(list)
    for key, r in sorted(index.items()):
        assay, seed, condition, method = key
        old = old_index[key[:3]]
        assert (
            r["initial_ids"] == old["initial_ids"]
            and r["schedule_sha256"] == old["schedule_sha256"]
        )
        assert r["snapshot"]["resource_sha256"] == old["snapshot"]["resource_sha256"]
        groups[(assay, condition, method)].append(r)
        comparisons.append(
            {
                "assay": assay,
                "seed": seed,
                "condition": condition,
                "method": method,
                **r["metrics"],
                "initial_actives": r["initial_active_count"],
                "selected_requests": r["selector"]["selected_requests"],
                "selector_fallback_requests": r["selector"]["fallback_requests"],
                "fit_successes": r["selector"]["fit_successes"],
                "prediction_calls": r["selector"]["prediction_calls"],
                "attempt_wall_seconds": r["attempt_wall_seconds"],
                "lr_greedy_hits": old["metrics"]["new_hits"],
                "gp_minus_lr_hits_descriptive_only": r["metrics"]["new_hits"]
                - old["metrics"]["new_hits"],
            }
        )
        if method == "gp_ucb_blind" and (*key[:3], "gp_ucb_pending") in index:
            b = index[(*key[:3], "gp_ucb_pending")]
            assert (
                r["initial_ids"] == b["initial_ids"]
                and r["schedule_sha256"] == b["schedule_sha256"]
            )
            same = r["snapshot"]["events"] == b["snapshot"]["events"]
            if condition == "common":
                assert same, "Common-delay exact negative control failed"
            pairs.append(
                {
                    "assay": assay,
                    "seed": seed,
                    "condition": condition,
                    "blind_hits": r["metrics"]["new_hits"],
                    "pending_hits": b["metrics"]["new_hits"],
                    "pending_minus_blind_hits": b["metrics"]["new_hits"] - r["metrics"]["new_hits"],
                    "same_event_trace": same,
                }
            )
    summary = []
    for (assay, condition, method), points in sorted(groups.items()):
        summary.append(
            {
                "assay": assay,
                "condition": condition,
                "method": method,
                "n_complete": len(points),
                "mean_new_hits": statistics.mean(r["metrics"]["new_hits"] for r in points),
                "mean_delivered": statistics.mean(r["metrics"]["delivered"] for r in points),
                "mean_reserved": statistics.mean(r["metrics"]["reserved"] for r in points),
                "selected_requests": sum(r["selector"]["selected_requests"] for r in points),
                "fallback_requests": sum(r["selector"]["fallback_requests"] for r in points),
                "fit_successes": sum(r["selector"]["fit_successes"] for r in points),
            }
        )
    (PACKET / "results").mkdir(exist_ok=True)
    for name, rows in (
        ("runs.csv", comparisons),
        ("summary.csv", summary),
        ("pending-pairs.csv", pairs),
    ):
        if rows:
            with (PACKET / "results" / name).open("w", newline="", encoding="utf-8") as out:
                writer = csv.DictWriter(out, fieldnames=list(rows[0]))
                writer.writeheader()
                writer.writerows(rows)
    (PACKET / "runs").mkdir(exist_ok=True)
    for name in ("ledger.json", "canary-check.json"):
        artifacts[name] = (folder / name).read_bytes()
    for name, raw in artifacts.items():
        dest = PACKET / "runs" / name
        if dest.exists():
            assert dest.read_bytes() == raw, "Do not overwrite different evidence"
        else:
            dest.write_bytes(raw)
    result = {
        "status": "PASS" if len(complete) == 54 else "FAIL_WITH_RETAINED_FAILURES",
        "scope": "DEVELOPMENT_ONLY_GAUSSIAN_BINARY_APPROXIMATION; same-implementer second-pass audit",
        "analyzed_at_utc": datetime.now(timezone.utc).isoformat(),
        "config_sha256": digest(cfg),
        "execution_source_sha256": source_identity(),
        "expected_runs": 54,
        "complete": len(complete),
        "failed": len(runs) - len(complete),
        "warnings": sum(len(r.get("warnings", [])) for r in runs),
        "zero_initial_active_runs": sum(r["initial_active_count"] == 0 for r in complete),
        "run_wall_seconds": ledger["wall_seconds"],
        "process_cpu_seconds": ledger["cpu_seconds"],
        "peak_runner_working_set_bytes": ledger["peak_runner_working_set_bytes"],
        "common_exact_pairs": sum(
            p["condition"] == "common" and p["same_event_trace"] for p in pairs
        ),
        "pairs": pairs,
        "summary": summary,
        "final_evaluation": False,
        "learned_controller_evaluated": False,
        "artifact_sha256": {
            n: hashlib.sha256(raw).hexdigest() for n, raw in sorted(artifacts.items())
        },
    }
    write(PACKET / "results/results.json", result)
    print(
        json.dumps(
            {k: v for k, v in result.items() if k not in ("pairs", "summary", "artifact_sha256")},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
