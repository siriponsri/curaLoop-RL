"""Constructed mechanisms with analytic answers, independent of real assays."""

from itertools import product

import numpy as np
import pytest

from research.planning_v3.mixture import Mixture
from research.planning_v3.recourse import PublicState, RecoursePlanner


def test_xor_joint_information_beats_greedy_and_is_not_factorized():
    p = [[a, b, a ^ b, 1 - (a ^ b), 0.6] for a, b in product((0, 1), repeat=2)]
    planner = RecoursePlanner(Mixture(p, [0.25] * 4), (1,), 2)
    state = PublicState(2, 3, frozenset(), ())
    values, _ = planner.evaluate_actions(state, [(0, 1), (0, 4)])
    assert values == pytest.approx([2.0, 1.6])
    action, trace = planner.choose(state, shortlist=None)
    assert action == (0, 1) and trace["selected_value"] == pytest.approx(2)
    assert planner.choose(state, shortlist=4)[0] == (0, 1)


def test_pending_information_wait_reverses_at_tight_deadline():
    p = [[0, 0.01, 0.99, 0.01, 0.99], [1, 0.99, 0.01, 0.99, 0.01]]
    planner = RecoursePlanner(Mixture(p, [0.5, 0.5]), (2,), 2)
    roomy = PublicState(4, 2, frozenset({0}), ((0, 0),))
    tight = PublicState(2, 2, frozenset({0}), ((0, 0),))
    assert planner.choose(roomy, shortlist=None)[0] == ()
    assert planner.choose(tight, shortlist=None)[0] != ()
    values, _ = planner.evaluate_actions(roomy, [(), (1,)])
    assert values == pytest.approx([2.48, 1.99])
    blinded, _ = planner.evaluate_actions(roomy, [()], suppress_pending_information=True)
    assert blinded == pytest.approx([1.5])


def test_direct_pending_reward_retained_once_at_deadline_with_no_budget():
    planner = RecoursePlanner(Mixture([[0.7, 0.2]], [1]), (2,), 2)
    for horizon, expected in ((1, 0), (2, 0.7), (3, 0.7)):
        state = PublicState(horizon, 0, frozenset({0}), ((0, 0),))
        values, trace = planner.evaluate_actions(state, [()])
        assert values == pytest.approx([expected])
        assert trace["branches"] == 0


def test_deterministic_sequential_ens_limit_matches_direct_two_step_enumeration():
    model = Mixture([[0.1, 0.7, 0.2], [0.9, 0.2, 0.8]], [0.4, 0.6])
    planner = RecoursePlanner(model, (1,), 1)
    state = PublicState(2, 2, frozenset(), ())
    for i in range(3):
        expected = model.mu[i]
        for _, mass, q in model.label_branches((i,)):
            expected += mass * max(q @ model.p[:, [j for j in range(3) if j != i]])
        values, _ = planner.evaluate_actions(state, [(i,)])
        assert values == pytest.approx([expected])


@pytest.mark.parametrize("seed", range(5))
def test_dense_screened_actions_values_and_ties_match(seed):
    rng = np.random.default_rng(seed)
    model = Mixture(rng.uniform(0.01, 0.99, (4, 8)), rng.dirichlet(np.ones(4)))
    planner = RecoursePlanner(model, (1, 2, 4), 2)
    state = PublicState(4, 3, frozenset({0, 1}), ((1, 1),))
    dense, dt = planner.choose(state, shortlist=None)
    screened, st = planner.choose(state, screened=True, shortlist=None)
    assert dense == screened
    assert [a["value"] for a in dt["actions"]] == pytest.approx(
        [a["value"] for a in st["actions"]], abs=1e-10
    )


def test_all_accepted_ids_excluded_and_invalid_wait_rejected():
    planner = RecoursePlanner(Mixture([[0.9, 0.1, 0.8]], [1]), (1,), 2)
    state = PublicState(2, 1, frozenset({0}), ())
    actions = planner.actions(state, shortlist=None)
    assert actions and all(0 not in a for a in actions)
    with pytest.raises(ValueError, match="Infeasible root"):
        planner.evaluate_actions(state, [()])
    with pytest.raises(ValueError, match="already be accepted"):
        planner.actions(PublicState(2, 1, frozenset(), ((0, 0),)))


def test_timing_blind_tail_is_identified_as_count_proxy():
    planner = RecoursePlanner(Mixture([[0.9, 0.8, 0.7, 0.6]], [1]), (2,), 1)
    state = PublicState(3, 4, frozenset(), ())
    true, tt = planner.evaluate_actions(state, [(0,)])
    proxy, pt = planner.evaluate_actions(state, [(0,)], timing_blind_tail=True)
    assert true == pytest.approx([0.9]) and proxy == pytest.approx([3.0])
    assert tt["objective"] == "expected_additional_delivered_positives_fixed_list_recourse"
    assert pt["objective"] == "deadline_direct_plus_count_tail_PROXY"


def test_numerical_tie_loss_is_reported_instead_of_zero_certificate(monkeypatch):
    planner = RecoursePlanner(Mixture([[0.9, 0.8]], [1]), (1,), 1)
    monkeypatch.setattr(
        planner, "evaluate_actions", lambda *args, **kwargs: ([1.0, 1.0 + 5e-13], {})
    )
    action, trace = planner.choose(PublicState(1, 1, frozenset(), ()), shortlist=None)
    assert action == (0,)
    assert trace["gap"] == pytest.approx(5e-13, abs=1e-15, rel=0)
    assert trace["numerical_tie_tolerance"] == 1e-12


def test_count_budget_ens_proxy_ignores_deadline_for_its_acquisition_objective():
    planner = RecoursePlanner(Mixture([[0.9, 0.8, 0.7, 0.6]], [1]), (2,), 1)
    state = PublicState(1, 4, frozenset(), ())
    true, _ = planner.evaluate_actions(state, [(0,)])
    count, trace = planner.evaluate_actions(state, [(0,)], count_budget_proxy=True)
    assert true == pytest.approx([0]) and count == pytest.approx([3])
    assert trace["objective"] == "expected_additional_count_budget_PROXY"
    with pytest.raises(ValueError, match="separate arms"):
        planner.evaluate_actions(state, [(0,)], count_budget_proxy=True, timing_blind_tail=True)
