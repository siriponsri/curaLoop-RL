import subprocess
import sys
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import pytest

from curaloop._oracle import TruthStore, build_fixture
from curaloop.domain import Candidate, Event, ExperimentRequest, PublicDataset, Scenario, Selection
from curaloop.engine import Campaign
from curaloop.evaluation import curve_from_events, metrics_from_events
from curaloop.policies import propose
from curaloop.service import RunService, compare


def small(**kwargs):
    return Scenario(candidate_count=24, initial_count=6, budget_units=6, batch_size=3, **kwargs)


def select(run, n=1):
    return tuple(Selection(c, "test request") for c in run.observe().eligible_candidate_ids[:n])


def test_synthetic_generation_and_hash_are_deterministic():
    a, _, seed_a = build_fixture(small())
    b, _, seed_b = build_fixture(small())
    assert a == b and seed_a == seed_b
    assert len(a.sha256) == len(a.feature_sha256) == 64


@pytest.mark.parametrize("field,value", [("budget_units", -1), ("assay_cost_units", 0),
    ("assay_cost_units", float("nan")), ("delay_steps", -1), ("batch_size", 0), ("seed", True),
    ("missing_percent", 101), ("initial_count", 241)])
def test_invalid_scenarios_reject_before_run(field, value):
    with pytest.raises(ValueError):
        Scenario(**{field: value})


def test_unsupported_dataset_rejected():
    with pytest.raises(ValueError, match="Unsupported dataset"):
        Scenario(dataset="made_up_target")


def test_duplicate_candidate_ids_rejected():
    c = Candidate("a", (1.0,))
    with pytest.raises(ValueError, match="Duplicate"):
        PublicDataset("test", (c, c), "1", "hash", "hash")


@pytest.mark.parametrize("values", [(float("nan"),), (float("inf"),), ("bad",), (True,), ()])
def test_malformed_features_rejected(values):
    with pytest.raises(ValueError):
        Candidate("a", values)


def test_empty_pool_and_zero_budget_stop_without_worker():
    for scenario in (Scenario(candidate_count=0, initial_count=0), Scenario(budget_units=0)):
        run = Campaign(scenario, "greedy")
        run.finish()
        assert run.done and not run.requests and run.spent == 0


def test_observation_has_only_public_fields_and_immutable_data():
    run = Campaign(small(delay_steps=3), "random")
    obs = run.observe()
    assert not hasattr(obs, "truth") and not hasattr(obs, "labels") and not hasattr(obs, "oracle")
    assert len(obs.revealed_assay_results) == run.scenario.initial_count
    with pytest.raises(FrozenInstanceError):
        obs.step = 100
    with pytest.raises(TypeError):
        obs.available_features[0][1][0] = 9


def test_fake_leaking_policy_cannot_read_hidden_label():
    obs = Campaign(small(), "random").observe().to_dict()
    with pytest.raises(KeyError):
        _ = obs["private_truth"]
    with pytest.raises(TypeError):
        _ = obs["available_features"][obs["eligible_candidate_ids"][0]]["active"]


def test_worker_import_guard_blocks_simulator_import():
    import curaloop.policy_worker as worker
    code = ("import runpy,sys; n=runpy.run_path(sys.argv[1]); "
            "sys.meta_path.insert(0,n['DenyPrivateImports']()); import curaloop._oracle")
    p = subprocess.run([sys.executable, "-I", "-c", code, str(Path(worker.__file__))],
                       capture_output=True, text=True)
    assert p.returncode != 0
    assert "cannot import simulator internals" in p.stderr


def test_policy_is_invariant_to_public_row_order():
    obs = Campaign(small(), "greedy").observe()
    shuffled = replace(obs, eligible_candidate_ids=tuple(reversed(obs.eligible_candidate_ids)),
                       available_features=tuple(reversed(obs.available_features)))
    assert propose(obs) == propose(shuffled)


