"""Format verified metadata/aggregate tables locally; no scientific fitting."""

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    packet = ROOT / "docs/evidence/goal4r1-20261105-v1"
    audit = json.loads((packet / "execution-audit-v1.json").read_text())
    proof = json.loads((packet / "local-full-return-verification-v1.json").read_text())
    absence = json.loads((packet / "remote-absence-v1.json").read_text())
    snapshot = json.loads((packet / "remote-full-snapshot-v1.json").read_text())
    preflight = json.loads((packet / "return-preflight-completion-v1.json").read_text())
    if proof["status"] != "PASS_LOCAL_ALL_FILES_VERIFIED" or not absence["status"].startswith("PASS"):
        raise ValueError("Preservation/absence gates incomplete.")
    changes = []
    for r in audit["receipts"]:
        finish = datetime.fromisoformat(r["finish_utc"])
        begin = finish - timedelta(seconds=r["wall_seconds"])
        changes.extend(((begin, 1), (finish, -1)))
    active = maximum = 0
    for _, value in sorted(changes, key=lambda r: (r[0], r[1])):
        active += value
        maximum = max(maximum, active)
    if maximum > 4:
        raise ValueError("Observed worker overlap exceeds four.")
    known_extra = {"D1": 0., "D3": proof["verification_cpu_seconds"] + snapshot["snapshot_cpu_seconds"] + preflight["cpu_seconds"]}
    for r in audit["analysis_cpu_inside_allowances"]:
        known_extra[r["stage"]] += r["actual_cpu_seconds"]
    if any(known_extra[k] > audit["utility_allowances_seconds"][k] for k in known_extra):
        raise ValueError("Known preservation/analysis CPU exceeds utility reserve.")
    charge = audit["conservative_total_charge_seconds"]
    result = {"status": "PASS_BOUNDED_EXECUTION_PRESERVATION_AND_ABSENCE", "utc": datetime.now(timezone.utc).isoformat(),
              "conservative_charged_seconds": charge, "conservative_charged_cpu_hours": charge / 3600,
              "cap_cpu_hours": 8, "recorded_worker_cpu_seconds": sum(audit["phase_actual_worker_cpu_seconds"].values()),
              "known_cpu_inside_utility_allowances": known_extra, "utility_allowances_seconds": audit["utility_allowances_seconds"],
              "actual_guarded_worker_overlap_max": maximum,
              "exact_exhaustive_host_cpu_accounting": "NOT_CERTIFIED; conservative utility allowances remain charged",
              "local_verification": "PASS", "all_regular_files_returned": proof["file_count"],
              "bytes": proof["bytes"], "remote_absence_status": absence["status"], "remote_absence_utc": absence["utc"],
              "scientific_compute_host": "dr-train", "local_work": "Preparation, metadata formatting, byte verification and one transport engineering regression",
              "final_outcomes_used": False, "gpu_or_new_paid_service_used": False}
    with (packet / "budget-closeout-v1.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    table = json.loads((packet / "results-v1.json").read_text())["method_cells"]
    fields = ["arm", "operation_role_provenance", "campaigns", "H", "policy_cpu", "policy_wall", "optional_waits", "campaigns_with_fallback"]
    with (packet / "method-cells-v1.csv").open("x", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(table)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
