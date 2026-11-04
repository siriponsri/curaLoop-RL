"""Execute constructed scheduler diagnostics, not an empirical assay benchmark."""

import argparse
import hashlib
import itertools
import json
import platform
import subprocess
import time
from dataclasses import asdict
from pathlib import Path

from .event_time import VERSION, Campaign, Candidate, Scenario, Task


def fixture(durations=(1, 1, 1), outcomes=(True, True, False), missing=()) -> Task:
    ids = ("a", "b", "c")
    return Task(
        "constructed-three-candidates-v1",
        tuple(Candidate(cid, (float(i),)) for i, cid in enumerate(ids)),
        tuple(zip(ids, durations)),
        tuple((cid, 1) for cid in ids),
        tuple(zip(ids, outcomes)),
        tuple(missing),
    )


def run_order(task: Task, scenario: Scenario, order: tuple[str, ...]) -> Campaign:
    """Static public ordering; never reads outcomes or private future durations."""
    run = Campaign(task, scenario)
    while not run.done:
        obs = run.observe()
        feasible = [cid for cid in order if cid in obs.eligible_ids]
        if feasible:
            chosen, balance = [], obs.uncommitted
            costs = dict(obs.cost_quotes)
            for cid in feasible:
                if costs[cid] <= balance and len(chosen) < obs.slots:
                    chosen.append(cid)
                    balance -= costs[cid]
            run.submit(tuple(chosen))
        elif not run.wait():
            raise ValueError("Static ordering omits an eligible candidate.")
    if scenario.deadline is not None and run.time < scenario.deadline:
        run.advance_to(scenario.deadline)
    return run


def serial_reference(order, durations, outcomes, budget, deadline) -> int:
    """Independent mathematical reference for a unit-cost, one-slot fixture."""
    elapsed = hits = 0
    for cid in order[:budget]:
        if elapsed >= deadline:
            break
        elapsed += durations[cid]
        if elapsed <= deadline:
            hits += int(outcomes[cid])
    return hits


def report() -> dict:
    started = time.perf_counter()
    invariance = []
    for duration in (0, 1, 4):
        run = run_order(fixture((duration,) * 3), Scenario(2, 1, None), ("a", "b", "c"))
        invariance.append(
            {
                "common_duration": duration,
                "selected_ids": [
                    e.candidate_id for e in run.events if e.kind == "REQUEST_ACCEPTED"
                ],
                "metrics": run.metrics,
                "events": [asdict(e) for e in run.events],
            }
        )
    assert all(
        r["selected_ids"] == ["a", "b"] and r["metrics"]["new_hits"] == 2 for r in invariance
    )

    heterogeneous = fixture((4, 1, 1), (True, True, True))
    slow = run_order(heterogeneous, Scenario(2, 1, 2), ("a", "b", "c"))
    fast = run_order(heterogeneous, Scenario(2, 1, 2), ("b", "c", "a"))
    upper_bound = max(
        serial_reference(order, dict(heterogeneous.durations), dict(heterogeneous._outcomes), 2, 2)
        for order in itertools.permutations(("a", "b", "c"))
    )
    assert slow.metrics["new_hits"] == 0 and slow.metrics["reserved"] == 1
    assert fast.metrics["new_hits"] == upper_bound == 2

    task = fixture((2, 2, 4), (True, False, True), ("b",))
    pending = Campaign(task, Scenario(3, 3, 2))
    pending.submit(("a", "b", "c"))
    saved = pending.snapshot()
    restored = Campaign.restore(task, saved)
    assert restored.snapshot() == saved
    restored.advance_to(2)
    assert restored.metrics["new_hits"] == 1 and restored.metrics["missing"] == 1
    assert restored.metrics["spent"] == 2 and restored.metrics["reserved"] == 1

    cases = orders = 0
    for duration_tuple in itertools.product((0, 1, 2), repeat=3):
        for truth in itertools.product((False, True), repeat=3):
            t = fixture(duration_tuple, truth)
            for deadline in (0, 1, 3):
                for order in itertools.permutations(("a", "b", "c")):
                    run = run_order(t, Scenario(2, 1, deadline), order)
                    expected = serial_reference(
                        order, dict(t.durations), dict(t._outcomes), 2, deadline
                    )
                    assert run.metrics["new_hits"] == expected, (
                        duration_tuple,
                        truth,
                        deadline,
                        order,
                    )
                    orders += 1
                cases += 1
    root = Path(__file__).resolve().parents[1]
    source_hash = hashlib.sha256(
        json.dumps(
            {
                p.relative_to(root).as_posix(): p.read_text(encoding="utf-8")
                for p in sorted((root / "research").glob("*.py"))
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return {
        "status": "PASS",
        "schema_version": VERSION,
        "reference_source_sha256": source_hash,
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True
        ).strip(),
        "working_tree_dirty": bool(
            subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True).strip()
        ),
        "python": platform.python_version(),
        "scope": "Constructed synthetic scheduler diagnostics only; no biological or policy-superiority inference",
        "diagnostic_wall_seconds": time.perf_counter() - started,
        "common_delay_without_deadline": invariance,
        "heterogeneous_deadline": {
            "slow_first": slow.snapshot(),
            "fast_first": fast.snapshot(),
            "enumerated_evaluator_upper_bound_hits": upper_bound,
            "interpretation": "An intentionally constructed duration tradeoff; the two static orders are not an H1 pending-aware comparison.",
        },
        "exact_deadline_missing_and_restart": restored.snapshot(),
        "enumerated_serial_fixtures": cases,
        "ordering_checks": orders,
        "not_run": [
            "empirical H1 contrast",
            "multi-target study",
            "new controller training",
            "backend adapter",
            "customer validation",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(
        f"PASS: {result['enumerated_serial_fixtures']} fixtures / {result['ordering_checks']} order checks; synthetic only."
    )


if __name__ == "__main__":
    main()
