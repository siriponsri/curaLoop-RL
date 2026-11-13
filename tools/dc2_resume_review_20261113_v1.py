"""Record explicit resume and attachment review without activating a new study."""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from dc2_admin_v1 import PUBLIC, ROOT, TASK, preserve, read, save, sha, write


def main():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    pause = read(PUBLIC / "owner-pause-v1.json")
    assert ledger["status"] == "PAUSED_OWNER_REQUEST"
    assert sha(TASK / "ledger.json") == pause["ledger_sha256"]
    preserve(release)
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    source = Path(
        "C:/Users/User/Downloads/CuraLoop_Local_Agent_Research_Product_Proposal_2026-11-13.md"
    )
    folder = TASK / "proposal-review-20261113-v1"
    folder.mkdir(exist_ok=False)
    copied = folder / source.name
    copied.write_bytes(source.read_bytes())
    assert sha(source) == sha(copied)
    start = datetime(2026, 11, 13, 11, 51, 7, tzinfo=timezone.utc)
    deadline = start + timedelta(hours=168)
    amendment = {
        "schema": "curaloop.lr-dc2.resume-review.v1",
        "status": "OWNER_RESUMED_READ_AND_RECONCILE_NEW_PROPOSAL",
        "owner_request": "goal resume and read the new proposal first",
        "effective_resume_start_utc": start.isoformat(),
        "effective_resume_deadline_utc": deadline.isoformat(),
        "clock_basis": "First trusted UTC clock after explicit resume; prior owner amendment grants 168 hours from this resume",
        "original_release_sha256": sha(TASK / "release.json"),
        "previous_paused_ledger_sha256": pause["ledger_sha256"],
        "attachment_name": source.name,
        "attachment_sha256": sha(source),
        "attachment_bytes": source.stat().st_size,
        "attachment_instructions_are_execution_authority": False,
        "new_scope_approved": False,
        "current_execution_scope": "Read-only reconciliation and administrative review; no changed study implementation or model/GPU run",
        "cpu_cap_seconds": release["cpu_cap_seconds"],
        "gpu_cap_seconds": release["gpu_allocated_cap_seconds"],
        "retained_cpu_seconds": sum(ledger["retained_cpu_seconds"].values()),
        "retained_gpu_seconds": sum(ledger["retained_gpu_seconds"].values()),
        "budgets_or_old_bookings_reset": False,
        "old_outcomes_opened": False,
    }
    write(ROOT / "research/manifests/lr_dc2_resume_review_20261113_v1.json", amendment)
    write(PUBLIC / "owner-resume-review-20261113-v1.json", amendment)
    ledger.update(
        status="RESUMED_REVIEW_PENDING_SCOPE_DECISION",
        owner_scope_mode="REVIEW_ONLY_PENDING_SCOPE_DECISION",
        evaluation_clock_state="RUNNING_FROM_EXPLICIT_OWNER_RESUME",
        effective_resume_start_utc=start.isoformat(),
        effective_resume_deadline_utc=deadline.isoformat(),
        resume_review_amendment_sha256=sha(PUBLIC / "owner-resume-review-20261113-v1.json"),
    )
    save(ledger)
    assert ledger["retained_cpu_seconds"] == read(TASK / "ledger.json")["retained_cpu_seconds"]
    print(
        {
            "status": ledger["status"],
            "start_utc": start.isoformat(),
            "deadline_utc": deadline.isoformat(),
            "attachment_sha256": amendment["attachment_sha256"],
            "new_scope_approved": False,
        }
    )


if __name__ == "__main__":
    main()
