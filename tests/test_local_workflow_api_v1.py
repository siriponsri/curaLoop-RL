"""Served API checks use actual RDKit subprocesses; no fake model successes."""

import time

import pytest
from fastapi.testclient import TestClient

from api.main import create_app

CSV = "compound_id,smiles\naspirin,CC(=O)Oc1ccccc1C(=O)O\nethanol,CCO\ninvalid,bad!\n"


@pytest.fixture
def application(tmp_path, monkeypatch):
    monkeypatch.delenv("CURALOOP_LOCAL_WORKFLOW_SESSION", raising=False)
    return create_app(tmp_path / "local-workflow-api.sqlite3")


def complete(client, identity):
    for _ in range(200):
        response = client.get("/api/v1/local-workflow/jobs/" + identity)
        assert response.status_code == 200, response.text
        row = response.json()
        if row["state"] in ("COMPLETED", "FAILED", "CANCELLED", "ABSTAINED"):
            return row
        time.sleep(0.05)
    raise AssertionError("Actual local workflow did not finish in the test envelope")


def test_same_origin_loopback_preview_and_external_refusal(application):
    with TestClient(application, base_url="http://127.0.0.1:18083") as client:
        path = "/api/v1/local-workflow/runtime"
        assert client.get(path, headers={"origin": "http://127.0.0.1:18083"}).status_code == 200
        assert client.get(path, headers={"origin": "https://outside.example"}).status_code == 403
        assert client.get(path, headers={"host": "outside.example"}).status_code == 403


def test_actual_submit_status_collect_and_structure(application):
    with TestClient(application) as client:
        runtime = client.get("/api/v1/local-workflow/runtime").json()
        assert runtime["deterministic_available"] and not runtime["model_session_authorized"]
        assert len(client.get("/api/v1/local-workflow/tools").json()["tools"]) == 3
        created = client.post(
            "/api/v1/local-workflow/jobs",
            json={
                "csv_text": CSV,
                "parameters": {"molecular_weight_max": 100, "logp_max": 5, "tpsa_max": 140},
            },
        )
        assert created.status_code == 202, created.text
        identity = created.json()["job_id"]
        row = complete(client, identity)
        assert row["state"] == "COMPLETED", row["error"]
        assert row["result"]["counts"] == {
            "input_rows": 3,
            "valid": 2,
            "rejected": 1,
            "selected": 1,
        }
        assert row["data"]["rdkit_version"] and row["result"]["new_model_calls"] == 0
        bundle = client.get(f"/api/v1/local-workflow/jobs/{identity}/artifacts/bundle.zip")
        assert bundle.status_code == 200 and bundle.content.startswith(b"PK")
        svg = client.get(f"/api/v1/local-workflow/jobs/{identity}/structures/0")
        assert svg.status_code == 200 and "<svg" in svg.text
        assert "sandbox" in svg.headers["content-security-policy"]
        assert (
            client.get(f"/api/v1/local-workflow/jobs/{identity}/artifacts/secret.json").status_code
            == 404
        )
        assert (
            client.get(f"/api/v1/local-workflow/jobs/{identity}/structures/2000").status_code == 404
        )


def test_invalid_scope_fields_and_unconfigured_model_do_not_run(application):
    with TestClient(application) as client:
        assert (
            client.post(
                "/api/v1/local-workflow/jobs", json={"csv_text": CSV, "mode": "agent"}
            ).status_code
            == 503
        )
        for extra in ({"path": "private-final16.csv"}, {"ssh_host": "elsewhere"}, {"mode": "paid"}):
            assert (
                client.post(
                    "/api/v1/local-workflow/jobs", json={"csv_text": CSV, **extra}
                ).status_code
                == 422
            )
        assert (
            client.post(
                "/api/v1/local-workflow/jobs", json={"csv_text": "wrong,header\na,b\n"}
            ).status_code
            == 422
        )
        assert client.get("/api/v1/local-workflow/jobs").json()["items"] == []


def test_tampered_export_is_refused_without_replacing_original(application):
    with TestClient(application) as client:
        identity = client.post("/api/v1/local-workflow/jobs", json={"csv_text": CSV}).json()[
            "job_id"
        ]
        row = complete(client, identity)
        store = application.state.local_workflow_store
        target = store.folder(identity) / f"attempt-{row['attempt']}/artifacts/selected.csv"
        target.write_text("compound_id,smiles\nforged,O\n")
        assert (
            client.get(f"/api/v1/local-workflow/jobs/{identity}/artifacts/bundle.zip").status_code
            == 409
        )
        assert store.read(identity)["result"]["manifest_sha256"] == row["result"]["manifest_sha256"]
        assert store.read(identity)["attempt"] == 1


def test_stale_revision_and_terminal_resume_are_refused(application):
    with TestClient(application) as client:
        identity = client.post("/api/v1/local-workflow/jobs", json={"csv_text": CSV}).json()[
            "job_id"
        ]
        row = complete(client, identity)
        assert (
            client.post(
                f"/api/v1/local-workflow/jobs/{identity}/resume",
                json={"expected_revision": row["revision"]},
            ).status_code
            == 409
        )
        assert (
            client.post(
                f"/api/v1/local-workflow/jobs/{identity}/cancel", json={"expected_revision": 0}
            ).status_code
            == 409
        )
        assert client.get("/api/v1/health").status_code == 200
