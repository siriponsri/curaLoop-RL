"""Read-only counters for the known local reread process, not source contents."""
import ctypes,json
from ctypes import wintypes as w
from datetime import datetime,timezone
from r0dq_core_v1 import PRIVATE,LocalGuard,now

if __name__=='__main__':
    guard=LocalGuard('reread-stat-'+now().replace(':','').replace('.','').replace('+',''),cpu_seconds=2,wall=10,memory_mib=128)
    try:
        row=json.loads((PRIVATE/'complete-return-reread-v1-resource.json').read_text())
        result={'receipt_status':row['status'],'elapsed_seconds':(datetime.now(timezone.utc)-datetime.fromisoformat(row['start_utc'])).total_seconds()}
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
        kernel.CloseHandle.argtypes=[w.HANDLE]
        handle=kernel.OpenProcess(0x1000,False,row['pid'])
        if handle:
            kernel.GetProcessTimes.argtypes=[w.HANDLE]+[ctypes.POINTER(w.FILETIME)]*4
            times=[w.FILETIME() for _ in range(4)]
            if kernel.GetProcessTimes(handle,*[ctypes.byref(t) for t in times]):
                result['process_cpu_seconds']=sum((t.dwHighDateTime<<32)+t.dwLowDateTime for t in times[2:])/10000000
            class IO(ctypes.Structure):
                _fields_=[(name,ctypes.c_uint64) for name in ['read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes']]
            kernel.GetProcessIoCounters.argtypes=[w.HANDLE,ctypes.POINTER(IO)];io=IO()
            if kernel.GetProcessIoCounters(handle,ctypes.byref(io)):result['process_read_bytes']=io.read_bytes
            kernel.CloseHandle(handle)
        print(json.dumps(result))
    except BaseException as exc:guard.finish('FAIL',error_type=type(exc).__name__);raise
    else:guard.finish('PASS',control_only=True,source_data_opened=False)
