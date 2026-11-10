"""Independent direct CSV arithmetic. Does not import adapter or verifier."""

import csv
import hashlib
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CSV = "docs/evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv"
CSV_SHA = "495fd9d918b00db16e779a866f9f8a801e300ef0b6e4c23635dd1fb9a395d831"
METRICS = {"H": "confirmed_positives", "D": "positive_structure_groups", "FP": "positive_fingerprint_groups",
           "B": "confirmation_count", "HB": "hits_per_confirmation", "DB": "groups_per_confirmation"}


def mean(values):
    return math.fsum(values) / len(values)


def expected_values(spec):
    path = ROOT / CSV
    assert hashlib.sha256(path.read_bytes()).hexdigest() == CSV_SHA
    with path.open(newline="", encoding="utf-8") as stream:
        cells = list(csv.DictReader(stream))
    result = {}
    for budget in spec["budgets"]:
        for index, arm in enumerate(spec["arms"]):
            ranker, operator = arm.split("/")
            selected = [r for r in cells if int(r["budget_percent"]) == budget and r["ranker"] == ranker and r["operator"] == operator
                        and (spec["campaign"] == "equal" or spec["campaign"] == r["campaign"])]
            assert len(selected) == (30 if spec["campaign"] == "equal" else 5)
            for short, metric in METRICS.items():
                seeds = [mean([float(r[metric]) for r in selected if int(r["seed"]) == seed])
                         for seed in (90101, 90113, 90133, 90149, 90163)]
                prefix = f"b{budget}:a{index}:{short}"
                result.update({prefix: round(mean(seeds), 3), prefix + ":min": round(min(seeds), 3), prefix + ":max": round(max(seeds), 3)})
    if len(spec["arms"]) >= 2:
        for budget in spec["budgets"]:
            for metric in ("H", "D", "FP", "HB", "DB"):
                result[f"delta:b{budget}:{metric}"] = round(result[f"b{budget}:a1:{metric}"] - result[f"b{budget}:a0:{metric}"], 3)
    if len(spec["budgets"]) > 1:
        for index in range(len(spec["arms"])):
            for metric in ("H", "D"):
                result[f"sweep:a{index}:{metric}"] = round(result[f"b{spec['budgets'][-1]}:a{index}:{metric}"] - result[f"b{spec['budgets'][0]}:a{index}:{metric}"], 3)
    # The fixed observation interface exposes only H/D min/max; all means.
    return {k: v for k, v in result.items() if not k.endswith((":min", ":max")) or ":H:" in k or ":D:" in k}


def gold(cases):
    return {c["case_id"]: {"expected_action": c["expected_action"], "acceptable_reasons": c["acceptable_reasons"],
            "required_keys": c["required_keys"], "required_limits": c["required_limits"],
            "permitted_values": {} if c["fault"] else expected_values(c["spec"])} for c in cases}
