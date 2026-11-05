"""Closed hash-checked source bundle; no private records in bootstrap stage."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--development-inputs", action="store_true")
    args = p.parse_args()
    run = ROOT / ".local/goal4r1-20261105-v1"
    run.mkdir(parents=True, exist_ok=True)
    names = {str(p.relative_to(ROOT)).replace("\\", "/")
             for folder in ("research/redesign_v1", "research/planning_v3")
             for p in (ROOT / folder).glob("*.py")}
    names.update(("research/event_time.py", "research/study_v1/__init__.py", "research/study_v1/campaign.py",
                  "tools/resource_guard_v1.py", "tools/goal4r1_setup_v1.py", "tools/goal4r1_admin_v1.py",
                  "tests/research/test_goal4r1_v1.py", "research/requirements_goal4r1_v1.txt"))
    for name in ("research/__init__.py", "tools/__init__.py", "research/configs/goal4r1_protocol_v1.json",
                 "docs/evidence/goal4r1-20261105-v1/protocol-freeze-v1.json"):
        if (ROOT / name).is_file():
            names.add(name)
    private_count = 0
    if args.development_inputs:
        config = json.loads((ROOT / "research/configs/goal4r1_protocol_v1.json").read_text())
        if config["status"] != "FROZEN_BEFORE_NEW_CODE_EVALUATION":
            raise ValueError("Freeze before packaging exposed development inputs.")
        for task in config["tasks"]:
            path = run / "private-inputs" / (task["task_id"] + ".json")
            if task["role"] != "development" or hashlib.sha256(path.read_bytes()).hexdigest() != task["sha256"]:
                raise ValueError("Private task identity/role changed.")
            names.add(path.relative_to(ROOT).as_posix())
            private_count += 1
    rows = []
    with zipfile.ZipFile(run / (args.name + ".zip"), "x", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(names):
            data = (ROOT / name).read_bytes()
            z.writestr(name, data)
            rows.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    manifest = {"files": rows, "archive_sha256": hashlib.sha256((run / (args.name + ".zip")).read_bytes()).hexdigest(),
                "private_outcome_files": private_count}
    (run / (args.name + ".json")).write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"status": "PASS", "files": len(rows), "private_outcome_files": private_count,
                      "archive_sha256": manifest["archive_sha256"]}))


if __name__ == "__main__":
    main()
