"""Task-owned environment and blinded support checks; compatible with Python3.8."""

import csv
import hashlib
import importlib.util
import json
import math
import posixpath
import sys
import tarfile
import zipfile
from pathlib import Path

from research.m2_costed_v2.guard import CostedGuard, new


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    value = hashlib.sha256()
    with Path(path).open("rb") as file:
        for block in iter(lambda: file.read(1048576), b""):
            value.update(block)
    return value.hexdigest()


def environment(root, permit):
    inputs = read(root / "inputs/dependency-inputs.json")
    archive = root / "inputs/python38.tar.gz"
    assert sha(archive) == inputs["python"]["sha256"]
    assert not (root / "python").exists()
    with tarfile.open(str(archive), "r:gz") as source:
        members = {m.name: m for m in source.getmembers()}
        assert len(members) < 4000 and sum(m.size for m in members.values()) < 128 * 1024**2

        def target(member, depth=0):
            assert depth < 12
            if member.issym():
                name = posixpath.normpath(posixpath.join(posixpath.dirname(member.name), member.linkname))
                assert name.startswith("python/") and name in members
                return target(members[name], depth + 1)
            assert member.isfile()
            return member

        for member in members.values():
            assert member.name.startswith("python/") and ".." not in Path(member.name).parts
            original = target(member)
            path = root / member.name
            path.parent.mkdir(parents=True, exist_ok=True)
            with source.extractfile(original) as inp, path.open("xb") as out:
                for block in iter(lambda: inp.read(1048576), b""):
                    out.write(block)
            path.chmod(original.mode & 0o777)
    site = root / "python/lib/python3.8/site-packages"
    site.mkdir(parents=True, exist_ok=True)
    count = 0
    for wheel in inputs["wheels"]:
        path = root / "wheels" / wheel["filename"]
        assert sha(path) == wheel["sha256"]
        with zipfile.ZipFile(str(path)) as source:
            assert sum(m.file_size for m in source.infolist()) < 512 * 1024**2
            for member in source.infolist():
                if member.is_dir():
                    continue
                relative = Path(member.filename)
                assert not relative.is_absolute() and ".." not in relative.parts
                # Wheel library data use the normal installation root. Auxiliary
                # headers/scripts remain retained under their .data directory.
                if len(relative.parts) >= 3 and relative.parts[0].endswith(".data") and relative.parts[1] in ("purelib", "platlib"):
                    relative = Path(*relative.parts[2:])
                destination = site / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                with source.open(member) as inp, destination.open("xb") as out:
                    for block in iter(lambda: inp.read(1048576), b""):
                        out.write(block)
                destination.chmod(0o600)
                count += 1
    return {"status": "PASS_CPU_ENVIRONMENT_EXTRACTED_SMOKE_PENDING", "runtime_version": "3.8.16",
            "wheel_count": len(inputs["wheels"]), "wheel_files": count,
            "symlinks_materialized_within_archive": True, "gpu_packages_installed": False,
            "model_fits": 0, "confirmation_values_analyzed": False}


