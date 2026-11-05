"""Constructed selected-row, public-input and accounting checks before outcomes."""

import copy
import gzip
import hashlib
import json
from collections import Counter

import pytest

from research.event_time import Observation
from research.planning_v3.policy import METHODS, PolicySession
from research.planning_v3.queue import residual_law
from research.study_v1.campaign import initial_ids, make_task, run_campaign, support_law
from research.study_v1.labels import LabelAccessError, prepare_role, project_labels, source_boolean


def fixture_payload(n=24):
    return {"task_id": "constructed-task", "role": "development", "family_id": "constructed-group",
            "records": [{"candidate_id": f"c{i:03}", "morgan_on_bits": [i, i + 30], "active": i % 3 == 0} for i in range(n)]}


@pytest.mark.parametrize("value, expected", [("0", False), ("0.0", False), ("1", True),
    ("1.0", True), ("1e0", True), (0, False), (1, True), (False, False), (True, True), (0.0, False)])
def test_source_numeric_boolean_semantics_without_string_truthiness(value, expected):
    assert source_boolean(value) is expected


@pytest.mark.parametrize("value", ["private-not-numeric", "nan", "inf", -1, 2, None, [], {}, float("nan")])
def test_bad_source_values_are_sanitized_and_never_inferred(value):
    with pytest.raises(LabelAccessError) as error:
        source_boolean(value)
    assert str(error.value) == "UNSUPPORTED_SOURCE_BOOLEAN_SEMANTICS"


def test_role_rejection_precedes_any_path_or_member_access():
    class Unreadable:
        def __truediv__(self, other):
            raise AssertionError("Forbidden role opened a path.")
    protocol = {"permitted_outcome_roles": ["development", "validation"]}
    with pytest.raises(LabelAccessError, match="FORBIDDEN_OUTCOME_ROLE"):
        prepare_role("final", protocol, Unreadable(), Unreadable())
    with pytest.raises(LabelAccessError, match="FORBIDDEN_OUTCOME_ROLE"):
        project_labels({"role": "final"}, b"private-not-gzip", {})


def test_validation_requires_actual_selection_proof_before_archive_access(tmp_path):
    protocol = {"permitted_outcome_roles": ["development", "validation"], "status": "FROZEN_BEFORE_GOAL4_OUTCOMES"}
    with pytest.raises(LabelAccessError, match="VALIDATION_REQUIRES_SELECTION_FREEZE"):
        prepare_role("validation", protocol, tmp_path, tmp_path / "out")


def test_selected_row_identity_hash_and_one_class_are_preserved():
    smi = "CCO"
    cid = "s-" + hashlib.sha256(smi.encode()).hexdigest()
    data = gzip.compress((json.dumps({"Assay_ID": "CHEMBL_TEST", "SMILES": smi, "Property": "0.0"}) + "\n").encode())
    feature = {"role": "development", "task_id": "CHEMBL_TEST", "member_sha256": hashlib.sha256(data).hexdigest(),
               "records": [{"source_row": 0, "canonical_smiles": smi, "candidate_id": cid}]}
    limits = {"maximum_rows_per_assay": 10, "maximum_row_bytes": 1024, "maximum_member_expanded_bytes": 10000}
    assert project_labels(feature, data, limits) == {cid: False}
    with pytest.raises(LabelAccessError, match="MEMBER_HASH_MISMATCH"):
        project_labels(feature, data + b"wrong", limits)
    bad = copy.deepcopy(feature)
    bad["task_id"] = "OTHER"
    with pytest.raises(LabelAccessError, match="SELECTED_ROW_IDENTITY_MISMATCH"):
        project_labels(bad, data, limits)


def test_duration_probabilities_match_policy_and_private_sampling_law():
    operation = {"id": "tail", "law": {"1": .5, "3": .25, "9": .25}, "role": "held_out", "capacity": 2, "deadline": 7}
    assert support_law(operation) == (1, 1, 3, 9)
    assert dict(residual_law(support_law(operation), 0)) == {1: .5, 3: .25, 9: .25}
    payload = fixture_payload()
    task = make_task(payload, 101, operation)
    from research.event_time import Campaign, Scenario
    obs = Campaign(task, Scenario(4, 2, 7, initial_ids(payload, 101, 4))).observe()
    policy = PolicySession(obs, "random", 101, support_law(operation), 2, 32)
    assert policy.law == (1, 1, 3, 9)
    values = Counter(d for seed in range(512) for _, d in make_task(payload, seed, operation).durations)
    assert .47 < values[1] / sum(values.values()) < .53
    assert .22 < values[3] / sum(values.values()) < .28


