"""One guarded remote worker, fixed phase cases, private scientific outputs."""

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from .guard import GoalGuard
from .identity import CONFIG, PACKET, RUN, frozen, load_task, sha, write_new

ROOT = Path(__file__).resolve().parents[2]


def case_key(case):
    return hashlib.sha256(json.dumps(case, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def cases(protocol, phase, selected=None):
    if phase.startswith("diagnosis"):
        values = [{"task_id": t["task_id"], "seed": s, "support": n, "predictor": m}
                  for t in protocol["tasks"] for s in protocol["seeds"] for n in (16, 28)
                  for m in protocol["diagnostic_predictors"]]
    else:
        arms = protocol["main_arms"]
        if phase == "ablation":
            if selected not in ("anchor_normalized", "tanimoto_gp"):
                raise ValueError("Locked repair selection required.")
            arms = [selected + "__" + m for m in protocol["ablations"]]
        values = [{"task_id": t["task_id"], "seed": s, "operation": op["id"], "arm": a}
                  for t in protocol["tasks"] for s in protocol["seeds"]
                  for op in protocol["operations"] for a in arms]
    if phase.endswith("canary"):
        largest = sorted(protocol["tasks"], key=lambda t: (-t["rows"], t["task_id"]))[0]["task_id"]
        values = [c for c in values if c["task_id"] == largest and c["seed"] == 101]
    if phase == "reexecution":
        smallest = min(t["task_id"] for t in protocol["tasks"])
        values = [c for c in values if c["task_id"] == smallest and c["seed"] == 101]
    return values


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=["constructed", "diagnosis_canary", "diagnosis", "campaign_canary", "campaign", "ablation", "reexecution"], required=True)
    p.add_argument("--shard", type=int, default=0)
    p.add_argument("--shards", type=int, choices=[1, 2, 4], default=1)
    p.add_argument("--cpu", type=int, required=True)
    p.add_argument("--cpu-seconds", type=int, required=True)
    p.add_argument("--wall-seconds", type=int, required=True)
    p.add_argument("--attempt", default="v1")
    args = p.parse_args()
    if os.name != "posix" or ROOT != Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1"):
        raise ValueError("Owner-directed scientific compute is remote only.")
    if not 0 <= args.shard < args.shards or args.cpu not in os.sched_getaffinity(0):
        raise ValueError("Invalid shard/affinity.")
    os.sched_setaffinity(0, {args.cpu})
    output = ROOT / RUN / "runs" / (args.phase + "-" + args.attempt) / f"shard-{args.shard}"
    output.mkdir(parents=True, exist_ok=False)
    guard = GoalGuard(output / "resources.json", args.wall_seconds, args.cpu_seconds)
    try:
        if args.phase == "constructed":
            import pytest
            status = pytest.main(["-q", "tests/research/test_goal4r1_v1.py", "-p", "no:cacheprovider", "--tb=short"])
            guard.finish("PASS" if status == 0 else "FAIL", pytest_exit_code=int(status))
            raise SystemExit(status)
        protocol = frozen(ROOT)
        selected = None
        if args.phase == "ablation":
            selection = json.loads((ROOT / RUN / "selection.json").read_text())
            proof = json.loads((ROOT / PACKET / "selection-freeze-v1.json").read_text())
            if sha(ROOT / RUN / "selection.json") != proof["selection_sha256"]:
                raise ValueError("Selection changed.")
            selected = selection["selected_repair"]
        values = cases(protocol, args.phase, selected)[args.shard::args.shards]
        write_new(output / "identity.json", {"phase": args.phase, "cases": values,
                  "protocol_sha256": sha(ROOT / CONFIG), "python": sys.version, "cpu": args.cpu})
        from .campaign import run_campaign
        from .diagnostics import diagnose
        operations = {op["id"]: op for op in protocol["operations"]}
        payloads = {tid: load_task(ROOT, protocol, tid) for tid in sorted({c["task_id"] for c in values})}
        results = []
        with (output / "progress.jsonl").open("x", encoding="utf-8", newline="\n") as f:
            for case in values:
                if args.phase.startswith("diagnosis"):
                    result = diagnose(payloads[case["task_id"]], case["seed"], case["support"], case["predictor"])
                else:
                    result = run_campaign(payloads[case["task_id"]], case["seed"], operations[case["operation"]], case["arm"], protocol)
                result["case"] = case
                key = case_key(case)
                path = output / (key + ".json")
                write_new(path, result)
                results.append({"case_key": key, "file": path.name, "sha256": sha(path)})
                f.write(json.dumps({"completed": len(results), "total": len(values), "case_key": key}) + "\n")
                f.flush()
        write_new(output / "complete.json", {"status": "PASS", "results": results})
        guard.finish("PASS", completed_cases=len(results), final_outcome_use=False)
        print(json.dumps({"status": "PASS", "phase": args.phase, "shard": args.shard, "cases": len(results)}))
    except Exception as e:
        write_new(output / "failure.json", {"status": "FAIL", "exception_type": type(e).__name__, "raw_text_suppressed": True})
        guard.finish("FAIL", sanitized_reason=type(e).__name__)
        print(json.dumps({"status": "FAIL", "exception_type": type(e).__name__}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
