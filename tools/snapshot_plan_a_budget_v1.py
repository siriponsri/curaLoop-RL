"""Account known receipts and explicit conservative reservations, never labels."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    output = ROOT / args.output
    if output.exists() or not output.resolve().is_relative_to(
        ROOT / "docs/evidence/plan-a-20261105-v1"
    ):
        raise ValueError("New evidence receipt path required.")
    sources = []
    names = [
        "source-metadata-v1",
        "uniprot-family-canary-v1",
        "uniprot-family-bulk-v1",
        "uniprot-family-exposure-v1",
        "interpro-types-canary-v1",
        "interpro-types-bulk-v1",
        "interpro-types-resume-v1",
        "interpro-types-finish-v1",
    ]
    for name in names:
        path = RAW / name / "requests.json"
        report = json.loads(path.read_text())
        sources.append(
            {
                "path": str(path.relative_to(ROOT)),
                "measured_cpu_seconds": report["cpu_seconds"],
                "received_body_bytes": sum(r["bytes"] for r in report["requests"]),
            }
        )
    path = RAW / "chembl37-mapping-v1/summary.json"
    report = json.loads(path.read_text())
    sources.append(
        {
            "path": str(path.relative_to(ROOT)),
            "measured_cpu_seconds": report["cpu_seconds"],
            "received_body_bytes": report["payload_bytes"],
        }
    )
    for path in sorted(RAW.glob("interpro-ftp-*/receipt.json")):
        report = json.loads(path.read_text())
        sources.append(
            {
                "path": str(path.relative_to(ROOT)),
                "measured_cpu_seconds": report["cpu_seconds"],
                "received_body_bytes": report["bytes"],
            }
        )
    download = sum(r["received_body_bytes"] for r in sources)
    reservations = {
        "delegated_metadata_unknown_actual_reservation": 80_000_000,
        "partial_buffered_FTP_timeout_read_reservation": 10_000_001,
        "unrecorded_initial_API_disconnect_reservation": 200_001,
        "primary_web_document_reading_reservation": 5_000_000,
    }
    charged = download + sum(reservations.values())
    jobs = []
    job_paths = list(RAW.glob("feature-cohort-*/resources.json"))
    job_paths += list((ROOT / "docs/evidence/plan-a-20261105-v1").glob("*-resources-*.json"))
    job_paths += list(
        (ROOT / "docs/evidence/plan-a-20261105-v1").glob("constructed-all-*-resources.json")
    )
    for path in sorted(job_paths):
        report = json.loads(path.read_text())
        if report.get("schema_version") != "curaloop.resource-receipt.v1":
            raise ValueError("Unexpected resource receipt schema.")
        jobs.append(
            {
                "path": str(path.relative_to(ROOT)),
                "status": report["status"],
                "measured_cpu_seconds": report["cpu_seconds"],
            }
        )
    return_proof = (
        ROOT / "docs/evidence/plan-a-20261105-v1/plan-a-return-local-verification-v2.json"
    )
    if return_proof.exists():
        proof = json.loads(return_proof.read_text())
        jobs.append(
            {
                "path": str(return_proof.relative_to(ROOT)),
                "status": proof["status"],
                "measured_cpu_seconds": proof["verification_cpu_seconds"],
            }
        )
    measured = sum(r["measured_cpu_seconds"] for r in sources) + sum(
        r["measured_cpu_seconds"] for r in jobs
    )
    report = {
        "schema_version": "curaloop.plan-a.budget-snapshot.v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_CONSERVATIVE_CHARGE" if charged <= 200_000_000 else "FAIL_METADATA_BUDGET",
        "cpu_ceiling_seconds": 172800,
        "goal3_cpu_ceiling_seconds": 28800,
        "goal4_cpu_ceiling_seconds": 144000,
        "recorded_goal3_cpu_seconds": measured,
        "unmetered_pre_guard_preflight_utility_test_overhead_charge_seconds": 7200,
        "goal3_charged_cpu_seconds": measured + 7200,
        "cpu_accounting_scope": "Process CPU from available source/job receipts plus conservative charge; exhaustive historical process accounting is not certified",
        "metadata_recorded_body_bytes": download,
        "metadata_unknown_usage_reservations": reservations,
        "metadata_conservative_charged_bytes": charged,
        "metadata_ceiling_bytes": 200_000_000,
        "delegated_request_count_compliance": "NOT_CERTIFIED; see delegated-metadata-accounting.json",
        "reservations_are_not_measured_usage": True,
        "sources": sources,
        "bounded_jobs": jobs,
        "next_preparation_max_cpu_seconds": 1800,
        "new_heavy_jobs_use_affinity_memory_wall_CPU_guards": True,
        "final_evaluation": False,
    }
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: v for k, v in report.items() if k not in ("sources", "bounded_jobs")}, indent=2
        )
    )
    if report["status"].startswith("FAIL"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
