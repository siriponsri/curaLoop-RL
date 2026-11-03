"""Rebuild the attributed, label-blind historical replay subset (RDKit required)."""

import argparse
import csv
import gzip
import io
import json
import random
from hashlib import sha256
from pathlib import Path
from urllib.request import urlopen

from rdkit import Chem, RDLogger, rdBase
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

SOURCE = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/HIV.csv"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, default=Path("data/raw/HIV.csv"))
    p.add_argument("--download", action="store_true")
    p.add_argument("--output", type=Path, default=Path("src/curaloop/resources"))
    args = p.parse_args()
    if args.download:
        with urlopen(SOURCE, timeout=60) as response:
            raw = response.read(20_000_001)
        if len(raw) > 20_000_000:
            raise ValueError("Source exceeds size limit")
        args.source.parent.mkdir(parents=True, exist_ok=True)
        args.source.write_bytes(raw)
    raw = args.source.read_bytes()
    RDLogger.DisableLog("rdApp.*")
    rows = list(csv.DictReader(io.StringIO(raw.decode("utf-8"))))
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    parsed = []
    invalid = duplicates = conflicts = 0
    seen = {}
    for i, row in enumerate(rows):
        mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None:
            invalid += 1
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True, isomericSmiles=True)
        label = int(row["HIV_active"])
        if label not in (0, 1) or row["activity"] not in ("CA", "CM", "CI"):
            raise ValueError("Unexpected label semantics")
        if label != int(row["activity"] in ("CA", "CM")):
            raise ValueError("Inconsistent activity/label")
        if canonical in seen:
            duplicates += 1
            conflicts += int(seen[canonical] != label)
            continue
        seen[canonical] = label
        parsed.append((i, mol, canonical, label))
    if conflicts:
        raise ValueError("Conflicting duplicate labels require explicit adjudication")
    sampled = random.Random(20261103).sample(parsed, 1200)
    selected = []
    for i, mol, canonical, label in sampled:
        selected.append({"compound_id": f"HIV-ROW-{i:05d}", "source_row_zero_based": i,
                         "canonical_smiles": canonical, "active": bool(label),
                         "scaffold_id": MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False),
                         "morgan_on_bits": list(generator.GetFingerprint(mol).GetOnBits())})
    selected.sort(key=lambda r: r["compound_id"])
    content = json.dumps(selected, sort_keys=True, separators=(",", ":")).encode()
    compressed = gzip.compress(content, mtime=0)
    manifest = {
        "name": "MoleculeNet HIV label-blind replay subset", "release": "curaloop-hiv-1.0.0",
        "source_url": SOURCE, "source_access_date": "2026-11-03", "source_sha256": sha256(raw).hexdigest(),
        "source_rows": len(rows), "invalid_smiles_removed": invalid,
        "canonical_duplicates_removed": duplicates, "label_conflicts": conflicts,
        "valid_unique_source_rows": len(parsed), "subset_rows": len(selected),
        "subset_sampling": "random.Random(20261103).sample(valid_unique_rows, 1200); no label stratification",
        "resource_sha256": sha256(compressed).hexdigest(),
        "resource_uncompressed_sha256": sha256(content).hexdigest(),
        "license": "CC BY 4.0 as stated for HIV by Therapeutics Data Commons",
        "license_evidence_url": "https://tdcommons.ai/single_pred_tasks/hts/#hiv",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "attribution": "NCI DTP AIDS Antiviral Screen; Wu et al., MoleculeNet (2018), DOI 10.1039/C7SC02664A; DeepChem; Therapeutics Data Commons.",
        "changes": "Removed invalid/duplicate canonical structures; label-blind 1200-row subset; canonical SMILES, Morgan bits and Murcko scaffolds added.",
        "label_semantics": "CA/CM=1; CI=0, checked against HIV_active for every source record",
        "preprocessing": "RDKit canonical isomeric SMILES; no salt stripping, tautomer normalization or stereo removal; Morgan radius=2, bits=1024; Murcko nonchiral scaffolds.",
        "rdkit_version": rdBase.rdkitVersion,
        "benchmark_scope": "Custom historical replay subset, not official MoleculeNet/TDC leaderboard split or reproduction.",
        "cost_delay_provenance": "SYNTHETIC_ASSUMPTION, independent of historical assay outcomes",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "hiv_replay_v1.json.gz").write_bytes(compressed)
    (args.output / "hiv_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
