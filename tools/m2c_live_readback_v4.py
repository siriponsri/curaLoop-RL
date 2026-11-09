"""Read live metadata without denying atomic replacement on Windows."""
import ctypes,json,msvcrt,os
from ctypes import wintypes as w
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];TASK=ROOT/'.local/m2-costed-20261108-v2'


def pin_local_reader():
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=w.HANDLE
    kernel.SetProcessAffinityMask.argtypes=[w.HANDLE,ctypes.c_size_t]
    if not kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(),1):raise ctypes.WinError(ctypes.get_last_error())


def shared_json(path):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.CreateFileW.argtypes=[w.LPCWSTR,w.DWORD,w.DWORD,ctypes.c_void_p,w.DWORD,w.DWORD,w.HANDLE]
    kernel.CreateFileW.restype=w.HANDLE;kernel.CloseHandle.argtypes=[w.HANDLE]
    handle=kernel.CreateFileW(str(path),0x80000000,1|2|4,None,3,0x80,None)
    if handle==ctypes.c_void_p(-1).value:raise ctypes.WinError(ctypes.get_last_error())
    try:fd=msvcrt.open_osfhandle(handle,os.O_RDONLY)
    except BaseException:kernel.CloseHandle(handle);raise
    with os.fdopen(fd,'r',encoding='utf-8') as f:return json.load(f)


def alive(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];kernel.OpenProcess.restype=w.HANDLE
    kernel.GetExitCodeProcess.argtypes=[w.HANDLE,ctypes.POINTER(w.DWORD)];kernel.CloseHandle.argtypes=[w.HANDLE]
    handle=kernel.OpenProcess(0x1000,False,pid)
    if not handle:
        error=ctypes.get_last_error()
        if error==87:return False
        raise ctypes.WinError(error)
    try:
        code=w.DWORD();return bool(kernel.GetExitCodeProcess(handle,ctypes.byref(code))) and code.value==259
    finally:kernel.CloseHandle(handle)


def main():
    pin_local_reader()
    now=datetime.now(timezone.utc);phase=shared_json(TASK/'pipeline-status.json')
    version=next(v for v in(5,4,3) if (TASK/f'durable-pipeline-pid-v{v}.json').exists())
    resource=shared_json(TASK/f'durable-pipeline-resource-v{version}.json')
    launch=shared_json(TASK/f'durable-pipeline-pid-v{version}.json');lines=(TASK/f'durable-v{version}-stdout.log').read_text().splitlines()
    child_path=TASK/f'main-resume-v{version}-orchestration-resource.json'
    child=shared_json(child_path) if child_path.exists() else None
    last=json.loads(next(s for s in reversed(lines) if s.startswith('{')))
    parent_age=(now-datetime.fromisoformat(resource['heartbeat_utc'])).total_seconds()
    value={'observed_utc':now.isoformat(),'controller_pid':resource['pid'],'controller_process_alive':alive(resource['pid']),
      'phase':phase.get('step',phase['status']),'latest_progress':last,'guard_heartbeat_age_seconds':parent_age,
      'guard_heartbeat_fresh':parent_age<90,'local_wall_seconds':(now-datetime.fromisoformat(launch['started_utc'])).total_seconds(),
      'local_wall_limit_seconds':launch['wall_limit_seconds'],'final_outcomes_opened':False}
    if child:value['main_child_guard']={'status':child['status'],'pid':child.get('pid'),'process_alive':alive(child['pid']) if child.get('pid') else None,
      'heartbeat_age_seconds':(now-datetime.fromisoformat(child['heartbeat_utc'])).total_seconds() if child.get('heartbeat_utc') else None,
      'aggregate_cpu_seconds':child['aggregate_cpu_seconds'],'cpu_envelope_seconds':child['reserved_envelope_cpu_seconds']}
    if not value['guard_heartbeat_fresh'] and version==3:
        value['telemetry_note']='Parent heartbeat thread encountered Windows replace contention; do not treat stale RUNNING as fresh accounting. Verify process, advancing log and healthy child guard separately.'
    ledger=shared_json(TASK/'ledger.json')
    value['cumulative_charged_cpu_hours']=(ledger['prior_retained_seconds']+sum(ledger['bucket_reserved_seconds'].values()))/3600
    value['engineering_charged_seconds']=ledger['bucket_reserved_seconds']['engineering_guards']
    value['engineering_cap_seconds']=ledger['bucket_caps_seconds']['engineering_guards']
    print(json.dumps(value))


if __name__=='__main__':main()
