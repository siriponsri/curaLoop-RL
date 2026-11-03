"""Compare protected files with the fixed pre-change Git revision, byte for byte."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "b16d2fb9ee56d03fdc6cf0628fc444670a433c43"
PROTECTED = (
    "src/curaloop/resources/", "docs/evidence/", "requirements_v3/",
    "docs/requirements/", "history/", "papers/", "assets/", "frontend/public/",
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=ROOT / "docs/evidence/poc-v0.3/preservation.json")
    args = parser.parse_args()
    paths = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", BASE], cwd=ROOT, text=True,
    ).splitlines()
    checks = []
    for name in paths:
        if not name.startswith(PROTECTED):
            continue
        original = subprocess.check_output(["git", "show", f"{BASE}:{name}"], cwd=ROOT)
        path = ROOT / name
        actual = path.read_bytes() if path.is_file() else None
        checks.append({
            "path": name,
            "expected_sha256": hashlib.sha256(original).hexdigest(),
            "actual_sha256": hashlib.sha256(actual).hexdigest() if actual is not None else None,
            "matches": actual == original,
        })
    result = {"status": "PASS" if all(c["matches"] for c in checks) else "FAIL",
              "base_commit": BASE, "protected_file_count": len(checks), "checks": checks}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"{result['status']}: {len(checks)} protected files checked against {BASE}")
    for check in checks:
        if not check["matches"]:
            print(check["path"])
    raise SystemExit(0 if result["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