def test_private_truth_changes_cannot_change_first_action(monkeypatch):
    scenario = small()
    public, _, initial = build_fixture(scenario)
    initial_map = {r.compound_id: r.active for r in initial}
    first = Campaign(scenario, "greedy").suggest()
    def alternate(_):
        labels = {c.compound_id: initial_map.get(c.compound_id, True) for c in public.candidates}
        return public, TruthStore(labels), initial
    monkeypatch.setattr("curaloop.engine.build_fixture", alternate)
    assert Campaign(scenario, "greedy").suggest() == first


def test_budget_reserves_then_settles_once():
    run = Campaign(small(delay_steps=2), "random")
    run.submit(select(run, 3))
    assert (run.spent, run.reserved, run.remaining) == (0, 3, 3)
    run.advance(2)
    assert (run.spent, run.reserved, run.remaining) == (3, 0, 3)
    run.advance(2)
    assert run.spent == 3 and len(run.results) == 3


def test_rejected_overspend_has_no_partial_budget_or_requests():
    run = Campaign(replace(small(), budget_units=1), "random")
    with pytest.raises(ValueError, match="Insufficient"):
        run.submit(select(run, 2))
    assert run.spent == run.reserved == 0 and not run.requests
    assert run.events[-1].event_type == "REQUEST_REJECTED"


def test_duplicate_within_batch_and_repeat_request_rejected():
    run = Campaign(small(), "random")
    action = select(run)
    with pytest.raises(ValueError, match="Duplicate"):
        run.submit(action + action)
    assert not run.requests
    run.submit(action)
    with pytest.raises(ValueError, match="already tested"):
        run.submit(action)
    assert len(run.requests) == 1 and run.reserved == 1


def test_initial_labels_cannot_be_retested():
    run = Campaign(small(), "random")
    with pytest.raises(ValueError):
        run.submit((Selection(run.initial_results[0].compound_id, "invalid"),))


def test_unknown_candidate_and_capacity_rejected():
    run = Campaign(replace(small(), batch_size=1), "random")
    with pytest.raises(ValueError):
        run.submit((Selection("UNKNOWN", "invalid"),))
    with pytest.raises(ValueError, match="capacity"):
        run.submit(select(run, 2))


def test_delayed_truth_invisible_until_due_step():
    run = Campaign(small(delay_steps=3), "greedy")
    run.next_batch()
    known = run.observe().revealed_assay_results
    run.advance(2)
    assert not run.results and run.observe().revealed_assay_results == known
    assert all(e.delivered_active is None for e in run.events if e.event_type != "INITIAL_LABEL")
    run.advance()
    assert len(run.results) == 3 and len(run.observe().revealed_assay_results) == len(known) + 3


def test_oracle_refuses_unregistered_early_and_repeat_deliveries():
    oracle = TruthStore({"a": True})
    request = ExperimentRequest("q", "b", "a", "assay", 0, 3, 1, "test")
    with pytest.raises(ValueError, match="registered"):
        oracle.deliver("q", 3)
    oracle.register(request)
    with pytest.raises(ValueError, match="not due"):
        oracle.deliver("q", 2)
    assert oracle.deliver("q", 3).active is True
    with pytest.raises(ValueError, match="already delivered"):
        oracle.deliver("q", 4)


@pytest.mark.parametrize("cost", [-1, 0, float("nan"), float("inf"), True])
def test_raw_experiment_request_cannot_bypass_cost_validation(cost):
    with pytest.raises(ValueError, match="cost"):
        ExperimentRequest("q", "b", "a", "assay", 0, 3, cost, "invalid")


def test_partial_completion_with_jitter():
    run = Campaign(replace(small(), delay_steps=1, delay_jitter=5), "random")
    run.next_batch()
    due = sorted(r.due_at_step for r in run.pending)
    assert due[0] < due[-1]
    run.advance(due[0])
    assert 0 < len(run.results) < len(run.requests)
    assert len(run.results) + len(run.pending) == len(run.requests)


