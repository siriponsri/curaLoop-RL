import csv
import io
import json

import pytest
from gymnasium.utils.env_checker import check_env

from curaloop._datasets import hiv_resource
from curaloop.domain import POLICIES, Scenario
from curaloop.export import csv_report, json_report
from curaloop.learning import ScreeningEnv, load_checkpoint, train_controllers
from curaloop.service import RunService, compare


def test_historical_dataset_is_real_and_provenance_is_complete():
    r = hiv_resource()
    assert len(r["records"]) == 1200
    assert r["manifest"]["source_rows"] == 41127
    assert r["manifest"]["invalid_smiles_removed"] == 7
    assert r["manifest"]["label_conflicts"] == 0
    assert "CC BY 4.0" in r["manifest"]["license"]
    assert all(row["canonical_smiles"] and row["morgan_on_bits"] for row in r["records"])
    assert len({row["canonical_smiles"] for row in r["records"]}) == 1200


def test_historical_random_seed_and_actual_delivery_have_correct_origin():
    scenario = Scenario(dataset="hiv_moleculenet_replay_v1", candidate_count=60, initial_count=6,
                        budget_units=2, batch_size=2)
    a, b = RunService(scenario), RunService(scenario, "random")
    assert a.initial_results == b.initial_results
    assert a.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
    a.finish()
    assert all(r.source_type == "HISTORICAL_PUBLIC_DATA" for r in a.results)
    assert all(e.data_origin == "HISTORICAL_PUBLIC_DATA" for e in a.events)
    assert a.report()["manifest"]["initial_label_selection"] == "Uniform random without using labels"


def test_json_and_csv_round_trip_include_configuration_provenance_and_ledger():
    run = RunService(Scenario(budget_units=3, batch_size=3), "random")
    run.finish()
    report = run.report()
    assert json.loads(json_report([report]))["runs"][0] == report
    rows = list(csv.DictReader(io.StringIO(csv_report([report]))))
    assert len(rows) == len(report["events"])
    assert json.loads(rows[0]["manifest_json"]) == report["manifest"]
    assert json.loads(rows[-1]["final_metrics_json"]) == report["metrics"]
    assert [json.loads(r["event_json"]) for r in rows] == report["events"]


def test_partial_export_contains_no_unrevealed_labels():
    run = RunService(Scenario(delay_steps=5), "random")
    run.next_batch()
    report = run.report()
    assert not report["delivered_results"]
    assert report["metrics"]["confirmed_hits"] == 0
    assert not any("active" in r for r in report["requests"])
    assert all(e["delivered_active"] is None for e in report["events"] if e["event_type"] != "INITIAL_LABEL")
    assert "private_truth" not in json_report([report]) and "y_true" not in csv_report([report])


def test_gymnasium_api_and_seed_determinism():
    env = ScreeningEnv(Scenario(candidate_count=24, initial_count=6, budget_units=3, batch_size=3))
    check_env(env, skip_render_check=True)
    a, ia = env.reset(seed=19)
    b, ib = env.reset(seed=19)
    assert (a == b).all() and ia == ib
    _, _, terminated, truncated, _ = env.step(0)
    assert terminated and not truncated


def test_actual_q_and_bandit_checkpoints_have_training_evidence():
    for policy in POLICIES[3:]:
        cp = load_checkpoint(policy)
        assert cp["training_episodes"] == 160
        assert len(cp["episode_returns"]) == 160
        assert cp["values"] and any(any(v != 0 for v in row) for row in cp["values"].values())
        assert cp["real_assay_labels_used_in_training"] is False
        assert not set(cp["training_episode_seeds"]) & set(range(10))


def test_training_is_reproducible_and_writes_real_json_weights(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    train_controllers(episodes=2, output=a)
    train_controllers(episodes=2, output=b)
    assert (a / "q_learning.json").read_bytes() == (b / "q_learning.json").read_bytes()
    assert json.loads((a / "q_learning.json").read_text())["values"]


@pytest.mark.parametrize("policy", POLICIES[3:])
def test_learned_controller_is_executed_with_real_delivered_rewards(policy):
    run = RunService(Scenario(candidate_count=24, initial_count=6, budget_units=3, batch_size=3), policy)
    run.finish()
    report = run.report()
    assert len(report["delivered_results"]) == 3
    assert report["manifest"]["algorithm_status"] in ("RL_TRAINED", "BANDIT_TRAINED")
    assert all(policy in r["explanation"] for r in report["requests"])
    assert report["manifest"]["controller"]["checkpoint_sha256"] == load_checkpoint(policy)["checkpoint_sha256"]


def test_five_policy_comparison_is_matched():
    reports = compare(Scenario(candidate_count=24, initial_count=6, budget_units=3), POLICIES)
    assert len(reports) == 5
    assert all(r["metrics"]["spent_units"] == 3 for r in reports)
    assert all(r["manifest"]["initial_label_ids"] == reports[0]["manifest"]["initial_label_ids"] for r in reports)