def test_hidden_outcome_permutation_cannot_change_initial_ids_features_or_durations():
    payload = fixture_payload()
    changed = copy.deepcopy(payload)
    for record in changed["records"]:
        record["active"] = not record["active"]
    operation = {"id": "same", "law": {"1": .5, "4": .5}}
    assert initial_ids(payload, 211, 4) == initial_ids(changed, 211, 4)
    a, b = make_task(payload, 211, operation), make_task(changed, 211, operation)
    assert a.candidates == b.candidates and a.durations == b.durations
    assert a.resource_sha256 != b.resource_sha256
    assert make_task({**payload, "records": list(reversed(payload["records"]))}, 211, operation).durations == a.durations


@pytest.mark.parametrize("method", METHODS)
def test_all_arms_account_to_deadline_and_reexecute_deterministically(method):
    payload = fixture_payload()
    operation = {"id": "constructed", "role": "familiar", "capacity": 2, "law": {"1": .5, "4": .5}, "deadline": 3}
    protocol = {"budget": 4, "initial_labels": 4}
    first = run_campaign(payload, 101, operation, method, 32, protocol)
    again = run_campaign(payload, 101, operation, method, 32, protocol)
    assert first["scientific_sha256"] == again["scientific_sha256"]
    assert first["metrics"]["time"] == 3
    assert first["metrics"]["accepted_exposure"] <= 4
    assert first["metrics"]["new_hits"] <= first["metrics"]["delivered"]
    assert first["policy_wall_seconds"] >= first["policy_setup_seconds"] > 0
    assert first["learned_action_share"] == 0
    assert json.loads(json.dumps(first))["scientific_sha256"] == first["scientific_sha256"]


def test_early_budget_exhaustion_is_advanced_to_deadline_without_flushing_late_jobs():
    payload = fixture_payload()
    protocol = {"budget": 2, "initial_labels": 4}
    operation = {"id": "quick", "role": "familiar", "capacity": 1, "law": {"1": 1}, "deadline": 10}
    result = run_campaign(payload, 101, operation, "random", 32, protocol)
    assert result["metrics"]["time"] == 10 and result["metrics"]["delivered"] == 2
    operation = {"id": "late", "role": "held_out", "capacity": 2, "law": {"9": 1}, "deadline": 3}
    result = run_campaign(payload, 101, operation, "random", 32, protocol)
    assert result["metrics"]["time"] == 3
    assert result["metrics"]["pending"] == result["metrics"]["reserved"] == 2
    assert result["metrics"]["new_hits"] == result["metrics"]["delivered"] == 0


def test_case_design_excludes_final_and_withholds_validation_and_new_operations():
    from pathlib import Path
    from research.study_v1.design import cases
    config = json.loads((Path(__file__).resolve().parents[2] / "research/configs/goal4_protocol_v1.json").read_text())
    tasks = [
        {"assay_id": "d1", "role": "development", "retained_structures": 128},
        {"assay_id": "d2", "role": "development", "retained_structures": 300},
        {"assay_id": "v1", "role": "validation", "retained_structures": 150},
        {"assay_id": "f1", "role": "final", "retained_structures": 600},
    ]
    canary = cases(config, tasks, "canary")
    assert len(canary) == 84
    assert {case["task_id"] for case in canary} == {"d2"}
    assert {case["operation"] for case in canary} == {"sequential", "async_mixed"}
    dev = cases(config, tasks, "development", config["seeds"])
    assert all(case["role"] == "development" for case in dev)
    cross = cases(config, tasks, "crossed", config["seeds"], 32)
    assert all(case["role"] != "final" for case in cross)
    assert all(case["operation"] in {"async_longtail", "single_shift"} for case in cross if case["role"] == "development")
    with pytest.raises(ValueError, match="frozen seed prefix"):
        cases(config, tasks, "development", [999])
    with pytest.raises(ValueError, match="Selected configuration"):
        cases(config, tasks, "crossed", config["seeds"], 256)


def test_family_weighting_does_not_turn_extra_assays_or_seeds_into_extra_groups():
    from research.study_v1.admin import family_means
    records = [
        {"family_id": "a", "task_id": "a1", "metrics": {"new_hits": value}} for value in (0, 2)
    ] + [
        {"family_id": "a", "task_id": "a2", "metrics": {"new_hits": 3}},
        {"family_id": "b", "task_id": "b1", "metrics": {"new_hits": 10}},
    ]
    assert family_means(records) == {"a": 2, "b": 10}
    assert sum(family_means(records).values()) / 2 == 6


