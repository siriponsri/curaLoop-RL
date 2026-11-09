"""Descriptive matched-state analysis, without an oracle or policy fitting."""

from collections import defaultdict
from statistics import mean


def balanced(rows, field):
    groups = defaultdict(lambda: defaultdict(list))
    for row in rows:
        groups[row["component"]][row["task_id"]].append(row[field])
    if not groups:
        return {"mean": None, "components": {}, "positive_components": 0, "rows": 0}
    components = {g: mean(mean(values) for values in tasks.values()) for g, tasks in groups.items()}
    return {"mean": mean(components.values()), "components": components,
            "positive_components": sum(value > 0 for value in components.values()), "rows": len(rows)}


def pair(branches, snapshot):
    """Require a complete matched triple; actual-op failure is never equivalence."""
    assert set(branches) == {"REUSE", "UPDATE", "PLAN"}
    specs = [row["result"]["spec"] for row in branches.values()]
    for key in ("prefix_job", "snapshot", "regime", "cap", "task_id", "n0", "seed", "predictor", "input_sha256"):
        assert all(spec[key] == specs[0][key] for spec in specs), "UNMATCHED_COUNTERFACTUAL"
    first = {}
    for operation, row in branches.items():
        trace = row["trace"]
        assert len(trace) == row["result"]["new_deliveries"]
        assert [t["query"] for t in trace] == list(range(1, len(trace) + 1))
        assert sum(t["delivered_label"] for t in trace) == row["result"]["new_positives"]
        first[operation] = trace[snapshot] if len(trace) > snapshot else None
    return first


def summarize(rows):
    output = {}
    for regime in sorted({row["regime"] for row in rows}):
        selected = [row for row in rows if row["regime"] == regime]
        output[regime] = {}
        for contrast in ("UPDATE-REUSE", "PLAN-UPDATE", "PLAN-REUSE"):
            subset = [row for row in selected if row["contrast"] == contrast]
            supported = [row for row in subset if row["executed_support"]]
            output[regime][contrast] = {
                "assigned_hit_effect": balanced(subset, "hit_delta"),
                "supported_hit_effect": balanced(supported, "hit_delta"),
                "assigned_cpu_effect_seconds": balanced(subset, "cpu_delta"),
                "assigned_deliveries_effect": balanced(subset, "delivery_delta"),
                "assigned_whole_process_cpu_effect_seconds": balanced(subset, "process_cpu_delta"),
                "supported_states": len(supported), "assigned_states": len(subset),
                "action_changes": sum(row["choice_changed"] for row in supported),
                "unsupported_reasons": {
                    reason: sum(row["support_reason"] == reason for row in subset)
                    for reason in sorted({row["support_reason"] for row in subset if not row["executed_support"]})
                },
                "positive_zero_negative": [sum(row["hit_delta"] > 0 for row in supported),
                                           sum(row["hit_delta"] == 0 for row in supported),
                                           sum(row["hit_delta"] < 0 for row in supported)],
            }
    return output
