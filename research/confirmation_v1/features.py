"""Source fingerprints and fixed operational structure groups, without outcomes."""

import ast
import csv
import json
import typing

import numpy as np
import rdkit
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem
from rdkit.Chem.Scaffolds import MurckoScaffold

from research.confirmation_v1.technical_worker import read, sha
from research.m2_costed_v2.guard import new


def source_fingerprint_function(root):
    path = root / "author/utils.py"
    tree = ast.parse(path.read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "get_ECFP"]
    assert len(functions) == 1
    namespace = {"List": typing.List, "rdkit": rdkit, "np": np, "AllChem": AllChem, "DataStructs": DataStructs}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), namespace)
    return namespace["get_ECFP"]


def structure_group(molecule):
    scaffold = MurckoScaffold.GetScaffoldForMol(molecule)
    if scaffold.GetNumAtoms():
        return "MURCKO:" + Chem.MolToSmiles(scaffold, canonical=True, isomericSmiles=False)
    generic = MurckoScaffold.MakeScaffoldGeneric(molecule)
    return "ACYCLIC:" + Chem.MolToSmiles(generic, canonical=True, isomericSmiles=False)


def bitvectors(bits):
    return [DataStructs.CreateFromBitString("".join(map(str, row.tolist()))) for row in bits]


def leader_groups(fingerprints, rows):
    leaders, assignment = [], [None] * len(rows)
    order = sorted(range(len(rows)), key=lambda i: (rows[i]["canonical_smiles"], rows[i]["record_id"]))
    for i in order:
        similarities = DataStructs.BulkTanimotoSimilarity(fingerprints[i], [fingerprints[j] for j in leaders])
        group = next((j for j, value in enumerate(similarities) if value >= 0.60), None)
        if group is None:
            leaders.append(i)
            group = len(leaders) - 1
        assignment[i] = "FP_LEADER:" + rows[leaders[group]]["record_id"]
    return assignment


def prepare(root, permit):
    assert rdkit.__version__ == "2022.09.4"
    RDLogger.DisableLog("rdApp.warning")
    RDLogger.DisableLog("rdApp.error")
    support = next(r for r in read(root / "inputs/blinded-support-v1.json")["campaigns"] if r["campaign"] == permit["campaign"])
    projection = root / support["projection"]
    assert sha(projection) == support["projection_sha256"]
    assert support["status"] == "PASS_BLINDED_STRUCTURE_SUPPORT"
    output = root / "features" / permit["output_name"]
    output.mkdir(parents=True, exist_ok=False)
    n = support["counts"]["retained_primary_rows"]
    x = np.lib.format.open_memmap(str(output / "fingerprints.npy"), mode="w+", dtype=np.uint8, shape=(n, 1024))
    y = np.empty(n, dtype=np.uint8)
    universe, rows = [], []
    function = source_fingerprint_function(root)
    offset = 0

    def process(batch):
        nonlocal offset
        mols = [Chem.MolFromSmiles(row["SMILES"]) for row in batch]
        assert all(molecule is not None for molecule in mols), "SOURCE_2022_REPRESENTATION_FAILURE"
        raw = function(mols)
        compact = raw.astype(np.uint8)
        assert raw.dtype == np.float32 and np.array_equal(compact.astype(np.float32), raw)
        assert np.isin(compact, [0, 1]).all()
        x[offset:offset + len(batch)] = compact
        for j, (row, molecule) in enumerate(zip(batch, mols)):
            y[offset + j] = int(row["Primary"])
            if row["Primary"] == "1" and row["confirmation_observed"] == "1":
                universe.append(offset + j)
                rows.append({"record_id": row["record_id"], "source_row": int(row["source_row"]),
                             "canonical_smiles": row["canonical_smiles"], "group": structure_group(molecule),
                             "primary_score": float(row["Score"])})
        offset += len(batch)

    with projection.open(newline="") as source:
        batch = []
        for row in csv.DictReader(source):
            batch.append(row)
            if len(batch) == 1024:
                process(batch)
                batch = []
        if batch:
            process(batch)
    assert offset == n and len(universe) == support["counts"]["eligible_confirmation_observations"]
    x.flush()
    indices = np.array(universe, dtype=np.int64)
    fps = bitvectors(x[indices])
    sensitivity = leader_groups(fps, rows)
    for row, group in zip(rows, sensitivity):
        row["sensitivity_group"] = group
    # The nearest reference includes all observed primary hits, not only U.
    positives = np.flatnonzero(y == 1)
    reference = bitvectors(x[positives])
    position = {int(i): j for j, i in enumerate(positives)}
    nearest = []
    for i, fingerprint in zip(indices, fps):
        similarities = DataStructs.BulkTanimotoSimilarity(fingerprint, reference)
        similarities[position[int(i)]] = -1.0
        nearest.append(max(0.0, max(similarities)))
    np.save(str(output / "primary-labels.npy"), y, allow_pickle=False)
    np.save(str(output / "universe-indices.npy"), indices, allow_pickle=False)
    np.save(str(output / "nearest-primary.npy"), np.asarray(nearest), allow_pickle=False)
    with (output / "universe.json").open("x") as file:
        json.dump({"campaign": permit["campaign"], "rows": rows, "confirmation_values_present": False}, file)
    x._mmap.close()
    files = {path.name: sha(path) for path in output.iterdir() if path.is_file()}
    result = {"status": "PASS_SOURCE_FEATURES_AND_FIXED_GROUPS", "campaign": permit["campaign"],
              "directory": str(output.relative_to(root)), "primary_rows": n, "universe_size": len(rows),
              "murcko_or_fallback_groups": len({r["group"] for r in rows}),
              "acyclic_universe_rows": sum(r["group"].startswith("ACYCLIC:") for r in rows),
              "fingerprint_sensitivity_groups": len(set(sensitivity)), "files": files,
              "budgets": support["budgets"], "model_fits": 0, "confirmation_values_analyzed": False}
    new(output / "manifest.json", result)
    return result


def load(root, descriptor):
    directory = root / descriptor["directory"]
    for name, expected in descriptor["files"].items():
        assert sha(directory / name) == expected
    x = np.load(str(directory / "fingerprints.npy"), mmap_mode="r", allow_pickle=False)
    y = np.load(str(directory / "primary-labels.npy"), allow_pickle=False)
    indices = np.load(str(directory / "universe-indices.npy"), allow_pickle=False)
    rows = read(directory / "universe.json")["rows"]
    assert len(rows) == len(indices) and len(y) == len(x)
    return directory, x, y, indices, rows
