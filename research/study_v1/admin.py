"""Complete phase verification and prespecified timing/selection gates."""

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import sha_file, write_new
from .identity import CONFIG_RELATIVE, PACKET_RELATIVE, RUN_RELATIVE, verify_frozen, verify_selection
from .design import case_key, cases

ROOT = Path(__file__).resolve().parents[2]


def roster(root):
    return json.loads((root / "docs/evidence/plan-a-20261105-v1/feature-cohort-v2-result.json").read_text())["selected_task_manifest"]


def collect(root, phase, protocol, seeds=None, selected=None):
    run = root / RUN_RELATIVE
    expected = {case_key(c): c for c in cases(protocol, roster(root), phase, seeds, selected)}
    records, identities = {}, {}
    directories = sorted((run / "runs" / phase).glob("shard-*"))
    if not directories:
        raise ValueError("No completed phase workers.")
    for directory in directories:
        resources = json.loads((directory / "resources.json").read_text())
        complete = json.loads((directory / "complete.json").read_text())
        if resources["status"] != "PASS" or complete["status"] != "PASS":
            raise ValueError("Worker incomplete/failed; retain and report.")
        if sha_file(directory / "identity.json") != complete["identity_sha256"]:
            raise ValueError("Worker identity changed.")
        identity = json.loads((directory / "identity.json").read_text())
        if identity["protocol_sha256"] != sha_file(root / CONFIG_RELATIVE):
            raise ValueError("Wrong worker protocol.")
        for item in complete["results"]:
            path = (directory / item["file"]).resolve()
            if path.parent != directory.resolve() or sha_file(path) != item["sha256"]:
                raise ValueError("Result changed.")
            result = json.loads(path.read_text())
            key = item["case_key"]
            if key in records or key not in expected or result["case"] != expected[key] or result["status"] != "PASS":
                raise ValueError("Duplicate/unexpected/failed case.")
            records[key] = result
            identities[path.relative_to(run.resolve()).as_posix()] = item["sha256"]
    if set(records) != set(expected):
        raise ValueError("The mandatory finite allocation is incomplete.")
    return list(records.values()), identities


def family_means(records, field="new_hits"):
    grouped = defaultdict(lambda: defaultdict(list))
    for r in records:
        grouped[r["family_id"]][r["task_id"]].append(r["metrics"][field])
    return {group: sum(sum(values)/len(values) for values in assays.values())/len(assays)
            for group, assays in sorted(grouped.items())}


