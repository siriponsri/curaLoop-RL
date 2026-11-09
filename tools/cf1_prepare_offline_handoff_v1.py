"""Emit an honest EN/TH pending evidence card, without runtime integration."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, now, start
from research.confirmation_v1.contracts import GATE_NAMES, validate_report


def main():
    report = {
        "schema": "curaloop.confirmation.offline-report.v1", "status": "WAITING_INPUT",
        "created_utc": now().isoformat(), "estimand": "OBSERVATION_SUPPORTED_PRIMARY_HITS_ONLY",
        "final16_access": False, "new_selector_training": False,
        "gates": dict.fromkeys(GATE_NAMES, False),
        "campaigns_admitted": 0, "campaign_metadata_entries": 17,
        "provisional_cached_target_matches": 8, "source_experiment_blocks": None,
        "metrics": {"confirmed_positives": None, "positive_structure_groups": None},
        "uncertainty": {"estimated": False, "seed_intervals_are_biological_uncertainty": False},
        "integration_status": "OFFLINE_HANDOFF_ONLY",
        "evidence": ["source-inventory-v1.json", "role-review-v1.json", "cached-target-review-v1.json",
                     "remote-preflight-v1.json", "constructed-checks-v1.json"],
        "labels": {
            "en": {
                "title": "Confirmation portfolio evidence", "status": "Waiting for source information",
                "results": "Not run", "population": "Historically confirmed primary hits only",
                "scope": "Retrospective source-defined activity; no whole-library or clinical claim",
                "confirmation_zero": "Source nonpositive: inactive or inconclusive; original state unavailable",
                "missing_confirmation": "Not observed; never filled as inactive",
                "next_step": "Validate Supporting Information and finish campaign admission before fitting baselines",
            },
            "th": {
                "title": "หลักฐานการจัดชุดสารเพื่อยืนยันผล", "status": "รอข้อมูลจากแหล่งต้นฉบับ",
                "results": "ยังไม่ได้รัน", "population": "เฉพาะสารที่ออกฤทธิ์ในการคัดกรองรอบแรกและมีผลยืนยันในอดีต",
                "scope": "การศึกษาย้อนหลังตามนิยามต้นฉบับ ยังไม่สรุปผลต่อทั้งคลังสารหรือผลทางคลินิก",
                "confirmation_zero": "กลุ่มที่ไม่ได้ยืนยันว่าออกฤทธิ์ รวมผลไม่ออกฤทธิ์และผลที่ยังสรุปไม่ได้ โดยแยกสถานะเดิมกลับไม่ได้",
                "missing_confirmation": "ไม่มีผลที่สังเกตได้ ไม่เติมเป็นผลไม่ออกฤทธิ์",
                "next_step": "ตรวจ Supporting Information และการรับแต่ละ campaign เข้าศึกษาให้ครบก่อนฝึก baseline",
            },
        },
    }
    validate_report(report)
    new(TASK / "offline-handoff-v1.json", report)
    new(PUBLIC / "offline-handoff-v1.json", report)
    print("PASS validated offline EN/TH pending card; all unrun metrics null")


if __name__ == "__main__":
    guard = start("offline-handoff-preparation", 120, 300, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("offline-handoff-preparation", guard, "PASS_OFFLINE_PENDING_CARD")
    except BaseException:
        finish("offline-handoff-preparation", guard, "FAIL")
        raise
