"""Constructed privacy, forecast and interrupted-computation checks."""

import dataclasses

import numpy as np

from research.lr_m12_v1.acquisition import acquire
from research.lr_m12_v1.predictor import fit_predictive, public_pool


def run_checks(arguments, task_root):
    checked = []
    rows = [{'candidate_id': 'c-' + str(i), 'morgan_on_bits': [i, i + 10]} for i in range(4)]
    pool = public_pool(rows)
    try:
        public_pool([dict(r, active=False) for r in rows])
        raise AssertionError('Forbidden field accepted')
    except ValueError:
        checked.append('oracle_fields_rejected_by_public_feature_interface')
    model = fit_predictive(pool, (('c-0', False),), 101)
    assert model.probabilities.shape == (3, 128, 4)
    assert np.isfinite(model.probabilities).all()
    assert not model.probabilities.flags.writeable
    checked.append('fixed_gp_contexts_one_class_start_and_immutable_joint_probabilities')
    duplicate = fit_predictive(pool, (('c-0', False),), 101)
    assert np.array_equal(model.probabilities, duplicate.probabilities)
    assert model.provenance == duplicate.provenance
    checked.append('deterministic_predictor_from_public_features_and_delivered_labels')
    try:
        fit_predictive(pool, (('c-0', 0),), 101)
        raise AssertionError('Implicit numeric label accepted')
    except ValueError:
        checked.append('explicit_boolean_delivered_labels_required')
    try:
        acquire({'probabilities': model.probabilities}, 2, 101, variant='point_min')
        raise AssertionError('Untyped input accepted')
    except ValueError:
        checked.append('typed_predictive_policy_boundary')
    for variant in ('nominal', 'point_min', 'confidence_min'):
        one = acquire(model, 1, 101, variant=variant, shortlist=3, horizon=1, wall_seconds=30)
        assert one.candidate_id == one.baseline_id and one.paired_traces == 0
        checked.append(variant + '_last_step_exact_greedy')
        stopped = acquire(model, 2, 101, variant=variant, shortlist=3, horizon=2,
                          max_states=0, wall_seconds=30)
        assert stopped.candidate_id == stopped.baseline_id and stopped.interrupted
        assert stopped.completed_comparisons == 0
        checked.append(variant + '_no_partial_score_after_compute_limit')
        decision = acquire(model, 2, 101, variant=variant, shortlist=3, horizon=2,
                           samples=8, stages=(8, 16), max_pairs=128, wall_seconds=30)
        assert decision.candidate_id not in model.known_ids
        assert decision.greedy_states <= 4096 and decision.paired_traces <= 128
        checked.append(variant + '_feasible_bounded_model_only_decision')
    altered = dataclasses.replace(model, probabilities=np.zeros_like(model.probabilities))
    try:
        acquire(altered, 2, 101, variant='point_min', shortlist=3, horizon=2)
        raise AssertionError('Degenerate forecast accepted')
    except ValueError:
        checked.append('invalid_forecast_fails_closed')
    for predictor_call in (True, False):
        try:
            if predictor_call:
                fit_predictive(pool, (('c-0', False),), 101, oracle={'c-1': True})
            else:
                acquire(model, 2, 101, variant='point_min', oracle={'c-1': True})
            raise AssertionError('Oracle keyword crossed the information boundary')
        except TypeError:
            checked.append(('predictor' if predictor_call else 'policy') + '_rejects_oracle_argument')
    return {'status': 'PASS_CONSTRUCTED_M1_CHECKS', 'count': len(checked), 'checks': checked,
            'actual_molecular_data_access': False, 'real_world_safety_or_novelty_proven': False}
