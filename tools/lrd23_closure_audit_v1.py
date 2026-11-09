"""Independent file/trace re-read after the complete private LR-D23 return."""
# ruff: noqa: E402

import json
import math
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.analysis import analyze
from research.lr_d23_v1.common import PUBLIC, TASK, new, read, sha, utility_finish, utility_start
from research.m2_costed_v2.worker import seed_for
from research.m2_v1.models import seeded_order
from tools.lrd23_pipeline_v1 import validate_freeze


def audit():
    frozen = validate_freeze()
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    retained = sum(ledger["retained_seconds"].values())
    assert retained <= 86400 and not ledger["final_outcomes_open"]
    assert not release["conditional96h_activated"]
    preservation = read(TASK / "preservation-pins-v1.json")
    assert all(sha(ROOT / p) == digest for p, digest in preservation["pins"].items())
    assert all(sha(ROOT / p) == digest for p, digest in preservation["prior_ledgers"].items())
    returned = read(TASK / "remote-return/verified-v1.json")
    assert returned["status"] == "PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD"
    assert read(PUBLIC / "fresh-absence-v1.json")["status"] == "PASS_FRESH_EXACT_ABSENCE"
    files = TASK / "remote-return/files"
    sources = read(TASK / "sources.json")
    data = {}
    for task, meta in sources.items():
        path = files / "inputs" / (task + ".json")
        assert sha(path) == meta["sha256"]
        data[task] = read(path)
        assert data[task]["role"] == "development" and data[task]["component"] == meta["component"]
    assert len(data) == 6 and len(list((files / "inputs").glob("*.json"))) == 6
    for name, digest in frozen["code_pins"].items():
        assert sha(files / "code" / name) == digest
    matrix_keys = ["round0", "round1", "primary", "attribution"]
    if ledger["D3_status"] == "COMPLETE_PRESPECIFIED_CELLS":
        matrix_keys += [k for k in frozen["matrices"] if k.startswith("transfer-")]
    expected = {u["name"]: u for k in matrix_keys for u in read(TASK / "matrices" / (k + ".json"))["units"]}
    paths = list((files / "units").glob("*/a*/result.json"))
    assert len(paths) == len(expected)
    seen, counters, campaign_rows = set(), {}, []
    actual_override_total = 0
    for path in paths:
        value = read(path)
        spec = value["spec"]
        name = spec["name"]
        assert name not in seen and name in expected and spec == expected[name]
        assert path.parent.name == "a0" and value["status"] == "PASS" and not value["cpu_violation"]
        seen.add(name)
        counters[spec["stage"]] = counters.get(spec["stage"], 0) + 1
        trace = read(path.parent / "trace-private.json")
        assert len(trace) == value["new_deliveries"] <= spec["budget"]
        assert [r["query"] for r in trace] == list(range(1, len(trace) + 1))
        assert len({r["candidate_index"] for r in trace}) == len(trace)
        records = data[spec["task_id"]]["records"]
        initial = set(map(int, seeded_order(tuple(r["candidate_id"] for r in records),
                                           seed_for(spec["task_id"], spec["seed"]))[:spec["n0"]]))
        assert not initial.intersection(r["candidate_index"] for r in trace)
        assert all(int(records[r["candidate_index"]]["active"]) == r["delivered_label"] for r in trace)
        assert sum(r["delivered_label"] for r in trace) == value["new_positives"]
        assert all(r["new_positives"] == sum(t["delivered_label"] for t in trace[:i + 1]) for i, r in enumerate(trace))
        assert all(0 <= r["scientific_cpu_seconds"] <= value["assigned_C"] for r in trace)
        logs = read(path.parent / "gate-log-private.json")
        requested = sum(r["override_requested"] and r["delivered"] and not r["feasibility_fallback"] for r in logs)
        actual = sum(r["override_requested"] and r["delivered"] and not r["feasibility_fallback"]
                     and r["actual_operation"] == r["proposed_operation"] for r in logs)
        assert requested == value["delivered_overrides"]
        if spec["stage"] in ("D2_primary", "attribution") and spec["control"] == "candidate_v1":
            assert actual == requested, "INTERRUPTED_OVERRIDE_COUNT_REQUIRES_QUALIFIED_REANALYSIS"
            actual_override_total += actual
        if spec["stage"] in ("training_prefixes", "paired_branches"):
            assert value["component"] != spec["heldout"] and value["component"] in spec["training_components"]
        else:
            assert value["component"] == spec["heldout"]
            campaign_rows.append(value)
        if spec["stage"] == "training_prefixes":
            assert sha(path.parent / "snapshots.json") == value["snapshot_sha256"]
            assert sha(path.parent / "public-cache.npz") == value["cache_sha256"]
            snapshots = read(path.parent / "snapshots.json")
            initial = set(map(int, snapshots["0"]["observed"]))
            assert len(initial) == spec["n0"] and not initial.intersection(r["candidate_index"] for r in trace)
    assert seen == set(expected)
    fit_support = {}
    for round_index in (0, 1):
        result = read(files / "jobs" / ("fit-r" + str(round_index)) / "result.json")
        assert result["status"] == "PASS" and result["heldout_behavior_training_exclusion"]
        fit_support[str(round_index)] = result["support"]
        for artifact in result["artifacts"].values():
            assert artifact["training_states"] >= 30 and len(artifact["training_components"]) >= 2
            assert artifact["heldout_component"] not in artifact["training_components"]
            assert all(sources[t]["component"] != artifact["heldout_component"] for t in artifact["training_tasks"])
            if artifact["variant"] == "no_history":
                assert artifact["feature_indices"] == [0, 1, 3, 4]
    kernel_count, worker_cpu, training_cpu, max_unit_cpu = 0, 0., 0., 0.
    events, core_events = [], {}
    for name, booking in ledger["bookings"].items():
        if booking["host"] != "dr-train" or not (files / "jobs" / name / "permit.json").exists():
            continue
        permit = read(files / "jobs" / name / "permit.json")
        if permit["handler"] not in ("profiles", "campaigns", "fit"):
            continue
        proof = read(files / "jobs" / name / "kernel-proof.json")
        assert proof == {"cpu.max": "100000 100000", "memory.max": "4294967296", "memory.swap.max": "0"}
        resource = read(files / "jobs" / name / "resource.json")
        assert resource["status"] == "PASS" and booking["status"] == "PASS"
        assert resource["actual_cpu_affinity"] == [permit["cpu"]]
        cpu = resource["cpu_seconds"]
        assert cpu <= permit["reservation_seconds"]
        start = datetime.fromisoformat(resource["start_utc"]).timestamp()
        interval = [(start, 1), (start + resource["wall_seconds"], -1)]
        events.extend(interval)
        core_events.setdefault(permit["cpu"], []).extend(interval)
        worker_cpu += cpu
        if booking["bucket"] in ("training_prefixes", "paired_branches", "gate_fits"):
            training_cpu += cpu
        if permit["handler"] == "campaigns":
            previous = 0.
            for spec in permit["units"]:
                value = read(files / "units" / spec["name"] / "a0/result.json")
                completion = value["whole_batch_cpu_seconds_at_completion"]
                max_unit_cpu = max(max_unit_cpu, completion - previous)
                assert completion - previous <= 10., "WHOLE_UNIT_ENVELOPE_EXCEEDED"
                previous = completion
        kernel_count += 1
    original_rows = read(TASK / "D2-rows-private.json")
    reconstructed = [r for r in campaign_rows if r["spec"]["name"] in {u["name"] for k in ("primary", "attribution") for u in read(TASK / "matrices" / (k + ".json"))["units"]}]
    assert {r["spec"]["name"]: r for r in original_rows} == {r["spec"]["name"]: r for r in reconstructed}
    # Preserve the frozen collection order for bitwise floating-point reproduction.
    by_name = {r["spec"]["name"]: r for r in reconstructed}
    reconstructed = [by_name[r["spec"]["name"]] for r in original_rows]
    aggregate = analyze(reconstructed)
    assert aggregate == read(PUBLIC / "D2-aggregate-v1.json")
    def concurrency(points):
        current, maximum = 0, 0
        for _, change in sorted(points):
            current += change
            maximum = max(maximum, current)
        assert current == 0
        return maximum
    assert concurrency(events) <= 3 and all(concurrency(v) == 1 for v in core_events.values())
    delta = aggregate["means"]["G1"]["scientific_cpu_seconds"] - aggregate["means"]["candidate_v1"]["scientific_cpu_seconds"]
    result = {"status": "PASS_COMPLETE_CLOSURE_AUDIT", "biological_units": len(seen), "stage_counts": counters,
              "old_pins_unchanged": len(preservation["pins"]), "old_ledgers_unchanged": len(preservation["prior_ledgers"]),
              "all_returned_traces_labels_and_counts_verified": True, "outer_fold_support": fit_support,
              "kernel_verified_worker_batches": kernel_count, "measured_worker_process_cpu_seconds": worker_cpu,
              "maximum_remote_scientific_batch_concurrency": concurrency(events),
              "same_core_worker_overlap": False,
              "measured_experimental_training_cpu_seconds": training_cpu,
              "maximum_incremental_unit_cpu_seconds_including_first_unit_startup": max_unit_cpu,
              "hypothetical_training_recovery_campaigns_vs_G1": math.ceil(training_cpu / delta) if delta > 0 else None,
              "recovery_scope": "experimental fold-training workload / observed mean scientific CPU saving; excludes utility costs and is not a deployment or lab-economics estimate",
              "retained_cpu_envelope_seconds": retained, "cpu_cap_seconds": 86400,
              "actual_primary_delivered_overrides": actual_override_total,
              "exact_D2_aggregate_reproduction": True, "final_outcomes_open": False,
              "complete_return_sha256": sha(TASK / "remote-return/verified-v1.json")}
    new(PUBLIC / "closure-audit-v1.json", result)
    print(json.dumps(result))


if __name__ == "__main__":
    guard = utility_start("closure-audit", 240, 600)
    try:
        audit()
        utility_finish("closure-audit", guard, "PASS")
    except BaseException:
        utility_finish("closure-audit", guard, "FAIL")
        raise
