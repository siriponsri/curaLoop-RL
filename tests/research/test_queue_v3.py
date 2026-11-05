"""Independent exhaustive checks of queue and timing-conditioning identities."""

from itertools import product

import pytest

from research.planning_v3.queue import completion_weights, next_events, residual_law


def brute(law, horizon, capacity, ages, budget):
    residual = [[d - a for d in law if d > a] for a in ages]
    totals = [0.0] * budget
    count = 0
    for old in product(*residual):
        for durations in product(law, repeat=budget):
            free = list(old) + [0] * (capacity - len(old))
            for rank, duration in enumerate(durations):
                worker = min(range(capacity), key=lambda i: (free[i], i))
                free[worker] += duration
                totals[rank] += free[worker] <= horizon
            count += 1
    return tuple(v / count for v in totals)


@pytest.mark.parametrize(
    "law,horizon,capacity,ages,budget",
    [
        ((1,), 3, 1, (), 5),
        ((2,), 4, 2, (), 5),
        ((1, 2, 4), 5, 2, (1,), 4),
        ((1, 3), 3, 2, (0, 1), 4),
        ((1, 2, 2), 3, 2, (0,), 4),
        ((1, 4), 0, 2, (0,), 3),
        ((1, 3), 1, 1, (1,), 3),
        ((1, 2, 4), 6, 2, (2, 0), 4),
    ],
)
def test_queue_matches_full_duration_enumeration(law, horizon, capacity, ages, budget):
    got = completion_weights(law, horizon, capacity, ages, budget)
    assert got == pytest.approx(brute(law, horizon, capacity, ages, budget), abs=2e-12)
    assert all(a >= b - 1e-12 for a, b in zip(got, got[1:]))


def test_residual_conditions_on_survival_and_preserves_multiplicity():
    assert residual_law((1, 2, 2, 4), 1) == ((1, 2 / 3), (3, 1 / 3))
    with pytest.raises(ValueError):
        residual_law((1, 2), 2)


def test_next_public_event_probability_and_survival():
    events = next_events((1, 2, 4), ((7, 1), (9, 0)), 3)
    assert sum(e[3] for e in events) == pytest.approx(1)
    assert all(0 <= e[0] <= 3 for e in events)
    for delta, delivered, remaining, probability in events:
        assert probability > 0
        assert not set(delivered) & {i for i, _ in remaining}
        assert all(age == dict(((7, 1), (9, 0)))[i] + delta for i, age in remaining)


def test_terminal_no_delivery_and_exact_deadline():
    assert next_events((4,), ((0, 0),), 3) == ((3, (), ((0, 3),), 1.0),)
    assert next_events((4,), ((0, 0),), 4) == ((4, (0,), (), 1.0),)
    assert completion_weights((2,), 4, 1, (), 4) == (1, 1, 0, 0)


@pytest.mark.parametrize("horizon", [-1, 1.5, True])
def test_event_horizon_rejects_invalid_time(horizon):
    with pytest.raises(ValueError, match="nonnegative integer"):
        next_events((1, 3), ((7, 0),), horizon)


def test_exact_next_event_pmf_and_pending_order():
    expected = ((1, (7,), ((9, 2),), 0.5), (2, (9,), ((7, 2),), 0.5))
    assert next_events((1, 3), ((7, 0), (9, 1)), 3) == expected
    assert next_events((1, 3), ((9, 1), (7, 0)), 3) == expected
    events = {
        (delta, delivered): p
        for delta, delivered, _, p in next_events((1, 2, 2), ((7, 0), (9, 0)), 1)
    }
    assert events == pytest.approx(
        {(1, (7, 9)): 1 / 9, (1, (7,)): 2 / 9, (1, (9,)): 2 / 9, (1, ()): 4 / 9}
    )
    assert completion_weights((1, 2), 3, 2, (1,), 0) == ()
