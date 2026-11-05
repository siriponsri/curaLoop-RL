"""Build a closed source+development-input bundle, with no final outcomes."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    packet = ROOT / "docs/evidence/goal4-20261105-v1"
    run = ROOT / ".local/plan-a-20261105-v2"
    proof = json.loads((packet / "protocol-freeze-v1.json").read_text())
    names = set(proof["source_sha256"])
    names.update([
        "research/configs/goal4_protocol_v1.json", "research/requirements_plan_a_constructed_v1.txt",
        "docs/evidence/goal4-20261105-v1/protocol-freeze-v1.json",
        "docs/evidence/goal4-20261105-v1/allocation-freeze-v1.json",
        "docs/evidence/goal4-20261105-v1/label-access-development-v1.json",
        "tools/remote_goal4_setup_v1.py", ".local/plan-a-20261105-v2/allocation.json",
    ])
    for name in ("research/__init__.py", "research/benchmark_v3/__init__.py", "tools/__init__.py"):
        if (ROOT / name).exists():
            names.add(name)
    for path in (run / "private-inputs/development").glob("*.json"):
        names.add(path.relative_to(ROOT).as_posix())
    output = run / "remote-input-v1.zip"
    rows = []
    with zipfile.ZipFile(output, "x", zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(names):
            path = ROOT / name
            if path.is_symlink() or not path.is_file() or path.stat().st_size > 16*1024**2:
                raise ValueError("Unexpected input entry.")
            data = path.read_bytes()
            archive.writestr(name, data)
            rows.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    report = {"status": "PASS_CLOSED_INPUT_BUNDLE", "files": rows, "archive_bytes": output.stat().st_size,
              "archive_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
              "final_outcome_inputs": 0, "development_tasks": 6,
              "private_input_rows_or_outcomes_in_public_receipt": False}
    (run / "remote-input-v1-manifest.json").open("x", encoding="utf-8").write(json.dumps(report, indent=2) + "\n")
    (packet / "remote-input-bundle-v1.json").open("x", encoding="utf-8").write(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, indent=2))


if __name__ == "__main__":
    main()
