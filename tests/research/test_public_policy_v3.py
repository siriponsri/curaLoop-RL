"""End-to-end policy privacy/feasibility on small constructed engine tasks."""

from dataclasses import replace

import pytest

from research.event_time import Campaign, Candidate, Result, Scenario, Task
from research.planning_v3.policy import METHODS, PolicySession


def task(negate_private=False, duration=2, missing=()):
    ids = tuple(f"c{i}" for i in range(8))
    candidates = tuple(
        Candidate(cid, tuple(float(j in (i, i + 8)) for j in range(1024)))
        for i, cid in enumerate(ids)
    )
    labels = [(cid, bool(i % 2)) for i, cid in enumerate(ids)]
    if negate_private:
        labels = [(cid, y if i < 2 else not y) for i, (cid, y) in enumerate(labels)]
    return Task(
        "constructed-public-boundary-v3",
        candidates,
        tuple((cid, duration) for cid in ids),
        tuple((cid, 1) for cid in ids),
        tuple(labels),
        missing,
    )


@pytest.mark.parametrize("method", METHODS)
def test_every_method_respects_public_feasibility_and_engine_accounting(method):
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), method, 7, (2, 4), 2, 32)
    traces = []
    while not campaign.done:
        obs = campaign.observe()
        action, trace = session.select(obs)
        assert set(action) <= set(obs.eligible_ids)
        traces.append(trace)
        if action:
            campaign.submit(action)
            session.record_acceptance(action, obs.time)
        if not campaign.done:
            assert campaign.wait()
    assert (
        campaign.metrics["spent"] + campaign.metrics["reserved"] + campaign.metrics["uncommitted"]
        == 3
    )
    assert campaign.metrics["new_hits"] <= campaign.metrics["delivered"]
    assert all(not t["learned_controller_action"] for t in traces)


@pytest.mark.parametrize("method", METHODS)
def test_private_outcome_and_due_time_permutations_cannot_change_matching_public_decisions(method):
    a = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    b = Campaign(task(negate_private=True, duration=4), Scenario(3, 2, 4, ("c0", "c1")))
    assert a.snapshot()["resource_sha256"] != b.snapshot()["resource_sha256"]
    assert a.observe() == b.observe()
    pa, pb = (
        PolicySession(a.observe(), method, 3, (2, 4)),
        PolicySession(b.observe(), method, 3, (2, 4)),
    )
    aa, at = pa.select(a.observe())
    ba, bt = pb.select(b.observe())
    assert aa == ba
    if at["model_trace"]:
        assert at["model_trace"]["draw_seed"] == bt["model_trace"]["draw_seed"]
    a.submit(aa)
    b.submit(ba)
    pa.record_acceptance(aa, 0)
    pb.record_acceptance(ba, 0)
    a.advance_to(1)
    b.advance_to(1)
    assert a.observe() == b.observe()
    assert pa.select(a.observe())[0] == pb.select(b.observe())[0]


def test_only_initial_and_delivered_labels_reach_predictor(monkeypatch):
    import research.planning_v3.policy as policy

    real = policy.fit_mixture
    calls = []

    def spy(design, known, seed, hypotheses):
        calls.append(dict(known))
        return real(design, known, seed, hypotheses)

    monkeypatch.setattr(policy, "fit_mixture", spy)
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    while not campaign.done:
        obs = campaign.observe()
        before = len(calls)
        action, _ = session.select(obs)
        if len(calls) > before:
            assert calls[-1] == {
                r.candidate_id: r.active for r in obs.initial_results + obs.delivered_results
            }
        if action:
            campaign.submit(action)
            session.record_acceptance(action, obs.time)
        if not campaign.done:
            campaign.wait()


def test_time_only_change_preserves_parameter_draw_seed():
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    _, before = session.select(campaign.observe())
    campaign.advance_to(1)
    _, after = session.select(campaign.observe())
    assert before["model_trace"]["draw_seed"] == after["model_trace"]["draw_seed"]


