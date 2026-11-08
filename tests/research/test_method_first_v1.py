"""Constructed mechanism checks; no molecular datasets or outcome files."""

from dataclasses import asdict
from math import isclose

import pytest

from research.method_first_v1.rollout import ScenarioRollout

WORLDS = ((1, 1, 0), (1, 0, 1), (0, 1, 0), (0, 0, 1))
PRIOR = (0.3, 0.3, 0.2, 0.2)


def independent_return(model, true_world, first_action, budget, observed=None):
    """Direct per-world path calculation, without the reference's trace cache."""
    seen = dict(observed or {})
    reward = 0
    for step in range(budget):
        consistent = [j for j, w in enumerate(model.worlds)
                      if all(w[a] == y for a, y in seen.items())]
        if step == 0 and first_action is not None:
            action = first_action
        else:
            action = max((a for a in range(model.n) if a not in seen),
                         key=lambda a: (sum(model.mixture[j] * model.worlds[j][a]
                                            for j in consistent), -a))
        seen[action] = true_world[action]
        reward += true_world[action]
    return reward


def test_nonmyopic_mechanism_known_analytical_example():
    model = ScenarioRollout(WORLDS, (PRIOR,))
    decision = model.choose({}, 2)
    assert decision.baseline_action == 0
    assert decision.action == 1
    assert isclose(decision.lower_gain_in_declared_models, 0.2, abs_tol=1e-12)
    # Baseline expectation 1.1, deviation-then-Greedy expectation 1.3.
    assert isclose(sum(p * independent_return(model, w, None, 2)
                       for p, w in zip(PRIOR, WORLDS)), 1.1)


def test_robust_gate_rejects_nominal_optimism():
    model = ScenarioRollout(WORLDS, (PRIOR, (0, 1, 0, 0)))
    robust = model.choose({}, 2, objective='robust')
    nominal = model.choose({}, 2, objective='mixture')
    assert robust.action == robust.baseline_action == 0
    assert nominal.action != nominal.baseline_action
    assert robust.lower_gain_in_declared_models == 0
    assert nominal.lower_gain_in_declared_models is None
    # This conservative fallback can forgo a positive mixture expectation.


def test_last_label_reduces_to_common_greedy():
    decision = ScenarioRollout(WORLDS, (PRIOR,)).choose({}, 1)
    assert decision.action == decision.baseline_action == 0


def test_model_conditional_certificate_is_not_real_world_safety():
    model = ScenarioRollout(WORLDS, (PRIOR,))
    decision = model.choose({}, 2)
    outside_declared_support = (1, 0, 0)
    assert decision.lower_gain_in_declared_models > 0
    actual_gate = independent_return(model, outside_declared_support, decision.action, 2)
    actual_baseline = independent_return(model, outside_declared_support, None, 2)
    assert actual_gate < actual_baseline


@pytest.mark.parametrize('budget', [1, 2, 3])
def test_cached_uncached_and_independent_enumerator_agree(budget):
    model = ScenarioRollout(WORLDS, (PRIOR, (0.2, 0.4, 0.3, 0.1)))
    cached = model.choose({}, budget)
    plain = model.choose({}, budget, use_cache=False)
    assert cached.action == plain.action
    assert isclose(cached.lower_gain_in_declared_models,
                   plain.lower_gain_in_declared_models, abs_tol=1e-12)
    baseline = [independent_return(model, w, None, budget) for w in WORLDS]
    alternative = [independent_return(model, w, cached.action, budget) for w in WORLDS]
    differences = [a - b for a, b in zip(alternative, baseline)]
    exact = min(sum(p * d for p, d in zip(row, differences)) for row in model.models)
    assert exact >= -1e-12
    assert isclose(exact, cached.lower_gain_in_declared_models, abs_tol=1e-12)
    assert cached.state_evaluations <= plain.state_evaluations


def test_trace_reuse_is_observable_without_a_wall_clock_claim():
    model = ScenarioRollout(WORLDS, (PRIOR,))
    cached, plain = model.choose({}, 3), model.choose({}, 3, use_cache=False)
    assert cached.cache_hits > 0
    assert cached.state_evaluations < plain.state_evaluations


@pytest.mark.parametrize('cap', [0, 1, 3, 8])
def test_interruption_never_uses_a_partial_score(cap):
    model = ScenarioRollout(WORLDS, (PRIOR,))
    decision = model.choose({}, 2, max_states=cap)
    assert decision.state_evaluations <= cap
    if decision.action != decision.baseline_action:
        assert decision.evaluated_alternatives > 0
        exact = sum(p * (independent_return(model, w, decision.action, 2) -
                         independent_return(model, w, None, 2))
                    for p, w in zip(PRIOR, WORLDS))
        assert isclose(exact, decision.lower_gain_in_declared_models)
        assert exact > 0


def test_delivered_labels_condition_predictions_and_exclude_repeats():
    model = ScenarioRollout(WORLDS, (PRIOR,))
    decision = model.choose({1: 0}, 1)
    assert decision.action == 2
    assert decision.action not in {1: 0}


def test_impossible_delivered_observation_is_rejected():
    with pytest.raises(ValueError, match='contradict'):
        ScenarioRollout(WORLDS, (PRIOR,)).choose({1: 1, 2: 1}, 1)


def test_zero_posterior_model_is_not_divided_by_zero():
    model = ScenarioRollout(WORLDS, ((1, 0, 0, 0), (0, 1, 0, 0)))
    assert model.choose({1: 0}, 1).action == 0  # deterministic tie by candidate ID


@pytest.mark.parametrize('probabilities', [(-1, 1, 1, 1), (0, 0, 0, 0),
                                          (float('nan'), 1, 1, 1), (1, 1)])
def test_invalid_predictive_scenarios_fail_closed(probabilities):
    with pytest.raises(ValueError):
        ScenarioRollout(WORLDS, (probabilities,))


def test_budget_bounds_and_typed_decision_are_explicit():
    model = ScenarioRollout(WORLDS, (PRIOR,))
    for invalid in (0, 4, True):
        with pytest.raises(ValueError):
            model.choose({}, invalid)
    payload = asdict(model.choose({}, 2))
    assert 'action' in payload and 'interrupted' in payload
    assert not any('clinical' in key or 'oracle' in key for key in payload)