def test_successful_private_projection_under_guard_needs_no_child_process(tmp_path, monkeypatch):
    # The test runner itself is inside active-process-limit1 Guard. Complete the
    # happy path with a constructed compressed source, including numeric strings.
    from pathlib import Path
    from research.benchmark_v3.prepare_features_v2 import sha_file
    from research.study_v1.identity import PACKET_RELATIVE, RUN_RELATIVE
    import subprocess
    def forbidden_child(*args, **kwargs):
        raise AssertionError("A guarded label projection attempted a child process.")
    monkeypatch.setattr(subprocess, "run", forbidden_child)
    root = tmp_path
    raw = root / "research/raw_data/external-benchmarks/fs-mol-0.1"
    cohort = raw / "feature-cohort-v2"
    cohort.mkdir(parents=True)
    config_path = root / "research/configs/goal3_feature_preparation_v2.json"
    config_path.parent.mkdir(parents=True)
    limits = {"maximum_rows_per_assay": 10, "maximum_row_bytes": 1024,
              "maximum_member_expanded_bytes": 10000, "maximum_member_compressed_bytes": 10000}
    config_path.write_text(json.dumps(limits))
    smi = "CCO"
    cid = "s-" + hashlib.sha256(smi.encode()).hexdigest()
    data = gzip.compress((json.dumps({"Assay_ID": "CHEMBL_TEST", "SMILES": smi, "Property": "0.0"}) + "\n").encode())
    archive = raw / "fsmol.tar"
    archive.write_bytes(data)
    header = raw / "header-audit-v2.json"
    header.write_text(json.dumps({"members": [{"name": "fs-mol/train/CHEMBL_TEST.jsonl.gz", "kind": "file", "bytes": len(data), "data_offset": 0}]}))
    feature = {"role": "development", "task_id": "CHEMBL_TEST", "family_id": "test-group",
               "source_member": "fs-mol/train/CHEMBL_TEST.jsonl.gz", "member_sha256": hashlib.sha256(data).hexdigest(),
               "records": [{"source_row": 0, "canonical_smiles": smi, "candidate_id": cid, "morgan_on_bits": [1, 3]}]}
    feature_path = cohort / "CHEMBL_TEST.features.json"
    feature_path.write_text(json.dumps(feature))
    manifest_path = cohort / "manifest.json"
    manifest_path.write_text(json.dumps({"status": "PASS_FEATURE_COHORT",
        "identities": {"archive_sha256": sha_file(archive), "header_index_sha256": sha_file(header)},
        "selected_assays": [{"role": "development", "assay_id": "CHEMBL_TEST", "family_id": "test-group",
                             "feature_file": feature_path.name, "feature_sha256": sha_file(feature_path)}]}))
    protocol = {"status": "FROZEN_BEFORE_GOAL4_OUTCOMES", "permitted_outcome_roles": ["development", "validation"],
                "cohort_manifest": manifest_path.relative_to(root).as_posix(), "cohort_manifest_sha256": sha_file(manifest_path),
                "cohort_config_sha256": sha_file(config_path)}
    output = root / RUN_RELATIVE / "private-inputs/development"
    output.parent.mkdir(parents=True)
    (root / ".gitignore").write_text(".local/\n")
    packet = root / PACKET_RELATIVE
    packet.mkdir(parents=True)
    (packet / "ignored-path-development-v1.json").write_text(json.dumps({
        "status": "PASS_GIT_IGNORE_PREFLIGHT", "output_relative": output.relative_to(root).as_posix(),
        "gitignore_sha256": sha_file(root / ".gitignore")}))
    result = prepare_role("development", protocol, root, output)
    payload = json.loads((output / result[0]["file"]).read_text())
    assert payload["records"][0]["active"] is False
    assert len(result) == 1 and (output / "manifest.json").exists()


def test_missing_private_ignore_proof_stops_before_archive_access(tmp_path):
    from research.study_v1.identity import RUN_RELATIVE
    protocol = {"permitted_outcome_roles": ["development", "validation"], "status": "FROZEN_BEFORE_GOAL4_OUTCOMES"}
    output = tmp_path / RUN_RELATIVE / "private-inputs/development"
    with pytest.raises(LabelAccessError, match="PRIVATE_OUTPUT_NOT_VERIFIED_IGNORED"):
        prepare_role("development", protocol, tmp_path, output)
