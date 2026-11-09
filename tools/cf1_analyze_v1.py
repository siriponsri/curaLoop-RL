"""Independently verify private CF1 selections; emit aggregate-only results."""
# ruff: noqa: E402

import csv
import itertools
import statistics
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start

FRACTIONS = (1, 2, 5, 10, 20)
METRICS = ("confirmed_positives", "positive_structure_groups", "positive_fingerprint_groups",
           "hits_per_confirmation", "groups_per_confirmation")


def write_csv(path, rows):
    assert rows
    with path.open("x", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarized(rows, keys):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in keys)].append(row)
    output = []
    for key, members in groups.items():
        value = dict(zip(keys, key))
        value["conditional_seed_count"] = len(members)
        for metric in METRICS:
            values = [m[metric] for m in members]
            value.update({metric + "_mean": statistics.mean(values), metric + "_sd": statistics.stdev(values),
                          metric + "_min": min(values), metric + "_max": max(values)})
        output.append(value)
    return output


def nondominated(rows, x, y):
    return [r for r in rows if not any(t[x] >= r[x] and t[y] >= r[y] and (t[x] > r[x] or t[y] > r[y]) for t in rows)]


def main():
    assert read(TASK / "remote-return/verified-v1.json")["status"] == "PASS_COMPLETE_PRIVATE_RETURN_AND_LOCAL_REREAD"
    returned = TASK / "remote-return/files"
    features = read(TASK / "feature-manifests-v1.json")["campaigns"]
    support = {r["campaign"]: r for r in read(TASK / "blinded-support-v1.json")["campaigns"]}
    matrix = read(TASK / "cell-manifest-v1.json")
    expected = {(r["campaign"], r["seed"], r["ranker"], r["operator"], r["confirmation_count"]) for r in matrix["cells"]}
    all_cells, campaigns = [], []
    for feature in features:
        campaign = feature["campaign"]
        key = campaign.replace("/", "-")
        folder = returned / "portfolios" / key
        manifest = read(folder / "manifest.json")
        assert sha(folder / "cells.csv") == manifest["cells_sha256"]
        assert sha(folder / "selection-manifest.json") == manifest["selection_manifest_sha256"]
        rows = read(returned / feature["directory"] / "universe.json")["rows"]
        with (returned / support[campaign]["sealed"]).open(newline="") as file:
            sealed_rows = list(csv.DictReader(file))
        assert len({r["record_id"] for r in sealed_rows}) == len(sealed_rows)
        assert all(float(r["raw_confirmatory"]) in (0.0, 1.0) for r in sealed_rows)
        observed = {r["record_id"]: int(float(r["raw_confirmatory"])) for r in sealed_rows}
        assert len(observed) == len(rows) and set(observed) == {r["record_id"] for r in rows}
        positives = [observed[r["record_id"]] for r in rows]
        assert set(positives) <= {0, 1}
        selection = read(folder / "selection-manifest.json")
        assert selection["confirmation_values_analyzed_at_selection"] is False
        independent = {}
        for arm in selection["selections"]:
            assert len(set(arm["prefix"])) == len(arm["prefix"]) == max(feature["budgets"])
            assert all(type(i) is int and 0 <= i < len(rows) for i in arm["prefix"])
            for budget in feature["budgets"]:
                selected_positive = [i for i in arm["prefix"][:budget] if positives[i]]
                h = len(selected_positive)
                d = len({rows[i]["group"] for i in selected_positive})
                f = len({rows[i]["sensitivity_group"] for i in selected_positive})
                independent[(arm["seed"], arm["ranker"], arm["operator"], budget)] = (h, d, f)
        assert len(independent) == 450
        with (folder / "cells.csv").open(newline="") as file:
            cells = list(csv.DictReader(file))
        for cell in cells:
            for name in ("seed", "confirmation_count", "confirmed_positives", "positive_structure_groups", "positive_fingerprint_groups"):
                cell[name] = int(cell[name])
            for name in ("hits_per_confirmation", "groups_per_confirmation"):
                cell[name] = float(cell[name])
            identity = (cell["seed"], cell["ranker"], cell["operator"], cell["confirmation_count"])
            assert tuple(cell[k] for k in METRICS[:3]) == independent.pop(identity)
            assert cell["hits_per_confirmation"] == cell["confirmed_positives"] / cell["confirmation_count"]
            assert cell["groups_per_confirmation"] == cell["positive_structure_groups"] / cell["confirmation_count"]
            cell["budget_percent"] = FRACTIONS[feature["budgets"].index(cell["confirmation_count"])]
            cell["provider_block"] = support[campaign]["provider_block"]
            all_cells.append(cell)
        assert not independent
        campaigns.append({"campaign": campaign, "provider_block": support[campaign]["provider_block"],
            "source_rows": support[campaign]["counts"]["source_rows"], "retained_primary_rows": feature["primary_rows"],
            "universe_size": len(rows), "source_confirmed_positive_count": sum(positives),
            "source_positive_structure_groups": len({r["group"] for r, y in zip(rows, positives) if y}),
            "murcko_or_fallback_groups": feature["murcko_or_fallback_groups"],
            "fingerprint_sensitivity_groups": feature["fingerprint_sensitivity_groups"], "budgets": feature["budgets"]})
    actual = {(r["campaign"], r["seed"], r["ranker"], r["operator"], r["confirmation_count"]) for r in all_cells}
    assert len(actual) == len(all_cells) == 2700 and actual == expected
    write_csv(PUBLIC / "portfolio-cells-v1.csv", all_cells)
    campaign_summary = summarized(all_cells, ("campaign", "provider_block", "budget_percent", "confirmation_count", "ranker", "operator"))
    write_csv(PUBLIC / "campaign-summary-v1.csv", campaign_summary)
    # Descriptive cross-campaign rates: average campaigns first within each seed.
    pooled = defaultdict(list)
    for r in all_cells:
        pooled[(r["seed"], r["budget_percent"], r["ranker"], r["operator"])].append(r)
    equal_campaign = []
    for key, members in pooled.items():
        assert len(members) == 6
        equal_campaign.append({**dict(zip(("seed", "budget_percent", "ranker", "operator"), key)),
                              **{metric: statistics.mean(r[metric] for r in members) for metric in METRICS}})
    global_summary = summarized(equal_campaign, ("budget_percent", "ranker", "operator"))
    write_csv(PUBLIC / "equal-campaign-summary-v1.csv", global_summary)
    block_rows = defaultdict(list)
    for r in all_cells:
        block_rows[(r["provider_block"], r["seed"], r["budget_percent"], r["ranker"], r["operator"])].append(r)
    provider_seeds = [{**dict(zip(("provider_block", "seed", "budget_percent", "ranker", "operator"), key)),
                       **{metric: statistics.mean(r[metric] for r in members) for metric in METRICS}}
                      for key, members in block_rows.items()]
    write_csv(PUBLIC / "provider-summary-v1.csv", summarized(provider_seeds, ("provider_block", "budget_percent", "ranker", "operator")))
    index = {(r["campaign"], r["seed"], r["budget_percent"], r["ranker"], r["operator"]): r for r in all_cells}
    contrasts = []
    for r in all_cells:
        for reference in ("same_ranker_top", "mvsa_top"):
            baseline = index[(r["campaign"], r["seed"], r["budget_percent"], r["ranker"] if reference == "same_ranker_top" else "mvsa", "top_ranked")]
            contrasts.append({**{k: r[k] for k in ("campaign", "seed", "budget_percent", "ranker", "operator")},
                "reference": reference, **{metric + "_difference": r[metric] - baseline[metric] for metric in METRICS[:3]}})
    write_csv(PUBLIC / "paired-contrasts-v1.csv", contrasts)
    frontiers = []
    for campaign, percent in itertools.product((r["campaign"] for r in campaigns), FRACTIONS):
        rows = [r for r in campaign_summary if r["campaign"] == campaign and r["budget_percent"] == percent]
        for r in nondominated(rows, "confirmed_positives_mean", "positive_structure_groups_mean"):
            frontiers.append({k: r[k] for k in ("campaign", "budget_percent", "confirmation_count", "ranker", "operator", "confirmed_positives_mean", "positive_structure_groups_mean")})
    write_csv(PUBLIC / "campaign-mean-frontiers-v1.csv", frontiers)
    seed_frontiers = []
    for campaign, percent, seed in itertools.product((r["campaign"] for r in campaigns), FRACTIONS, (90101, 90113, 90133, 90149, 90163)):
        rows = [r for r in all_cells if r["campaign"] == campaign and r["budget_percent"] == percent and r["seed"] == seed]
        seed_frontiers.extend(nondominated(rows, "confirmed_positives", "positive_structure_groups"))
    write_csv(PUBLIC / "campaign-seed-frontiers-v1.csv", seed_frontiers)
    new(PUBLIC / "results-summary-v1.json", {"status": "PASS_INDEPENDENT_AGGREGATE_RECALCULATION", "cells": len(all_cells),
        "campaigns": campaigns, "source_experiment_blocks": len({r["provider_block"] for r in campaigns}),
        "annotation_connected_components": 1, "equal_campaign_summary": global_summary,
        "uncertainty": "observed range and sample SD across five conditional seeds; no biological population CI",
        "confirmation_values_analyzed": True, "final16_access": False, "new_selector_training": False})
    print({"status": "PASS_INDEPENDENT_2700_CELL_RECALCULATION", "campaigns": campaigns})


if __name__ == "__main__":
    guard = start("independent-aggregate-analysis-v1", 180, 600, bucket="utilities_return_handoff_delivery")
    try:
        main()
        finish("independent-aggregate-analysis-v1", guard, "PASS_INDEPENDENT_AGGREGATE_ANALYSIS")
    except BaseException:
        finish("independent-aggregate-analysis-v1", guard, "FAIL")
        raise
