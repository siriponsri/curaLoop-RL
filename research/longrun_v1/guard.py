"""Explicit leased-CPU guard. Trusted single-process workers, not a code sandbox."""

import ctypes
import hashlib
import json
import os
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path


def deny_linux_children():
    if os.uname().machine != 'x86_64':
        raise RuntimeError('Reviewed child policy supports the inspected x86_64 host only')
    lib = ctypes.CDLL('libseccomp.so.2', use_errno=True)
    lib.seccomp_init.argtypes = [ctypes.c_uint32]
    lib.seccomp_init.restype = ctypes.c_void_p
    lib.seccomp_attr_set.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_uint32]
    lib.seccomp_syscall_resolve_name.argtypes = [ctypes.c_char_p]
    lib.seccomp_syscall_resolve_name.restype = ctypes.c_int
    class Comparison(ctypes.Structure):
        _fields_ = [('arg', ctypes.c_uint), ('op', ctypes.c_int),
                    ('datum_a', ctypes.c_uint64), ('datum_b', ctypes.c_uint64)]
    lib.seccomp_rule_add_array.argtypes = [ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int,
                                         ctypes.c_uint, ctypes.POINTER(Comparison)]
    lib.seccomp_load.argtypes = [ctypes.c_void_p]
    lib.seccomp_release.argtypes = [ctypes.c_void_p]
    ctx = lib.seccomp_init(0x7fff0000)  # SCMP_ACT_ALLOW.
    if not ctx:
        raise RuntimeError('Cannot create mandatory single-process policy')
    try:
        if lib.seccomp_attr_set(ctx, 3, 1) != 0 or lib.seccomp_attr_set(ctx, 4, 1) != 0:
            raise RuntimeError('Cannot enforce no-new-privileges and thread synchronization')
        for name in ('fork', 'vfork', 'execve', 'execveat', 'clone3'):
            syscall = lib.seccomp_syscall_resolve_name(name.encode())
            # ENOSYS for clone3 permits glibc's legacy clone fallback for threads.
            errno = 38 if name == 'clone3' else 1
            if syscall < 0 or lib.seccomp_rule_add_array(ctx, 0x00050000 | errno, syscall, 0, None) != 0:
                raise RuntimeError('Cannot install mandatory process-creation restriction')
        comparison = Comparison(0, 7, 0x10000, 0)  # clone without CLONE_THREAD.
        syscall = lib.seccomp_syscall_resolve_name(b'clone')
        if syscall < 0 or lib.seccomp_rule_add_array(ctx, 0x00050001, syscall, 1, ctypes.byref(comparison)) != 0:
            raise RuntimeError('Cannot restrict non-thread clone')
        if lib.seccomp_load(ctx) != 0:
            raise RuntimeError('Cannot activate mandatory single-process policy')
    finally:
        lib.seccomp_release(ctx)
    return 'SECCOMP_DENY_PROCESS_CREATION_ALLOW_THREADS'


class ResourceGuard:
    def __init__(self, receipt, permit):
        if sys.flags.optimize != 0:
            raise RuntimeError('Qualification assertions must remain enabled')
        self.receipt, self.permit = Path(receipt), permit
        if self.receipt.exists():
            raise FileExistsError('Preserve original resource receipt')
        self.receipt.parent.mkdir(parents=True, exist_ok=True)
        self.cpu_id = permit['cpu']
        self.cpu_limit = permit['guard_cpu_seconds']
        self.ram_limit = permit['memory_bytes']
        self.deadline = datetime.fromisoformat(permit['deadline_utc'].replace('Z', '+00:00'))
        self.wall_limit = min(permit['wall_seconds'], (self.deadline - datetime.now(timezone.utc)).total_seconds())
        if type(self.cpu_id) is not int or self.cpu_id < 0 or min(self.wall_limit, self.cpu_limit, self.ram_limit) <= 0:
            raise ValueError('Positive limits and exact leased CPU required')
        self.started = time.monotonic()
        self.completed, self.lock = threading.Event(), threading.Lock()
        for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
            os.environ[name] = '1'
        self._limit_process()
        self.child_policy = deny_linux_children() if os.name != 'nt' else 'WINDOWS_JOB_ACTIVE_PROCESS_LIMIT_ONE_NO_BREAKAWAY'
        self.base = {'schema': 'curaloop.lrbc.resources.v1', 'attempt': permit['attempt'], 'token': permit['token'],
                     'host': permit['host'], 'bundle_sha256': permit['bundle_sha256'], 'pid': os.getpid(),
                     'start_utc': datetime.now(timezone.utc).isoformat(), 'deadline_utc': permit['deadline_utc'],
                     'cpu_affinity': [self.cpu_id], 'guard_cpu_seconds': self.cpu_limit,
                     'memory_limit_bytes': self.ram_limit, 'child_policy': self.child_policy,
                     'whole_process_cpu_includes_startup': True, 'python_optimization': sys.flags.optimize,
                     'guard_source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        self._write('RUNNING')
        threading.Thread(target=self._watch, daemon=True).start()

    def _limit_process(self):
        if os.name != "nt":
            import resource

            cpu_id = self.cpu_id
            if cpu_id not in os.sched_getaffinity(0):
                raise ValueError('Leased CPU is unavailable')
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
        cpu_id = self.cpu_id
        if not mask.value & (1 << cpu_id):
            raise ValueError('Leased CPU is unavailable')
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

    def _write(self, status):
        value = dict(self.base, status=status, cpu_seconds=time.process_time(),
                     wall_seconds=time.monotonic() - self.started,
                     actual_cpu_affinity=sorted(os.sched_getaffinity(0)) if os.name != 'nt' else self._windows_affinity())
        with self.lock:
            temp = self.receipt.with_suffix('.tmp')
            with temp.open('w', encoding='utf-8', newline='\n') as handle:
                json.dump(value, handle, indent=2, allow_nan=False)
                handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
            os.replace(temp, self.receipt)

    def _windows_affinity(self):
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.GetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t)]
        mask, system = ctypes.c_size_t(), ctypes.c_size_t()
        if not kernel.GetProcessAffinityMask(kernel.GetCurrentProcess(), ctypes.byref(mask), ctypes.byref(system)):
            raise ctypes.WinError(ctypes.get_last_error())
        return [i for i in range(mask.value.bit_length()) if mask.value & (1 << i)]

    def _watch(self):
        while not self.completed.wait(.25):
            if (time.process_time() >= self.cpu_limit or time.monotonic() - self.started >= self.wall_limit
                    or datetime.now(timezone.utc) >= self.deadline):
                try:
                    self._write('FAIL_RESOURCE_LIMIT')
                finally:
                    # A full disk must never disable absolute deadline enforcement.
                    os._exit(124)

    def finish(self, status):
        self.completed.set()
        self._write(status)
