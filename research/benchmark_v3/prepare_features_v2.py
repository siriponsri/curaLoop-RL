"""Owner-approved reserve expansion A. Trusted structure projection only."""

import gzip
import hashlib
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"
CONFIG = ROOT / "research/configs/goal3_feature_preparation_v2.json"


class PreparationError(Exception):
    """Only fixed reason codes reach the outer log."""


def sha_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024**2), b""):
            digest.update(chunk)
    return digest.hexdigest()


def project_row(line, expected_assay):
    try:
        row = json.loads(line)
    except (ValueError, UnicodeError):
        raise PreparationError("INVALID_JSON_ROW") from None
    if not isinstance(row, dict) or type(row.get("SMILES")) is not str:
        raise PreparationError("INVALID_STRUCTURE_SCHEMA")
    if row.get("Assay_ID") != expected_assay:
        raise PreparationError("SOURCE_ASSAY_IDENTITY_MISMATCH")
    # Positive projection: outcome/property/graph/descriptor values are unused.
    return row["SMILES"]


def canonical(smiles):
    from rdkit import Chem, rdBase

    if len(smiles) > 4096:
        return None
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(smiles)
    if mol is None or not 1 <= mol.GetNumAtoms() <= 256:
        return None
    return Chem.MolToSmiles(mol, isomericSmiles=True)


def old_reference_structures():
    prior = json.loads((ROOT / "research/configs/goal_02_real_data_v1.json").read_text())
    paths = {
        assay: ROOT / f"research/raw_data/ncats-development-20261104/{assay}.smiles"
        for assay in ("ahr", "pparg", "p53")
    }
    refs, hashes = set(), {}
    for assay, path in paths.items():
        digest = sha_file(path)
        if digest != prior["raw_source_sha256"][assay]:
            raise PreparationError("PRIOR_EXPOSURE_SOURCE_HASH_MISMATCH")
        hashes[str(path.relative_to(ROOT))] = digest
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                # Previously exposed source only, never use the activity column.
                smi = canonical(line.split("\t", 1)[0].rstrip("\r\n"))
                if smi:
                    refs.add(smi)
    path = ROOT / "src/curaloop/resources/hiv_replay_v1.json.gz"
    digest = sha_file(path)
    hiv_manifest = json.loads((ROOT / "src/curaloop/resources/hiv_manifest.json").read_text())
    if digest != hiv_manifest["resource_sha256"]:
        raise PreparationError("PRIOR_HIV_SOURCE_HASH_MISMATCH")
    hashes[str(path.relative_to(ROOT))] = digest
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        rows = json.load(handle)
    for row in rows:
        smi = canonical(row["canonical_smiles"])
        if smi:
            refs.add(smi)
    return refs, hashes


def unique_structures(rows):
    counts = Counter(smi for _, smi in rows)
    return [(index, smi) for index, smi in rows if counts[smi] == 1]


