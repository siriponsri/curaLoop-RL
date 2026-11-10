"""Only existing authenticated aggregate views; no simulator/private adapters."""

from curaloop_rd.confirmation_study import ROOT, StudyUnavailable, view

from .contracts import LIMITS, MissionSpec, digest

METRICS = {"H": "confirmed_positives", "D": "positive_structure_groups", "FP": "positive_fingerprint_groups",
           "B": "confirmation_count", "HB": "hits_per_confirmation", "DB": "groups_per_confirmation"}


def collect(spec: MissionSpec, *, source_root=ROOT):
    values, views = {}, []
    for budget in spec.budgets:
        current = view(spec.campaign, budget, root=source_root)
        views.append(current)
        for arm in current["arms"]:
            identity = arm["ranker"] + "/" + arm["operator"]
            if identity not in spec.arms:
                continue
            for short, metric in METRICS.items():
                prefix = f"b{budget}:a{spec.arms.index(identity)}:{short}"
                for stat in ("mean", "min", "max"):
                    # Explicit contract: source operands first rounded to 3 decimals.
                    values[prefix + ("" if stat == "mean" else ":" + stat)] = round(arm["metrics"][metric][stat], 3)
    evidence = {"schema": "curaloop.agent-rd.evidence.v1", "status": "available", "campaign": spec.campaign,
                "budgets": spec.budgets, "arms": spec.arms, "values": values,
                "units": {"H": "historical positive observations", "D": "positive fixed structure groups",
                          "FP": "positive fingerprint groups", "B": "confirmation observations",
                          "HB": "fraction, not percent or currency", "DB": "fraction, not percent or currency"},
                "limitations": LIMITS, "source_hashes": views[0]["source_hashes"],
                "source_snapshot": views[0]["source_snapshot"], "paper_url": views[0]["paper_url"],
                "source_url": views[0]["source_url"], "final16_access": False}
    evidence["evidence_digest"] = digest(evidence)
    evidence["evidence_id"] = evidence["evidence_digest"][:16]
    return evidence


def comparisons(evidence):
    """Right-minus-left over explicitly rounded displayed source operands."""
    values, derived = evidence["values"], {}
    arms, budgets = evidence["arms"], evidence["budgets"]
    if len(arms) >= 2:
        for budget in budgets:
            for metric in ("H", "D", "FP", "HB", "DB"):
                left, right = (f"b{budget}:a{index}:{metric}" for index in (0, 1))
                derived[f"delta:b{budget}:{metric}"] = round(values[right] - values[left], 3)
    if len(budgets) > 1:
        for index, arm in enumerate(arms):
            for metric in ("H", "D"):
                derived[f"sweep:a{index}:{metric}"] = round(values[f"b{budgets[-1]}:a{index}:{metric}"] - values[f"b{budgets[0]}:a{index}:{metric}"], 3)
    return {"evidence_id": evidence["evidence_id"], "definition": "right-minus-left for first two arms; last-minus-first budget for sweeps; rounded operands",
            "values": derived}


def unavailable(error):
    if not isinstance(error, StudyUnavailable):
        raise error
    return {"status": "source_unavailable", "values": {}, "limitations": LIMITS,
            "diagnostic": str(error), "evidence_id": None, "source_hashes": []}


def compact(evidence, derived=None):
    value = {k: evidence[k] for k in ("status", "campaign", "budgets", "arms", "evidence_id") if k in evidence}
    value["values"] = {k: v for k, v in evidence["values"].items()
                       if not k.endswith((":min", ":max")) or ":H:" in k or ":D:" in k}
    value["limitation_codes"] = list(LIMITS)
    value["source_facts"] = {"campaigns": 6, "annotation_components": 1, "conditional_seeds": 5,
                            "missing": "excluded", "nonpositive": "inactive_or_inconclusive",
                            "round_robin_D_equals_H": "mechanical", "lab_clinical_cost_data": "unavailable"}
    if derived:
        value["derived"] = derived["values"]
    return value
