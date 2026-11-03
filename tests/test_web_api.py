import csv
import io
import json
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from curaloop.domain import Scenario
from curaloop.service import RunService


@pytest.fixture
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client
    app.state.executor.shutdown(wait=True)


def config(**kwargs):
    return {
        "dataset": "synthetic_linear_v1",
        "seed": 42,
        "candidate_count": 24,
        "initial_count": 6,
        "budget_units": 6,
        "batch_size": 3,
        "delay_steps": 2,
        **kwargs,
    }


def create(client, **kwargs):
    r = client.post("/api/v1/runs", json={"scenario": config(**kwargs), "policy": "greedy"})
    assert r.status_code == 201, r.text
    return r.json()


def action(client, run, name, **kwargs):
    return client.post(
        f"/api/v1/runs/{run['session_id']}/{name}",
        json={"expected_revision": run["revision"], **kwargs},
    )


def test_health_meta_datasets_and_policies(client):
    assert client.get("/api/v1/health").json()["status"] == "ok"
    assert client.get("/api/v1/meta").json()["digital_twin_maturity"] == "RETROSPECTIVE_SIMULATOR"
    assert len(client.get("/api/v1/datasets").json()) == 3
    policies = client.get("/api/v1/policies").json()
    assert len(policies) == 5 and policies[-1]["training_episodes"] == 160


def test_historical_provenance_regression(client):
    r = client.post(
        "/api/v1/runs",
        json={
            "scenario": {
                "dataset": "hiv_moleculenet_replay_v1",
                "candidate_count": 24,
                "initial_count": 6,
                "budget_units": 0,
            }
        },
    )
    assert r.status_code == 201
    m = r.json()["report"]["manifest"]
    assert m["data_origin"] == "HISTORICAL_PUBLIC_DATA"
    assert m["dataset"]["source"] == m["dataset_provenance"]["source_url"]
    assert "no external data" not in m["dataset"]["source"]
    assert len(m["dataset"]["sha256"]) == 64
    assert "synthetic fixture" not in r.json()["report"]["events"][0]["explanation"]


def test_legacy_start_description_is_restored_without_changing_scientific_events(client):
    from copy import deepcopy

    run = create(client, budget_units=0)
    legacy = deepcopy(run["report"])
    legacy["events"][0]["explanation"] = "Original synthetic fixture; no live laboratory."
    r = client.post("/api/v1/resume", json={"runs": [legacy]})
    assert r.status_code == 201
    restored = r.json()["report"]
    assert restored["events"] == legacy["events"]
    assert restored["metrics"] == legacy["metrics"]
    assert any("Legacy RUN_STARTED" in note for note in restored["manifest"]["limitations"])


def test_request_pending_delivered_budget_and_event_contract(client):
    run = create(client)
    r = action(client, run, "select")
    assert r.status_code == 200
    run = r.json()
    assert (
        run["report"]["metrics"]["reserved_units"] == 3
        and run["report"]["metrics"]["spent_units"] == 0
    )
    assert not run["report"]["delivered_results"]
    run = action(client, run, "advance").json()
    assert not run["report"]["delivered_results"]
    run = action(client, run, "advance").json()
    assert len(run["report"]["delivered_results"]) == 3
    assert run["report"]["metrics"]["spent_units"] == 3


def test_stale_duplicate_action_and_full_queue_rejected_without_charge(client):
    original = create(client)
    current = action(client, original, "select").json()
    assert action(client, original, "select").status_code == 409
    assert action(client, current, "select").status_code == 409
    after = client.get(f"/api/v1/runs/{original['session_id']}").json()
    assert (
        after["report"]["metrics"]["reserved_units"] == 3 and len(after["report"]["requests"]) == 3
    )


def test_concurrent_clicks_never_double_charge(client):
    run = create(client)
    with ThreadPoolExecutor(2) as executor:
        results = list(executor.map(lambda _: action(client, run, "select").status_code, range(2)))
    assert sorted(results) == [200, 409]
    assert (
        client.get(f"/api/v1/runs/{run['session_id']}").json()["report"]["metrics"][
            "reserved_units"
        ]
        == 3
    )


def test_same_deterministic_run_ids_have_isolated_http_sessions(client):
    a, b = create(client), create(client)
    assert a["session_id"] != b["session_id"]
    assert a["report"]["manifest"]["run_id"] == b["report"]["manifest"]["run_id"]
    action(client, a, "select")
    other = client.get(f"/api/v1/runs/{b['session_id']}").json()
    assert not other["report"]["requests"] and other["revision"] == 0


def test_api_and_existing_engine_match_exact_records(client):
    run = create(client)
    done = action(client, run, "finish").json()
    reference = RunService(Scenario(**config()), "greedy")
    reference.finish()
    report = reference.report()
    for key in ("events", "metrics", "curve", "requests", "delivered_results", "initial_results"):
        assert done["report"][key] == report[key]


def test_public_candidate_search_filter_sort_pagination_hides_labels(client):
    run = create(client)
    base = f"/api/v1/runs/{run['session_id']}/candidates"
    result = client.get(base, params={"status": "eligible", "page_size": 3}).json()
    assert result["total"] == 18 and len(result["items"]) == 3
    assert all(
        c["revealed_active"] is None and c["predicted_probability"] is None for c in result["items"]
    )
    identifier = result["items"][0]["compound_id"]
    assert client.get(base, params={"search": identifier}).json()["total"] == 1
    assert client.get(base, params={"page_size": 3, "page": 2}).json()["items"] != result["items"]
    assert client.get(base, params={"sort": "feature_count", "descending": True}).status_code == 200


