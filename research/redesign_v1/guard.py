"""New-window worker guard, reusing reviewed platform resource-limit methods."""

import hashlib
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

from tools.resource_guard_v1 import Guard

DEADLINE = datetime(2026, 11, 6, 2, 43, 55, tzinfo=timezone.utc)


class GoalGuard(Guard):
    def __init__(self, receipt, wall_seconds, cpu_seconds, ram_bytes=1024**3):
        remaining = (DEADLINE - datetime.now(timezone.utc)).total_seconds()
        if min(wall_seconds, cpu_seconds, ram_bytes, remaining) <= 0:
            raise ValueError("Positive resource limits inside the new owner window required.")
        self.receipt = Path(receipt)
        if self.receipt.exists():
            raise FileExistsError("Preserve previous attempt resource evidence.")
        self.receipt.parent.mkdir(parents=True, exist_ok=True)
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS",
                     "VECLIB_MAXIMUM_THREADS"):
            os.environ[name] = "1"
        self.started, self.cpu = time.monotonic(), time.process_time()
        self.wall_limit, self.cpu_limit = min(wall_seconds, remaining), cpu_seconds
        self.ram_limit = ram_bytes
        self.completed, self.lock = threading.Event(), threading.Lock()
        self.cpu_id = self._limit_process()
        self.base = {"schema_version": "curaloop.goal4r1.resources.v1", "pid": os.getpid(),
                     "start_utc": datetime.now(timezone.utc).isoformat(), "absolute_deadline_utc": DEADLINE.isoformat(),
                     "cpu_affinity": [self.cpu_id], "wall_limit_seconds": self.wall_limit,
                     "cpu_limit_seconds": cpu_seconds, "memory_limit_bytes": ram_bytes,
                     "descendant_processes_allowed": False, "threads_per_blas": 1,
                     "python": sys.version, "command": sys.argv,
                     "guard_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        self._write("RUNNING")
        threading.Thread(target=self._watch, daemon=True).start()