def smoke(root, permit):
    import lightgbm
    import numpy as np
    import pandas
    import rdkit
    import scipy
    import sklearn

    versions = {"python": ".".join(map(str, sys.version_info[:3])), "numpy": np.__version__,
                "scipy": scipy.__version__, "pandas": pandas.__version__, "sklearn": sklearn.__version__,
                "lightgbm": lightgbm.__version__, "rdkit": rdkit.__version__}
    assert versions == {"python": "3.8.16", "numpy": "1.22.3", "scipy": "1.8.1", "pandas": "1.4.4",
                        "sklearn": "1.0.2", "lightgbm": "3.1.1", "rdkit": "2022.09.4"}
    spec = importlib.util.spec_from_file_location("pinned_aic_mvsa", str(root / "author/MVS_A.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rng = np.random.RandomState(90101)
    obj = module.sample_analysis(rng.randint(0, 2, size=(100, 16)).astype(np.float32),
                                 np.array([0, 1] * 50), params="default", verbose=False, seed=90101)
    obj.params["num_threads"] = 1
    obj.get_model()
    values = obj.get_importance()
    assert values.shape == (100,) and np.isfinite(values).all()
    return {"status": "PASS_ORIGINAL_VERSION_CPU_RUNTIME_SMOKE", "versions": versions,
            "synthetic_fits": 1, "molecular_fits": 0, "confirmation_values_analyzed": False,
            "original_author_code_used": True, "iterations_observed": obj.n_estimators,
            "interpreter_sha256": sha(root / "python/bin/python3.8")}


def stored_index(text, seen):
    value = int(text)
    assert value >= 0 and value not in seen, "DUPLICATE_OR_NEGATIVE_SOURCE_INDEX"
    seen.add(value)
    return value


def protect(root, permit):
    import rdkit
    from rdkit import Chem, RDLogger

    assert sys.version_info[:2] == (3, 12) and rdkit.__version__ == "2026.09.1"
    RDLogger.DisableLog("rdApp.warning")
    RDLogger.DisableLog("rdApp.error")
    selected = read(root / "inputs/metadata-admission.json")["selected"]
    campaign = permit["campaign"]
    metadata = next(r for r in selected if r["campaign"] == campaign)
    intake = next(r for r in read(root / "inputs/opaque-intake.json")["files"] if r["campaign"] == campaign)
    source = root / "data" / (campaign.replace("/", "-") + ".csv")
    assert sha(source) == intake["sha256"] and metadata["role"] == "DEVELOPMENT_EXPOSED"
    protection = read(root / "inputs/protection-private.json")
    assert protection["outcome_values_present"] is False
    assert metadata["target"] not in protection["uniprot_accessions"]
    protected = set(protection["canonical_smiles"])
    canonical, seen, duplicates = {}, {}, set()
    original_indices = set()
    counts = {"source_rows": 0, "invalid_structures": 0, "protected_excluded": 0,
              "canonical_duplicate_rows_excluded": 0, "retained_primary_rows": 0,
              "eligible_confirmation_observations": 0}
    with source.open(newline="") as inp:
        reader = csv.DictReader(inp)
        assert set(reader.fieldnames) == {"", "SMILES", "Primary", "Score", "Confirmatory"}
        for i, row in enumerate(reader):
            counts["source_rows"] += 1
            assert counts["source_rows"] <= 2000000
            stored_index(row[""], original_indices)
            molecule = Chem.MolFromSmiles(row["SMILES"])
            if molecule is None:
                counts["invalid_structures"] += 1
                continue
            value = Chem.MolToSmiles(molecule, canonical=True, isomericSmiles=True)
            if value in protected:
                counts["protected_excluded"] += 1
                continue
            canonical[i] = value
            if value in seen:
                duplicates.update((seen[value], i))
            else:
                seen[value] = i
    output = root / "admission" / permit["output_name"]
    output.mkdir(parents=True, exist_ok=False)
    projection, sealed = output / "primary-projection.csv", output / "confirmation-sealed.csv"
    with source.open(newline="") as inp, projection.open("x", newline="") as public, sealed.open("x", newline="") as private:
        writer, evaluator = csv.writer(public), csv.writer(private)
        writer.writerow(["record_id", "source_row", "SMILES", "canonical_smiles", "Primary", "Score", "confirmation_observed", "source_index"])
        evaluator.writerow(["record_id", "raw_confirmatory"])
        for i, row in enumerate(csv.DictReader(inp)):
            if i not in canonical:
                continue
            if i in duplicates:
                counts["canonical_duplicate_rows_excluded"] += 1
                continue
            primary = float(row["Primary"])
            assert primary in (0.0, 1.0)
            observed = row["Confirmatory"] != ""
            eligible = primary == 1.0 and observed
            if eligible:
                assert math.isfinite(float(row["Score"]))
            identifier = campaign.replace("/", "_") + ":" + str(i)
            writer.writerow([identifier, i, row["SMILES"], canonical[i], int(primary), row["Score"], int(observed), int(row[""])])
            counts["retained_primary_rows"] += 1
            if eligible:
                evaluator.writerow([identifier, row["Confirmatory"]])  # Opaque text; no numerical conversion.
                counts["eligible_confirmation_observations"] += 1
    assert counts["eligible_confirmation_observations"] <= 100000
    budgets = sorted({int(math.ceil(f * counts["eligible_confirmation_observations"])) for f in (0.01, 0.02, 0.05, 0.10, 0.20)})
    return {"status": "PASS_BLINDED_STRUCTURE_SUPPORT" if counts["eligible_confirmation_observations"] else "NOT_EVALUABLE_EMPTY_SUPPORTED_UNIVERSE",
            "campaign": campaign, "counts": counts, "budgets": budgets,
            "projection": str(projection.relative_to(root)), "projection_sha256": sha(projection),
            "sealed": str(sealed.relative_to(root)), "sealed_sha256": sha(sealed),
            "source_sha256": intake["sha256"], "confirmation_values_analyzed": False,
            "protected_identities_disclosed": False, "final16_payloads_opened": False}


def main():
    permit = read(sys.argv[1])
    root = Path(permit["task_root"])
    assert root == Path.home() / "curaloop-tasks/lr-cf1-20261109-v1" and root.resolve() == root
    assert read(root / "inputs/owner-source-a.json")["choice"] == "A"
    for relative, expected in permit["code_pins"].items():
        assert sha(root / "code" / relative) == expected
    job = root / "jobs" / permit["attempt"]
    guard = CostedGuard(job / "resource.json", permit)
    try:
        new(job / "kernel-proof.json", guard.kernel_proof())
        action = permit["handler"]
        assert action in ("environment", "smoke", "protect")
        result = {"environment": environment, "smoke": smoke, "protect": protect}[action](root, permit)
        new(job / "result.json", result)
        guard.finish("PASS" if result["status"].startswith("PASS") else "NOT_EVALUABLE")
    except BaseException as error:
        new(job / "failure.json", {"type": type(error).__name__, "message": str(error)[:240]})
        guard.finish("FAIL")
        raise


if __name__ == "__main__":
    main()
