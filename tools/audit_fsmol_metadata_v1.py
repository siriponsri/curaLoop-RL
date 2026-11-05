"""Outcome-free source/target/category/physical-member audit, no assay parsing."""

import csv
import hashlib
import json
import time
from collections import Counter, defaultdict
from pathlib import PurePosixPath

from tools.fetch_fsmol_metadata_v1 import EXPECTED_COLUMNS, ROOT


def scalar_category(value):
    value = value.strip()
    return bool(
        value
        and value not in ("unclassified", "undefined enzyme/protein")
        and not any(c in value for c in "()[],")
    )


def audit(rows_by_role, manifest, headers):
    role_ids, target_ids, category_counts, rows_index = {}, {}, {}, {}
    for role, rows in rows_by_role.items():
        ids = [r["chembl_id"] for r in rows]
        if len(ids) != len(set(ids)) or set(ids) != set(manifest[role]):
            raise ValueError("Source metadata/manifest identity mismatch: " + role)
        role_ids[role] = set(ids)
        target_ids[role] = {r["target_id"] for r in rows if r["target_id"]}
        counts = Counter()
        for row in rows:
            rows_index[row["chembl_id"]] = {**row, "source_role": role}
            group = row["protein_super_family"]
            if row["reliable_target_protein_super"] == "True" and scalar_category(group):
                counts[group] += 1
        category_counts[role] = dict(sorted(counts.items()))
    overlaps = []
    for a, b in (("train", "valid"), ("train", "test"), ("valid", "test")):
        if role_ids[a] & role_ids[b]:
            raise ValueError("Source assay overlap.")
        shared = sorted(target_ids[a] & target_ids[b])
        overlaps.append(
            {
                "source_roles": [a, b],
                "internal_target_ids": shared,
                "assays": {
                    role: sorted(
                        r["chembl_id"] for r in rows_by_role[role] if r["target_id"] in shared
                    )
                    for role in (a, b)
                },
            }
        )
    members = defaultdict(list)
    for row in headers["members"]:
        if row["kind"] == "file":
            parts = PurePosixPath(row["name"]).parts
            if (
                len(parts) != 3
                or parts[0] != "fs-mol"
                or parts[1] not in role_ids
                or not parts[2].endswith(".jsonl.gz")
            ):
                raise ValueError("Unexpected physical source entry: " + row["name"])
            members[parts[1]].append(parts[2][:-9])
    physical = {}
    for role in role_ids:
        ids = members[role]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate tar member identities.")
        missing = role_ids[role] - set(ids)
        physical[role] = {
            "physical_files": len(ids),
            "default_manifest_tasks": len(role_ids[role]),
            "additional_physical_tasks": len(set(ids) - role_ids[role]),
            "missing_default_tasks": sorted(missing),
        }
        if missing:
            raise ValueError("Default-manifest source file missing: " + role)
    union = sorted(set().union(*(set(v) for v in category_counts.values())))
    return {
        "status": "PASS_METADATA_AUDIT_NOT_DATASET_READY",
        "assay_rows_parsed": False,
        "outcome_fields_read": False,
        "source_role_counts": {r: len(v) for r, v in role_ids.items()},
        "manifest_tasks": sum(len(v) for v in role_ids.values()),
        "paper_total": 5120,
        "source_role_count_sum": 5135,
        "paper_discrepancy_resolution": "Use exact pinned5135-ID manifest; retain inconsistent5120 paper total, do not drop15arbitrarily",
        "physical_source": physical,
        "internal_target_overlap": overlaps,
        "source_supercategory_counts": category_counts,
        "source_supercategory_union": union,
        "test_supercategories_also_in_train": sorted(
            set(category_counts["test"]) & set(category_counts["train"])
        ),
        "verified_homology_family_count": None,
        "final_ready_families": 0,
        "category_limit": "Provider source categories/reliability flags do not prove uniform biological/homology hierarchy or statistical independence",
        "heldout_split_decision": "OWNER_QUESTION_PENDING; no derived roles frozen",
        "known_aggregate_exposure_task": "CHEMBL1614128; development-only",
        "internal_target_ids_are_public_chembl_target_ids": False,
    }


def main():
    started, cpu = time.perf_counter(), time.process_time()
    raw = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"
    source = raw / "source-metadata-v1"
    folder = ROOT / "docs/evidence/plan-a-20261105-v1"
    output = folder / "source-metadata-audit-v1.json"
    if output.exists():
        raise FileExistsError(output)
    rows = {}
    source_hashes = {}
    for role in ("train", "valid", "test"):
        path = source / f"{role}_proteins.csv"
        source_hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != EXPECTED_COLUMNS:
                raise ValueError("Unexpected source metadata columns; no row inspection.")
            rows[role] = list(reader)
    manifest = json.loads((source / "fsmol-0.1.json").read_text())
    headers = json.loads((raw / "header-audit-v2.json").read_text())
    report = audit(rows, manifest, headers)
    report.update(
        source_sha256=source_hashes,
        wall_seconds=time.perf_counter() - started,
        cpu_seconds=time.process_time() - cpu,
    )
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
