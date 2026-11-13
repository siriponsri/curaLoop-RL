"""Final local delivery gate; no model inference or protected scientific-data access."""
import json
import re
import sys

from dc2_local_admin_v1 import PUBLIC, ROOT, TASK, authority, read, sha, write


def main():
    release, ledger = authority()
    allowed_self = "local-workflow-delivery-audit-v1"
    assert not any(b["status"] == "RESERVED" and identity != allowed_self for identity,b in ledger["bookings"].items())
    assert "58 passed" in (TASK / "jobs/local-workflow-final-api-regression-v1/stdout.txt").read_text(encoding="utf-8")
    for name in ("local-workflow-final-api-regression-v1", "local-workflow-browser-v5", "product-model-author-acceptance-v1", "product-model-saved-browser-v1", "public-workflow-reproduction-v1", "offline-software-reproduction-v1"):
        assert ledger["bookings"][name]["status"] == "PASS", name
    for path, expected in read(PUBLIC / "product-acceptance-freeze-v1.json")["source_sha256"].items():
        assert sha(ROOT / path) == expected, path
    assert read(PUBLIC / "model-product-browser-v1.json")["same_revisions"]
    assert read(PUBLIC / "owned-cleanup-v2.json")["remote_root_absent"]
    assert read(PUBLIC / "full-remote-return-v1.json")["local_all_files_reread"]
    assert read(PUBLIC / "frontend-source-lint-v1.json")["status"] == "PASS"
    assert read(PUBLIC / "document-visual-review-v1.json")["status"] == "PASS_AUTHOR_ALL_PAGES_AND_FIGURE_REVIEW"
    assert len(read(PUBLIC / "product-provider-calls-v1.json")["calls"]) == 12
    index = (ROOT / "frontend/dist/index.html").read_text(encoding="utf-8")
    for path in re.findall(r'(?:src|href)="(/assets/[^\"]+)"',index):
        assert (ROOT / "frontend/dist" / path.lstrip("/")).is_file(), path
    for link in ("docs/manual/CuraLoop-Local-Molecular-Workflow-Guide-EN-v3.pdf", "docs/07_publication/CuraLoop-Local-Workflow-Feasibility-EN-v2.pdf", "examples/local-workflow/request.json"):
        assert (ROOT / link).is_file(), link
    cpu, gpu = sum(ledger["retained_cpu_seconds"].values()), sum(ledger["retained_gpu_seconds"].values())
    assert cpu <= release["cpu_cap_seconds"] and gpu <= release["gpu_allocated_cap_seconds"]
    output = {"status":"PASS_DELIVERY_READY_ACCOUNT_CLOSE_PENDING", "scope":"Author checks; independent expert/user/clinical validation not claimed", "component_api_tests":58,"actual_model_cases":"6/6","product_provider_responses":12,"external_comparison":"NOT_RUN","primary_effect":None,"primary_effect_status":"NOT_ESTIMABLE","publication_readiness":"FEASIBILITY_SOFTWARE_REPORT_ONLY_NOT_SUPERIOR_METHOD_READY","original_final16_private_cf1_hidden_outcomes":"CLOSED","old_preservation_pins":"PASS_ALL_CURRENT_RAW_IDENTITIES","retained_cpu_seconds":cpu,"retained_cpu_hours":cpu/3600,"retained_gpu_seconds":gpu,"retained_gpu_hours":gpu/3600,"prior_cpu_hours_separate":.675,"resource_accounting":"Conservative retained reservations, including failed attempts; not measured aggregate CPU/GPU usage","owned_remote_persistent_file_return":"PASS_39565_FILES","exact_owned_remote_cleanup":"PASS","shared_models_other_projects":"PRESERVED","paid_api_deployment_submission":"NONE","source_package_sha256":read(PUBLIC / "product-acceptance-freeze-v1.json")["source_sha256"]}
    write(PUBLIC / "delivery-readiness-audit-v1.json",output)
    print(json.dumps(output))


if __name__ == "__main__":
    main()
