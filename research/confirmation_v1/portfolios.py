"""Classical portfolio controls and evaluator boundary for the frozen study."""

import csv
import hashlib

import numpy as np
from rdkit import DataStructs

from research.confirmation_v1.features import bitvectors, load
from research.confirmation_v1.technical_worker import read, sha
from research.m2_costed_v2.guard import new

SEEDS = (90101, 90113, 90133, 90149, 90163)
RANKERS = ("random", "primary_score", "mvsa", "gbm", "rf", "nearest_primary")
OPERATORS = ("top_ranked", "cluster_round_robin", "classical_max_min")


def ranked(values, rows, seed, ascending=False):
    assert len(values) == len(rows) and np.isfinite(values).all()
    direction = 1.0 if ascending else -1.0
    return sorted(range(len(rows)), key=lambda i: (direction * values[i],
        hashlib.sha256((str(seed) + "|" + rows[i]["record_id"]).encode()).hexdigest(), rows[i]["record_id"]))


def select_prefix(order, groups, fingerprints, maximum, operator):
    assert len(set(order)) == len(order) == len(groups) and 0 <= maximum <= len(order)
    if operator == "top_ranked":
        return order[:maximum]
    if operator == "cluster_round_robin":
        grouped = {}
        for i in order:
            grouped.setdefault(groups[i], []).append(i)
        result, depth = [], 0
        while len(result) < maximum:
            for positions in grouped.values():
                if depth < len(positions):
                    result.append(positions[depth])
                    if len(result) == maximum:
                        break
            depth += 1
        return result
    assert operator == "classical_max_min"
    if not maximum:
        return []
    distances = np.ones(len(order), dtype=np.float64)
    result, candidate = [], order[0]
    order_array = np.asarray(order)
    while len(result) < maximum:
        result.append(candidate)
        values = DataStructs.BulkTanimotoSimilarity(fingerprints[candidate], fingerprints)
        distances = np.minimum(distances, 1.0 - np.asarray(values))
        distances[np.asarray(result)] = -1.0
        candidate = int(order_array[np.argmax(distances[order_array])])
    return result


def prepare_selections(root, permit, descriptor, model_descriptors):
    directory, bits, _labels, indices, rows = load(root, descriptor)
    fingerprints = bitvectors(bits[indices])
    groups = [row["group"] for row in rows]
    scores = {"primary_score": np.array([row["primary_score"] for row in rows]),
              "nearest_primary": np.load(str(directory / "nearest-primary.npy"), allow_pickle=False)}
    budgets, selections = descriptor["budgets"], []
    for seed in SEEDS:
        for method in ("mvsa", "rf"):
            model = next(r for r in model_descriptors if r["campaign"] == permit["campaign"] and r["seed"] == seed and r["ranker"] == method)
            folder = root / model["directory"]
            for name, expected in model["files"].items():
                assert sha(folder / name) == expected
            if method == "mvsa":
                scores["mvsa"] = np.load(str(folder / "mvsa-scores.npy"), allow_pickle=False)
                scores["gbm"] = np.load(str(folder / "gbm-probabilities.npy"), allow_pickle=False)
            else:
                scores["rf"] = np.load(str(folder / "rf-probabilities.npy"), allow_pickle=False)
        for ranker in RANKERS:
            order = np.random.RandomState(seed).permutation(len(rows)).tolist() if ranker == "random" else ranked(scores[ranker], rows, seed, ranker == "mvsa")
            for operator in OPERATORS:
                prefix = select_prefix(order, groups, fingerprints, max(budgets), operator)
                assert len(prefix) == len(set(prefix)) == max(budgets)
                selections.append({"ranker": ranker, "operator": operator, "seed": seed, "prefix": prefix})
    assert len(selections) == 90
    return rows, budgets, selections


def evaluate(root, permit):
    release = read(root / "inputs/evaluation-release-v1.json")
    assert release["confirmation_values_released"] is True and release["final16_access"] is False
    assert release["frozen_code_pins"] == permit["code_pins"]
    features = read(root / "inputs/feature-manifests-v1.json")
    descriptor = next(r for r in features["campaigns"] if r["campaign"] == permit["campaign"])
    models = read(root / "inputs/rank-manifests-v1.json")
    assert sha(root / "inputs/feature-manifests-v1.json") == release["feature_manifest_sha256"]
    assert sha(root / "inputs/rank-manifests-v1.json") == release["rank_manifest_sha256"]
    rows, budgets, selections = prepare_selections(root, permit, descriptor, models["models"])
    output = root / "portfolios" / permit["output_name"]
    output.mkdir(parents=True, exist_ok=False)
    # Commit every selection before the evaluator reads any confirmation value.
    new(output / "selection-manifest.json", {"campaign": permit["campaign"], "budgets": budgets,
        "selections": selections, "confirmation_values_analyzed_at_selection": False})
    support = next(r for r in read(root / "inputs/blinded-support-v1.json")["campaigns"] if r["campaign"] == permit["campaign"])
    sealed = root / support["sealed"]
    assert sha(sealed) == support["sealed_sha256"]
    observed = {}
    with sealed.open(newline="") as source:
        for row in csv.DictReader(source):
            assert row["record_id"] not in observed
            value = float(row["raw_confirmatory"])
            assert value in (0.0, 1.0), "INVALID_SOURCE_CONFIRMATION_STATE_NO_IMPUTATION"
            observed[row["record_id"]] = int(value)
    assert set(observed) == {row["record_id"] for row in rows}
    positives = [observed[row["record_id"]] for row in rows]
    records = []
    for selection in selections:
        for budget in budgets:
            selected = selection["prefix"][:budget]
            active = [i for i in selected if positives[i] == 1]
            records.append({"campaign": permit["campaign"], "seed": selection["seed"],
                "ranker": selection["ranker"], "operator": selection["operator"], "confirmation_count": budget,
                "confirmed_positives": len(active), "positive_structure_groups": len({rows[i]["group"] for i in active}),
                "positive_fingerprint_groups": len({rows[i]["sensitivity_group"] for i in active}),
                "hits_per_confirmation": len(active) / budget if budget else None,
                "groups_per_confirmation": len({rows[i]["group"] for i in active}) / budget if budget else None})
    assert len(records) <= 450 and len({(r["seed"], r["ranker"], r["operator"], r["confirmation_count"]) for r in records}) == len(records)
    with (output / "cells.csv").open("x", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    result = {"status": "PASS_FROZEN_PORTFOLIO_CELLS", "campaign": permit["campaign"], "cells": len(records),
              "universe_size": len(rows), "source_confirmed_positive_count": sum(positives),
              "source_positive_structure_groups": len({rows[i]["group"] for i, y in enumerate(positives) if y}),
              "budgets": budgets, "directory": str(output.relative_to(root)),
              "cells_sha256": sha(output / "cells.csv"), "selection_manifest_sha256": sha(output / "selection-manifest.json"),
              "confirmation_values_analyzed": True, "protected_final16_access": False}
    new(output / "manifest.json", result)
    return result
