"""Record the user's fresh D1 release before reading any new diagnostic utility."""
# ruff: noqa: E402 -- repository-only CLI bootstraps the source import path.

import secrets
import sys
from datetime import timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import OLD, TASK, new, now, read, sha


def main():
    assert not TASK.exists(), "PRESERVE_ANY_EXISTING_D1_ROOT"
    pins = read(ROOT / "docs/evidence/m2-diagnostics-20261109-v1/preservation-pins-v1.json")
    assert all(sha(ROOT / name) == expected for name, expected in pins["pins"].items())
    started = now()
    release = {
        "schema": "curaloop.d1.release.v1", "owner_approval": "อนุมัติ D1 ครับ",
        "release_utc": started.isoformat(), "deadline_utc": (started + timedelta(hours=24)).isoformat(),
        "cpu_cap_seconds": 14400, "max_combined_workers": 1,
        "plan": "docs/06_execution/M2_DIAGNOSTIC_PLAN_20261109.md",
        "plan_sha256": sha(ROOT / "docs/06_execution/M2_DIAGNOSTIC_PLAN_20261109.md"),
        "plan_config_sha256": sha(ROOT / "research/configs/m2_diagnostics_plan_20261109_v1.json"),
        "minimum_useful_effect_new_hits_B32": 1.0, "cpu_saving_fraction": 0.20,
        "max_mean_hit_loss_for_saving": 0.25,
        "threshold_interpretation": "owner-approved exploratory engineering preferences; not clinical thresholds",
        "reuse_first": True, "historical_reuse_is_not_independent_replication": True,
        "final_outcomes_open": False, "conditional_96h_activated": False,
        "D2_automatic": False, "M3_automatic": False,
        "old_m2_ledger_sha256": sha(OLD / "ledger.json"),
        "preservation_pins_sha256": sha(ROOT / "docs/evidence/m2-diagnostics-20261109-v1/preservation-pins-v1.json"),
        "new_root": str(TASK.relative_to(ROOT)),
        "no_push_or_external_publication": True,
    }
    TASK.mkdir(parents=True, exist_ok=False)
    new(TASK / "release.json", release)
    new(ROOT / "research/manifests/d1_release_20261109_v1.json", release)
    new(TASK / "ledger.json", {
        "schema": "curaloop.d1.ledger.v1", "status": "ACTIVE",
        "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
        "cpu_cap_seconds": 14400,
        "retained_reservations_seconds": {"utilities_setup_analysis_tests_return_report": 2400},
        "jobs": {}, "final_outcomes_open": False, "scientific_outcome_analysis_started": False,
    })
    for name in ("support", "analysis", "verification", "report"):
        new(TASK / "permits" / (name + ".json"), {
            "attempt": name, "token": secrets.token_hex(16), "host": "local", "cpu": 0,
            "guard_cpu_seconds": 300, "memory_bytes": 4294967296, "wall_seconds": 600,
            "deadline_utc": release["deadline_utc"], "release_utc": release["release_utc"],
            "bundle_sha256": release["plan_sha256"],
            "reservation_bucket": "utilities_setup_analysis_tests_return_report",
        })
    print({"status": "D1_RELEASED", "deadline_utc": release["deadline_utc"], "cpu_cap_seconds": 14400})


if __name__ == "__main__":
    main()
