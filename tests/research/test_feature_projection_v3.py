"""Adversarial outcome noninterference and fixed-pool chemical purge checks."""

import gzip
import io
import json
from collections import Counter

import pytest

from research.benchmark_v3.prepare_features import (
    PreparationError,
    chemical_audit,
    project_row,
    purge,
    read_member,
    unique_structures,
)


def test_arbitrary_hidden_outcomes_cannot_change_projection_or_duplicate_rule():
    rows = []
    for value in (0, 1, None, "secret-outcome", {"activity": float("nan")}):
        line = json.dumps(
            {
                "SMILES": "CCO",
                "Assay_ID": "CHEMBL1",
                "Property": value,
                "RegressionProperty": value,
                "LogRegressionProperty": value,
                "graph": value,
            }
        )
        rows.append(project_row(line, "CHEMBL1"))
    assert set(rows) == {"CCO"}
    assert unique_structures([(0, "CCO"), (1, "CCC"), (2, "CCO")]) == [(1, "CCC")]


def test_projection_uses_explicit_assay_identity_and_sanitizes_json():
    with pytest.raises(PreparationError, match="SOURCE_ASSAY_IDENTITY_MISMATCH"):
        project_row('{"SMILES":"CCO","Assay_ID":"CHEMBL2","Property":"secret"}', "CHEMBL1")
    with pytest.raises(PreparationError) as caught:
        project_row("secret-outcome-not-json", "CHEMBL1")
    assert str(caught.value) == "INVALID_JSON_ROW"


def test_cross_role_purge_removes_from_every_role_and_preserves_within_role():
    pools = {
        "a": [(0, "CCO"), (1, "CCC"), (2, "CCN")],
        "b": [(0, "CCO"), (1, "CCCC")],
        "c": [(0, "CCC"), (1, "CO")],
    }
    roles = {"a": "development", "b": "final", "c": "development"}
    clean, counts = purge(pools, roles, {"CCN"})
    assert clean == {"a": [(1, "CCC")], "b": [(1, "CCCC")], "c": [(0, "CCC"), (1, "CO")]}
    assert counts["a"]["cross_role_rows_removed"] == 1
    assert counts["a"]["prior_exposure_rows_removed"] == 1


def test_member_integrity_and_row_bound_without_outcome_emission():
    config = {
        "maximum_member_compressed_bytes": 10000,
        "maximum_total_compressed_bytes": 10000,
        "maximum_rows_per_assay": 3,
        "maximum_row_bytes": 1024,
        "maximum_member_expanded_bytes": 10000,
        "maximum_total_expanded_bytes": 10000,
        "maximum_total_canonical_rows": 10,
    }
    source = b"".join(
        json.dumps({"SMILES": smi, "Assay_ID": "CHEMBL1", "Property": "private"}).encode() + b"\n"
        for smi in ("CCO", "CCC", "CCO")
    )
    data = gzip.compress(source)
    rows, support, stats = read_member(
        io.BytesIO(data), {"bytes": len(data), "data_offset": 0}, "CHEMBL1", config, Counter()
    )
    assert rows == [(1, "CCC")]
    assert support == {"CCO", "CCC"}
    assert stats["source_rows"] == 3
    assert stats["duplicate_structure_rows_removed"] == 2
    assert "private" not in json.dumps(stats)
    with pytest.raises(PreparationError, match="TRUNCATED_SOURCE_MEMBER"):
        read_member(
            io.BytesIO(data[:-1]),
            {"bytes": len(data), "data_offset": 0},
            "CHEMBL1",
            config,
            Counter(),
        )


def test_duplicate_or_ineligible_pool_still_blocks_cross_role_collision():
    pools = {"dev": [], "final": [(0, "CCO"), (1, "CCCC")]}
    clean, _ = purge(
        pools,
        {"dev": "development", "final": "final"},
        set(),
        {"dev": {"CCO"}, "final": {"CCO", "CCCC"}},
    )
    assert clean["final"] == [(1, "CCCC")]
    with pytest.raises(PreparationError, match="INCOMPLETE_FIXED_COLLISION_SUPPORT"):
        purge(pools, {"dev": "development", "final": "final"}, set(), {"final": {"CCO"}})


def test_failed_bounded_read_is_charged_and_cannot_become_an_empty_collision_pool():
    data = gzip.compress(b'{"SMILES":"CCO","Assay_ID":"CHEMBL1"}\n')
    config = {
        "maximum_member_compressed_bytes": 10000,
        "maximum_total_compressed_bytes": 10000,
        "maximum_rows_per_assay": 3,
        "maximum_row_bytes": 4,
        "maximum_member_expanded_bytes": 10000,
        "maximum_total_expanded_bytes": 10000,
        "maximum_total_canonical_rows": 10,
    }
    totals = Counter()
    with pytest.raises(PreparationError, match="RESERVE_POOL_ROW_COUNT_OR_SIZE_LIMIT"):
        read_member(
            io.BytesIO(data), {"bytes": len(data), "data_offset": 0}, "CHEMBL1", config, totals
        )
    assert totals["compressed_bytes"] == len(data)
    assert totals["expanded_bytes"] == 5


def test_chemical_audit_computes_exact_overlap_and_excludes_empty_scaffolds():
    from rdkit.Chem import rdFingerprintGenerator

    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    artifacts = [
        {
            "task_id": "a",
            "role": "development",
            "records": [{"canonical_smiles": "CCO", "scaffold": ""}],
        },
        {"task_id": "b", "role": "final", "records": [{"canonical_smiles": "CCC", "scaffold": ""}]},
    ]
    report = chemical_audit(artifacts, generator, 0.8, {"CCCC"})
    assert report["cross_role_pairs"][0]["exact_canonical_overlap"] == 0
    assert report["cross_role_pairs"][0]["shared_nonempty_scaffolds"] == 0
    assert report["roles"]["final"]["acyclic_unique_structures"] == 1
    artifacts[1]["records"][0]["canonical_smiles"] = "CCO"
    with pytest.raises(PreparationError, match="SELECTED_CROSS_ROLE_EXACT_OVERLAP"):
        chemical_audit(artifacts, generator, 0.8)
