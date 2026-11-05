"""Constructed nested-weighting, pairing and honest uncertainty regressions."""

import pytest

from tools.analyze_goal4_v1 import compute_pair, descriptive_interval, grouped_values, paired_group_effects


def row(task, group, seed, hits):
    return {"task_id": task, "family_id": group, "seed": seed, "operation": "fixed", "metrics": {"new_hits": hits}}


def test_nested_means_weight_groups_and_assays_instead_of_seed_counts():
    rows = [row("a1", "a", 1, 0), row("a1", "a", 2, 2), row("a2", "a", 1, 3), row("b1", "b", 1, 10)]
    values = grouped_values(rows, lambda r: r["metrics"]["new_hits"])
    assert values == {"a": 2, "b": 10}


def test_paired_effects_retain_losses_and_fail_on_missing_or_duplicate_pairs():
    planner = [row("a1", "a", 1, 2), row("a1", "a", 2, 0), row("b1", "b", 1, 3)]
    reference = [row("a1", "a", 2, 2), row("a1", "a", 1, 4), row("b1", "b", 1, 2)]
    assert paired_group_effects(planner, reference) == {"a": -2, "b": 1}
    with pytest.raises(ValueError, match="Matched unique"):
        paired_group_effects(planner, reference[:-1])
    with pytest.raises(ValueError, match="Matched unique"):
        paired_group_effects(planner + planner[:1], reference)


def test_group_bootstrap_is_deterministic_descriptive_and_does_not_invent_groups():
    first = descriptive_interval([-2, 2])
    assert first == descriptive_interval([-2, 2])
    assert first["mean"] == 0 and first["groups"] == 2
    assert first["descriptive_group_bootstrap_95_interval"] == [-2, 2]
    assert not first["independent_population_coverage_certified"]
    single = descriptive_interval([-3])
    assert single["groups"] == 1
    assert single["descriptive_group_bootstrap_95_interval"] == [-3, -3]
    assert not single["independent_population_coverage_certified"]


def test_unmatched_computation_never_gets_a_matched_timing_ratio():
    a = {"decisions": [{"public_state_sha256": "state"}], "scientific_sha256": "result", "policy_wall_seconds": 6, "policy_cpu_seconds": 4}
    b = {"decisions": [{"public_state_sha256": "state"}], "scientific_sha256": "result", "policy_wall_seconds": 3, "policy_cpu_seconds": 2}
    assert compute_pair(a, b)["screened_over_dense_wall_ratio"] == 2
    mismatch = compute_pair({**a, "scientific_sha256": "different"}, b)
    assert mismatch["pairing_status"].startswith("FAIL")
    assert mismatch["screened_over_dense_wall_ratio"] is None
    assert mismatch["raw_unqualified_wall_ratio"] == 2
