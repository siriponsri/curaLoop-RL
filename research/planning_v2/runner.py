"""Immutable, single-process real-assay DEVELOPMENT experiment for Goal 2."""

import argparse
import hashlib
import itertools
import json
import platform
import random
import signal
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

from research.event_time import Campaign, Candidate, Scenario, Task, keyed_duration

from .model import build, clusters

ROOT = Path(__file__).resolve().parents[2]
FILES = (
    "research/event_time.py",
    "research/planning_v2/finite.py",
    "research/planning_v2/model.py",
    "research/planning_v2/runner.py",
)
METHODS = (
    "random",
    "frozen_greedy",
    "greedy",
    "posterior_mean",
    "nearest_hit",
    "pending_cluster_wait",
    "cpe_rollout",
    "rollout",
    "cardinality_pruned",
    "content_pruned",
)


def digest(value):
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def identity():
    return {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in FILES}


def write(path, value):
    if path.exists():
        raise FileExistsError("Immutable output already exists: " + str(path))
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def select(obs, launched, groups, packed, support, seed, cfg, method, frozen):
    started = time.perf_counter()
    public_key = [
        seed,
        obs.time,
        [(r.candidate_id, r.active) for r in obs.initial_results + obs.delivered_results],
        list(obs.pending_ids),
        sorted(launched.items()),
    ]
    model_seed = int(digest(public_key)[:16], 16)
    model, state = build(obs, launched, groups, support, model_seed, cfg["worlds"], cfg["capacity"])
    model_seconds = time.perf_counter() - started
    ids = [c.candidate_id for c in obs.candidates]
    eligible = model.rank(state, model.full)
    count = min(obs.slots, obs.uncommitted, len(eligible))
    fallback, trace = None, {}
    if method in ("rollout", "cardinality_pruned", "content_pruned", "cpe_rollout"):
        bound = {"cardinality_pruned": "cardinality", "content_pruned": "content"}.get(method)
        action, trace = model.choose(
            state, cfg["shortlist"], bound, "cpe" if method == "cpe_rollout" else "hits"
        )
    else:
        ranking = eligible
        if method == "random":
            ranking = eligible.copy()
            random.Random(model_seed).shuffle(ranking)
        elif method == "frozen_greedy":
            if not frozen:
                frozen.update({i: model.bits[i].bit_count() for i in range(model.n)})
            ranking = sorted(eligible, key=lambda i: (-frozen[i], i))
        elif method == "posterior_mean":
            counts = [[0.5, 9.5] for _ in range(max(groups) + 1)]
            index = {cid: i for i, cid in enumerate(ids)}
            for r in obs.initial_results + obs.delivered_results:
                counts[groups[index[r.candidate_id]]][0 if r.active else 1] += 1
            ranking = sorted(
                eligible, key=lambda i: (-counts[groups[i]][0] / sum(counts[groups[i]]), i)
            )
        elif method == "nearest_hit":
            known = {
                r.candidate_id for r in obs.initial_results + obs.delivered_results if r.active
            }
            hits = [i for i, cid in enumerate(ids) if cid in known]
            if hits:

                def score(i):
                    return max(
                        (packed[i] & packed[h]).bit_count() / (packed[i] | packed[h]).bit_count()
                        if packed[i] | packed[h]
                        else 1
                        for h in hits
                    )

                ranking = sorted(eligible, key=lambda i: (-score(i), i))
            else:
                fallback = "NO_DELIVERED_ACTIVE_RANDOM"
                ranking = eligible.copy()
                random.Random(model_seed).shuffle(ranking)
        action = tuple(ranking[:count])
        if method == "pending_cluster_wait" and eligible and obs.pending_ids:
            pending_groups = {groups[ids.index(cid)] for cid in obs.pending_ids}
            if groups[eligible[0]] in pending_groups and obs.remaining_time >= max(support) + min(
                support
            ):
                action = ()
    trace.update(
        {
            "time": obs.time,
            "pending_ids": obs.pending_ids,
            "chosen": [ids[i] for i in action],
            "fallback_reason": fallback,
            "model_seconds": model_seconds,
            "policy_seconds": time.perf_counter() - started,
            "finite_worlds": cfg["worlds"],
            "model_seed": model_seed,
            "learned_controller_action": False,
        }
    )
    return tuple(ids[i] for i in action), trace