def read_member(handle, header, aid, config, totals):
    size = header["bytes"]
    if size > config["maximum_member_compressed_bytes"]:
        raise PreparationError("RESERVE_POOL_COMPRESSED_MEMBER_LIMIT")
    if totals["compressed_bytes"] + size > config["maximum_total_compressed_bytes"]:
        raise PreparationError("GLOBAL_COMPRESSED_LIMIT")
    handle.seek(header["data_offset"])
    data = handle.read(size)
    if len(data) != size:
        raise PreparationError("TRUNCATED_SOURCE_MEMBER")
    totals["compressed_bytes"] += size
    rows, expanded = [], 0
    try:
        with gzip.GzipFile(fileobj=io.BytesIO(data)) as stream:
            for index in range(config["maximum_rows_per_assay"] + 1):
                line = stream.readline(config["maximum_row_bytes"] + 1)
                if not line:
                    break
                expanded += len(line)
                totals["expanded_bytes"] += len(line)
                if (
                    index >= config["maximum_rows_per_assay"]
                    or len(line) > config["maximum_row_bytes"]
                ):
                    raise PreparationError("RESERVE_POOL_ROW_COUNT_OR_SIZE_LIMIT")
                if totals["expanded_bytes"] > config["maximum_total_expanded_bytes"]:
                    raise PreparationError("GLOBAL_EXPANDED_LIMIT")
                if expanded > config["maximum_member_expanded_bytes"]:
                    raise PreparationError("RESERVE_POOL_EXPANDED_MEMBER_LIMIT")
                smi = canonical(project_row(line, aid))
                totals["source_rows_trusted_parsed"] += 1
                if smi:
                    rows.append((index, smi))
                    totals["canonical_rows"] += 1
                    totals["canonical_characters"] += len(smi)
                    if (
                        totals["canonical_rows"] > config["maximum_total_canonical_rows"]
                        or totals["canonical_characters"] > 50_000_000
                    ):
                        raise PreparationError("GLOBAL_CANONICAL_LIMIT")
    except (gzip.BadGzipFile, EOFError, OSError):
        raise PreparationError("INVALID_SOURCE_COMPRESSION") from None
    unique = unique_structures(rows)
    return (
        unique,
        {smi for _, smi in rows},
        {
            "member_sha256": hashlib.sha256(data).hexdigest(),
            "compressed_bytes": size,
            "expanded_bytes": expanded,
            "source_rows": index if not line else index + 1,
            "valid_structure_rows": len(rows),
            "duplicate_structure_rows_removed": len(rows) - len(unique),
            "unique_structure_rows": len(unique),
        },
    )


def reserve(registry, config):
    families, assays = [], []
    for role, limit in config["maximum_attempted_families"].items():
        ranked = sorted(
            [f for f in registry["family_records"] if f["role"] == role],
            key=lambda f: f["family_rank"],
        )
        for family in ranked[:limit]:
            families.append(family)
            rows = sorted(
                [a for a in registry["assays"] if a["family_id"] == family["family_id"]],
                key=lambda a: a["assay_rank"],
            )
            assays.extend(rows[: config["maximum_assays_attempted_per_family"]])
    return families, assays


def purge(pools, roles, references, supports=None):
    structure_roles = defaultdict(set)
    if supports is None:
        supports = {aid: {smi for _, smi in rows} for aid, rows in pools.items()}
    if set(supports) != set(pools):
        raise PreparationError("INCOMPLETE_FIXED_COLLISION_SUPPORT")
    for aid, structures in supports.items():
        for smi in structures:
            structure_roles[smi].add(roles[aid])
    shared = {smi for smi, rs in structure_roles.items() if len(rs) > 1}
    clean, counts = {}, {}
    for aid, rows in pools.items():
        clean[aid] = [(i, s) for i, s in rows if s not in references and s not in shared]
        counts[aid] = {
            "prior_exposure_rows_removed": sum(s in references for _, s in rows),
            "cross_role_rows_removed": sum(s in shared for _, s in rows),
            "surviving_unique_structures": len(clean[aid]),
            "removed_union_rows": len(rows) - len(clean[aid]),
            "reason_counts_may_overlap": True,
        }
    return clean, counts


