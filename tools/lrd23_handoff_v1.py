"""Aggregate-only card, accounting and figure QA inputs for the closed candidate."""
# ruff: noqa: E402

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import PUBLIC, TASK, new, read, sha, utility_finish, utility_start


def main():
    import jsonschema
    from PIL import Image

    aggregate_path = PUBLIC / "D2-aggregate-v1.json"
    result, audit, ledger = read(aggregate_path), read(PUBLIC / "closure-audit-v1.json"), read(TASK / "ledger.json")
    assert audit["status"] == "PASS_COMPLETE_CLOSURE_AUDIT" and result["status"] == "INCONCLUSIVE_D2"
    target = ROOT / "research/product_handoffs/lr_d23_v1"
    card = {
        "schema": "curaloop.lr_d23.evidence_card.v1", "research_status": result["status"],
        "D3_status": ledger["D3_status"], "evaluation_scope": "six exposed FS-Mol development assays / four annotation components",
        "result": {"path": aggregate_path.relative_to(ROOT).as_posix(), "sha256": sha(aggregate_path)},
        "comparisons": [{"arm": arm, "mean_new_positives": values["new_positives"],
                         "mean_scientific_cpu_seconds": values["scientific_cpu_seconds"]} for arm, values in result["means"].items()],
        "decision": {
            "en": "The residual candidate did not meet D2 criteria. D3 was not run. Keep all controls visible; await owner review before a new research or integration phase.",
            "th": "วิธี residual ยังไม่ผ่านเกณฑ์ D2 จึงไม่ได้รัน D3 ให้แสดงผลของ baseline ทุกตัว และรอเจ้าของโครงการตัดสินใจก่อนเริ่มงานวิจัยหรือเชื่อมระบบใน phase ใหม่"},
        "limitations": ["Previously exposed development evidence, not final validation.",
                        "Four annotation components are not certified independent biological families.",
                        "Intervals resample five joint seeds conditional on the same six assays.",
                        "Scientific CPU excludes offline training and is not a laboratory cost saving.",
                        "Random was not assigned in this experiment; app demonstrations are separate evidence.",
                        "No runtime integration, clinical efficacy, customer benefit or commercial-data clearance is established."],
        "runtime_integration": "NOT_RUN_OFFLINE_HANDOFF_ONLY",
    }
    jsonschema.Draft202012Validator.check_schema(read(target / "evidence-card.schema.json"))
    jsonschema.validate(card, read(target / "evidence-card.schema.json"))
    new(target / "evidence-card-v1.json", card)
    rejected = dict(card, compound_labels=[True])
    try:
        jsonschema.validate(rejected, read(target / "evidence-card.schema.json"))
    except jsonschema.ValidationError:
        pass
    else:
        raise AssertionError("CARD_ACCEPTED_UNDECLARED_LABEL_PAYLOAD")
    new(PUBLIC / "product-card-validation-v1.json", {"status": "PASS_AGGREGATE_ONLY_SCHEMA_AND_NEGATIVE_BOUNDARY",
        "schema_sha256": sha(target / "evidence-card.schema.json"), "card_sha256": sha(target / "evidence-card-v1.json"),
        "undeclared_label_payload_rejected": True, "runtime_integration": "NOT_RUN"})
    claims = {
        "superior_discovery_compute_tradeoff": "NOT_SUPPORTED_Gk2_MEAN_POINT_DOMINATES",
        "history_features_add_useful_value": "NOT_SUPPORTED",
        "reduced_scientific_CPU_vs_G1": "OBSERVED_WITH_HIT_LOSS_OUTSIDE_PREFERENCE",
        "two_training_rounds_executed": "PASS",
        "D3_broad_transfer": "NOT_RUN_D2_GATE_NOT_MET",
        "independent_final_generalization": "NOT_RUN_FINAL16_SEALED",
        "product_runtime_acceptance": "NOT_RUN_OFFLINE_HANDOFF_ONLY",
        "clinical_or_laboratory_benefit": "NOT_ESTABLISHED",
        "journal_submission": "NOT_RUN",
    }
    new(PUBLIC / "claim-map-v1.json", {"schema": "curaloop.lr_d23.claims.v1", "claims": claims})
    with (PUBLIC / "primary-results-v1.csv").open("x", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["arm", "mean_new_positives", "mean_scientific_cpu_seconds", "mean_new_deliveries"])
        for arm, values in result["means"].items():
            writer.writerow([arm, values["new_positives"], values["scientific_cpu_seconds"], values["new_deliveries"]])
    with Image.open(ROOT / "docs/assets/research/lr-d23-v1/primary-comparison.png") as image:
        image.resize((673, 451), Image.Resampling.LANCZOS).save(TASK / "primary-comparison-final-size.png")
    with Image.open(TASK / "primary-comparison-grayscale.png") as image:
        image.resize((673, 451), Image.Resampling.LANCZOS).save(TASK / "primary-comparison-final-size-grayscale.png")
    utilities = sum(b.get("guard_cpu_seconds", b.get("aggregate_cpu_seconds", b.get("retained_seconds", 0)))
                    for b in ledger["bookings"].values() if b["bucket"] == "utilities_handoff")
    assert utilities <= 6000
    new(PUBLIC / "budget-accounting-v1.json", {"status": "PASS_RETAINED_ENVELOPES_WITHIN_RELEASE",
        "retained_by_stage_seconds": ledger["retained_seconds"], "retained_total_seconds": sum(ledger["retained_seconds"].values()),
        "retained_total_cpu_hours": sum(ledger["retained_seconds"].values()) / 3600,
        "cap_seconds": 86400, "utility_bucket_seconds": 6000, "utility_individual_envelopes_at_handoff_seconds": utilities,
        "utility_scope": "includes failures, reading, setup, transport, verification, cleanup, figures, tests, report and routine metadata/Git delivery; not a complete measurement of all utility CPU",
        "measured_remote_scientific_worker_process_cpu_seconds": audit["measured_worker_process_cpu_seconds"],
        "measured_experimental_training_cpu_seconds": audit["measured_experimental_training_cpu_seconds"],
        "hypothetical_training_recovery_campaigns_vs_G1": audit["hypothetical_training_recovery_campaigns_vs_G1"],
        "unspent_allowance_released_for_another_study": False})
    new(PUBLIC / "engineering-notes-v1.json", {"scientific_design_changed_after_outcomes": False,
        "notes": ["Historical D1 pool-frame wording corrected by identifier-only equality; original masks/results preserved.",
                  "One pre-outcome Windows signal test stub had a method-signature error; repaired, with original failure retained.",
                  "Two early local utilities briefly overlapped on CPU0 before molecular execution; physical one-core bound held, strict process serialization did not.",
                  "A figure geometry check initially included off-view log ticks; filtered before final render. No metric or gate changed.",
                  "Frozen return adapter retains one I001 import-order warning. Correctness lint and targeted lint with this explicit style exception are reported separately."]})
    print({"status": "PASS_OFFLINE_CARD_AND_HANDOFF_INPUTS", "retained_CPU_hours": sum(ledger["retained_seconds"].values()) / 3600})


if __name__ == "__main__":
    guard = utility_start("handoff-artifacts", 180, 300)
    try:
        main()
        utility_finish("handoff-artifacts", guard, "PASS")
    except BaseException:
        utility_finish("handoff-artifacts", guard, "FAIL")
        raise
