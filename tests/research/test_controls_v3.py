"""Comparator invariants independent of any real assay labels."""

import pytest

from research.planning_v3.controls import CountProxyScheduler, greedy_rollout_values, uniform
from research.planning_v3.mixture import Mixture
from research.planning_v3.recourse import PublicState, RecoursePlanner


def test_count_scheduler_has_information_waiting_and_explicit_scope():
    scheduler = CountProxyScheduler((2,), 2)
    size, trace = scheduler.choose_size(3, 2, (1,), 0)
    assert size == 0  # Wait for the first completion, then launch both with feedback.
    assert trace["objective"] == "COMPLETION_FIRST_CPE_COUNT_PROXY" and trace["fallback"] is None
    assert (
        scheduler.choose_size(1, 2, (1,), 0)[0] == 1
    )  # No later launch has value; work-conserving tie.


def test_count_proxy_cap_is_reported_without_claiming_an_exact_value():
    scheduler = CountProxyScheduler((1, 2, 4), 2, state_limit=0)
    size, trace = scheduler.choose_size(5, 3, (0,), 0)
    assert size == 1 and trace["fallback"] == "CPE_STATE_LIMIT_WORK_CONSERVING_FALLBACK"
    assert "completion_count_gap" not in trace


def test_full_rollout_counts_pending_and_new_positives_once_in_deterministic_case():
    planner = RecoursePlanner(Mixture([[1, 1, 0, 1]], [1]), (1,), 2)
    state = PublicState(2, 2, frozenset({0}), ((0, 0),))
    values, trace = greedy_rollout_values(planner, state, [(), (1,), (2,)], 7, 16)
    assert values == pytest.approx([3, 3, 2])
    assert trace["certified_gap"] is None and not trace["actual_assay_outcomes_accessed"]


def test_rollout_repeatability_and_root_action_order_share_virtual_random_numbers():
    planner = RecoursePlanner(
        Mixture([[0.2, 0.8, 0.1, 0.6], [0.8, 0.1, 0.7, 0.3]], [0.4, 0.6]), (1, 2, 4), 2
    )
    state = PublicState(4, 2, frozenset({0}), ((0, 1),))
    forward, _ = greedy_rollout_values(planner, state, [(), (1,), (2,)], 9, 16)
    reverse, _ = greedy_rollout_values(planner, state, [(2,), (1,), ()], 9, 16)
    assert forward == list(reversed(reverse))
    assert all(0 <= uniform(i, "test", i) < 1 for i in range(100))
    with pytest.raises(ValueError, match="event limit"):
        greedy_rollout_values(planner, PublicState(4, 30, frozenset({0}), ((0, 1),)), [()], 9, 16)


def test_completion_priority_does_not_trade_a_finished_experiment_for_more_launch_information():
    scheduler = CountProxyScheduler((2,), 2)
    size, trace = scheduler.choose_size(3, 2, (1,), 0)
    assert size == 0
    assert trace["expected_additional_completion_count"] == 3
    assert trace["expected_CPE"] == 2
    assert scheduler.choose_size(2, 2, (1,), 0)[0] == 1


def test_nondegenerate_rollout_mean_matches_analytic_two_step_value_with_MC_noise_visible():
    planner = RecoursePlanner(Mixture([[0.1, 0.9, 0.2], [0.9, 0.1, 0.8]], [0.5, 0.5]), (1,), 1)
    state = PublicState(2, 2, frozenset(), ())
    values, trace = greedy_rollout_values(planner, state, [(0,)], 17, 4096)
    assert values[0] == pytest.approx(1.28, abs=0.05)
    assert len(trace["root_trajectory_samples"][0]) == 4096
    assert trace["root_MC_standard_errors"][0] > 0
    assert trace["MC_error_is_not_family_or_scientific_uncertainty"]
