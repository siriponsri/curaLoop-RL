"""Fresh AgentRD accounting; never reopen a historical resource account."""

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/agent-rd-run-20261110-v1"
PUBLIC = ROOT / "docs/evidence/agent-rd-20261110-v1"
REMOTE = "/home/chaw/curaloop-tasks/agent-rd-20261110-v1"
CONTAINER = "curaloop-agent-rd-20261110-v1"


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def save(value):
    write(TASK / "ledger.next.json", value)
    os.replace(TASK / "ledger.next.json", TASK / "ledger.json")


def init():
    base = subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert base == "3fa17f09fc90b89dc4cc98668d86afb17d81552d"
    old = ROOT / ".local/lr-cf2p-20261110-v1"
    previous = read(old / "release.json")
    ledgers = {**previous["prior_ledger_pins"], ".local/lr-cf2p-20261110-v1/ledger.json": sha(old / "ledger.json")}
    assert len(ledgers) == 14 and all(sha(ROOT / p) == h for p, h in ledgers.items())
    old_statuses = {p: read(ROOT / p)["status"] for p in ledgers}
    assert all(s.startswith("CLOSED") or (p == ".local/r0r-chembl-20261107-v1/ledger.json" and s == "AWAITING_OWNER_INPUT")
               for p, s in old_statuses.items())
    frozen = previous["frozen_scientific_pins"]
    assert len(frozen) == 66 and all(sha(ROOT / p) == h for p, h in frozen.items())
    TASK.mkdir(exist_ok=False)
    # Conservative minute-floor of the first clock observed after resource approval.
    start = datetime(2026, 11, 10, 11, 10, tzinfo=timezone.utc)
    release = {"schema": "curaloop.agent-rd.release.v1", "base_commit": base,
               "owner_scope": "Continuous A0/A1/necessary A2/evaluation/analysis/manuscript; option A approved",
               "release_utc": start.isoformat(), "deadline_utc": (start + timedelta(hours=120)).isoformat(),
               "cpu_cap_seconds": 345600, "combined_cpu_cores": 4, "local_cpu_cores": 1,
               "remote_cpu_equivalent": 3, "remote_memory_bytes": 12884901888, "remote_swap_bytes": 0,
               "remote_root": REMOTE, "owned_container": CONTAINER,
               "model": "hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M",
               "model_digest": "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b",
               "proposal_sha256": sha(ROOT / "docs/08_agent_rd/RESOURCE_AND_MODEL_DECISION_20261110.md"),
               "planning_pack": read(ROOT / ".local/agent-rd-intake-20261110-v1/pack-manifest.json"),
               "prior_ledger_pins": ledgers, "prior_ledger_recorded_statuses": old_statuses,
               "prior_accounts_inactive_no_resume": True, "frozen_scientific_pins": frozen,
               "new_model_download": False, "gpu": False, "paid_api": False,
               "final16_access": False, "private_cf1_row_access": False, "hidden_outcomes_access": False,
               "external_writes_deployment_submission": False, "main_delivery_authorized": True}
    write(TASK / "release.json", release, True)
    write(ROOT / "research/manifests/agent_rd_release_20261110_v1.json", release, True)
    caps = {"admission": 7200, "implementation": 43200, "development": 36000,
            "evaluation": 201600, "analysis_manuscript": 28800, "return_delivery": 14400, "technical_retry": 14400}
    save({"schema": "curaloop.agent-rd.ledger.v1", "status": "ACTIVE", "stage_caps_seconds": caps,
          "retained_seconds": {k: 60 if k == "admission" else 0 for k in caps},
          "bookings": {"bootstrap-ledger-validation-v1": {"status": "FAIL_DESCRIPTOR_MISMATCH", "host": "local", "bucket": "admission", "cpu_cap": 60,
          "error": "Pre-account assertion assumed literal CLOSED; retained exact historical inactive statuses without changing old ledgers",
          "source_copy": ".local/agent-rd-intake-20261110-v1/admin-bootstrap-first-attempt.py", "measured_cpu_seconds": None}}, "release_utc": release["release_utc"],
          "deadline_utc": release["deadline_utc"]})
    write(PUBLIC / "release-admission-v1.json", {"status": "PASS_FRESH_OWNER_RELEASE", "historical_ledger_identities_preserved": 14,
          "prior_raw_statuses_closed_prefix": 13, "prior_inactive_raw_status_awaiting_owner_input": 1,
          "old_frozen_scientific_pins_preserved": 66, "new_model_inference": "NOT_RUN", "release_utc": release["release_utc"],
          "deadline_utc": release["deadline_utc"]}, True)
    print(json.dumps({"status": "RELEASED", "deadline_utc": release["deadline_utc"]}))


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE" and datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert all(sha(ROOT / p) == h for p, h in release["prior_ledger_pins"].items())
    return release, ledger