def test_candidate_labels_stay_hidden_while_pending(client):
    run = create(client)
    run = action(client, run, "select").json()
    r = client.get(
        f"/api/v1/runs/{run['session_id']}/candidates", params={"status": "pending"}
    ).json()
    assert len(r["items"]) == 3 and all(c["revealed_active"] is None for c in r["items"])
    payload = json.dumps(run)
    assert "private_truth" not in payload and "y_true" not in payload
    assert all(
        e["delivered_active"] is None
        for e in run["report"]["events"]
        if e["event_type"] != "INITIAL_LABEL"
    )


def test_json_csv_exports_and_pending_resume(client):
    run = action(client, create(client), "select").json()
    url = f"/api/v1/runs/{run['session_id']}/export"
    payload = client.get(url, params={"format": "json"}).json()
    rows = list(
        csv.DictReader(
            io.StringIO(client.get(url, params={"format": "csv"}).content.decode("utf-8-sig"))
        )
    )
    assert len(rows) == len(payload["runs"][0]["events"])
    assert json.loads(rows[0]["manifest_json"]) == payload["runs"][0]["manifest"]
    resumed = client.post("/api/v1/resume", json=payload)
    assert resumed.status_code == 201
    assert resumed.json()["report"]["events"] == run["report"]["events"]
    assert len(resumed.json()["pending"]) == 3


def test_replay_reset_and_delete(client):
    run = action(client, create(client), "finish").json()
    replay = action(client, run, "replay").json()
    assert replay["report"]["events"] == run["report"]["events"]
    reset = action(client, replay, "reset").json()
    assert not reset["report"]["requests"] and reset["revision"] == 3
    assert client.delete(f"/api/v1/runs/{reset['session_id']}").status_code == 204
    assert client.get(f"/api/v1/runs/{reset['session_id']}").status_code == 404


def test_comparisons_are_real_matched_and_exportable(client):
    r = client.post(
        "/api/v1/comparisons",
        json={"scenario": config(budget_units=3), "policies": ["random", "greedy", "uncertainty"]},
    )
    assert r.status_code == 202
    job_id = r.json()["job_id"]
    for _ in range(150):
        job = client.get("/api/v1/comparisons/" + job_id).json()
        if job["status"] in ("completed", "failed"):
            break
        time.sleep(0.1)
    assert job["status"] == "completed", job
    assert len(job["reports"]) == 3
    assert all(r["metrics"]["spent_units"] == 3 for r in job["reports"])
    assert all(
        r["manifest"]["initial_label_ids"] == job["reports"][0]["manifest"]["initial_label_ids"]
        for r in job["reports"]
    )
    assert len(client.get(f"/api/v1/comparisons/{job_id}/export").json()["runs"]) == 3


@pytest.mark.parametrize(
    "updates",
    [
        {"budget_units": -1},
        {"seed": True},
        {"initial_count": 25},
        {"dataset": "unknown"},
        {"extra_truth": [1, 0]},
    ],
)
def test_invalid_scenarios_fail_clearly(client, updates):
    assert client.post("/api/v1/runs", json={"scenario": config(**updates)}).status_code == 422


def test_origin_cors_and_host_are_local_only(client):
    assert (
        client.get("/api/v1/health", headers={"Origin": "https://evil.example"}).status_code == 403
    )
    assert client.get("/api/v1/health", headers={"Host": "evil.example"}).status_code == 403
    r = client.get("/api/v1/health", headers={"Origin": "http://localhost:5173"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert r.headers["x-content-type-options"] == "nosniff"


def test_zero_budget_errors_and_corrupted_import(client):
    run = create(client, budget_units=0)
    assert run["done"] and action(client, run, "select").status_code == 409
    assert action(client, run, "advance").status_code == 409
    assert client.post("/api/v1/resume", json={"runs": [{"manifest": {}}]}).status_code == 422
    assert client.get(f"/api/v1/runs/{run['session_id']}/export?format=pickle").status_code == 422


def test_evidence_is_explicitly_recorded_not_new_or_superior(client):
    data = client.get("/api/v1/evidence").json()
    assert data["recorded_release"] == "v0.1"
    assert data["predictor"]["scaffold_overlap"] == 0
    assert "300 / 300" in data["controller_historical_fallback"]
    assert len(data["controllers"][0]["episode_returns"]) == 160


def test_no_molecule_placeholder_for_synthetic_descriptor(client):
    run = create(client)
    assert client.get(f"/api/v1/runs/{run['session_id']}/molecules/CMP-0001.svg").status_code == 404


def test_production_frontend_deep_links_font_and_build_identity(client):
    import re

    root = client.get("/")
    assert root.status_code == 200 and '<div id="root"></div>' in root.text
    assert client.get("/lab").text == root.text
    asset = re.search(r'src="(/assets/[^" ]+\.js)"', root.text).group(1)
    assert client.get(asset).status_code == 200
    font = client.get("/fonts/NotoSansThai.ttf")
    assert font.status_code == 200 and len(font.content) > 10000
    assert client.get("/api/v1/not-an-endpoint").status_code == 404
    assert len(client.get("/api/v1/meta").json()["frontend_build_sha256"]) == 64


def test_historical_molecule_svg_uses_public_structure_without_label(client):
    run = create(
        client, dataset="hiv_moleculenet_replay_v1", candidate_count=1200, initial_count=48
    )
    base = f"/api/v1/runs/{run['session_id']}"
    candidate = client.get(base + "/candidates?status=eligible&page_size=1").json()["items"][0]
    assert candidate["revealed_active"] is None and candidate["canonical_smiles"]
    svg = client.get(base + f"/molecules/{candidate['compound_id']}.svg")
    assert svg.status_code == 200 and svg.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in svg.text and "bond-" in svg.text
    assert client.get(base + "/molecules/not-a-compound.svg").status_code == 404
