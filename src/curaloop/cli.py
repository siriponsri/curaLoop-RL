"""Offline reproducible runs, paired-seed evaluations and public-log replay checks."""

import argparse
import json
from pathlib import Path

from .domain import DATASETS, POLICIES, Scenario
from .export import csv_report, json_report
from .service import RunService, compare, evaluate_seeds


def main() -> None:
    parser = argparse.ArgumentParser(description="CuraLoop-RL synthetic screening simulator")
    parser.add_argument("command", choices=("demo", "compare", "evaluate", "replay"))
    parser.add_argument("--dataset", choices=DATASETS, default=DATASETS[0])
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--budget", type=int, default=30)
    parser.add_argument("--batch-size", type=int, default=5)
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--policy", choices=POLICIES, default="greedy")
    parser.add_argument("--seeds", default="0,1,2,3,4,5,6,7,8,9")
    parser.add_argument("--config", type=Path, help="Strict local JSON Scenario fields")
    parser.add_argument("--input", type=Path, help="Public JSON report for deterministic replay")
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    try:
        if args.command == "replay":
            if args.input is None:
                parser.error("replay requires --input report.json")
            if args.input.stat().st_size > 20_000_000:
                raise ValueError("Replay report exceeds the 20 MB input limit.")
            payload = json.loads(args.input.read_text(encoding="utf-8"))
            for original in payload["runs"]:
                m = original["manifest"]
                run = RunService(Scenario(**m["scenario_config"]), m["policy_id"])
                # Partial UI exports are valid reports but not full-campaign replay inputs.
                if not m["finished"]:
                    raise ValueError("Replay CLI currently supports completed campaigns only.")
                run.finish()
                replayed = run.report()
                for key in ("events", "metrics", "requests", "delivered_results", "curve"):
                    if replayed[key] != original[key]:
                        raise ValueError(f"Replay mismatch: {key}; check source/dependency versions.")
            print(f"Replay PASS: {len(payload['runs'])} completed runs, exact public event records.")
            return
        scenario = Scenario(
            dataset=args.dataset, seed=args.seed, budget_units=args.budget,
            batch_size=args.batch_size, delay_steps=args.delay,
        )
        if args.config:
            if args.config.stat().st_size > 100_000:
                raise ValueError("Configuration exceeds 100 kB.")
            scenario = Scenario(**json.loads(args.config.read_text(encoding="utf-8")))
        if args.command == "evaluate":
            seeds = [int(s) for s in args.seeds.split(",")]
            if len(seeds) > 100:
                raise ValueError("At most 100 seeds per local evaluation.")
            payload = evaluate_seeds(scenario, seeds)
            reports = payload["runs"]
        elif args.command == "compare":
            reports = compare(scenario)
            payload = None
        else:
            run = RunService(scenario, args.policy)
            run.finish()
            reports = [run.report()]
            payload = None
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "report.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
            if payload else json_report(reports), encoding="utf-8",
        )
        (args.output / "report.csv").write_text(csv_report(reports), encoding="utf-8-sig")
        for report in reports:
            m, metric = report["manifest"], report["metrics"]
            print(f"{m['policy_id']:12s} seed={m['seed']} hits={metric['confirmed_hits']} "
                  f"spent={metric['spent_units']} step={metric['step']} "
                  f"{m['data_origin']}")
        print(f"Reports: {args.output.resolve()}")
    except (ValueError, TypeError, KeyError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
