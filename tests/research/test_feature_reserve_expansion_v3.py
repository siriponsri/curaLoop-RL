"""Revision A preserves the scientific boundary and expands a finite reserve."""

import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import pytest

from research.benchmark_v3 import prepare_features as v1
from research.benchmark_v3 import prepare_features_v2 as v2

ROOT = Path(__file__).resolve().parents[2]


def test_previous_source_and_frozen_configuration_are_unchanged():
    for name, expected in {
        "research/benchmark_v3/prepare_features.py": "844b92327398431fc169693ffe8a86c91df2f2841e18230193b701ab260dec11",
        "research/configs/goal3_feature_preparation_v1.json": "e36cedf449cc9e4a2c3aa9612af08f7041e3fbc43f355955a0c321f7d3661035",
    }.items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected


def test_only_declared_entrypoint_and_output_identity_changes():
    expected = (ROOT / "research/benchmark_v3/prepare_features.py").read_text()
    expected = expected.replace(
        "Trusted feature-only extraction. Never emit source outcomes or arbitrary rows.",
        "Owner-approved reserve expansion A. Trusted structure projection only.",
    ).replace("goal3_feature_preparation_v1.json", "goal3_feature_preparation_v2.json")
    expected = expected.replace('out = RAW / "feature-cohort-v1"', 'out = RAW / "feature-cohort-v2"')
    assert (ROOT / "research/benchmark_v3/prepare_features_v2.py").read_text() == expected
    assert v1.CONFIG != v2.CONFIG


def test_only_reserve_and_version_provenance_change_in_configuration():
    old, new = (json.loads(module.CONFIG.read_text()) for module in (v1, v2))
    permitted = {
        "schema_version", "status", "maximum_attempted_families", "frozen_utc",
        "frozen_source_sha256", "parent_commit", "owner_revision", "supersedes_attempt",
    }
    assert {k: value for k, value in old.items() if k not in permitted} == {
        k: value for k, value in new.items() if k not in permitted
    }
    assert new["maximum_attempted_families"] == {"development": 40, "validation": 34, "final": 65}
    assert new["minimum_surviving_structures_per_assay"] == 128
    assert new["maximum_retained_structures_per_assay"] == 600
    assert new["desired_family_counts"] == {"development": 4, "validation": 2, "final": 12}


def test_metadata_only_reserve_matches_fixed_header_projection():
    config = json.loads(v2.CONFIG.read_text())
    registry_path = ROOT / config["family_registry"]
    assert v2.sha_file(registry_path) == config["family_registry_sha256"]
    registry = json.loads(registry_path.read_text())
    families, assays = v2.reserve(registry, config)
    assert Counter(f["role"] for f in families) == {"development": 40, "validation": 34, "final": 65}
    assert Counter(a["role"] for a in assays) == {"development": 116, "validation": 136, "final": 205}
    assert len({a["assay_id"] for a in assays}) == len(assays) == 457
    family_roles = {f["family_id"]: f["role"] for f in families}
    assert all(a["role"] == family_roles[a["family_id"]] for a in assays)
    headers = {m["name"]: m for m in json.loads((v2.RAW / "header-audit-v2.json").read_text())["members"]}
    sizes = [headers[f"fs-mol/{a['source_role']}/{a['assay_id']}.jsonl.gz"]["bytes"] for a in assays]
    assert sum(sizes) == 35_997_355
    assert max(sizes) == 4_712_666


def test_old_ranked_reserves_are_subsets_with_original_order():
    registry = json.loads((ROOT / json.loads(v2.CONFIG.read_text())["family_registry"]).read_text())
    old_families, old_assays = v1.reserve(registry, json.loads(v1.CONFIG.read_text()))
    new_families, new_assays = v2.reserve(registry, json.loads(v2.CONFIG.read_text()))
    for role in ("development", "validation", "final"):
        previous = [f for f in old_families if f["role"] == role]
        assert [f for f in new_families if f["role"] == role][:len(previous)] == previous
    old_ids = {a["assay_id"] for a in old_assays}
    assert [a for a in new_assays if a["assay_id"] in old_ids] == old_assays


@pytest.mark.parametrize("module", [v1, v2])
def test_hidden_values_cannot_change_structure_projection_or_purge(module):
    projected = [module.project_row(json.dumps({
        "SMILES": "CCO", "Assay_ID": "CHEMBL1", "Property": value,
        "RegressionProperty": value, "graph": value,
    }), "CHEMBL1") for value in (0, 1, None, {"private": [1, 2]})]
    assert projected == ["CCO"] * 4
    pools = {"dev": [], "val": [(0, "CCO"), (1, "CCC")], "final": [(0, "CCC"), (1, "CCN")]}
    support = {"dev": {"CCO"}, "val": {"CCO", "CCC"}, "final": {"CCC", "CCN"}}
    clean, _ = module.purge(pools, {"dev": "development", "val": "validation", "final": "final"}, set(), support)
    assert clean == {"dev": [], "val": [], "final": [(1, "CCN")]}
    with pytest.raises(module.PreparationError, match="INCOMPLETE_FIXED_COLLISION_SUPPORT"):
        module.purge(pools, {"dev": "development", "val": "validation", "final": "final"}, set(), {"val": {"CCO"}})


def test_v2_incomplete_capped_projection_aborts_instead_of_omitting_collision_pool():
    compressed = gzip.compress(b'{"SMILES":"CCO","Assay_ID":"CHEMBL1","Property":"private"}\n')
    config = json.loads(v2.CONFIG.read_text()) | {"maximum_row_bytes": 8}
    totals = Counter()
    with pytest.raises(v2.PreparationError, match="RESERVE_POOL_ROW_COUNT_OR_SIZE_LIMIT"):
        v2.read_member(io.BytesIO(compressed), {"bytes": len(compressed), "data_offset": 0}, "CHEMBL1", config, totals)
    assert totals["compressed_bytes"] == len(compressed)
    assert totals["expanded_bytes"] == 9
