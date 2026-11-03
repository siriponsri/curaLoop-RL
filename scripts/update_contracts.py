"""Generate versioned runtime schemas from actual public contracts and a zero-budget run."""

import json
from pathlib import Path

from curaloop.domain import Scenario
from curaloop.service import RunService


def infer(value):
    if value is None:
        return {"type": ["null", "object", "string", "number", "boolean", "array"]}
    if isinstance(value, bool):
        return {"type": "boolean"}
    if isinstance(value, str):
        return {"type": "string"}
    if isinstance(value, int):
        return {"type": "integer"}
    if isinstance(value, float):
        return {"type": "number"}
    if isinstance(value, (list, tuple)):
        return {"type": "array", "items": infer(value[0]) if value else {}}
    if isinstance(value, dict):
        return {"type": "object", "additionalProperties": False,
                "required": list(value), "properties": {k: infer(v) for k, v in value.items()}}
    raise TypeError(type(value))


def main():
    run = RunService(Scenario(budget_units=0))
    report = run.report()
    manifest = infer(report["manifest"])
    manifest["properties"]["budget_units"]["minimum"] = 0
    manifest["properties"]["controller"] = {"type": ["object", "null"]}
    manifest["properties"]["working_tree_dirty"] = {"type": ["boolean", "null"]}
    manifest["properties"]["dataset_provenance"] = {"type": "object"}
    observation = infer(run.observation.to_dict())
    observation["properties"]["available_features"] = {
        "type": "object", "additionalProperties": {"type": "array", "items": {"type": "number"}}}
    observation["properties"]["controller_json"] = {"type": ["string", "null"]}
    event = infer(report["events"][0])
    props = event["properties"]
    for key in ("compound_id", "request_id"):
        props[key] = {"type": ["string", "null"]}
    props["due_at_step"] = {"type": ["integer", "null"], "minimum": 0}
    props["delivered_active"] = {"type": ["boolean", "null"]}
    props["event_type"] = {"enum": ["RUN_STARTED", "INITIAL_LABEL", "REQUEST_ACCEPTED", "REQUEST_REJECTED",
                                    "RESULT_PENDING", "RESULT_DELIVERED", "RESULT_MISSING", "CLOCK_ADVANCED", "RUN_STOPPED"]}
    props["step"]["minimum"] = props["cost_units"]["minimum"] = 0
    event["allOf"] = [{"if": {"properties": {"event_type": {"not": {"enum": ["INITIAL_LABEL", "RESULT_DELIVERED"]}}}},
                       "then": {"properties": {"delivered_active": {"type": "null"}}}}]
    for name, schema in (("run_manifest", manifest), ("policy_observation", observation), ("experiment_event", event)):
        schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
        schema["title"] = name + " v1.1"
        schema["properties"]["schema_version"] = {"const": "1.1"}
        (Path("contracts") / f"{name}.schema.json").write_text(json.dumps(schema, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
