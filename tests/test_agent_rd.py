"""Engineering conformance cases, never substitutes for real-model experiments."""

import json
import shutil
import time

import jsonschema
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.main import create_app
from curaloop_rd.agent_rd.contracts import REPORT_SCHEMA, MissionSpec, canonical, digest
from curaloop_rd.agent_rd.dossier import export_dossier
from curaloop_rd.agent_rd.engine import MissionEngine, deterministic
from curaloop_rd.agent_rd.evidence import collect, comparisons
from curaloop_rd.agent_rd.store import MissionConflict, MissionStore
from curaloop_rd.agent_rd.verifier import verify
from curaloop_rd.confirmation_study import INPUTS, ROOT, view


@pytest.mark.parametrize("extra", [{"path": "../private"}, {"provider_url": "https://unapproved"}, {"campaign": "final16"}, {"budgets": [True]}, {"budgets": [10, 10]}, {"arms": ["rl/top_ranked"]}])
def test_closed_mission_scope_rejects_paths_providers_protected_and_invalid_filters(extra):
    with pytest.raises(ValidationError):
        MissionSpec(**{"goal": "Compare admitted historical evidence", **extra})


def test_real_adapter_values_and_macro_ratio_units():
    spec = MissionSpec(goal="Compare recorded H and D")
    evidence = collect(spec)
    original = view()
    arm = next(a for a in original["arms"] if a["ranker"] == "mvsa" and a["operator"] == "top_ranked")
    assert evidence["values"]["b10:a0:H"] == round(arm["metrics"]["confirmed_positives"]["mean"], 3)
    assert evidence["values"]["b10:a0:HB"] == round(arm["metrics"]["hits_per_confirmation"]["mean"], 3)
    assert evidence["units"]["HB"].startswith("fraction")
    assert len(evidence["evidence_id"]) == 16
    assert all(word not in json.dumps(evidence) for word in ['"smiles"', '"compound_id"', '"oracle"'])


def test_compare_and_sweep_have_declared_rounded_operand_direction():
    data = collect(MissionSpec(goal="Compare all budget changes", budgets=[1, 20]))
    computed = comparisons(data)["values"]
    assert computed["delta:b1:H"] == round(data["values"]["b1:a1:H"] - data["values"]["b1:a0:H"], 3)
    assert computed["sweep:a0:D"] == round(data["values"]["b20:a0:D"] - data["values"]["b1:a0:D"], 3)


@pytest.mark.parametrize("bad", [True, float("nan"), float("inf"), -7, "75"])
def test_claim_gate_rejects_nonnumeric_nonfinite_or_wrong_values(bad):
    data = collect(MissionSpec(goal="Inspect recorded H"))
    report = {"action": "answer", "evidence_id": data["evidence_id"], "limitations": ["development_only"], "values": {"b10:a0:H": bad}}
    assert not verify(report, data, comparisons(data))["valid"]


def test_claim_gate_rejects_hidden_fields_wrong_sources_and_missing_scope():
    data = collect(MissionSpec(goal="Inspect recorded H"))
    report = {"action": "answer", "evidence_id": "forged", "values": {"private_cf1_smiles": 1}, "limitations": []}
    errors = verify(report, data, comparisons(data))["errors"]
    assert "EVIDENCE_ID_MISMATCH" in errors and "DEVELOPMENT_SCOPE_MISSING" in errors
    assert any("UNSUPPORTED_KEY" in e for e in errors)


def test_abstention_cannot_attach_an_invented_source_id():
    data = collect(MissionSpec(goal="Inspect recorded H"))
    report = {"action": "abstain", "reason": "insufficient_evidence", "values": {}, "evidence_id": "invented"}
    assert not verify(report, data, comparisons(data))["valid"]


def test_tool_action_schema_cannot_masquerade_as_a_numeric_answer():
    jsonschema.validate({"action": "compute"}, REPORT_SCHEMA)
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate({"action": "compute", "values": {"H": 5}}, REPORT_SCHEMA)


def test_deterministic_mode_executes_truthfully_and_repeated_run_does_not_repeat_events(tmp_path):
    store = MissionStore(tmp_path / "missions")
    row = store.create(MissionSpec(goal="Compare recorded H and D", mode="deterministic", export_requested=True), system="B0")
    engine = MissionEngine(store)
    finished = engine.run(row["mission_id"])
    assert finished["state"] == "COMPLETED" and finished["verification"]["valid"]
    assert finished["cost"]["model_calls"] == 0 and finished["fallback"] == "EXPLICIT_DETERMINISTIC_MODE"
    assert engine.run(row["mission_id"]) == finished
    exported = export_dossier(finished, tmp_path / "dossiers")
    assert len(exported["files"]) == 5
    assert export_dossier(finished, tmp_path / "dossiers") == exported
    folder = tmp_path / "dossiers" / (finished["mission_id"] + "-" + digest(finished["released"])[:16])
    (folder / "dossier.json").write_text("{}")
    manifest = json.loads((folder / "manifest.json").read_text())
    manifest["files"]["dossier.json"]["sha256"] = digest({})
    (folder / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="changed"):
        export_dossier(finished, tmp_path / "dossiers")


