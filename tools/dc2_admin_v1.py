"""Fresh LR-DC2 resource account; historical artifacts are read-only inputs."""

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/lr-dc2-20261111-v1"
PUBLIC = ROOT / "docs/evidence/lr-dc2-20261111-v1"
PROPOSAL = ROOT / "docs/08_agent_rd/NEXT_GOAL_DECISION_CONTRACT_PROPOSAL_20261111.md"
CONFIG = ROOT / "research/configs/lr_dc2_proposal_20261111_v1.json"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, value, exclusive=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def save(ledger):
    write(TASK / "ledger.next.json", ledger, False)
    os.replace(TASK / "ledger.next.json", TASK / "ledger.json")


def preserve(release):
    for group in ("prior_ledger_pins", "old_scientific_pins", "agent_rd_frozen_pins", "prior_agent_rd_artifact_pins"):
        assert all(sha(ROOT / path) == identity for path, identity in release[group].items()), group
    assert sha(PROPOSAL) == release["proposal_sha256"]
    assert sha(CONFIG) == release["proposal_config_sha256"]


def init():
    head = subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert head == "4247a2c63c6eaf32c87028738282888c8ef52791"
    previous = read(ROOT / "research/manifests/agent_rd_release_20261110_v1.json")
    ledgers = {**previous["prior_ledger_pins"],
               ".local/agent-rd-run-20261110-v1/ledger.json": sha(ROOT / ".local/agent-rd-run-20261110-v1/ledger.json")}
    assert len(ledgers) == 15
    assert read(ROOT / ".local/agent-rd-run-20261110-v1/ledger.json")["status"] == "CLOSED_DELIVERED_COMPUTATIONAL_REPORT"
    frozen = read(ROOT / "research/manifests/agent_rd_protocol_freeze_20261110_v1.json")
    artifacts = {p.relative_to(ROOT).as_posix(): sha(p)
                 for p in sorted((ROOT / "docs/evidence/agent-rd-20261110-v1").rglob("*")) if p.is_file()}
    for name in ("docs/manual/CuraLoop-AgentRD-Guide-EN-v2.pdf",
                 "docs/07_publication/CuraLoop-AgentRD-Computational-Report-EN-v1.pdf",
                 "docs/07_publication/CuraLoop-AgentRD-Computational-Report-EN-v2.pdf",
                 "docs/07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V1.md",
                 "docs/07_publication/CURALOOP_AGENTRD_COMPUTATIONAL_REPORT_EN_V2.md"):
        artifacts[name] = sha(ROOT / name)
    # Minute floor of the first trusted clock after this owner's approval.
    start = datetime(2026, 11, 11, 7, 39, tzinfo=timezone.utc)
    release = {"schema": "curaloop.lr-dc2.release.v1", "status": "OWNER_RELEASED_GATED_EXECUTION",
        "base_commit": head, "release_utc": start.isoformat(), "deadline_utc": (start + timedelta(hours=168)).isoformat(),
        "cpu_cap_seconds": 64 * 3600, "gpu_allocated_cap_seconds": 24 * 3600,
        "combined_cpu_cores": 4, "local_cpu_cores": 1, "local_max_memory_bytes": 2 * 1024 ** 3,
        "remote_cpu_equivalent": 3, "remote_max_memory_bytes": 32 * 1024 ** 3, "remote_swap_bytes": 0,
        "gpu_workers": 1, "gpu_min_vram_bytes": 24 * 1024 ** 3,
        "proposal_sha256": sha(PROPOSAL), "proposal_config_sha256": sha(CONFIG),
        "proposal_snapshot_remains_disabled": True, "prior_ledger_pins": ledgers,
        "prior_recorded_ledger_statuses": {path: read(ROOT / path)["status"] for path in ledgers},
        "old_scientific_pins": previous["frozen_scientific_pins"], "agent_rd_frozen_pins": frozen["pins"],
        "prior_agent_rd_artifact_pins": artifacts,
        "remote_root": "/home/chaw/curaloop-tasks/lr-dc2-20261111-v1",
        "remote_root_created": False, "gpu_admitted": False,
        "model_download_cap_bytes": 12 * 1024 ** 3, "benchmark_download_cap_bytes": 4 * 1024 ** 3,
        "total_new_download_cap_bytes": 22 * 1024 ** 3, "task_owned_disk_cap_bytes": 48 * 1024 ** 3,
        "stop_on_first_failed_gate": True, "automatic_model_or_dataset_substitution": False,
        "original_final16_access": False, "private_cf1_rows_access": False, "old_hidden_outcomes_access": False,
        "paid_api_or_rental": False, "public_deployment": False, "external_team_writes": False,
        "manuscript_submission": False, "main_delivery_authorized": True}
    preserve(release)
    TASK.mkdir(exist_ok=False)
    write(TASK / "release.json", release)
    write(ROOT / "research/manifests/lr_dc2_release_20261111_v1.json", release)
    cpu_caps = {"admission": 28800, "implementation": 43200, "development": 21600,
                "evaluation": 79200, "analysis_manuscript": 28800, "return_delivery": 14400, "technical_retry": 14400}
    gpu_caps = {"admission": 3600, "implementation": 0, "development": 10800,
                "evaluation": 64800, "analysis_manuscript": 0, "return_delivery": 0, "technical_retry": 7200}
    assert sum(cpu_caps.values()) == release["cpu_cap_seconds"]
    assert sum(gpu_caps.values()) == release["gpu_allocated_cap_seconds"]
    save({"schema": "curaloop.lr-dc2.ledger.v1", "status": "ACTIVE_ADMISSION", "stage_cpu_caps_seconds": cpu_caps,
          "stage_gpu_caps_seconds": gpu_caps, "retained_cpu_seconds": {k: 600 if k == "admission" else 0 for k in cpu_caps},
          "retained_gpu_seconds": dict.fromkeys(gpu_caps, 0), "release_utc": release["release_utc"],
          "deadline_utc": release["deadline_utc"], "bookings": {
              "interactive-administrative-control-v1": {"status": "RETAINED_UNMETERED_CONTROL_ALLOWANCE", "host": "control",
                  "bucket": "admission", "cpu_cap": 600, "gpu_cap": 0, "measured_cpu_seconds": None,
                  "note": "Administrative reading/authoring/tool coordination not separately metered; allocation is not measured use or retroactive hard enforcement"}},
          "gates": {}, "downloads_bytes": 0, "model_calls": 0, "generated_tokens": 0})
    write(PUBLIC / "release-admission-v1.json", {"status": "PASS_FRESH_OWNER_LR_DC2_RELEASE", "base_commit": head,
          "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
          "cpu_cap_hours": 64, "gpu_allocated_cap_hours": 24, "prior_ledgers_preserved": len(ledgers),
          "old_scientific_pins_preserved": len(release["old_scientific_pins"]),
          "agent_rd_frozen_pins_preserved": len(frozen["pins"]), "agent_rd_artifacts_preserved": len(artifacts),
          "gpu_admitted": False, "model_inference": "NOT_RUN", "benchmark_assets": "NOT_ADMITTED",
          "administrative_cpu_separately_metered": False})
    print(json.dumps({"status": "RELEASED", "deadline_utc": release["deadline_utc"], "prior_artifacts": len(artifacts)}))


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"].startswith("ACTIVE")
    now = datetime.now(timezone.utc)
    if ledger.get("evaluation_clock_state") == "AWAITING_OWNER_RESUME":
        assert ledger["owner_scope_mode"] == "DATASET_INTAKE_THEN_PAUSE"
        assert sha(PUBLIC / "owner-clock-amendment-v1.json") == ledger["clock_amendment_sha256"]
        # A short admission-operation watchdog, not the seven-day research clock.
        effective_deadline = (now + timedelta(hours=1)).isoformat()
    else:
        effective_deadline = ledger.get("effective_resume_deadline_utc") or release["deadline_utc"]
    assert now < datetime.fromisoformat(effective_deadline)
    assert not any(gate.get("decision") in ("FAIL", "NO_GO", "DATA_NOT_READY", "BLOCKED_RESOURCE_ADMISSION")
                   for gate in ledger["gates"].values())
    preserve(release)
    return {**release, "deadline_utc": effective_deadline}, ledger


