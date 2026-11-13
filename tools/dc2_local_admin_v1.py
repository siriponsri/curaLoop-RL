"""Fresh owner-approved local-agent account; never resets prior accounts."""

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone

from dc2_admin_v1 import ROOT, preserve, read, sha, write

TASK = ROOT / ".local/lr-dc2-local-20261113-v1"
PUBLIC = ROOT / "docs/evidence/lr-dc2-local-20261113-v1"
DEADLINE = "2026-11-20T11:51:07+00:00"
OLD_TASK = ROOT / ".local/lr-dc2-20261111-v1"


def save(ledger):
    write(TASK / "ledger.next.json", ledger, False)
    os.replace(TASK / "ledger.next.json", TASK / "ledger.json")


def verify_preservation(release):
    old = read(OLD_TASK / "release.json")
    preserve(old)
    assert sha(OLD_TASK / "ledger.json") == release["superseded_account_ledger_sha256"]
    for path, identity in release["new_preservation_pins"].items():
        assert sha(ROOT / path) == identity, path


def init():
    old_release, old_ledger = read(OLD_TASK / "release.json"), read(OLD_TASK / "ledger.json")
    preserve(old_release)
    assert old_ledger["status"] == "RESUMED_SCOPE_ADOPTED_BUDGET_PENDING"
    assert not any(b["status"] == "RESERVED" for b in old_ledger["bookings"].values())
    assert sum(old_ledger["retained_cpu_seconds"].values()) == 2430
    assert sum(old_ledger["retained_gpu_seconds"].values()) == 0
    now = datetime.now(timezone.utc)
    assert now < datetime.fromisoformat(DEADLINE)
    head = subprocess.check_output(
        ["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    assert head == "46a1c6f4fed2b540a30eeaed775123c98a3bca1f"
    pins = {
        path: sha(ROOT / path)
        for path in (
            "research/manifests/lr_dc2_release_20261111_v1.json",
            "research/manifests/lr_dc2_owner_clock_amendment_20261111_v1.json",
            "research/manifests/lr_dc2_resume_review_20261113_v1.json",
            "research/manifests/lr_dc2_local_scope_adoption_20261113_v1.json",
            "docs/08_agent_rd/LOCAL_AGENT_PROPOSAL_REVIEW_20261113.md",
            "docs/08_agent_rd/LOCAL_AGENT_PROTOCOL_DESIGN_20261113.md",
            "docs/08_agent_rd/LR_DC2_DATASET_PAUSE_HANDOFF_20261111.md",
            "docs/evidence/lr-dc2-20261111-v1/owner-pause-v1.json",
        )
    }
    release = {
        "schema": "curaloop.lr-dc2-local.release.v1",
        "status": "OWNER_RELEASED_LOCAL_WORKFLOW_AND_MATCHED_STUDY",
        "recorded_utc": now.isoformat(),
        "base_commit": head,
        "owner_scope_decision": "Adopt new local scientific workflow proposal, option A",
        "owner_resource_decision": "B: fresh 96 CPU-hours and 24 allocated GPU-hours",
        "clock_start_utc": "2026-11-13T11:51:07+00:00",
        "deadline_utc": DEADLINE,
        "cpu_cap_seconds": 96 * 3600,
        "gpu_allocated_cap_seconds": 24 * 3600,
        "combined_cpu_cores": 4,
        "local_cpu_cores": 1,
        "remote_cpu_equivalent": 3,
        "local_max_memory_bytes": 2 * 1024**3,
        "remote_max_memory_bytes": 32 * 1024**3,
        "remote_swap_bytes": 0,
        "gpu_workers": 1,
        "prior_retained_cpu_seconds": 2430,
        "prior_retained_gpu_seconds": 0,
        "cumulative_cpu_ceiling_seconds": 96 * 3600 + 2430,
        "superseded_account_ledger_sha256": sha(OLD_TASK / "ledger.json"),
        "superseded_account_raw_status_preserved": old_ledger["status"],
        "superseded_unused_allowance_available": False,
        "new_preservation_pins": pins,
        "feasibility_cpu_cap_seconds": 4 * 3600,
        "feasibility_gpu_cap_seconds": 3600,
        "development_provider_call_cap": 96,
        "primary_model_count": 1,
        "permitted_models": [
            "existing Typhoon2.1 Gemma3 12B Q4_K_M",
            "Qwen/Qwen2.5-14B-Instruct-GGUF Q4_K_M",
        ],
        "new_model_download_cap_bytes": 12 * 1024**3,
        "new_benchmark_download_cap_bytes": 4 * 1024**3,
        "task_owned_disk_cap_bytes": 48 * 1024**3,
        "remote_root": "/home/chaw/curaloop-tasks/lr-dc2-local-20261113-v1",
        "remote_root_created": False,
        "routine_phase_approval_required": False,
        "fallback": "Same real local workflow and negative/inconclusive feasibility/software report; no substitute benchmark, model search or second mechanism",
        "final16_access": False,
        "private_cf1_rows_access": False,
        "old_hidden_outcomes_access": False,
        "paid_api_or_rental": False,
        "public_deployment": False,
        "external_team_writes": False,
        "manuscript_submission": False,
        "main_delivery_authorized": True,
    }
    verify_preservation(release)
    TASK.mkdir(exist_ok=False)
    cpu_hours = {
        "admission": 4,
        "implementation": 16,
        "development": 8,
        "evaluation": 44,
        "analysis_manuscript": 12,
        "return_delivery": 8,
        "technical_retry": 4,
    }
    gpu_hours = {
        "admission": 1,
        "implementation": 0,
        "development": 3,
        "evaluation": 18,
        "analysis_manuscript": 0,
        "return_delivery": 0,
        "technical_retry": 2,
    }
    assert sum(cpu_hours.values()) == 96 and sum(gpu_hours.values()) == 24
    write(TASK / "release.json", release)
    write(ROOT / "research/manifests/lr_dc2_local_release_20261113_v1.json", release)
    write(PUBLIC / "owner-resource-release-v1.json", release)
    save(
        {
            "schema": "curaloop.lr-dc2-local.ledger.v1",
            "status": "ACTIVE_ADMISSION",
            "deadline_utc": DEADLINE,
            "stage_cpu_caps_seconds": {k: v * 3600 for k, v in cpu_hours.items()},
            "stage_gpu_caps_seconds": {k: v * 3600 for k, v in gpu_hours.items()},
            "retained_cpu_seconds": {k: 900 if k == "admission" else 0 for k in cpu_hours},
            "retained_gpu_seconds": dict.fromkeys(gpu_hours, 0),
            "bookings": {
                "administrative-control-v1": {
                    "status": "RETAINED_UNMETERED_CONTROL_ALLOWANCE",
                    "host": "control",
                    "bucket": "admission",
                    "cpu_cap": 900,
                    "gpu_cap": 0,
                    "measured_cpu_seconds": None,
                    "note": "Read/author/coordinate control work not separately metered; allocation is not measured CPU or retrospective enforcement",
                }
            },
            "gates": {},
            "downloads_bytes": 0,
            "model_calls": 0,
            "development_model_calls": 0,
            "generated_tokens": 0,
        }
    )
    print(
        json.dumps(
            {
                "status": "PASS_FRESH_RESOURCE_RELEASE",
                "cpu_hours": 96,
                "gpu_hours": 24,
                "prior_cpu_hours_preserved": 0.675,
                "deadline_utc": DEADLINE,
            }
        )
    )


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"].startswith("ACTIVE")
    assert datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    verify_preservation(release)
    return release, ledger


def run(args):
    from dc2_local_guard_v1 import LocalGuard

    release, ledger = authority()
    if ledger.get("admission_closed"):
        assert args.bucket in (
            "implementation",
            "development",
            "analysis_manuscript",
            "return_delivery",
            "technical_retry",
        )
    assert args.name not in ledger["bookings"]
    assert not any(
        b["status"] == "RESERVED" and b["host"] == "local" for b in ledger["bookings"].values()
    )
    assert 0 < args.cpu <= args.wall
    ledger["retained_cpu_seconds"][args.bucket] += args.cpu
    assert (
        ledger["retained_cpu_seconds"][args.bucket] <= ledger["stage_cpu_caps_seconds"][args.bucket]
    )
    assert sum(ledger["retained_cpu_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"][args.name] = {
        "status": "RESERVED",
        "host": "local",
        "bucket": args.bucket,
        "cpu_cap": args.cpu,
        "gpu_cap": 0,
        "command": args.command,
    }
    save(ledger)
    folder = TASK / "jobs" / args.name
    folder.mkdir(parents=True, exist_ok=False)
    write(folder / "controller-source-pin.json", {"path": __file__, "sha256": sha(__file__)})
    # Earlier jobs retain their original pins. Capture future executed sources only.
    paths = set()
    for base in ("src/curaloop_rd/local_agent_v1", "research/local_agent_eval_v1", "api"):
        paths.update(p for p in (ROOT / base).rglob("*.py") if "__pycache__" not in p.parts)
    paths.update((ROOT / "tools").glob("dc2_local_*.py"))
    paths.update((ROOT / "tests").glob("test_local_*v1.py"))
    for base in ("frontend/src",):
        paths.update(p for p in (ROOT / base).rglob("*") if p.is_file())
    identities = {}
    for source in sorted(paths):
        relative = source.relative_to(ROOT)
        target = folder / "source" / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        identities[relative.as_posix()] = sha(target)
    write(folder / "source-manifest.json", {"sha256": identities, "scope": "Listed Python/API sources; not a full repository snapshot"})
    guard = None
    try:
        guard = LocalGuard(folder / "resource.json", args.cpu, release["deadline_utc"], args.wall)
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src") + os.pathsep + str(ROOT))
        with (folder / "stdout.txt").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
            result = subprocess.run(args.command, cwd=ROOT, env=env, stdout=out, stderr=err)
        status = "PASS" if result.returncode == 0 else "FAIL"
        guard.finish(status)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name].update(
            status=status,
            exit_code=result.returncode,
            resource_sha256=sha(folder / "resource.json"),
        )
        save(ledger)
        print(
            json.dumps(
                {"name": args.name, "status": status, "resource": read(folder / "resource.json")}
            )
        )
        print((folder / "stdout.txt").read_text(encoding="utf-8", errors="replace")[-7000:])
        if result.returncode:
            print((folder / "stderr.txt").read_text(encoding="utf-8", errors="replace")[-3000:])
        return result.returncode
    except BaseException:
        if guard is not None:
            guard.finish("FAIL")
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name]["status"] = "FAIL"
        save(ledger)
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init")
    job = sub.add_parser("run")
    for name in ("name", "bucket"):
        job.add_argument(name)
    for name in ("cpu", "wall"):
        job.add_argument(name, type=int)
    job.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == "init":
        init()
    else:
        raise SystemExit(run(args))
