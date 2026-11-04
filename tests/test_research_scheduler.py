"""New integer reference contracts; legacy simulator and checkpoints are untouched."""

import copy
import itertools
import json
from dataclasses import asdict, replace

import pytest

from research.event_time import Campaign, Event, Scenario, keyed_duration, reconcile
from research.toy_validation import fixture, run_order, serial_reference


def test_deadline_processes_all_simultaneous_outcomes_and_retains_late_commitments():
    task = fixture((2, 2, 4), (True, False, True), ("b",))
    run = Campaign(task, Scenario(3, 3, 2))
    run.submit(("a", "b", "c"))
    assert run.metrics["reserved"] == 3 and run.observe().delivered_results == ()
    run.advance_to(2)
    assert run.metrics == {
        "time": 2,
        "new_hits": 1,
        "seed_hits": 0,
        "delivered": 1,
        "missing": 1,
        "pending": 1,
        "spent": 2,
        "reserved": 1,
        "uncommitted": 0,
        "accepted_exposure": 3,
        "time_discovery_area": 0,
    }
    assert run.observe().pending_ids == ("c",) and run.observe().missing_ids == ("b",)
    assert run.done and not run.wait()
    with pytest.raises(ValueError, match="deadline"):
        run.advance_to(4)
    with pytest.raises(ValueError):
        run.submit(("c",))


def test_observation_is_invariant_to_all_unrevealed_truth_changes():
    first = fixture((2, 2, 2), (True, False, True))
    flipped = replace(first, _outcomes=tuple((cid, not y) for cid, y in first._outcomes))
    a, b = (Campaign(t, Scenario(2, 2, 3)) for t in (first, flipped))
    a.submit(("a", "b"))
    b.submit(("a", "b"))
    assert asdict(a.observe()) == asdict(b.observe())
    assert a.events == b.events
    public = asdict(a.observe())
    assert not {"_outcomes", "resource_sha256", "durations", "task", "truth"} & public.keys()
    assert all(e.active is None for e in a.events)
    a.advance_to(2)
    b.advance_to(2)
    assert a.observe().delivered_results != b.observe().delivered_results


def test_zero_duration_does_not_create_wait_loops_or_exceed_simultaneous_capacity():
    run = Campaign(fixture((0, 0, 0)), Scenario(2, 2, 1))
    run.submit(("a", "b"))
    assert run.metrics["new_hits"] == 2 and run.metrics["reserved"] == 0
    assert run.metrics["spent"] == 2 and run.time == 0
    assert run.done and not run.wait()
    assert [e.kind for e in run.events] == ["REQUEST_ACCEPTED"] * 2 + ["RESULT_DELIVERED"] * 2


@pytest.mark.parametrize("bad", [("a", "a"), ("a", "unknown"), ("a", "b", "c"), (), ["a"]])
def test_invalid_batch_has_no_partial_acceptance_or_accounting(bad):
    run = Campaign(fixture(), Scenario(2, 2, 4))
    before = run.snapshot()
    with pytest.raises(ValueError):
        run.submit(bad)
    assert run.snapshot() == before


def test_heterogeneous_cost_batch_rejection_is_atomic():
    task = replace(fixture(), costs=(("a", 2), ("b", 2), ("c", 1)))
    run = Campaign(task, Scenario(3, 2, 4))
    before = run.snapshot()
    with pytest.raises(ValueError, match="Batch exceeds"):
        run.submit(("a", "b"))
    assert run.snapshot() == before
    run.submit(("a", "c"))
    assert run.metrics["reserved"] == 3
    run.advance_to(1)
    assert run.metrics["spent"] == 3 and run.metrics["reserved"] == 0


def test_seeds_pending_and_missing_do_not_count_as_new_hits():
    task = fixture((1, 1, 3), (True, True, True), ("b",))
    run = Campaign(task, Scenario(2, 2, 2, ("a",)))
    assert "a" not in run.observe().eligible_ids
    run.submit(("b", "c"))
    run.advance_to(2)
    assert run.metrics["seed_hits"] == 1 and run.metrics["new_hits"] == 0
    assert run.metrics["missing"] == 1 and run.metrics["pending"] == 1
    assert run.metrics["spent"] == run.metrics["reserved"] == 1
    assert run.observe().delivered_results == ()


def test_time_integral_has_zero_point_mass_at_exact_deadline():
    run = Campaign(fixture((1, 2, 3), (True, True, False)), Scenario(3, 3, 2))
    run.submit(("a", "b", "c"))
    run.advance_to(2)
    assert run.metrics["new_hits"] == 2
    assert run.metrics["time_discovery_area"] == 1


