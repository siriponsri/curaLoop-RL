"""Release the exact approved LR-D23 plan with a new clock and private root."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import TASK, new, now, read, sha


def main():
    assert not TASK.exists(), "PRESERVE_ANY_EXISTING_LR_D23_ROOT"
    proposal = ROOT / "research/configs/lr_d23_proposal_20261109_v1.json"
    config = read(proposal)
    assert config["status"] == "PROPOSED_NOT_RELEASED" and not config["execution_enabled"]
    assert sum(r["units"] * r["seconds_per_unit"] for r in config["allocations"]) == 59400
    previous = read(ROOT / "docs/evidence/m2-diagnostics-20261109-v1/preservation-pins-v1.json")["pins"]
    assert all(sha(ROOT / name) == value for name, value in previous.items())
    pins = {str(p.relative_to(ROOT)).replace("\\", "/"): sha(p) for p in (ROOT / ".local").glob("*/ledger.json")}
    start = now()
    release = {
        "schema": "curaloop.lr_d23.release.v1", "owner_instruction": "อนุมัติ goal long run",
        "base_commit": "36f3812fe2633eb170b554813fa6df987567a539",
        "release_utc": start.isoformat(), "deadline_utc": (start + timedelta(hours=72)).isoformat(),
        "cpu_cap_seconds": 86400, "elapsed_hours": 72, "max_combined_workers": 4,
        "local_workers": 1, "remote_workers": 3,
        "plan": config["plan"], "plan_sha256": sha(ROOT / config["plan"]),
        "proposal_sha256": sha(proposal), "prior_ledger_pins": pins,
        "full_development_training_with_outer_fold_isolation": True,
        "D3_only_after_D2_gate": True, "final_feature_label_presence_open": False,
        "conditional96h_activated": False, "new_dataset_intake": False,
        "actual_product_integration": False, "journal_submission": False,
        "normal_main_commit_push_at_closure": True,
    }
    TASK.mkdir(parents=True, exist_ok=False)
    new(TASK / "release.json", release)
    new(ROOT / "research/manifests/lr_d23_release_20261109_v1.json", release)
    new(TASK / "preservation-pins-v1.json", {"pins": previous, "prior_ledgers": pins})
    new(TASK / "ledger.json", {
        "schema": "curaloop.lr_d23.ledger.v1", "status": "ACTIVE",
        "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
        "cpu_cap_seconds": 86400, "retained_seconds": {"utilities_handoff": 6000},
        "stage_caps": {r["stage"]: r["units"] * r["seconds_per_unit"] for r in config["allocations"]},
        "bookings": {}, "development_labels_decoded": False, "final_outcomes_open": False,
        "D2_gate": "NOT_EVALUATED", "D3": "NOT_STARTED",
    })
    print({"status": "LR_D23_RELEASED", "deadline_utc": release["deadline_utc"], "old_ledgers_pinned": len(pins)})


if __name__ == "__main__":
    main()
