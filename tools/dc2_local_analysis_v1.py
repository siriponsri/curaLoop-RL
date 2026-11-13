"""Descriptive software/admission results only; no invented comparative estimate."""
import csv
import json
from pathlib import Path

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, read, sha, write


def main():
    model = read(PUBLIC / "product-model-acceptance-v1.json")
    native = read(PUBLIC / "native-admission-final-v1.json")
    freeze = read(PUBLIC / "product-acceptance-freeze-v1.json")
    rows = []
    for case in model["cases"]:
        calls = case["result"]["provider_calls"]
        rows.append({"case": case["id"], "status": case["result"]["state"], "software_pass": case["pass"], "selected_count": len(case["actual_selected_ids"]), "provider_attempts": len(calls), "generated_tokens": sum(c.get("tokens", 0) or 0 for c in calls), "observed_wall_seconds": round(case["wall_seconds"], 3)})
    output = PUBLIC / "tables-v2"
    output.mkdir(exist_ok=False)
    with (output / "author-model-cases.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    native_rows = [{"task_id": r["instance_id"], "role": r["role"], "lineage_group": r["lineage_group"], "reference_qualified": r["native_success"], "last_qualifying_or_final_reference_cpu_seconds": r["observed_cpu_seconds"], "agent_evaluation": "NOT_RUN"} for r in native["results"]]
    with (output / "native-reference-admission.csv").open("x", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=native_rows[0].keys())
        writer.writeheader()
        writer.writerows(native_rows)
    receipts = [read(TASK / "provider-calls" / c["call_id"] / "response.json") for case in model["cases"] for c in case["result"]["provider_calls"]]
    gpu_verified = all(any(m["size_vram"] > 0 for m in r["running_model_metadata"]["models"]) for r in receipts)
    assert gpu_verified
    lease = read(TASK / "ledger.json")["bookings"]["product-acceptance-v1"]
    summary = {"scope": "Descriptive author software acceptance; not population inference", "author_cases_passed": sum(r["software_pass"] for r in rows), "author_cases_attempted": len(rows), "deterministic_conformance_passed": sum(c["pass"] for c in model["deterministic_cases"]), "deterministic_conformance_attempted": len(model["deterministic_cases"]), "actual_product_provider_attempts": sum(r["provider_attempts"] for r in rows), "actual_product_generated_tokens": sum(r["generated_tokens"] for r in rows), "actual_case_wall_seconds": [r["observed_wall_seconds"] for r in rows], "retained_model_lease_cpu_seconds": lease["cpu_cap"], "retained_model_lease_gpu_seconds": model["stop"]["retained_gpu_seconds"], "all_product_responses_gpu_resident": gpu_verified, "actual_prompt_tokens": sum(r["response"].get("prompt_eval_count", 0) for r in receipts), "model_stop": model["stop"], "external_comparison": "NOT_RUN", "primary_effect": None, "primary_effect_status": "NOT_ESTIMABLE", "confidence_interval": "NOT_ESTIMABLE_NO_COMPARATIVE_SAMPLE", "uncertainty_note": "Six author-selected related bilingual cases, one attempt each; no sampling interval or seed variance inferred", "source_sha256": {"product": sha(PUBLIC / "product-model-acceptance-v1.json"), "native": sha(PUBLIC / "native-admission-final-v1.json"), "freeze": sha(PUBLIC / "product-acceptance-freeze-v1.json")}}
    write(PUBLIC / "descriptive-analysis-v1.json", summary)
    text = "# Actual local-workflow results\n\nAuthor engineering acceptance only. External agent comparison: **NOT_RUN**. Primary effect: **NOT_ESTIMABLE**.\n\n"
    text += f"Frozen model cases: **{summary['author_cases_passed']}/{len(rows)}**. Actual deterministic conformance: **{summary['deterministic_conformance_passed']}/3**. Product provider attempts: **{summary['actual_product_provider_attempts']}**; generated tokens: **{summary['actual_product_generated_tokens']}**. No mock responses, automatic deterministic fallback or outcome-driven repeated cases.\n\n"
    text += "| Frozen case | State | Selected | Calls | Generated tokens | Observed wall (s) |\n| --- | --- | ---: | ---: | ---: | ---: |\n"
    for r in rows:
        text += f"| {r['case']} | {r['status']} | {r['selected_count']} | {r['provider_attempts']} | {r['generated_tokens']} | {r['observed_wall_seconds']:.3f} |\n"
    text += "\nCase wall time covers queue/model/tool/validation polling, in a fixed sequential order, with a cold first model request and later warm requests. It is not a controlled EN-versus-TH or method timing comparison. Cases are author-selected paired translations; no population confidence interval is justified. Generated-token totals exclude prompt tokens and the separate seven-token technical canary. Conservative resource reservations are not measured compute use.\n\n"
    text += "Native admission: one development reference, six evaluation candidates, three evaluation repository groups against a minimum of four. This fails readiness; it is not an agent method failure result. All proposed research controls and ablations remain NOT_RUN.\n"
    (ROOT / "docs/07_publication/LOCAL_WORKFLOW_ACTUAL_RESULTS_20261113.md").write_text(text, encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("model_stop", "source_sha256")}))

if __name__ == "__main__":
    main()
