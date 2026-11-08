"""Exact baseline-relative rollout in a small predictive scenario model.

This is an adaptation of established robust policy-improvement principles,
not a novel algorithm or a molecular/clinical safety certificate. Scenarios
must be model predictions based on delivered information, never hidden labels.
No data files, network, application state or outcome oracle are accessed here.
"""

from dataclasses import dataclass
from math import fsum, isfinite


class PlanningLimit(RuntimeError):
    """A declared computation-state bound was reached."""


@dataclass(frozen=True)
class Decision:
    action: int
    baseline_action: int
    objective: str
    reason: str
    selection_gain: float
    lower_gain_in_declared_models: float | None
    evaluated_alternatives: int
    state_evaluations: int
    cache_hits: int
    interrupted: bool


class ScenarioRollout:
    """A deliberately small, exact reference with common predictor/greedy tails.

    Each model supplies probabilities over the same finite binary worlds.
    Equal prior model weights define the common predictive mixture. Observation
    updates condition that mixture and every supported model on delivered labels.
    One action acquires one binary result; all actions have unit measurement cost.
    State evaluations are a computation proxy, not elapsed time or CPU seconds.
    """

    def __init__(self, worlds, model_probabilities):
        self.worlds = tuple(tuple(row) for row in worlds)
        self.models = tuple(tuple(row) for row in model_probabilities)
        if not self.worlds or not 1 <= len(self.worlds[0]) <= 12:
            raise ValueError('Require 1..12 candidate positions')
        self.n = len(self.worlds[0])
        if len(self.worlds) > 64 or not 1 <= len(self.models) <= 8:
            raise ValueError('Constructed reference limit: 64 worlds, 8 models')
        if any(len(w) != self.n or any(type(y) is not int or y not in (0, 1)
                                      for y in w) for w in self.worlds):
            raise ValueError('Worlds must be equally sized binary integer rows')
        normalized = []
        for row in self.models:
            if len(row) != len(self.worlds):
                raise ValueError('Model/world dimensions differ')
            if any(not isfinite(p) or p < 0 for p in row) or fsum(row) <= 0:
                raise ValueError('Probabilities must be finite, nonnegative, nonzero')
            total = fsum(row)
            if not isfinite(total):
                raise ValueError('Probability total must be finite')
            normalized.append(tuple(p / total for p in row))
        self.models = tuple(normalized)
        self.mixture = tuple(fsum(m[j] for m in self.models) / len(self.models)
                             for j in range(len(self.worlds)))

    def _observations(self, observed):
        pairs = tuple(sorted(observed.items()))
        if any(type(a) is not int or not 0 <= a < self.n or
               type(y) is not int or y not in (0, 1) for a, y in pairs):
            raise ValueError('Invalid delivered observation')
        if not self._support(pairs):
            raise ValueError('Delivered observations contradict all declared models')
        return pairs

    def _support(self, observed):
        return tuple(j for j, w in enumerate(self.worlds)
                     if self.mixture[j] > 0 and all(w[a] == y for a, y in observed))

    def _greedy(self, observed):
        support = self._support(observed)
        available = [a for a in range(self.n) if a not in dict(observed)]
        if not support or not available:
            raise ValueError('No feasible prediction/action')
        # The normalization constant is shared by every candidate.
        return min(available, key=lambda a: (
            -fsum(self.mixture[j] * self.worlds[j][a] for j in support), a))

    def choose(self, observed, budget, *, objective='robust', max_states=4096,
               use_cache=True):
        """Choose one deviation followed by common adaptive Greedy continuation.

        Only completed rollout differences can change the baseline action.
        Interruption retains the best completed positive-gain action, or Greedy.
        The exact-model gain is conditional on the declared finite distributions;
        no frequentist/real-world guarantee is inferred from sampled scenarios.
        """
        obs = self._observations(observed)
        if type(budget) is not int or not 1 <= budget <= min(6, self.n - len(obs)):
            raise ValueError('Budget must be 1..6 and fit remaining candidates')
        if objective not in ('robust', 'mixture'):
            raise ValueError('Unknown objective')
        if type(max_states) is not int or max_states < 0:
            raise ValueError('max_states must be a nonnegative integer')
        baseline_action = self._greedy(obs)
        memo = {}
        stats = {'states': 0, 'hits': 0}

        def tail(state, remaining):
            key = (state, remaining)
            if use_cache and key in memo:
                stats['hits'] += 1
                return memo[key]
            if remaining == 0:
                return (0,) * len(self.worlds)
            if stats['states'] >= max_states:
                raise PlanningLimit
            stats['states'] += 1
            result = forced(self._greedy(state), state, remaining)
            if use_cache:
                memo[key] = result
            return result

        def forced(action, state, remaining):
            support = self._support(state)
            children = {}
            for y in (0, 1):
                branch = tuple(sorted((*state, (action, y))))
                if self._support(branch):
                    children[y] = tail(branch, remaining - 1)
            values = [0] * len(self.worlds)
            for j in support:
                y = self.worlds[j][action]
                values[j] = y + children[y][j]
            return tuple(values)

        support = self._support(obs)

        def gain(delta):
            distributions = self.models if objective == 'robust' else (self.mixture,)
            scores = []
            for row in distributions:
                mass = fsum(row[j] for j in support)
                if mass > 0:
                    scores.append(fsum(row[j] * delta[j] for j in support) / mass)
            return min(scores)

        best_action, best_gain, completed, interrupted = baseline_action, 0.0, 0, False
        try:
            baseline = tail(obs, budget)
            for action in range(self.n):
                if action == baseline_action or action in dict(obs):
                    continue
                values = forced(action, obs, budget)
                score = gain(tuple(v - b for v, b in zip(values, baseline)))
                completed += 1
                if score > best_gain + 1e-12:
                    best_action, best_gain = action, score
        except PlanningLimit:
            interrupted = True
        reason = ('COMPLETED_POSITIVE_ROLLOUT' if best_action != baseline_action
                  else 'GREEDY_BY_IDENTITY')
        lower = best_gain if objective == 'robust' else None
        return Decision(best_action, baseline_action, objective, reason, best_gain, lower,
                        completed, stats['states'], stats['hits'], interrupted)
