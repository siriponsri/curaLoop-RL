"""Typed ancestry closure of provisional broad families, without assay labels."""

import hashlib
import json
import re
import time
from collections import Counter, defaultdict

from research.benchmark_v3.families import RAW, family_annotation, normalize

EXPOSED_ACCESSIONS = ("P04637", "P37231", "P35869", "Q00975", "Q02410")


def iprs(protein):
    return {s for s in protein.get("InterPro", "").split(";") if s}


def typed_entries():
    from tools.finish_interpro_types_v1 import cached_types

    records, failed = cached_types()
    path = RAW / "interpro-ftp-entries110-curl-v2/body"
    receipt = json.loads(path.with_name("receipt.json").read_text())
    data = path.read_bytes()
    if (
        receipt["status"] != 200
        or receipt["error"]
        or hashlib.sha256(data).hexdigest() != receipt["sha256"]
    ):
        raise ValueError("Unverified release110.0 bulk type listing.")
    lines = data.decode("utf-8").splitlines()
    if lines[0].split("\t") != ["ENTRY_AC", "ENTRY_TYPE", "ENTRY_NAME"]:
        raise ValueError("Unexpected bulk type schema.")
    bulk = {}
    for line in lines[1:]:
        aid, kind, name = line.split("\t", 2)
        kind = kind.lower().replace(" ", "_")
        if aid in bulk or not re.fullmatch(r"IPR\d{6}", aid):
            raise ValueError("Invalid/duplicate bulk entry identity.")
        if aid in records and kind != records[aid]["type"]:
            raise ValueError("Pinned release/API types disagree: " + aid)
        bulk[aid] = {"accession": aid, "type": kind, "name": name, "release": "110.0"}
    receipt = {
        **receipt,
        "source": "Official pinned release110.0 entry.list",
        "release": "110.0",
        "typed_entries": len(bulk),
        "api_crosschecked_entries": len(records),
        "previous_unavailable_now_resolved": sorted(failed),
    }
    records = bulk
    return records, receipt


def ambiguity_reason(protein):
    annotation = family_annotation(protein)
    clauses = re.findall(
        r"SIMILARITY: Belongs to the (.+?(?:superfamily|family))\.",
        protein.get("Sequence similarities", ""),
        flags=re.IGNORECASE,
    )
    if len({normalize(c) for c in clauses}) != 1 or annotation is None:
        return "AMBIGUOUS_MULTIFAMILY_SIMILARITY"
    if ";" in protein.get("Protein families", "") or re.search(
        r"\b(?:bifunctional|trifunctional|multifunctional)\b",
        protein.get("Protein names", ""),
        re.IGNORECASE,
    ):
        return "UNRESOLVED_MULTIFUNCTIONAL_OR_MULTIFAMILY_PROTEIN"
    if re.search(
        r"SIMILARITY:.*(?:N-terminal|C-terminal|section|region)",
        protein.get("Sequence similarities", ""),
        re.IGNORECASE,
    ):
        return "REGION_SPECIFIC_FAMILY_ASSIGNMENT"
    return None


