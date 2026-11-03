"""Build a wheel with a genuine source revision even outside a Git checkout."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = bool(subprocess.check_output(["git", "diff", "--name-only", "HEAD", "--", "src", "pyproject.toml"], cwd=ROOT, text=True).strip())
    (ROOT / "src/curaloop/resources/build_info.json").write_text(json.dumps({
        "source_commit": sha, "source_working_tree_dirty": dirty,
        "note": "Build-time identity, not a claim that installed wheel has a Git working tree."
    }, indent=2), encoding="utf-8")
    subprocess.run([sys.executable, "-m", "build", "--wheel", "--no-isolation"], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
