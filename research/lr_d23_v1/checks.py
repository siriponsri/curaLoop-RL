"""Eight constructed mechanism/guard checks, the last requiring Linux SIGPROF."""

import copy

import numpy as np

from research.lr_d23_v1.policy import ResidualState
from research.m2_costed_v2.engine import Clock, Oracle, PublicPool, run
from research.m2_v1.models import synthetic_pool


def artifact(value):
    return {"schema": "curaloop.lr_d23.gate.v1", "feature_indices": list(range(8)),
            "mean": [0.] * 8, "scale": [1.] * 8, "coefficients": [0.] * 8, "intercept": value}


class FixedClock:
    cap = 1.

    def remaining(self):
        return .8

    def spent(self):
        return .2

    def enough(self, cost=0.):
        return .8 > cost + .002


def state(value=.5):
    x, _, ids = synthetic_pool(128, 37)
    value = ResidualState(PublicPool("constructed", "c0", tuple(ids), x), "neighbor", 71, 2, 32,
                          dict(REUSE=.00001, UPDATE=.00001, PLAN=.1),
                          control="candidate_v1", gate_artifact=artifact(value))
    value.observed = {0: 1, 1: 0}
    value.model.update(value.observed)
    value.observed[2] = 1
    return value


def checks(include_signal=True):
    rows = []
    def ok(name, condition):
        assert condition, name
        rows.append({"name": name, "status": "PASS"})
    fixed = FixedClock()
    a = state()
    ok("eight-delivered-information-features", a.residual_features(fixed).shape == (8,))
    ok("positive-residual-overrides-reuse-with-update", a.choose_operation("D23", fixed)[0] == "UPDATE")
    b = state(-.5)
    b.observed[3] = 0
    ok("negative-residual-overrides-incumbent-update", b.choose_operation("D23", fixed)[0] == "REUSE")
    c = state(.25)
    ok("deadband-boundary-keeps-Gk2", c.choose_operation("D23", fixed)[0] == "REUSE")
    a.costs["UPDATE"] = 2.
    ok("no-free-override-when-update-infeasible", a.choose_operation("D23", fixed)[0] == "REUSE"
       and a.gate_log[-1]["feasibility_fallback"])
    snap = b.snapshot(fixed)
    restored = ResidualState.restore_residual(b.pool, b.kind, b.seed, b.n0, b.budget, snap,
                                              b.similarity, b.neighbors, b.control, artifact(-.5))
    ok("snapshot-preserves-public-state-and-decisions", np.array_equal(b.residual_features(fixed), restored.residual_features(fixed))
       and b.choose_operation("D23", fixed) == restored.choose_operation("D23", fixed))
    original = state()
    changed = copy.deepcopy(original)
    # These arrays are evaluator-only; neither is attached to policy State.
    labels = np.zeros(128, dtype=int)
    labels[:3] = [1, 0, 1]
    altered = labels.copy()
    altered[3:] = 1
    assert Oracle(labels, 32).initial([0, 1, 2]) == Oracle(altered, 32).initial([0, 1, 2])
    ok("hidden-label-permutation-invariant", np.array_equal(original.residual_features(fixed), changed.residual_features(fixed))
       and original.choose_operation("D23", fixed) == changed.choose_operation("D23", fixed))
    if include_signal:
        value = state()
        cache = value.model.p.copy()
        def busy(observed):
            while True:
                pass
        value.model.update = busy
        outcome, _ = run(value, Oracle(labels, 32), Clock(.04), "D23")
        ok("actual-cpu-interrupt-retains-cache-and-query-boundary", outcome["interruptions"] > 0
           and outcome["new_deliveries"] == 0 and not outcome["cpu_violation"]
           and np.array_equal(cache, value.model.p))
    return {"status": "PASS", "checks": rows, "biological_records": False}
