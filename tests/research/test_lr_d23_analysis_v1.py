"""Frozen weighting, matched-core rejection and conservative attribution."""

import copy

import pytest

from research.lr_d23_v1.analysis import analyze, estimate


def rows():
    output = []
    points = {"candidate_v1": (10., 1.), "G1": (10., 2.), "Gk2": (9., 1.),
              "Gk4": (8., .6), "T_k4_tau0.05": (9.5, 3.), "frozen_cache_greedy": (7., .1),
              "nearest_hit": (6., .01), "no_history_v1": (9., 1.), "candidate_v0": (9., 1.)}
    for arm, (hits, cpu) in points.items():
        for task, group in enumerate(("g0", "g1", "g1", "g2", "g3", "g3")):
            for n0 in (0, 16):
                for seed in range(5):
                    output.append(dict(status="PASS", cpu_violation=False, component=group, task_id=str(task),
                                       spec=dict(control=arm, cpu=69, input_sha256=str(task), n0=n0, seed=seed),
                                       new_positives=hits, scientific_cpu_seconds=cpu, new_deliveries=32,
                                       interruptions=0, feasibility_fallbacks=0, gate_decisions=30,
                                       delivered_overrides=2, initial_fit_count=1))
    return output


def test_gate_requires_usefulness_and_history_support():
    data = rows()
    result = analyze(data)
    assert result["status"] == "PASS_D2"
    assert result["contrasts"]["G1"]["new_positives"]["conditional_seed_95_percentile_interval"] == [0., 0.]
    for row in data:
        if row["spec"]["control"] == "no_history_v1":
            row["new_positives"] = 10.
    result = analyze(data)
    assert result["status"] == "INCONCLUSIVE_D2" and not result["attribution"]["history_usefulness"]


def test_component_weight_and_unmatched_core_rejected():
    data = rows()
    selected = [r for r in data if r["spec"]["control"] == "G1"]
    for row in selected:
        row["new_positives"] = int(row["component"][1:])
    assert estimate(selected, "new_positives") == 1.5
    changed = copy.deepcopy(data)
    changed[0]["spec"]["cpu"] = 70
    with pytest.raises(AssertionError, match="UNMATCHED_CORE"):
        analyze(changed)
