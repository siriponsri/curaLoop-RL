"""Bounded, immutable development replay; no final-test inference or paid compute."""

import argparse
import hashlib
import itertools
import json
import os
import platform
import random
import subprocess
import sys
import time
import traceback
import warnings
from contextlib import contextmanager
from datetime import datetime, timezone
from importlib.metadata import version
from pathlib import Path

from threadpoolctl import threadpool_info, threadpool_limits

from research.event_time import Campaign, Candidate, Scenario, Task, keyed_duration

from .baselines import METHODS, Selector
from .prepare_cohort import OUT, ROOT

EXECUTION_FILES = (
    "research/event_time.py",
    "research/development/baselines.py",
    "research/development/runner.py",
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def execution_identity():
    return digest({name: (ROOT / name).read_text(encoding="utf-8") for name in EXECUTION_FILES})


def write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


@contextmanager
def study_lock(folder):
    handle = (folder / "study.lock").open("a+b")
    try:
        if sys.platform == "win32":
            import msvcrt

            handle.seek(0)
            handle.write(b"0")
            handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield
    finally:
        handle.close()


def peak_working_set_bytes():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes

        class Counters(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD)] + [
                (name, ctypes.c_size_t)
                for name in (
                    "PeakWorkingSetSize",
                    "WorkingSetSize",
                    "QuotaPeakPagedPoolUsage",
                    "QuotaPagedPoolUsage",
                    "QuotaPeakNonPagedPoolUsage",
                    "QuotaNonPagedPoolUsage",
                    "PagefileUsage",
                    "PeakPagefileUsage",
                )
            ]

        counters = Counters()
        counters.cb = ctypes.sizeof(counters)
        process = ctypes.windll.kernel32.GetCurrentProcess
        process.restype = wintypes.HANDLE
        get_memory = ctypes.windll.psapi.GetProcessMemoryInfo
        get_memory.argtypes = (wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD)
        get_memory.restype = wintypes.BOOL
        if get_memory(process(), ctypes.byref(counters), counters.cb):
            return counters.PeakWorkingSetSize
    return None


def load_cohort(assay, expected):
    data = (OUT / (assay + ".json")).read_bytes()
    if hashlib.sha256(data).hexdigest() != expected:
        raise ValueError("Frozen cohort changed: " + assay)
    cohort = json.loads(data)
    if cohort["controller_role"] != "development":
        raise ValueError("Only declared development tasks are admitted.")
    return cohort