def reserve(name, bucket, cpu, host, command):
    release, ledger = authority()
    if ledger.get("owner_scope_mode") == "DATASET_INTAKE_THEN_PAUSE":
        assert bucket in ("admission", "return_delivery", "technical_retry")
        assert not any("infer" in str(part).lower() or "evaluate" in str(part).lower() for part in command)
    assert name not in ledger["bookings"] and cpu > 0
    assert not any(b["status"] == "RESERVED" and b["host"] == host for b in ledger["bookings"].values())
    ledger["retained_cpu_seconds"][bucket] += cpu
    assert ledger["retained_cpu_seconds"][bucket] <= ledger["stage_cpu_caps_seconds"][bucket]
    assert sum(ledger["retained_cpu_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"][name] = {"status": "RESERVED", "host": host, "bucket": bucket,
                                "cpu_cap": cpu, "gpu_cap": 0, "command": command}
    save(ledger)
    return release


def run(args):
    from cf2p_guard_v1 import LocalGuard

    command = args.command
    release = reserve(args.name, args.bucket, args.cpu, "local", command)
    folder = TASK / "jobs" / args.name
    folder.mkdir(parents=True, exist_ok=False)
    sources = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted((ROOT / "tools").glob("dc2_*.py"))}
    write(folder / "code-pins.json", sources)
    for path in sources:
        target = folder / "source_snapshot" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / path).read_bytes())
    guard = LocalGuard(folder / "resource.json", args.cpu, release["deadline_utc"], args.wall)
    try:
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src") + os.pathsep + str(ROOT))
        with (folder / "stdout.txt").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=err)
        status = "PASS" if result.returncode == 0 else "FAIL"
        guard.finish(status)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name].update(status=status, exit_code=result.returncode,
                                              resource_sha256=sha(folder / "resource.json"))
        save(ledger)
        print(json.dumps({"name": args.name, "status": status, "resource": read(folder / "resource.json")}))
        print((folder / "stdout.txt").read_text(encoding="utf-8", errors="replace")[-5000:])
        if result.returncode:
            print((folder / "stderr.txt").read_text(encoding="utf-8", errors="replace")[-3500:])
        return result.returncode
    except BaseException:
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
