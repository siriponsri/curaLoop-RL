"""Record the explicit owner answer without changing the original account."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, authority, finish, new, now, sha, start


def main():
    release, ledger = authority()
    value = {
        "schema": "curaloop.lr_cf1.owner-source-choice.v1", "choice": "A",
        "owner_answer": "A — ใช้ AID + repository พร้อมบันทึกข้อขัดแย้ง (แนะนำ)",
        "recorded_utc": now().isoformat(), "original_release_utc": release["release_utc"],
        "original_deadline_utc": release["deadline_utc"], "cpu_cap_seconds": 172800,
        "source_commit": "04c58e85188e724ec5ff44cbed2e7b960f6f3df3",
        "decision_document_sha256": sha(ROOT / "docs/06_execution/LR_CF1_SOURCE_CONCORDANCE_DECISION_20261109.md"),
        "discrepancy_audit_sha256": sha(PUBLIC / "si-concordance-v2.json"),
        "canonical_campaign_key": "primary_aid/confirmation_aid",
        "eligibility_order": "NUMERIC_PRIMARY_AID_THEN_CONFIRMATION_AID_BEFORE_OUTCOMES",
        "si_aliases_preserved": True, "qualified_processed_repository_reproduction": True,
        "other_admission_gates_waived": False, "author_code_corrected": False,
        "budget_or_deadline_reset": False, "old_ledger_status_changed": False,
        "prior_ledger_pins_unchanged": len(release["prior_ledger_pins"]),
        "retained_upper_cpu_seconds_at_record": sum(ledger["retained_seconds"].values()),
        "final16_access": False, "new_selector_training": False,
    }
    new(TASK / "owner-source-a-v1.json", value)
    new(ROOT / "research/manifests/lr_cf1_source_a_owner_20261109_v1.json", value)
    print("PASS owner A recorded; original account, clock and all other gates retained")


if __name__ == "__main__":
    guard = start("owner-source-a-record", 60, 180, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("owner-source-a-record", guard, "PASS_OWNER_A_RECORDED")
    except BaseException:
        finish("owner-source-a-record", guard, "FAIL")
        raise