def chemical_audit(artifacts, generator, threshold, prior_structures=()):
    from rdkit import Chem, DataStructs

    by_role = defaultdict(dict)
    by_role_assays = defaultdict(lambda: defaultdict(set))
    for artifact in artifacts:
        role = artifact["role"]
        for record in artifact["records"]:
            smi = record["canonical_smiles"]
            by_role[role][smi] = record["scaffold"]
            by_role_assays[role][smi].add(artifact["task_id"])
    roles = sorted(by_role)
    fps = {
        role: [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in sorted(by_role[role])]
        for role in roles
    }
    summaries = {}
    for role in roles:
        summaries[role] = {
            "unique_structures": len(by_role[role]),
            "structures_in_multiple_assays": sum(
                len(ids) > 1 for ids in by_role_assays[role].values()
            ),
            "unique_nonempty_scaffolds": len({s for s in by_role[role].values() if s}),
            "acyclic_unique_structures": sum(not s for s in by_role[role].values()),
        }
    pairs = []
    for i, a in enumerate(roles):
        for b in roles[i + 1 :]:
            exact = len(by_role[a].keys() & by_role[b].keys())
            if exact:
                raise PreparationError("SELECTED_CROSS_ROLE_EXACT_OVERLAP")
            scaffolds = len(
                {s for s in by_role[a].values() if s} & {s for s in by_role[b].values() if s}
            )
            nearest = {}
            for query, reference in ((a, b), (b, a)):
                maxima = [
                    max(DataStructs.BulkTanimotoSimilarity(fp, fps[reference]), default=0)
                    for fp in fps[query]
                ]
                nearest[query + "_to_" + reference] = {
                    "query_n": len(maxima),
                    "count_at_least_threshold": sum(v >= threshold for v in maxima),
                    "mean_nearest_tanimoto": sum(maxima) / len(maxima) if maxima else None,
                    "max_nearest_tanimoto": max(maxima, default=None),
                }
            pairs.append(
                {
                    "roles": [a, b],
                    "exact_canonical_overlap": exact,
                    "shared_nonempty_scaffolds": scaffolds,
                    "nearest": nearest,
                }
            )
    from rdkit.Chem.Scaffolds import MurckoScaffold

    prior_mols = [Chem.MolFromSmiles(smi) for smi in sorted(prior_structures)]
    prior_fps = [generator.GetFingerprint(mol) for mol in prior_mols]
    prior_scaffolds = {
        MurckoScaffold.MurckoScaffoldSmiles(mol=mol, includeChirality=False) for mol in prior_mols
    }
    prior_scaffolds.discard("")
    prior_audit = {}
    for role in roles:
        exact = len(set(prior_structures) & by_role[role].keys())
        if exact:
            raise PreparationError("SELECTED_PRIOR_EXPOSURE_EXACT_OVERLAP")
        maxima = [
            max(DataStructs.BulkTanimotoSimilarity(fp, prior_fps), default=0) for fp in fps[role]
        ]
        prior_audit[role] = {
            "exact_canonical_overlap": exact,
            "shared_nonempty_scaffolds": len(
                prior_scaffolds & {s for s in by_role[role].values() if s}
            ),
            "query_n": len(maxima),
            "count_at_least_threshold": sum(v >= threshold for v in maxima),
            "mean_nearest_tanimoto": sum(maxima) / len(maxima) if maxima else None,
            "max_nearest_tanimoto": max(maxima, default=None),
        }
    return {
        "status": "PASS_EXACT_PURGE_ONLY",
        "threshold": threshold,
        "roles": summaries,
        "cross_role_pairs": pairs,
        "prior_reference_n": len(prior_structures),
        "prior_reference_overlap": prior_audit,
        "chemical_ood_claim": False,
        "scaffold_and_analogue_purge": False,
    }


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write("\n")


