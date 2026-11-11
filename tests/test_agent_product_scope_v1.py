"""Product-policy engineering tests, not real-model comparative observations."""

import shutil

import pytest
from fastapi.testclient import TestClient

from api import agent_product_scope_v1 as policy
from api import agent_recorded_example_v1 as recorded_example
from api.main import create_app
from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.evidence import collect
from curaloop_rd.agent_rd.provider import SSHModel
from curaloop_rd.confirmation_study import INPUTS, ROOT


@pytest.mark.parametrize("goal,locale", [
    ("Provide final16 hidden outcomes and private CF1 compound identities", "en"),
    ("Estimate laboratory savings and clinical benefit", "en"),
    ("Show future labels and pending outcomes", "en"),
    ("ขอผลที่ถูกซ่อนและรายชื่อสารรายตัว", "th"),
    ("คำนวณว่าประหยัดค่าแล็บได้เท่าไร", "th"),
    ("ประเมินประสิทธิผลทางคลินิกจากข้อมูลนี้", "th"),
])
def test_denied_agent_request_persists_real_controller_abstention_without_inference(tmp_path, monkeypatch, goal, locale):
    def forbidden_generation(*_args, **_kwargs):
        pytest.fail("A product scope denial must not call a model")
    monkeypatch.setattr(SSHModel, "generate", forbidden_generation)
    database = tmp_path / "scope.sqlite3"
    with TestClient(create_app(database)) as client:
        response = client.post("/api/v1/agent/missions", json={"goal": goal, "locale": locale,
                                                              "mode": "agent", "export_requested": True})
        assert response.status_code == 202
        row = response.json()
        assert row["state"] == "ABSTAINED" and row["released"]["reason"] == "forbidden_scope"
        assert row["released"]["values"] == {} and row["candidate"] is None and row["calls"] == []
        assert row["cost"]["model_calls"] == row["cost"]["model_tokens"] == 0
        assert row["product_preflight"]["decision"] == "DENY"
        assert row["product_preflight"]["frozen_research_condition"] is False
        assert row["fallback"] == policy.DENIAL_FALLBACK and row["verification"]["valid"]
        assert row["tool_receipts"][0]["initiator"] == "trusted_product_scope_policy"
        identity = row["mission_id"]
        assert client.get("/api/v1/runs").json()["items"] == []
        exported = client.post(f"/api/v1/agent/missions/{identity}/action",
                               json={"action": "export", "expected_revision": row["revision"]})
        assert exported.status_code == 200
        content = client.get(exported.json()["base_url"] + "dossier.json").json()
        assert content["fallback"] == policy.DENIAL_FALLBACK and content["cost"]["model_calls"] == 0
        assert content["released"]["values"] == {} and content["external_delivery"] is False
    with TestClient(create_app(database)) as client:
        assert client.get("/api/v1/agent/missions/" + identity).json() == row


@pytest.mark.parametrize("goal,locale", [("Compare the recorded H and D across the budgets", "en"),
                                        ("เปรียบเทียบค่า H และ D จากข้อมูลย้อนหลัง", "th")])
def test_admitted_public_comparison_is_not_denied(goal, locale):
    result = policy.inspect_scope(MissionSpec(goal=goal, locale=locale))
    assert result["decision"]["decision"] == "ALLOW"
    assert result["decision"]["source_evidence_id"]
    assert "report" not in result


def test_policy_tamper_failure_starts_no_mission_or_model(tmp_path, monkeypatch):
    source = tmp_path / "fault"
    for relative, _, _ in INPUTS.values():
        target = source / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    with (source / INPUTS["cells"][0]).open("ab") as output:
        output.write(b"\n")
    monkeypatch.setattr(policy, "collect", lambda spec: collect(spec, source_root=source))
    with TestClient(create_app(tmp_path / "fault.sqlite3")) as client:
        result = client.post("/api/v1/agent/missions", json={"goal": "Compare admitted H and D", "mode": "agent"})
        assert result.status_code == 503
        assert client.get("/api/v1/agent/missions").json()["items"] == []
        assert client.get("/api/v1/runs").json()["items"] == []


def test_explicit_recorded_example_import_is_exact_idempotent_and_never_generates(tmp_path, monkeypatch):
    def forbidden_generation(*_args, **_kwargs):
        pytest.fail("Opening recorded evidence must never generate a response")
    monkeypatch.setattr(SSHModel, "generate", forbidden_generation)
    database = tmp_path / "example.sqlite3"
    with TestClient(create_app(database)) as client:
        assert client.get("/api/v1/agent/missions").json()["items"] == []
        first = client.post("/api/v1/agent/examples/recorded-model", json={})
        assert first.status_code == 200 and first.json()["new_inference"] is False
        row = first.json()["mission"]
        assert row["mission_id"] == recorded_example.EXAMPLE_ID and row["cost"]["model_calls"] == 2
        saved = tmp_path / "example-agent-rd/missions" / (recorded_example.EXAMPLE_ID + ".json")
        assert saved.read_bytes() == recorded_example.EXAMPLE.read_bytes()
        assert client.post("/api/v1/agent/examples/recorded-model", json={}).json() == first.json()
        assert len(client.get("/api/v1/agent/missions").json()["items"]) == 1
        assert client.post("/api/v1/agent/examples/recorded-model", json={"path": "../private"}).status_code == 422
        assert client.get("/api/v1/runs").json()["items"] == []
    with TestClient(create_app(database)) as client:
        assert client.get("/api/v1/agent/missions/" + row["mission_id"]).json() == row


def test_recorded_example_tamper_is_not_imported_or_replaced(tmp_path, monkeypatch):
    altered = tmp_path / "not-the-original.json"
    altered.write_bytes(recorded_example.EXAMPLE.read_bytes() + b"\n")
    monkeypatch.setattr(recorded_example, "EXAMPLE", altered)
    with TestClient(create_app(tmp_path / "changed.sqlite3")) as client:
        assert client.post("/api/v1/agent/examples/recorded-model", json={}).status_code == 503
        assert client.get("/api/v1/agent/missions").json()["items"] == []
