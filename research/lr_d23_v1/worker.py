"""One authenticated LR-D23 batch, bounded by cgroup and whole-process guards."""

import hashlib
import json
import signal
import sys
import time
from pathlib import Path

from research.m2_costed_v2.guard import CostedGuard, new


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def campaign(root, spec, artifacts, caps, sources, unit_paths=None, unit_pins=None):
    import numpy as np

    from research.lr_d23_v1.policy import ResidualState, selector
    from research.m2_costed_v2.engine import Clock, Oracle, PublicPool
    from research.m2_costed_v2.worker import seed_for
    from research.m2_v1.models import dense_bits

    source = root / "inputs" / (spec["task_id"] + ".json")
    assert spec["task_id"] in sources and sha(source) == sources[spec["task_id"]]["sha256"]
    assert spec["input_sha256"] == sources[spec["task_id"]]["sha256"]
    data = read(source)
    assert data["role"] == "development" and data["task_id"] == spec["task_id"]
    assert data["component"] == sources[spec["task_id"]]["component"]
    kind, n0, budget = spec["predictor"], spec["n0"], spec["budget"]
    if spec["stage"] in ("training_prefixes", "paired_branches"):
        assert (kind, budget, spec.get("cpu_multiplier", 1.)) == ("rf", 32, 1.)
        assert data["component"] != spec["heldout"] and data["component"] in spec["training_components"]
    else:
        assert data["component"] == spec["heldout"]
    cap_data = caps[f"{kind}:{n0}:{budget}"]
    cap = cap_data["C_ref"] * spec.get("cpu_multiplier", 1.)
    artifact = artifacts.get(spec.get("gate_key"))
    if artifact:
        assert artifact["heldout_component"] == spec["heldout"]
        assert spec["heldout"] not in artifact["training_components"]
        if spec["stage"] in ("training_prefixes", "paired_branches"):
            assert data["component"] in artifact["allowed_components"]
        else:
            assert data["component"] == spec["heldout"]
    rows = data["records"]
    clock = Clock(cap)
    if spec["stage"] == "paired_branches":
        prefix = root / (unit_paths or {}).get(spec["prefix"], "units/" + spec["prefix"] + "/a0")
        assert sha(prefix / "result.json") == unit_pins[spec["prefix"]]
        prefix_result = read(prefix / "result.json")
        assert prefix_result["status"] == "PASS"
        assert sha(prefix / "snapshots.json") == prefix_result["snapshot_sha256"]
        assert sha(prefix / "public-cache.npz") == prefix_result["cache_sha256"]
        for key in ("task_id", "heldout", "n0", "seed", "budget", "predictor", "round"):
            assert prefix_result["spec"][key] == spec[key], "PREFIX_CONTEXT_MISMATCH"
        snapshot = read(prefix / "snapshots.json")[str(spec["snapshot"])]
        with np.load(prefix / "public-cache.npz", allow_pickle=False) as cache:
            x, similarity, neighbors = cache["x"], cache["similarity"], cache["neighbors"]
        pool = PublicPool(data["task_id"], data["component"], tuple(r["candidate_id"] for r in rows), x)
        clock = Clock(cap, snapshot["prefix_cpu_seconds"])
        state = ResidualState.restore_residual(
            pool, kind, seed_for(data["task_id"], spec["seed"]), n0, budget,
            snapshot, similarity, neighbors, control=spec["control"], gate_artifact=artifact,
        )
        class FrozenClock:
            def remaining(self):
                return max(0., cap - snapshot["prefix_cpu_seconds"])
        fixed = FrozenClock()
        fixed.cap = cap
        features = state.residual_features(fixed).tolist()
        eligible = snapshot["prefix_cpu_seconds"] < cap - clock.margin and snapshot["deliveries"] < budget
    else:
        x = dense_bits(rows)
        pool = PublicPool(data["task_id"], data["component"], tuple(r["candidate_id"] for r in rows), x)
        state = ResidualState(pool, kind, seed_for(data["task_id"], spec["seed"]), n0, budget,
                              cap_data["cost_priors"], control=spec["control"], gate_artifact=artifact)
        features, eligible = None, True
    oracle = Oracle([int(r["active"]) for r in rows], budget)
    policy, parameter = selector(spec["control"])
    if eligible:
        result, snapshots = run_campaign(state, oracle, clock, policy, parameter,
                                         spec.get("forced"), spec["stage"] == "training_prefixes")
    else:
        result = {"new_positives": state.hits, "new_deliveries": state.deliveries,
                  "assigned_B": budget, "assigned_C": cap, "scientific_cpu_seconds": snapshot["prefix_cpu_seconds"],
                  "cpu_violation": False, "trace": state.trace, "interruptions": state.interruptions,
                  "feasibility_fallbacks": state.feasibility_fallbacks, "operations": state.operation_counts}
        snapshots = {}
    assert not result["cpu_violation"], "CAMPAIGN_CPU_VIOLATION"
    assert result["new_positives"] == sum(r["delivered_label"] for r in result["trace"])
    result.update(spec=spec, task_id=data["task_id"], component=data["component"],
                  features=features, branch_eligible=eligible, initial_fit_count=state.initial_fit_count,
                  final_fitted_observations=state.model.fitted_observations,
                  gate_decisions=len(state.gate_log),
                  override_requests=sum(r["override_requested"] for r in state.gate_log),
                  delivered_overrides=sum(r["override_requested"] and r["delivered"] and not r["feasibility_fallback"] for r in state.gate_log))
    if spec["control"] == "frozen_cache_greedy":
        assert state.initial_fit_count <= 1 and state.model.fitted_observations <= n0
    return result, snapshots, state


