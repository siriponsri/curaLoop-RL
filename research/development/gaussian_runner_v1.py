"""Separate immutable 54-run development amendment for Gaussian controls."""

import argparse
import hashlib
import json
import platform
import random
import subprocess
import time
import traceback
import warnings
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from threadpoolctl import threadpool_info, threadpool_limits

from research.event_time import Campaign, Candidate, Scenario, Task, keyed_duration

from .gaussian_controls_v1 import GP_METHODS, GP_PARAMETERS, GaussianSelector
from .prepare_cohort import ROOT
from .runner import (
    EXECUTION_FILES,
    digest,
    load_cohort,
    peak_working_set_bytes,
    plan,
    study_lock,
    write,
)

CONFIG = ROOT / "research/configs/ncats_gaussian_development_v1.json"
PACKET = ROOT / "docs/evidence/ncats-gaussian-development-20261104-v1"
SOURCE_FILES = EXECUTION_FILES + (
    "research/development/gaussian_controls_v1.py",
    "research/development/gaussian_runner_v1.py",
)


def source_identity():
    return digest({p: (ROOT / p).read_text(encoding="utf-8") for p in SOURCE_FILES})


def freeze():
    if CONFIG.exists() or PACKET.exists():
        raise ValueError("Existing amendment must be preserved; use a new version.")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip():
        raise ValueError("Commit implementation/protocol before freezing.")
    base = json.loads((ROOT / "research/configs/ncats_development_v1.json").read_text())
    for a, sha in base["cohort_sha256"].items():
        load_cohort(a, sha)
    cfg = {
        **base,
        "schema_version": "curaloop.gaussian-development.v1",
        "protocol_id": "ncats-gaussian-development-20261104-v1",
        "base_config_sha256": digest(base),
        "methods": list(GP_METHODS),
        "predictor": {"family": "sklearn GaussianProcessRegressor", **GP_PARAMETERS},
        "expected_runs": 54,
        "frozen_at_utc": datetime.now(timezone.utc).isoformat(),
        "implementation_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "execution_source_sha256": source_identity(),
        "canary": "9 included seed0 heterogeneous runs; projection <=300s required before remaining45",
        "primary_development_diagnostic": "gp_ucb_pending minus gp_ucb_blind H(T), descriptive only; Gaussian mean arm isolates exploration",
        "common_negative_control": "GP UCB blind/pending exact event histories match",
        "unimplemented_controls": [
            "calibrated Bernoulli GP",
            "BayBE/BoTorch integration",
            "learned controller",
        ],
        "new_method_outcomes_inspected_before_freeze": False,
    }
    cfg.pop("pending_lambda")
    write(CONFIG, cfg)
    PACKET.mkdir(parents=True)
    (PACKET / ".gitattributes").write_text(
        "runs/*.json -text\n*.json whitespace=trailing-space,space-before-tab,cr-at-eol\n*.csv whitespace=trailing-space,space-before-tab,cr-at-eol\n",
        newline="\n",
    )
    write(
        PACKET / "freeze.json",
        {
            "status": "FROZEN_DEVELOPMENT_ONLY",
            "config_sha256": digest(cfg),
            "execution_source_sha256": source_identity(),
            "implementation_commit": cfg["implementation_commit"],
            "frozen_at_utc": cfg["frozen_at_utc"],
            "new_method_outcomes_inspected_before_freeze": False,
            "original_108_results_exposed": True,
            "final_protocol_frozen": False,
        },
    )
    print("FROZEN " + digest(cfg))


def run_one(cohort, cfg, seed, condition, method):
    records = cohort["records"]
    candidates = []
    for r in records:
        on = set(r["morgan_on_bits"])
        candidates.append(Candidate(r["candidate_id"], tuple(float(i in on) for i in range(1024))))
    ids = sorted(c.candidate_id for c in candidates)
    initial = tuple(sorted(random.Random(seed).sample(ids, cfg["initial_count"])))
    durations = tuple(
        (
            cid,
            keyed_duration(
                cohort["task_id"],
                seed,
                cid,
                "ncats-training-assay",
                tuple(cfg["conditions"][condition]),
            ),
        )
        for cid in ids
    )
    task = Task(
        cohort["task_id"],
        tuple(candidates),
        durations,
        tuple((c, 1) for c in ids),
        tuple((r["candidate_id"], r["active"]) for r in records),
    )
    campaign = Campaign(task, Scenario(cfg["budget"], cfg["capacity"], cfg["deadline"], initial))
    selector = GaussianSelector(method, seed)
    decisions = []
    for tick in range(cfg["deadline"]):
        campaign.advance_to(tick)
        obs = campaign.observe()
        if obs.eligible_ids:
            chosen, trace = selector.choose(obs)
            campaign.submit(chosen)
            decisions.append(trace)
    campaign.advance_to(cfg["deadline"])
    snapshot = campaign.snapshot()
    if Campaign.restore(task, snapshot).snapshot() != snapshot:
        raise ValueError("Public journal restoration differs.")
    metrics = campaign.metrics
    by_id = {r["candidate_id"]: r for r in records}
    active = [e.candidate_id for e in campaign.events if e.kind == "RESULT_DELIVERED" and e.active]
    metrics["new_active_nonempty_scaffolds"] = len(
        {by_id[c]["scaffold"] for c in active if by_id[c]["scaffold"]}
    )
    metrics["new_active_empty_scaffold_count"] = sum(not by_id[c]["scaffold"] for c in active)
    return {
        "status": "COMPLETE",
        "initial_ids": list(initial),
        "initial_active_count": sum(r.active for r in campaign.observe().initial_results),
        "schedule_sha256": digest(durations),
        "metrics": metrics,
        "snapshot": snapshot,
        "decisions": decisions,
        "selector": selector.report(),
        "restoration_verified": True,
        "scope": "DEVELOPMENT_ONLY_GAUSSIAN_BINARY_APPROXIMATION",
    }


