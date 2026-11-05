"""Run only inside the verified owned remote task, with isolated dependencies."""

import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

TASK = Path("/home/chaw/curaloop-rl/plan-a-20261105-v2")


def main():
    if Path.cwd().resolve() != TASK or TASK.resolve() != TASK or TASK.stat().st_uid != os.getuid():
        raise ValueError("Wrong task root/owner.")
    receipt = TASK / "remote-install-v1.json"
    if receipt.exists():
        raise FileExistsError("Preserve setup attempts.")
    os.umask(0o077)
    os.sched_setaffinity(0, {71})
    os.nice(19)
    resource.setrlimit(resource.RLIMIT_AS, (4*1024**3, 4*1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (1200, 1210))
    for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[name] = "1"
    started, cpu = time.monotonic(), time.process_time()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    info = {"status": "RUNNING", "pid": os.getpid(), "root": str(TASK),
            "start_utc": datetime.now(timezone.utc).isoformat(), "affinity": [71],
            "python": sys.version, "memory_limit_bytes": 4*1024**3,
            "wall_ceiling_seconds": 1500, "subprocesses": "Sequential venv/pip only, same single CPU",
            "helper_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    receipt.write_text(json.dumps(info, indent=2) + "\n")
    try:
        with (TASK / "remote-install-v1.txt").open("x") as log:
            subprocess.run([sys.executable, "-m", "venv", "--copies", str(TASK / ".venv")], stdout=log, stderr=log, check=True, timeout=120)
            subprocess.run([str(TASK / ".venv/bin/python"), "-m", "pip", "install", "--no-cache-dir", "--only-binary=:all:", "-r", "research/requirements_plan_a_constructed_v1.txt"], stdout=log, stderr=log, check=True, timeout=1200)
            subprocess.run([str(TASK / ".venv/bin/python"), "-m", "pip", "freeze", "--all"], stdout=(TASK / "remote-pip-freeze-v1.txt").open("x"), stderr=log, check=True, timeout=60)
        # venv creates this convenience symlink even with --copies. Remove only
        # the exact owned internal symlink so complete return can reject links.
        link = TASK / ".venv/lib64"
        if link.is_symlink():
            if link.resolve() != TASK / ".venv/lib":
                raise ValueError("Unexpected venv link target.")
            link.unlink()
        info["status"] = "PASS"
    except Exception as error:
        info.update(status="FAIL", exception_type=type(error).__name__)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    info.update(wall_seconds=time.monotonic()-started,
                cpu_seconds=time.process_time()-cpu+(after.ru_utime-before.ru_utime)+(after.ru_stime-before.ru_stime))
    receipt.write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps(info))
    raise SystemExit(0 if info["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