def test_pending_snapshot_restores_without_time_or_charge_change():
    task = fixture((2, 2, 4))
    run = Campaign(task, Scenario(3, 2, 5))
    run.submit(("a", "b"))
    saved = run.snapshot()
    resumed = Campaign.restore(task, json.loads(json.dumps(saved)))
    assert resumed.snapshot() == saved and resumed.time == 0
    for campaign in (run, resumed):
        campaign.advance_to(2)
        campaign.submit(("c",))
        campaign.advance_to(5)
        before = campaign.snapshot()
        campaign.advance_to(5)
        assert campaign.snapshot() == before
    assert run.snapshot() == resumed.snapshot()
    assert run.metrics["spent"] == 2 and run.metrics["reserved"] == 1


@pytest.mark.parametrize("field", ["events", "metrics", "journal", "scenario", "schema_version"])
def test_tampered_snapshot_cannot_create_early_results_or_new_budget(field):
    task = fixture((2, 2, 2))
    run = Campaign(task, Scenario(2, 2, 3))
    run.submit(("a",))
    bad = copy.deepcopy(run.snapshot())
    if field == "events":
        bad[field][0]["active"] = True
    elif field == "metrics":
        bad[field]["new_hits"] = 99
    elif field == "journal":
        bad[field].append({"action": "advance_to", "time": 3})
    elif field == "scenario":
        bad[field]["budget"] = -1
    else:
        bad[field] = "unreviewed-future-schema"
    with pytest.raises(ValueError):
        Campaign.restore(task, bad)


def test_snapshot_requires_exact_resource_and_returns_independent_values():
    task = fixture()
    run = Campaign(task, Scenario(2, 2, 3))
    saved = run.snapshot()
    changed = replace(task, _outcomes=(("a", False), ("b", True), ("c", False)))
    with pytest.raises(ValueError, match="resource identity"):
        Campaign.restore(changed, saved)
    saved["metrics"]["new_hits"] = 5
    assert run.metrics["new_hits"] == 0


def test_ledger_rejects_reused_request_id_after_settlement():
    events = (
        Event(0, 0, "REQUEST_ACCEPTED", "a", "r0", 1),
        Event(1, 1, "RESULT_DELIVERED", "a", "r0", 1, True),
        Event(2, 1, "REQUEST_ACCEPTED", "b", "r0", 1),
    )
    with pytest.raises(ValueError, match="Duplicate"):
        reconcile(events, 2, 1)


@pytest.mark.parametrize("values", [(-1, 1, None), (1, 0, 2), (1, 1, True), (1, 1, -1)])
def test_invalid_operational_configuration_is_rejected(values):
    with pytest.raises(ValueError):
        Scenario(*values)


def test_schedule_key_is_independent_of_request_order_and_private_labels():
    ids = ("a", "b", "c")
    forward = {cid: keyed_duration("task-v1", 42, cid, "assay") for cid in ids}
    backward = {cid: keyed_duration("task-v1", 42, cid, "assay") for cid in reversed(ids)}
    assert forward == backward and set(forward.values()) <= {1, 2, 4}
    with pytest.raises(ValueError):
        keyed_duration("task-v1", True, "a", "assay")


def test_common_delay_only_rescales_static_selection_without_deadline():
    runs = [run_order(fixture((d, d, d)), Scenario(2, 1, None), ("a", "b", "c")) for d in (0, 1, 4)]
    assert [[e.candidate_id for e in r.events if e.kind == "REQUEST_ACCEPTED"] for r in runs] == [
        ["a", "b"]
    ] * 3
    assert [r.time for r in runs] == [0, 2, 8]
    assert all(r.metrics["new_hits"] == 2 and r.metrics["spent"] == 2 for r in runs)


def test_all_small_serial_schedules_match_independent_enumeration():
    # 648 fixtures, six permutations each; truth is evaluator-only in this test.
    for durations in itertools.product((0, 1, 2), repeat=3):
        for truth in itertools.product((False, True), repeat=3):
            task = fixture(durations, truth)
            for deadline in (0, 1, 3):
                for order in itertools.permutations(("a", "b", "c")):
                    run = run_order(task, Scenario(2, 1, deadline), order)
                    expected = serial_reference(
                        order, dict(task.durations), dict(task._outcomes), 2, deadline
                    )
                    assert run.metrics["new_hits"] == expected, (durations, truth, deadline, order)


def test_deadline_creates_constructed_tradeoff_with_retained_unfinished_cost():
    task = fixture((4, 1, 1), (True, True, True))
    slow = run_order(task, Scenario(2, 1, 2), ("a", "b", "c"))
    fast = run_order(task, Scenario(2, 1, 2), ("b", "c", "a"))
    assert slow.metrics["new_hits"] == 0 and slow.metrics["reserved"] == 1
    assert fast.metrics["new_hits"] == 2 and fast.metrics["spent"] == 2
    long = run_order(task, Scenario(2, 1, 8), ("a", "b", "c"))
    assert long.metrics["new_hits"] == 2
