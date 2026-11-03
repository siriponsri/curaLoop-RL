"""Durability, failure atomicity and public-only recovery contracts."""

import hashlib
import json
import sqlite3
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from api.storage import SnapshotStore, StorageError, encode
from curaloop.domain import Scenario
from curaloop.service import RunService


def config(**updates):
    return {
        "dataset": "synthetic_linear_v1",
        "seed": 42,
        "candidate_count": 30,
        "initial_count": 6,
        "budget_units": 6,
        "batch_size": 3,
        "delay_steps": 2,
        **updates,
    }


def create(client, **updates):
    response = client.post("/api/v1/runs", json={"scenario": config(**updates), "policy": "random"})
    assert response.status_code == 201, response.text
    return response.json()


def act(client, run, action, **updates):
    return client.post(
        f"/api/v1/runs/{run['session_id']}/{action}",
        json={"expected_revision": run["revision"], **updates},
    )


def test_pending_restart_preserves_identity_revision_delay_and_accounting(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        pending = act(client, create(client), "select").json()
        partial = act(client, pending, "advance").json()
        assert not partial["report"]["delivered_results"]
        original_export = client.get(f"/api/v1/runs/{partial['session_id']}/export").json()
    with TestClient(create_app(path)) as client:
        recovered = client.get(f"/api/v1/runs/{partial['session_id']}").json()
        assert recovered["revision"] == partial["revision"]
        assert recovered["report"] == partial["report"]
        assert recovered["pending"] == partial["pending"]
        assert recovered["persistence"]["recovered"]
        assert (
            recovered["persistence"]["creation_identity"]
            == partial["persistence"]["creation_identity"]
        )
        assert client.get(f"/api/v1/runs/{partial['session_id']}/export").json() == original_export
        delivered = act(client, recovered, "advance").json()
        reference = RunService(Scenario(**config()), "random")
        reference.next_batch()
        reference.advance(2)
        assert delivered["report"]["events"] == reference.report()["events"]
        assert delivered["report"]["metrics"] == reference.metrics
        assert delivered["report"]["metrics"]["spent_units"] == 3
        assert delivered["report"]["metrics"]["reserved_units"] == 0


@pytest.mark.parametrize("missing_percent", [0, 100])
def test_completed_restart_and_replay_are_exact(tmp_path, missing_percent):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        done = act(client, create(client, missing_percent=missing_percent), "finish").json()
    with TestClient(create_app(path)) as client:
        recovered = client.get(f"/api/v1/runs/{done['session_id']}").json()
        assert recovered["done"] and recovered["report"] == done["report"]
        replay = act(client, recovered, "replay").json()
        assert replay["report"]["events"] == done["report"]["events"]
        assert replay["report"]["metrics"] == done["report"]["metrics"]
        assert replay["report"]["metrics"]["spent_units"] == 6


def test_stale_retry_after_restart_does_not_charge_twice(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        old = create(client)
        selected = act(client, old, "select").json()
    with TestClient(create_app(path)) as client:
        assert act(client, old, "select").status_code == 409
        current = client.get(f"/api/v1/runs/{old['session_id']}").json()
        assert current["report"] == selected["report"] and current["revision"] == 1


def test_failed_write_keeps_memory_and_disk_unchanged(tmp_path, monkeypatch):
    app = create_app(tmp_path / "state.sqlite3")
    with TestClient(app) as client:
        original = create(client)

        def fail(*_args):
            raise StorageError("Injected durable write failure.")

        monkeypatch.setattr(app.state.storage, "update_run", fail)
        response = act(client, original, "select")
        assert response.status_code == 503 and "write failure" in response.text
        after = client.get(f"/api/v1/runs/{original['session_id']}").json()
        assert after["revision"] == 0 and after["report"] == original["report"]
        assert not after["pending"]
        assert len(app.state.storage.revisions(original["session_id"])) == 1


def test_transaction_rolls_back_when_revision_insert_fails_after_current_update(tmp_path):
    path = tmp_path / "state.sqlite3"
    app = create_app(path)
    with TestClient(app) as client:
        original = create(client)
        with sqlite3.connect(path) as connection:
            connection.execute("""
                CREATE TRIGGER reject_new_revision BEFORE INSERT ON run_revisions
                WHEN NEW.revision > 0 BEGIN SELECT RAISE(ABORT, 'injected failure'); END
            """)
        assert act(client, original, "select").status_code == 503
        after = client.get(f"/api/v1/runs/{original['session_id']}").json()
        assert after["report"] == original["report"] and after["revision"] == 0
        assert app.state.storage.run_record(original["session_id"])["revision"] == 0
        assert len(app.state.storage.revisions(original["session_id"])) == 1


@pytest.mark.parametrize("bad", [{"manifest": []}, {"manifest": {"schema_version": "999"}}, 1])
def test_malformed_or_incompatible_import_returns_validation_error(tmp_path, bad):
    with TestClient(create_app(tmp_path / "state.sqlite3")) as client:
        response = client.post("/api/v1/resume", json={"runs": [bad]})
        assert response.status_code == 422
        assert not client.get("/api/v1/runs").json()["items"]


def test_import_rejects_inconsistent_seed_result_even_when_event_ledger_is_intact(tmp_path):
    with TestClient(create_app(tmp_path / "state.sqlite3")) as client:
        run = create(client)
        report = run["report"]
        report["initial_results"][0]["active"] = not report["initial_results"][0]["active"]
        response = client.post("/api/v1/resume", json={"runs": [report]})
        assert response.status_code == 422 and "initial_results" in response.text


@pytest.mark.parametrize("bad_event", [None, 1])
def test_malformed_event_record_is_validation_error_and_saved_row_is_retained(tmp_path, bad_event):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        run = create(client)
        report = run["report"]
        report["events"][0] = bad_event
        response = client.post("/api/v1/resume", json={"runs": [report]})
        assert response.status_code == 422 and "records must be objects" in response.text
    payload, checksum = encode(report)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE runs SET snapshot=?, checksum=?", (payload, checksum))
    with TestClient(create_app(path)) as client:
        result = client.get("/api/v1/runs").json()
        assert not result["items"] and result["recovery_issues"][0]["id"] == run["session_id"]
        assert client.get(f"/api/v1/runs/{run['session_id']}").status_code == 503
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT snapshot FROM runs").fetchone()[0] == payload


def test_two_api_instances_use_durable_compare_and_set(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as first, TestClient(create_app(path)) as second:
        original = create(first)
        assert second.get(f"/api/v1/runs/{original['session_id']}").status_code == 200
        with ThreadPoolExecutor(2) as executor:
            results = list(
                executor.map(lambda c: act(c, original, "select").status_code, [first, second])
            )
        assert sorted(results) == [200, 409]
        current = second.get(f"/api/v1/runs/{original['session_id']}").json()
        assert current["revision"] == 1 and current["report"]["metrics"]["reserved_units"] == 3
        assert len(second.app.state.storage.revisions(original["session_id"])) == 2


def test_sqlite_contains_public_snapshot_only_and_no_pending_outcomes(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        run = act(client, create(client), "select").json()
    with sqlite3.connect(path) as connection:
        raw = connection.execute("SELECT snapshot FROM runs").fetchone()[0]
        report = json.loads(raw)
        assert report == run["report"]
        assert not report["delivered_results"]
        assert "private_truth" not in raw and "y_true" not in raw and "TruthStore" not in raw
        assert all("active" not in request for request in report["requests"])
        pending_ids = {request["compound_id"] for request in report["requests"]}
        assert all(row["compound_id"] not in pending_ids for row in report["initial_results"])
        assert all(
            event["delivered_active"] is None
            for event in report["events"]
            if event["event_type"] != "INITIAL_LABEL"
        )


def test_corrupt_row_is_retained_other_runs_work_and_old_revision_can_recover(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        original = create(client)
        run = act(client, original, "select").json()
        other = create(client)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "UPDATE runs SET snapshot='corrupt' WHERE session_id=?", (run["session_id"],)
        )
    with TestClient(create_app(path)) as client:
        response = client.get("/api/v1/runs").json()
        assert [row["session_id"] for row in response["items"]] == [other["session_id"]]
        assert response["recovery_issues"][0]["id"] == run["session_id"]
        assert client.get(f"/api/v1/runs/{run['session_id']}").status_code == 503
        revisions = client.get(f"/api/v1/runs/{run['session_id']}/revisions").json()["items"]
        assert [row["revision"] for row in revisions] == [1, 0]
        recovered = client.post(
            "/api/v1/recovery/runs",
            json={
                "session_id": run["session_id"],
                "revision": 1,
            },
        )
        assert recovered.status_code == 201
        assert recovered.json()["session_id"] != run["session_id"]
        assert recovered.json()["report"]["events"] == run["report"]["events"]
    with sqlite3.connect(path) as connection:
        assert (
            connection.execute(
                "SELECT snapshot FROM runs WHERE session_id=?", (run["session_id"],)
            ).fetchone()[0]
            == "corrupt"
        )


def test_unreconcilable_snapshot_is_reported_without_overwriting(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        run = create(client)
    corrupt = run["report"]
    corrupt["metrics"]["confirmed_hits"] += 1
    payload, checksum = encode(corrupt)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE runs SET snapshot=?, checksum=?", (payload, checksum))
    with TestClient(create_app(path)) as client:
        assert client.get("/api/v1/runs").json()["recovery_issues"]
        assert client.get(f"/api/v1/runs/{run['session_id']}").status_code == 503


@pytest.mark.parametrize("section", ["initial_results", "data_origin", "feature_sha256"])
def test_recomputed_checksum_does_not_hide_corrupt_scientific_metadata(tmp_path, section):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        run = create(client)
    corrupt = run["report"]
    if section == "initial_results":
        corrupt["initial_results"][0]["active"] = not corrupt["initial_results"][0]["active"]
    elif section == "data_origin":
        corrupt["manifest"]["data_origin"] = "HISTORICAL_PUBLIC_DATA"
    else:
        corrupt["manifest"]["dataset"]["feature_sha256"] = "0" * 64
    payload, checksum = encode(corrupt)
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE runs SET snapshot=?, checksum=?", (payload, checksum))
    with TestClient(create_app(path)) as client:
        saved = client.get("/api/v1/runs").json()
        assert not saved["items"] and saved["recovery_issues"][0]["id"] == run["session_id"]
        assert client.get(f"/api/v1/runs/{run['session_id']}").status_code == 503
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT snapshot FROM runs").fetchone()[0] == payload


@pytest.mark.parametrize("mode", ["future-schema", "not-sqlite", "unrecognized-schema"])
def test_incompatible_database_fails_closed_and_bytes_are_unchanged(tmp_path, mode):
    path = tmp_path / "state.sqlite3"
    if mode == "not-sqlite":
        path.write_bytes(b"Not a SQLite database; preserve this evidence.")
    else:
        with sqlite3.connect(path) as connection:
            if mode == "future-schema":
                connection.execute("PRAGMA user_version=999")
            else:
                connection.execute("CREATE TABLE other_app (id INTEGER)")
    before = hashlib.sha256(path.read_bytes()).hexdigest()
    with TestClient(create_app(path)) as client:
        health = client.get("/api/v1/health").json()
        assert health["status"] == "degraded" and not health["sessions_persistent"]
        assert client.get("/api/v1/meta").json()["storage"]["status"] == "unavailable"
        assert client.get("/api/v1/runs").status_code == 503
        assert client.post("/api/v1/runs", json={"scenario": config()}).status_code == 503
        assert "CURALOOP_STORAGE_PATH" in health["storage_error"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == before


def test_delete_is_durable_and_cascades_revision_history(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        run = create(client)
        assert client.delete(f"/api/v1/runs/{run['session_id']}").status_code == 204
    with TestClient(create_app(path)) as client:
        assert client.get(f"/api/v1/runs/{run['session_id']}").status_code == 404
        assert not client.get("/api/v1/runs").json()["items"]
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT COUNT(*) FROM run_revisions").fetchone()[0] == 0


def wait_job(client, job_id):
    for _ in range(200):
        job = client.get("/api/v1/comparisons/" + job_id).json()
        if job["status"] in ("completed", "failed", "interrupted"):
            return job
        time.sleep(0.1)
    pytest.fail("Comparison did not reach a terminal state.")


def test_completed_independent_comparison_survives_restart_and_exports(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        job_id = client.post(
            "/api/v1/comparisons",
            json={
                "scenario": config(budget_units=3),
                "policies": ["random", "greedy", "uncertainty"],
            },
        ).json()["job_id"]
        done = wait_job(client, job_id)
        assert done["status"] == "completed"
    with TestClient(create_app(path)) as client:
        recovered = client.get("/api/v1/comparisons/" + job_id).json()
        assert recovered == done
        assert client.get("/api/v1/comparisons").json()["items"] == [done]
        assert all(report["metrics"]["spent_units"] == 3 for report in done["reports"])
        assert len({report["manifest"]["run_id"] for report in done["reports"]}) == 3
        assert len(client.get(f"/api/v1/comparisons/{job_id}/export").json()["runs"]) == 3
        assert client.delete("/api/v1/comparisons/" + job_id).status_code == 204
        assert client.get("/api/v1/comparisons/" + job_id).status_code == 404


@pytest.mark.parametrize("previous", ["queued", "running"])
def test_unfinished_jobs_are_interrupted_without_automatic_replay(tmp_path, monkeypatch, previous):
    path = tmp_path / "state.sqlite3"
    store = SnapshotStore(path)
    job = {
        "job_id": "interrupted-job",
        "status": previous,
        "scenario": config(),
        "policies": ["random"],
        "reports": [],
        "error": None,
    }
    store.create_job(job)

    def unexpected(*_args):
        pytest.fail("An interrupted comparison must never be resubmitted automatically.")

    monkeypatch.setattr("api.main.compare", unexpected)
    with TestClient(create_app(path)) as client:
        recovered = client.get("/api/v1/comparisons/interrupted-job").json()
        assert recovered["status"] == "interrupted" and not recovered["reports"]
        assert "not replayed" in recovered["error"]
        assert client.get("/api/v1/comparisons/interrupted-job/export").status_code == 409


def test_corrupt_comparison_retained_and_reported(tmp_path):
    path = tmp_path / "state.sqlite3"
    store = SnapshotStore(path)
    store.create_job({"job_id": "bad", "status": "completed", "reports": []})
    with sqlite3.connect(path) as connection:
        connection.execute("UPDATE comparisons SET snapshot='broken'")
    with TestClient(create_app(path)) as client:
        response = client.get("/api/v1/comparisons").json()
        assert not response["items"] and response["recovery_issues"][0]["id"] == "bad"
        assert client.get("/api/v1/comparisons/bad").status_code == 503


def test_saved_comparison_checks_scientific_metadata_even_with_recomputed_checksum(tmp_path):
    path = tmp_path / "state.sqlite3"
    with TestClient(create_app(path)) as client:
        job_id = client.post(
            "/api/v1/comparisons",
            json={
                "scenario": config(budget_units=0),
                "policies": ["random", "greedy"],
            },
        ).json()["job_id"]
        job = wait_job(client, job_id)
        assert job["status"] == "completed"
    job["reports"][0]["manifest"]["data_origin"] = "HISTORICAL_PUBLIC_DATA"
    SnapshotStore(path).update_job(job, "completed")
    with TestClient(create_app(path)) as client:
        result = client.get("/api/v1/comparisons").json()
        assert not result["items"] and result["recovery_issues"][0]["id"] == job_id
        assert client.get(f"/api/v1/comparisons/{job_id}/export").status_code == 503


def test_storage_path_environment_and_separate_adapter_identity(tmp_path, monkeypatch):
    path = tmp_path / "chosen.sqlite3"
    monkeypatch.setenv("CURALOOP_STORAGE_PATH", str(path))
    with TestClient(create_app()) as client:
        assert client.get("/api/v1/health").json()["sessions_persistent"]
        meta = client.get("/api/v1/meta").json()
        assert len(meta["api_source_sha256"]) == 64
        assert meta["api_source_sha256"] != meta["source_sha256"]
    assert path.exists()
