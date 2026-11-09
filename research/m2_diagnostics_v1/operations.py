"""Probe frozen M2 operations on independent public-state copies.

No loader, oracle, training, continuation or outcome scoring lives here. This is
only D1's first-action instrumentation, not its paired terminal-utility evaluator.
Production Clock use requires Linux SIGPROF; injected clocks are constructed-test
instruments and their reported durations cannot establish performance.
"""

import math
import signal
from contextlib import contextmanager
from dataclasses import dataclass

import numpy as np

from research.m2_costed_v2.engine import OPS, Clock, ComputeInterrupt, State
from research.m2_v1.models import ranked


@dataclass(frozen=True)
class _Origin:
    prefix: float

    def spent(self):
        return self.prefix


@contextmanager
def _timer(clock):
    if not isinstance(clock, Clock):
        # Dependency injection is explicit in the output, never a timer fallback.
        yield
        return
    if not all(hasattr(signal, name) for name in ("SIGPROF", "ITIMER_PROF", "setitimer")):
        raise RuntimeError("LINUX_CPU_GUARD_REQUIRED")
    previous = signal.getsignal(signal.SIGPROF)

    def interrupt(signum, frame):
        raise ComputeInterrupt("DIAGNOSTIC_CPU_LIMIT")

    signal.signal(signal.SIGPROF, interrupt)
    try:
        yield
    finally:
        clock.disarm()
        signal.signal(signal.SIGPROF, previous)


def probe_operations(state, *, prefix_cpu_seconds, clock_factory):
    """Compare REUSE/UPDATE/PLAN choices without acquiring even one label.

    The caller supplies a fresh equal-cap clock per branch, with the same prefix
    charge. Clone reconstruction, ranking and operation work are charged by that
    clock. The source State is never used as a branch. Public graph arrays are
    shared read-only under the frozen M2 implementation. No policy is fitted.
    Data admission and authorization are the caller's responsibility; this API
    does not grant biological access or implement a molecular runner.
    """
    if not math.isfinite(prefix_cpu_seconds) or prefix_cpu_seconds < 0:
        raise ValueError("INVALID_PREFIX_CPU")
    if len(state.pool.ids) > 512 or state.budget > 32:
        raise ValueError("BOUNDED_PROBE_LIMIT")
    if state.deliveries >= state.budget or not state.eligible():
        return {"status": "BLOCKED", "reason": "NO_REMAINING_ACTION"}
    if state.cold():
        return {"status": "BLOCKED", "reason": "COLD_UNIFORM_OVERRIDES_OPERATION"}
    if not state.ready():
        return {"status": "BLOCKED", "reason": "COMMON_INITIAL_FIT_REQUIRED"}
    snapshot = state.snapshot(_Origin(prefix_cpu_seconds))
    rows = []
    caps = []
    clocks = []
    for operation in OPS:
        clock = clock_factory()
        if any(clock is previous for previous in clocks):
            raise ValueError("BRANCH_CLOCK_REUSED")
        clocks.append(clock)
        caps.append(clock.cap)
        if (not math.isfinite(clock.cap) or clock.cap <= prefix_cpu_seconds
                or clock.prefix != prefix_cpu_seconds or len(set(caps)) != 1):
            raise ValueError("UNMATCHED_PREFIX_OR_CAP")
        with _timer(clock):
            branch = State.restore(
                state.pool, state.kind, state.seed, state.n0, state.budget,
                snapshot, state.similarity, state.neighbors,
            )
            before = branch.model.p.copy()
            fitted = branch.model.fitted_observations
            old_ranking = ranked(before, branch.eligible(), branch.tie)
            chosen, actual = branch.execute(operation, "G1", clock)
            rows.append({
                "operation": operation, "actual_operation": actual,
                "candidate_index": None if chosen is None else int(chosen),
                "stale_before": state.stale(),
                "fit_observation_count_changed": fitted != branch.model.fitted_observations,
                "cache_changed": not np.array_equal(before, branch.model.p),
                "ranking_changed": old_ranking != ranked(
                    branch.model.p, branch.eligible(), branch.tie),
                "candidate_prediction": None if chosen is None else float(branch.model.p[chosen]),
                "cpu_increment_seconds": clock.spent() - prefix_cpu_seconds,
                "clock_kind": "PROCESS_CPU_GUARDED" if isinstance(clock, Clock)
                              else "INJECTED_CONSTRUCTED_CLOCK",
                "valid_choice": chosen is not None and actual == operation and clock.enough(),
            })
    by_op = {row["operation"]: row for row in rows}

    def changed(left, right):
        a, b = by_op[left], by_op[right]
        if not (a["valid_choice"] and b["valid_choice"]):
            return None
        return a["candidate_index"] != b["candidate_index"]

    return {
        "status": "PASS_OPERATION_PROBE", "branches": rows,
        "update_changes_reuse_choice": changed("UPDATE", "REUSE"),
        "plan_changes_updated_greedy_choice": changed("PLAN", "UPDATE"),
        "terminal_utility": "NOT_IDENTIFIED_NO_OUTCOMES_OR_CONTINUATION",
        "labels_acquired": 0,
    }
