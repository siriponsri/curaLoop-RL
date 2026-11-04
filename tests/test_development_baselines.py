import json
import warnings
from dataclasses import replace

import numpy as np
import pytest

from research.development.baselines import METHODS, Selector
from research.development.prepare_cohort import normalize_rows, select_pool
from research.development.runner import peak_working_set_bytes, run_one
from research.event_time import Candidate, Observation, Result


def observation(initial=(Result("s0", False, 0), Result("s1", True, 0)), pending=()):
    candidates = tuple(
        Candidate(cid, features)
        for cid, features in (
            ("s0", (0.0, 0.0)),
            ("s1", (1.0, 1.0)),
            ("near", (1.0, 0.0)),
            ("far", (0.0, 1.0)),
            ("pending", (1.0, 0.0)),
        )
    )
    return Observation(
        1,
        5,
        4,
        candidates,
        ("far", "near"),
        pending,
        initial,
        (),
        (),
        tuple((c.candidate_id, 1) for c in candidates),
        1,
        3,
    )


def test_conflicting_canonical_labels_are_excluded_whole_and_duplicates_collapsed():
    clean, excluded, stats = normalize_rows(
        [
            "CCO\tid1\t1",
            "OCC\tid2\t0",
            "CO\tid3\t0",
            "OC\tid4\t0",
            "not-smiles\tid5\t1",
            "CCC\tid6\t",
        ]
    )
    assert len(clean) == 1 and clean[0]["source_ids"] == ["id3", "id4"]
    assert stats["canonical_conflict_groups"] == 1
    assert {x["reason"] for x in excluded} == {
        "CONFLICTING_CANONICAL_LABEL",
        "CONSISTENT_CANONICAL_DUPLICATE",
        "INVALID_SMILES",
        "MISSING_LABEL_NOT_INACTIVE",
    }
    assert len(clean) + len(excluded) == 6


def test_unknown_activity_and_duplicate_source_ids_fail_closed():
    for lines in (["CC\tid\t2"], ["CC\tid\t0", "CO\tid\t1"]):
        with pytest.raises(ValueError):
            normalize_rows(lines)


def test_pool_membership_is_label_blind():
    records = [{"canonical_smiles": str(i), "active": bool(i % 2)} for i in range(20)]
    flipped = [{**r, "active": not r["active"]} for r in records]
    assert [r["canonical_smiles"] for r in select_pool(records, "ahr", 8)] == [
        r["canonical_smiles"] for r in select_pool(flipped, "ahr", 8)
    ]


def test_frozen_model_keeps_initial_one_class_fallback_after_new_active():
    first = observation(initial=(Result("s0", False, 0),))
    frozen = Selector("frozen_greedy", 0)
    frozen.choose(first)
    frozen.choose(replace(first, delivered_results=(Result("s1", True, 1),)))
    assert frozen.stats["fit_attempts"] == 1 and frozen.stats["fit_successes"] == 0
    assert frozen.stats["fallback_requests"] == 2
    retrained = Selector("greedy", 0)
    retrained.choose(first)
    retrained.choose(replace(first, delivered_results=(Result("s1", True, 1),)))
    assert retrained.stats["fit_attempts"] == 2 and retrained.stats["fit_successes"] == 1


def test_predictor_does_not_refit_without_new_delivered_labels():
    selector = Selector("greedy", 42)
    obs = observation()
    selector.choose(obs)
    selector.choose(replace(obs, time=2, pending_ids=("pending",)))
    assert selector.stats["fit_successes"] == 1 and selector.stats["prediction_calls"] == 2


def test_pending_treatment_changes_ranking_but_not_duplicate_exclusion():
    class FixedPublicScores:
        def predict_proba(self, x):
            p = np.asarray([0.9 if row[0] else 0.8 for row in x])
            return np.stack([1 - p, p], axis=1)

    obs = observation(pending=("pending",))
    selectors = [Selector(m, 0, 0.2) for m in ("greedy", "pending_penalty")]
    for selector in selectors:
        selector.initialized = True
        selector.signature = tuple((r.candidate_id, r.active) for r in obs.initial_results)
        selector.model = FixedPublicScores()
    blind, aware = [s.choose(obs)[0] for s in selectors]
    assert blind == ("near",) and aware == ("far",)
    assert "pending" not in blind + aware


@pytest.mark.parametrize("method", METHODS)
def test_public_row_order_cannot_change_selection(method):
    obs = observation()
    shuffled = replace(
        obs,
        candidates=tuple(reversed(obs.candidates)),
        eligible_ids=tuple(reversed(obs.eligible_ids)),
        initial_results=tuple(reversed(obs.initial_results)),
    )
    assert Selector(method, 3).choose(obs)[0] == Selector(method, 3).choose(shuffled)[0]


def test_no_active_similarity_fallback_is_reported():
    selector = Selector("nearest_hit", 0)
    selector.choose(observation(initial=(Result("s0", False, 0),)))
    assert selector.report()["fallback_reasons"] == {"NO_DELIVERED_ACTIVE": 1}


