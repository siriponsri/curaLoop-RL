"""Authenticate retained exclusion metadata; never open protected payloads."""
# ruff: noqa: E402

import csv
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start


def main():
    old = ROOT / ".local/goal4r2a3-20261106-v1/remote-return/full-v1"
    assert sha(old / "manifest.json") == "eb2eeeef2de9915b08c35c0f73ac5bfeb32b1e5fff8fad3c081f8f3b8315aa0c"
    manifest = {r["path"]: r for r in read(old / "manifest.json")["files"]}
    inputs = {}

    def verified(name):
        path = old / "files" / name
        assert sha(path) == manifest[name]["sha256"]
        inputs[name] = manifest[name]["sha256"]
        return read(path)

    protection = verified("runs/metadata-audit-v1/protection-private.json")
    assert protection["outcome_values_present"] is False
    rights = {r["aid"]: r for r in verified("runs/metadata-audit-v1/rights-register.json")["records"]}
    gates = verified("runs/cached-reconciliation-v2/pair-metadata-gates.json")["records"]
    gates = {(r["primary_aid"], r["confirmation_aid"]): r for r in gates}
    source = TASK / "source/metadata/Logs/dataset_metadata.csv"
    records = []
    for row in csv.DictReader(source.open(encoding="utf-8", newline="")):
        pair = (row["Primary  HTS AID"].strip(), row["Confirmatory HTS AID"].strip())
        gate = gates.get(pair)
        accession = row["UniProt ID"].strip()
        target_protected = accession in protection["uniprot_accessions"]
        records.append({
            "codename": row["Codename"], "pair": pair, "source_publication": row["Source publication ID"],
            "source_target": accession, "direct_protected_target": target_protected,
            "retained_pair_role_evidence": gate,
            "retained_rights_evidence": [rights.get(a) for a in pair],
        })
    new(TASK / "role-review-private-v1.json", {"inputs": inputs, "records": records})
    statuses = Counter()
    admitted_roles = []
    for row in records:
        gate = row["retained_pair_role_evidence"]
        if row["direct_protected_target"]:
            statuses["EXCLUDE_DIRECT_PROTECTED_TARGET"] += 1
        elif gate is None:
            statuses["UNRESOLVED_NO_RETAINED_PAIR_BINDING"] += 1
        elif not gate["metadata_admitted"]:
            statuses["QUARANTINE_RETAINED_PAIR_ROLE_NOT_ADMITTED"] += 1
        else:
            statuses["RETAINED_ROLE_METADATA_ADMITTED_ONLY"] += 1
            admitted_roles.append({"codename": row["codename"], "pair": row["pair"],
                                   "family_roles": gate["target_family_gate"],
                                   "source_publication": row["source_publication"]})
    summary = {"status": "ROLE_METADATA_REVIEW_NOT_DATA_ADMISSION", "campaign_metadata_count": len(records),
               "aggregate_role_status": dict(statuses), "historical_manifest_sha256": sha(old / "manifest.json"),
               "historical_input_hashes": inputs, "final_payloads_opened": False,
               "confirmation_values_analyzed": False, "raw_data_downloaded": False}
    new(PUBLIC / "role-review-v1.json", summary)
    print(summary)
    print("PRIVATE_ADMITTED_ROLE_METADATA", admitted_roles)
    print("RIGHTS_COUNTS", Counter("MISSING" if r is None else r["publication"] for row in records for r in row["retained_rights_evidence"]))


if __name__ == "__main__":
    guard = start("retained-role-review", 120, 300)
    try:
        main()
        finish("retained-role-review", guard, "PASS_REVIEW_NOT_ADMISSION")
    except BaseException:
        finish("retained-role-review", guard, "FAIL")
        raise
