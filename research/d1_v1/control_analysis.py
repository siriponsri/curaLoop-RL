"""Paired full-pool control summaries, kept separate from masked-prefix effects."""

from research.d1_v1.analysis import balanced

ARMS = ("frozen_cache_greedy", "G1", "Gk_k4", "T_k4_tau0.05", "nearest_hit")


def summarize_controls(units):
    index = {(r["task_id"], r["spec"]["n0"], r["spec"]["seed"], r["spec"]["control"]): r for r in units}
    assert len(index) == len(units), "DUPLICATE_CONTROL_UNIT"
    contexts = {key[:3] for key in index}
    assert all((*key, arm) in index for key in contexts for arm in ARMS), "MISSING_MATCHED_CONTROL"
    output = {}
    for arm in ARMS:
        rows = []
        for task, n0, seed in sorted(contexts):
            result = index[task, n0, seed, arm]
            row = dict(task_id=task, component=result["component"], hits=result["new_positives"],
                       cpu=result["scientific_cpu_seconds"], deliveries=result["new_deliveries"])
            for base in ("G1", "Gk_k4", "T_k4_tau0.05", "nearest_hit"):
                baseline = index[task, n0, seed, base]
                assert baseline["component"] == result["component"]
                assert baseline["spec"]["input_sha256"] == result["spec"]["input_sha256"]
                assert baseline["assigned_C"] == result["assigned_C"] == 5
                assert baseline["assigned_B"] == result["assigned_B"] == 32
                row[base + "_delta"] = row["hits"] - baseline["new_positives"]
                row[base + "_cpu_delta"] = row["cpu"] - baseline["scientific_cpu_seconds"]
                row[base + "_base_cpu"] = baseline["scientific_cpu_seconds"]
            rows.append(row)
        comparisons = {}
        for base in ("G1", "Gk_k4", "T_k4_tau0.05", "nearest_hit"):
            delta = balanced(rows, base + "_delta")
            base_cpu = balanced(rows, base + "_base_cpu")["mean"]
            saving = 1 - balanced(rows, "cpu")["mean"] / base_cpu
            comparisons[base] = {
                "hit_delta": delta, "cpu_saving_fraction": saving,
                "meets_mean_discovery_preference": delta["mean"] >= 1,
                "meets_mean_saving_preference": saving >= .2 and delta["mean"] >= -.25,
                "components_with_positive_hit_delta": delta["positive_components"],
            }
        output[arm] = {
            "hits": balanced(rows, "hits"), "scientific_cpu_seconds": balanced(rows, "cpu"),
            "deliveries": balanced(rows, "deliveries"), "comparisons": comparisons,
        }
    return {"arms": output, "matched_contexts": len(contexts), "units": len(units),
            "inference": "descriptive fixed six-assay cohort, two seeds; no population confidence interval"}
