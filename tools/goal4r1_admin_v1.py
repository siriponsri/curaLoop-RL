"""Task-local locked reservations and sanitized worker status on dr-train."""

import argparse
import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")
RUN = TASK / ".local/goal4r1-20261105-v1"
CAPS = {"D0": 3600, "D1": 7200, "D2": 10800, "D3": 7200}
ALLOWANCE = {"D0": 600, "D1": 120, "D2": 120, "D3": 900}
DEADLINE = datetime(2026, 11, 6, 2, 43, 55, tzinfo=timezone.utc)


def check_root():
    if TASK.resolve() != TASK or Path.cwd().resolve() != TASK or TASK.stat().st_uid != os.getuid():
        raise ValueError("Wrong task root/owner.")
    os.umask(0o077)
    os.sched_setaffinity(0, {68, 69, 70, 71})


def live(job):
    if job.get("pid") is None:
        return True  # Durable unresolved reservation blocks capacity conservatively.
    proc = Path("/proc") / str(job["pid"])
    try:
        return Path(os.readlink(proc / "cwd")).resolve() == TASK and b"goal4r1" in (proc / "cmdline").read_bytes()
    except OSError:
        return False


def state(jobs):
    charges = dict(ALLOWANCE)
    active, rows = 0, []
    for job in jobs:
        path = TASK / job["resource_relative"]
        r = json.loads(path.read_text()) if path.is_file() else {}
        running = live(job)
        active += int(running)
        # A dead process without a final receipt is conservatively charged its
        # whole reservation; never erase failed attempts or reuse their outputs.
        charge = r.get("cpu_seconds", job["cpu_limit"]) if not running and r.get("status") == "PASS" else job["cpu_limit"]
        charge += 2  # process startup/CPU hard-limit margin
        charges[job["stage"]] += charge
        progress = None
        progress_path = path.parent / "progress.jsonl"
        if progress_path.exists():
            with progress_path.open("rb") as f:
                f.seek(max(0, progress_path.stat().st_size - 2048))
                lines = f.read().splitlines()
            if lines:
                try:
                    progress = json.loads(lines[-1])
                except ValueError:
                    progress = None  # A concurrent partial progress write is not failure.
        rows.append({"phase": job["phase"], "attempt": job["attempt"], "shard": job["shard"],
                     "pid": job["pid"], "live": running, "status": r.get("status", "STARTING_OR_UNKNOWN"),
                     "charged_cpu_seconds": charge, "recorded_cpu_seconds": r.get("cpu_seconds"),
                     "progress": progress})
    return charges, active, rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["setup", "launch", "status"])
    p.add_argument("--phase")
    p.add_argument("--attempt", default="v1")
    p.add_argument("--shards", type=int, choices=[1, 2, 4], default=1)
    p.add_argument("--cpu-seconds", type=int, default=600)
    p.add_argument("--wall-seconds", type=int, default=3600)
    args = p.parse_args()
    check_root()
    RUN.mkdir(parents=True, exist_ok=True)
    ledger = RUN / "reservations.json"
    with (TASK / ".admin.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        jobs = json.loads(ledger.read_text())["jobs"] if ledger.exists() else []
        charges, active, rows = state(jobs)
        if args.action == "status":
            print(json.dumps({"utc": datetime.now(timezone.utc).isoformat(), "charges": charges,
                              "global_charge": sum(charges.values()), "active": active, "jobs": rows}, indent=2))
            return
        if datetime.now(timezone.utc) >= DEADLINE:
            raise RuntimeError("New owner window exhausted.")
        if args.action == "setup":
            # The single completed setup has measured parent+child CPU. Do not
            # run the historical per-process setup limiter again in this root.
            if (TASK / "remote-install-v1.json").exists():
                raise FileExistsError("Setup attempt already exists; no new setup launch.")
            phase, stage, shards, cap = "setup", "D0", 1, 1200
        else:
            phase = args.phase
            mapping = {"constructed": "D0", "diagnosis_canary": "D1", "diagnosis": "D1",
                       "campaign_canary": "D2", "campaign": "D2", "ablation": "D2", "reexecution": "D3"}
            if phase not in mapping or not args.attempt.isalnum():
                raise ValueError("Frozen phase/attempt required.")
            stage, shards, cap = mapping[phase], args.shards, args.cpu_seconds
        if active + shards > 4 or cap <= 0 or charges[stage] + shards * (cap + 2) > CAPS[stage] or sum(charges.values()) + shards * (cap + 2) > 28800:
            raise RuntimeError("Phase/global CPU reservation or worker cap exceeded.")
        cpus = [71, 70, 69, 68]
        if any(j.get("pid") is None for j in jobs):
            raise RuntimeError("Unresolved launch reservation; reconcile before new work.")
        # Reject scoped unregistered worker processes. Never enumerate other
        # projects' command text into output or send signals to their processes.
        registered = {j["pid"] for j in jobs}
        for proc in Path("/proc").iterdir():
            if not proc.name.isdigit():
                continue
            try:
                cmd = (proc / "cmdline").read_bytes()
                if (b"research.redesign_v1.worker" in cmd or b"tools/goal4r1_setup_v1.py" in cmd) and Path(os.readlink(proc / "cwd")).resolve() == TASK and int(proc.name) not in registered:
                    raise RuntimeError("Unregistered task worker; no new launch.")
            except (OSError, ValueError):
                pass
        pending = []
        for shard in range(shards):
            if any(j["phase"] == phase and j["attempt"] == args.attempt and j["shard"] == shard for j in jobs):
                raise FileExistsError("Preserve all previous attempts.")
            resource = "remote-install-v1.json" if phase == "setup" else str(Path(".local/goal4r1-20261105-v1/runs") / (phase + "-" + args.attempt) / f"shard-{shard}" / "resources.json")
            job = {"phase": phase, "stage": stage, "attempt": args.attempt, "shard": shard,
                   "cpu_limit": cap, "pid": None, "resource_relative": resource,
                   "start_utc": datetime.now(timezone.utc).isoformat()}
            jobs.append(job)
            pending.append(job)
        def persist():
            tmp = ledger.with_suffix(".tmp")
            with tmp.open("w") as handle:
                handle.write(json.dumps({"jobs": jobs, "utility_allowances_seconds": ALLOWANCE}, indent=2) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp, ledger)
        persist()  # Reserve the ENTIRE batch before starting any child.
        for shard in range(shards):
            if phase == "setup":
                resource = "remote-install-v1.json"
                log = TASK / "setup-launch-v1.log"
                command = [sys.executable, "tools/goal4r1_setup_v1.py"]
            else:
                resource = str(Path(".local/goal4r1-20261105-v1/runs") / (phase + "-" + args.attempt) / f"shard-{shard}" / "resources.json")
                log = TASK / f"launch-{phase}-{args.attempt}-{shard}.log"
                command = [str(TASK / ".venv/bin/python"), "-m", "research.redesign_v1.worker", "--phase", phase,
                           "--attempt", args.attempt, "--shard", str(shard), "--shards", str(shards),
                           "--cpu", str(cpus[shard]), "--cpu-seconds", str(cap), "--wall-seconds", str(args.wall_seconds)]
            with log.open("xb") as handle:
                proc = subprocess.Popen(command, cwd=TASK, stdin=subprocess.DEVNULL, stdout=handle, stderr=handle,
                                        start_new_session=True, close_fds=True)
            pending[shard]["pid"] = proc.pid
            persist()
        print(json.dumps({"status": "LAUNCHED", "phase": phase, "shards": shards, "cpu_limit_each": cap}))


if __name__ == "__main__":
    main()
