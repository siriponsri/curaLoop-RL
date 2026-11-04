"""Prepare label-blind NCATS training subsets with explicit structure/label audits."""

import csv
import gzip
import hashlib
import json
import time
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from rdkit import Chem, rdBase
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

from .fetch_sources import RAW, SOURCES

ROOT = Path(__file__).resolve().parents[2]
PREP_VERSION = "curaloop.ncats-development-cohort.v1"
EXPECTED = {
    "ahr": "8b57bcfec402bbe76ac008a5e243341de5b4c92f891324b34351c5534827aebb",
    "pparg": "d9962585e65b170f2423dd13c3384ae8fcb33434b5bbf2a3800357441c5ea28f",
    "p53": "1fa72a15760a228c9b649b9b90675556f205b101445936181980a9ad87792052",
}
OUT = RAW / "prepared-v1"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_rows(lines: list[str]) -> tuple[list[dict], list[dict], dict]:
    groups = defaultdict(list)
    exclusions = []
    sources = set()
    for row, line in enumerate(lines):
        fields = line.split("\t")
        if len(fields) != 3:
            raise ValueError(f"Unexpected column count at source row {row}.")
        smiles, identifier, label = fields
        if identifier in sources:
            raise ValueError("Duplicate source ID requires explicit resolution: " + identifier)
        sources.add(identifier)
        if label not in ("0", "1"):
            if label.strip() == "":
                exclusions.append(
                    {
                        "source_row": row,
                        "source_id": identifier,
                        "reason": "MISSING_LABEL_NOT_INACTIVE",
                    }
                )
                continue
            raise ValueError("Unknown activity code; do not infer inactive: " + label)
        with rdBase.BlockLogs():
            mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            exclusions.append(
                {"source_row": row, "source_id": identifier, "reason": "INVALID_SMILES"}
            )
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
        groups[canonical].append(
            {"source_row": row, "source_id": identifier, "active": label == "1"}
        )
    clean = []
    conflict_groups = duplicate_rows = 0
    for canonical, rows in sorted(groups.items()):
        if len({r["active"] for r in rows}) > 1:
            conflict_groups += 1
            exclusions.extend({**r, "reason": "CONFLICTING_CANONICAL_LABEL"} for r in rows)
            continue
        rows.sort(key=lambda r: r["source_id"])
        representative = rows[0]
        for alias in rows[1:]:
            exclusions.append({**alias, "reason": "CONSISTENT_CANONICAL_DUPLICATE"})
            duplicate_rows += 1
        clean.append(
            {
                "canonical_smiles": canonical,
                "source_ids": [r["source_id"] for r in rows],
                "source_rows": [r["source_row"] for r in rows],
                "active": representative["active"],
            }
        )
    return (
        clean,
        exclusions,
        {
            "source_rows": len(lines),
            "canonical_conflict_groups": conflict_groups,
            "consistent_duplicate_rows": duplicate_rows,
            "eligible_unique_rows": len(clean),
        },
    )


def select_pool(records: list[dict], assay: str, count: int) -> list[dict]:
    """Hash ranking consumes identity/structure only, never activity."""
    if len(records) < count:
        raise ValueError("Insufficient eligible structures; do not refill using actives.")

    def key(record):
        return sha(json.dumps([PREP_VERSION, 20261104, assay, record["canonical_smiles"]]).encode())

    return sorted(records, key=key)[:count]


def packed(bits):
    return sum(1 << int(i) for i in bits)


def max_similarities(a: list[int], b: list[int]) -> list[float]:
    return [
        max(((x & y).bit_count() / (x | y).bit_count() if (x | y) else 1.0 for y in b), default=0.0)
        for x in a
    ]


