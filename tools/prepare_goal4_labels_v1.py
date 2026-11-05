"""Guarded role-specific private projection after protocol and access gates."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from tools.resource_guard_v1 import Guard

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=["development", "validation"], required=True)
    args = parser.parse_args()
    packet = ROOT / "docs/evidence/goal4-20261105-v1"
    receipt = packet / f"label-access-{args.role}-v1.json"
    if receipt.exists():
        raise FileExistsError("Preserve existing access receipts.")
    # Git creates a child process, so this outcome-free check MUST precede Guard.
    # Guard retains its active_process_limit=1 throughout actual row projection.
    relative = f".local/plan-a-20261105-v2/private-inputs/{args.role}"
    if subprocess.run(["git", "check-ignore", "--quiet", "--", relative], cwd=ROOT).returncode != 0:
        raise ValueError("Private output is not git-ignored.")
    with (packet / f"ignored-path-{args.role}-v1.json").open("x", encoding="utf-8", newline="\n") as handle:
        json.dump({"status": "PASS_GIT_IGNORE_PREFLIGHT", "output_relative": relative,
                   "gitignore_sha256": hashlib.sha256((ROOT / ".gitignore").read_bytes()).hexdigest(),
                   "before_resource_guard": True, "outcome_access": False}, handle, indent=2)
        handle.write("\n")
    guard = Guard(packet / f"label-access-{args.role}-resources-v1.json", 900, 1024**3, 900)
    try:
        from research.study_v1.identity import verify_frozen, RUN_RELATIVE, CONFIG_RELATIVE
        from research.study_v1.labels import LabelAccessError, prepare_role
        from research.benchmark_v3.prepare_features_v2 import write_new, sha_file
        protocol = verify_frozen(ROOT)
        parent = ROOT / RUN_RELATIVE / "private-inputs"
        parent.mkdir(parents=True, exist_ok=True)
        output = parent / args.role
        tasks = prepare_role(args.role, protocol, ROOT, output)
        write_new(receipt, {"status": "PASS_TRUSTED_ROLE_CHECKED_PREPARATION", "role": args.role,
                  "tasks": [{k: task[k] for k in ("task_id", "role", "family_id", "rows", "sha256")} for task in tasks],
                  "private_manifest_sha256": sha_file(output / "manifest.json"),
                  "protocol_sha256": sha_file(ROOT / CONFIG_RELATIVE),
                  "source_boolean_mapping": "Pinned FS-Mol bool(float(Property)); restricted to finite binary numeric values, including numeric strings",
                  "outcomes_emitted_to_agents": False, "final_outcomes_prepared": False})
        guard.finish("PASS", tasks_prepared=len(tasks), final_outcome_use=False)
        print(json.dumps({"status": "PASS", "role": args.role, "tasks": len(tasks), "outcome_values_emitted": False}))
    except Exception as error:
        code = str(error) if type(error).__name__ == "LabelAccessError" else type(error).__name__
        guard.finish("FAIL", sanitized_reason=code)
        (packet / f"label-access-{args.role}-failure-v1.json").write_text(json.dumps({"status": "FAIL", "reason": code}) + "\n")
        print(json.dumps({"status": "FAIL", "reason": code}))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
