"""Single-process scientific-job limits and immutable resource receipts."""

import ctypes
import hashlib
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


class Guard:
    def __init__(self, receipt, wall_seconds, ram_bytes, cpu_seconds=None):
        if wall_seconds <= 0 or ram_bytes <= 0:
            raise ValueError("Positive resource ceilings required.")
        deadline = datetime(2026, 11, 5, 22, 37, 4, tzinfo=timezone.utc)
        remaining = (deadline - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            raise RuntimeError("Plan A owner-authorized wall window is exhausted.")
        wall_seconds = min(wall_seconds, remaining)
        self.receipt = Path(receipt)
        if self.receipt.exists():
            raise FileExistsError("Resource receipt already exists.")
        self.receipt.parent.mkdir(parents=True, exist_ok=True)
        for key in (
            "OMP_NUM_THREADS",
            "OPENBLAS_NUM_THREADS",
            "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS",
        ):
            os.environ[key] = "1"
        self.started, self.cpu = time.monotonic(), time.process_time()
        self.wall_limit = wall_seconds
        self.cpu_limit = cpu_seconds or wall_seconds
        self.ram_limit = ram_bytes
        self.completed = threading.Event()
        self.lock = threading.Lock()
        self.cpu_id = self._limit_process()
        self.base = {
            "schema_version": "curaloop.resource-receipt.v1",
            "pid": os.getpid(),
            "start_utc": datetime.now(timezone.utc).isoformat(),
            "cpu_affinity": [self.cpu_id],
            "wall_limit_seconds": wall_seconds,
            "cpu_limit_seconds": self.cpu_limit,
            "memory_limit_bytes": ram_bytes,
            "descendant_processes_allowed": False,
            "threads_per_blas": 1,
            "python": sys.version,
            "command": sys.argv,
            "guard_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }
        self._write("RUNNING")
        threading.Thread(target=self._watch, daemon=True).start()

    def _limit_process(self):
        if os.name != "nt":
            import resource

            cpu_id = max(os.sched_getaffinity(0))
            os.sched_setaffinity(0, {cpu_id})
            resource.setrlimit(
                resource.RLIMIT_CPU, (int(self.cpu_limit) + 1, int(self.cpu_limit) + 2)
            )
            resource.setrlimit(resource.RLIMIT_AS, (self.ram_limit, self.ram_limit))
            os.nice(19)
            return cpu_id
        from ctypes import wintypes as w

        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = w.HANDLE
        process = kernel.GetCurrentProcess()
        mask, system = ctypes.c_size_t(), ctypes.c_size_t()
        kernel.GetProcessAffinityMask.argtypes = [
            w.HANDLE,
            ctypes.POINTER(ctypes.c_size_t),
            ctypes.POINTER(ctypes.c_size_t),
        ]
        kernel.SetProcessAffinityMask.argtypes = [w.HANDLE, ctypes.c_size_t]
        if not kernel.GetProcessAffinityMask(process, ctypes.byref(mask), ctypes.byref(system)):
            raise ctypes.WinError(ctypes.get_last_error())
        cpu_id = mask.value.bit_length() - 1
        if not kernel.SetProcessAffinityMask(process, 1 << cpu_id):
            raise ctypes.WinError(ctypes.get_last_error())
        kernel.SetPriorityClass.argtypes = [w.HANDLE, w.DWORD]
        if not kernel.SetPriorityClass(process, 0x40):  # IDLE_PRIORITY_CLASS
            raise ctypes.WinError(ctypes.get_last_error())

        class Basic(ctypes.Structure):
            _fields_ = [
                ("process_time", ctypes.c_int64),
                ("job_time", ctypes.c_int64),
                ("flags", w.DWORD),
                ("min_working", ctypes.c_size_t),
                ("max_working", ctypes.c_size_t),
                ("active", w.DWORD),
                ("affinity", ctypes.c_size_t),
                ("priority", w.DWORD),
                ("scheduling", w.DWORD),
            ]

        class IO(ctypes.Structure):
            _fields_ = [
                (name, ctypes.c_uint64)
                for name in (
                    "read_ops",
                    "write_ops",
                    "other_ops",
                    "read_bytes",
                    "write_bytes",
                    "other_bytes",
                )
            ]

        class Limits(ctypes.Structure):
            _fields_ = [
                ("basic", Basic),
                ("io", IO),
                ("process_memory", ctypes.c_size_t),
                ("job_memory", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t),
                ("peak_job", ctypes.c_size_t),
            ]

        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        self.job = kernel.CreateJobObjectW(None, None)
        limits = Limits()
        limits.basic.flags = 0x2 | 0x8 | 0x100  # process user CPU, active process, memory
        limits.basic.active = 1
        limits.basic.process_time = int(self.cpu_limit * 10_000_000)
        limits.process_memory = self.ram_limit
        if (
            not self.job
            or not kernel.SetInformationJobObject(
                self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits)
            )
            or not kernel.AssignProcessToJobObject(self.job, process)
        ):
            raise ctypes.WinError(ctypes.get_last_error())
        return cpu_id

    def _write(self, status, **extra):
        data = {
            **self.base,
            "status": status,
            "wall_seconds": time.monotonic() - self.started,
            "cpu_seconds": time.process_time() - self.cpu,
            **extra,
        }
        with self.lock:
            tmp = self.receipt.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
            os.replace(tmp, self.receipt)

    def _watch(self):
        while not self.completed.wait(1):
            wall, cpu = time.monotonic() - self.started, time.process_time() - self.cpu
            if wall >= self.wall_limit or cpu >= self.cpu_limit:
                self._write(
                    "FAIL_RESOURCE_LIMIT", limit="wall" if wall >= self.wall_limit else "CPU"
                )
                os._exit(124)

    def finish(self, status="PASS", **extra):
        self.completed.set()
        self._write(status, **extra)
