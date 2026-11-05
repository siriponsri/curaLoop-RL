"""Metadata-only resource/source closeout before full task preservation."""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.redesign_v1.identity import CONFIG, PACKET, RUN, frozen, sha, write_new
from tools.goal4r1_admin_v1 import ALLOWANCE, CAPS, state

ROOT = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")


def main():
    if Path.cwd().resolve() != ROOT:
        raise ValueError("Owned remote root required.")
    os.sched_setaffinity(0, {71})
    protocol = frozen(ROOT)
    ledger = json.loads((ROOT / RUN / "reservations.json").read_text())
    charges, active, jobs = state(ledger["jobs"])
    if active or any(j["status"] != "PASS" for j in jobs) or any(charges[k] > CAPS[k] for k in CAPS) or sum(charges.values()) > 28800:
        raise ValueError("Resource completion/cap gate failed.")
    receipts, actual = [], {}
    deadline = datetime(2026, 11, 6, 2, 43, 55, tzinfo=timezone.utc)
    for job in ledger["jobs"]:
        r = json.loads((ROOT / job["resource_relative"]).read_text())
        finish = datetime.fromisoformat(r["start_utc"]) + timedelta(seconds=r["wall_seconds"])
        if finish > deadline or len(r["cpu_affinity"]) != 1 or r["cpu_affinity"][0] not in (68, 69, 70, 71):
            raise ValueError("Worker affinity/window differed.")
        actual[job["stage"]] = actual.get(job["stage"], 0) + r["cpu_seconds"]
        receipts.append({"phase": job["phase"], "shard": job["shard"], "cpu_seconds": r["cpu_seconds"],
                         "wall_seconds": r["wall_seconds"], "finish_utc": finish.isoformat(),
                         "receipt_sha256": sha(ROOT / job["resource_relative"])})
    inside_allowance = []
    for filename, stage in (("selection-resources.json", "D1"), ("reporting-check-resources.json", "D3"), ("analysis-resources.json", "D3")):
        p = ROOT / RUN / filename
        r = json.loads(p.read_text())
        if r["status"] != "PASS":
            raise ValueError("Analysis/check did not pass.")
        inside_allowance.append({"file": filename, "stage": stage, "actual_cpu_seconds": r["cpu_seconds"], "sha256": sha(p)})
    # Preserve completed setup's actual compliance without retroactively claiming
    # a parent-plus-child CPU watchdog existed in that preparation helper.
    setup = json.loads((ROOT / "remote-install-v1.json").read_text())
    private = ROOT / RUN / "private-inputs"
    if {p.name for p in private.iterdir()} != {t["task_id"] + ".json" for t in protocol["tasks"]}:
        raise ValueError("Unexpected private-input roster.")
    if any(sha(private / (t["task_id"] + ".json")) != t["sha256"] for t in protocol["tasks"]):
        raise ValueError("Private input changed.")
    results = json.loads((ROOT / PACKET / "results-v1.json").read_text())
    report = {"status": "PASS_REMOTE_EXECUTION_COMPLETE_BEFORE_PRESERVATION", "utc": datetime.now(timezone.utc).isoformat(),
              "phase_actual_worker_cpu_seconds": actual, "analysis_cpu_inside_allowances": inside_allowance,
              "conservative_phase_charges_seconds": charges, "conservative_total_charge_seconds": sum(charges.values()),
              "utility_allowances_seconds": ALLOWANCE, "phase_caps_seconds": CAPS, "global_cap_seconds": 28800,
              "exhaustive_exact_host_cpu_accounting": "NOT_CERTIFIED; startup margins and utility reserves are conservative",
              "maximum_scientific_cpu_workers": 4, "blas_threads_per_worker": 1, "gpu_used": False,
              "all_worker_receipts_passed": True, "active_task_workers": active, "receipts": receipts,
              "setup_actual_cpu_with_children": setup["cpu_seconds"], "setup_aggregate_watchdog_implemented": False,
              "frozen_protocol_sha256": sha(ROOT / CONFIG), "all_frozen_source_hashes_verified": True,
              "main_campaigns": 2496, "ablation_campaigns": 576, "campaign_canary": 52,
              "reexecution": 52, "actual_campaign_executions": results["actual_campaign_executions"],
              "diagnostic_cases": 576, "diagnostic_canary": 12, "final_outcome_files": 0,
              "source_sha256": sha(Path(__file__)), "preservation_status": "PENDING_FULL_LOCAL_RETURN_AND_VERIFICATION"}
    write_new(ROOT / PACKET / "execution-audit-v1.json", report)
    print(json.dumps({k: v for k, v in report.items() if k not in ("receipts", "analysis_cpu_inside_allowances")}))


if __name__ == "__main__":
    main()