def run_one(cohort, cfg, seed, condition, method):
    started, cpu = time.perf_counter(), time.process_time()
    candidates = []
    for row in cohort["records"]:
        bits = set(row["morgan_on_bits"])
        candidates.append(
            Candidate(row["candidate_id"], tuple(float(i in bits) for i in range(1024)))
        )
    candidates = tuple(sorted(candidates, key=lambda c: c.candidate_id))
    ids = [c.candidate_id for c in candidates]
    initial = tuple(sorted(random.Random(seed).sample(ids, cfg["initial_count"])))
    support = cfg["conditions"][condition]
    durations = tuple(
        (cid, keyed_duration(cohort["task_id"], seed, cid, "goal2-real-assay-v1", tuple(support)))
        for cid in ids
    )
    task = Task(
        cohort["task_id"],
        candidates,
        durations,
        tuple((cid, 1) for cid in ids),
        tuple((r["candidate_id"], r["active"]) for r in cohort["records"]),
    )
    campaign = Campaign(task, Scenario(cfg["budget"], cfg["capacity"], cfg["deadline"], initial))
    groups, packed = clusters(candidates, cfg["clusters"])
    launched, frozen, decisions = {}, {}, []
    while not campaign.done:
        obs = campaign.observe()
        if obs.eligible_ids:
            # Only public Observation, accepted launches, features and frozen scenario law cross here.
            action, trace = select(
                obs, launched, groups, packed, support, seed, cfg, method, frozen
            )
            decisions.append(trace)
            if action:
                campaign.submit(action)
                launched.update({cid: obs.time for cid in action})
            elif not obs.pending_ids:
                raise AssertionError("Purposeless WAIT without pending work.")
        if not campaign.done:
            campaign.wait()  # trusted scheduler advances; selector never receives actual due times
    if campaign.time < cfg["deadline"]:
        campaign.advance_to(cfg["deadline"])
    snapshot = campaign.snapshot()
    if Campaign.restore(task, snapshot).snapshot() != snapshot:
        raise AssertionError("Restoration mismatch.")
    metrics = campaign.metrics
    if metrics["spent"] + metrics["reserved"] + metrics["uncommitted"] != cfg["budget"]:
        raise AssertionError("Cost conservation failure.")
    return {
        "status": "COMPLETE",
        "assay": cohort["task_id"],
        "seed": seed,
        "condition": condition,
        "method": method,
        "schedule_sha256": digest(durations),
        "initial_ids": initial,
        "initial_active_count": sum(r.active for r in campaign.observe().initial_results),
        "metrics": metrics,
        "decisions": decisions,
        "snapshot": snapshot,
        "restoration_verified": True,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu,
        "scope": "exposed development assay labels; synthetic operations; no final or clinical inference",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--phase", choices=("canary", "remaining"), required=True)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    if cfg["status"] != "FROZEN_DEVELOPMENT_ONLY" or cfg["source_sha256"] != identity():
        raise ValueError("Exact source freeze differs.")
    if tuple(cfg["methods"]) != METHODS or cfg["final_evaluation"] or cfg["worlds"] != 16:
        raise ValueError("Unsupported study contract.")
    args.output.mkdir(parents=True, exist_ok=True)
    runs = args.output / "runs"
    runs.mkdir(exist_ok=True)
    attempts = args.output / "attempts"
    attempts.mkdir(exist_ok=True)
    config_sha = hashlib.sha256(args.config.read_bytes()).hexdigest()
    for attempt in attempts.glob("*.json"):
        marker = json.loads(attempt.read_text())
        if not (runs / attempt.name).exists():
            raise ValueError("Unresolved attempt blocks identity replay: " + attempt.name)
        if marker["config_sha256"] != config_sha or marker["source_sha256"] != identity():
            raise ValueError("Attempt source/config differs.")
    completed = [json.loads(p.read_text()) for p in runs.glob("*.json")]
    elapsed = sum(r.get("wall_seconds", 0) for r in completed)
    if any(r["status"] != "COMPLETE" for r in completed):
        raise ValueError("A retained failure blocks continuation.")
    plan = list(itertools.product(cfg["assays"], cfg["seeds"], cfg["conditions"], cfg["methods"]))
    canary = [(cfg["assays"][0], cfg["seeds"][0], "heterogeneous", m) for m in cfg["methods"]]
    selected = canary if args.phase == "canary" else [r for r in plan if r not in canary]
    if args.phase == "remaining":
        expected = {f"{a}-{s}-{c}-{m}.json" for a, s, c, m in canary}
        if {p.name for p in runs.glob("*.json")} != expected:
            raise ValueError("Exact canary identities required before remaining phase.")
        receipt = json.loads((args.output / "canary-receipt.json").read_text())
        if (
            receipt["status"] != "PASS"
            or receipt["config_sha256"] != config_sha
            or receipt["source_sha256"] != identity()
        ):
            raise ValueError("Canary receipt differs from this freeze.")
    elif completed or list(attempts.glob("*.json")):
        raise ValueError("Canary output already used; preserve it.")
    started = time.perf_counter()
    for assay, seed, condition, method in selected:
        path = runs / f"{assay}-{seed}-{condition}-{method}.json"
        if path.exists():
            raise FileExistsError("Never replay a run identity.")
        if elapsed + time.perf_counter() - started >= cfg["max_run_wall_seconds"]:
            raise TimeoutError("Cumulative execution cap exhausted; no new run.")
        data = (ROOT / cfg["input_folder"] / f"{assay}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != cfg["cohort_sha256"][assay]:
            raise ValueError("Input identity differs.")
        cohort = json.loads(data)
        if cohort["controller_role"] != "development":
            raise ValueError("Only exposed declared development cohorts admitted.")
        before = time.perf_counter()
        write(
            attempts / path.name,
            {
                "status": "ATTEMPT_STARTED",
                "assay": assay,
                "seed": seed,
                "condition": condition,
                "method": method,
                "utc": datetime.now(timezone.utc).isoformat(),
                "config_sha256": config_sha,
                "source_sha256": identity(),
            },
        )

        def expired(_signum, _frame):
            raise TimeoutError("Cumulative execution cap reached inside a run.")

        signal.signal(signal.SIGALRM, expired)
        signal.setitimer(
            signal.ITIMER_REAL, cfg["max_run_wall_seconds"] - elapsed - (before - started)
        )
        try:
            result = run_one(cohort, cfg, seed, condition, method)
        except Exception:
            result = {
                "status": "FAILED",
                "assay": assay,
                "seed": seed,
                "condition": condition,
                "method": method,
                "error": traceback.format_exc(),
                "wall_seconds": time.perf_counter() - before,
            }
            write(path, result)
            raise
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        write(path, result)
        print(
            f"COMPLETE {path.name} H={result['metrics']['new_hits']} wall={result['wall_seconds']:.3f}",
            flush=True,
        )
    import resource  # Linux execution host only; no local runtime dependency added

    write(
        args.output / f"{args.phase}-receipt.json",
        {
            "status": "PASS",
            "phase": args.phase,
            "runs": len(selected),
            "utc": datetime.now(timezone.utc).isoformat(),
            "host": platform.node(),
            "python": sys.version,
            "platform": platform.platform(),
            "source_sha256": identity(),
            "config_sha256": hashlib.sha256(args.config.read_bytes()).hexdigest(),
            "phase_wall_seconds": time.perf_counter() - started,
            "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
        },
    )


if __name__ == "__main__":
    main()
