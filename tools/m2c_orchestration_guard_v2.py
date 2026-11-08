"""Aggregate Windows limits for trusted local orchestration and its CLI children."""
import ctypes
import json
import os
import threading
import time
from datetime import datetime,timezone,timedelta
from pathlib import Path


class OrchestrationGuard:
    def __init__(self,receipt,cpu_seconds,deadline_utc,wall_seconds=None):
        assert os.name=='nt'
        from ctypes import wintypes as w
        self.path=Path(receipt);assert not self.path.exists()
        self.limit=cpu_seconds;self.project_deadline=datetime.fromisoformat(deadline_utc.replace('Z','+00:00'))
        self.deadline=min(self.project_deadline,datetime.now(timezone.utc)+timedelta(seconds=wall_seconds)) if wall_seconds else self.project_deadline
        self.done=threading.Event();self.started=time.monotonic();self.write_lock=threading.Lock()
        k=ctypes.WinDLL('kernel32',use_last_error=True);self.kernel=k
        class Basic(ctypes.Structure):
            _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),('flags',w.DWORD),
                      ('min_working',ctypes.c_size_t),('max_working',ctypes.c_size_t),('active',w.DWORD),
                      ('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
        class IO(ctypes.Structure):
            _fields_=[(n,ctypes.c_uint64) for n in('read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes')]
        class Limits(ctypes.Structure):
            _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),
                      ('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
        class Accounting(ctypes.Structure):
            _fields_=[(n,ctypes.c_int64) for n in('user','kernel','period_user','period_kernel')]+[
                      (n,w.DWORD) for n in('page_faults','total_processes','active_processes','terminated_processes')]
        self.Accounting=Accounting
        k.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];k.CreateJobObjectW.restype=w.HANDLE
        k.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
        k.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
        k.GetCurrentProcess.restype=w.HANDLE
        k.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p]
        self.job=k.CreateJobObjectW(None,None);limits=Limits()
        limits.basic.flags=0x4|0x8|0x10|0x200|0x2000
        limits.basic.job_time=int(cpu_seconds*10_000_000);limits.basic.active=32;limits.basic.affinity=1
        limits.job_memory=536870912
        if not(self.job and k.SetInformationJobObject(self.job,9,ctypes.byref(limits),ctypes.sizeof(limits))
               and k.AssignProcessToJobObject(self.job,k.GetCurrentProcess())):raise ctypes.WinError(ctypes.get_last_error())
        self.write('RUNNING');threading.Thread(target=self.watch,daemon=True).start()

    def accounting(self):
        a=self.Accounting()
        assert self.kernel.QueryInformationJobObject(self.job,1,ctypes.byref(a),ctypes.sizeof(a),None)
        return {'aggregate_cpu_seconds':(a.user+a.kernel)/10_000_000,'processes':a.total_processes,'active_processes':a.active_processes}

    def write(self,status):
        with self.write_lock:
            if status=='RUNNING' and self.done.is_set():return
            value={'status':status,'mechanism':'WINDOWS_JOB_CPU0_AGGREGATE_512MIB_WITH_CLI_CHILDREN',
                   'pid':os.getpid(),'heartbeat_utc':datetime.now(timezone.utc).isoformat(),
                   'reserved_envelope_cpu_seconds':self.limit,'deadline_utc':self.deadline.isoformat(),
                   'project_deadline_utc':self.project_deadline.isoformat(),
                   'wall_seconds':time.monotonic()-self.started,**self.accounting()}
            tmp=self.path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8');os.replace(tmp,self.path)

    def watch(self):
        next_heartbeat=time.monotonic()+30
        while not self.done.wait(.25):
            if self.accounting()['aggregate_cpu_seconds']>=self.limit-.5 or datetime.now(timezone.utc)>=self.deadline:
                try:self.write('FAIL_ORCHESTRATION_RESOURCE_LIMIT')
                finally:os._exit(124)
            if time.monotonic()>=next_heartbeat:
                self.write('RUNNING');next_heartbeat=time.monotonic()+30

    def finish(self,status='PASS'):
        self.done.set();self.write(status)
