"""One-core/aggregate-memory Windows utility tree for SSH transport."""
import ctypes
import os
import time
from r0dq_core_v1 import LocalGuard


class TransportGuard(LocalGuard):
    def _limit_process(self):
        assert os.name=='nt'
        from ctypes import wintypes as w
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.GetCurrentProcess.restype=w.HANDLE
        process=kernel.GetCurrentProcess()
        mask,system=ctypes.c_size_t(),ctypes.c_size_t()
        kernel.GetProcessAffinityMask.argtypes=[w.HANDLE,ctypes.POINTER(ctypes.c_size_t),ctypes.POINTER(ctypes.c_size_t)]
        kernel.SetProcessAffinityMask.argtypes=[w.HANDLE,ctypes.c_size_t]
        assert kernel.GetProcessAffinityMask(process,ctypes.byref(mask),ctypes.byref(system))
        cpu=mask.value.bit_length()-1
        assert kernel.SetProcessAffinityMask(process,1<<cpu)
        kernel.SetPriorityClass.argtypes=[w.HANDLE,w.DWORD]
        assert kernel.SetPriorityClass(process,0x40)
        class Basic(ctypes.Structure):
            _fields_=[('process_time',ctypes.c_int64),('job_time',ctypes.c_int64),('flags',w.DWORD),
                ('min_working',ctypes.c_size_t),('max_working',ctypes.c_size_t),('active',w.DWORD),
                ('affinity',ctypes.c_size_t),('priority',w.DWORD),('scheduling',w.DWORD)]
        class IO(ctypes.Structure):
            _fields_=[(n,ctypes.c_uint64) for n in ['read_ops','write_ops','other_ops','read_bytes','write_bytes','other_bytes']]
        class Limits(ctypes.Structure):
            _fields_=[('basic',Basic),('io',IO),('process_memory',ctypes.c_size_t),('job_memory',ctypes.c_size_t),('peak_process',ctypes.c_size_t),('peak_job',ctypes.c_size_t)]
        kernel.CreateJobObjectW.argtypes=[ctypes.c_void_p,w.LPCWSTR];kernel.CreateJobObjectW.restype=w.HANDLE
        kernel.SetInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD]
        kernel.AssignProcessToJobObject.argtypes=[w.HANDLE,w.HANDLE]
        self.job=kernel.CreateJobObjectW(None,None)
        limits=Limits();limits.basic.flags=0x4|0x8|0x200|0x2000
        limits.basic.job_time=int(self.cpu_limit*10000000)
        limits.basic.active=4;limits.job_memory=self.ram_limit
        assert self.job and kernel.SetInformationJobObject(self.job,9,ctypes.byref(limits),ctypes.sizeof(limits))
        assert kernel.AssignProcessToJobObject(self.job,process)
        return cpu

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.base.update(descendants_allowed=True,max_processes=4,
                         aggregate_tree_memory_enforced=True,aggregate_tree_cpu_time_enforced=True,
                         children_inherit_single_cpu_affinity=True)
        self._write('RUNNING')

    def _job_cpu(self):
        from ctypes import wintypes as w
        class Accounting(ctypes.Structure):
            _fields_=[('user',ctypes.c_int64),('kernel',ctypes.c_int64),
                ('period_user',ctypes.c_int64),('period_kernel',ctypes.c_int64),
                ('faults',w.DWORD),('total_processes',w.DWORD),('active_processes',w.DWORD),('terminated_processes',w.DWORD)]
        kernel=ctypes.WinDLL('kernel32',use_last_error=True)
        kernel.QueryInformationJobObject.argtypes=[w.HANDLE,ctypes.c_int,ctypes.c_void_p,w.DWORD,ctypes.c_void_p]
        data=Accounting()
        assert kernel.QueryInformationJobObject(self.job,1,ctypes.byref(data),ctypes.sizeof(data),None)
        return (data.user+data.kernel)/10000000

    def _write(self,status,**extra):
        if hasattr(self,'job'):extra['aggregate_tree_cpu_seconds']=self._job_cpu()
        super()._write(status,**extra)

    def _watch(self):
        while not self.completed.wait(.25):
            wall=time.monotonic()-self.started;cpu=self._job_cpu()
            if wall>=self.wall_limit or cpu>=max(.25,self.cpu_limit-.5):
                self._write('FAIL_RESOURCE_LIMIT',limit='wall' if wall>=self.wall_limit else 'aggregate_tree_CPU')
                os._exit(124)