def test_real_runner_common_delay_is_an_exact_pending_pair_negative_control():
    records = [
        {
            "candidate_id": f"c{i:02d}",
            "active": bool(i % 3 == 0),
            "morgan_on_bits": [i % 6, (i + 1) % 6],
            "scaffold": f"s{i % 3}",
        }
        for i in range(18)
    ]
    cohort = {"records": records, "task_id": "constructed-endpoint-v1"}
    cfg = {
        "initial_count": 6,
        "budget": 8,
        "capacity": 2,
        "deadline": 8,
        "conditions": {"common": [2]},
        "pending_lambda": 0.2,
    }
    a, b = (run_one(cohort, cfg, 2, "common", m) for m in ("greedy", "pending_penalty"))
    assert a["snapshot"]["events"] == b["snapshot"]["events"]
    assert a["metrics"] == b["metrics"]
    assert a["initial_ids"] == b["initial_ids"] and a["schedule_sha256"] == b["schedule_sha256"]


def test_own_memory_observer_is_bounded_metadata_only():
    value = peak_working_set_bytes()
    assert value is None or value > 0


@pytest.fixture
def ledger_study(tmp_path, monkeypatch):
    from research.development import runner

    cfg = {
        "status": "FROZEN_DEVELOPMENT_ONLY",
        "final_evaluation": False,
        "execution_source_sha256": runner.execution_identity(),
        "schema_version": "curaloop.ncats-development-run.v1",
        "predictor": {
            "family": "StandardScaler->LogisticRegression",
            "solver": "liblinear",
            "C": 1.0,
            "max_iter": 500,
        },
        "assays": ["ahr", "pparg", "p53"],
        "methods": ["random"],
        "seeds": [0],
        "threads": 1,
        "concurrency": 1,
        "unit_cost": 1,
        "expected_runs": 3,
        "sample_size_per_assay": 1,
        "cohort_sha256": {a: "test" for a in ("ahr", "pparg", "p53")},
        "conditions": {"heterogeneous": [1, 2, 4]},
        "max_cumulative_run_wall_seconds": 300,
    }
    config = tmp_path / "config.json"
    config.write_text(json.dumps(cfg))
    monkeypatch.setattr(runner, "load_cohort", lambda *args: {"records": [{}]})
    return runner, config, tmp_path / "runs"


def test_completed_artifacts_are_skipped_and_corruption_is_not_rerun(ledger_study, monkeypatch):
    runner, cfg, folder = ledger_study
    calls = []

    def run(*args):
        calls.append(args)
        return {"status": "COMPLETE", "metrics": {"new_hits": 0}}

    monkeypatch.setattr(runner, "run_one", run)
    first = runner.execute(cfg, folder, "all")
    second = runner.execute(cfg, folder, "all")
    assert len(calls) == 3 and first == second
    run_id = next(iter(first["attempts"]))
    (folder / (run_id + ".json")).write_text("changed")
    with pytest.raises(ValueError, match="artifact changed"):
        runner.execute(cfg, folder, "all")
    assert len(calls) == 3


def test_failed_runs_preserve_warning_resources_and_denominator(ledger_study, monkeypatch):
    runner, cfg, folder = ledger_study

    def fail(*args):
        warnings.warn("preserved warning", UserWarning)
        raise RuntimeError("constructed failure")

    monkeypatch.setattr(runner, "run_one", fail)
    ledger = runner.execute(cfg, folder, "all")
    assert len(ledger["attempts"]) == 3
    for run_id, entry in ledger["attempts"].items():
        data = json.loads((folder / (run_id + ".json")).read_text())
        assert entry["status"] == "FAILED" and data["warnings"] == ["preserved warning"]
        assert data["attempt_wall_seconds"] > 0 and "constructed failure" in data["traceback"]
    monkeypatch.setattr(runner, "run_one", lambda *args: pytest.fail("must not rerun failure"))
    assert runner.execute(cfg, folder, "all") == ledger


def test_interruption_or_missing_ledger_cannot_reset_denominators(ledger_study):
    runner, cfg, folder = ledger_study
    folder.mkdir()
    (folder / "unexplained.json").write_text("{}")
    with pytest.raises(ValueError, match="without their ledger"):
        runner.execute(cfg, folder, "all")
    runner.write(
        folder / "ledger.json",
        {
            "config_sha256": runner.digest(json.loads(cfg.read_text())),
            "attempts": {"uncertain": {"status": "RUNNING"}},
        },
    )
    with pytest.raises(ValueError, match="Interrupted/uncertain"):
        runner.execute(cfg, folder, "all")


def test_concurrent_study_writer_is_rejected(tmp_path):
    from research.development.runner import study_lock

    with study_lock(tmp_path):
        with pytest.raises(OSError):
            with study_lock(tmp_path):
                pytest.fail("second writer acquired the same lock")