def reserve(name, bucket, cpu, host, command):
    release, ledger = authority()
    assert name not in ledger["bookings"] and cpu > 0
    assert not any(r["status"] == "RESERVED" and r["host"] == host for r in ledger["bookings"].values())
    assert bucket in ledger["retained_seconds"]
    ledger["retained_seconds"][bucket] += cpu
    assert ledger["retained_seconds"][bucket] <= ledger["stage_caps_seconds"][bucket]
    assert sum(ledger["retained_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"][name] = {"status": "RESERVED", "host": host, "bucket": bucket, "cpu_cap": cpu, "command": command}
    save(ledger)
    return release


def run(args):
    from cf2p_guard_v1 import LocalGuard

    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    release = reserve(args.name, args.bucket, args.cpu, "local", command)
    folder = TASK / "jobs" / args.name
    folder.mkdir(parents=True, exist_ok=False)
    for n, token in enumerate(command):
        p = ROOT / token
        if p.is_file() and p.suffix == ".py":
            (folder / f"executed-{n}-{p.name}").write_bytes(p.read_bytes())
    sources = [*sorted((ROOT / "src/curaloop_rd/agent_rd").glob("*.py")),
               *sorted((ROOT / "research/agent_rd_eval_v1").glob("*.py")),
               ROOT / "api/agent_rd_routes.py", ROOT / "api/main.py",
               *sorted((ROOT / "tools").glob("agent_rd_*.py"))]
    pins = {}
    for source in sources:
        if source.is_file():
            relative = source.relative_to(ROOT)
            target = folder / "source_snapshot" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
            pins[relative.as_posix()] = sha(source)
    write(folder / "code-pins.json", pins)
    guard = LocalGuard(folder / "resource.json", args.cpu, release["deadline_utc"], args.wall)
    try:
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src") + os.pathsep + str(ROOT), CURALOOP_STORAGE_PATH=str(folder / "disposable-api.sqlite3"))
        with (folder / "stdout.txt").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=out, stderr=err)
        status = "PASS" if result.returncode == 0 else "FAIL"
        guard.finish(status)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name].update(status=status, exit_code=result.returncode, resource_sha256=sha(folder / "resource.json"))
        save(ledger)
        print(json.dumps({"name": args.name, "status": status, "resource": read(folder / "resource.json")}))
        print((folder / "stdout.txt").read_text(encoding="utf-8", errors="replace")[-4500:])
        if result.returncode:
            print((folder / "stderr.txt").read_text(encoding="utf-8", errors="replace")[-3000:])
        return result.returncode
    except BaseException:
        guard.finish("FAIL")
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name]["status"] = "FAIL"
        save(ledger)
        raise


def remote_envelope():
    release, ledger = authority()
    assert "remote-model-envelope-v1" not in ledger["bookings"]
    allocations = {"admission": 6600, "development": 36000, "evaluation": 201600}
    for bucket, cpu in allocations.items():
        ledger["retained_seconds"][bucket] += cpu
        assert ledger["retained_seconds"][bucket] <= ledger["stage_caps_seconds"][bucket]
    assert sum(ledger["retained_seconds"].values()) <= release["cpu_cap_seconds"]
    ledger["bookings"]["remote-model-envelope-v1"] = {"status": "RESERVED_PHASE_ENVELOPE", "host": "remote",
        "allocations": allocations, "cpu_cap": sum(allocations.values()), "remote_client_cpu_cap": 600,
        "admission_container_cpu_cap": 6000, "single_model_worker": True,
        "failed_and_unused_reservations_retained": True, "phase_transition_resets_clock": False}
    save(ledger)
    print("PASS retained one remote model envelope with separate admission/development/evaluation caps")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init")
    sub.add_parser("remote-envelope")
    job = sub.add_parser("run")
    for name in ("name", "bucket"):
        job.add_argument(name)
    for name in ("cpu", "wall"):
        job.add_argument(name, type=int)
    job.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == "init":
        init()
    elif args.action == "remote-envelope":
        remote_envelope()
    else:
        raise SystemExit(run(args))
