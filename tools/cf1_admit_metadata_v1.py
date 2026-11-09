"""Freeze AID-based eligibility using metadata only, never campaign outcomes."""
# ruff: noqa: E402

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start


def target_binding(description, cached):
    targets = description.get("target_metadata")
    if not isinstance(targets, list) or len(targets) != 1:
        return False
    target = targets[0]
    accession = (target.get("mol_id") or {}).get("protein_accession", "")
    exact = {r["accession_version"] for r in cached["refseq"]}
    direct = re.fullmatch(re.escape(cached["accession"]) + r"(?:\.[1-9][0-9]*)?", accession) is not None
    taxon = ((target.get("organism") or {}).get("org") or {}).get("db", [])
    taxids = {str(r.get("tag", {}).get("id")) for r in taxon if r.get("db") == "taxon"}
    return (direct or accession in exact) and cached["tax_id"] in taxids


def main():
    owner = read(TASK / "owner-source-a-v1.json")
    assert owner["choice"] == "A" and owner["budget_or_deadline_reset"] is False
    assert sha(TASK / "owner-source-a-v1.json") == sha(ROOT / "research/manifests/lr_cf1_source_a_owner_20261109_v1.json")
    assert sha(PUBLIC / "si-concordance-v2.json") == owner["discrepancy_audit_sha256"]
    source = read(TASK / "source-inventory.json")
    assert source["commit"] == owner["source_commit"]
    blobs = {r["path"]: r for r in source["dataset_metadata"]}
    descriptions = {r["aid"]: r for r in read(TASK / "description-review-private-v1.json")["records"]}
    rows = sorted(read(TASK / "cached-target-review-private-v1.json")["records"],
                  key=lambda r: tuple(map(int, r["source_pair"])))
    records, selected = [], []
    for row in rows:
        cached = row["cached_target"]
        verdict = "QUARANTINE_UNRESOLVED_TARGET_ROLE"
        if cached and cached["verdict"] == "NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY":
            ds = [descriptions.get(a) for a in row["source_pair"]]
            if all(d is not None and target_binding(d, cached) for d in ds):
                if all(type(d["project_category_raw"]) is int and d["project_category_raw"] in (1, 2) for d in ds):
                    providers = {d["provider"]["db"]["name"] for d in ds}
                    verdict = "PASS_METADATA_PRECONDITIONS" if len(providers) == 1 else "QUARANTINE_PROVIDER_BINDING"
                else:
                    verdict = "QUARANTINE_PROGRAMME_USE_EVIDENCE"
            else:
                verdict = "QUARANTINE_UNRESOLVED_EXACT_TARGET_VERSION_OR_TAXON"
        entry = {**row, "metadata_verdict": verdict}
        records.append(entry)
        if verdict == "PASS_METADATA_PRECONDITIONS" and len(selected) < 6:
            name = "Datasets/" + row["codename"] + ".csv"
            selected.append({"campaign": "/".join(row["source_pair"]), "primary_aid": row["source_pair"][0],
                "confirmation_aid": row["source_pair"][1], "repository_codename": row["codename"],
                "source_file": name, "source_blob_oid": blobs[name]["sha"], "source_bytes": blobs[name]["size"],
                "target": cached["accession"], "source_experiment_block": ds[0]["provider"]["db"]["name"],
                "annotation_connected_component": cached["family_id"], "role": "DEVELOPMENT_EXPOSED",
                "description_hashes": {d["aid"]: d["source_sha256"] for d in ds}})
    blocks = {r["source_experiment_block"] for r in selected}
    assert 4 <= len(selected) <= 6 and len(blocks) >= 2
    assert sum(r["source_bytes"] for r in selected) < 1073741824
    new(TASK / "metadata-admission-private-v1.json", {"records": records, "selected": selected})
    summary = {"status": "PASS_METADATA_PRECONDITIONS_OPAQUE_INTAKE_ONLY", "utc_source_choice": owner["recorded_utc"],
        "source_commit": source["commit"], "owner_choice_sha256": sha(TASK / "owner-source-a-v1.json"),
        "selection_order": owner["eligibility_order"], "campaign_metadata_count": len(rows), "selected": selected,
        "provider_block_count": len(blocks), "provider_blocks_are_not_biological_independence": True,
        "shared_library_dependence_still_to_report": True,
        "annotation_component_count": len({r["annotation_connected_component"] for r in selected}),
        "aggregate_dispositions": dict(Counter(r["metadata_verdict"] for r in records)),
        "data_rights_scope": "BOUNDED_NONCOMMERCIAL_REANALYSIS_DERIVED_AGGREGATE_REPORT_PREPARATION_WITH_ATTRIBUTION",
        "commercial_or_raw_redistribution_clearance": False, "campaign_values_analyzed": False,
        "confirmation_value_analysis_released": False, "structure_support_resource_gates_remaining": True,
        "si_alias_correction_applied_to_original": False, "final16_access": False}
    new(TASK / "metadata-admission-v1.json", summary)
    new(PUBLIC / "metadata-admission-v1.json", summary)
    print({"status": summary["status"], "selected": [(r["campaign"], r["repository_codename"]) for r in selected],
           "provider_blocks": len(blocks), "dispositions": summary["aggregate_dispositions"]})


if __name__ == "__main__":
    guard = start("aid-metadata-admission", 180, 300)
    try:
        main()
        finish("aid-metadata-admission", guard, "PASS_METADATA_OPAQUE_INTAKE_ONLY")
    except BaseException:
        finish("aid-metadata-admission", guard, "FAIL")
        raise