def test_zero_delay_reveals_only_after_valid_request():
    run = Campaign(small(delay_steps=0), "random")
    assert not run.results
    run.next_batch()
    assert len(run.results) == 3 and run.reserved == 0 and run.spent == 3


def test_missing_results_cost_money_but_are_neither_class_nor_hit():
    run = Campaign(replace(small(), missing_percent=100), "greedy")
    run.finish()
    m = metrics_from_events(run.events, 6, 1)
    assert m["missing_assays"] == 6 and m["confirmed_hits"] == m["delivered_assays"] == 0
    assert run.spent == 6 and len(run.observe().revealed_assay_results) == 6


def test_deterministic_replay_event_for_event():
    a, b = Campaign(small(), "uncertainty"), Campaign(small(), "uncertainty")
    a.finish()
    b.finish()
    assert a.events == b.events and a.requests == b.requests and a.results == b.results


def test_all_candidates_exhausted_and_repeated_finish_are_idempotent():
    run = Campaign(Scenario(candidate_count=3, initial_count=0, budget_units=100), "random")
    run.finish()
    events = run.events
    run.finish()
    assert run.events == events and len(run.results) == 3 and run.spent == 3


@pytest.mark.parametrize("policy", ["greedy", "uncertainty"])
def test_single_class_or_no_seed_has_explicit_random_fallback(policy):
    run = Campaign(Scenario(candidate_count=24, initial_count=0, budget_units=3), policy)
    decisions = run.suggest()
    assert all(d.model_status == "FALLBACK_RANDOM_ONE_CLASS" for d in decisions)
    assert all(d.predicted_probability is None for d in decisions)


def test_greedy_and_uncertainty_really_rank_differently():
    obs = Campaign(small(), "greedy").observe()
    greedy = propose(obs)
    uncertain = propose(replace(obs, current_policy_id="uncertainty"))
    assert all(d.model_status == "FITTED_LOGISTIC_UNCALIBRATED" for d in greedy + uncertain)
    assert [d.compound_id for d in greedy] != [d.compound_id for d in uncertain]
    assert [d.predicted_probability for d in greedy] == sorted((d.predicted_probability for d in greedy), reverse=True)


def test_equal_comparison_and_independent_runs():
    reports = compare(replace(small(), budget_units=3))
    manifests = [r["manifest"] for r in reports]
    for key in ("scenario_config", "initial_label_ids", "dataset"):
        assert manifests[0][key] == manifests[1][key] == manifests[2][key]
    assert len({m["run_id"] for m in manifests}) == 3
    assert all(r["metrics"]["spent_units"] == 3 for r in reports)
    a, b = RunService(small(), "random"), RunService(small(), "random")
    a.next_batch()
    assert not b.requests and b.metrics["remaining_units"] == 6


def test_metrics_reconcile_to_unique_delivered_events_not_seeds():
    run = Campaign(small(), "random")
    run.finish()
    m = metrics_from_events(run.events, 6, 1)
    results = [e for e in run.events if e.event_type == "RESULT_DELIVERED"]
    assert m["confirmed_hits"] == sum(e.delivered_active for e in results)
    assert m["spent_units"] == sum(e.cost_units for e in results)
    assert m["delivered_assays"] == len({e.compound_id for e in results}) == 6
    assert 0 <= m["auc_discovery_budget_normalized"] <= 1


def test_immutable_event_log_and_pre_reveal_guard():
    run = Campaign(small(), "random")
    with pytest.raises(FrozenInstanceError):
        run.events[0].step = 90
    assert isinstance(run.events, tuple)
    with pytest.raises(ValueError, match="Unrevealed"):
        Event("1.1", "e", "r", "s", "p", "RESULT_PENDING", 0, delivered_active=True)


def test_metric_reader_detects_duplicate_outcome_corruption():
    run = Campaign(small(), "random")
    run.finish()
    result = next(e for e in run.events if e.event_type == "RESULT_DELIVERED")
    with pytest.raises(ValueError, match="duplicate outcome"):
        curve_from_events(run.events + (result,), 6)
