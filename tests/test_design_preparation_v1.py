import json

import numpy as np
import pytest

from research.preparation_v1.candidate_audit import project_payload, select_ids, validate_url
from research.preparation_v1.candidates import CANDIDATES
from research.preparation_v1.design_sensitivity import (
    CONFIG,
    family_means,
    summarize,
    theoretical_variance,
)


@pytest.mark.parametrize(
    "suffix,kind",
    [
        ("assay/aid/743053/description/JSON", "description"),
        ("assay/aid/743053/cids/JSON?cids_type=all", "cids"),
        ("compound/cid/1,2/property/IsomericSMILES/JSON", "structures"),
    ],
)
def test_only_explicit_outcome_free_operations_are_allowed(suffix, kind):
    assert validate_url("https://pubchem.ncbi.nlm.nih.gov/rest/pug/" + suffix) == kind


@pytest.mark.parametrize(
    "url",
    [
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/concise/JSON",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/summary/JSON",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/record/JSON",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/cids/JSON?cids_type=active",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/cids/JSON?cids_type=%61ctive",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/cids/JSON?cids_type=all&activity=inactive",
        "https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/cids/JSON",
        "https://user:password@pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/description/JSON",
        "http://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/1/description/JSON",
        "https://example.org/rest/pug/assay/aid/1/description/JSON",
    ],
)
def test_outcome_filters_data_operations_and_unknown_origins_fail_closed(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_payload_projection_rejects_outcomes_and_does_not_export_unread_prose():
    d = {
        "PC_AssayContainer": [
            {"assay": {"descr": {"name": "metadata", "protocol": ["unread prose"]}}}
        ]
    }
    assert "protocol" not in project_payload("description", d)
    d["PC_AssayContainer"][0]["assay"]["data"] = [{"active": True}]
    with pytest.raises(ValueError, match="data section"):
        project_payload("description", d)
    with pytest.raises(AssertionError):
        project_payload(
            "structures",
            {"PropertyTable": {"Properties": [{"CID": 1, "SMILES": "CC", "ActivityOutcome": 2}]}},
        )


def test_fixed_census_does_not_promote_exposed_tasks_or_select_by_activity():
    assert len(CANDIDATES) == len({r["aid"] for r in CANDIDATES}) == 24
    assert not {743122, 743140, 720552} & {r["aid"] for r in CANDIDATES}
    assert select_ids(1, list(range(300))) == select_ids(1, list(reversed(range(300))))
    assert len(select_ids(1, list(range(300)))) == 200
    cfg = json.loads(CONFIG.read_text())
    assert cfg["primary_material_margin_selected"] is None
    assert not cfg["new_outcome_values_permitted"] and not cfg["final_execution_permitted"]


def test_seed_repeats_cannot_remove_family_uncertainty():
    p = {"sd_family": 1.0, "sd_task": 0.0, "sd_paired_seed": 0.0}
    a = family_means(np.random.default_rng(1), 100, 4, 1, 3, p, "gaussian")
    b = family_means(np.random.default_rng(1), 100, 4, 2, 100, p, "gaussian")
    np.testing.assert_array_equal(a, b)
    assert theoretical_variance(4, 1, 3, p) == theoretical_variance(4, 2, 100, p) == 0.25


def test_nested_paired_variance_and_null_coverage_match_declared_model():
    p = {"sd_family": 0.75, "sd_task": 0.75, "sd_paired_seed": 2.0}
    v = family_means(np.random.default_rng(1729), 30000, 8, 2, 10, p, "gaussian")
    assert np.var(v.mean(axis=1), ddof=1) == pytest.approx(
        theoretical_variance(8, 2, 10, p), rel=0.04
    )
    s = summarize(v, 0)
    assert 0.04 < s["prob_one_sided_lcb_gt_zero"] < 0.06
    assert 0.94 < s["two_sided_95_coverage"] < 0.96