def run_campaign(state, oracle, clock, policy, parameter=None, forced=None, snapshots=False):
    from research.m2_costed_v2.engine import run

    return run(state, oracle, clock, policy, parameter=parameter, forced=forced, snapshots=snapshots)


def profile_batch(root, job, permit):
    from research.lr_d23_v1.checks import checks
    from research.m2_costed_v2.engine import Clock, Oracle, PublicPool, State, run
    from research.m2_v1.models import synthetic_pool

    results = []
    for i, spec in enumerate(permit["contexts"]):
        clock = Clock(5 if spec["predictor"] == "rf" else 1)
        x, y, ids = synthetic_pool(spec["n"], 23)
        state = State(PublicPool("synthetic", "synthetic", tuple(ids), x), spec["predictor"],
                      823, spec["n0"], spec["budget"], dict(REUSE=.00001, UPDATE=.00001, PLAN=.1))
        result, _ = run(state, Oracle(y, spec["budget"]), clock, "G1")
        result.pop("trace")
        result.update(spec=spec, derived_cap_seconds=1.25 * result["scientific_cpu_seconds"],
                      last_fit_cpu_seconds=state.model.last_fit_cpu)
        good = (result["new_deliveries"] == spec["budget"] and result["interruptions"] == 0
                and result["feasibility_fallbacks"] == 0 and not result["cpu_violation"]
                and result["derived_cap_seconds"] <= clock.cap)
        result["status"] = "PASS" if good else "FAIL_REFERENCE_ADMISSION"
        new(job / f"context-{i:02d}.json", result)
        results.append(result)
        if not good:
            return {"status": "FAIL_ADMISSION", "contexts": results, "biological_labels_decoded": False}
    edge = checks()
    assert len(edge["checks"]) == 8
    return {"status": "PASS", "contexts": results, "edge_checks": edge,
            "biological_labels_decoded": False, "cpu": permit["cpu"]}


