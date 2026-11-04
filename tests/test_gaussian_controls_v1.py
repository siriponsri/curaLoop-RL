from dataclasses import replace

import numpy as np
import pytest
from sklearn.gaussian_process import GaussianProcessRegressor

from research.development.gaussian_controls_v1 import (
    GP_METHODS,
    GaussianSelector,
    IndexedTanimoto,
    pending_variance,
    tanimoto_gram,
)
from research.development.gaussian_runner_v1 import run_one
from research.event_time import Candidate, Observation, Result


def observation():
    candidates = tuple(
        Candidate(c, f)
        for c, f in (
            ("s0", (0.0, 1.0, 0.0)),
            ("s1", (1.0, 1.0, 0.0)),
            ("near", (1.0, 0.0, 0.0)),
            ("far", (0.0, 0.0, 1.0)),
            ("pending", (1.0, 0.0, 0.0)),
        )
    )
    return Observation(
        1,
        12,
        11,
        candidates,
        ("far", "near"),
        ("pending",),
        (Result("s0", False, 0), Result("s1", True, 0)),
        (),
        (),
        tuple((c.candidate_id, 1) for c in candidates),
        1,
        24,
    )


def test_binary_tanimoto_kernel_matches_set_similarity_and_is_psd():
    x = np.array([[1, 0, 1], [1, 1, 0], [0, 0, 0], [0, 0, 0]])
    k = tanimoto_gram(x)
    assert k[0, 1] == pytest.approx(1 / 3) and k[2, 3] == 1 and k[0, 2] == 0
    assert np.linalg.eigvalsh(k).min() >= -1e-12
    with pytest.raises(ValueError):
        tanimoto_gram([[0.2, 1]])


def test_pending_variance_equals_direct_augmented_gp_but_not_pending_labels():
    gram = tanimoto_gram(np.array([[1, 0, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]]))
    g = GaussianProcessRegressor(kernel=IndexedTanimoto(gram), optimizer=None, alpha=0.1)
    g.fit([[0], [1]], [0, 1])
    means, cov = g.predict([[2], [3]], return_cov=True)
    reduced = pending_variance(cov, 1)
    for invented_pending_label in (0.0, 1.0):
        augmented = GaussianProcessRegressor(
            kernel=IndexedTanimoto(gram), optimizer=None, alpha=0.1
        )
        augmented.fit([[0], [1], [3]], [0, 1, invented_pending_label])
        _, std = augmented.predict([[2]], return_std=True)
        assert reduced[0] == pytest.approx(std[0] ** 2)
    np.testing.assert_array_equal(pending_variance(cov, 2), np.diag(cov))
    assert np.isfinite(means).all()


def test_conditioning_reduces_near_pending_variance_and_can_change_rank():
    # Query order is far, near, pending; equal means remain untouched.
    class PublicPosterior:
        def predict(self, x, return_cov):
            n = len(x)
            return np.array([0.45, 0.5, 0.5])[:n], np.array(
                [[1.0, 0.0, 0.0], [0.0, 1.0, 0.9], [0.0, 0.9, 1.0]]
            )[:n, :n]

    obs = observation()
    selectors = [GaussianSelector(m, 0) for m in ("gp_ucb_blind", "gp_ucb_pending")]
    for s in selectors:
        s.indices = {c.candidate_id: i for i, c in enumerate(obs.candidates)}
        s.initialized = True
        s.signature = tuple((r.candidate_id, r.active) for r in obs.initial_results)
        s.model = PublicPosterior()
    blind, pending = [s.choose(obs) for s in selectors]
    assert blind[0] == ("near",) and pending[0] == ("far",)
    assert all(
        x["predicted_probability"] is None for _, trace in (blind, pending) for x in trace["chosen"]
    )


@pytest.mark.parametrize("method", GP_METHODS)
def test_row_order_and_one_class_fallback_are_explicit(method):
    obs = observation()
    reverse = replace(
        obs,
        candidates=tuple(reversed(obs.candidates)),
        eligible_ids=tuple(reversed(obs.eligible_ids)),
        initial_results=tuple(reversed(obs.initial_results)),
    )
    assert (
        GaussianSelector(method, 0).choose(obs)[0] == GaussianSelector(method, 0).choose(reverse)[0]
    )
    selector = GaussianSelector(method, 0)
    selector.choose(replace(obs, initial_results=(Result("s0", False, 0),)))
    assert selector.report()["fallback_reasons"] == {"ONE_CLASS_RANDOM": 1}


def test_same_method_campaigns_have_independent_fitted_models():
    a, b = GaussianSelector("gp_mean", 0), GaussianSelector("gp_mean", 0)
    a.choose(observation())
    b.choose(observation())
    assert a.model is not b.model and a.model.kernel_ is not b.model.kernel_


def constructed_cohort():
    return {
        "task_id": "constructed-gaussian-v1",
        "records": [
            {
                "candidate_id": f"c{i:02d}",
                "active": i % 3 == 0,
                "morgan_on_bits": [i % 6, (i + 1) % 6],
                "scaffold": str(i % 2),
            }
            for i in range(18)
        ],
    }


def test_common_delay_pair_and_hidden_future_labels_boundary():
    cohort = constructed_cohort()
    cfg = {
        "initial_count": 6,
        "budget": 6,
        "capacity": 2,
        "deadline": 6,
        "conditions": {"common": [2]},
    }
    a, b = [run_one(cohort, cfg, 2, "common", m) for m in ("gp_ucb_blind", "gp_ucb_pending")]
    assert a["snapshot"]["events"] == b["snapshot"]["events"]
    changed = {
        **cohort,
        "records": [
            {
                **r,
                "active": r["active"] if r["candidate_id"] in a["initial_ids"] else not r["active"],
            }
            for r in cohort["records"]
        ],
    }
    altered = run_one(changed, cfg, 2, "common", "gp_ucb_blind")
    assert a["decisions"][0] == altered["decisions"][0]
    assert a["schedule_sha256"] == altered["schedule_sha256"]