def main() -> None:
    started = time.perf_counter()
    if OUT.exists():
        raise ValueError(
            "Prepared cohort already exists; retain it and use a new version for amendments."
        )
    OUT.mkdir()
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    cohorts, audits, exclusion_rows = {}, {}, []
    for name in SOURCES:
        data = (RAW / (name + ".smiles")).read_bytes()
        if sha(data) != EXPECTED[name]:
            raise ValueError("Raw source digest differs: " + name)
        clean, exclusions, stats = normalize_rows(data.decode("utf-8-sig").splitlines())
        assert len(clean) + len(exclusions) == stats["source_rows"]
        records = select_pool(clean, name, 600)
        for record in records:
            mol = Chem.MolFromSmiles(record["canonical_smiles"])
            record["candidate_id"] = "ncats-" + sha(record["canonical_smiles"].encode())[:24]
            record["morgan_on_bits"] = list(generator.GetFingerprint(mol).GetOnBits())
            record["scaffold"] = MurckoScaffold.MurckoScaffoldSmiles(
                mol=mol, includeChirality=False
            )
        assert len({r["candidate_id"] for r in records}) == len(records)
        payload = {
            "schema_version": PREP_VERSION,
            "task_id": "ncats2014-" + name + "-development-v1",
            "assay": SOURCES[name],
            "controller_role": "development",
            "raw_sha256": EXPECTED[name],
            "sample_size": 600,
            "sampling": "SHA256 rank of version, fixed seed 20261104, assay, canonical SMILES; no activity input",
            "standardization": "RDKit canonical isomeric SMILES; no salt stripping/tautomer normalization/stereo removal",
            "fingerprints": "Morgan radius 2, 1024 bits; includeChirality=False",
            "rdkit_version": rdBase.rdkitVersion,
            "records": sorted(records, key=lambda r: r["candidate_id"]),
        }
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
        (OUT / (name + ".json")).write_bytes(encoded)
        cohorts[name] = payload
        audits[name] = {
            **stats,
            "eligible_actives": sum(r["active"] for r in clean),
            "subset_n": 600,
            "subset_actives": sum(r["active"] for r in records),
            "cohort_sha256": sha(encoded),
            "unique_nonempty_scaffolds": len({r["scaffold"] for r in records if r["scaffold"]}),
            "empty_scaffold_rows": sum(not r["scaffold"] for r in records),
            "exclusion_counts": dict(Counter(r["reason"] for r in exclusions)),
        }
        exclusion_rows.extend({"assay": name, **r} for r in exclusions)
    with (OUT / "exclusions.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["assay", "source_row", "source_id", "reason"], extrasaction="ignore"
        )
        writer.writeheader()
        writer.writerows(exclusion_rows)
    hiv = json.loads(
        gzip.decompress((ROOT / "src/curaloop/resources/hiv_replay_v1.json.gz").read_bytes())
    )
    reference = [packed(r["morgan_on_bits"]) for r in hiv]
    hiv_canonical = {r["canonical_smiles"] for r in hiv}
    overlaps = {}
    for name, cohort in cohorts.items():
        rows = cohort["records"]
        sims = max_similarities([packed(r["morgan_on_bits"]) for r in rows], reference)
        overlaps[name + "_vs_HIV_regression"] = {
            "exact_canonical_overlap": len({r["canonical_smiles"] for r in rows} & hiv_canonical),
            "queries_with_max_tanimoto_ge_0_8": sum(x >= 0.8 for x in sims),
            "max_tanimoto": max(sims),
            "mean_nearest_tanimoto": sum(sims) / len(sims),
        }
    for a, b in combinations(cohorts, 2):
        ar, br = cohorts[a]["records"], cohorts[b]["records"]
        similarities = max_similarities(
            [packed(r["morgan_on_bits"]) for r in ar], [packed(r["morgan_on_bits"]) for r in br]
        )
        overlaps[a + "_vs_" + b] = {
            "exact_canonical_overlap": len(
                {r["canonical_smiles"] for r in ar} & {r["canonical_smiles"] for r in br}
            ),
            "shared_nonempty_scaffolds": len(
                {r["scaffold"] for r in ar if r["scaffold"]}
                & {r["scaffold"] for r in br if r["scaffold"]}
            ),
            "a_queries_with_max_tanimoto_ge_0_8": sum(x >= 0.8 for x in similarities),
        }
    report = {
        "status": "PASS",
        "schema_version": PREP_VERSION,
        "rdkit_version": rdBase.rdkitVersion,
        "preparation_wall_seconds": time.perf_counter() - started,
        "assays": audits,
        "overlaps": overlaps,
        "role": "DEVELOPMENT_ONLY; all three endpoints and chemical pools are now exposed; never untouched final tests",
        "labels": "NCATS 1=assay active, 0=inactive; not therapeutic efficacy; no relabelling/inversion",
        "unknown_labels": "Excluded or rejected, never converted to inactive",
        "rights": "Public NCATS challenge source; source-provider public-domain statement separately documented; raw/derived pools remain ignored",
        "final_protocol_frozen": False,
    }
    (OUT / "preparation-audit.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
