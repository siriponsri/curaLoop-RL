"""Constructed count-based scheduling and full greedy-fantasy references."""

import hashlib
from functools import lru_cache

import numpy as np

from .mixture import top_indices
from .queue import next_events, residual_law, validate_law


def uniform(seed, namespace, candidate=0):
    value = int(hashlib.sha256(f"{seed}|{namespace}|{candidate}".encode()).hexdigest()[:16], 16)
    return (value >> 11) * 2**-53


def sample_distribution(distribution, u):
    total = 0.0
    for value, probability in distribution:
        total += probability
        if u < total:
            return value
    return distribution[-1][0]


class CPEStateLimit(Exception):
    pass


class CountProxyScheduler:
    """Azimi2011-inspired count-information proxy, not H(T) optimization.

    First maximize expected completed experiment count by the deadline, then
    expected cumulative prior NEW experiments at launch among primary ties.
    This is an explicit completion-first adaptation, not the paper's p-safe
    policy generator/theorem. Only batch SIZE/timing is optimized; content is
    matched posterior-mean Greedy outside this scheduler. It is not H(T).
    Each instance/cache/state cap belongs to ONE campaign, never another arm.
    """

    def __init__(self, law, capacity, state_limit=20000):
        if (
            type(capacity) is not int
            or not 1 <= capacity <= 2
            or type(state_limit) is not int
            or state_limit < 0
        ):
            raise ValueError("Invalid bounded count-scheduler configuration.")
        self.law, self.capacity, self.state_limit = validate_law(law), capacity, state_limit
        self.states = 0
        self.value = lru_cache(maxsize=None)(self._value)

    def _actions(self, horizon, budget, ages):
        if not horizon:
            return []
        sizes = list(range(min(self.capacity - len(ages), budget), 0, -1))
        if ages:
            sizes.append(0)
        return sizes

    def _after(self, horizon, budget, ages, completed, size):
        pending = tuple(enumerate(tuple(ages) + (0,) * size))
        completion_value, information_value = 0.0, float(completed * size)
        for delta, delivered, remaining, probability in next_events(self.law, pending, horizon):
            completion_value += probability * len(delivered)
            if not delivered or delta >= horizon:
                continue
            future_completion, future_information = self.value(
                horizon - delta,
                budget - size,
                tuple(sorted(age for _, age in remaining)),
                completed + len(delivered),
            )
            completion_value += probability * future_completion
            information_value += probability * future_information
        return completion_value, information_value

    @staticmethod
    def _best(values):
        best = 0
        for i, (completed, information) in enumerate(values):
            bc, bi = values[best]
            if completed > bc + 1e-12 or (
                abs(completed - bc) <= 1e-12 and information > bi + 1e-12
            ):
                best = i
        return best

    def _value(self, horizon, budget, ages, completed):
        self.states += 1
        if self.states > self.state_limit:
            raise CPEStateLimit("CPE_STATE_LIMIT_WORK_CONSERVING_FALLBACK")
        actions = self._actions(horizon, budget, ages)
        values = [self._after(horizon, budget, ages, completed, k) for k in actions]
        return values[self._best(values)] if values else (0.0, 0.0)

    def choose_size(self, horizon, budget, ages, completed):
        previous_states = self.states
        if (
            any(type(v) is not int or v < 0 for v in (horizon, budget, completed))
            or len(ages) > self.capacity
        ):
            raise ValueError("Invalid public count-scheduler state.")
        for age in ages:
            residual_law(self.law, age)
        sizes = self._actions(horizon, budget, tuple(sorted(ages)))
        if not sizes:
            return 0, {"forced_or_terminal": True, "objective": "COMPLETION_FIRST_CPE_COUNT_PROXY"}
        try:
            values = [
                self._after(horizon, budget, tuple(sorted(ages)), completed, k) for k in sizes
            ]
            best = self._best(values)
            return sizes[best], {
                "objective": "COMPLETION_FIRST_CPE_COUNT_PROXY",
                "states_total": self.states,
                "new_states_this_call": self.states - previous_states,
                "state_cap_scope": "per_campaign_instance",
                "sizes": sizes,
                "values": values,
                "fallback": None,
                "expected_additional_completion_count": values[best][0],
                "completed_prefix_count": completed,
                "expected_CPE": values[best][1],
                "completion_count_gap": max(v[0] for v in values) - values[best][0],
                "numerical_tie_tolerance": 1e-12,
            }
        except CPEStateLimit as exc:
            return max(sizes), {
                "objective": "COMPLETION_FIRST_CPE_COUNT_PROXY",
                "states_total": self.states,
                "new_states_this_call": self.states - previous_states,
                "state_cap_scope": "per_campaign_instance",
                "fallback": str(exc),
            }


