"""Fresh copied-binary environment in the new owned root, one CPU only."""

import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/goal4r1-20261105-v1")


def main():
    if Path.cwd().resolve() != TASK or TASK.resolve() != TASK or TASK.stat().st_uid != os.getuid():
        raise ValueError("Wrong new task root/owner.")
    receipt = TASK / "remote-install-v1.json"
    if receipt.exists():
        raise FileExistsError("Retain all setup attempts.")
    os.umask(0o077)
    os.sched_setaffinity(0, {71})
    os.nice(19)
    resource.setrlimit(resource.RLIMIT_AS, (4 * 1024**3, 4 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (1200, 1210))
    for n in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[n] = "1"
    start, cpu = time.monotonic(), time.process_time()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    data = {"status": "RUNNING", "pid": os.getpid(), "root": str(TASK), "cpu_affinity": [71],
            "start_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
            "cpu_ceiling_seconds": 1200, "memory_ceiling_bytes": 4 * 1024**3,
            "children": "Sequential venv/pip only on same CPU; children charged",
            "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    receipt.write_text(json.dumps(data, indent=2) + "\n")
    try:
        with (TASK / "remote-install-v1.log").open("x") as log:
            subprocess.run([sys.executable, "-m", "venv", "--copies", str(TASK / ".venv")],
                           stdout=log, stderr=log, check=True, timeout=120)
            subprocess.run([str(TASK / ".venv/bin/python"), "-m", "pip", "install", "--no-cache-dir",
                            "--only-binary=:all:", "-r", "research/requirements_goal4r1_v1.txt"],
                           stdout=log, stderr=log, check=True, timeout=1200)
            with (TASK / "remote-pip-freeze-v1.txt").open("x") as freeze:
                subprocess.run([str(TASK / ".venv/bin/python"), "-m", "pip", "freeze", "--all"],
                               stdout=freeze, stderr=log, check=True, timeout=60)
        link = TASK / ".venv/lib64"
        if link.is_symlink():
            if link.resolve() != TASK / ".venv/lib":
                raise ValueError("Unexpected internal venv link.")
            link.unlink()
        data["status"] = "PASS"
    except Exception as e:
        data.update(status="FAIL", exception_type=type(e).__name__)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    data.update(wall_seconds=time.monotonic() - start, cpu_seconds=time.process_time() - cpu +
                after.ru_utime - before.ru_utime + after.ru_stime - before.ru_stime)
    receipt.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(data))
    raise SystemExit(0 if data["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
