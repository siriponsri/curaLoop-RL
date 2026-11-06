"""Run the fixed offline demonstration without network or scientific execution."""

import argparse
import json
from pathlib import Path

from .demo import run_demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run_demo(args.output), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
