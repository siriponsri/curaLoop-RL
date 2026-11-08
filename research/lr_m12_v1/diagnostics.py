"""Trusted exposed-data diagnostics; no final-data path or M2 campaign handler."""

import hashlib
import json
import time
from pathlib import Path

import numpy as np

from research.lr_m12_v1.acquisition import acquire, payload
from research.lr_m12_v1.guard import write_new
from research.lr_m12_v1.predictor import fit_predictive, public_pool


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def adapter_diagnostics(arguments, task_root):
    design_path = Path(__file__).resolve().parents[2] / 'research/configs/lr_m12_m1_design_20261108_v1.json'
    assert digest(design_path) == arguments['design_sha256']
    cfg = json.loads(design_path.read_text())
    assert cfg['status'] == 'FROZEN_BEFORE_NEW_PREDICTOR_OR_METHOD_DIAGNOSTICS'
    assert cfg['m2_campaigns_released'] is False
    admitted = json.loads((task_root / 'inputs/manifest-v1.json').read_text())
    by_id = {r['task_id']: r for r in admitted['tasks'] if r['status'] == 'ADMITTED_EXPOSED_DEVELOPMENT'}
    tasks = arguments.get('task_ids', cfg['task_ids'])
    assert set(tasks).issubset(cfg['task_ids'])
    results = []
    for tid in tasks:
        row = by_id[tid]
        source = task_root / row['input_relative']
        assert row['input_relative'] == 'inputs/development/' + tid + '.json'
        assert digest(source) == row['input_sha256']
        source_data = json.loads(source.read_text())
        assert source_data['role'] == 'development' and source_data['task_id'] == tid
        # Trusted evaluator splits oracle data from the public predictor interface.
        ordered = sorted(source_data['records'], key=lambda r: hashlib.sha256(
            (tid + '|' + r['candidate_id'] + '|CuraLoopLRM12M1Pool-v1').encode()).hexdigest())
        for n in cfg['pool_sizes']:
            assert n <= len(ordered)
            selected = ordered[:n]
            public = public_pool([{'candidate_id': r['candidate_id'], 'morgan_on_bits': r['morgan_on_bits']}
                                  for r in selected])
            oracle = {r['candidate_id']: r['active'] for r in selected}
            for initial in cfg['initial_counts']:
                for seed in cfg['seeds']:
                    rng = np.random.default_rng(seed)
                    initial_ids = tuple(public.ids[i] for i in rng.choice(n, size=initial, replace=False))
                    delivered = tuple((cid, oracle[cid]) for cid in initial_ids)
                    started, cpu = time.monotonic(), time.process_time()
                    model = fit_predictive(public, delivered, seed)
                    fit_wall, fit_cpu = time.monotonic() - started, time.process_time() - cpu
                    query = [i for i, cid in enumerate(model.ids) if cid not in model.known_ids]
                    prediction = model.probabilities.mean(axis=(0, 1))[query]
                    labels = np.array([oracle[model.ids[i]] for i in query], dtype=float)
                    prediction = np.clip(prediction, 1e-9, 1 - 1e-9)
                    case = {'task_id': tid, 'pool_size': n, 'initial_count': initial, 'seed': seed,
                            'public_provenance': public.provenance, 'predictor_provenance': model.provenance,
                            'fit_wall_seconds': fit_wall, 'fit_cpu_seconds': fit_cpu,
                            'query_rows': len(query), 'brier': float(np.mean((prediction - labels)**2)),
                            'log_loss': float(-np.mean(labels*np.log(prediction) + (1-labels)*np.log1p(-prediction))),
                            'fit_fallbacks': [x['fallback'] for x in model.fitting_details],
                            'calibration_established': False, 'molecular_campaign': False, 'acquisition': []}
                    for variant in ('nominal', 'point_min', 'confidence_min'):
                        started_cpu = time.process_time()
                        decision = acquire(model, min(16, len(query)), seed + 991,
                            variant=variant, shortlist=min(cfg['candidate_shortlist'], len(query)),
                            horizon=cfg['timing_horizon'], samples=cfg['point_rollout_samples_per_model'],
                            stages=tuple(cfg['rollout_sample_stages']), delta=cfg['revision_2_confidence_delta'],
                            max_states=cfg['max_greedy_states_per_call'], max_pairs=cfg['max_paired_traces_per_call'],
                            wall_seconds=cfg['planning_wall_seconds_per_call'])
                        entry = payload(decision)
                        entry['cpu_seconds'] = time.process_time() - started_cpu
                        entry['returned_feasible_unobserved'] = decision.candidate_id in public.ids and decision.candidate_id not in model.known_ids
                        assert entry['returned_feasible_unobserved']
                        case['acquisition'].append(entry)
                    # Noninterference: replacing held-back evaluation labels does
                    # not alter the feature/delivered input or predictive bundle.
                    alternative_oracle = {cid: (value if cid in model.known_ids else not value)
                                          for cid, value in oracle.items()}
                    assert tuple((cid, alternative_oracle[cid]) for cid in initial_ids) == delivered
                    assert model.known_ids == frozenset(initial_ids)
                    case['withheld_label_argument_absent_from_predictor_and_policy'] = True
                    results.append(case)
    assert sum(len(r['acquisition']) for r in results) <= cfg['diagnostic_cases_max']
    result = {'schema': 'curaloop.lr_m12.adapter_diagnostics.v1', 'tasks': tasks, 'cases': results,
              'case_count': len(results), 'timing_calls': sum(len(r['acquisition']) for r in results),
              'm2_campaigns_executed': 0, 'final_data_access': False,
              'predictor': 'Tanimoto logistic Bernoulli GP Laplace, fixed three kernel scales',
              'forecast': 'fixed posterior particles reweighted for fantasy observations; not future GP refit',
              'novelty_certified': False}
    write_new(task_root / 'diagnostics' / (arguments['output_name'] + '.json'), result)
    # Only aggregates return through controller stdout; full exposed traces stay private.
    return {'status': 'PASS_M1_EXPOSED_ADAPTER_DIAGNOSTICS', 'case_count': len(results),
            'timing_calls': result['timing_calls'], 'm2_campaigns_executed': 0,
            'final_data_access': False, 'output_relative': 'diagnostics/' + arguments['output_name'] + '.json'}
