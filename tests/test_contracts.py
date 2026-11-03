import json
from dataclasses import asdict
from pathlib import Path

import jsonschema
import pytest

from curaloop.domain import Scenario
from curaloop.service import RunService

ROOT = Path(__file__).parents[1] / "contracts"


@pytest.mark.parametrize("dataset", ["synthetic_linear_v1", "hiv_moleculenet_replay_v1"])
@pytest.mark.parametrize("policy", ["greedy", "q_learning"])
def test_actual_contracts_accept_public_data_and_reject_extra_truth(dataset, policy):
    run = RunService(Scenario(dataset=dataset, candidate_count=24, initial_count=6, budget_units=1), policy)
    observation = json.loads(json.dumps(run.observation.to_dict()))
    obs_schema = json.loads((ROOT / "policy_observation.schema.json").read_text())
    jsonschema.validate(observation, obs_schema)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({**observation, "hidden_labels": [True]}, obs_schema)
    run.finish()
    manifest_schema = json.loads((ROOT / "run_manifest.schema.json").read_text())
    jsonschema.validate(run.report()["manifest"], manifest_schema)
    event_schema = json.loads((ROOT / "experiment_event.schema.json").read_text())
    for event in run.events:
        jsonschema.validate(asdict(event), event_schema)


def test_contract_allows_zero_budget_and_refuses_pre_delivery_label():
    run = RunService(Scenario(budget_units=0))
    jsonschema.validate(run.report()["manifest"], json.loads((ROOT / "run_manifest.schema.json").read_text()))
    event = asdict(run.events[0])
    event["delivered_active"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(event, json.loads((ROOT / "experiment_event.schema.json").read_text()))
