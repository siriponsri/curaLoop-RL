"""Curated broad family roles from reviewed UniProt metadata, never assay labels."""

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"


def normalize(text):
    return " ".join(text.strip().rstrip(".").casefold().split())


def family_annotation(record):
    text = record.get("Protein families", "").strip()
    if record.get("Reviewed") != "reviewed" or not text:
        return None
    parts = [normalize(x) for x in text.split(",")]
    top = parts[0]
    match = re.search(
        r"SIMILARITY: Belongs to the (.+?(?:superfamily|family))\.",
        record.get("Sequence similarities", ""),
        flags=re.IGNORECASE,
    )
    if (
        not match
        or normalize(match.group(1)) != top
        or not re.search(r"\b(?:superfamily|family)$", top)
    ):
        return None
    # These hierarchy nodes can merge broad groups; subfamilies never become independent units.
    family_nodes = {p for p in parts if re.search(r"\b(?:superfamily|family)$", p)}
    return top, family_nodes


def build_registry(assays, targets, proteins, source_manifest):
    by_target = {t["target_chembl_id"]: t for t in targets}
    by_accession = {p["Entry"]: p for p in proteins}
    source_role = {a: role for role, ids in source_manifest.items() for a in ids}
    parsed = {a: family_annotation(p) for a, p in by_accession.items()}
    tops = {v[0] for v in parsed.values() if v}
    parent = {t: t for t in tops}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for value in parsed.values():
        if value:
            broad, nodes = value
            for other in nodes & tops:
                a, b = find(broad), find(other)
                if a != b:
                    parent[max(a, b)] = min(a, b)
    groups = defaultdict(list)
    for top in tops:
        groups[find(top)].append(top)
    canonical = {t: min(groups[find(t)]) for t in tops}
    accepted, exclusions = [], []
    available = {a["assay_chembl_id"] for a in assays}
    for aid in sorted(set(source_role) - available):
        exclusions.append({"assay_id": aid, "reason": "NOT_RETURNED_BY_CURRENT_CHEMBL37_METADATA"})
    for row in assays:
        aid = row["assay_chembl_id"]
        target = by_target.get(row.get("target_chembl_id"), {})
        components = target.get("components", [])
        reason = None
        if row.get("confidence_score") != 9 or row.get("relationship_type") != "D":
            reason = "NOT_DIRECT_CONFIDENCE9"
        elif target.get("target_type") != "SINGLE PROTEIN" or len(components) != 1:
            reason = "NOT_UNAMBIGUOUS_SINGLE_PROTEIN"
        elif components[0].get("component_type") != "PROTEIN":
            reason = "NOT_PROTEIN_COMPONENT"
        else:
            accession = components[0].get("accession")
            protein = by_accession.get(accession, {})
            annotation = parsed.get(accession)
            if not annotation:
                reason = "NO_REVIEWED_CONCORDANT_BROAD_FAMILY_ANNOTATION"
            elif str(target.get("tax_id")) != protein.get("Organism (ID)"):
                reason = "TARGET_UNIPROT_TAXON_MISMATCH"
        if reason:
            exclusions.append({"assay_id": aid, "reason": reason})
            continue
        family = canonical[annotation[0]]
        family_id = "uniprot-broad-" + hashlib.sha256(family.encode()).hexdigest()[:20]
        bucket = (
            int(
                hashlib.sha256(("curaloop-family-roles-v1|" + family).encode()).hexdigest()[:16], 16
            )
            % 10
        )
        role = "development" if bucket < 3 else "validation" if bucket < 5 else "final"
        if aid == "CHEMBL1614128" and role != "development":
            exclusions.append(
                {"assay_id": aid, "reason": "KNOWN_AGGREGATE_EXPOSURE_NONDEVELOPMENT_ROLE"}
            )
            continue
        accepted.append(
            {
                "assay_id": aid,
                "source_role": source_role[aid],
                "source_internal_target_id_semantics": "Preserved separately in source CSV",
                "annotation_target_id": target["target_chembl_id"],
                "uniprot_accession": accession,
                "tax_id": target["tax_id"],
                "organism": target["organism"],
                "family_id": family_id,
                "family": family,
                "curated_broad_annotation": annotation[0],
                "role": role,
                "uniprot_release": "2026_04",
                "chembl_annotation_release": "ChEMBL_37",
                "role_rank": hashlib.sha256(
                    ("curaloop-family-rank-v1|" + family).encode()
                ).hexdigest(),
                "assay_rank": hashlib.sha256(
                    ("curaloop-assay-rank-v1|" + aid).encode()
                ).hexdigest(),
            }
        )
    family_records = []
    for fid in sorted({r["family_id"] for r in accepted}):
        rows = [r for r in accepted if r["family_id"] == fid]
        family_records.append(
            {
                "family_id": fid,
                "family": rows[0]["family"],
                "role": rows[0]["role"],
                "family_rank": rows[0]["role_rank"],
                "assays": len(rows),
                "targets": len({r["annotation_target_id"] for r in rows}),
                "taxa": sorted({r["tax_id"] for r in rows}),
                "broad_names_merged": sorted(groups[find(rows[0]["curated_broad_annotation"])]),
            }
        )
    return {
        "status": "METADATA_ROLE_CANDIDATES_NOT_FEATURE_READY",
        "source_default_tasks": len(source_role),
        "eligible_assays": len(accepted),
        "family_groups": len(family_records),
        "role_family_counts": dict(Counter(r["role"] for r in family_records)),
        "role_assay_counts": dict(Counter(r["role"] for r in accepted)),
        "exclusion_reasons": dict(Counter(r["reason"] for r in exclusions)),
        "family_records": sorted(family_records, key=lambda r: (r["role"], r["family_rank"])),
        "assays": sorted(accepted, key=lambda r: (r["role"], r["role_rank"], r["assay_rank"])),
        "exclusions": exclusions,
        "labels_read": False,
        "hierarchy_rule": "Reviewed broadest family/superfamily prefix concordant with SIMILARITY; merge ancestor broad labels, never count kinase children separately",
        "statistical_independence_certified": False,
    }


def main():
    output = RAW / "family-registry-v1.json"
    if output.exists():
        raise FileExistsError(output)
    report = build_registry(
        json.loads((RAW / "chembl37-mapping-v1/assays.json").read_text()),
        json.loads((RAW / "chembl37-mapping-v1/targets.json").read_text()),
        json.loads((RAW / "uniprot-family-bulk-v1/families.json").read_text()),
        json.loads((RAW / "source-metadata-v1/fsmol-0.1.json").read_text()),
    )
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                k: v
                for k, v in report.items()
                if k not in ("assays", "family_records", "exclusions")
            },
            indent=2,
        )
    )
    print(
        "FIRST_FINAL",
        json.dumps([r for r in report["family_records"] if r["role"] == "final"][:14], indent=2),
    )


if __name__ == "__main__":
    main()
