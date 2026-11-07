"""Fresh owner-released R0-A1 accounting; no network capability."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
from resource_guard_v1 import Guard as OSGuard

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/r0a1-chembl-20261107-v1'
RELEASE=datetime(2026,11,7,8,17,48,tzinfo=timezone.utc)
DEADLINE=datetime(2026,11,7,16,17,48,tzinfo=timezone.utc)


def now():return datetime.now(timezone.utc).isoformat()


def save(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('wb') as stream:
        stream.write((json.dumps(payload,indent=2,allow_nan=False)+'\n').encode('utf-8'))
        stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


def initialize():
    assert not PRIVATE.exists(), 'Fresh root required; do not reset a ledger'
    PRIVATE.mkdir(parents=True)
    save(PRIVATE/'ledger.json',{'id':PRIVATE.name,'status':'ACTIVE',
        'owner_release':'Explicit approval of option A / R0-A1 at proposal c3a95b4',
        'release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'cpu_cap_seconds':3600,'utility_reserved_seconds':600,'worker_reserved_seconds':0,
        'source_read_bytes':0,'source_read_cap_bytes':33554432,'network_requests':0,
        'jobs':[],'no_automatic_next_phase':True,'prior_r0r_charge_retained_seconds':3200})


class Guard(OSGuard):
    def __init__(self,name,cpu_seconds=60,wall=120,utility=False):
        book=json.loads((PRIVATE/'ledger.json').read_text())
        assert book['status']=='ACTIVE' and datetime.now(timezone.utc)<DEADLINE
        assert 0<cpu_seconds<=300
        self.receipt=PRIVATE/(name+'-resource.json')
        assert not self.receipt.exists()
        reserve=0 if utility else cpu_seconds
        assert book['utility_reserved_seconds']+book['worker_reserved_seconds']+reserve<=3600
        book['worker_reserved_seconds']+=reserve
        book['jobs'].append({'name':name,'reserved_cpu_seconds':reserve,'utility':utility,'status':'ADMITTED','utc':now()})
        save(PRIVATE/'ledger.json',book)
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:
            os.environ[key]='1'
        self.started,self.cpu=time.monotonic(),time.process_time()
        self.wall_limit=min(wall,(DEADLINE-datetime.now(timezone.utc)).total_seconds())
        self.cpu_limit=cpu_seconds;self.ram_limit=512*1024**2
        self.completed=threading.Event();self.lock=threading.Lock()
        cpu_id=self._limit_process()  # OS limits only; never the expired constructor.
        entry=Path(sys.argv[0]).resolve()
        self.base={'schema':'curaloop.r0a1.resource.v1','pid':os.getpid(),'start_utc':now(),
            'cpu_affinity':[cpu_id],'cpu_limit_seconds':cpu_seconds,'wall_limit_seconds':self.wall_limit,
            'memory_limit_bytes':self.ram_limit,'descendants_allowed':False,
            'deadline_utc':DEADLINE.isoformat(),'entry_source_sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),
            'core_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'executable':sys.executable,'charged_to':'600-second utility reserve' if utility else 'worker reservation'}
        for path in [entry,Path(__file__),ROOT/'tools/resource_guard_v1.py']:
            archive_code(path)
        self._write('RUNNING')
        threading.Thread(target=self._watch,daemon=True).start()


def archive_code(path):
    raw=path.read_bytes();target=PRIVATE/'code'/(hashlib.sha256(raw).hexdigest()+'.py')
    target.parent.mkdir(exist_ok=True)
    if not target.exists():target.write_bytes(raw)


def read_input(path):
    path=path.resolve()
    assert path.is_relative_to(ROOT.resolve()) and not path.is_symlink()
    size=path.stat().st_size
    assert size<=4194304
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE' and datetime.now(timezone.utc)<DEADLINE
    assert book['source_read_bytes']+size<=book['source_read_cap_bytes']
    raw=path.read_bytes()
    assert len(raw)==size
    book['source_read_bytes']+=len(raw)
    save(PRIVATE/'ledger.json',book)
    return raw


def load(path):return json.loads(read_input(path))
