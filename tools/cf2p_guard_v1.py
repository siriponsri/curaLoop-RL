"""Aggregate Windows Job limits for this fresh product/design release."""

import ctypes
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path


class LocalGuard:
    def __init__(self, path, cpu_seconds, deadline_utc, wall_seconds):
        if os.name != "nt":
            raise RuntimeError("This local guard requires Windows")
        from ctypes import wintypes as w

        self.path = Path(path)
        if self.path.exists():
            raise FileExistsError(self.path)
        self.limit = cpu_seconds
        self.deadline = min(datetime.fromisoformat(deadline_utc),
                            datetime.now(timezone.utc) + timedelta(seconds=wall_seconds))
        self.done = threading.Event()
        self.lock = threading.Lock()
        self.started = time.monotonic()
        k = self.kernel = ctypes.WinDLL("kernel32", use_last_error=True)

        class Basic(ctypes.Structure):
            _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                        ("flags", w.DWORD), ("min_working", ctypes.c_size_t),
                        ("max_working", ctypes.c_size_t), ("active", w.DWORD),
                        ("affinity", ctypes.c_size_t), ("priority", w.DWORD), ("scheduling", w.DWORD)]

        class IO(ctypes.Structure):
            _fields_ = [(n, ctypes.c_uint64) for n in
                        ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

        class Limits(ctypes.Structure):
            _fields_ = [("basic", Basic), ("io", IO), ("process_memory", ctypes.c_size_t),
                        ("job_memory", ctypes.c_size_t), ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]

        class Accounting(ctypes.Structure):
            _fields_ = [(n, ctypes.c_int64) for n in ("user", "kernel", "period_user", "period_kernel")] + [
                (n, w.DWORD) for n in ("page_faults", "total_processes", "active_processes", "terminated_processes")]

        self.Accounting = Accounting
        k.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        k.CreateJobObjectW.restype = w.HANDLE
        k.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        k.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        k.GetCurrentProcess.restype = w.HANDLE
        k.GetProcessAffinityMask.argtypes = [w.HANDLE, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
        k.QueryInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD, ctypes.c_void_p]
        mask, system = ctypes.c_size_t(), ctypes.c_size_t()
        if not k.GetProcessAffinityMask(k.GetCurrentProcess(), ctypes.byref(mask), ctypes.byref(system)):
            raise ctypes.WinError(ctypes.get_last_error())
        affinity = mask.value & -mask.value
        self.cpu = affinity.bit_length() - 1
        self.job = k.CreateJobObjectW(None, None)
        limits = Limits()
        limits.basic.flags = 0x4 | 0x8 | 0x10 | 0x200 | 0x2000
        limits.basic.job_time = int(cpu_seconds * 10_000_000)
        limits.basic.active = 32
        limits.basic.affinity = affinity
        limits.job_memory = 1073741824
        if not (self.job and k.SetInformationJobObject(self.job, 9, ctypes.byref(limits), ctypes.sizeof(limits))
                and k.AssignProcessToJobObject(self.job, k.GetCurrentProcess())):
            raise ctypes.WinError(ctypes.get_last_error())
        for name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
            os.environ[name] = "1"
        self.write("RUNNING")
        threading.Thread(target=self.watch, daemon=True).start()

    def accounting(self):
        value = self.Accounting()
        if not self.kernel.QueryInformationJobObject(self.job, 1, ctypes.byref(value), ctypes.sizeof(value), None):
            raise ctypes.WinError(ctypes.get_last_error())
        return {"aggregate_cpu_seconds": (value.user + value.kernel) / 10_000_000,
                "processes": value.total_processes, "active_processes": value.active_processes}

    def write(self, status):
        with self.lock:
            value = {"status": status, "pid": os.getpid(), "heartbeat_utc": datetime.now(timezone.utc).isoformat(),
                     "mechanism": "WINDOWS_JOB_AGGREGATE_CPU_AFFINITY_MEMORY_KILL_ON_CLOSE",
                     "cpu_affinity": [self.cpu], "memory_limit_bytes": 1073741824,
                     "cpu_limit_seconds": self.limit, "deadline_utc": self.deadline.isoformat(),
                     "wall_seconds": time.monotonic() - self.started, **self.accounting()}
            temporary = self.path.with_suffix(".tmp")
            for attempt in range(20):
                try:
                    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
                    os.replace(temporary, self.path)
                    return
                except PermissionError:
                    if attempt == 19:
                        raise
                    time.sleep(.02)

    def watch(self):
        heartbeat = time.monotonic() + 30
        while not self.done.wait(.25):
            if self.accounting()["aggregate_cpu_seconds"] >= self.limit - .5 or datetime.now(timezone.utc) >= self.deadline:
                try:
                    self.write("FAIL_RESOURCE_LIMIT")
                finally:
                    os._exit(124)
            if time.monotonic() >= heartbeat:
                try:
                    self.write("RUNNING")
                except OSError:
                    pass  # A telemetry error must not stop the resource watchdog.
                heartbeat = time.monotonic() + 30

    def finish(self, status):
        self.done.set()
        self.write(status)
