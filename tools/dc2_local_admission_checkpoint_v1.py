"""Close native admission honestly and continue the approved product fallback."""

from datetime import datetime, timezone

from dc2_local_admin_v1 import PUBLIC, authority, read, save, sha, write


def main():
    release, ledger = authority()
    native = read(PUBLIC / "native-admission-final-v1.json")
    assert native["status"] == "DATA_NOT_READY_APPROVED_FALLBACK_FINAL_ADMISSION"
    assert not any(v["status"] == "RESERVED" for v in ledger["bookings"].values())
    assert ledger["model_calls"] == 1
    assert ledger["retained_cpu_seconds"]["admission"] <= 4 * 3600
    receipt = {
        "status": "NATIVE_ADMISSION_NOT_PASSED_APPROVED_PRODUCT_FALLBACK_ACTIVE",
        "utc": datetime.now(timezone.utc).isoformat(),
        "deadline_utc": release["deadline_utc"],
        "native_admission_sha256": sha(PUBLIC / "native-admission-final-v1.json"),
        "qualified_development_tasks": len(native["development_ids"]),
        "qualified_locked_candidate_tasks": len(native["locked_candidate_ids"]),
        "qualified_locked_repository_lineage_groups": len(
            native["locked_repository_lineage_groups"]
        ),
        "minimum_locked_repository_lineage_groups": 4,
        "scope_of_failure": "Bounded environment/native-reference readiness; not rejection of the method hypothesis or proof that ScienceAgentBench is invalid",
        "primary_agent_comparison": "NOT_RUN",
        "primary_effect": None,
        "native_protocol_or_matrix_frozen": False,
        "old_final16_or_cf1_hidden_outcomes_opened": False,
        "further_benchmark_environment_reference_retries": False,
        "next_authorized_work": "Finish the same real local molecular workflow, author engineering acceptance including real model calls, EN/TH localhost, English guide and feasibility/software manuscript; report the unrun comparison and publication limits",
        "real_model_calls_so_far": 1,
        "real_model_call_scope": "Technical format canary only; not an agent task or efficacy evaluation",
        "retained_cpu_seconds": ledger["retained_cpu_seconds"],
        "retained_gpu_seconds": ledger["retained_gpu_seconds"],
        "prior_retained_cpu_seconds_preserved_separately": 2430,
    }
    write(PUBLIC / "admission-checkpoint-v1.json", receipt)
    write(
        PUBLIC / "source-exposure-register-v1.json",
        {
            "reported_prior_exposure": {
                "task_id": 11,
                "source": "Owner proposal: BBBC002 reference demo in an earlier assistant context",
                "role": "excluded",
            },
            "direct_review_exposure": {
                "task_id": 1,
                "source": "ScienceAgentBench paper v3, Figure 2 ClinTox reference-code snippet displayed while inspecting the paper",
                "role": "already excluded neural-training task; never in the selected eleven-task pool",
            },
            "reference_bodies_processed_programmatically_for_private_qualification": True,
            "private_reference_bodies_or_gold_values_displayed_in_author_context": False,
            "candidate_model_received_reference_or_gold_contents": False,
            "only_model_call_so_far": "Independent technical format canary without benchmark input",
            "whole_benchmark_contamination_claim": False,
            "protected_old_outcomes_opened": False,
        },
    )
    ledger.update(
        status="ACTIVE_PRODUCT_FALLBACK",
        admission_closed=True,
        external_comparative_evaluation_authorized_to_start=False,
        admission_checkpoint_sha256=sha(PUBLIC / "admission-checkpoint-v1.json"),
    )
    save(ledger)
    print(
        {
            "status": ledger["status"],
            "native_cohort": "NOT_PASSED",
            "primary_comparison": "NOT_RUN",
            "next": "Same real local workflow and honest feasibility/software report",
        }
    )


if __name__ == "__main__":
    main()
