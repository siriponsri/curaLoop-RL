import random

import pytest

from research.event_time import Candidate, Observation, Result
from research.planning_v2.finite import FinitePlanner, State
from research.planning_v2.model import build


def test_informative_pending_reverses_wait_and_deadline():
    labels = [[True, True, False, False, True], [False, False, True, True, False]]
    state = State(0, 2, 1 << 4, ((4, 0),))
    planner = FinitePlanner(labels, [[1] * 5] * 2, 2, 2)
    action, trace = planner.choose(state, shortlist=4, bound="content")
    assert action == ()
    assert trace["chosen_lower"] == 2.5  # pending .5 plus two new hits
    assert planner.after(state, (0,), planner.full) == 2.0
    urgent = FinitePlanner(labels, [[1] * 5] * 2, 2, 1)
    action, trace = urgent.choose(state, shortlist=4, bound="content")
    assert action
    assert trace["chosen_lower"] == 1.0


def test_independent_pending_and_nonanticipative_continuation():
    labels = [[z, z, not z, not z, w] for z in (False, True) for w in (False, True)]
    planner = FinitePlanner(labels, [[1] * 5] * 4, 2, 2)
    state = State(0, 2, 1 << 4, ((4, 0),))
    assert planner.after(state, (), planner.full) == 1.5
    assert planner.after(state, (0,), planner.full) == 2.0
    assert planner.choose(state, shortlist=4)[0] != ()


def test_bounds_cover_exact_bayes_optimal_and_pruning_preserves_choice():
    rng = random.Random(20261104)
    comparisons = 0
    for _ in range(48):
        n = 4
        labels = [[bool(rng.getrandbits(1)) for _ in range(n)] for _ in range(4)]
        durations = [[rng.choice((1, 2, 4)) for _ in range(n)] for _ in range(4)]
        planner = FinitePlanner(labels, durations, 2, rng.choice((1, 2, 3, 4)))
        state = State(0, rng.choice((1, 2, 3)), 1 << 3, ((3, 0),))
        for action in planner.actions(state, planner.full):
            lower = planner.after(state, action, planner.full)
            optimal = planner.after(state, action, planner.full, optimal=True)
            upper = planner.upper(state, action, planner.full)
            cardinality = planner.upper(state, action, planner.full, "cardinality")
            assert lower <= optimal + 1e-10 <= upper + 2e-10
            assert upper <= cardinality + 1e-10
            comparisons += 1
        reference, _ = planner.choose(state, shortlist=4)
        assert planner.choose(state, shortlist=4, bound="cardinality")[0] == reference
        assert planner.choose(state, shortlist=4, bound="content")[0] == reference
    assert comparisons >= 150


def test_direct_late_reward_and_no_continuation():
    planner = FinitePlanner([[True, True]], [[1, 4]], 2, 1)
    state = State(0, 0, 3, ((0, 0), (1, 0)))
    assert planner.after(state, (), planner.full) == 1
    assert planner.upper(state, (), planner.full) == 1


def test_xor_joint_observation_is_not_pairwise_independence():
    labels = [[bool(x ^ y), bool(x), bool(y)] for x in (0, 1) for y in (0, 1)]
    planner = FinitePlanner(labels, [[1, 1, 1]] * 4, 2, 2)
    state = State(0, 1, 6, ((1, 0), (2, 0)))
    branches = list(planner.branches(state, planner.full))
    assert len(branches) == 4
    assert all(mask.bit_count() == 1 for _, _, _, mask in branches)
    assert planner.after(state, (), planner.full) == 1.5


def test_residual_duration_support_and_hidden_outcome_invariance():
    candidates = tuple(Candidate(str(i), (float(i % 2),)) for i in range(3))
    obs = Observation(
        2,
        6,
        4,
        candidates,
        ("2",),
        ("1",),
        (Result("0", False, 0),),
        (),
        (),
        tuple((str(i), 1) for i in range(3)),
        1,
        2,
    )
    a, state = build(obs, {"1": 0}, (0, 0, 1), (1, 2, 4), 7, 16, 2)
    b, other = build(obs, {"1": 0}, (0, 0, 1), (1, 2, 4), 7, 16, 2)
    assert a.labels == b.labels and state == other
    assert all(row[1] == 2 for row in a.durations)
    # Future private Task labels/due times have no input parameter here.
    with pytest.raises(ValueError, match="support"):
        build(obs, {"1": 0}, (0, 0, 1), (1, 2), 7, 16, 2)


def test_reject_unsupported_or_invalid_actions():
    with pytest.raises(ValueError):
        FinitePlanner([[True]], [[0]], 1, 2)
    planner = FinitePlanner([[True, False]], [[1, 1]], 1, 2)
    state = State(0, 1, 0, ())
    for action in ((), (0, 0), (0, 1), (9,)):
        with pytest.raises(ValueError):
            planner.launch(state, action)


def test_joint_xor_information_changes_the_optimal_choice():
    labels = [[bool(x ^ y), not bool(x ^ y), bool(x), bool(y)] for x in (0, 1) for y in (0, 1)]
    planner = FinitePlanner(labels, [[1] * 4] * 4, 3, 2)
    state = State(0, 1, 12, ((2, 0), (3, 0)))
    assert planner.after(state, (), planner.full, optimal=True) == 2.0
    assert planner.after(state, (0,), planner.full, optimal=True) == 1.5
    assert planner.choose(state, shortlist=2)[0] == ()
    assert planner.choose(state, shortlist=2, bound="content")[0] == ()


def test_shortlist_gap_does_not_certify_omitted_root_actions():
    labels = [[a < 3, bool(b), not bool(b)] for a in range(4) for b in range(2)]
    planner = FinitePlanner(labels, [[1] * 3] * 8, 1, 2)
    state = State(0, 2, 0, ())
    short, trace = planner.choose(state, shortlist=1, bound="content")
    all_actions, full_trace = planner.choose(state, shortlist=3)
    assert short == (0,) and all_actions != short
    assert trace["chosen_lower"] == 1.25
    assert full_trace["chosen_lower"] == 1.375
    assert "shortlisted" in trace["gap_scope"]
