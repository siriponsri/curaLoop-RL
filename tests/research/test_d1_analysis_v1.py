"""Constructed pairing and aggregation checks before D1 outcome analysis."""

import copy

import pytest

from research.d1_v1.analysis import balanced, pair, summarize


def branches():
    spec = dict(prefix_job="p", snapshot=1, regime="cheap", cap=5, task_id="t",
                n0=0, seed=1, predictor="rf", input_sha256="same")
    return {op: {"result": {"spec": dict(spec), "new_deliveries": 2, "new_positives": 1},
                 "trace": [{"query": 1, "delivered_label": 1, "actual_operation": "COLD_UNIFORM"},
                           {"query": 2, "delivered_label": 0, "actual_operation": op}]}
            for op in ("REUSE", "UPDATE", "PLAN")}


def test_balancing_uses_components_and_assays_not_row_count():
    rows = [{"component": "a", "task_id": "a1", "value": 0}] * 8
    rows += [{"component": "a", "task_id": "a2", "value": 2},
             {"component": "b", "task_id": "b1", "value": 5}]
    assert balanced(rows, "value")["mean"] == 3


def test_empty_support_is_unknown_not_zero_effect():
    assert balanced([], "value")["mean"] is None


@pytest.mark.parametrize("field,value", [("seed", 99), ("cap", 6), ("input_sha256", "other"),
                                        ("snapshot", 2), ("prefix_job", "other")])
def test_pair_rejects_mismatched_counterfactuals(field, value):
    values = branches()
    values["PLAN"]["result"]["spec"][field] = value
    with pytest.raises(AssertionError, match="UNMATCHED_COUNTERFACTUAL"):
        pair(values, 1)


def test_pair_rejects_missing_operation():
    values = branches()
    del values["UPDATE"]
    with pytest.raises(AssertionError):
        pair(values, 1)


def test_pair_preserves_cold_override_for_support_decision():
    values = branches()
    values["PLAN"]["trace"][1]["actual_operation"] = "COLD_UNIFORM"
    assert pair(values, 1)["PLAN"]["actual_operation"] == "COLD_UNIFORM"


def test_pair_checks_new_discovery_accounting():
    values = branches()
    values["REUSE"]["result"]["new_positives"] = 2
    with pytest.raises(AssertionError):
        pair(values, 1)


def test_summary_does_not_erase_unsupported_assigned_states():
    row = dict(component="a", task_id="t", regime="cheap", contrast="UPDATE-REUSE",
               executed_support=False, support_reason="COLD", hit_delta=0, cpu_delta=0,
               delivery_delta=0, process_cpu_delta=0, choice_changed=False)
    data = [row, dict(row, executed_support=True, support_reason="SUPPORTED", hit_delta=2)]
    before = copy.deepcopy(data)
    out = summarize(data)["cheap"]["UPDATE-REUSE"]
    assert out["assigned_hit_effect"]["mean"] == 1
    assert out["supported_hit_effect"]["mean"] == 2
    assert out["unsupported_reasons"] == {"COLD": 1}
    assert data == before