def allocate(root, workers):
    protocol = verify_frozen(root)
    run, packet = root / RUN_RELATIVE, root / PACKET_RELATIVE
    records, source_ids = collect(root, "canary", protocol)
    # Only timings/case identities inform allocation; discovery metrics unused.
    maxima_cpu, maxima_wall = defaultdict(float), defaultdict(float)
    for record in records:
        key = (record["method"], record["hypotheses"])
        maxima_cpu[key] = max(maxima_cpu[key], record["run_cpu_seconds"])
        maxima_wall[key] = max(maxima_wall[key], record["run_wall_seconds"])
    method_cpu = {method: max(maxima_cpu[(method, m)] for m in protocol["hypotheses"]) for method in protocol["methods"]}
    method_wall = {method: max(maxima_wall[(method, m)] for m in protocol["hypotheses"]) for method in protocol["methods"]}
    charged_canary = sum(json.loads(p.read_text())["cpu_seconds"] for p in (run / "runs/canary").glob("shard-*/resources.json"))
    remaining_cpu = protocol["goal4_cpu_limit_seconds"] - charged_canary - 1800
    remaining_wall = (datetime.fromisoformat(protocol["deadline_utc"]) - datetime.now(timezone.utc)).total_seconds()
    forecasts = []
    chosen = None
    for n in (8, 4):
        seeds = protocol["seeds"][:n]
        batches = cases(protocol, roster(root), "development", seeds)
        batches += cases(protocol, roster(root), "crossed", seeds, 128)
        batches += cases(protocol, roster(root), "benchmark", seeds, 128)
        batches += cases(protocol, roster(root), "reexecution", seeds, 128)
        cpu = 3 * sum(method_cpu[case["method"]] for case in batches)
        wall = 3 * sum(method_wall[case["method"]] for case in batches)
        cpu += 900  # Calibration, result verification, fresh checks and utility reserve.
        wall += 900
        feasible = cpu <= remaining_cpu * .8 and wall / workers <= remaining_wall * .75
        forecasts.append({"seeds": n, "projected_cpu_seconds": cpu,
                          "projected_serial_wall_seconds": wall, "workers": workers, "feasible": feasible})
        if chosen is None and feasible:
            chosen = seeds
    if chosen is None:
        write_new(packet / "allocation-infeasible-v1.json", {"status": "REQUIRES_OWNER_CONSULTATION", "forecasts": forecasts})
        raise ValueError("Cannot afford mandatory allocation.")
    allocation = {"status": "PASS_TIMING_ONLY_ALLOCATION", "seeds": chosen, "workers": workers,
                  "forecasts": forecasts, "canary_result_sha256": source_ids,
                  "canary_cpu_seconds": charged_canary, "protocol_sha256": sha_file(root / CONFIG_RELATIVE),
                  "utility_used_for_allocation": False, "factor": 3,
                  "created_utc": datetime.now(timezone.utc).isoformat()}
    write_new(run / "allocation.json", allocation)
    write_new(packet / "allocation-freeze-v1.json", {"status": "PASS", "seeds": chosen, "workers": workers,
              "allocation_sha256": sha_file(run / "allocation.json"),
              "protocol_sha256": sha_file(root / CONFIG_RELATIVE), "forecasts": forecasts,
              "utility_used_for_allocation": False})
    print(json.dumps({"status": "PASS", "seeds": chosen, "workers": workers, "forecasts": forecasts}, indent=2))


def select(root):
    protocol = verify_frozen(root)
    run, packet = root / RUN_RELATIVE, root / PACKET_RELATIVE
    allocation = json.loads((run / "allocation.json").read_text())
    proof = json.loads((packet / "allocation-freeze-v1.json").read_text())
    if sha_file(run / "allocation.json") != proof["allocation_sha256"]:
        raise ValueError("Allocation identity changed.")
    records, source_ids = collect(root, "development", protocol, allocation["seeds"])
    summaries = []
    for m in protocol["hypotheses"]:
        relevant = [r for r in records if r["method"] == "event_screened" and r["hypotheses"] == m]
        grouped = family_means(relevant)
        if len(grouped) != 4:
            raise ValueError("Development group allocation incomplete.")
        summaries.append({"hypotheses": m, "family_means_H": grouped,
                          "macro_H": sum(grouped.values()) / len(grouped),
                          "mean_policy_seconds": sum(r["policy_wall_seconds"] for r in relevant)/len(relevant)})
    selected = sorted(summaries, key=lambda row: (-row["macro_H"], row["hypotheses"]))[0]["hypotheses"]
    selection = {"status": "PASS_SELECTION_FROZEN", "selected_hypotheses": selected,
                 "rule": protocol["selection"], "candidates": summaries,
                 "development_result_sha256": source_ids,
                 "protocol_sha256": sha_file(root / CONFIG_RELATIVE),
                 "allocation_sha256": sha_file(run / "allocation.json"),
                 "validation_or_heldout_operation_utility_used": False,
                 "created_utc": datetime.now(timezone.utc).isoformat()}
    write_new(run / "selection.json", selection)
    write_new(packet / "selection-freeze-v1.json", {k: v for k, v in selection.items() if k != "development_result_sha256"} |
              {"selection_sha256": sha_file(run / "selection.json"), "development_campaigns": len(records)})
    print(json.dumps({"status": "PASS", "selected_hypotheses": selected, "candidates": summaries}, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["allocate", "select"])
    parser.add_argument("--workers", type=int, choices=[1, 2, 4], default=2)
    args = parser.parse_args()
    if args.action == "allocate":
        allocate(ROOT, args.workers)
    else:
        select(ROOT)


if __name__ == "__main__":
    main()