def fit_batch(root, job, permit):
    from research.lr_d23_v1.learning import fit_gate

    matrix = read(root / permit["matrix_path"])
    assert sha(root / permit["matrix_path"]) == permit["matrix_sha256"]
    artifacts, support = {}, {}
    for heldout, allowed in permit["folds"].items():
        rows = []
        prefixes = [u for u in matrix["units"] if u["stage"] == "training_prefixes" and u["heldout"] == heldout]
        for prefix in prefixes:
            for snapshot in (8, 16, 24):
                pair = [u for u in matrix["units"] if u["stage"] == "paired_branches"
                        and u["prefix"] == prefix["name"] and u["snapshot"] == snapshot]
                assert len(pair) == 2
                locations = {u["forced"]: root / permit["unit_paths"][u["name"]] for u in pair}
                for u in pair:
                    assert sha(locations[u["forced"]] / "result.json") == permit["unit_pins"][u["name"]]
                values = {op: read(path / "result.json") for op, path in locations.items()}
                for u in pair:
                    assert all(values[u["forced"]]["spec"][key] == value for key, value in u.items() if key != "attempt")
                assert set(values) == {"UPDATE", "REUSE"}
                a, b = values["UPDATE"], values["REUSE"]
                assert a["features"] == b["features"] and a["spec"]["cpu"] == b["spec"]["cpu"]
                traces = {op: read(path / "trace-private.json") for op, path in locations.items()}
                eligible = all(values[op]["branch_eligible"] and len(traces[op]) > snapshot
                               and traces[op][snapshot]["actual_operation"] == op for op in values)
                parent = permit.get("behavior_artifacts", {}).get(prefix.get("gate_key"))
                rows.append({"heldout": heldout, "component": a["component"], "task_id": a["task_id"],
                             "round": permit["round"], "eligible": bool(eligible), "features": a["features"],
                             "update_minus_reuse": a["new_positives"] - b["new_positives"],
                             "behavior_training_components": parent["training_components"] if parent else []})
        artifact = fit_gate(rows, heldout, allowed, permit["round"])
        key = heldout + (":v0" if permit["round"] == 0 else ":v1")
        artifacts[key] = artifact
        if permit["round"] == 1:
            artifacts[heldout + ":no_history"] = fit_gate(rows, heldout, allowed, 1, True)
        support[heldout] = {"assigned": len(rows), "eligible": sum(r["eligible"] for r in rows)}
    new(job / "gates-private.json", artifacts)
    return {"status": "PASS", "artifacts": artifacts, "support": support,
            "heldout_behavior_training_exclusion": True}


def main():
    permit = read(Path(sys.argv[1]))
    root = Path(permit["task_root"])
    assert root == Path.home() / "curaloop-tasks/lr-d23-20261109-v1"
    job = root / "jobs" / permit["attempt"]
    guard = CostedGuard(job / "resource.json", permit)
    try:
        new(job / "kernel-proof.json", guard.kernel_proof())
        for name, expected in permit["code_pins"].items():
            assert sha(root / "code" / name) == expected
        __import__("numpy")
        __import__("sklearn.ensemble")
        __import__("sklearn.linear_model")
        from threadpoolctl import threadpool_info, threadpool_limits

        threadpool_limits(limits=1)
        assert all(row["num_threads"] == 1 for row in threadpool_info())
        if permit["handler"] == "profiles":
            result = profile_batch(root, job, permit)
        elif permit["handler"] == "fit":
            assert permit["technical_admission"] == "PASS"
            result = fit_batch(root, job, permit)
        else:
            assert permit["handler"] == "campaigns" and permit["technical_admission"] == "PASS"
            import numpy as np

            emitted = []
            for spec in permit["units"]:
                folder = root / "units" / spec["name"] / ("a" + str(spec.get("attempt", 0)))
                folder.mkdir(parents=True, exist_ok=False)
                new(folder / "spec.json", spec)
                result, snapshots, state = campaign(root, spec, permit["artifacts"], permit["caps"], permit["sources"], permit["unit_paths"], permit["unit_pins"])
                new(folder / "trace-private.json", result.pop("trace"))
                new(folder / "gate-log-private.json", state.gate_log)
                if spec["stage"] == "training_prefixes":
                    assert set(snapshots) >= {8, 16, 24}, "INCOMPLETE_PREFIX_SUPPORT"
                    new(folder / "snapshots.json", snapshots)
                    np.savez_compressed(folder / "public-cache.npz", x=state.pool.x,
                                        similarity=state.similarity, neighbors=state.neighbors)
                    result["snapshot_sha256"] = sha(folder / "snapshots.json")
                    result["cache_sha256"] = sha(folder / "public-cache.npz")
                result["status"] = "PASS"
                result["whole_batch_cpu_seconds_at_completion"] = time.process_time()
                new(folder / "result.json", result)
                emitted.append({"unit": spec["name"], "path": str(folder.relative_to(root)),
                                "sha256": sha(folder / "result.json")})
            result = {"status": "PASS", "units": emitted, "count": len(emitted), "final_outcomes_open": False}
        new(job / "result.json", result)
        guard.finish("PASS" if result["status"] == "PASS" else "FAIL_ADMISSION")
        return 0 if result["status"] == "PASS" else 2
    except BaseException as error:
        signal.setitimer(signal.ITIMER_PROF, 0)
        new(job / "failure.json", {"type": type(error).__name__, "message": str(error)[:400]})
        guard.finish("FAIL")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
