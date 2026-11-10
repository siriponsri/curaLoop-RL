"""Audit completed delivery, close only the fresh account, retain every cap.

audit/close run under the normal bounded local admin job after return and
review. finalize records the settled closed-ledger identity without launching
research work. No historical ledger/result is edited by any mode.
"""

import json
import re
import sys
from datetime import datetime, timezone

from agent_rd_admin_v1 import PUBLIC, ROOT, TASK, read, save, sha, write


def audit():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE"
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert all(sha(ROOT / p) == h for p, h in release["prior_ledger_pins"].items())
    assert all(sha(ROOT / p) == h for p, h in release["frozen_scientific_pins"].items())
    freeze_path = ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json"
    freeze = read(freeze_path)
    assert sha(freeze_path) == "5b70e5f1454e9062441b3e292a50fab45f9aebe73ed7994971c6a88de2ad4c8e"
    assert all(sha(ROOT / p) == h for p, h in freeze["pins"].items())
    assert sum(ledger["retained_seconds"].values()) <= release["cpu_cap_seconds"]
    assert all(value <= ledger["stage_caps_seconds"][bucket] for bucket, value in ledger["retained_seconds"].items())
    requirements = {
        "reproducibility-replay-v1.json": "PASS_READ_ONLY_FROZEN_SCORE_AND_ANALYSIS_REPLAY",
        "complete-remote-return-v1.json": "PASS_COMPLETE_RETURN_AND_FULL_FILE_REREAD",
        "owned-remote-cleanup-v1.json": "PASS_EXACT_OWNED_CLEANUP_AFTER_VERIFIED_RETURN",
        "fresh-remote-absence-v1.json": "PASS_FRESH_OWNED_ABSENCE",
        "manual-visual-review-v1.json": "PASS_AUTHOR_RENDERED_PAGE_REVIEW",
        "manuscript-visual-review-v1.json": "PASS_AUTHOR_ALL_PAGE_VISUAL_REVIEW",
        "result-figures-visual-review-v1.json": "PASS_AUTHOR_COLOR_GRAYSCALE_AND_INSERTION_REVIEW",
    }
    for name, expected in requirements.items():
        assert read(PUBLIC / name)["status"] == expected, name
    for name in ("manual-visual-review-v1.json", "manuscript-visual-review-v1.json"):
        record = read(PUBLIC / name)
        assert sha(ROOT / record["pdf"]) == record["pdf_sha256"]
        assert record["pages_reviewed"] == list(range(1, len(record["pages_reviewed"]) + 1))
    figure_review = read(PUBLIC / "result-figures-visual-review-v1.json")
    assert all(sha(ROOT / path) == identity for path, identity in figure_review["files"].items())
    returned_sources = read(PUBLIC / "complete-remote-return-v1.json")["public_exact_executed_worker_sources"]
    assert all(sha(ROOT / path) == identity for path, identity in returned_sources.items())
    analysis = read(PUBLIC / "analysis-v1/analysis.json")
    progress = read(PUBLIC / "locked-progress-v1.json")
    assert progress["attempted_units"] == analysis["attempted"]
    assert len(progress["disposition"]) == analysis["planned"] == 408
    assert analysis["protected_data_access"] is False and analysis["independent_expert_validation"] is False
    assert (analysis["primary"]["exploratory_paired_case_interval_95_pp"] is not None) == (analysis["status"] == "COMPLETE")
    sources = read(PUBLIC / "analysis-v1/source-pins.json")
    assert all(sha(ROOT / path) == value for path, value in sources.items())
    links = []
    documents = [ROOT / "README.md", ROOT / "docs/evidence/agent-rd-20261110-v1/README.md",
                 ROOT / "docs/07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V1.md"]
    for document in documents:
        for target in re.findall(r"\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "mailto:", "#")):
                continue
            target = target.split("#", 1)[0]
            assert (document.parent / target).resolve().exists(), (str(document), target)
            links.append({"document": document.relative_to(ROOT).as_posix(), "target": target})
    receipt = {"status": "PASS_FINAL_REPORT_PRESERVATION_RESOURCE_AND_LOCAL_LINK_AUDIT",
               "prior_ledger_identities_preserved": len(release["prior_ledger_pins"]),
               "old_scientific_pins_preserved": len(release["frozen_scientific_pins"]),
               "new_frozen_pins_preserved": len(freeze["pins"]), "matrix_status": analysis["status"],
               "attempted": analysis["attempted"], "planned": analysis["planned"],
               "verified_required_receipts": {name: sha(PUBLIC / name) for name in requirements},
               "local_links_checked": len(links), "local_links": links,
               "retained_cpu_seconds": dict(ledger["retained_seconds"]),
               "retained_total_cpu_seconds": sum(ledger["retained_seconds"].values()),
               "authorized_total_cpu_seconds": release["cpu_cap_seconds"], "original_deadline_utc": release["deadline_utc"],
               "final16_access": False, "private_compound_row_access": False, "hidden_outcome_access": False,
               "paid_api": False, "gpu": False, "public_deployment": False, "external_tool_writes": False,
               "manuscript_submission": False, "independent_expert_validation": False,
               "review_scope": "Project self-checks, actual model computation and rendered authoring review only",
               "utc": datetime.now(timezone.utc).isoformat()}
    write(PUBLIC / "final-audit-v1.json", receipt, True)
    print(json.dumps({"status": receipt["status"], "matrix_status": analysis["status"], "retained_total": receipt["retained_total_cpu_seconds"]}))


def close():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE"
    assert read(PUBLIC / "final-audit-v1.json")["status"] == "PASS_FINAL_REPORT_PRESERVATION_RESOURCE_AND_LOCAL_LINK_AUDIT"
    assert read(PUBLIC / "fresh-remote-absence-v1.json")["status"] == "PASS_FRESH_OWNED_ABSENCE"
    reserved = {name for name, booking in ledger["bookings"].items() if booking["status"] == "RESERVED"}
    assert reserved == {"remote-model-envelope-v1", "close-agent-rd-account-v1"}, reserved
    retained = dict(ledger["retained_seconds"])
    assert sum(retained.values()) <= release["cpu_cap_seconds"]
    ledger["bookings"]["remote-model-envelope-v1"].update(status="CLOSED_RETURNED_AND_REMOVED",
        note="Full original remote reservations retained, including failed attempts and unknown overhead; no refund/reset")
    ledger.update(status="CLOSED_DELIVERED_COMPUTATIONAL_REPORT", closed_utc=datetime.now(timezone.utc).isoformat(),
                  scientific_matrix_status=read(PUBLIC / "analysis-v1/analysis.json")["status"],
                  final_audit_sha256=sha(PUBLIC / "final-audit-v1.json"))
    save(ledger)
    assert read(TASK / "ledger.json")["retained_seconds"] == retained
    write(PUBLIC / "account-closure-v1.json", {"status": ledger["status"], "closed_utc": ledger["closed_utc"],
          "retained_cpu_seconds": retained, "retained_total_cpu_seconds": sum(retained.values()),
          "authorized_cap_cpu_seconds": release["cpu_cap_seconds"], "unused_allowance_not_released": True,
          "refund_or_clock_reset": False, "original_deadline_utc": release["deadline_utc"],
          "parent_closure_job_settlement": "Recorded separately after this bounded process exits",
          "historical_ledgers_changed": False, "scientific_success_claim": False}, True)
    print("Closed only the new AgentRD account; every reservation and historical ledger remains preserved")


def finalize():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "CLOSED_DELIVERED_COMPUTATIONAL_REPORT"
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    assert ledger["bookings"]["close-agent-rd-account-v1"]["status"] == "PASS"
    assert all(sha(ROOT / p) == h for p, h in release["prior_ledger_pins"].items())
    write(PUBLIC / "settled-account-identity-v1.json", {"status": "PASS_CLOSED_ACCOUNT_FULLY_SETTLED",
          "ledger_sha256": sha(TASK / "ledger.json"), "retained_total_cpu_seconds": sum(ledger["retained_seconds"].values()),
          "all_bookings_settled": True, "historical_ledgers_preserved": len(release["prior_ledger_pins"]),
          "closure_job_resource_sha256": ledger["bookings"]["close-agent-rd-account-v1"]["resource_sha256"],
          "control_operation_only": True, "new_research_or_model_work": False}, True)
    print("Recorded final settled account identity; no research work or new allowance started")


if __name__ == "__main__":
    assert sys.argv[1] in ("audit", "close", "finalize")
    {"audit": audit, "close": close, "finalize": finalize}[sys.argv[1]]()
