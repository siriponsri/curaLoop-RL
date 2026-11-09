"""Constructed control behavior, without biological records."""

import numpy as np

from research.d1_v1.controls import DiagnosticState, selector
from research.m2_costed_v2.engine import PublicPool


class ConstructedClock:
    def enough(self, cost=0):
        return True

    def arm(self):
        pass

    def disarm(self):
        pass


def state(control):
    x = np.array([[1, 0], [1, 1], [0, 1], [1, 0]], dtype=np.uint8)
    pool = PublicPool("constructed", "constructed", tuple(map(str, range(4))), x)
    return DiagnosticState(pool, "rf", 19, 2, 3, dict(REUSE=.001, UPDATE=.01, PLAN=.1), control=control)


def test_frozen_cold_start_is_not_rescued_by_later_labels():
    value = state("frozen_cache_greedy")
    value.observed = {0: 1}
    assert value.initialize_model(ConstructedClock())
    value.observed[2] = 0
    assert value.initialize_model(ConstructedClock())
    assert value.model.fitted_observations == -1


def test_frozen_fit_does_not_refit_after_new_labels():
    value = state("frozen_cache_greedy")
    value.observed = {0: 1, 2: 0}
    assert value.initialize_model(ConstructedClock())
    cached = value.model.p.copy()
    value.observed[1] = 1
    assert value.initialize_model(ConstructedClock())
    assert value.initial_fit_count == 1
    assert np.array_equal(cached, value.model.p)


def test_nearest_hit_needs_only_delivered_positive_and_excludes_observed():
    value = state("nearest_hit")
    value.observed = {0: 1}
    assert not value.cold()
    assert value.initialize_model(ConstructedClock())
    chosen, actual = value.execute("REUSE", "REUSE", ConstructedClock())
    assert chosen == 3 and actual == "NEAREST_HIT"
    assert value.initial_fit_count == 0 and value.model.fitted_observations == -1


def test_nearest_no_active_has_declared_seeded_fallback():
    value = state("nearest_hit")
    value.observed = {0: 0}
    chosen, actual = value.execute("REUSE", "REUSE", ConstructedClock())
    assert actual == "NO_ACTIVE_SEEDED_FALLBACK"
    assert chosen == min(value.eligible(), key=lambda i: int(value.tie[i]))


def test_threshold_control_is_the_existing_Gk():
    assert selector("Gk_k4") == ("Gk", 4)
    assert selector("T_k4_tau0.05") == ("T", (4, .05))
