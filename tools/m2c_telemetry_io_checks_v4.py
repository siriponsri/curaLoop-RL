"""Constructed real Windows reader-lock regression; no ML, labels or new jobs."""
import ctypes,json,os,sys,threading,time
from datetime import datetime,timezone,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from tools.m2c_orchestration_guard_v2 import OrchestrationGuard
TASK=ROOT/'.local/m2-costed-20261108-v2'


def main():
    assert os.name=='nt'
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.GetCurrentProcess.restype=ctypes.c_void_p
    kernel.SetProcessAffinityMask.argtypes=[ctypes.c_void_p,ctypes.c_size_t]
    assert kernel.SetProcessAffinityMask(kernel.GetCurrentProcess(),1)
    fixture=TASK/'telemetry-lock-fixtures-v4';fixture.mkdir(exist_ok=False)
    def dummy(name):
        guard=OrchestrationGuard.__new__(OrchestrationGuard);guard.path=fixture/name;guard.path.write_text('{}')
        guard.limit=60;guard.project_deadline=datetime.now(timezone.utc)+timedelta(minutes=1);guard.deadline=guard.project_deadline
        guard.started=time.monotonic();guard.done=threading.Event();guard.write_lock=threading.Lock()
        guard.accounting=lambda:{'aggregate_cpu_seconds':0,'processes':1,'active_processes':1}
        return guard
    first=dummy('short-lock.json');result=[];errors=[]
    def write():
        try:result.append(first.write('RUNNING'))
        except BaseException as exc:errors.append(str(exc))
    with first.path.open('r'):
        worker=threading.Thread(target=write);worker.start();time.sleep(.08)
    worker.join(2);assert not worker.is_alive() and result==[True] and not errors
    assert json.loads(first.path.read_text())['status']=='RUNNING'
    second=dummy('long-lock.json')
    with second.path.open('r'):
        assert second.write('RUNNING')is False
    assert second.path.with_suffix('.telemetry-errors.jsonl').exists()
    assert second.write('PASS')is True and json.loads(second.path.read_text())['status']=='PASS'
    out={'status':'PASS_CONSTRUCTED_TELEMETRY_IO_CHECKS','checks':[
      {'name':'actual-Windows-reader-lock-retries-until-release','status':'PASS'},
      {'name':'prolonged-telemetry-contention-does-not-raise-or-disable-watchdog','status':'PASS'}],
      'scope':'metadata writer only; fabricated accounting fixture is not resource enforcement or molecular evidence',
      'biological_records_read':False,'scientific_units_run':0}
    with (TASK/'telemetry-io-checks-v4.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(out,f,indent=2);f.write('\n')
    print(json.dumps(out))


if __name__=='__main__':main()
