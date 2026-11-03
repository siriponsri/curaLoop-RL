"""Historical replay, paired uncertainty, and a separate scaffold-disjoint predictor audit."""

import argparse
import json
import random
import statistics
from collections import defaultdict
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path

from ._datasets import hiv_resource
from .domain import POLICIES, Scenario, digest
from .export import csv_report
from .service import compare


def predictor_benchmark(seed: int = 42) -> dict:
    """Evaluator-only labels. Its model is never given to a campaign policy."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    resource = hiv_resource()
    groups = defaultdict(list)
    for record in resource["records"]:
        groups[record["scaffold_id"]].append(record)
    ordered = sorted(groups, key=lambda s: sha256(f"scaffold:{seed}:{s}".encode()).hexdigest())
    test, train = [], []
    for scaffold in ordered:
        (test if len(test) < 0.2 * len(resource["records"]) else train).extend(groups[scaffold])
    train_scaffolds = {r["scaffold_id"] for r in train}
    test_scaffolds = {r["scaffold_id"] for r in test}
    if train_scaffolds & test_scaffolds:
        raise RuntimeError("Scaffold overlap")
    def features(records):
        return [[int(i in set(r["morgan_on_bits"])) for i in range(1024)] for r in records]
    y_train, y_test = [r["active"] for r in train], [r["active"] for r in test]
    metadata = {
        "scope": "Custom 80/20 whole-scaffold split of 1200-row HIV subset; NOT official leaderboard split.",
        "seed": seed, "source_resource_sha256": resource["manifest"]["resource_sha256"],
        "train_count": len(train), "test_count": len(test),
        "train_actives": sum(y_train), "test_actives": sum(y_test), "scaffold_overlap": 0,
        "train_ids": [r["compound_id"] for r in train], "test_ids": [r["compound_id"] for r in test],
        "split_sha256": digest({"train": [r["compound_id"] for r in train], "test": [r["compound_id"] for r in test]}),
        "classifier": "StandardScaler -> LogisticRegression(C=1,liblinear,max_iter=500)",
        "preprocessing_fit": "Training rows only; no held-out feature scaling fit.",
        "policy_access": "This evaluator and its trained model are never passed to screening policies.",
    }
    if len(set(y_train)) < 2 or len(set(y_test)) < 2:
        return {**metadata, "status": "NOT_ESTIMABLE_ONE_CLASS", "auroc": None, "average_precision": None}
    model = make_pipeline(StandardScaler(), LogisticRegression(solver="liblinear", C=1, max_iter=500, random_state=seed))
    model.fit(features(train), y_train)
    p = model.predict_proba(features(test))[:, 1]
    return {**metadata, "status": "EXECUTED", "auroc": roc_auc_score(y_test, p),
            "average_precision": average_precision_score(y_test, p),
            "brier_score": brier_score_loss(y_test, p), "test_prevalence": sum(y_test) / len(y_test)}


def summarize(reports: list[dict], bootstrap_samples: int = 2000) -> dict:
    by_policy = defaultdict(dict)
    for r in reports:
        by_policy[r["manifest"]["policy_id"]][r["manifest"]["seed"]] = r["metrics"]["confirmed_hits"]
    summary = []
    for policy, points in by_policy.items():
        values = list(points.values())
        summary.append({"policy": policy, "n_seeds": len(values), "mean_hits": statistics.mean(values),
                        "sd_hits": statistics.stdev(values) if len(values) > 1 else None,
                        "min_hits": min(values), "max_hits": max(values)})
    contrasts = []
    for policy in by_policy:
        if policy == "random":
            continue
        seeds = sorted(set(by_policy[policy]) & set(by_policy["random"]))
        diffs = [by_policy[policy][s] - by_policy["random"][s] for s in seeds]
        rng = random.Random(20261103)
        estimates = sorted(statistics.mean(rng.choices(diffs, k=len(diffs))) for _ in range(bootstrap_samples))
        contrasts.append({"contrast": policy + " minus random", "paired_seeds": seeds,
                          "mean_hit_difference": statistics.mean(diffs),
                          "bootstrap_95_percentile_interval": [estimates[int(.025 * bootstrap_samples)], estimates[int(.975 * bootstrap_samples)]],
                          "bootstrap_samples": bootstrap_samples})
    return {"summary": summary, "paired_contrasts": contrasts,
            "interpretation": "Within-assay seed variability only. These intervals do not establish cross-target, prospective or pharmacological utility; multiple contrasts exploratory."}


def run_benchmark(output: Path, seeds: list[int], budget: int = 30) -> dict:
    if not seeds or len(seeds) != len(set(seeds)) or len(seeds) > 100:
        raise ValueError("Use 1-100 distinct paired seeds.")
    scenario = Scenario(dataset="hiv_moleculenet_replay_v1", candidate_count=1200,
                        initial_count=48, budget_units=budget, batch_size=5, delay_steps=2)
    reports = []
    for seed in seeds:
        reports.extend(compare(replace(scenario, seed=seed), POLICIES))
        print(f"Completed historical replay seed {seed}: all five policies", flush=True)
    payload = {"schema_version": "1.1", "benchmark": "HIV_HISTORICAL_REPLAY_CUSTOM_SUBSET",
               "scenario_template": asdict(scenario), "seeds": seeds,
               "statistics": summarize(reports), "runs": reports,
               "predictor_benchmark": predictor_benchmark(),
               "training_evaluation_separation": "Controllers trained on synthetic seeds >=10000; HIV labels never used for controller training.",
               "research_status": "ENGINEERING_BENCHMARK_ONLY_NOT_PAPER_REPRODUCTION"}
    output.mkdir(parents=True, exist_ok=True)
    (output / "benchmark.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    (output / "benchmark.csv").write_text(csv_report(reports), encoding="utf-8-sig")
    (output / "summary.json").write_text(json.dumps({k: v for k, v in payload.items() if k != "runs"}, indent=2, allow_nan=False), encoding="utf-8")
    return payload


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=Path("outputs/benchmark"))
    p.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    p.add_argument("--budget", type=int, default=30)
    args = p.parse_args()
    run_benchmark(args.output, [int(s) for s in args.seeds.split(",")], args.budget)


if __name__ == "__main__":
    main()
