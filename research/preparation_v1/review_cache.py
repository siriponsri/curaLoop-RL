"""Verify pinned outcome-free responses and publish metadata-only adjudication."""

import csv
import hashlib
import json
from datetime import datetime, timezone

from .candidate_audit import PACKET, RAW, project_payload, validate_url

NOTES = {
    1631: (
        "DIRECTION_DISCREPANCY",
        "LIT source index describes inhibition; primary AID title describes PKM2 activation. No label inversion; exact phenotype/release gate stays open.",
    ),
    743094: (
        "DIRECTION_DISCREPANCY_AND_EXPOSED_FAMILY",
        "LIT index describes inhibition; primary AID title describes PPAR-gamma agonism. Earlier project's inhibitor shorthand is not resolved source truth. Same PPARG development family is excluded from final-transfer allocation.",
    ),
    651631: (
        "DIRECTION_DISCREPANCY_AND_EXPOSED_FAMILY",
        "LIT index describes inhibition; primary AID title describes p53 agonism. Same p53 development pathway is excluded from final-transfer allocation.",
    ),
    2101: (
        "MIXED_DIRECTION_AND_MUTANT_CONTEXT",
        "Primary title includes both inhibitors and activators of N370S glucocerebrosidase. Generic GBA inhibition is insufficient endpoint definition.",
    ),
    602179: (
        "MUTANT_CONTEXT_REQUIRED",
        "Primary title specifies mutant IDH1; do not relabel as wild-type IDH1.",
    ),
    493208: (
        "PATHWAY_AND_CELL_CONTEXT_REQUIRED",
        "mTORC1 pathway reporter in Tsc2-/-, p53-/- MEF cells, not a demonstrated direct MTOR binding task; p53-related cellular context must be assessed.",
    ),
    504327: (
        "ALIAS_AND_ENDPOINT_REVIEW",
        "Primary GCN5L2 name is the KAT2A alias; no new independent target is created by that alias.",
    ),
    995: (
        "PATHWAY_ENDPOINT_REVIEW",
        "Primary title names ERK signaling; metadata must support the precise MAPK1 endpoint before final ingestion.",
    ),
    492947: (
        "FUNCTIONAL_BIAS_CONTEXT",
        "Primary ADRB2 assay concerns beta-arrestin-biased ligands; preserve that functional context.",
    ),
    1030: ("ISOFORM_CONTEXT", "Primary ALDH1 title specifies ALDH1A1; preserve the isoform."),
    504847: (
        "UNRESOLVED_VDR_GATE",
        "Primary source uses inhibition; prior main/supplement descriptions differ in antagonism/agonism. Source version and prepared-file mapping remain unresolved.",
    ),
}


def main():
    audit = json.loads((PACKET / "candidate-audit.json").read_text())
    receipts = json.loads((PACKET / "request-receipts.json").read_text())
    assert len(receipts) == 72 and all(r["status"] == "PASS" for r in receipts)
    for receipt in receipts:
        kind = validate_url(receipt["url"])
        raw = (RAW / receipt["raw_file"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == receipt["sha256"]
        project_payload(kind, json.loads(raw))
    rows, details = [], []
    for r in audit["records"]:
        metadata = r["metadata"]
        key = "all_previously_retrieved_NCATS_structures"
        overlap = r["overlaps"][key]
        category, note = NOTES.get(
            r["aid"],
            (
                "CONTEXT_AND_RIGHTS_GATES_OPEN",
                "Metadata/structure audit only; no final role or usable-label count has been established.",
            ),
        )
        rows.append(
            {
                "aid": r["aid"],
                "name": r["short_name"],
                "source_index": r["source_program"],
                "aid_version": metadata["aid"]["version"],
                "description_revision": metadata["revision"],
                "depositor_db_as_supplied": metadata["aid_source"]["db"]["name"],
                "provisional_family": r["provisional_planning_family"],
                "all_unfiltered_cids": r["all_unfiltered_cid_count"],
                "feature_sample_unique": r["sample_valid_unique"],
                "exact_with_all_seen_ncats": overlap["exact_canonical_matches"],
                "near_ge_0_8_with_all_seen_ncats": overlap["queries_nearest_tanimoto_ge_0_8"],
                "exact_with_seen_600_union": r["overlaps"]["three_exposed_600_subsets_union"][
                    "exact_canonical_matches"
                ],
                "exact_with_hiv": r["overlaps"]["HIV_regression_1200"]["exact_canonical_matches"],
                "semantic_review": category,
                "outcomes_inspected": False,
                "final_ready": False,
            }
        )
        details.append(
            {
                "aid": r["aid"],
                "status": category,
                "note": note,
                "source_metadata_url": f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{r['aid']}/description/JSON",
                "review_type": "Source-derived title/context check plus explicit implementer inference; not independent domain adjudication",
            }
        )
    with (PACKET / "candidate-summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "status": "PASS_CACHE_INTEGRITY_WITH_OPEN_SCIENTIFIC_RIGHTS_GATES",
        "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
        "cached_responses_verified": len(receipts),
        "outcome_response_sections_present": 0,
        "final_ready_tasks": 0,
        "semantic_reviews": details,
        "source_rights_review": {
            "NCATS_Tox21": "Provider public-domain statement applies to stated Tox21 data scope; exact response/prepared release and structure-source terms still need closure for a final distribution.",
            "PubChem": "Contributor-specific conditions; no blanket data license inferred. NCGC source page presented reCAPTCHA; no bypass or substitute license claim.",
            "LIT_PCBA": "Provider prepared-file grant not verified; direct download inspection hit local TLS verification failure, which was not disabled. This audit inspected raw source AIDs, not prepared LIT-PCBA molecules/outcomes.",
            "ChEMBL": "Provider states CC BY-SA 3.0; release LICENSE endpoint timed out; no version-specific ChEMBL assay files were ingested.",
        },
        "allocation_options_not_assignments": {
            "development_regression_only": ["HIV", "AhR", "PPARG", "p53"],
            "within_panel_estimation_candidate_aids": [
                r["aid"] for r in audit["records"] if r["source_program"].startswith("NCATS")
            ],
            "broader_validation_proposal": {
                "aldehyde_dehydrogenase": [1030],
                "acetyltransferase": [504327],
            },
            "broader_final_candidate_families_proposal": {
                "GPCR": [492947, 1777],
                "genome_maintenance": [588795],
                "mutant_isocitrate_dehydrogenase": [602179],
                "protein_kinase_pathway": [995, 493208],
            },
            "additional_families_quarantined": {
                "GBA_mutant_dual_direction": [2101],
                "PKM2_direction_discrepancy": [1631],
                "VDR_unresolved": [504847],
            },
            "rules": "Proposals only, not reserved/frozen roles. Group related genes/functional reporters conservatively, assess source/chemical dependence, close rights/phenotype gates first. Final-ready count is zero. 8-12 independent final families would require additional reviewed sources.",
        },
        "exposure": audit["published_aggregate_exposure"],
        "final_protocol_frozen": False,
    }
    (PACKET / "candidate-review.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                k: v
                for k, v in result.items()
                if k not in ("semantic_reviews", "allocation_options_not_assignments")
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
