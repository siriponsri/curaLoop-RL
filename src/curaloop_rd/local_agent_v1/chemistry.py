"""Actual bounded RDKit computation; no assay, efficacy or hidden-outcome access."""

import csv
import io
import math
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FilterSpec:
    molecular_weight_max: float = 500.0
    logp_max: float = 5.0
    tpsa_max: float = 140.0

    def __post_init__(self):
        for value in asdict(self).values():
            if isinstance(value, bool) or not math.isfinite(value):
                raise ValueError("Filter limits must be finite numbers")
        if self.molecular_weight_max <= 0 or self.tpsa_max < 0:
            raise ValueError("Invalid molecular-weight or TPSA limit")


def validate_csv(text, *, max_rows=2000):
    if len(text.encode("utf-8")) > 1024**2:
        raise ValueError("Compound CSV exceeds one MiB")
    reader = csv.DictReader(io.StringIO(text.removeprefix("\ufeff")))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("CSV needs unique column names")
    if not {"compound_id", "smiles"}.issubset(reader.fieldnames):
        raise ValueError("CSV must contain compound_id and smiles columns")
    rows, rejected, seen = [], [], set()
    for number, row in enumerate(reader, 2):
        if number > max_rows + 1:
            raise ValueError("Compound CSV exceeds the row limit")
        identity, smiles = (row.get("compound_id") or "").strip(), (row.get("smiles") or "").strip()
        reason = None
        if None in row or any(v is None for v in row.values()):
            reason = "MALFORMED_CSV_ROW"
        elif not identity or len(identity) > 128:
            reason = "MISSING_OR_TOO_LONG_COMPOUND_ID"
        elif identity in seen:
            reason = "DUPLICATE_COMPOUND_ID"
        elif not smiles or len(smiles) > 2048:
            reason = "MISSING_OR_TOO_LONG_SMILES"
        seen.add(identity)
        item = {"row": number, "compound_id": identity, "smiles": smiles}
        (rejected if reason else rows).append({**item, "reason": reason} if reason else item)
    if not rows and not rejected:
        raise ValueError("Compound CSV has no data rows")
    return rows, rejected


def compute(text, spec):
    from rdkit import Chem, rdBase
    from rdkit.Chem import Crippen, Descriptors, Lipinski, rdMolDescriptors

    rows, rejected = validate_csv(text)
    input_rows = len(rows) + len(rejected)
    compounds = []
    for row in rows:
        with rdBase.BlockLogs():
            mol = Chem.MolFromSmiles(row["smiles"])
        if mol is None or mol.GetNumAtoms() == 0 or mol.GetNumAtoms() > 512:
            rejected.append({**row, "reason": "INVALID_EMPTY_OR_TOO_LARGE_MOLECULE"})
            continue
        mw, logp, tpsa = (
            Descriptors.MolWt(mol),
            Crippen.MolLogP(mol),
            rdMolDescriptors.CalcTPSA(mol),
        )
        if not all(math.isfinite(v) for v in (mw, logp, tpsa)):
            rejected.append({**row, "reason": "NONFINITE_DESCRIPTOR"})
            continue
        reasons = [
            name
            for name, value, limit in (
                ("MOLECULAR_WEIGHT_LIMIT", mw, spec.molecular_weight_max),
                ("LOGP_LIMIT", logp, spec.logp_max),
                ("TPSA_LIMIT", tpsa, spec.tpsa_max),
            )
            if value > limit
        ]
        compounds.append(
            {
                **row,
                "canonical_smiles": Chem.MolToSmiles(mol),
                "molecular_weight": mw,
                "logp": logp,
                "tpsa": tpsa,
                "hbd": Lipinski.NumHDonors(mol),
                "hba": Lipinski.NumHAcceptors(mol),
                "selected": not reasons,
                "filter_reasons": reasons,
            }
        )
    return {
        "schema": "curaloop.local-agent.compound-result.v1",
        "rdkit_version": rdBase.rdkitVersion,
        "parameters": asdict(spec),
        "compounds": compounds,
        "rejected": rejected,
        "counts": {
            "input_rows": input_rows,
            "valid": len(compounds),
            "rejected": len(rejected),
            "selected": sum(r["selected"] for r in compounds),
        },
        "units": {"molecular_weight": "g/mol", "tpsa": "angstrom^2", "logp": "dimensionless"},
        "limitations": [
            "Physicochemical filtering only",
            "No assay or efficacy prediction",
            "Author-selected local workflow, not an external benchmark result",
        ],
    }
