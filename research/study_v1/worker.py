"""Guarded one-campaign-at-a-time worker. Private results stay under .local."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import sys
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[2]


def set_cpu(cpu):
    if cpu is None:
        return
    if os.name == "nt":
        import ctypes
        from ctypes import wintypes
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = wintypes.HANDLE
        kernel.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
        if not kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(), 1 << cpu):
            raise ctypes.WinError(ctypes.get_last_error())
    else:
        if cpu not in os.sched_getaffinity(0):
            raise ValueError("CPU is outside the allowed affinity.")
        os.sched_setaffinity(0, {cpu})


def calibration(payload, seed, hypotheses, protocol):
    import numpy as np
    from .campaign import initial_ids
    from research.planning_v3.belief import fit_mixture, make_design
    rows = sorted(payload["records"], key=lambda r: r["candidate_id"])
    ids = tuple(r["candidate_id"] for r in rows)
    packed = tuple(sum(1 << bit for bit in r["morgan_on_bits"]) for r in rows)
    design = make_design(ids, packed, 64)
    initial = set(initial_ids(payload, seed, protocol["initial_labels"]))
    known = [(r["candidate_id"], r["active"]) for r in rows if r["candidate_id"] in initial]
    model, trace = fit_mixture(design, known, seed, hypotheses)
    audit = [i for i, r in enumerate(rows) if r["candidate_id"] not in initial]
    p = np.clip(model.mu[audit], 1e-9, 1 - 1e-9)
    y = np.array([float(rows[i]["active"]) for i in audit])
    bins = []
    for i in range(5):
        mask = (p >= i / 5) & ((p < (i + 1) / 5) if i < 4 else (p <= 1))
        bins.append({"lower": i / 5, "upper": (i + 1) / 5, "n": int(mask.sum()),
                     "mean_probability": float(p[mask].mean()) if mask.any() else None,
                     "active_fraction": float(y[mask].mean()) if mask.any() else None})
    return {"status": "PASS", "task_id": payload["task_id"], "role": payload["role"],
            "family_id": payload["family_id"], "seed": seed, "hypotheses": hypotheses,
            "method": "calibration", "audit_n": len(audit), "brier": float(np.mean((p-y)**2)),
            "log_loss": float(-np.mean(y*np.log(p)+(1-y)*np.log1p(-p))),
            "bins": bins, "model_trace": trace, "initial_only_diagnostic": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["canary", "development", "crossed", "benchmark", "reexecution", "calibration"], required=True)
    parser.add_argument("--shard", type=int, default=0)
    parser.add_argument("--shards", type=int, choices=[1, 2, 4], default=1)
    parser.add_argument("--cpu", type=int)
    parser.add_argument("--cpu-seconds", type=int, required=True)
    parser.add_argument("--wall-seconds", type=int, required=True)
    args = parser.parse_args()
    if not 0 <= args.shard < args.shards or (args.phase == "benchmark" and args.shards != 1):
        raise ValueError("Invalid protocol shard/order.")
    set_cpu(args.cpu)
    run = ROOT / ".local/plan-a-20261105-v2"
    output = run / "runs" / args.phase / f"shard-{args.shard}"
    output.mkdir(parents=True, exist_ok=False)
    guard = Guard(output / "resources.json", args.wall_seconds, 1024**3, args.cpu_seconds)
    try:
        from .identity import CONFIG_RELATIVE, PACKET_RELATIVE, RUN_RELATIVE, verify_frozen, verify_selection
        from .design import cases, case_key
        from .campaign import run_campaign
        from research.benchmark_v3.prepare_features_v2 import sha_file, write_new
        protocol = verify_frozen(ROOT)
        packet = ROOT / PACKET_RELATIVE
        tasks = json.loads((ROOT / "docs/evidence/plan-a-20261105-v1/feature-cohort-v2-result.json").read_text())["selected_task_manifest"]
        allocation = None
        if args.phase != "canary":
            allocation_path = run / "allocation.json"
            allocation_proof = json.loads((packet / "allocation-freeze-v1.json").read_text())
            if sha_file(allocation_path) != allocation_proof["allocation_sha256"] or sha_file(ROOT / CONFIG_RELATIVE) != allocation_proof["protocol_sha256"]:
                raise ValueError("Allocation freeze changed.")
            allocation = json.loads(allocation_path.read_text())
        selection = verify_selection(ROOT, protocol) if args.phase not in ("canary", "development") else None
        seed_values = allocation["seeds"] if allocation else None
        selected = selection["selected_hypotheses"] if selection else None
        all_cases = cases(protocol, tasks, args.phase, seed_values, selected)
        assigned = [case for i, case in enumerate(all_cases) if i % args.shards == args.shard]
        if not assigned:
            raise ValueError("No allowlisted cases assigned.")
        operations = {op["id"]: op for op in protocol["operations"]}
        data, data_ids = {}, {}
        for role in sorted({case["role"] for case in assigned}):
            path = run / "private-inputs" / role
            proof = json.loads((packet / f"label-access-{role}-v1.json").read_text())
            if sha_file(path / "manifest.json") != proof["private_manifest_sha256"]:
                raise ValueError("Private input manifest changed.")
            manifest = json.loads((path / "manifest.json").read_text())
            expected = {t["assay_id"]: t for t in tasks if t["role"] == role}
            if {t["task_id"] for t in manifest["tasks"]} != set(expected):
                raise ValueError("Private input roster differs from frozen feature population.")
            for item in manifest["tasks"]:
                source = (path / item["file"]).resolve()
                if source.parent != path.resolve() or sha_file(source) != item["sha256"]:
                    raise ValueError("Private input file changed.")
                payload = json.loads(source.read_text())
                target = expected[item["task_id"]]
                if (payload["role"] != role or payload["task_id"] != target["assay_id"] or
                    payload["family_id"] != target["family_id"] or
                    payload["feature_sha256"] != target["feature_sha256"] or
                    len(payload["records"]) != target["retained_structures"]):
                    raise ValueError("Private/public input identity mismatch.")
                data[item["task_id"]] = payload
                data_ids[item["task_id"]] = item["sha256"]
        identity = {"phase": args.phase, "shard": args.shard, "shards": args.shards,
                    "case_count": len(assigned), "cases": assigned,
                    "protocol_sha256": sha_file(ROOT / CONFIG_RELATIVE),
                    "freeze_sha256": sha_file(packet / "protocol-freeze-v1.json"),
                    "private_input_sha256": data_ids, "python": sys.version, "platform": platform.platform(),
                    "packages": {name: importlib.metadata.version(name) for name in ("numpy", "scipy", "scikit-learn", "rdkit", "threadpoolctl")}}
        write_new(output / "identity.json", identity)
        records = []
        with (output / "progress.jsonl").open("x", encoding="utf-8", newline="\n") as progress:
            for number, case in enumerate(assigned):
                payload = data[case["task_id"]]
                if case["method"] == "calibration":
                    result = calibration(payload, case["seed"], case["hypotheses"], protocol)
                else:
                    result = run_campaign(payload, case["seed"], operations[case["operation"]], case["method"], case["hypotheses"], protocol)
                key = case_key(case)
                result["case"] = case
                result["private_input_sha256"] = data_ids[case["task_id"]]
                write_new(output / f"{key}.json", result)
                records.append({"case_key": key, "file": f"{key}.json", "sha256": sha_file(output / f"{key}.json")})
                progress.write(json.dumps({"completed": number + 1, "total": len(assigned), "case_key": key}) + "\n")
                progress.flush()
        write_new(output / "complete.json", {"status": "PASS", "results": records,
                  "identity_sha256": sha_file(output / "identity.json")})
        guard.finish("PASS", completed_campaigns=len(records), final_outcome_use=False)
        print(json.dumps({"status": "PASS", "phase": args.phase, "shard": args.shard, "completed": len(records)}))
    except Exception as error:
        # Do not emit source rows, label vectors, path values or traceback locals.
        from research.benchmark_v3.prepare_features_v2 import write_new
        write_new(output / "failure.json", {"status": "FAIL", "exception_type": type(error).__name__, "raw_text_suppressed": True})
        guard.finish("FAIL", sanitized_reason=type(error).__name__)
        print(json.dumps({"status": "FAIL", "exception_type": type(error).__name__}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
