"""Constructed controls pairing checks, not diagnostic results."""

import copy

import pytest

from research.d1_v1.control_analysis import ARMS, summarize_controls


def units():
    return [dict(task_id="t", component="g", spec=dict(n0=0, seed=1, control=arm, input_sha256="same"),
                 new_positives=10, scientific_cpu_seconds=1 if arm == "G1" else .5,
                 new_deliveries=32, assigned_B=32, assigned_C=5) for arm in ARMS]


def test_controls_pair_correctly_and_do_not_require_more_hits_for_saving():
    out = summarize_controls(units())
    assert out["arms"]["Gk_k4"]["comparisons"]["G1"]["meets_mean_saving_preference"]
    assert not out["arms"]["Gk_k4"]["comparisons"]["G1"]["meets_mean_discovery_preference"]


def test_missing_or_duplicate_control_is_rejected():
    with pytest.raises(AssertionError, match="MISSING_MATCHED_CONTROL"):
        summarize_controls(units()[:-1])
    with pytest.raises(AssertionError, match="DUPLICATE_CONTROL_UNIT"):
        summarize_controls(units() + units()[:1])


def test_different_cost_or_input_cannot_be_a_matched_comparison():
    rows = units()
    rows[0]["assigned_C"] = 6
    with pytest.raises(AssertionError):
        summarize_controls(rows)
    rows = units()
    rows[0]["spec"]["input_sha256"] = "different"
    with pytest.raises(AssertionError):
        summarize_controls(rows)


def test_summary_is_read_only():
    rows = units()
    before = copy.deepcopy(rows)
    summarize_controls(rows)
    assert rows == before
