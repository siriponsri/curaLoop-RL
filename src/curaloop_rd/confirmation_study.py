"""Fixed, authenticated CF1 aggregates shared by the local API and C Workspace.

No molecular rows, hidden oracle, simulator, model loader or network is used.
The registry is code-owned; a request cannot supply an input path or digest.
"""

import csv
import hashlib
import io
import json
import math
import statistics
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUTS = {
    "card": ("research/product_handoffs/lr_cf1_v1/evidence-card-v1.json", 3884,
             "e4ed702d61f1a283cc7bc0f1abcd4b41dd4f241f1b66857afed9a299254a3fa9"),
    "schema": ("research/product_handoffs/lr_cf1_v1/evidence-card.schema.json", 4357,
               "06709cfa3d1878a95291a5d0ef1b4b4a26c54e9777eda9b9d1f1ec353f5fea69"),
    "cells": ("docs/evidence/lr-cf1-20261109-v1/portfolio-cells-v1.csv", 384138,
              "495fd9d918b00db16e779a866f9f8a801e300ef0b6e4c23635dd1fb9a395d831"),
    "summary": ("docs/evidence/lr-cf1-20261109-v1/results-summary-v1.json", 114773,
                "fff5b722a6ade896f056c798bcf40fdc3a21909e63882909f9915dbec7e10486"),
}
CAMPAIGNS = ("628/677", "1040/1254", "2661/2821", "449739/489005", "485270/492964", "485273/493155")
RANKERS = ("mvsa", "rf", "gbm", "primary_score", "nearest_primary", "random")
OPERATORS = ("top_ranked", "cluster_round_robin", "classical_max_min")
BUDGETS = (1, 2, 5, 10, 20)
SEEDS = (90101, 90113, 90133, 90149, 90163)
COUNTS = ("confirmation_count", "confirmed_positives", "positive_structure_groups", "positive_fingerprint_groups")
RATIOS = ("hits_per_confirmation", "groups_per_confirmation")
METRICS = COUNTS + RATIOS
COLUMNS = {"campaign", "seed", "ranker", "operator", "budget_percent", "provider_block", *METRICS}
LIMITATIONS = (
    "Exposed development evidence; no independent confirmation evaluation or new selector.",
    "Observation-supported primary hits only; missing confirmation is excluded, not negative.",
    "Source nonpositive combines inactive and inconclusive outcomes.",
    "Five-seed ranges describe conditional repetitions, not biological population confidence intervals.",
    "Four provider blocks, one annotation-connected component; no independent-family or chemical-OOD claim.",
    "Round-robin has one selection per group at these budgets: D equals H mechanically.",
    "SI/repository names conflict for 13 of 17 pairs; numeric AIDs and the pinned repository govern.",
    "Counts per confirmation are not monetary savings, laboratory time or clinical efficacy.",
    "RL was not evaluated in CF1. HIV policies and current simulator results are separate studies.",
    "Internal derived-report use only; raw redistribution and commercial data clearance are not established.",
)


class StudyUnavailable(ValueError):
    """The fixed study cannot be authenticated or its contract is invalid."""


def _authenticated(root, key):
    relative, size, expected = INPUTS[key]
    path = root / relative
    for parent in (path, *path.parents):
        if parent == root.parent:
            break
        if parent.is_symlink():
            raise StudyUnavailable("Study inputs must be regular owned files")
    try:
        if path.stat().st_size != size:
            raise StudyUnavailable("Study input size differs from the fixed release")
        data = path.read_bytes()
    except OSError as exc:
        raise StudyUnavailable("Recorded confirmation evidence is unavailable") from exc
    if hashlib.sha256(data).hexdigest() != expected:
        raise StudyUnavailable("Recorded confirmation evidence failed source verification")
    return data


def _strict_object(value, schema):
    """Check the closed pinned card schema without adding a runtime dependency."""
    if "$ref" in schema:
        raise StudyUnavailable("Internal schema reference must be resolved")
    if "const" in schema and (value != schema["const"] or type(value) is not type(schema["const"])):
        raise StudyUnavailable("Card constant differs")
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(value, dict) or set(value) != set(schema["required"]):
            raise StudyUnavailable("Card has missing or unexpected fields")
        for key in value:
            _strict_object(value[key], schema["properties"][key])
    elif kind == "integer":
        if type(value) is not int or value < schema.get("minimum", value) or value > schema.get("maximum", value):
            raise StudyUnavailable("Card count differs")
    elif kind == "string" and (not isinstance(value, str) or len(value) < schema.get("minLength", 0)):
        raise StudyUnavailable("Card text differs")


def _resolve_schema(value, definitions):
    if isinstance(value, dict):
        if "$ref" in value:
            return _resolve_schema(definitions[value["$ref"].split("/")[-1]], definitions)
        return {k: _resolve_schema(v, definitions) for k, v in value.items()}
    if isinstance(value, list):
        return [_resolve_schema(v, definitions) for v in value]
    return value


