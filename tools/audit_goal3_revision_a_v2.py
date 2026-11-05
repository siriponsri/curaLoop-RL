"""Read back feature artifacts and emit outcome-free preparation gate evidence."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from research.benchmark_v3.prepare_features_v2 import reserve, sha_file, write_new
from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/evidence/plan-a-20261105-v1"
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"


def main():
    output = PACKET / "revision-a-feature-readback-v2.json"
    if output.exists():
        raise FileExistsError("Keep every audit attempt.")
    guard = Guard(PACKET / "revision-a-audit-resources-v2.json", 180, 1024**3, 180)
    config_path = ROOT / "research/configs/goal3_feature_preparation_v2.json"
    config = json.loads(config_path.read_text())
    registry_path = ROOT / config["family_registry"]
    assert sha_file(registry_path) == config["family_registry_sha256"]
    registry = json.loads(registry_path.read_text())
    _, reserved = reserve(registry, config)
    out = RAW / "feature-cohort-v2"
    manifest = json.loads((out / "manifest.json").read_text())
    frozen = json.loads((PACKET / "feature-preparation-freeze-v2.json").read_text())
    assert manifest["identities"]["config_sha256"] == frozen["config_sha256"] == sha_file(config_path)
    for name, digest in frozen["source_sha256"].items():
        assert sha_file(ROOT / name) == digest
    assert len(reserved) == len(manifest["all_attempts"]) == 457
    assert [a["assay_id"] for a in reserved] == [a["assay_id"] for a in manifest["all_attempts"]]
    assert not any(manifest[k] for k in (
        "outcome_values_emitted", "semantic_outcome_use", "final_evaluation", "final_labels_prepared"
    ))
    registry_assays = {a["assay_id"]: a for a in registry["assays"]}
    structure_roles, family_roles = defaultdict(set), defaultdict(set)
    groups, assays, structures, source_rows = defaultdict(set), Counter(), Counter(), set()
    feature_hashes = {}
    for selected in manifest["selected_assays"]:
        aid, role = selected["assay_id"], selected["role"]
        original = registry_assays[aid]
        assert selected["family_id"] == original["family_id"] and role == original["role"]
        path = (out / selected["feature_file"]).resolve()
        assert path.parent == out.resolve() and sha_file(path) == selected["feature_sha256"]
        feature = json.loads(path.read_text())
        assert set(feature) == {
            "task_id", "role", "family_id", "family", "source_role", "source_member",
            "member_sha256", "records", "outcome_values_present"
        }
        assert feature["task_id"] == aid and feature["role"] == role
        assert feature["family_id"] == selected["family_id"]
        assert feature["member_sha256"] == selected["member_sha256"]
        assert feature["outcome_values_present"] is False
        records = feature["records"]
        assert len(records) == selected["retained_structures"]
        assert config["minimum_surviving_structures_per_assay"] <= len(records) <= config["maximum_retained_structures_per_assay"]
        assert len({r["candidate_id"] for r in records}) == len(records)
        assert len({r["canonical_smiles"] for r in records}) == len(records)
        assert len({r["source_row"] for r in records}) == len(records)
        for record in records:
            assert set(record) == {"candidate_id", "canonical_smiles", "source_row", "morgan_on_bits", "scaffold"}
            assert record["candidate_id"] == "s-" + hashlib.sha256(record["canonical_smiles"].encode()).hexdigest()
            assert type(record["source_row"]) is int and record["source_row"] >= 0
            assert all(type(bit) is int and 0 <= bit < 1024 for bit in record["morgan_on_bits"])
            assert len(set(record["morgan_on_bits"])) == len(record["morgan_on_bits"])
            structure_roles[record["canonical_smiles"]].add(role)
        groups[role].add(feature["family_id"])
        family_roles[feature["family_id"]].add(role)
        assays[role] += 1
        structures[role] += len(records)
        feature_hashes[selected["feature_file"]] = selected["feature_sha256"]
    assert not any(len(roles) > 1 for roles in structure_roles.values())
    assert not any(len(roles) > 1 for roles in family_roles.values())
    counts = {role: len(groups[role]) for role in config["desired_family_counts"]}
    assert counts == manifest["selected_family_counts"]
    assert dict(assays) == manifest["selected_assay_counts"]
    chemical_path = out / manifest["chemical_audit_file"]
    assert sha_file(chemical_path) == manifest["chemical_audit_sha256"]
    chemical = json.loads(chemical_path.read_text())
    assert all(p["exact_canonical_overlap"] == 0 for p in chemical["cross_role_pairs"])
    assert all(p["exact_canonical_overlap"] == 0 for p in chemical["prior_reference_overlap"].values())
    assert chemical["chemical_ood_claim"] is False
    passed = counts == config["desired_family_counts"]
    assert manifest["status"] == ("PASS_FEATURE_COHORT" if passed else "FAIL_FAMILY_QUOTAS")
    report = {
        "artifact_integrity": "PASS", "required_group_gate": "PASS" if passed else "FAIL",
        "selected_group_counts": counts, "selected_assay_counts": dict(assays),
        "retained_structure_rows": dict(structures), "full_reserved_assays": len(reserved),
        "manifest_sha256": sha_file(out / "manifest.json"), "feature_sha256": feature_hashes,
        "audit_source_sha256": sha_file(Path(__file__)),
        "cross_role_exact_canonical_overlap": 0, "cross_role_group_overlap": 0,
        "source_or_final_outcomes_opened_by_this_audit": False,
        "chemical_ood_claim": False, "independent_evolutionary_family_claim": False,
        "goal4_readiness": "NEEDS_DATASET_CARD_AND_SCOPED_REVIEW" if passed else "FAIL_REQUIRED_GROUP_COUNTS",
    }
    write_new(output, report)
    guard.finish("PASS")
    print(json.dumps({k: v for k, v in report.items() if k != "feature_sha256"}, indent=2))


if __name__ == "__main__":
    main()