def test_random_and_nearest_hit_never_construct_unused_belief(monkeypatch):
    import research.planning_v3.policy as policy

    def forbidden(*args, **kwargs):
        raise AssertionError("unused belief called")

    monkeypatch.setattr(policy, "fit_mixture", forbidden)
    monkeypatch.setattr(policy, "make_design", forbidden)
    for method in ("random", "nearest_hit"):
        campaign = Campaign(task(), Scenario(3, 2, 4, ("c0",)))
        session = PolicySession(campaign.observe(), method, 3, (2, 4))
        action, trace = session.select(campaign.observe())
        assert action and trace["model_trace"] is None


def test_rejects_unowned_labels_and_false_public_commitments():
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    obs = campaign.observe()
    with pytest.raises(ValueError, match="commitments"):
        session.select(replace(obs, uncommitted=2))
    with pytest.raises(ValueError, match="initial public Observation"):
        PolicySession(campaign, "greedy", 3, (2, 4))
    with pytest.raises(ValueError, match="latest successfully accepted"):
        session.record_acceptance(("c7",), 0)


def test_missing_deliveries_never_become_training_negatives_or_relaunch(monkeypatch):
    import research.planning_v3.policy as policy

    real = policy.fit_mixture
    calls = []

    def spy(design, known, seed, hypotheses):
        calls.append(dict(known))
        return real(design, known, seed, hypotheses)

    monkeypatch.setattr(policy, "fit_mixture", spy)
    campaign = Campaign(
        task(missing=tuple(f"c{i}" for i in range(2, 8))), Scenario(3, 2, 4, ("c0", "c1"))
    )
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    while not campaign.done:
        obs = campaign.observe()
        action, _ = session.select(obs)
        assert not set(action) & set(obs.missing_ids)
        if action:
            campaign.submit(action)
            session.record_acceptance(action, obs.time)
        if not campaign.done:
            campaign.wait()
    assert campaign.metrics["missing"] == 3 and campaign.metrics["new_hits"] == 0
    assert calls and all(known == {"c0": False, "c1": True} for known in calls)


def test_forced_full_capacity_budget_zero_and_terminal_pending_keep_commitments():
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    action, _ = session.select(campaign.observe())
    campaign.submit(action)
    session.record_acceptance(action, 0)
    obs = campaign.observe()
    assert obs.slots == 0
    forced, trace = session.select(obs)
    assert forced == () and trace["forced_or_terminal"] and trace["model_trace"] is None
    late = Campaign(task(duration=2), Scenario(1, 2, 1, ("c0", "c1")))
    policy = PolicySession(late.observe(), "greedy", 3, (2, 4))
    one, _ = policy.select(late.observe())
    late.submit(one)
    policy.record_acceptance(one, 0)
    assert policy.select(late.observe())[0] == ()
    late.wait()
    terminal, tt = policy.select(late.observe())
    assert terminal == () and tt["forced_or_terminal"]
    assert (
        late.metrics["reserved"] == 1
        and late.metrics["spent"] == 0
        and late.metrics["new_hits"] == 0
    )


def test_rejected_submit_does_not_enter_acceptance_log_and_duplicate_record_is_rejected():
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "random", 3, (2, 4))
    action, _ = session.select(campaign.observe())
    other = next(cid for cid in campaign.observe().eligible_ids if cid not in action)
    with pytest.raises(ValueError):
        campaign.submit(action + (other,))
    assert session.launched == {}
    assert session.select(campaign.observe())[0] == action
    campaign.submit(action)
    session.record_acceptance(action, 0)
    with pytest.raises(ValueError, match="latest successfully accepted"):
        session.record_acceptance(action, 0)


def test_genuinely_unowned_delivered_label_is_rejected_before_predictor():
    campaign = Campaign(task(), Scenario(3, 2, 4, ("c0", "c1")))
    session = PolicySession(campaign.observe(), "greedy", 3, (2, 4))
    forged = replace(campaign.observe(), delivered_results=(Result("c7", True, 0),))
    with pytest.raises(ValueError, match="acceptance/time provenance"):
        session.select(forged)
    assert session.seen == {"c0": False, "c1": True}
