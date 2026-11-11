"""Record explicit owner steering without changing an earlier release's bytes."""

from datetime import datetime, timezone

from dc2_admin_v1 import PUBLIC, ROOT, TASK, preserve, read, save, sha, write


def main():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    preserve(release)
    assert ledger["status"] == "ACTIVE_ADMISSION"
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    before = sha(TASK / "release.json")
    receipt = {"schema": "curaloop.lr-dc2.owner-clock-amendment.v1",
        "status": "OWNER_APPROVED_DATASET_THEN_PAUSE_AND_RESUME_BASED_CLOCK",
        "recorded_utc": datetime.now(timezone.utc).isoformat(), "original_release_sha256": before,
        "owner_instruction_source": "Current conversation: finish dataset download then pause; seven days begin at the next owner resume",
        "effective_scope_until_pause": "Dataset intake/integrity and administrative handoff only",
        "evaluation_clock_state": "AWAITING_OWNER_RESUME", "effective_resume_start_utc": None,
        "effective_resume_deadline_utc": None, "elapsed_hours_from_next_owner_resume": 168,
        "cpu_cap_seconds_unchanged": release["cpu_cap_seconds"],
        "gpu_cap_seconds_unchanged": release["gpu_allocated_cap_seconds"],
        "pre_pause_consumption_and_reservations_retained": True, "cpu_gpu_budget_reset": False,
        "original_release_rewritten": False, "new_model_or_gpu_job_started": False}
    write(ROOT / "research/manifests/lr_dc2_owner_clock_amendment_20261111_v1.json", receipt)
    write(PUBLIC / "owner-clock-amendment-v1.json", receipt)
    ledger.update(owner_scope_mode="DATASET_INTAKE_THEN_PAUSE", evaluation_clock_state="AWAITING_OWNER_RESUME",
                  effective_resume_start_utc=None, effective_resume_deadline_utc=None,
                  clock_amendment_sha256=sha(PUBLIC / "owner-clock-amendment-v1.json"))
    save(ledger)
    assert sha(TASK / "release.json") == before
    print("Recorded explicit owner clock amendment; 168 hours start on next resume, no CPU/GPU reset")


if __name__ == "__main__":
    main()