def greedy_rollout_values(planner, state, actions, seed, trajectories=16, event_limit=16):
    """Full remaining-budget/time greedy feedback under a frozen mixture.

    Hidden virtual theta and lazy label/duration draws belong to the simulator.
    Continuation choices use conditional weights ONLY, never sampled theta or
    an actual assay resource. Root actions share random numbers by candidate.
    """
    if type(seed) is not int or type(trajectories) is not int or trajectories < 1:
        raise ValueError("Explicit integer seed and positive trajectory count required.")
    if state.budget + len(state.pending) > event_limit:
        raise ValueError("Frozen rollout event limit cannot cover this public budget.")
    planner.validate(state)
    model = planner.model
    n = model.p.shape[1]
    duration_law = residual_law(planner.law, 0)
    values, root_samples = [], []
    for action in actions:
        planner.validate_action(state, action)  # No unused exact recourse calculation.
        samples = []
        for trajectory in range(trajectories):
            trial_seed = f"{seed}|greedy-rollout-v1|{trajectory}"
            theta = sample_distribution(tuple(enumerate(model.w)), uniform(trial_seed, "theta"))
            q = model.w.copy()
            pending = {}
            for i, age in state.pending:
                pending[i] = sample_distribution(
                    residual_law(planner.law, age), uniform(trial_seed, "duration", i)
                )
            for i in action:
                pending[i] = sample_distribution(duration_law, uniform(trial_seed, "duration", i))
            used = state.used | frozenset(action)
            budget = state.budget - len(action)
            gain, event_count = 0, 0
            while pending:
                when = min(pending.values())
                if when > state.horizon:
                    break
                event_count += 1
                if event_count > event_limit:
                    raise AssertionError("Rollout exceeded its validated public event bound.")
                delivered = sorted(i for i, t in pending.items() if t == when)
                likelihood = np.ones(len(q))
                for i in delivered:
                    y = uniform(trial_seed, "label", i) < model.p[theta, i]
                    gain += y
                    likelihood *= model.p[:, i] if y else 1 - model.p[:, i]
                    del pending[i]
                q *= likelihood
                total = q.sum()
                if not total > 0:
                    raise AssertionError("Virtual observations lost all positive mixture support.")
                q /= total
                if when >= state.horizon:
                    break
                count = min(planner.capacity - len(pending), budget, n - len(used))
                if count:
                    prediction = q @ model.p
                    ranking = top_indices(prediction, [i for i in range(n) if i not in used], count)
                    for i in ranking:
                        pending[i] = when + sample_distribution(
                            duration_law, uniform(trial_seed, "duration", i)
                        )
                    used |= frozenset(ranking)
                    budget -= len(ranking)
            samples.append(float(gain))
        values.append(float(np.mean(samples)))
        root_samples.append(samples)
    return values, {
        "objective": "MC_estimate_additional_delivered_positives_full_greedy_rollout",
        "trajectories": trajectories,
        "event_limit": event_limit,
        "certified_gap": None,
        "virtual_labels_drawn_lazily_on_delivery": True,
        "actual_assay_outcomes_accessed": False,
        "finite_belief_frozen_within_rollout": True,
        "root_trajectory_samples": root_samples,
        "root_MC_standard_errors": [
            float(np.std(samples, ddof=1) / np.sqrt(trajectories)) if trajectories > 1 else None
            for samples in root_samples
        ],
        "MC_error_is_not_family_or_scientific_uncertainty": True,
    }
