"""Pure offline re-analysis of returned LR-D23 rows; never launches a campaign."""
# ruff: noqa: E402

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.analysis import analyze


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("rows", type=Path)
    parser.add_argument("expected", type=Path)
    parser.add_argument("--transfer", action="store_true")
    args = parser.parse_args()
    rows = json.loads(args.rows.read_text(encoding="utf-8"))
    result = analyze(rows, require_attribution=not args.transfer, budget=rows[0]["spec"]["budget"])
    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    assert result == expected, "OFFLINE_AGGREGATE_REPRODUCTION_MISMATCH"
    print(json.dumps({"status": "PASS_EXACT_OFFLINE_AGGREGATE_REPRODUCTION",
                      "units": result["unit_count"], "scientific_disposition": result["status"]}))


if __name__ == "__main__":
    main()
