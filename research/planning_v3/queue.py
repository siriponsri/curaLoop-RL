"""Exact finite-support queue probabilities, independent of private outcomes."""

import math
from collections import defaultdict
from functools import lru_cache
from itertools import product


def validate_law(law):
    law = tuple(law)
    if not law or any(type(d) is not int or d < 1 for d in law):
        raise ValueError("Duration law needs positive integer draws.")
    return law


def residual_law(law, age):
    law = validate_law(law)
    if type(age) is not int or age < 0:
        raise ValueError("Pending age must be a nonnegative integer.")
    values = [d - age for d in law if d > age]
    if not values:
        raise ValueError("Pending age contradicts public duration support.")
    counts = defaultdict(int)
    for value in values:
        counts[value] += 1
    return tuple((d, count / len(values)) for d, count in sorted(counts.items()))


@lru_cache(maxsize=4096)
def completion_weights(law, horizon, capacity, pending_ages, budget):
    """P(rth future dispatched job completes), conditional on POST-event state.

    The distribution of sorted worker-free times is sufficient. Appending the
    next list job replaces the earliest free time by that time plus its IID
    duration. This avoids identity-labelled queue-state enumeration.
    Weights are unconditional over future duration realizations; discarded
    late-start mass is NEVER renormalized to the surviving trajectories.
    """
    law = validate_law(law)
    if (
        any(type(x) is not int or x < 0 for x in (horizon, budget))
        or type(capacity) is not int
        or capacity < 1
    ):
        raise ValueError("Invalid queue horizon/budget/capacity.")
    if len(pending_ages) > capacity:
        raise ValueError("Pending count exceeds capacity.")
    pending = [residual_law(law, age) for age in pending_ages]
    states = defaultdict(float)
    for draws in product(*pending):
        free = tuple(sorted([0] * (capacity - len(pending)) + [d for d, _ in draws]))
        states[free] += math.prod(p for _, p in draws)
    duration = residual_law(law, 0)
    weights = []
    for rank in range(budget):
        next_states = defaultdict(float)
        weight = 0.0
        for free, probability in states.items():
            start = free[0]
            if start >= horizon:
                continue
            for d, p in duration:
                finish = start + d
                joint = probability * p
                if finish <= horizon:
                    weight += joint
                next_states[tuple(sorted(free[1:] + (finish,)))] += joint
        weights.append(weight)
        states = next_states
    if any(b > a + 1e-12 for a, b in zip(weights, weights[1:])):
        raise AssertionError("Completion weights must be nonincreasing.")
    return tuple(weights)


def next_events(law, pending, horizon):
    """Public next delivery patterns and their probabilities; no private due times.

    pending=(candidate index, current public age). A terminal no-delivery event
    is represented by (horizon, (), surviving_pending_ages, probability).
    An empty delivered tuple is a terminal censoring sentinel, not a free queue.
    """
    if type(horizon) is not int or horizon < 0:
        raise ValueError("Event horizon must be a nonnegative integer.")
    if not pending or len({i for i, _ in pending}) != len(pending):
        raise ValueError("Next event needs unique accepted candidate IDs.")
    distributions = [residual_law(law, age) for _, age in pending]
    events = defaultdict(float)
    for draws in product(*distributions):
        delta = min(d for d, _ in draws)
        probability = math.prod(p for _, p in draws)
        if delta > horizon:
            key = (horizon, (), tuple(sorted((i, age + horizon) for i, age in pending)))
        else:
            delivered = tuple(sorted(i for (i, _), (d, _) in zip(pending, draws) if d == delta))
            remaining = tuple(
                sorted((i, age + delta) for (i, age), (d, _) in zip(pending, draws) if d > delta)
            )
            key = (delta, delivered, remaining)
        events[key] += probability
    return tuple((*key, probability) for key, probability in sorted(events.items()))
