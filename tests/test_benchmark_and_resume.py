from copy import deepcopy

import pytest

from curaloop.benchmark import predictor_benchmark, summarize
from curaloop.domain import Scenario
from curaloop.service import RunService


def test_partial_pending_snapshot_restores_and_continues_identically():
    a = RunService(Scenario(candidate_count=30, initial_count=6, budget_units=8, delay_steps=3), "greedy")
    a.next_batch()
    a.advance()
    b = RunService.restore(a.report())
    assert a.events == b.events and a.pending == b.pending
    a.finish()
    b.finish()
    assert a.events == b.events and a.metrics == b.metrics


def test_completed_snapshot_reconciles_and_corruption_is_rejected():
    a = RunService(Scenario(budget_units=2), "random")
    a.finish()
    assert RunService.restore(a.report()).events == a.events
    corrupt = deepcopy(a.report())
    corrupt["metrics"]["confirmed_hits"] += 1
    with pytest.raises(ValueError, match="reconciled"):
        RunService.restore(corrupt)
    corrupt = deepcopy(a.report())
    corrupt["manifest"]["dataset"]["sha256"] = "bad"
    with pytest.raises(ValueError, match="hash"):
        RunService.restore(corrupt)


def test_scaffold_benchmark_runs_with_disjoint_split():
    report = predictor_benchmark()
    assert report["status"] == "EXECUTED"
    assert report["scaffold_overlap"] == 0
    assert set(report["train_ids"]).isdisjoint(report["test_ids"])
    assert report["train_count"] + report["test_count"] == 1200
    assert 0 <= report["auroc"] <= 1 and 0 <= report["average_precision"] <= 1
    assert report["train_actives"] > 0 and report["test_actives"] > 0


def test_paired_summary_uses_paired_seed_differences():
    reports = [{"manifest": {"policy_id": policy, "seed": seed}, "metrics": {"confirmed_hits": hits}}
               for policy, values in (("random", [0, 1, 2]), ("greedy", [1, 2, 3]))
               for seed, hits in enumerate(values)]
    summary = summarize(reports, bootstrap_samples=100)
    assert summary["paired_contrasts"][0]["mean_hit_difference"] == 1
    assert summary["paired_contrasts"][0]["bootstrap_95_percentile_interval"] == [1, 1]


@pytest.mark.parametrize("seed", range(8))
def test_budget_conservation_across_stress_conditions(seed):
    scenario = Scenario(seed=seed, candidate_count=30, initial_count=6, budget_units=13,
                        batch_size=3, assay_cost_units=2, delay_steps=seed % 3,
                        delay_jitter=seed % 4, missing_percent=seed * 10)
    run = RunService(scenario, "random")
    run.finish()
    assert run.metrics["spent_units"] == 12 and run.metrics["remaining_units"] == 1
    assert not run.pending and len(run.results) == 6
    assert all(p["spent_units"] + p["reserved_units"] + p["remaining_units"] == 13 for p in run.curve)