def run_one(cohort, cfg, seed, condition, method):
    records = cohort["records"]
    candidates = []
    for r in records:
        on = set(r["morgan_on_bits"])
        candidates.append(Candidate(r["candidate_id"], tuple(float(i in on) for i in range(1024))))
    ids = sorted(c.candidate_id for c in candidates)
    initial = tuple(sorted(random.Random(seed).sample(ids, cfg["initial_count"])))
    values = tuple(cfg["conditions"][condition])
    durations = tuple(
        (cid, keyed_duration(cohort["task_id"], seed, cid, "ncats-training-assay", values))
        for cid in ids
    )
    task = Task(
        cohort["task_id"],
        tuple(candidates),
        durations,
        tuple((cid, 1) for cid in ids),
        tuple((r["candidate_id"], r["active"]) for r in records),
    )
    scenario = Scenario(cfg["budget"], cfg["capacity"], cfg["deadline"], initial)
    run = Campaign(task, scenario)
    selector = Selector(method, seed, cfg["pending_lambda"])
    decisions = []
    ticks = []
    started = time.perf_counter()
    cpu = time.process_time()
    for tick in range(cfg["deadline"]):
        run.advance_to(tick)
        obs = run.observe()
        ticks.append(
            {
                "time": tick,
                "pending": len(obs.pending_ids),
                "eligible": len(obs.eligible_ids),
                "slots": obs.slots,
            }
        )
        if obs.eligible_ids:
            choices, trace = selector.choose(obs)
            run.submit(choices)
            decisions.append(trace)
    run.advance_to(cfg["deadline"])
    snapshot = run.snapshot()
    # A real completed public journal reconstructs identically with pending work retained.
    restored = Campaign.restore(task, snapshot)
    if restored.snapshot() != snapshot:
        raise ValueError("Restoration mismatch.")
    metrics = run.metrics
    if metrics["spent"] + metrics["reserved"] + metrics["uncommitted"] != cfg["budget"]:
        raise ValueError("Budget reconciliation failed.")
    by_id = {r["candidate_id"]: r for r in records}
    hits = [e.candidate_id for e in run.events if e.kind == "RESULT_DELIVERED" and e.active]
    metrics["new_active_nonempty_scaffolds"] = len(
        {by_id[c]["scaffold"] for c in hits if by_id[c]["scaffold"]}
    )
    metrics["new_active_empty_scaffold_count"] = sum(not by_id[c]["scaffold"] for c in hits)
    return {
        "status": "COMPLETE",
        "assay": cohort["task_id"],
        "seed": seed,
        "condition": condition,
        "method": method,
        "initial_ids": list(initial),
        "initial_active_count": sum(r.active for r in run.observe().initial_results),
        "schedule_sha256": digest(durations),
        "metrics": metrics,
        "selector": selector.report(),
        "decisions": decisions,
        "decision_grid": ticks,
        "snapshot": snapshot,
        "restoration_verified": True,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu,
        "scope": "DEVELOPMENT_HISTORICAL_ASSAY_REPLAY; simulated unit costs/durations; not therapeutic efficacy",
    }


def plan(cfg):
    return list(itertools.product(cfg["assays"], cfg["seeds"], cfg["conditions"], cfg["methods"]))


