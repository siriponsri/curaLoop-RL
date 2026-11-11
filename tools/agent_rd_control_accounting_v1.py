"""Retain a separate allowance for interactive control overhead, transparently.

Administrative file operations and read-only process observations were not
separately CPU-metered. This is not retroactive enforcement or measured usage.
The original project/stage ceilings and every existing booking remain intact.
"""

from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, TASK, authority, read, reserve, save, sha, write


def main():
    release, before = authority()
    original_sha = sha(TASK / "ledger.json")
    name = "interactive-control-overhead-v1"
    retained = 1800
    reserve(name, "technical_retry", retained, "local-administrative-control",
            ["interactive_authoring_and_read_only_process_observation", "actual_cpu_not_separately_metered"])
    ledger = read(TASK / "ledger.json")
    assert all(ledger["bookings"][key] == value for key, value in before["bookings"].items())
    assert set(ledger["bookings"]) == set(before["bookings"]) | {name}
    assert ledger["retained_seconds"] == {key: value + (retained if key == "technical_retry" else 0)
                                         for key, value in before["retained_seconds"].items()}
    ledger["bookings"][name].update(status="RETAINED_CONTROL_COST_NOT_SEPARATELY_METERED",
        measured_cpu_seconds=None, retrospective_hard_enforcement_claim=False,
        scope="Interactive file authoring and read-only local monitoring; no additional model, test or study worker",
        note="Conservative retained allowance within original budget, not a claim of observed CPU usage")
    save(ledger)
    write(PUBLIC / "interactive-control-accounting-v1.json", {
        "status": "RETAINED_UNMETERED_ADMINISTRATIVE_CONTROL_ALLOWANCE",
        "utc": datetime.now(timezone.utc).isoformat(), "booking": name,
        "retained_cpu_seconds": retained, "observed_cpu_seconds": None,
        "retrospective_hard_enforcement_claim": False,
        "original_ledger_before_sha256": original_sha,
        "original_deadline_utc": release["deadline_utc"],
        "existing_bookings_unchanged": len(before["bookings"]),
        "model_phase_budget_or_clock_reset": False, "new_model_or_study_worker": False,
        "interpretation": "Administrative control CPU was not separately metered. Retained allowance is an accounting provision, not measured consumption or retroactive proof of a hard cap. Substantive model/test jobs have their separate guards and receipts."
    }, True)
    print("Retained 1800 administrative-control CPU seconds within original caps; actual control CPU remains unmeasured")


if __name__ == "__main__":
    main()
