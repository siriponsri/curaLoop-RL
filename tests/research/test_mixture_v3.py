"""Independent conditional-label, probability interval and exact-rank checks."""

import numpy as np
import pytest

from research.planning_v3.mixture import Mixture, weighted_top


def test_joint_labels_condition_parameter_weights_not_sampled_label_vectors():
    p = np.array([[0.1, 0.7, 0.3], [0.8, 0.2, 0.9]])
    w = np.array([0.3, 0.7])
    model = Mixture(p, w)
    for labels, mass, q in model.label_branches((0, 1)):
        likelihood = np.array(
            [
                np.prod([p[m, i] if y else 1 - p[m, i] for i, y in enumerate(labels)])
                for m in range(2)
            ]
        )
        assert mass == pytest.approx(w @ likelihood)
        assert q == pytest.approx(w * likelihood / mass)
    assert sum(mass for _, mass, _ in model.label_branches((0, 1))) == pytest.approx(1)
    assert model.label_branches(())[0][1] == pytest.approx(1)


def test_weighted_tail_partial_selection_must_sort_selected_values():
    assert weighted_top([0.2, 0.9, 0.8, 0.1], [1, 0.5]) == pytest.approx(1.3)
    assert weighted_top([0.2, 0.9], []) == 0
    with pytest.raises(ValueError):
        weighted_top([0.2, 0.9], [0.5, 1])


@pytest.mark.parametrize("seed", range(8))
def test_probability_rank_and_weighted_tail_bounds_cover_dense_reference(seed):
    rng = np.random.default_rng(seed)
    p = rng.uniform(0, 1, (5, 31))
    w = rng.dirichlet(np.ones(5))
    model = Mixture(p, w)
    rows = []
    for _ in range(9):
        q = rng.dirichlet(np.ones(5))
        eligible = sorted(rng.choice(31, size=23, replace=False).tolist())
        lo, hi = model.intervals(q, eligible)
        exact = q @ p[:, eligible]
        assert np.all(lo <= exact + 1e-12) and np.all(exact <= hi + 1e-12)
        rows.append((q, eligible, (1, 0.8, 0.5, 0.1)))
    dense, _ = model.dense_batch(rows)
    for fallback in (0, 0.7, 1):
        screened, _ = model.screened_batch(rows, fallback)
        assert screened == pytest.approx(dense, abs=1e-11)


def test_zero_support_exact_probabilities_and_deterministic_ties():
    model = Mixture([[0, 1, 0.5], [1, 0, 0.5]], [1, 0])
    branches = model.label_branches((0, 1))
    assert len(branches) == 1 and branches[0][0] == (0, 1)
    assert branches[0][2] == pytest.approx([1, 0])
    with pytest.raises(ValueError, match="positive prior support"):
        model.intervals([0.5, 0.5], [0, 1])
    tied = Mixture([[0.5] * 8, [0.5] * 8], [0.5, 0.5])
    values, records = tied.screened_batch([([0.8, 0.2], list(range(8)), [1, 1])], 1)
    assert values[0] == 1 and records[0]["kept_by_bounds"] == 8
    assert not tied.p.flags.writeable


def test_screening_can_safely_remove_separated_candidates_and_k_zero():
    model = Mixture([[0.9, 0.8, 0.1, 0.01], [0.91, 0.81, 0.11, 0.02]], [0.5, 0.5])
    values, record = model.screened_batch(
        [([0.6, 0.4], [0, 1, 2, 3], [1, 0.5]), ([0.6, 0.4], [], [])], 1
    )
    assert values[0] == pytest.approx(0.904 + 0.5 * 0.804)
    assert record[0]["exact_refined"] == 2
    assert values[1] == 0


def test_extreme_positive_support_uses_finite_tv_bound_when_chi_overflows():
    model = Mixture([[0, 0.5], [1, 0.5]], [1, 1e-320])
    lo, hi = model.intervals([0, 1], [0, 1])
    assert np.isfinite(lo).all() and np.isfinite(hi).all()
    assert lo[1] == hi[1] == 0.5
    assert lo[0] <= 1 <= hi[0]
