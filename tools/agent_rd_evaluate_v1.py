"""Serial locked execution with immutable per-unit receipts and all planned units."""

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write
from agent_rd_remote_v1 import call

from curaloop_rd.agent_rd.contracts import MissionSpec
from curaloop_rd.agent_rd.store import MissionStore
from research.agent_rd_eval_v1.execution import execute
from research.agent_rd_eval_v1.scoring import score

FREEZE = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
FROZEN = ROOT / "research/agent_rd_eval_v1/frozen"
WORK = TASK / "locked-evaluation-v1"
RESULTS = PUBLIC / "locked-results-v1"


def validate():
    release, ledger = authority()
    freeze = read(FREEZE)
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items()), "Frozen code/input/protocol changed; stop, never rebase"
    assert sha(FREEZE) == sha(PUBLIC / "protocol-freeze-v1.json")
    return release, ledger


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-units", type=int, default=408)
    args = parser.parse_args()
    release, _ = validate()
    # Protocol lock must be reachable from committed main before the first call.
    committed = subprocess.run(["rtk", "proxy", "git", "cat-file", "-e", "HEAD:research/manifests/agent_rd_protocol_freeze_20261110_v1.json"], cwd=ROOT, capture_output=True)
    assert committed.returncode == 0, "Commit the freeze before locked calls"
    clean = subprocess.run(["rtk", "proxy", "git", "diff", "--quiet", "HEAD", "--", *read(FREEZE)["pins"], str(FREEZE.relative_to(ROOT))], cwd=ROOT)
    assert clean.returncode == 0, "Commit exact frozen execution bytes before locked calls"
    WORK.mkdir(exist_ok=True)
    RESULTS.mkdir(exist_ok=True)
    cards = {row["case_id"]: row for row in read(FROZEN / "locked-cases.json")}
    truth = read(FROZEN / "locked-oracle.json")
    plan = read(FROZEN / "schedule.json")
    store = MissionStore(WORK / "missions")
    phase = call("status")
    assert phase["phase"]["phase"] == "evaluation", "Evaluation resource phase must be entered exactly once after freeze"
    lock = TASK / "evaluation.lock"
    if not lock.exists():
        write(lock, {"freeze_sha256": sha(FREEZE), "purpose": "Prevent ad-hoc product model calls during locked evaluation"}, True)
    assert read(lock)["freeze_sha256"] == sha(FREEZE)
    write(WORK / ("invocation-" + str(time.time_ns()) + ".json"), {"utc": datetime.now(timezone.utc).isoformat(),
          "max_units": args.max_units, "head": subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
          "freeze_sha256": sha(FREEZE), "phase": phase}, True)
    completed, launched, stopped = 0, 0, None
    for unit in plan:
        result_path = RESULTS / (unit["unit_id"] + ".json")
        if result_path.exists():
            existing = read(result_path)
            assert existing["unit"] == unit and sha(WORK / "missions" / (existing["mission_id"] + ".json")) == existing["mission_file_sha256"]
            completed += 1
            continue
        if launched >= args.max_units:
            stopped = "OPERATIONAL_BATCH_BOUNDARY"
            break
        validate()
        deadline_left = (datetime.fromisoformat(release["deadline_utc"]) - datetime.now(timezone.utc)).total_seconds()
        status = call("status")
        remaining = status["phase"]["cpu_base"] + status["phase"]["cpu_cap"] - status["container_cpu_seconds"]
        if remaining < 3000 or deadline_left < 900:
            stopped = "NOT_RUN_RESOURCE_LIMIT"
            break
        identity_path = WORK / (unit["unit_id"] + "-identity.json")
        card = cards[unit["case_id"]]
        if identity_path.exists():
            identity = read(identity_path)["mission_id"]
        else:
            row = store.create(MissionSpec.model_validate(card["spec"]), system=unit["system"], seed=unit["seed"])
            identity = row["mission_id"]
            write(identity_path, {"unit": unit, "mission_id": identity}, True)
        started = time.monotonic()
        cpu_started = time.process_time()
        try:
            row = execute(card, unit, store, WORK, identity=identity)
        except Exception as exc:
            current = store.read(identity)
            row = store.update(identity, current["revision"], "FAILED", "Locked harness exception retained; no replacement unit",
                               error=type(exc).__name__ + ": " + str(exc)[:800])
            stopped = "HARNESS_FAILURE"
        observed = score(card, truth[unit["case_id"]], row)
        trace = WORK / "missions" / (identity + ".json")
        receipt = {"unit": unit, "mission_id": identity, "state": row["state"], "score": observed,
                   "mission_file_sha256": sha(trace), "unit_wall_seconds": time.monotonic() - started,
                   "controller_cpu_seconds": time.process_time() - cpu_started,
                   "controller_cpu_scope": "This Python process only; model CPU is separate and local SSH child overhead is excluded",
                   "utc": datetime.now(timezone.utc).isoformat(), "freeze_sha256": sha(FREEZE)}
        write(result_path, receipt, True)
        # Public trace contains only the same admitted aggregate packet/model output.
        write(RESULTS / (unit["unit_id"] + "-trace.json"), read(trace), True)
        completed += 1
        launched += 1
        print(json.dumps({"completed": completed, "planned": 408, "unit": unit["unit_id"], "state": row["state"],
                          "task_success": observed["success"], "model_cpu": row["cost"]["model_cpu_seconds"]}), flush=True)
        write(WORK / "progress.json", {"completed": completed, "planned": 408, "last_unit": unit, "last_receipt": receipt})
        if row["state"] == "FAILED":
            stopped = stopped or "PROVIDER_OR_CONTROLLER_FAILURE"
        if stopped:
            break
    attempted = {p.name.removesuffix(".json") for p in RESULTS.glob("*.json") if not p.name.endswith("-trace.json")}
    disposition = [{**u, "status": "ATTEMPTED" if u["unit_id"] in attempted else (stopped or "NOT_RUN")} for u in plan]
    summary = {"status": "COMPLETE" if len(attempted) == len(plan) else "INCOMPLETE", "attempted_units": len(attempted), "planned_units": len(plan),
               "stop_reason": stopped, "disposition": disposition, "utc": datetime.now(timezone.utc).isoformat()}
    write(WORK / ("batch-disposition-" + str(time.time_ns()) + ".json"), summary, True)
    write(PUBLIC / "locked-progress-v1.json", summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "disposition"}), flush=True)


if __name__ == "__main__":
    main()
