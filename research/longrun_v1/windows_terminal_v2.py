"""Native terminal/absence proof with a successful independent PID enumeration."""

import ctypes
import os
from ctypes import wintypes as w


def observe(pid):
    if os.name != 'nt' or type(pid) is not int or pid <= 0:
        raise ValueError('Exact positive Windows PID required')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]; k.OpenProcess.restype = w.HANDLE
    k.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]; k.WaitForSingleObject.restype = w.DWORD
    k.CloseHandle.argtypes = [w.HANDLE]
    handle = k.OpenProcess(0x1000 | 0x100000, False, pid)
    if handle:
        try:
            if k.WaitForSingleObject(handle, 0) != 0:
                raise ValueError('Process is active or terminal proof is ambiguous; lease retained')
            return {'pid': pid, 'state': 'SIGNALED_ORIGINAL_OR_REUSED_PROCESS_HANDLE', 'observed_terminal': True}
        finally:
            k.CloseHandle(handle)
    if ctypes.get_last_error() != 87:
        raise ValueError('Process absence not established')
    ps = ctypes.WinDLL('psapi', use_last_error=True)
    ps.EnumProcesses.argtypes = [ctypes.POINTER(w.DWORD), w.DWORD, ctypes.POINTER(w.DWORD)]
    for size in (4096, 16384, 65536):
        array = (w.DWORD * size)(); used = w.DWORD()
        if not ps.EnumProcesses(array, ctypes.sizeof(array), ctypes.byref(used)):
            raise ctypes.WinError(ctypes.get_last_error())
        if used.value < ctypes.sizeof(array):
            if pid in set(array[:used.value // ctypes.sizeof(w.DWORD)]):
                raise ValueError('PID present in independent native enumeration; lease retained')
            return {'pid': pid, 'state': 'OPEN_ERROR87_AND_ABSENT_FROM_SUCCESSFUL_NATIVE_ENUMERATION',
                    'observed_terminal': True, 'enumerated_process_count': used.value // ctypes.sizeof(w.DWORD)}
    raise ValueError('Native enumeration capacity exhausted')