def execute(folder, phase):
    cfg = json.loads(CONFIG.read_text())
    if (
        cfg["schema_version"] != "curaloop.gaussian-development.v1"
        or cfg["status"] != "FROZEN_DEVELOPMENT_ONLY"
        or cfg["assays"] != ["ahr", "pparg", "p53"]
        or cfg["seeds"] != [0, 1, 2]
        or cfg["conditions"] != {"common": [2], "heterogeneous": [1, 2, 4]}
        or (cfg["initial_count"], cfg["budget"], cfg["capacity"], cfg["deadline"], cfg["unit_cost"])
        != (24, 24, 3, 12, 1)
    ):
        raise ValueError("Operational allocation differs from this fixed amendment.")
    if cfg["execution_source_sha256"] != source_identity() or cfg["predictor"] != {
        "family": "sklearn GaussianProcessRegressor",
        **GP_PARAMETERS,
    }:
        raise ValueError("Execution code or fixed Gaussian parameters changed after freeze.")
    if (
        cfg["methods"] != list(GP_METHODS)
        or cfg["expected_runs"] != 54
        or cfg["final_evaluation"]
        or cfg["threads"] != 1
        or cfg["concurrency"] != 1
    ):
        raise ValueError("Amendment allocation differs.")
    folder.mkdir(parents=True, exist_ok=True)
    with study_lock(folder), threadpool_limits(limits=1):
        ledger_path = folder / "ledger.json"
        if not ledger_path.exists() and any(folder.glob("*.json")):
            raise ValueError("Artifacts without ledger: do not reset or silently repeat.")
        ledger = (
            json.loads(ledger_path.read_text())
            if ledger_path.exists()
            else {
                "config_sha256": digest(cfg),
                "wall_seconds": 0.0,
                "cpu_seconds": 0.0,
                "attempts": {},
            }
        )
        if ledger["config_sha256"] != digest(cfg) or any(
            e["status"] == "RUNNING" for e in ledger["attempts"].values()
        ):
            raise ValueError(
                "Different config or uncertain interrupted attempt; explicit new identity required."
            )
        cohorts = {a: load_cohort(a, cfg["cohort_sha256"][a]) for a in cfg["assays"]}
        metadata = {
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "packages": {
                p: version(p) for p in ("numpy", "scipy", "scikit-learn", "rdkit", "threadpoolctl")
            },
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "working_tree_dirty": bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=ROOT, text=True
                ).strip()
            ),
            "execution_source_sha256": source_identity(),
            "threadpools": threadpool_info(),
            "phase": phase,
        }
        jobs = plan(cfg)
        if phase == "canary":
            jobs = [j for j in jobs if j[1] == 0 and j[2] == "heterogeneous"]
        for assay, seed, condition, method in jobs:
            identity = dict(
                config_sha256=digest(cfg),
                assay=assay,
                seed=seed,
                condition=condition,
                method=method,
            )
            run_id = digest(identity)[:24]
            path = folder / (run_id + ".json")
            if run_id in ledger["attempts"]:
                if (
                    hashlib.sha256(path.read_bytes()).hexdigest()
                    != ledger["attempts"][run_id]["sha256"]
                ):
                    raise ValueError("Saved artifact changed; do not silently rerun.")
                continue
            if ledger["wall_seconds"] >= cfg["max_cumulative_run_wall_seconds"]:
                print("STOP cumulative run-wall cap reached", flush=True)
                break
            ledger["attempts"][run_id] = {"status": "RUNNING", "identity": identity}
            write(ledger_path, ledger)
            start, cpu, recorded = time.perf_counter(), time.process_time(), []
            try:
                with warnings.catch_warnings(record=True) as recorded:
                    warnings.simplefilter("always")
                    result = run_one(cohorts[assay], cfg, seed, condition, method)
            except Exception as error:
                result = {
                    "status": "FAILED",
                    "error": type(error).__name__ + ": " + str(error),
                    "traceback": traceback.format_exc(),
                }
            result.update(
                run_id=run_id,
                identity=identity,
                execution=metadata,
                warnings=[str(w.message) for w in recorded],
                attempt_wall_seconds=time.perf_counter() - start,
                attempt_cpu_seconds=time.process_time() - cpu,
            )
            write(path, result)
            ledger["wall_seconds"] += time.perf_counter() - start
            ledger["cpu_seconds"] += time.process_time() - cpu
            ledger["attempts"][run_id] = {
                "status": result["status"],
                "identity": identity,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
            ledger["peak_runner_working_set_bytes"] = max(
                ledger.get("peak_runner_working_set_bytes", 0), peak_working_set_bytes() or 0
            )
            write(ledger_path, ledger)
            print(
                f"{result['status']} {assay} seed={seed} {condition} {method} hits={result.get('metrics', {}).get('new_hits')}",
                flush=True,
            )
        print(
            json.dumps(
                {k: v for k, v in ledger.items() if k != "attempts"}
                | {"attempts": len(ledger["attempts"])},
                indent=2,
            )
        )
        return ledger


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--phase", choices=("canary", "all"), default="canary")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "research/runs/ncats-gaussian-development-20261104-v1"
    )
    args = parser.parse_args()
    freeze() if args.freeze else execute(args.output, args.phase)
