"""Deduplicate process receipts across hosts/copies and retain accounting limits."""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/goal4-20261105-v1"
RETENTION = ROOT / ".local/plan-a-20261105-v1/remote-return/goal4-full-v1"


def main():
    retained = RETENTION / "files"
    candidates = list(PACKET.glob("*resources*.json"))
    candidates += list((retained / ".local/plan-a-20261105-v2").rglob("*resources*.json"))
    candidates += list((retained / "docs/evidence/goal4-20261105-v1").glob("*resources*.json"))
    candidates += [retained / "remote-constructed-resources-v1.json"]
    jobs, copies = {}, []
    for path in candidates:
        data = json.loads(path.read_text())
        if data.get("schema_version") != "curaloop.resource-receipt.v1":
            continue
        if data["status"] == "RUNNING":
            raise ValueError("A job is not terminal; do not finalize budget.")
        key = (data["pid"], data["start_utc"], data["guard_source_sha256"])
        if key in jobs:
            if abs(jobs[key]["cpu_seconds"] - data["cpu_seconds"]) > 1e-9:
                raise ValueError("Conflicting copies of a process receipt.")
            copies.append(path.relative_to(ROOT).as_posix())
            continue
        jobs[key] = {"path": path.relative_to(ROOT).as_posix(), "pid": data["pid"],
                     "start_utc": data["start_utc"], "status": data["status"],
                     "cpu_seconds": data["cpu_seconds"], "wall_seconds": data["wall_seconds"]}
    install = json.loads((retained / "remote-install-v1.json").read_text())
    full_manifest = json.loads((RETENTION / "manifest.json").read_text())
    verification = []
    for name in ("goal4-development-v1", "goal4-full-v1"):
        path = ROOT / ".local/plan-a-20261105-v1/remote-return" / name / "local-verification-with-manifest.json"
        proof = json.loads(path.read_text())
        verification.append({"path": path.relative_to(ROOT).as_posix(), "cpu_seconds": proof["verification_cpu_seconds"]})
    measured = sum(row["cpu_seconds"] for row in jobs.values()) + install["cpu_seconds"] + full_manifest["snapshot_cpu_seconds"] + sum(row["cpu_seconds"] for row in verification)
    base = json.loads((ROOT / "docs/evidence/plan-a-20261105-v1/revision-a-budget-v2.json").read_text())
    charge = measured + 1800
    global_charge = base["goal3_charged_cpu_seconds"] + charge
    now = datetime.now(timezone.utc)
    deadline = datetime(2026, 11, 5, 22, 37, 4, tzinfo=timezone.utc)
    passed = charge < 144000 and global_charge < 172800 and now < deadline
    report = {"status": "PASS_CONSERVATIVE_ACCOUNTING" if passed else "FAIL_RESOURCE_CEILING",
              "created_utc": now.isoformat(), "deadline_utc": deadline.isoformat(),
              "goal3_charged_cpu_seconds": base["goal3_charged_cpu_seconds"],
              "goal4_recorded_cpu_seconds": measured, "goal4_unmetered_utility_overhead_charge_seconds": 1800,
              "goal4_charged_cpu_seconds": charge, "global_charged_cpu_seconds": global_charge,
              "goal4_cpu_ceiling_seconds": 144000, "global_cpu_ceiling_seconds": 172800,
              "new_metadata_primary_code_bytes": 6815,
              "goal3_metadata_charge_bytes": base["metadata_conservative_charged_bytes"],
              "unique_guarded_processes": list(jobs.values()), "duplicate_receipts_not_double_counted": copies,
              "remote_environment_cpu_including_children_seconds": install["cpu_seconds"],
              "remote_full_snapshot_cpu_seconds": full_manifest["snapshot_cpu_seconds"],
              "local_verification_cpu_receipts": verification,
              "full_return_regular_files": full_manifest["file_count"], "full_return_bytes": full_manifest["bytes"],
              "maximum_scientific_workers": 4, "GPU_or_paid_compute": False,
              "exhaustive_historical_process_accounting_certified": False,
              "reserves_are_not_measured_usage": True,
              "accounting_scope": "Available unique process/setup/verification/snapshot receipts plus explicit conservative reserves. Unmetered utility, transfer, mirroring, cleanup and final package operations charged to reserve; early historical metadata limitations remain disclosed."}
    with (PACKET / "budget-closeout-v1.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps({k: report[k] for k in ("status", "goal3_charged_cpu_seconds", "goal4_recorded_cpu_seconds", "goal4_charged_cpu_seconds", "global_charged_cpu_seconds")}, indent=2))
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
