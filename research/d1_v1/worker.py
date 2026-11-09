"""New-root Linux D1 calibration/controls using the original screening engine."""

import hashlib
import json
import signal
import sys
import time
from pathlib import Path

from research.m2_costed_v2.guard import CostedGuard, new


def main():
    permit = json.loads(Path(sys.argv[1]).read_text())
    root = Path(permit["task_root"])
    assert root == Path.home() / "curaloop-tasks/d1-operation-headroom-20261109-v1"
    job = root / "jobs" / permit["attempt"]
    guard = CostedGuard(job / "resource.json", permit)
    try:
        new(job / "kernel-proof.json", guard.kernel_proof())
        for name, expected in permit["code_pins"].items():
            assert hashlib.sha256((root / "code" / name).read_bytes()).hexdigest() == expected
        # Eager scientific imports are measured startup, inside the whole-job guard.
        __import__("numpy")
        __import__("sklearn.ensemble")
        __import__("sklearn.linear_model")
        from threadpoolctl import threadpool_info, threadpool_limits

        from research.m2_costed_v2.engine import Clock, Oracle, PublicPool, State, run
        from research.m2_v1.models import dense_bits, synthetic_pool

        threadpool_limits(limits=1)
        assert all(pool["num_threads"] == 1 for pool in threadpool_info())
        if permit["handler"] == "calibration":
            rows = []
            for i, spec in enumerate(permit["contexts"]):
                clock = Clock(5 if spec["policy"] == "G1" else 65)
                x, y, ids = synthetic_pool(spec["n"], spec["repeat"])
                pool = PublicPool("constructed", "constructed", tuple(ids), x)
                state = State(pool, "rf", 5000 + spec["repeat"], spec["n0"], 32,
                              dict(REUSE=.00001, UPDATE=.00001, PLAN=.00001))
                result, _ = run(state, Oracle(y, 32), clock, spec["policy"])
                result.pop("trace")
                result["context"] = spec
                result["derived_cap_seconds"] = result["scientific_cpu_seconds"] * 1.25
                passed = (result["new_deliveries"] == 32 and result["interruptions"] == 0
                          and result["feasibility_fallbacks"] == 0 and not result["cpu_violation"]
                          and result["derived_cap_seconds"] <= clock.cap)
                result["status"] = "PASS" if passed else "FAIL_REFERENCE_ADMISSION"
                new(job / (f"context-{i:02d}.json"), result)
                rows.append(result)
                if not passed:
                    break
            passed = len(rows) == 12 and all(row["status"] == "PASS" for row in rows)
            new(job / "result.json", {"status": "PASS" if passed else "FAIL", "contexts": rows,
                                      "biological_labels_decoded": False})
            guard.finish("PASS" if passed else "FAIL_ADMISSION")
            return 0 if passed else 2
        assert permit["handler"] == "controls" and permit["calibration_status"] == "PASS"
        assert hashlib.sha256((root / "jobs/calibration/result.json").read_bytes()).hexdigest() == permit["calibration_sha256"]
        from research.d1_v1.controls import DiagnosticState, selector
        from research.m2_costed_v2.worker import seed_for

        rows = []
        for spec in permit["units"]:
            # One startup accounting boundary per batch, individual C includes
            # fingerprints/graph, initialization, fitting and selector work.
            path = root / "inputs" / (spec["task_id"] + ".json")
            assert hashlib.sha256(path.read_bytes()).hexdigest() == spec["input_sha256"]
            data = json.loads(path.read_text())
            assert data["role"] == "development" and data["task_id"] == spec["task_id"]
            clock = Clock(5)
            records = data["records"]
            x = dense_bits(records)
            pool = PublicPool(data["task_id"], data["component"], tuple(r["candidate_id"] for r in records), x)
            state = DiagnosticState(pool, "rf", seed_for(data["task_id"], spec["seed"]), spec["n0"],
                                    32, spec["cost_priors"], control=spec["control"])
            oracle = Oracle([int(r["active"]) for r in records], 32)
            policy, parameter = selector(spec["control"])
            result, _ = run(state, oracle, clock, policy, parameter=parameter)
            trace = result.pop("trace")
            assert result["new_positives"] == sum(t["delivered_label"] for t in trace)
            assert result["new_deliveries"] == len(trace)
            assert not result["cpu_violation"]
            result.update(spec=spec, component=data["component"], task_id=data["task_id"],
                          initial_fit_count=state.initial_fit_count,
                          model_fitted_observations=state.model.fitted_observations,
                          whole_batch_process_cpu_seconds=time.process_time(),
                          nearest_prequential_prediction="constant 0.5 placeholder; not used as a calibrated probability")
            if spec["control"] == "frozen_cache_greedy":
                assert state.initial_fit_count <= 1 and state.model.fitted_observations <= spec["n0"]
            new(job / (spec["name"] + "-trace-private.json"), trace)
            new(job / (spec["name"] + ".json"), result)
            rows.append(result)
        assert len(rows) == 120
        new(job / "result.json", {"status": "PASS", "units": rows,
                                  "startup_amortized_once_for_batch": True,
                                  "final_outcomes_open": False})
        guard.finish("PASS")
        return 0
    except BaseException as error:
        signal.setitimer(signal.ITIMER_PROF, 0)
        new(job / "failure.json", {"type": type(error).__name__, "message": str(error)[:300]})
        guard.finish("FAIL")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
