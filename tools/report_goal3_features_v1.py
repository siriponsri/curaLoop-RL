"""Publish structure-only counts/hashes, never rows or assay outcomes."""

import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/feature-cohort-v1"
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"


def main():
    source = RAW / "manifest.json"
    manifest = json.loads(source.read_text())
    resources = json.loads((RAW / "resources.json").read_text())
    attempts = manifest["all_attempts"]
    rows = []
    for row in manifest["selected_assays"]:
        rows.append(
            {
                key: row[key]
                for key in (
                    "assay_id",
                    "role",
                    "source_role",
                    "family_id",
                    "family",
                    "feature_sha256",
                    "retained_structures",
                    "member_sha256",
                )
            }
        )
    report = {
        "status": manifest["status"],
        "manifest_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_identities": manifest["identities"],
        "selected_family_counts": manifest["selected_family_counts"],
        "selected_assay_counts": manifest["selected_assay_counts"],
        "attempted_assays": len(attempts),
        "attempted_families": dict(
            Counter({(r["role"], r["family_id"]): r["role"] for r in attempts}.values())
        ),
        "processing_totals": manifest["processing_totals"],
        "selected_task_manifest": rows,
        "resource_receipt": resources,
        "outcome_values_emitted": False,
        "semantic_outcome_use": False,
        "goal4_data_gate": "FAIL_REQUIRED_4_DEVELOPMENT_2_VALIDATION_12_FINAL_GROUPS",
        "new_campaigns_run": 0,
        "final_evaluation": False,
        "terms_notice": "See docs/03_research/PLAN_A_DATA_SOURCE_NOTICES_V1.md; software MIT does not replace data terms",
    }
    output = PACKET / "feature-cohort-v1-result.json"
    with output.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    audit_source = RAW / "chemical-audit.json"
    with (PACKET / "chemical-audit-v1.json").open("xb") as handle:
        handle.write(audit_source.read_bytes())
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "status",
                    "selected_family_counts",
                    "selected_assay_counts",
                    "attempted_assays",
                    "attempted_families",
                )
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
