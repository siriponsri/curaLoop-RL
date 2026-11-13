"""Actual local-process acceptance and constructed recovery/integrity failures."""

import json

import pytest

from curaloop_rd.local_agent_v1 import engine as engine_module
from curaloop_rd.local_agent_v1.chemistry import FilterSpec
from curaloop_rd.local_agent_v1.engine import LocalWorkflowEngine
from curaloop_rd.local_agent_v1.store import JobConflict, JobStore
from curaloop_rd.local_agent_v1.workflow import build_bundle, inspect_bundle

CSV = "compound_id,smiles\naspirin,CC(=O)Oc1ccccc1C(=O)O\nethanol,CCO\ninvalid,bad!\n"
PARAMETERS = {"molecular_weight_max": 100, "logp_max": 5, "tpsa_max": 140}


def spec(mode="deterministic"):
    return {
        "csv_text": CSV,
        "parameters": PARAMETERS,
        "mode": mode,
        "goal": "Keep molecular weight at most 100 g/mol",
        "locale": "en",
    }


def test_actual_bundle_counts_content_provenance_and_tamper_detection(tmp_path):
    root = tmp_path / "artifacts"
    result = build_bundle(root, CSV, FilterSpec(**PARAMETERS))
    assert result["counts"] == {"input_rows": 3, "valid": 2, "rejected": 1, "selected": 1}
    assert inspect_bundle(root, result["manifest_sha256"], result["bundle_sha256"])[
        "evidence_ready"
    ]
    report = json.loads((root / "report.json").read_text(encoding="utf-8"))
    assert report["rdkit_version"] and report["tools"]["chemistry_source_sha256"]
    assert (
        "ethanol" in (root / "selected.csv").read_text()
        and "aspirin" not in (root / "selected.csv").read_text()
    )
    (root / "bundle.zip").write_bytes(b"changed download")
    with pytest.raises(ValueError, match="Download bundle"):
        inspect_bundle(root, result["manifest_sha256"], result["bundle_sha256"])


def test_changed_artifact_cannot_be_collected_as_current(tmp_path):
    root = tmp_path / "artifacts"
    result = build_bundle(root, CSV, FilterSpec(**PARAMETERS))
    (root / "selected.csv").write_text("compound_id,smiles\ninvented,CC\n")
    with pytest.raises(ValueError, match="artifact changed"):
        inspect_bundle(root, result["manifest_sha256"])


def test_actual_rdkit_child_process_and_persisted_completion(tmp_path):
    store = JobStore(tmp_path / "jobs")
    row = store.create(spec())
    finished = LocalWorkflowEngine(store).run(row["job_id"])
    assert finished["state"] == "COMPLETED", finished["error"]
    assert finished["result"]["counts"]["selected"] == 1
    assert finished["result"]["new_model_calls"] == 0 and not finished["provider_calls"]
    assert finished["result"]["tool_cpu_seconds"] > 0
    assert any(
        e["changes"].get("process", {}).get("pid")
        for e in store.history(row["job_id"])[1:]
        if isinstance(e["changes"].get("process"), dict)
    )
    restored = JobStore(tmp_path / "jobs")
    restored.recover_interrupted()
    assert restored.read(row["job_id"]) == finished
    assert LocalWorkflowEngine(restored).run(row["job_id"]) == finished


def test_no_provider_is_an_explicit_failure_without_tool_or_deterministic_fallback(tmp_path):
    store = JobStore(tmp_path / "jobs")
    row = store.create(spec("agent"))
    finished = LocalWorkflowEngine(store).run(row["job_id"])
    assert finished["state"] == "FAILED" and "model session" in finished["error"]
    assert not finished["provider_calls"]
    assert not (store.folder(row["job_id"]) / "attempt-1/artifacts").exists()


def test_cancel_between_process_start_and_state_commit_stops_only_owned_handle(
    tmp_path, monkeypatch
):
    store = JobStore(tmp_path / "jobs")
    row = store.create(spec())
    actual_popen = engine_module.subprocess.Popen
    owned = []

    def start_and_cancel(*args, **kwargs):
        process = actual_popen(*args, **kwargs)
        owned.append(process)
        current = store.read(row["job_id"])
        store.update(
            row["job_id"],
            current["revision"],
            detail="Constructed cancellation race",
            state="CANCEL_REQUESTED",
        )
        return process

    monkeypatch.setattr(engine_module.subprocess, "Popen", start_and_cancel)
    result = LocalWorkflowEngine(store).run(row["job_id"])
    assert result["state"] == "CANCELLED"
    assert owned and all(p.poll() is not None for p in owned)


def test_revision_conflict_and_restart_require_explicit_resume(tmp_path):
    store = JobStore(tmp_path / "jobs")
    row = store.create(spec())
    running = store.update(
        row["job_id"],
        row["revision"],
        detail="Constructed interrupted execution",
        state="COMPUTING",
        process={"pid": 12345},
    )
    with pytest.raises(JobConflict):
        store.update(row["job_id"], row["revision"], detail="Stale revision", state="COMPLETED")
    store.recover_interrupted()
    recovered = store.read(row["job_id"])
    assert recovered["state"] == "INTERRUPTED" and recovered["process"] is None
    assert recovered["revision"] > running["revision"]
    assert LocalWorkflowEngine(store).run(row["job_id"]) == recovered
