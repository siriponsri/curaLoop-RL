"""Frozen equal-component estimands and conservative D2 attribution gate."""

import itertools

import numpy as np

METRICS = ("new_positives", "scientific_cpu_seconds", "new_deliveries", "interruptions",
           "feasibility_fallbacks", "gate_decisions", "delivered_overrides", "initial_fit_count")


def estimate(rows, metric, seed=None, component=None):
    selected = [r for r in rows if (seed is None or r["spec"]["seed"] == seed)
                and (component is None or r["component"] == component)]
    groups = sorted({r["component"] for r in selected})
    assert groups
    return float(np.mean([np.mean([np.mean([r[metric] for r in selected if r["task_id"] == task])
                                  for task in sorted({r["task_id"] for r in selected if r["component"] == group})])
                          for group in groups]))


def preference(candidate, baseline, hit_gain=1., loss=.25):
    return ((candidate["new_positives"] - baseline["new_positives"] >= hit_gain
             and candidate["scientific_cpu_seconds"] <= 1.1 * baseline["scientific_cpu_seconds"])
            or (candidate["scientific_cpu_seconds"] <= .8 * baseline["scientific_cpu_seconds"]
                and baseline["new_positives"] - candidate["new_positives"] <= loss))


def dominates(a, b):
    return (a["new_positives"] >= b["new_positives"] and
            a["scientific_cpu_seconds"] <= b["scientific_cpu_seconds"] and
            (a["new_positives"] > b["new_positives"] or
             a["scientific_cpu_seconds"] < b["scientific_cpu_seconds"]))


def analyze(rows, require_attribution=True, budget=32):
    arms = sorted({r["spec"]["control"] for r in rows})
    contexts = {}
    for arm in arms:
        values = [r for r in rows if r["spec"]["control"] == arm]
        assert len(values) == 60 and all(r["status"] == "PASS" and not r["cpu_violation"] for r in values)
        contexts[arm] = {(r["task_id"], r["spec"]["n0"], r["spec"]["seed"]): r for r in values}
        assert len(contexts[arm]) == 60
    keys = set(contexts["candidate_v1"])
    assert all(set(v) == keys for v in contexts.values())
    for key in keys:
        matched = [v[key] for v in contexts.values()]
        assert len({r["spec"]["cpu"] for r in matched}) == 1, "UNMATCHED_CORE"
        assert len({r["spec"]["input_sha256"] for r in matched}) == 1
    summary = {a: {m: estimate(list(contexts[a].values()), m) for m in METRICS} for a in arms}
    groups = sorted({r["component"] for r in rows})
    assert len(groups) == 4
    components = {g: {a: {m: estimate(list(contexts[a].values()), m, component=g) for m in METRICS}
                      for a in arms} for g in groups}
    seeds = sorted({r["spec"]["seed"] for r in rows})
    assert len(seeds) == 5
    intervals = {}
    for arm in arms:
        if arm == "candidate_v1":
            continue
        intervals[arm] = {}
        for metric in ("new_positives", "scientific_cpu_seconds"):
            differences = np.array([estimate(list(contexts["candidate_v1"].values()), metric, seed=s)
                                    - estimate(list(contexts[arm].values()), metric, seed=s) for s in seeds])
            boot = np.array([np.mean(differences[list(index)]) for index in itertools.product(range(5), repeat=5)])
            intervals[arm][metric] = {"mean_difference": float(np.mean(differences)),
                                     "conditional_seed_95_percentile_interval": np.quantile(boot, [.025, .975]).tolist()}
    candidate, g1, gk2 = (summary[a] for a in ("candidate_v1", "G1", "Gk2"))
    margin = .25 * budget / 32
    controls = [a for a in arms if a not in ("candidate_v1", "candidate_v0", "no_history_v1")]
    gate = {
        "G1_loss_and_saving": g1["new_positives"] - candidate["new_positives"] <= margin
                              and candidate["scientific_cpu_seconds"] <= .8 * g1["scientific_cpu_seconds"],
        "Gk2_usefulness": preference(candidate, gk2, budget / 32, margin),
        "component_coverage": sum(components[g]["G1"]["new_positives"] - components[g]["candidate_v1"]["new_positives"] <= margin for g in groups) >= 3,
        "not_control_dominated": not any(dominates(summary[a], candidate) for a in controls),
        "complete_matched_support": True,
    }
    attribution = {"status": "NOT_ASSIGNED_TRANSFER"}
    if require_attribution:
        assert "no_history_v1" in arms and "candidate_v0" in arms
        attribution = {
            "history_usefulness": preference(candidate, summary["no_history_v1"]),
            "round1_not_dominated_by_v0": not dominates(summary["candidate_v0"], candidate),
            "delivered_override_in_each_component": all(components[g]["candidate_v1"]["delivered_overrides"] > 0 for g in groups),
        }
        gate["attribution"] = all(attribution.values())
    return {"schema": "curaloop.lr_d23.aggregate.v1", "status": "PASS_D2" if all(gate.values()) else "INCONCLUSIVE_D2",
            "unit_count": len(rows), "means": summary, "components": components, "contrasts": intervals,
            "gate": gate, "attribution": attribution, "dominating_controls": [a for a in controls if dominates(summary[a], candidate)],
            "interval_scope": "joint evaluation-seed resampling conditional on these six exposed assays/four annotation components; not biological population uncertainty",
            "final_outcomes_open": False}
