"""Fresh LR-SC1 administrative account; never opens historical scientific data."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = ROOT / ".local/lr-sc1-20261113-v1"
PUBLIC = ROOT / "docs/evidence/lr-sc1-20261113-v1"
RELEASE = ROOT / "research/manifests/lr_sc1_release_20261113_v1.json"
START = "2026-11-13T16:03:03+00:00"
DEADLINE = "2026-11-27T16:03:03+00:00"
STAGES = {
    "gate0": (7200, 0), "admission": (50400, 7200),
    "development": (57600, 28800), "evaluation": (230400, 259200),
    "analysis_delivery": (86400, 21600), "technical_reserve": (28800, 28800),
}


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False)
        stream.write("\n")


def init():
    if RELEASE.exists() or (ACCOUNT / "ledger.json").exists():
        raise RuntimeError("Existing account must be resumed, never reset")
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    if branch != "main" or head != "1c3e1de1e6a28f8116ca45babb2f2bf8733f1bfb":
        raise RuntimeError("Review changed checkout before releasing account")
    previous = ROOT / ".local/lr-dc2-local-20261113-v1/ledger.json"
    old = json.loads(previous.read_text(encoding="utf-8"))
    if old["status"] != "COMPLETE_LOCAL_WORKFLOW_FEASIBILITY_ACCOUNT_CLOSED":
        raise RuntimeError("Previous account not closed")
    source_paths = [
        "docs/08_agent_rd/NEXT_GOAL_SCIENTIFIC_VALIDATION_PROPOSAL_20261113.md",
        "research/manifests/lr_dc2_local_release_20261113_v1.json",
        "docs/evidence/lr-dc2-local-20261113-v1/delivery-audit-v1.json",
        ".local/lr-dc2-local-20261113-v1/ledger.json",
        ".local/lr-dc2-local-20261113-v1/release.json",
    ]
    pins = {name: digest(ROOT / name) for name in source_paths}
    prior_release = json.loads((ROOT / source_paths[1]).read_text(encoding="utf-8"))
    for name in prior_release["new_preservation_pins"]:
        pins[name] = digest(ROOT / name)
    prior_manifest = ROOT / "research/manifests/agent_rd_release_20261110_v1.json"
    pins[str(prior_manifest.relative_to(ROOT)).replace("\\", "/")] = digest(prior_manifest)
    old_agent = json.loads(prior_manifest.read_text(encoding="utf-8"))
    for key, value in old_agent.items():
        if "pin" in key and isinstance(value, dict):
            for name in value:
                if (ROOT / name).is_file():
                    pins[name] = digest(ROOT / name)
    release = {
        "schema": "curaloop.lr-sc1.release.v1", "status": "OWNER_AUTHORIZED",
        "owner_instruction": "Approve LR-SC1 as proposed; SciCode; 128 CPU-hours + 96 GPU-hours / 14 days; advance only through passed gates, stop and report a failed gate without repeated experiments; manuscript and Empirical Software Engineering readiness; commit/push main",
        "base_commit": head, "start_utc": START, "deadline_utc": DEADLINE,
        "deadline_bangkok": "2026-11-27T23:03:03+07:00",
        "cpu_cap_seconds": 460800, "gpu_allocated_cap_seconds": 345600,
        "stage_caps_seconds": {k: {"cpu": v[0], "gpu_allocated": v[1]} for k, v in STAGES.items()},
        "max_combined_cpu_equivalents": 4, "local_cpu_equivalents": 1,
        "remote_cpu_equivalents": 3, "max_gpu_workers": 1,
        "local_memory_bytes": 2147483648, "remote_memory_bytes": 34359738368,
        "remote_swap_bytes": 0, "benchmark_intake_cap_bytes": 10737418240,
        "model_intake_cap_bytes": 10737418240, "task_owned_disk_cap_bytes": 68719476736,
        "models": ["Qwen/Qwen2.5-Coder-14B-Instruct-GGUF Q4_K_M", "existing Typhoon 2.1 Gemma3 12B Q4_K_M"],
        "benchmark": "SciCode; six fixed official validation problems; target all 65 test main problems, minimum 50 technically eligible before generation",
        "previous_account_reuse": False, "closed_account_ledger_sha256": digest(previous),
        "preservation_pins": pins, "final16_access": False, "private_cf1_rows_access": False,
        "old_hidden_outcomes_access": False, "paid_api_or_rental": False,
        "public_deployment": False, "manuscript_submission": False,
        "new_subagents": False, "main_commit_push_authorized": True,
        "gate0_required_before_intake_or_remote_compute": True,
        "remote_root": "/home/chaw/curaloop-tasks/lr-sc1-20261113-v1",
    }
    write_new(RELEASE, release)
    write_new(ACCOUNT / "release.json", release)
    ledger = {
        "schema": "curaloop.lr-sc1.ledger.v1", "status": "ACTIVE_GATE0",
        "release_sha256": digest(RELEASE), "deadline_utc": DEADLINE,
        "reservations": [{"id": "gate0-admin-v1", "stage": "gate0", "cpu_seconds": 7200,
                          "gpu_allocated_seconds": 0, "status": "RETAINED_CONSERVATIVE_UNMETERED_CONTROL_ALLOWANCE",
                          "scope": "Repository/bootstrap/source inspection, bounded literature audit and gate0 closeout control; actual aggregate CPU not established; not a model job"}],
        "active_jobs": [], "prior_accounts_unchanged": True,
    }
    write_new(ACCOUNT / "ledger.json", ledger)
    write_new(PUBLIC / "release-v1.json", release)
    print(json.dumps({"status": "ACTIVE_GATE0", "deadline_utc": DEADLINE,
                      "preservation_pin_count": len(pins), "gpu_jobs": 0}))


def verify():
    release = json.loads(RELEASE.read_text(encoding="utf-8"))
    checks = {name: (ROOT / name).is_file() and digest(ROOT / name) == expected
              for name, expected in release["preservation_pins"].items()}
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks}
    print(json.dumps(result, indent=2))
    return 0 if all(checks.values()) else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("init", "verify"))
    args = parser.parse_args()
    if args.action == "init":
        init()
        return 0
    return verify()


if __name__ == "__main__":
    sys.exit(main())