def main():
    from tools.resource_guard_v1 import Guard

    config = json.loads(CONFIG.read_text())
    if config["status"] != "FROZEN_BEFORE_ASSAY_PARSE":
        raise PreparationError("PREPARATION_CONFIG_NOT_FROZEN")
    for name, expected in config.get("frozen_source_sha256", {}).items():
        path = (ROOT / name).resolve()
        if not path.is_relative_to(ROOT) or sha_file(path) != expected:
            raise PreparationError("FROZEN_PREPARER_SOURCE_MISMATCH")
    if not config.get("frozen_source_sha256"):
        raise PreparationError("MISSING_FROZEN_SOURCE_IDENTITIES")
    out = RAW / "feature-cohort-v2"
    out.mkdir(exist_ok=False)
    guard = Guard(
        out / "resources.json",
        config["wall_limit_seconds"],
        config["max_ram_bytes"],
        config["cpu_limit_seconds"],
    )
    try:
        from rdkit import Chem, rdBase
        from rdkit.Chem import rdFingerprintGenerator
        from rdkit.Chem.Scaffolds import MurckoScaffold

        if rdBase.rdkitVersion != "2026.09.1":
            raise PreparationError("RDKIT_VERSION_MISMATCH")
        registry_path = ROOT / config["family_registry"]
        if sha_file(registry_path) != config["family_registry_sha256"]:
            raise PreparationError("FAMILY_REGISTRY_HASH_MISMATCH")
        registry = json.loads(registry_path.read_text())
        header_path = RAW / "header-audit-v2.json"
        headers = {
            r["name"]: r
            for r in json.loads(header_path.read_text())["members"]
            if r["kind"] == "file"
        }
        policy_path = ROOT / "research/configs/goal3_feature_access_policy_v2.json"
        policy = json.loads(policy_path.read_text())
        if (
            policy["trusted_row_projection_allowlist"] != ["SMILES", "Assay_ID"]
            or policy["semantic_outcome_use_goal3"]
        ):
            raise PreparationError("ACCESS_POLICY_PROJECTION_MISMATCH")
        archive_hash = sha_file(RAW / "fsmol.tar")
        if archive_hash != policy["archive_sha256"]:
            raise PreparationError("SOURCE_ARCHIVE_HASH_MISMATCH")
        identity = {
            "config_sha256": sha_file(CONFIG),
            "preparer_sha256": sha_file(Path(__file__)),
            "family_registry_sha256": sha_file(registry_path),
            "header_index_sha256": sha_file(header_path),
            "access_policy_sha256": sha_file(policy_path),
            "archive_sha256": archive_hash,
            "rdkit": rdBase.rdkitVersion,
        }
        write_new(out / "frozen-inputs.json", {"identities": identity, "configuration": config})
        references, reference_hashes = old_reference_structures()
        families, assays = reserve(registry, config)
        write_new(
            out / "fixed-reserves.json",
            {"families": families, "assays": assays, "prior_source_hashes": reference_hashes},
        )
        totals = Counter()
        pools, supports, attempts = {}, {}, []
        with (RAW / "fsmol.tar").open("rb") as handle:
            for number, assay in enumerate(assays):
                aid, role = assay["assay_id"], assay["source_role"]
                member = f"fs-mol/{role}/{aid}.jsonl.gz"
                if member not in headers:
                    raise PreparationError("MISSING_FROZEN_DEFAULT_MEMBER")
                rows, support, stats = read_member(handle, headers[member], aid, config, totals)
                pools[aid] = rows
                supports[aid] = support
                attempts.append({**assay, "source_member": member, **stats})
                print(
                    json.dumps(
                        {
                            "phase": "FEATURE_ONLY",
                            "assay": aid,
                            "completed": number + 1,
                            "total": len(assays),
                        }
                    ),
                    flush=True,
                )
        roles = {a["assay_id"]: a["role"] for a in assays}
        clean, purge_counts = purge(pools, roles, references, supports)
        for attempt in attempts:
            attempt.update(purge_counts[attempt["assay_id"]])
            attempt["feature_eligible"] = (
                not attempt.get("eligibility_failure")
                and attempt["surviving_unique_structures"]
                >= config["minimum_surviving_structures_per_assay"]
            )
        selected, selected_families, artifacts = [], [], []
        by_id = {a["assay_id"]: a for a in attempts}
        selected_counts = Counter()
        generator = rdFingerprintGenerator.GetMorganGenerator(
            radius=2, fpSize=1024, includeChirality=False
        )
        for family in families:
            role = family["role"]
            if selected_counts[role] >= config["desired_family_counts"][role]:
                continue
            eligible = [
                by_id[a["assay_id"]]
                for a in assays
                if a["family_id"] == family["family_id"]
                and by_id[a["assay_id"]]["feature_eligible"]
            ]
            if not eligible:
                continue
            selected_counts[role] += 1
            selected_families.append(family)
            for assay in eligible[: config["maximum_selected_assays_per_family"]]:
                aid = assay["assay_id"]
                ranked = sorted(
                    clean[aid],
                    key=lambda row: hashlib.sha256(
                        (config["structure_rank_namespace"] + row[1]).encode()
                    ).hexdigest(),
                )
                records = []
                for index, smi in ranked[: config["maximum_retained_structures_per_assay"]]:
                    mol = Chem.MolFromSmiles(smi)
                    records.append(
                        {
                            "candidate_id": "s-" + hashlib.sha256(smi.encode()).hexdigest(),
                            "canonical_smiles": smi,
                            "source_row": index,
                            "morgan_on_bits": list(generator.GetFingerprint(mol).GetOnBits()),
                            "scaffold": MurckoScaffold.MurckoScaffoldSmiles(
                                mol=mol, includeChirality=False
                            ),
                        }
                    )
                artifact = {
                    "task_id": aid,
                    "role": role,
                    "family_id": assay["family_id"],
                    "family": assay["family"],
                    "source_role": assay["source_role"],
                    "source_member": assay["source_member"],
                    "member_sha256": assay["member_sha256"],
                    "records": records,
                    "outcome_values_present": False,
                }
                artifacts.append(artifact)
                filename = aid + ".features.json"
                write_new(out / filename, artifact)
                selected.append(
                    {
                        k: v
                        for k, v in assay.items()
                        if k not in ("source_internal_target_id_semantics",)
                    }
                    | {
                        "feature_file": filename,
                        "feature_sha256": sha_file(out / filename),
                        "retained_structures": len(records),
                    }
                )
        audit = chemical_audit(
            artifacts, generator, config["near_analogue_reporting_threshold"], references
        )
        write_new(out / "chemical-audit.json", audit)
        quotas_met = dict(selected_counts) == config["desired_family_counts"]
        report = {
            "status": "PASS_FEATURE_COHORT" if quotas_met else "FAIL_FAMILY_QUOTAS",
            "identities": identity,
            "selected_family_counts": dict(selected_counts),
            "selected_assay_counts": dict(Counter(a["role"] for a in selected)),
            "selected_families": selected_families,
            "selected_assays": selected,
            "all_attempts": attempts,
            "processing_totals": dict(totals),
            "reference_structure_count": len(references),
            "prior_source_hashes": reference_hashes,
            "trusted_physical_row_parse": True,
            "outcome_values_emitted": False,
            "semantic_outcome_use": False,
            "final_evaluation": False,
            "final_labels_prepared": False,
            "cross_role_exact_overlap_after_purge": sum(
                p["exact_canonical_overlap"] for p in audit["cross_role_pairs"]
            ),
            "chemical_audit_file": "chemical-audit.json",
            "chemical_audit_sha256": sha_file(out / "chemical-audit.json"),
        }
        write_new(out / "manifest.json", report)
        output_bytes = sum(p.stat().st_size for p in out.rglob("*") if p.is_file())
        if output_bytes > config["maximum_additional_output_bytes"]:
            raise PreparationError("OUTPUT_SIZE_LIMIT")
        guard.finish("PASS" if quotas_met else "FAIL", output_bytes=output_bytes)
        print(
            json.dumps(
                {
                    k: report[k]
                    for k in (
                        "status",
                        "selected_family_counts",
                        "selected_assay_counts",
                        "processing_totals",
                    )
                },
                indent=2,
            )
        )
        return 0 if quotas_met else 2
    except Exception as exc:
        code = str(exc) if isinstance(exc, PreparationError) else type(exc).__name__
        guard.finish("FAIL", sanitized_reason=code)
        write_new(
            out / "failure.json",
            {"status": "FAIL", "reason": code, "raw_exception_text_suppressed": True},
        )
        print(json.dumps({"status": "FAIL", "reason": code}), flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
