"""Constructed matrix and real file-boundary replay, no biological data."""

import copy
import hashlib
import json

import numpy as np
import pytest

from research.lr_d23_v1.matrix import batches, evaluation, training
from research.lr_d23_v1.worker import campaign
from research.m2_costed_v2 import engine


def sources():
    return {"T" + str(i): dict(sha256="constructed", component="g" + str(g), rows=128)
            for i, g in enumerate((0, 1, 1, 2, 3, 3))}


def test_training_fold_rounds_and_paired_cpu_are_exact():
    meta = sources()
    for round_index in (0, 1):
        matrix = training(meta, [69, 70, 71], round_index)
        prefixes = {u["name"]: u for u in matrix["units"] if u["stage"] == "training_prefixes"}
        assert len(prefixes) == 108 and len(matrix["units"]) == 756
        for unit in matrix["units"]:
            assert meta[unit["task_id"]]["component"] != unit["heldout"]
            if round_index:
                assert unit["gate_key"] == unit["heldout"] + ":v0"
            if unit["stage"] == "paired_branches":
                assert unit["cpu"] == prefixes[unit["prefix"]]["cpu"]


def test_chunks_do_not_split_counterfactuals_or_comparators():
    for matrix, stage in ((training(sources(), [69, 70, 71], 0), "paired_branches"),
                          (evaluation(sources(), [69, 70, 71]), "D2_primary")):
        chunks = batches(matrix, [69, 70, 71], stage)
        assert all(len(units) <= 24 for cpu, units in chunks)
        index = {u["name"]: i for i, (_, units) in enumerate(chunks) for u in units}
        keys = {}
        for unit in matrix["units"]:
            if unit["stage"] != stage:
                continue
            key = unit["prefix"] if stage == "paired_branches" else (unit["task_id"], unit["n0"], unit["seed"])
            keys.setdefault(key, set()).add(index[unit["name"]])
        assert all(len(v) == 1 for v in keys.values())


def test_attribution_matches_primary_core_and_never_changes_arms():
    main = evaluation(sources(), [69, 70, 71])
    attr = evaluation(sources(), [69, 70, 71], attribution=True)
    assert len(main["units"]) == 420 and len(attr["units"]) == 120
    cores = {(u["task_id"], u["n0"], u["seed"]): u["cpu"] for u in main["units"]}
    assert all(u["cpu"] == cores[u["task_id"], u["n0"], u["seed"]] for u in attr["units"])
    assert all(u["heldout"] == sources()[u["task_id"]]["component"] for u in main["units"])


def test_no_third_round_or_unplanned_transfer_cell():
    with pytest.raises(AssertionError):
        training(sources(), [69], 2)
    with pytest.raises(AssertionError):
        evaluation(sources(), [69], budget=64)
    with pytest.raises(AssertionError):
        evaluation(sources(), [69], budget=16, attribution=True)


def test_real_prefix_files_restore_a_matched_pair(tmp_path, monkeypatch):
    # Only Windows signal plumbing is replaced. No runtime/timing claim follows.
    monkeypatch.setattr(engine.signal, "SIGPROF", 27, raising=False)
    monkeypatch.setattr(engine.signal, "getsignal", lambda signum: None)
    monkeypatch.setattr(engine.signal, "signal", lambda *args: None)
    monkeypatch.setattr(engine.Clock, "arm", lambda self: None)
    monkeypatch.setattr(engine.Clock, "disarm", lambda *args: None)
    task = "SYNTHETIC-64"
    data = {"task_id": task, "component": "g1", "role": "development",
            "records": [{"candidate_id": "synthetic-" + str(i), "active": bool(i % 3 == 0),
                         "morgan_on_bits": [i, i + 64]} for i in range(64)]}
    (tmp_path / "inputs").mkdir()
    source = tmp_path / "inputs" / (task + ".json")
    source.write_text(json.dumps(data), encoding="utf-8")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    meta = {task: dict(sha256=digest, component="g1")}
    caps = {"rf:16:32": {"C_ref": 5., "cost_priors": dict(REUSE=.00001, UPDATE=.00001, PLAN=.1)}}
    spec = dict(name="constructed-prefix", stage="training_prefixes", task_id=task,
                input_sha256=digest, heldout="g0", training_components=["g1", "g2", "g3"],
                predictor="rf", budget=32, n0=16, seed=41, round=0, control="Gk2")
    result, snapshots, state = campaign(tmp_path, spec, {}, caps, meta)
    assert result["new_deliveries"] == 32 and set(snapshots) >= {8, 16, 24}
    prefix = tmp_path / "units/constructed-prefix/a0"
    prefix.mkdir(parents=True)
    (prefix / "snapshots.json").write_text(json.dumps(snapshots), encoding="utf-8")
    np.savez_compressed(prefix / "public-cache.npz", x=state.pool.x, similarity=state.similarity, neighbors=state.neighbors)
    result.update(status="PASS", snapshot_sha256=hashlib.sha256((prefix / "snapshots.json").read_bytes()).hexdigest(),
                  cache_sha256=hashlib.sha256((prefix / "public-cache.npz").read_bytes()).hexdigest())
    (prefix / "result.json").write_text(json.dumps(result), encoding="utf-8")
    pin = hashlib.sha256((prefix / "result.json").read_bytes()).hexdigest()
    outcomes = []
    for operation in ("UPDATE", "REUSE"):
        branch = dict(spec, name="constructed-branch-" + operation, stage="paired_branches",
                      prefix="constructed-prefix", snapshot=8, forced=operation)
        outcome, _, restored = campaign(tmp_path, branch, {}, caps, meta,
                                         {"constructed-prefix": "units/constructed-prefix/a0"},
                                         {"constructed-prefix": pin})
        assert outcome["branch_eligible"] and outcome["new_deliveries"] == 32
        assert restored.trace[8]["actual_operation"] == operation
        outcomes.append(outcome)
    assert outcomes[0]["features"] == outcomes[1]["features"]
    assert len(state.observed) == 48
    wrong = copy.deepcopy(branch)
    wrong["seed"] = 99
    with pytest.raises(AssertionError, match="PREFIX_CONTEXT_MISMATCH"):
        campaign(tmp_path, wrong, {}, caps, meta, {"constructed-prefix": "units/constructed-prefix/a0"},
                 {"constructed-prefix": pin})