def execute(config_path, folder, phase):
    cfg = json.loads(config_path.read_text())
    if (
        cfg["status"] != "FROZEN_DEVELOPMENT_ONLY"
        or cfg["final_evaluation"]
        or cfg["execution_source_sha256"] != execution_identity()
    ):
        raise ValueError("Development freeze or exact execution code identity differs.")
    if any(m not in METHODS for m in cfg["methods"]):
        raise ValueError("Unimplemented method.")
    if cfg["schema_version"] != "curaloop.ncats-development-run.v1" or cfg["predictor"] != {
        "family": "StandardScaler->LogisticRegression",
        "solver": "liblinear",
        "C": 1.0,
        "max_iter": 500,
    }:
        raise ValueError("Predictor/configuration contract differs from this version.")
    if (
        cfg["threads"] != 1
        or cfg["concurrency"] != 1
        or cfg["unit_cost"] != 1
        or set(cfg["assays"]) != {"ahr", "pparg", "p53"}
        or len(cfg["assays"]) != 3
        or len(cfg["methods"]) != len(set(cfg["methods"]))
    ):
        raise ValueError("Unexpected cohort, concurrency or duplicate methods.")
    if cfg["expected_runs"] != len(plan(cfg)) or not cfg["seeds"]:
        raise ValueError("Run allocation differs from the declared denominator.")
    if any(type(s) is not int or not 0 <= s < 2**32 for s in cfg["seeds"]) or len(
        cfg["seeds"]
    ) != len(set(cfg["seeds"])):
        raise ValueError("Seeds must be distinct bounded integers.")
    config_sha = digest(cfg)
    folder.mkdir(parents=True, exist_ok=True)
    with study_lock(folder), threadpool_limits(limits=1):
        ledger_path = folder / "ledger.json"
        if not ledger_path.exists() and any(folder.glob("*.json")):
            raise ValueError(
                "Existing artifacts without their ledger; preserve before assigning a new study folder."
            )
        ledger = (
            json.loads(ledger_path.read_text())
            if ledger_path.exists()
            else {
                "config_sha256": config_sha,
                "wall_seconds": 0.0,
                "cpu_seconds": 0.0,
                "attempts": {},
            }
        )
        if ledger["config_sha256"] != config_sha:
            raise ValueError("Run folder belongs to a different frozen configuration.")
        if any(a["status"] == "RUNNING" for a in ledger["attempts"].values()):
            raise ValueError(
                "Interrupted/uncertain attempt retained; explicit new attempt identity required before replay."
            )
        cohorts = {a: load_cohort(a, cfg["cohort_sha256"][a]) for a in cfg["assays"]}
        if any(len(c["records"]) != cfg["sample_size_per_assay"] for c in cohorts.values()):
            raise ValueError("Frozen pool size differs from configuration.")
        metadata = {
            "config_sha256": config_sha,
            "execution_source_sha256": execution_identity(),
            "git_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            "working_tree_dirty": bool(
                subprocess.check_output(
                    ["git", "status", "--porcelain"], cwd=ROOT, text=True
                ).strip()
            ),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "logical_cpus_available": os.cpu_count(),
            "packages": {
                p: version(p) for p in ("numpy", "scikit-learn", "rdkit", "threadpoolctl")
            },
            "threadpools": threadpool_info(),
            "phase": phase,
            "started_utc": datetime.now(timezone.utc).isoformat(),
        }
        jobs = plan(cfg)
        if phase == "canary":
            jobs = [job for job in jobs if job[1] == cfg["seeds"][0] and job[2] == "heterogeneous"]
        for assay, seed, condition, method in jobs:
            identity = {
                "config_sha256": config_sha,
                "assay": assay,
                "seed": seed,
                "condition": condition,
                "method": method,
            }
            run_id = digest(identity)[:24]
            path = folder / (run_id + ".json")
            if run_id in ledger["attempts"]:
                entry = ledger["attempts"][run_id]
                if (
                    not path.is_file()
                    or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]
                ):
                    raise ValueError(
                        "Saved completed/failed artifact changed; do not silently rerun."
                    )
                continue
            if ledger["wall_seconds"] >= cfg["max_cumulative_run_wall_seconds"]:
                print("STOP: prespecified cumulative CPU-run wall cap reached", flush=True)
                break
            ledger["attempts"][run_id] = {"status": "RUNNING", "identity": identity}
            write(ledger_path, ledger)
            start = time.perf_counter()
            cpu = time.process_time()
            recorded = []
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
            result["warnings"] = [str(w.message) for w in recorded]
            result["attempt_wall_seconds"] = time.perf_counter() - start
            result["attempt_cpu_seconds"] = time.process_time() - cpu
            result.update({"run_id": run_id, "identity": identity, "execution": metadata})
            write(path, result)
            ledger["wall_seconds"] += time.perf_counter() - start
            ledger["cpu_seconds"] += time.process_time() - cpu
            ledger["attempts"][run_id] = {
                "status": result["status"],
                "identity": identity,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "attempt_wall_seconds": result["attempt_wall_seconds"],
                "attempt_cpu_seconds": result["attempt_cpu_seconds"],
            }
            peak = peak_working_set_bytes()
            ledger["peak_runner_working_set_bytes"] = (
                max(ledger.get("peak_runner_working_set_bytes") or 0, peak or 0) or None
            )
            write(ledger_path, ledger)
            print(
                f"{result['status']} {assay} seed={seed} {condition} {method} hits={result.get('metrics', {}).get('new_hits')}",
                flush=True,
            )
        return ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("canary", "all"), default="canary")
    args = parser.parse_args()
    ledger = execute(args.config, args.output, args.phase)
    print(
        json.dumps(
            {
                "attempts": len(ledger["attempts"]),
                "wall_seconds": ledger["wall_seconds"],
                "cpu_seconds": ledger["cpu_seconds"],
                "peak_working_set_bytes": ledger.get("peak_runner_working_set_bytes"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
