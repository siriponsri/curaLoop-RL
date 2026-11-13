"""Recompute the three public RDKit cases without a model or private research data."""
import argparse
import json
from pathlib import Path

from curaloop_rd.local_agent_v1.chemistry import FilterSpec
from curaloop_rd.local_agent_v1.workflow import build_bundle, inspect_bundle


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True, help="A new local folder; existing evidence is never overwritten")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[2]
    freeze = json.loads((root / "docs/evidence/lr-dc2-local-20261113-v1/product-acceptance-freeze-v1.json").read_text(encoding="utf-8"))
    results = []
    for case in freeze["cases"][::2]:
        folder = args.output / case["id"]
        result = build_bundle(folder, freeze["csv_text"], FilterSpec(**case["expected_parameters"]))
        inspected = inspect_bundle(folder, result["manifest_sha256"], result["bundle_sha256"])
        report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
        actual = sorted(c["compound_id"] for c in report["compounds"] if c["selected"])
        passed = actual == sorted(case["expected_selected_ids"])
        results.append({"case":case["id"],"status":"PASS" if passed else "FAIL","selected":actual,"current_evidence":inspected})
    summary = {"scope":"New actual deterministic RDKit computation; zero model calls, not a reproduction of comparative agent efficacy","results":results}
    (args.output / "reproduction.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary))
    return 0 if all(r["status"]=="PASS" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
