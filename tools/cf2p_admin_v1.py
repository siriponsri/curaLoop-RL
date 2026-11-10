"""Fresh LR-CF2P release and parent-only conservative task accounting."""

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / ".local/lr-cf2p-20261110-v1"
PUBLIC = ROOT / "docs/evidence/lr-cf2p-20261110-v1"
sys.path.insert(0, str(ROOT / "tools"))


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def write(path, value, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write("\n")


def save(value):
    write(TASK / "ledger.next.json", value)
    os.replace(TASK / "ledger.next.json", TASK / "ledger.json")


def initialize():
    proposal = read(ROOT / "research/configs/lr_cf2p_proposal_20261110_v1.json")
    base = subprocess.check_output(["rtk", "proxy", "git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    assert base == "ebf5c5be06e8b2a84c50d9d2f83e6d06f6558b60"
    old = ROOT / ".local/lr-cf1-20261109-v1"
    pins = dict(read(old / "release.json")["prior_ledger_pins"])
    pins[".local/lr-cf1-20261109-v1/ledger.json"] = sha(old / "ledger.json")
    assert len(pins) == 13 and all(sha(ROOT / p) == h for p, h in pins.items())
    preservation = read(ROOT / ".local/lr-d23-20261109-v1/preservation-pins-v1.json")["pins"]
    preservation = {p: h for p, h in preservation.items() if not p.startswith(".local/")}
    preservation.update(read(ROOT / ".local/lr-d23-20261109-v1/code-pins.json"))
    preservation.update(read(old / "code-pins-science-v2.json"))
    assert all(sha(ROOT / p) == h for p, h in preservation.items())
    for row in proposal["inputs"]:
        assert sha(ROOT / row["path"]) == row["sha256"]
    TASK.mkdir(exist_ok=False)
    release_time = datetime(2026, 11, 9, 22, 54, 26, tzinfo=timezone.utc)
    release = {"schema": "curaloop.cf2p.release.v1", "status": "RELEASED", "owner_instruction": "อนุมัติ LR-CF2P ตามแผน (แนะนำ)",
               "base_commit": base, "release_utc": release_time.isoformat(),
               "deadline_utc": (release_time + timedelta(hours=10)).isoformat(),
               "proposal_sha256": sha(ROOT / proposal["proposal_path"]),
               "proposal_config_sha256": sha(ROOT / "research/configs/lr_cf2p_proposal_20261110_v1.json"),
               "cpu_cap_seconds": 28800, "max_combined_workers": 2,
               "prior_ledger_pins": pins, "frozen_scientific_pins": preservation,
               "final16_access": False, "molecular_fits": False, "private_row_access": False,
               "paid_or_gpu": False, "normal_main_commit_push_at_closeout": True}
    write(TASK / "release.json", release, True)
    write(ROOT / "research/manifests/lr_cf2p_release_20261110_v1.json", release, True)
    ledger = {"schema": "curaloop.cf2p.ledger.v1", "status": "ACTIVE", "release_utc": release["release_utc"],
              "deadline_utc": release["deadline_utc"], "stage_caps_seconds": proposal["budget"]["buckets_cpu_seconds"],
              "retained_seconds": {k: 0 for k in proposal["budget"]["buckets_cpu_seconds"]}, "bookings": {}}
    save(ledger)
    write(PUBLIC / "admission-v1.json", {"status": "PASS_RELEASE_AND_INPUT_IDENTITY", "base_commit": base,
          "prior_closed_ledgers_unchanged": len(pins), "frozen_scientific_files_unchanged": len(preservation),
          "input_hashes_verified": proposal["inputs"], "final16_access": False, "new_molecular_labels": False}, True)
    print(json.dumps({"status": "RELEASED", "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
                      "prior_ledgers": len(pins), "frozen_sources": len(preservation)}))


def authority():
    release, ledger = read(TASK / "release.json"), read(TASK / "ledger.json")
    assert ledger["status"] == "ACTIVE" and datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
    assert all(sha(ROOT / p) == h for p, h in release["prior_ledger_pins"].items())
    return release, ledger


def run(args):
    from cf2p_guard_v1 import LocalGuard

    release, ledger = authority()
    assert args.name not in ledger["bookings"]
    assert not any(b["status"] == "RESERVED" and b["host"] == "local" for b in ledger["bookings"].values())
    assert args.cpu > 0 and args.bucket in ledger["stage_caps_seconds"]
    ledger["retained_seconds"][args.bucket] += args.cpu
    assert ledger["retained_seconds"][args.bucket] <= ledger["stage_caps_seconds"][args.bucket]
    assert sum(ledger["retained_seconds"].values()) <= 28800
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    assert command
    folder = TASK / "jobs" / args.name
    folder.mkdir(parents=True, exist_ok=False)
    for index, token in enumerate(command):
        candidate = ROOT / token
        if candidate.is_file() and candidate.suffix == ".py":
            (folder / f"executed-{index}-{candidate.name}").write_bytes(candidate.read_bytes())
    ledger["bookings"][args.name] = {"status": "RESERVED", "host": "local", "bucket": args.bucket,
                                   "cpu_cap": args.cpu, "command": command, "cwd": args.cwd}
    save(ledger)
    guard = None
    try:
        guard = LocalGuard(folder / "resource.json", args.cpu, release["deadline_utc"], args.wall)
        env = dict(os.environ, PYTHONPATH=str(ROOT / "src") + os.pathsep + str(ROOT),
                   CURALOOP_STORAGE_PATH=str(folder / "disposable-api.sqlite3"))
        with (folder / "stdout.txt").open("wb") as out, (folder / "stderr.txt").open("wb") as err:
            result = subprocess.run(command, cwd=ROOT / args.cwd, env=env, stdout=out, stderr=err)
        status = "PASS" if result.returncode == 0 else "FAIL"
        guard.finish(status)
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name].update(status=status, exit_code=result.returncode,
                                            resource_sha256=sha(folder / "resource.json"))
        save(ledger)
        print(json.dumps({"job": args.name, "status": status, "exit_code": result.returncode,
                          "resource": read(folder / "resource.json")}))
        print((folder / "stdout.txt").read_text(encoding="utf-8", errors="replace")[-5500:])
        if result.returncode:
            print((folder / "stderr.txt").read_text(encoding="utf-8", errors="replace")[-3500:])
        return result.returncode
    except BaseException as exc:
        if guard:
            guard.finish("FAIL")
        ledger = read(TASK / "ledger.json")
        ledger["bookings"][args.name].update(status="FAIL", error=repr(exc))
        save(ledger)
        raise


def close_account():
    release, ledger = authority()
    assert not any(row["status"] == "RESERVED" for row in ledger["bookings"].values())
    assert read(PUBLIC / "closure-audit-v1.json")["status"] == "PASS_PRE_CLOSURE_ACCEPTANCE_AND_PRESERVATION"
    assert all(sha(ROOT / path) == digest for path, digest in release["frozen_scientific_pins"].items())
    # Include bounded remote read-only probes and a retained, guarded Git delivery envelope.
    # These are conservative reservations, not measured process CPU.
    ledger["retained_seconds"]["shared_admission"] += 10
    ledger["retained_seconds"]["joint_acceptance_delivery"] += 600
    assert all(used <= ledger["stage_caps_seconds"][key] for key, used in ledger["retained_seconds"].items())
    retained = sum(ledger["retained_seconds"].values())
    assert retained <= release["cpu_cap_seconds"]
    measured = sum(read(TASK / "jobs" / name / "resource.json").get("aggregate_cpu_seconds", 0)
                   for name in ledger["bookings"] if (TASK / "jobs" / name / "resource.json").exists())
    ledger.update(status="CLOSED", closed_utc=datetime.now(timezone.utc).isoformat(),
                  retained_delivery_upper_seconds=600, remote_readonly_probe_upper_seconds=10,
                  measured_guarded_local_cpu_seconds_before_delivery=measured)
    save(ledger)
    write(PUBLIC / "budget-closeout-v1.json", {
        "status": "CLOSED_WITH_RETAINED_DELIVERY_ENVELOPE", "closed_utc": ledger["closed_utc"],
        "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
        "retained_seconds": retained, "ceiling_seconds": release["cpu_cap_seconds"],
        "stage_retained_seconds": ledger["retained_seconds"], "stage_caps_seconds": ledger["stage_caps_seconds"],
        "open_bookings": 0, "all_failures_and_full_reservations_retained": True,
        "measured_guarded_local_cpu_seconds_before_delivery": measured,
        "measured_value_excludes_remote_probes_and_final_git_delivery": True,
        "remote_readonly_probe_upper_seconds_included": 10, "guarded_parent_delivery_upper_seconds_included": 600,
        "compute_host": "local", "local_cpu_workers": 1, "local_aggregate_memory_bytes": 1073741824,
        "remote_compute_workers": 0, "max_combined_workers_authorized": 2,
        "final16_access": False, "molecular_fits": 0, "prior_ledgers_unchanged": 13,
        "frozen_scientific_identities_unchanged": 66, "local_closed_ledger_sha256": sha(TASK / "ledger.json"),
        "bookings": ledger["bookings"], "next_phase_released": False}, True)
    print(json.dumps({"status": "CLOSED", "retained_cpu_seconds": retained, "retained_cpu_hours": retained / 3600,
                      "measured_guarded_local_cpu_seconds_before_delivery": measured}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("init")
    sub.add_parser("close")
    job = sub.add_parser("run")
    job.add_argument("name")
    job.add_argument("bucket")
    job.add_argument("cpu", type=int)
    job.add_argument("wall", type=int)
    job.add_argument("--cwd", default=".")
    job.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    if args.action == "init":
        initialize()
    elif args.action == "close":
        close_account()
    else:
        raise SystemExit(run(args))
