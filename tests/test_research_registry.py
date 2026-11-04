import copy
import json
from pathlib import Path

import pytest

from research.task_registry import validate

ROOT = Path(__file__).resolve().parents[1]


def registry():
    return json.loads((ROOT / "research/manifests/task_registry.json").read_text())


def test_existing_hiv_is_registered_as_known_regression_only():
    result = validate(registry(), ROOT)
    assert result["status"] == "PASS" and result["new_assay_tasks"] == 0
    assert result["final_protocol_frozen"] is False


@pytest.mark.parametrize(
    "change",
    [
        "unresolved",
        "no_evidence",
        "link_only",
        "final_test",
        "wrong_hash",
        "escaping_file",
        "duplicate_id",
    ],
)
def test_missing_scientific_gates_cannot_become_executable_tasks(change):
    payload = registry()
    record = payload["records"][0]
    if change == "unresolved":
        record["label_mapping_status"] = "UNRESOLVED"
    elif change == "no_evidence":
        record["label_mapping_evidence"] = ""
    elif change == "link_only":
        record["data_rights_status"] = "SOURCE_LINK_ONLY"
    elif change == "final_test":
        record["controller_role"] = "final_test"
    elif change == "wrong_hash":
        record["dataset_sha256"] = "0" * 64
    elif change == "escaping_file":
        payload["local_resource_files"][record["task_id"]] = "../outside.gz"
    else:
        payload["records"].append(copy.deepcopy(record))
    with pytest.raises(ValueError):
        validate(payload, ROOT)


def test_related_task_family_cannot_cross_development_and_final_roles():
    payload = registry()
    first = payload["records"][0]
    first["controller_role"] = "development"
    second = copy.deepcopy(first)
    second["task_id"] = "another-endpoint-of-same-family"
    second["controller_role"] = "validation"
    payload["records"].append(second)
    payload["local_resource_files"][second["task_id"]] = payload["local_resource_files"][
        first["task_id"]
    ]
    with pytest.raises(ValueError, match="family crosses"):
        validate(payload, ROOT)


@pytest.mark.parametrize(
    "field,value",
    [
        ("label_mapping", {"CA": False, "CM": True, "CI": False}),
        ("source_release", "unreviewed-derivative"),
        ("source_url", "https://example.invalid/replacement.csv"),
        ("assay_id", "unverified-protein-specific-endpoint"),
    ],
)
def test_known_resource_cannot_be_relabelled_via_registry_metadata(field, value):
    payload = registry()
    payload["records"][0][field] = value
    with pytest.raises(ValueError, match="source/label identity"):
        validate(payload, ROOT)