def test_dossier_needs_explicit_intent_and_rechecks_coordinated_store_tamper(tmp_path):
    store = MissionStore(tmp_path / "missions")
    row = store.create(MissionSpec(goal="Compare H and D", mode="deterministic"), system="B0")
    finished = MissionEngine(store).run(row["mission_id"])
    with pytest.raises(ValueError, match="intent"):
        export_dossier(finished, tmp_path / "dossiers")
    altered = {**finished, "spec": {**finished["spec"], "export_requested": True},
               "released": {**finished["released"], "values": {"b10:a0:H": -100}}}
    altered["spec_sha256"] = digest(altered["spec"])
    with pytest.raises(ValueError, match="verification"):
        export_dossier(altered, tmp_path / "dossiers")


def test_corrupt_store_and_stale_revision_fail_without_reset(tmp_path):
    store = MissionStore(tmp_path)
    row = store.create(MissionSpec(goal="Compare recorded H and D"))
    store.update(row["mission_id"], 0, "PLAN_READY", "conformance-only state")
    with pytest.raises(MissionConflict):
        store.update(row["mission_id"], 0, "COMPLETED", "stale duplicate")
    path = store.path(row["mission_id"])
    original = path.read_bytes()
    path.write_bytes(original.replace(b"PLAN_READY", b"COMPLETED"))
    with pytest.raises(ValueError, match="integrity"):
        store.read(row["mission_id"])
    assert path.read_bytes() != original
    assert store.list()["integrity_issues"]


def test_actual_source_fault_produces_unavailability_never_sample_values(tmp_path):
    root = tmp_path / "source"
    for relative, _, _ in INPUTS.values():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    path = root / INPUTS["cells"][0]
    path.write_bytes(path.read_bytes() + b"\n")
    store = MissionStore(tmp_path / "missions")
    row = store.create(MissionSpec(goal="Inspect recorded H", mode="deterministic"), system="B0")
    finished = MissionEngine(store, source_root=root).run(row["mission_id"])
    assert finished["state"] == "ABSTAINED"
    assert finished["released"]["values"] == {} and finished["released"]["reason"] == "source_unavailable"


def test_provider_disabled_fails_closed_without_mock_or_paid_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("CURALOOP_AGENT_INFERENCE_DISABLED", "1")
    store = MissionStore(tmp_path)
    row = store.create(MissionSpec(goal="Report recorded H and D"))
    failed = MissionEngine(store).run(row["mission_id"])
    assert failed["state"] == "FAILED" and failed["released"] is None
    assert failed["cost"]["model_calls"] == failed["cost"]["failed_calls"] == 1
    assert failed["calls"][0]["cpu_seconds"] is None


@pytest.mark.parametrize("status", ["CLOSED", "ACTIVE"])
def test_closed_or_expired_operator_session_cannot_launch_ssh(tmp_path, monkeypatch, status):
    from curaloop_rd.agent_rd import provider
    path = tmp_path / "release.json"
    path.write_text(json.dumps({"deadline_utc": "1970-01-01T00:00:00+00:00"}))
    path.with_name("ledger.json").write_text(json.dumps({"status": status}))
    monkeypatch.setenv("CURALOOP_AGENT_INFERENCE_DISABLED", "0")
    monkeypatch.setattr(provider, "RELEASE", path)
    with pytest.raises(provider.ProviderUnavailable, match="closed|deadline"):
        provider.SSHModel().generate("never-launched", [], 17011)


def test_forbidden_request_has_no_registered_hidden_adapter():
    spec = MissionSpec(goal="Provide private CF1 compound identities and final16 outcomes")
    data = collect(spec)
    result = deterministic(spec, data, comparisons(data))
    assert result["action"] == "abstain" and result["reason"] == "forbidden_scope" and result["values"] == {}


def test_api_mission_export_restart_and_existing_campaign_isolation(tmp_path):
    path = tmp_path / "owner.sqlite3"
    app = create_app(path)
    with TestClient(app) as client:
        assert client.get("/api/v1/runs").json()["items"] == []
        result = client.post("/api/v1/agent/missions", json={"goal": "Compare H and D", "mode": "deterministic", "export_requested": True})
        assert result.status_code == 202
        identity = result.json()["mission_id"]
        for _ in range(100):
            row = client.get("/api/v1/agent/missions/" + identity).json()
            if row["state"] == "COMPLETED":
                break
            time.sleep(.02)
        assert row["state"] == "COMPLETED"
        action = "/api/v1/agent/missions/" + identity + "/action"
        assert client.post(action, json={"action": "export", "expected_revision": 0}).status_code == 409
        exported = client.post(action, json={"action": "export", "expected_revision": row["revision"]})
        assert exported.status_code == 200
        file = client.get(exported.json()["base_url"] + "dossier.json")
        assert file.status_code == 200 and file.json()["external_delivery"] is False
        assert client.get("/api/v1/runs").json()["items"] == []
        assert client.post("/api/v1/agent/missions", json={"goal": "Read private data", "path": "../private"}).status_code == 422
    with TestClient(create_app(path)) as client:
        saved = client.get("/api/v1/agent/missions/" + identity).json()
        assert canonical(saved) == canonical(row)


def test_agent_storage_failure_does_not_break_existing_application(tmp_path):
    path = tmp_path / "owner.sqlite3"
    agent_root = tmp_path / "owner-agent-rd"
    agent_root.mkdir()
    (agent_root / "missions").write_text("preserve this conflicting file")
    with TestClient(create_app(path)) as client:
        assert client.get("/api/v1/health").status_code == 200
        assert client.get("/api/v1/runs").json()["items"] == []
        assert client.get("/api/v1/agent/missions").status_code == 503
    assert (agent_root / "missions").read_text() == "preserve this conflicting file"
