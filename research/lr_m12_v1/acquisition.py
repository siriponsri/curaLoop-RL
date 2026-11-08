"""Two declared robust-rollout adaptations and a shared nominal control.

Neither variant is claimed novel. Confidence is conditional on the frozen
predictive forecast, not on the real assay distribution or future GP refits.
"""

import math
import time
from dataclasses import asdict, dataclass

import numpy as np

from research.lr_m12_v1.predictor import PredictiveBundle


class ComputationStop(Exception):
    pass


@dataclass(frozen=True)
class Acquisition:
    candidate_id: str
    baseline_id: str
    variant: str
    score: float
    score_scope: str
    completed_comparisons: int
    paired_traces: int
    greedy_states: int
    cache_hits: int
    interrupted: bool
    wall_seconds: float
    predictor_provenance: str


def acquire(bundle, budget, seed, *, variant, shortlist=8, horizon=4,
            samples=16, stages=(8, 16, 32, 64), delta=0.05,
            max_states=4096, max_pairs=1024, wall_seconds=0.75):
    if type(bundle) is not PredictiveBundle or variant not in ('nominal', 'point_min', 'confidence_min'):
        raise ValueError('TYPED_PREDICTIVE_BUNDLE_AND_DECLARED_VARIANT_REQUIRED')
    probabilities = bundle.probabilities
    if probabilities.ndim != 3 or probabilities.shape[2] != len(bundle.ids):
        raise ValueError('PREDICTIVE_DIMENSION_MISMATCH')
    if not np.isfinite(probabilities).all() or np.any(probabilities <= 0) or np.any(probabilities >= 1):
        raise ValueError('FINITE_INTERIOR_BERNOULLI_FORECAST_REQUIRED')
    available = tuple(i for i, cid in enumerate(bundle.ids) if cid not in bundle.known_ids)
    if type(budget) is not int or not 1 <= budget <= len(available) or type(seed) is not int:
        raise ValueError('MEASUREMENT_BUDGET_OR_SEED')
    if not (1 <= shortlist <= len(available) and 1 <= horizon <= budget and
            0 < delta < 1 and samples > 0 and max_states >= 0 and max_pairs >= 0 and wall_seconds > 0):
        raise ValueError('POSITIVE_DECLARED_COMPUTATION_LIMITS_REQUIRED')
    if tuple(sorted(set(stages))) != tuple(stages) or not stages or stages[0] <= 0:
        raise ValueError('FIXED_INCREASING_SAMPLE_STAGES_REQUIRED')
    started = time.monotonic()
    model_count, function_count, n = probabilities.shape
    flat = probabilities.reshape(-1, n)
    mean = flat.mean(axis=0)
    baseline = min(available, key=lambda a: (-mean[a], a))
    # Equal treatment: every variant uses the same bounded candidate menu/cache.
    variance = flat.var(axis=0)
    candidates = sorted(available, key=lambda a: (-(mean[a] + np.sqrt(variance[a])), a))[:shortlist]
    if baseline not in candidates:
        candidates[-1] = baseline
    candidates = sorted(set(candidates))
    alternatives = [a for a in candidates if a != baseline]
    stats = {'states': 0, 'hits': 0, 'pairs': 0, 'completed': 0}
    state_cache, baseline_cache = {}, {}
    log_p, log_not_p = np.log(flat), np.log1p(-flat)

    def check():
        if time.monotonic() - started >= wall_seconds:
            raise ComputationStop

    def greedy(observed):
        check()
        key = tuple(sorted(observed))
        if key in state_cache:
            stats['hits'] += 1
            return state_cache[key]
        if stats['states'] >= max_states:
            raise ComputationStop
        stats['states'] += 1
        used = {a for a, _ in key}
        log_weight = np.zeros(len(flat))
        for a, y in key:
            log_weight += log_p[:, a] if y else log_not_p[:, a]
        weight = np.exp(log_weight - log_weight.max())
        weight /= weight.sum()
        p = weight @ flat
        action = min((a for a in available if a not in used), key=lambda a: (-p[a], a))
        state_cache[key] = action
        return action

    max_samples = max(samples, stages[-1])
    rng = np.random.default_rng(seed)
    predictive_worlds = []
    for model in probabilities:
        functions = rng.integers(0, function_count, size=max_samples)
        worlds = rng.random((max_samples, n)) < model[functions]
        predictive_worlds.append(worlds)

    def rollout(world, forced=None):
        seen, reward = [], 0
        for step in range(horizon):
            action = forced if step == 0 and forced is not None else greedy(seen)
            y = bool(world[action])
            seen.append((action, y))
            reward += int(y)
        return reward

    cache = {(model, a): [] for model in range(model_count) for a in alternatives}

    def extend(model, action, target):
        values = cache[model, action]
        while len(values) < target:
            check()
            if stats['pairs'] >= max_pairs:
                raise ComputationStop
            i = len(values)
            world = predictive_worlds[model][i]
            if (model, i) not in baseline_cache:
                baseline_cache[model, i] = rollout(world)
            comparison = rollout(world, action) - baseline_cache[model, i]
            values.append(comparison)
            stats['pairs'] += 1

    best, best_score, interrupted = baseline, 0.0, False
    try:
        if horizon == 1:
            pass  # Exact one-step common-mixture Greedy; avoid sampling noise.
        elif variant in ('nominal', 'point_min'):
            for action in alternatives:
                scores = []
                for model in range(model_count):
                    extend(model, action, samples)
                    scores.append(float(np.mean(cache[model, action][:samples])))
                score = float(np.mean(scores)) if variant == 'nominal' else min(scores)
                stats['completed'] += 1
                if score > best_score + 1e-12:
                    best, best_score = action, score
        else:
            # Fixed-stage union bound: all models/actions/stages simultaneously.
            multiplicity = max(1, model_count * len(alternatives) * len(stages))
            pending = set(alternatives)
            for target in stages:
                for action in sorted(pending):
                    lowers, uppers = [], []
                    for model in range(model_count):
                        extend(model, action, target)
                        estimate = float(np.mean(cache[model, action][:target]))
                        radius = horizon * math.sqrt(2 * math.log(2 * multiplicity / delta) / target)
                        lowers.append(max(-horizon, estimate - radius))
                        uppers.append(min(horizon, estimate + radius))
                    low, high = min(lowers), min(uppers)
                    stats['completed'] += 1
                    if low > best_score + 1e-12:
                        best, best_score = action, low
                    if high <= best_score:
                        pending.discard(action)
                if not pending:
                    break
    except ComputationStop:
        interrupted = True
    scope = ('SIMULTANEOUS_MC_BOUND_FROZEN_FORECAST_ONLY' if variant == 'confidence_min'
             else 'MONTE_CARLO_POINT_ESTIMATE_NOT_CERTIFIED')
    return Acquisition(bundle.ids[best], bundle.ids[baseline], variant, best_score, scope,
                       stats['completed'], stats['pairs'], stats['states'], stats['hits'],
                       interrupted, time.monotonic() - started, bundle.provenance)


def payload(decision):
    return asdict(decision)
