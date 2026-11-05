"""Independent exhaustive nonanticipative oracle for stochastic recourse.

Only tiny constructed distributions are enumerated. This oracle is deliberately
different from the production posterior/queue calculations and never sees assays.
"""

import math
from collections import defaultdict
from itertools import permutations, product

import pytest

from research.planning_v3.mixture import Mixture
from research.planning_v3.recourse import PublicState, RecoursePlanner


def independent_oracle(p, w, law, capacity, state, action):
    pending = state.pending + tuple((i, 0) for i in action)
    unused = [i for i in range(len(p[0])) if i not in state.used and i not in action]
    count = min(state.budget - len(action), len(unused))
    future_lists = list(permutations(unused, count))
    duration_ids = [i for i, _ in pending] + unused
    supports = [[d - age for d in law if d > age] for _, age in pending] + [
        list(law) for _ in unused
    ]
    duration_mass = math.prod(1 / len(values) for values in supports)
    groups = defaultdict(list)
    for m, prior in enumerate(w):
        for labels in product((0, 1), repeat=len(p[0])):
            label_mass = prior * math.prod(
                p[m][i] if y else 1 - p[m][i] for i, y in enumerate(labels)
            )
            if not label_mass:
                continue
            for draws in product(*supports):
                durations = dict(zip(duration_ids, draws))
                event_time = min(durations[i] for i, _ in pending)
                delivered = tuple(
                    sorted((i, labels[i]) for i, _ in pending if durations[i] == event_time)
                )
                if event_time > state.horizon:
                    key = (state.horizon, ())
                else:
                    key = (event_time, delivered)
                groups[key].append((label_mass * duration_mass, labels, durations))
    assert sum(
        probability for worlds in groups.values() for probability, _, _ in worlds
    ) == pytest.approx(1)
    value = 0.0
    for (event_time, delivered), worlds in groups.items():
        action_values = []
        for future in future_lists:
            expected = 0.0
            for probability, labels, durations in worlds:
                gain = sum(labels[i] for i, _ in pending if durations[i] <= state.horizon)
                if delivered and event_time < state.horizon:
                    # The fixed list is chosen OUTSIDE this private-world loop.
                    free = sorted(
                        [durations[i] for i, _ in pending if durations[i] > event_time]
                        + [event_time]
                        * (capacity - sum(durations[i] > event_time for i, _ in pending))
                    )
                    for i in future:
                        start = free.pop(0)
                        finish = start + durations[i]
                        gain += labels[i] if finish <= state.horizon else 0
                        free.append(finish)
                        free.sort()
                expected += probability * gain
            action_values.append(expected)
        value += max(action_values)
    return value


@pytest.mark.parametrize(
    "state,action",
    [
        (PublicState(4, 2, frozenset({0, 1}), ((0, 1), (1, 0))), ()),
        (PublicState(4, 2, frozenset({0}), ((0, 1),)), (1,)),
    ],
)
def test_joint_labels_timing_ages_and_fixed_list_match_independent_world_oracle(state, action):
    p = [[0.1, 0.4, 0.8, 0.2, 0.6], [0.9, 0.3, 0.2, 0.7, 0.4]]
    w, law = [0.35, 0.65], (1, 2, 4)
    planner = RecoursePlanner(Mixture(p, w), law, 2)
    exact = independent_oracle(p, w, law, 2, state, action)
    values, _ = planner.evaluate_actions(state, [action])
    assert values[0] == pytest.approx(exact, abs=2e-11)
