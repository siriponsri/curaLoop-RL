"""Freeze the failed admission gate and publish only non-answer audit metadata."""
import csv
import json
from collections import defaultdict
from tools.sc1_control_v1 import ACCOUNT, PUBLIC, RELEASE, ROOT, digest, write_new
from tools.sc1_job_v1 import save


def main():
    versions = {}
    for version in (1, 2):
        path = ACCOUNT / f"native-admission-v1/native-qualify-remote-v{version}.json"
        record = json.loads(path.read_text())
        worker = record["worker_result"]
        results = worker["validation_native_results"]
        main = defaultdict(list)
        for item in results:
            main[item["step_id"].split(".")[0]].append(item["status"] == "PASS")
        versions[str(version)] = {"passed_subproblems": sum(r["status"] == "PASS" for r in results), "total_subproblems": len(results),
            "passed_main_problems": sum(all(states) for states in main.values()), "total_main_problems": len(main),
            "failed_step_ids": [r["step_id"] for r in results if r["status"] != "PASS"], "raw_receipt_sha256": digest(path),
            "container_exit_code": record["state"]["ExitCode"], "container_wall_seconds": record["wall_seconds"]}
        write_new(PUBLIC / f"native-qualification-v{version}.json", record)
    with (PUBLIC / "validation-reference-checks-v1.csv").open("x", newline="", encoding="utf-8") as stream:
        output = csv.DictWriter(stream, fieldnames=["technical_attempt", "step_id", "status", "returncode", "wall_seconds"])
        output.writeheader()
        for version in (1, 2):
            for item in json.loads((ACCOUNT / f"native-admission-v1/native-qualify-remote-v{version}.json").read_text())["worker_result"]["validation_native_results"]:
                output.writerow({"technical_attempt": version, **item})
    fixture_metadata = json.loads((ACCOUNT / "native-admission-v1/native-qualify-remote-v2.json").read_text())["worker_result"]["test_fixture_metadata"]
    source = ACCOUNT / "source-intake-v1/receipt.json"
    numeric = ACCOUNT / "numeric-download-v1.json"
    write_new(PUBLIC / "source-intake-v1.json", json.loads(source.read_text()))
    write_new(PUBLIC / "numeric-intake-v1.json", json.loads(numeric.read_text()))
    result = {"schema": "curaloop.lr-sc1.gate1.v1", "status": "NO_GO_NATIVE_EVALUATOR_READINESS",
              "gate0": "PASS_BOUNDED_EMPIRICAL_DISTINCTION", "native_technical_attempts": versions,
              "technical_repair_limit": 1, "technical_repairs_used": 1, "further_research_runs_authorized_in_this_goal": False,
              "native_reference_failure_remaining": "70.8: AssertionError in unchanged native predicate",
              "remaining_failure_cause": "UNRESOLVED_REFERENCE_TARGET_ENVIRONMENT_DISCORDANCE",
              "universal_dataset_defect_proven": False,
              "test_main_fixture_group_coverage": sum(r["fixture_groups_complete"] for r in fixture_metadata),
              "test_main_total": len(fixture_metadata), "native_scoreable_test_cohort": None,
              "native_scoreable_test_cohort_status": "NOT_ESTABLISHED",
              "known_upstream_skip_denominator_cases": ["13.6", "62.1", "76.3"],
              "official_code_revision": "e3158ea011d4235245a547460d3688d7ccbf9900",
              "hf_dataset_revision": "4510f6a6aa27c43fad7b43da2c59602a86e88480",
              "numeric_asset_sha256": json.loads(numeric.read_text())["sha256"],
              "agent_model_calls": 0, "agent_episodes_completed": 0, "agent_matrix_maximum_planned": 520,
              "new_model_download_bytes": 0, "allocated_gpu_seconds": 0,
              "external_comparison": "NOT_RUN", "primary_effect": None, "primary_effect_status": "NOT_ESTIMABLE",
              "test_expected_numeric_values_accessed": False, "test_reference_execution": False,
              "old_final16_private_cf1_hidden_outcomes": "CLOSED",
              "empirical_software_engineering_submission_readiness": "NO_GO_NO_AGENT_COMPARATIVE_EVIDENCE",
              "next_authorized_actions": ["Return and verify owned remote files", "Prepare admission report and manuscript-status note", "Exact owned remote cleanup", "Preservation and delivery audits", "Commit/push main"]}
    write_new(PUBLIC / "gate1-v1.json", result)
    ledger = json.loads((ACCOUNT / "ledger.json").read_text())
    ledger["status"] = "ACTIVE_CLOSEOUT_FAILED_GATE1"
    ledger["failed_gate_record_sha256"] = digest(PUBLIC / "gate1-v1.json")
    save(ACCOUNT / "ledger.json", ledger)
    print(json.dumps({"status": result["status"], "validation_v2": versions["2"], "model_calls": 0, "gpu_seconds": 0}))


if __name__ == "__main__":
    main()
