"""Constructed privacy/estimand regressions; no molecular data or real labels."""

from copy import deepcopy

import pytest

from research.confirmation_v1.contracts import (
    GATE_NAMES,
    ConfirmationObservation,
    EvidenceError,
    confirmation_universe,
    evaluate_selection,
    validate_report,
)


def pending():
    return {"schema": "curaloop.confirmation.offline-report.v1", "status": "WAITING_INPUT",
            "estimand": "OBSERVATION_SUPPORTED_PRIMARY_HITS_ONLY", "final16_access": False,
            "new_selector_training": False, "gates": dict.fromkeys(GATE_NAMES, False),
            "metrics": {"confirmed_positives": None, "positive_structure_groups": None}}


def test_missing_is_not_a_negative_and_inconclusive_is_not_renamed_inactive():
    assert ConfirmationObservation(False, None).state == "NOT_OBSERVED"
    assert ConfirmationObservation(True, 0).state == "SOURCE_NONPOSITIVE_INACTIVE_OR_INCONCLUSIVE"
    with pytest.raises(EvidenceError):
        ConfirmationObservation(False, 0)
    with pytest.raises(EvidenceError):
        ConfirmationObservation(True, None)


def test_universe_excludes_primary_nonhits_and_unobserved_confirmations():
    observations = [ConfirmationObservation(True, 1), ConfirmationObservation(False, None),
                    ConfirmationObservation(True, 0), ConfirmationObservation(True, 1)]
    assert confirmation_universe([1, 1, 1, 0], observations, True) == (0, 2)
    with pytest.raises(EvidenceError):
        confirmation_universe([1, 1, 1, 0], observations, False)


def test_hidden_value_swap_cannot_change_support_mask():
    a = [ConfirmationObservation(True, 0), ConfirmationObservation(True, 1)]
    b = [ConfirmationObservation(True, 1), ConfirmationObservation(True, 0)]
    assert confirmation_universe([1, 1], a, True) == confirmation_universe([1, 1], b, True)


def test_confirmation_evaluation_is_gated_and_no_missing_or_duplicate_selection():
    obs = [ConfirmationObservation(True, 1), ConfirmationObservation(False, None)]
    for selection, universe, released in [([0], [0], False), ([1], [0], True),
                                          ([0, 0], [0], True), ([0], [0, 1], True)]:
        with pytest.raises(EvidenceError):
            evaluate_selection(selection, universe, obs, ["a", "b"], released)


def test_hit_and_positive_group_counts_are_distinct():
    obs = [ConfirmationObservation(True, y) for y in (1, 1, 0, 1)]
    assert evaluate_selection([0, 1, 2, 3], [0, 1, 2, 3], obs, ["a", "a", "b", "c"], True) == {
        "confirmation_count": 4, "confirmed_positives": 3, "positive_structure_groups": 2}
    assert evaluate_selection([2], [0, 1, 2, 3], obs, ["a", "a", "b", "c"], True)["confirmed_positives"] == 0


def test_empty_scaffold_is_not_silently_a_common_group():
    with pytest.raises(EvidenceError):
        evaluate_selection([0], [0], [ConfirmationObservation(True, 1)], [""], True)


def test_unrun_metrics_must_be_null_not_zero():
    report = pending()
    validate_report(report)
    report["metrics"]["confirmed_positives"] = 0
    with pytest.raises(EvidenceError):
        validate_report(report)


@pytest.mark.parametrize("key", ["final16_access", "new_selector_training"])
def test_scope_cannot_be_changed_in_a_card(key):
    report = pending()
    report[key] = True
    with pytest.raises(EvidenceError):
        validate_report(report)


def test_whole_library_or_missing_gate_cannot_be_published():
    report = pending()
    report["estimand"] = "WHOLE_PRIMARY_LIBRARY"
    with pytest.raises(EvidenceError):
        validate_report(report)
    report = pending()
    del report["gates"]["rights"]
    with pytest.raises(EvidenceError):
        validate_report(report)


def test_all_gates_and_campaign_blocks_are_required_for_measured_report():
    report = pending()
    report.update(status="FEASIBILITY_COMPLETE", campaigns=4, source_experiment_blocks=2)
    report["metrics"] = {"confirmed_positives": 3, "positive_structure_groups": 2}
    for gate in GATE_NAMES:
        trial = deepcopy(report)
        trial["gates"] = dict.fromkeys(GATE_NAMES, True)
        trial["gates"][gate] = False
        with pytest.raises(EvidenceError):
            validate_report(trial)
    report["gates"] = dict.fromkeys(GATE_NAMES, True)
    validate_report(report)
    for campaigns, blocks in [(3, 2), (7, 2), (4, 1), (True, 2)]:
        trial = deepcopy(report)
        trial.update(campaigns=campaigns, source_experiment_blocks=blocks)
        with pytest.raises(EvidenceError):
            validate_report(trial)
