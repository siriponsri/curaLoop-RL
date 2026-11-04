"""Validate explicit local task identities; no downloading, preprocessing or labels."""

import argparse
import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


def validate(payload: dict, root: Path) -> dict:
    if payload.get("schema_version") != "curaloop.research.task-registry.v1":
        raise ValueError("Unsupported task registry version.")
    schema = json.loads((root / "research/schemas/task_record.schema.json").read_text())
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("A local registry needs at least one explicit task record.")
    known_hiv = json.loads((root / "src/curaloop/resources/hiv_manifest.json").read_text())
    ids, families, resource_roles = set(), {}, {}
    checks = []
    for record in records:
        try:
            validator.validate(record)
        except ValidationError as error:
            raise ValueError("Invalid task record: " + error.message) from error
        task_id = record["task_id"]
        if task_id in ids:
            raise ValueError("Duplicate task identity: " + task_id)
        ids.add(task_id)
        if record["data_rights_status"] == "SOURCE_LINK_ONLY":
            raise ValueError("A source link is not a local-use data gate: " + task_id)
        if (
            record["label_mapping_status"] != "RESOLVED_WITH_SOURCE_EVIDENCE"
            or not record.get("label_mapping_evidence")
            or not record.get("label_mapping")
        ):
            raise ValueError("Unresolved label mapping: " + task_id)
        family, role = record.get("target_family"), record["controller_role"]
        if role != "regression_only" and not family:
            raise ValueError("Controller task requires an explicit family: " + task_id)
        if family and family in families and families[family] != role:
            raise ValueError("Task family crosses controller roles: " + family)
        if family:
            families[family] = role
        resource = record["dataset_sha256"]
        if resource in resource_roles and resource_roles[resource] != role:
            raise ValueError("The same resource crosses controller roles.")
        resource_roles[resource] = role
        if resource == known_hiv["resource_sha256"] and role == "final_test":
            raise ValueError("Previously inspected HIV cannot be an untouched final test.")
        if resource == known_hiv["resource_sha256"]:
            expected_mapping = {"CA": True, "CM": True, "CI": False}
            if (
                record["label_mapping"] != expected_mapping
                or any(type(v) is not bool for v in record["label_mapping"].values())
                or record["source_release"] != known_hiv["release"]
                or record["source_url"] != known_hiv["source_url"]
                or record["assay_id"] != "NCI_DTP_HIV_active_CA_or_CM_vs_CI"
            ):
                raise ValueError("Frozen HIV source/label identity was changed in metadata.")
        relative = payload.get("local_resource_files", {}).get(task_id)
        if not isinstance(relative, str) or not relative:
            raise ValueError("Task has no explicit local resource: " + task_id)
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or not path.is_file():
            raise ValueError("Missing or escaping task resource: " + task_id)
        if hashlib.sha256(path.read_bytes()).hexdigest() != resource:
            raise ValueError("Task resource checksum differs: " + task_id)
        checks.append({"task_id": task_id, "controller_role": role, "sha256": resource})
    return {
        "status": "PASS",
        "scope": "Local registry schema, identity and declared gate checks; not an independent rights/phenotype audit",
        "records": checks,
        "new_assay_tasks": 0
        if all(r["controller_role"] == "regression_only" for r in records)
        else None,
        "final_protocol_frozen": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--registry", type=Path, default=Path("research/manifests/task_registry.json")
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = validate(json.loads(args.registry.read_text()), root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
