"""Constructed residual/outer-fold leakage checks; no molecular inputs."""

import copy

import numpy as np
import pytest

from research.lr_d23_v1.checks import FixedClock, artifact, checks, state
from research.lr_d23_v1.learning import fit_gate
from research.lr_d23_v1.policy import NO_HISTORY_KEEP, Gate, ResidualState, selector


def training_rows():
    return [dict(heldout="g0", component=g, task_id=g + "-task", round=1, eligible=True,
                 features=[i / 32, .5, .1, .01, .2, .5, .25, 1],
                 update_minus_reuse=(i % 3) - 1, behavior_training_components=["g1", "g2", "g3"])
            for g in ("g1", "g2", "g3") for i in range(12)]


def test_constructed_non_signal_boundary_checks():
    assert len(checks(include_signal=False)["checks"]) == 7


@pytest.mark.parametrize("gain", [-.25, 0, .25])
def test_deadband_does_not_replace_the_incumbent(gain):
    value = state(gain)
    assert value.choose_operation("D23", FixedClock())[0] == "REUSE"
    value.observed[3] = 0
    assert value.choose_operation("D23", FixedClock())[0] == "UPDATE"


def test_features_never_fit_a_shadow_model(monkeypatch):
    value = state()
    before = value.model.p.copy()
    monkeypatch.setattr(value.model, "update", lambda observed: pytest.fail("FREE_REFIT"))
    value.residual_features(FixedClock())
    value.choose_operation("D23", FixedClock())
    assert np.array_equal(before, value.model.p)


def test_outer_component_cannot_enter_gate_training():
    rows = training_rows()
    rows[0]["component"] = "g0"
    with pytest.raises(AssertionError, match="OUTER_FOLD_CONTAMINATION"):
        fit_gate(rows, "g0", ["g1", "g2", "g3"], 1)


def test_heldout_labels_cannot_leak_through_behavior_policy():
    rows = training_rows()
    rows[0]["behavior_training_components"] = ["g0", "g1", "g2"]
    with pytest.raises(AssertionError, match="BEHAVIOR_POLICY_LEAKAGE"):
        fit_gate(rows, "g0", ["g1", "g2", "g3"], 1)


def test_inadequate_executed_support_is_not_replaced_or_fitted():
    with pytest.raises(ValueError, match="INSUFFICIENT_EXECUTED_SUPPORT"):
        fit_gate(training_rows()[:20], "g0", ["g1", "g2", "g3"], 1)


def test_training_weights_and_no_history_have_frozen_contract():
    rows = training_rows()
    before = copy.deepcopy(rows)
    full = fit_gate(rows, "g0", ["g1", "g2", "g3"], 1)
    stripped = fit_gate(rows, "g0", ["g1", "g2", "g3"], 1, True)
    assert full["training_states"] == 36 and full["training_components"] == ["g1", "g2", "g3"]
    assert stripped["feature_indices"] == list(NO_HISTORY_KEEP)
    assert np.isfinite(Gate(full).predict(rows[0]["features"]))
    assert rows == before


def test_final_gate_uses_only_round_one_targets():
    rows = training_rows()
    rows[0]["round"] = 0
    with pytest.raises(AssertionError, match="OUTER_FOLD_CONTAMINATION"):
        fit_gate(rows, "g0", ["g1", "g2", "g3"], 1)


def test_nan_gate_coefficients_do_not_get_silent_fallback():
    bad = artifact(.5)
    bad["coefficients"][0] = float("nan")
    with pytest.raises(AssertionError):
        Gate(bad)


def test_restored_training_branch_keeps_prefix_history_counts():
    value = state()
    value.interruptions = 2
    value.feasibility_fallbacks = 3
    saved = value.snapshot(FixedClock())
    restored = ResidualState.restore_residual(value.pool, value.kind, value.seed, value.n0,
                                              value.budget, saved, value.similarity, value.neighbors,
                                              "candidate_v1", artifact(.5))
    assert restored.interruptions == 2 and restored.feasibility_fallbacks == 3
    assert selector("candidate_v1") == ("D23", None)
    assert selector("Gk2") == ("Gk", 2)
