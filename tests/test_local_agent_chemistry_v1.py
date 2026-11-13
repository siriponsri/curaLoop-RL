"""Actual RDKit calculations and explicit row/filter accounting."""

import pytest

from curaloop_rd.local_agent_v1.chemistry import FilterSpec, compute, validate_csv


def test_real_formula_masses_filter_boundaries_and_rejected_rows():
    csv = (
        "compound_id,smiles\naspirin,CC(=O)Oc1ccccc1C(=O)O\n"
        "ethanol,CCO\nbad,not_a_molecule\nethanol,O\nmissing,\n"
    )
    result = compute(csv, FilterSpec(molecular_weight_max=100, logp_max=5, tpsa_max=140))
    assert result["counts"] == {"input_rows": 5, "valid": 2, "rejected": 3, "selected": 1}
    by_id = {r["compound_id"]: r for r in result["compounds"]}
    assert by_id["aspirin"]["molecular_weight"] == pytest.approx(
        9 * 12.011 + 8 * 1.008 + 4 * 15.999
    )
    assert by_id["ethanol"]["molecular_weight"] == pytest.approx(2 * 12.011 + 6 * 1.008 + 15.999)
    assert not by_id["aspirin"]["selected"] and by_id["ethanol"]["selected"]
    assert {r["reason"] for r in result["rejected"]} == {
        "INVALID_EMPTY_OR_TOO_LARGE_MOLECULE",
        "DUPLICATE_COMPOUND_ID",
        "MISSING_OR_TOO_LONG_SMILES",
    }
    assert result["units"]["molecular_weight"] == "g/mol"


def test_malformed_header_and_bounds_are_explicit_errors():
    for text in (
        "id,smiles\na,CCO\n",
        "compound_id,smiles,smiles\na,O,O\n",
        "compound_id,smiles\n",
    ):
        with pytest.raises(ValueError):
            validate_csv(text)
    with pytest.raises(ValueError, match="row limit"):
        validate_csv("compound_id,smiles\na,O\nb,CCO\n", max_rows=1)
    rows, rejected = validate_csv("compound_id,smiles\na,O,extra\n")
    assert not rows and rejected[0]["reason"] == "MALFORMED_CSV_ROW"


@pytest.mark.parametrize("value", [float("nan"), float("inf"), True])
def test_nonfinite_or_boolean_filters_are_rejected(value):
    with pytest.raises(ValueError):
        FilterSpec(logp_max=value)
