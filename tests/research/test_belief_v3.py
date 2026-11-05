"""Predictor information-boundary, proper-prior and nested-draw regressions."""

import numpy as np
import pytest

from research.planning_v3.belief import fit_mixture, make_design, objective


def fixture():
    return make_design(["a", "b", "c", "d"], [0b0011, 0b0110, 0b1100, 0b1001], 3)


def test_gradient_matches_independent_finite_differences():
    x = np.array([[1, 0.2], [1, 0.8], [1, 0.5]])
    y = np.array([0, 1, 1])
    beta = np.array([-0.3, 0.4])
    precision = np.array([0.25, 1])
    _, gradient = objective(beta, x, y, precision)
    for i in range(2):
        change = np.eye(2)[i] * 1e-6
        difference = (
            objective(beta + change, x, y, precision)[0]
            - objective(beta - change, x, y, precision)[0]
        ) / 2e-6
        assert gradient[i] == pytest.approx(difference, abs=1e-8)


def test_public_anchor_design_is_order_invariant_and_retains_distinct_ids():
    a = fixture()
    b = make_design(["d", "c", "b", "a"], [0b1001, 0b1100, 0b0110, 0b0011], 3)
    assert a.feature_sha256 == b.feature_sha256
    assert np.array_equal(a.x, b.x)
    duplicate = make_design(["a", "b", "c"], [1, 1, 1], 3)
    assert len(set(duplicate.anchor_indices)) == 3
    assert not a.x.flags.writeable


def test_one_class_starts_fit_without_deleting_or_class_reweighting():
    design = fixture()
    zero, zt = fit_mixture(design, [("a", False), ("b", False)], 7, 32)
    one, ot = fit_mixture(design, [("a", True), ("b", True)], 7, 32)
    assert zt["fallback"] is None and ot["fallback"] is None
    assert zt["one_class_start_retained"] and ot["one_class_start_retained"]
    assert (zero.mu < 0.5).all() and (one.mu > 0.5).all()


def test_conditional_history_order_and_M_do_not_change_parameter_draw_prefix():
    design = fixture()
    small, st = fit_mixture(design, [("b", False), ("a", True)], 9, 32)
    large, lt = fit_mixture(design, [("a", True), ("b", False)], 9, 64)
    assert st["draw_seed"] == lt["draw_seed"]
    assert small.p == pytest.approx(large.p[:32], abs=1e-14)
    # Time, pending IDs, durations and resource hashes are absent from this API.
    again, _ = fit_mixture(design, [("a", True), ("b", False)], 9, 32)
    assert np.array_equal(small.p, again.p)


def test_empty_history_prior_is_proper_and_labels_must_be_explicit_known_set():
    design = fixture()
    model, trace = fit_mixture(design, [], 2, 32)
    assert model.mu == pytest.approx([0.5] * 4, abs=1e-14)
    assert trace["known_count"] == 0 and trace["fallback"] is None
    with pytest.raises(ValueError, match="Unique delivered"):
        fit_mixture(design, [("unseen", True)], 2, 32)
    with pytest.raises(ValueError, match="Unique delivered"):
        fit_mixture(design, [("a", False), ("a", True)], 2, 32)


@pytest.mark.parametrize("seed", [True, -1, 2**32, "resource-hash", {"time": 2}])
def test_seed_cannot_smuggle_timing_or_resource_objects(seed):
    with pytest.raises(ValueError, match="experiment seed"):
        fit_mixture(fixture(), [], seed, 32)


def test_optimizer_failure_is_explicit_prior_fallback(monkeypatch):
    from types import SimpleNamespace

    import research.planning_v3.belief as belief

    monkeypatch.setattr(
        belief, "minimize", lambda *args, **kwargs: SimpleNamespace(success=False, nit=100)
    )
    model, trace = fit_mixture(fixture(), [("a", True), ("b", False)], 3, 32)
    assert trace["fallback"] == "OPTIMIZER_DID_NOT_CONVERGE_PRIOR"
    assert model.mu == pytest.approx([0.5] * 4, abs=1e-14)


def test_cholesky_failure_is_explicit_prior_fallback(monkeypatch):
    import research.planning_v3.belief as belief

    def fail(*args, **kwargs):
        raise np.linalg.LinAlgError("constructed failure")

    monkeypatch.setattr(belief.np.linalg, "cholesky", fail)
    model, trace = fit_mixture(fixture(), [("a", True)], 3, 32)
    assert trace["fallback"] == "CHOLESKY_FAILURE_PRIOR"
    assert model.mu == pytest.approx([0.5] * 4, abs=1e-14)