def close_families(provisional, proteins, types):
    by_accession = {p["Entry"]: p for p in proteins}
    missing_anchors = set(EXPOSED_ACCESSIONS) - set(by_accession)
    if missing_anchors:
        raise ValueError("Exposure anchor metadata unresolved: " + str(sorted(missing_anchors)))
    exclusions = list(provisional["exclusions"])
    primary_rows = []
    for row in provisional["assays"]:
        reason = ambiguity_reason(by_accession[row["uniprot_accession"]])
        if reason:
            exclusions.append({"assay_id": row["assay_id"], "reason": reason})
        else:
            primary_rows.append(row)
    old_groups = {r["family_id"]: r for r in provisional["family_records"]}
    parent = {fid: fid for fid in old_groups}

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    entry_groups = defaultdict(set)
    for row in primary_rows:
        for accession in iprs(by_accession[row["uniprot_accession"]]):
            entry_groups[accession].add(row["family_id"])
    unresolved_groups, unresolved_entries = set(), []
    for accession, ids in entry_groups.items():
        if len(ids) > 1 and accession not in types:
            unresolved_groups.update(ids)
            unresolved_entries.append(
                {"accession": accession, "excluded_provisional_groups": sorted(ids)}
            )
    # Missing metadata never silently becomes evidence of separation. Exclude
    # every entire broad group touching an unresolved cross-group annotation.
    kept = []
    for row in primary_rows:
        if row["family_id"] in unresolved_groups:
            exclusions.append(
                {"assay_id": row["assay_id"], "reason": "UNRESOLVED_SHARED_INTERPRO_TYPE"}
            )
        else:
            kept.append(row)
    primary_rows = kept
    bridges = []
    for accession, groups in sorted(entry_groups.items()):
        groups = groups - unresolved_groups
        if len(groups) < 2:
            continue
        if accession not in types:
            raise ValueError(
                "Shared InterPro ancestry type unresolved after quarantine: " + accession
            )
        kind = types[accession]["type"]
        if kind not in ("family", "homologous_superfamily"):
            continue
        ordered = sorted(groups)
        for fid in ordered[1:]:
            a, b = find(ordered[0]), find(fid)
            if a != b:
                parent[max(a, b)] = min(a, b)
        bridges.append({**types[accession], "provisional_groups": ordered})
    components = defaultdict(list)
    for fid in parent.keys() - unresolved_groups:
        components[find(fid)].append(fid)
    groups = {}
    for root, ids in components.items():
        names = sorted({name for fid in ids for name in old_groups[fid]["broad_names_merged"]})
        identity = "|".join(names)
        digest = hashlib.sha256(identity.encode()).hexdigest()
        bucket = (
            int(hashlib.sha256(("curaloop-roles-v2|" + identity).encode()).hexdigest()[:16], 16)
            % 10
        )
        role = "development" if bucket < 3 else "validation" if bucket < 5 else "final"
        groups[root] = {
            "family_id": "typed-ancestry-" + digest[:20],
            "family": "; ".join(names),
            "broad_names_merged": names,
            "provisional_groups": sorted(ids),
            "role": role,
            "family_rank": hashlib.sha256(
                ("curaloop-family-rank-v2|" + identity).encode()
            ).hexdigest(),
            "exposure_quarantine": [],
        }
    # Exposure quarantine is intentionally stricter than family equivalence:
    # any shared InterPro annotation (even a generic domain/site) stays development.
    anchor_entries = {a: iprs(by_accession[a]) for a in EXPOSED_ACCESSIONS}
    for row in primary_rows:
        group = groups[find(row["family_id"])]
        row_entries = iprs(by_accession[row["uniprot_accession"]])
        for anchor, entries in anchor_entries.items():
            if row["uniprot_accession"] == anchor or entries & row_entries:
                group["exposure_quarantine"].append(anchor)
        if row["assay_id"] == "CHEMBL1614128":
            group["exposure_quarantine"].append("CHEMBL1614128")
    for group in groups.values():
        group["exposure_quarantine"] = sorted(set(group["exposure_quarantine"]))
        if group["exposure_quarantine"]:
            group["role"] = "development"
    accepted = []
    for row in primary_rows:
        protein = by_accession[row["uniprot_accession"]]
        clauses = re.findall(
            r"SIMILARITY: Belongs to the (.+?(?:superfamily|family))\.",
            protein.get("Sequence similarities", ""),
            flags=re.IGNORECASE,
        )
        if len({normalize(c) for c in clauses}) != 1 or family_annotation(protein) is None:
            exclusions.append(
                {"assay_id": row["assay_id"], "reason": "AMBIGUOUS_MULTIFAMILY_SIMILARITY"}
            )
            continue
        group = groups[find(row["family_id"])]
        accepted.append(
            {
                **row,
                "family_id": group["family_id"],
                "family": group["family"],
                "role": group["role"],
                "role_rank": group["family_rank"],
                "interpro_release": "110.0",
                "exposure_quarantine": group["exposure_quarantine"],
            }
        )
    records = []
    for group in groups.values():
        rows = [r for r in accepted if r["family_id"] == group["family_id"]]
        if rows:
            records.append(
                {
                    **group,
                    "assays": len(rows),
                    "targets": len({r["annotation_target_id"] for r in rows}),
                    "taxa": sorted({r["tax_id"] for r in rows}),
                }
            )
    return {
        "schema_version": "curaloop.family-registry.v2",
        "status": "METADATA_ROLES_NOT_FEATURE_READY",
        "hierarchy_rule": "Transitive closure of concordant reviewed broad families sharing typed InterPro family/homologous_superfamily entries; generic domains/sites/repeats do not define equivalence",
        "exposure_rule": "Any InterPro overlap with prior exposed p53/PPARG/AHR and canary PPI-component anchors forces complete component development-only",
        "independence_scope": "No typed shared family/homologous-superfamily identity across roles; not a claim of phylogenetic or statistical independence",
        "source_default_tasks": provisional["source_default_tasks"],
        "eligible_assays": len(accepted),
        "family_groups": len(records),
        "role_family_counts": dict(Counter(r["role"] for r in records)),
        "role_assay_counts": dict(Counter(r["role"] for r in accepted)),
        "exclusion_reasons": dict(Counter(r["reason"] for r in exclusions)),
        "family_records": sorted(records, key=lambda r: (r["role"], r["family_rank"])),
        "assays": sorted(accepted, key=lambda r: (r["role"], r["role_rank"], r["assay_rank"])),
        "typed_bridges": bridges,
        "unresolved_shared_entries": unresolved_entries,
        "known_exposed_assay_permanently_not_final": "CHEMBL1614128",
        "exclusions": exclusions,
        "assay_labels_accessed": False,
    }


def main():
    out = RAW / "family-registry-v3.json"
    if out.exists():
        raise FileExistsError(out)
    started, cpu = time.perf_counter(), time.process_time()
    types, receipt = typed_entries()
    proteins = json.loads((RAW / "uniprot-family-bulk-v1/families.json").read_text())
    proteins += json.loads((RAW / "uniprot-family-exposure-v1/families.json").read_text())
    report = close_families(
        json.loads((RAW / "family-registry-v1.json").read_text()), proteins, types
    )
    report.update(
        {
            "types_source": receipt,
            "wall_seconds": time.perf_counter() - started,
            "cpu_seconds": time.process_time() - cpu,
        }
    )
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("family_records", "assays", "exclusions", "typed_bridges")
            },
            indent=2,
        )
    )
    print(
        "FIRST_FINAL",
        json.dumps([r for r in report["family_records"] if r["role"] == "final"][:16], indent=2),
    )


if __name__ == "__main__":
    main()