def load_study(root=ROOT):
    """Authenticate every input per read; root is an internal testing seam only."""
    root = Path(root).absolute()
    blobs = {key: _authenticated(root, key) for key in INPUTS}
    card = json.loads(blobs["card"])
    schema = json.loads(blobs["schema"])
    _strict_object(card, _resolve_schema(schema, schema["$defs"]))
    summary = json.loads(blobs["summary"])
    if set(summary) != {"status", "cells", "campaigns", "source_experiment_blocks", "annotation_connected_components",
                         "equal_campaign_summary", "uncertainty", "confirmation_values_analyzed", "final16_access", "new_selector_training"}:
        raise StudyUnavailable("Study summary fields differ")
    campaigns = summary["campaigns"]
    if tuple(row["campaign"] for row in campaigns) != CAMPAIGNS or summary["cells"] != 2700:
        raise StudyUnavailable("Study roster differs")
    reader = csv.DictReader(io.StringIO(blobs["cells"].decode("utf-8")))
    if set(reader.fieldnames or []) != COLUMNS or len(reader.fieldnames) != len(COLUMNS):
        raise StudyUnavailable("Unexpected aggregate columns")
    rows, keys = [], set()
    campaign_map = {row["campaign"]: row for row in campaigns}
    for raw in reader:
        if set(raw) != COLUMNS or any(v is None for v in raw.values()):
            raise StudyUnavailable("Malformed aggregate row")
        row = dict(raw)
        for name in ("seed", "budget_percent", *COUNTS):
            try:
                row[name] = int(raw[name])
            except (ValueError, TypeError) as exc:
                raise StudyUnavailable("Invalid aggregate integer") from exc
        for name in RATIOS:
            try:
                row[name] = float(raw[name])
            except (ValueError, TypeError) as exc:
                raise StudyUnavailable("Invalid aggregate ratio") from exc
        key = (row["campaign"], row["seed"], row["ranker"], row["operator"], row["budget_percent"])
        if key in keys or row["campaign"] not in campaign_map:
            raise StudyUnavailable("Duplicate or unknown aggregate cell")
        keys.add(key)
        context = campaign_map[row["campaign"]]
        b, h, d, fp = (row[k] for k in COUNTS)
        if not (0 <= d <= h <= b <= context["universe_size"] and 0 <= fp <= h and b > 0):
            raise StudyUnavailable("Aggregate count bounds differ")
        if row["provider_block"] != context["provider_block"] or b != math.ceil(context["universe_size"] * row["budget_percent"] / 100):
            raise StudyUnavailable("Aggregate population or budget differs")
        if not all(math.isfinite(row[k]) for k in RATIOS) or not math.isclose(row[RATIOS[0]], h / b) or not math.isclose(row[RATIOS[1]], d / b):
            raise StudyUnavailable("Aggregate ratio differs")
        rows.append(row)
    if keys != set(product(CAMPAIGNS, SEEDS, RANKERS, OPERATORS, BUDGETS)):
        raise StudyUnavailable("Incomplete fixed study matrix")
    return card, summary, rows


def _metric(values):
    return {"mean": statistics.mean(values), "sd": statistics.stdev(values), "min": min(values), "max": max(values)}


def view(campaign="equal", budget_percent=10, *, root=ROOT):
    if campaign not in ("equal", *CAMPAIGNS) or type(budget_percent) is not int or budget_percent not in BUDGETS:
        raise ValueError("Choose a fixed campaign and budget: 1, 2, 5, 10 or 20 percent")
    card, summary, cells = load_study(root)
    selected = [r for r in cells if r["budget_percent"] == budget_percent and (campaign == "equal" or r["campaign"] == campaign)]
    arms = []
    for ranker, operator in product(RANKERS, OPERATORS):
        group = [r for r in selected if r["ranker"] == ranker and r["operator"] == operator]
        # First average the six campaigns WITHIN each fixed seed. This preserves
        # CF1's equal-campaign uncertainty unit instead of pooling 30 rows.
        seed_values = {metric: [statistics.mean(r[metric] for r in group if r["seed"] == seed) for seed in SEEDS] for metric in METRICS}
        arms.append({"ranker": ranker, "operator": operator, "seed_count": 5,
                     "metrics": {metric: _metric(values) for metric, values in seed_values.items()}})
    return {
        "schema": "curaloop.confirmation.study-view.v1", "study_id": "cf1", "integration_status": "LOCAL_AGGREGATE_ADAPTER",
        "research_status": "NO_GO_QUOTA_ONLY_METHOD_CLAIM", "source_snapshot": card["source_snapshot"],
        "campaign": campaign, "budget_percent": budget_percent, "campaigns": summary["campaigns"],
        "budgets": list(BUDGETS), "seeds": list(SEEDS), "arms": arms,
        "universe_observations": sum(c["universe_size"] for c in summary["campaigns"]),
        "primary_observations": sum(c["retained_primary_rows"] for c in summary["campaigns"]),
        "source_experiment_blocks": 4, "annotation_connected_components": 1,
        "aggregation": "equal-campaign mean within each seed" if campaign == "equal" else "five fixed conditional seeds within campaign",
        "uncertainty": "Observed seed range and SD; not a biological population confidence interval",
        "limitations": list(LIMITATIONS), "source_labels": card["labels"],
        "source_hashes": [{"path": path, "bytes": size, "sha256": digest} for path, size, digest in INPUTS.values()],
        "source_url": "https://github.com/dahvida/AIC_Finder/tree/04c58e85188e724ec5ff44cbed2e7b960f6f3df3",
        "paper_url": "https://doi.org/10.1021/acscentsci.3c01517",
        "final16_access": False, "new_selector_training": False, "publication_ready": False,
    }


def comparison_brief(campaign="equal", budget_percent=10, ranker="mvsa", operator="top_ranked", locale="en", *, root=ROOT):
    if ranker not in RANKERS or operator not in OPERATORS or locale not in ("en", "th"):
        raise ValueError("Unsupported fixed comparison filter")
    payload = view(campaign, budget_percent, root=root)
    return {"schema": "curaloop.confirmation.comparison-brief.v1", "locale": locale,
            "title": payload["source_labels"][locale]["title"],
            "purpose": "Historical aggregate comparison; not a molecular selection or laboratory instruction",
            "selection": {"campaign": campaign, "budget_percent": budget_percent, "ranker": ranker, "operator": operator},
            "selected_arm": next(a for a in payload["arms"] if a["ranker"] == ranker and a["operator"] == operator),
            "evidence": payload, "external_delivery": False}
