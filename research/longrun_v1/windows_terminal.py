"""Read-only Windows terminal check; access-denied and active PIDs fail closed."""

import ctypes
import os
from ctypes import wintypes as w


def observe(pid):
    if os.name != 'nt' or type(pid) is not int or pid <= 0:
        raise ValueError('Exact positive Windows PID required')
    k = ctypes.WinDLL('kernel32', use_last_error=True)
    k.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]; k.OpenProcess.restype = w.HANDLE
    k.GetExitCodeProcess.argtypes = [w.HANDLE, ctypes.POINTER(w.DWORD)]
    k.CloseHandle.argtypes = [w.HANDLE]
    handle = k.OpenProcess(0x1000 | 0x100000, False, pid)
    if not handle:
        error = ctypes.get_last_error()
        if error != 87:
            raise OSError(error, 'Process absence cannot be certified')
        return {'pid': pid, 'state': 'ABSENT_ERROR_INVALID_PARAMETER', 'observed_terminal': True}
    try:
        exit_code = w.DWORD()
        if not k.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            raise ctypes.WinError(ctypes.get_last_error())
        if exit_code.value == 259:
            raise ValueError('PID is active or reused by an active process; lease retained')
        return {'pid': pid, 'state': 'EXITED_NATIVE_PROCESS_HANDLE', 'exit_code': exit_code.value, 'observed_terminal': True}
    finally:
        k.CloseHandle(handle)
