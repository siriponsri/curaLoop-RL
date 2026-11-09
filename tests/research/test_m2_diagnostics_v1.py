"""Constructed semantic regressions, not new molecular evidence."""

import copy

import numpy as np
import pytest

from research.m2_costed_v2 import engine
from research.m2_costed_v2.engine import Oracle, PublicPool, State
from research.m2_diagnostics_v1.operations import probe_operations


class ConstructedClock:
    def __init__(self, cap=10, prefix=0):
        self.cap, self.prefix, self.margin = cap, prefix, 0.002

    def spent(self):
        return self.prefix

    def remaining(self):
        return self.cap - self.spent()

    def enough(self, cost=0):
        return self.remaining() > cost + self.margin

    def arm(self):
        pass

    def disarm(self):
        pass


def fixture(kind="neighbor"):
    x = np.array([[1, 0], [1, 1], [0, 1], [1, 0], [0, 1], [1, 1]], dtype=np.uint8)
    pool = PublicPool("constructed", "constructed", tuple(map(str, range(6))), x)
    state = State(pool, kind, 17, 2, 3, dict(REUSE=0.001, UPDATE=0.01, PLAN=0.1))
    state.observed = {0: 1, 2: 0}
    state.model.update(state.observed)
    state.observed[1] = 0  # delivered after the fit; cache is now stale
    state.deliveries = 1
    return state


def test_probe_isolates_branches_and_never_acquires_labels():
    state = fixture()
    before = copy.deepcopy(state.snapshot(ConstructedClock()))
    out = probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)
    assert out["labels_acquired"] == 0
    assert out["terminal_utility"] == "NOT_IDENTIFIED_NO_OUTCOMES_OR_CONTINUATION"
    assert state.snapshot(ConstructedClock()) == before
    reuse, update, plan = out["branches"]
    assert not reuse["fit_observation_count_changed"] and not reuse["cache_changed"]
    assert update["fit_observation_count_changed"] and plan["fit_observation_count_changed"]
    assert update["cache_changed"] and plan["cache_changed"]
    assert all(r["clock_kind"] == "INJECTED_CONSTRUCTED_CLOCK" for r in out["branches"])


def test_no_staleness_means_update_does_not_refit(monkeypatch):
    state = fixture()
    state.model.update(state.observed)

    def forbidden(self, observed):
        raise AssertionError("UNEXPECTED_REFIT")

    monkeypatch.setattr(type(state.model), "update", forbidden)
    out = probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)
    assert not any(row["fit_observation_count_changed"] for row in out["branches"])
    assert out["update_changes_reuse_choice"] is False


def test_plan_at_last_delivery_equals_updated_greedy():
    state = fixture()
    state.budget = state.deliveries + 1
    out = probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)
    assert out["plan_changes_updated_greedy_choice"] is False


@pytest.mark.parametrize("kind", ["neighbor", "rf"])
def test_probe_does_not_need_hidden_outcomes(kind):
    state = fixture(kind)
    out = probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)
    assert out["status"] == "PASS_OPERATION_PROBE"
    assert all(r["valid_choice"] for r in out["branches"])


def test_cold_or_unfitted_states_do_not_claim_operation_support():
    state = fixture("rf")
    state.observed = {0: 1}
    assert probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)[
        "reason"] == "COLD_UNIFORM_OVERRIDES_OPERATION"
    state = fixture()
    state.model.fitted_observations = -1
    assert probe_operations(state, prefix_cpu_seconds=0, clock_factory=ConstructedClock)[
        "reason"] == "COMMON_INITIAL_FIT_REQUIRED"


def test_exhausted_cpu_is_not_action_equivalence():
    out = probe_operations(fixture(), prefix_cpu_seconds=0,
                           clock_factory=lambda: ConstructedClock(cap=0.0001))
    assert out["update_changes_reuse_choice"] is None
    assert out["plan_changes_updated_greedy_choice"] is None
    assert all(row["actual_operation"] == "NO_CPU" for row in out["branches"])


def test_interrupted_operation_is_not_a_valid_counterfactual(monkeypatch):
    original = State.execute

    def interrupted(self, op, policy, clock):
        chosen, actual = original(self, op, policy, clock)
        return chosen, "INTERRUPTED_PLAN" if op == "PLAN" else actual

    monkeypatch.setattr(State, "execute", interrupted)
    out = probe_operations(fixture(), prefix_cpu_seconds=0, clock_factory=ConstructedClock)
    assert out["plan_changes_updated_greedy_choice"] is None


@pytest.mark.parametrize("prefix", [-1, float("nan"), float("inf")])
def test_invalid_prefix_rejected(prefix):
    with pytest.raises(ValueError, match="INVALID_PREFIX_CPU"):
        probe_operations(fixture(), prefix_cpu_seconds=prefix, clock_factory=ConstructedClock)


def test_prefix_is_not_refunded():
    out = probe_operations(fixture(), prefix_cpu_seconds=2,
                           clock_factory=lambda: ConstructedClock(prefix=2))
    assert all(row["cpu_increment_seconds"] == 0 for row in out["branches"])
    with pytest.raises(ValueError, match="UNMATCHED_PREFIX_OR_CAP"):
        probe_operations(fixture(), prefix_cpu_seconds=2, clock_factory=ConstructedClock)


def test_unequal_branch_caps_rejected():
    clocks = iter([ConstructedClock(10), ConstructedClock(11), ConstructedClock(10)])
    with pytest.raises(ValueError, match="UNMATCHED_PREFIX_OR_CAP"):
        probe_operations(fixture(), prefix_cpu_seconds=0, clock_factory=lambda: next(clocks))


def test_same_clock_cannot_be_shared_between_branches():
    clock = ConstructedClock()
    with pytest.raises(ValueError, match="BRANCH_CLOCK_REUSED"):
        probe_operations(fixture(), prefix_cpu_seconds=0, clock_factory=lambda: clock)


def test_real_clock_fails_closed_without_signal_guard(monkeypatch):
    monkeypatch.delattr(engine.signal, "SIGPROF", raising=False)
    with pytest.raises(RuntimeError, match="LINUX_CPU_GUARD_REQUIRED"):
        probe_operations(fixture(), prefix_cpu_seconds=0,
                         clock_factory=lambda: engine.Clock(1))


def test_frozen_feature_name_is_global_mean_not_top_mean():
    state = fixture()
    state.model.p = np.array([0.99, 0.99, 0.99, 0.9, 0.3, 0.1])
    features = dict(zip(engine.FEATURE_NAMES, state.features(ConstructedClock()), strict=True))
    assert features["cached_top_mean"] == pytest.approx((0.9 + 0.3 + 0.1) / 3)


def test_frozen_cold_start_discards_forced_operation(monkeypatch):
    # Windows lacks SIGPROF: inject signal plumbing only for this logic test.
    monkeypatch.setattr(engine.signal, "SIGPROF", 27, raising=False)
    monkeypatch.setattr(engine.signal, "getsignal", lambda value: None)
    monkeypatch.setattr(engine.signal, "signal", lambda *args: None)
    monkeypatch.setattr(engine.Clock, "disarm", lambda: None)
    state = fixture("rf")
    state.observed = {}
    state.n0 = 0
    state.budget = 1
    state.deliveries = 0
    state.hits = 0
    out, _ = engine.run(state, Oracle([1, 0, 0, 1, 0, 1], 1),
                        ConstructedClock(), "G1", forced="PLAN")
    assert out["trace"][0]["actual_operation"] == "COLD_UNIFORM"
    assert out["operations"] == dict(REUSE=0, UPDATE=0, PLAN=0)
