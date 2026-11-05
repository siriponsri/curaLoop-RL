"""Timing-only canary projection; never read discovery or predictor scores."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=["diagnosis", "campaign"])
    args = p.parse_args()
    run = ROOT / ".local/goal4r1-20261105-v1"
    path = run / "runs" / (args.phase + "_canary-v1") / "shard-0/resources.json"
    r = json.loads(path.read_text())
    total, count, cap = (576, 12, 7200) if args.phase == "diagnosis" else (3072, 52, 10800)
    projection = r["cpu_seconds"] * total / count * 3
    if r["status"] != "PASS" or r["completed_cases"] != count or projection > cap * .8:
        raise ValueError("Fixed full design fails timing-only feasibility gate.")
    report = {"status": "PASS_TIMING_ONLY_ALLOCATION", "utc": datetime.now(timezone.utc).isoformat(),
              "phase": args.phase, "factor": 3, "canary_cases": count,
              "canary_cpu_seconds": r["cpu_seconds"], "projected_full_cpu_seconds": projection,
              "planned_cases": total, "workers": 4, "cpus": [71, 70, 69, 68],
              "cpu_exclusivity_claimed": False, "candidate_selection_or_outcome_metrics_read": False,
              "case_reuse": False, "canary_separately_charged": True}
    output = ROOT / "docs/evidence/goal4r1-20261105-v1" / (args.phase + "-allocation-v1.json")
    with output.open("x") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
