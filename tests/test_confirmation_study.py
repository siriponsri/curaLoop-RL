"""Real public-source arithmetic, fail-closed boundaries and read-only integration."""

import hashlib
import json
import shutil
from itertools import product
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from curaloop_rd import confirmation_study as study
from curaloop_rd.confirmation_workspace_v3 import ConfirmationWorkspace


def test_all_2700_cells_and_35_views_match_the_recorded_macro_statistics():
    _, summary, cells = study.load_study()
    assert len(cells) == 2700
    expected = {(r["budget_percent"], r["ranker"], r["operator"]): r for r in summary["equal_campaign_summary"]}
    for campaign, budget in product(("equal", *study.CAMPAIGNS), study.BUDGETS):
        payload = study.view(campaign, budget)
        assert len(payload["arms"]) == 18
        for arm in payload["arms"]:
            for metric in study.METRICS:
                if campaign == "equal" and metric != "confirmation_count":
                    original = expected[budget, arm["ranker"], arm["operator"]]
                    for stat in ("mean", "sd", "min", "max"):
                        assert arm["metrics"][metric][stat] == pytest.approx(original[metric + "_" + stat], abs=1e-10)
            if arm["operator"] == "cluster_round_robin":
                assert arm["metrics"]["positive_structure_groups"] == arm["metrics"]["confirmed_positives"]
    # These source sums are assay observations, not a selected arm's discoveries.
    assert payload["universe_observations"] == 6896
    assert payload["primary_observations"] == 1333191


@pytest.mark.parametrize("key", tuple(study.INPUTS))
def test_fixed_source_hash_rejects_tamper_missing_and_extra_fields(tmp_path, key):
    relative = study.INPUTS[key][0]
    for row in study.INPUTS.values():
        path = tmp_path / row[0]
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(study.ROOT / row[0], path)
    assert study.view(root=tmp_path)["study_id"] == "cf1"
    target = tmp_path / relative
    original = target.read_bytes()
    target.write_bytes(original.replace(b"2700", b"2701", 1) if b"2700" in original else original + b" ")
    with pytest.raises(study.StudyUnavailable):
        study.view(root=tmp_path)
    if target.suffix == ".json":
        data = json.loads(original)
        data["pending_assay_results"] = [1]
        target.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(study.StudyUnavailable):
            study.view(root=tmp_path)
    target.unlink()
    with pytest.raises(study.StudyUnavailable):
        study.view(root=tmp_path)


@pytest.mark.parametrize("arguments", [
    {"campaign": "../private"}, {"budget_percent": 3}, {"budget_percent": True},
    {"ranker": "rl"}, {"operator": "new_selector"}, {"locale": "xx"},
])
def test_brief_rejects_unsupported_selection(arguments):
    with pytest.raises(ValueError):
        study.comparison_brief(**arguments)


def test_c_workspace_bilingual_exports_roundtrip_and_coordinated_tamper(tmp_path):
    workspace = ConfirmationWorkspace(tmp_path)
    selection = {"campaign": "628/677", "budget_percent": 5, "ranker": "rf", "operator": "cluster_round_robin"}
    result = workspace.call("confirmation_export", selection)
    folder = __import__("pathlib").Path(result["local_folder"])
    assert result == workspace.call("confirmation_export", {**selection, "locale": "th"})
    assert result["external_delivery"] is False
    for locale in ("en", "th"):
        brief = json.loads((folder / f"brief-{locale}.json").read_text(encoding="utf-8"))
        assert brief["selection"] == selection
        assert brief == workspace.call("confirmation_inspect", {**selection, "locale": locale})
        assert f'lang="{locale}"' in (folder / f"brief-{locale}.html").read_text(encoding="utf-8")
    # Editing the report and its adjacent manifest together cannot reauthenticate it.
    html = folder / "brief-en.html"
    html.write_text(html.read_text(encoding="utf-8").replace("MVS-A", "FAKE"), encoding="utf-8")
    manifest_path = folder / "manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["files"][0]["sha256"] = hashlib.sha256(html.read_bytes()).hexdigest()
    manifest["files"][0]["bytes"] = html.stat().st_size
    manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="altered"):
        workspace.call("confirmation_export", selection)
    with pytest.raises(ValueError, match="Unexpected"):
        workspace.call("confirmation_export", {"path": "../other"})


def test_c_workspace_rejects_extra_inventory(tmp_path):
    workspace = ConfirmationWorkspace(tmp_path)
    result = workspace.call("confirmation_export", {})
    (__import__("pathlib").Path(result["local_folder"]) / "extra.txt").write_text("unexpected")
    with pytest.raises(ValueError, match="inventory"):
        workspace.call("confirmation_export", {})


def test_interrupted_export_retains_staging_and_next_call_can_finish(tmp_path, monkeypatch):
    workspace = ConfirmationWorkspace(tmp_path)
    original = Path.open
    def fail_once(path, mode="r", *args, **kwargs):
        if path.name == "brief-en.json" and mode == "xb":
            raise OSError("Injected local write interruption")
        return original(path, mode, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", fail_once)
        with pytest.raises(OSError, match="Injected"):
            workspace.call("confirmation_export", {})
    assert list((tmp_path / "confirmation-v3").glob(".confirmation-staging-*"))
    result = workspace.call("confirmation_export", {})
    assert len(list(Path(result["local_folder"]).iterdir())) == 5


def test_api_study_without_campaign_and_preserves_existing_pending_run(tmp_path):
    app = create_app(tmp_path / "qa.sqlite3")
    with TestClient(app) as client:
        assert client.get("/api/v1/runs").json()["items"] == []
        for campaign, budget, locale in product(("equal", *study.CAMPAIGNS), study.BUDGETS, ("en", "th")):
            response = client.get("/api/v1/studies/cf1", params={"campaign": campaign, "budget_percent": budget})
            assert response.status_code == 200
            data = response.json()
            exported = client.get("/api/v1/studies/cf1/export", params={"campaign": campaign, "budget_percent": budget, "locale": locale})
            assert exported.status_code == 200 and exported.json()["evidence"] == data
            assert exported.json()["locale"] == locale
            assert "attachment" in exported.headers["content-disposition"]
        assert client.get("/api/v1/runs").json()["items"] == []
        config = {"dataset": "synthetic_linear_v1", "candidate_count": 24, "initial_count": 6,
                  "budget_units": 6, "batch_size": 3, "delay_steps": 2, "seed": 42}
        run = client.post("/api/v1/runs", json={"scenario": config, "policy": "greedy"}).json()
        url = "/api/v1/runs/" + run["session_id"]
        run = client.post(url + "/select", json={"expected_revision": run["revision"]}).json()
        before = client.get(url).json()
        assert before["pending"]
        client.get("/api/v1/studies/cf1")
        client.get("/api/v1/studies/cf1/export")
        assert client.get(url).json() == before
        assert all(row["revealed_active"] is None for row in client.get(url + "/candidates?status=pending").json()["items"])
        for query in ("path=../private", "campaign=equal&campaign=628/677", "ranker=rl", "budget_percent=3"):
            assert client.get("/api/v1/studies/cf1?" + query).status_code == 422


def test_api_unavailable_does_not_return_fake_zero_metrics(tmp_path, monkeypatch):
    def unavailable(*args, **kwargs):
        raise study.StudyUnavailable("Source verification failed")
    monkeypatch.setattr("api.main.confirmation_view", unavailable)
    app = create_app(tmp_path / "qa.sqlite3")
    with TestClient(app) as client:
        response = client.get("/api/v1/studies/cf1")
        assert response.status_code == 503 and response.json() == {"detail": "Source verification failed"}
