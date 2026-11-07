"""Fresh R0-DQ release/accounting; previous ledgers are read-only inputs."""
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
PRIVATE=ROOT/'.local/chembl-taskfirst-dq-20261107-v1'
PUBLIC=ROOT/'docs/evidence/chembl-taskfirst-dq-20261107-v1'
RELEASE=datetime(2026,11,7,9,41,43,tzinfo=timezone.utc)
DEADLINE=datetime(2026,11,10,9,41,43,tzinfo=timezone.utc)
REMOTE='/home/chaw/curaloop-runs/chembl-taskfirst-dq-20261107-v1'
HOST='100.77.149.83'
SSH_OPTIONS=['-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no','-o','ConnectTimeout=10',
             '-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']


def now():return datetime.now(timezone.utc).isoformat()


def save(path,payload):
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_suffix(path.suffix+'.tmp')
    with temporary.open('wb') as stream:
        stream.write((json.dumps(payload,indent=2,allow_nan=False)+'\n').encode('utf-8'))
        stream.flush();os.fsync(stream.fileno())
    os.replace(temporary,path)


def initialize():
    assert not PRIVATE.exists(),'Never reset a phase ledger'
    PRIVATE.mkdir(parents=True)
    proposal=ROOT/'research/manifests/chembl_taskfirst_plan_20261107_v1.json'
    release={'schema':'curaloop.r0dq.release.v1','status':'OWNER_RELEASED','base_commit':'9eb7480b9c62dd05fcad18a3f622b87fa01a7a69',
        'proposal_sha256':hashlib.sha256(proposal.read_bytes()).hexdigest(),
        'release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'release_bangkok':'2026-11-07 16:41:43 +07:00','deadline_bangkok':'2026-11-10 16:41:43 +07:00',
        'archive_and_restricted_support_validation_authorized':True,
        'procedural_condition_projection_authorized':True,
        'planner_numeric_outcomes_authorized':False,'old_final_outcomes_authorized':False,
        'max_cpu_seconds':57600,'max_combined_workers':2,'next_phase_requires_owner':True}
    save(PRIVATE/'release.json',release)
    save(ROOT/'research/manifests/chembl_taskfirst_dq_release_20261107_v1.json',release)
    save(PRIVATE/'ledger.json',{'id':PRIVATE.name,'status':'ACTIVE','release_utc':RELEASE.isoformat(),
        'deadline_utc':DEADLINE.isoformat(),'utility_reserved_seconds':3600,'worker_reserved_seconds':0,
        'stage_caps_seconds':{'source':10800,'frame':7200,'support':18000,'context':10800,'closeout':7200},
        'stage_reserved_seconds':{'source':0,'frame':0,'support':0,'context':0,'closeout':0},
        'jobs':[],'http_attempts':[],'http_cap':96,'nonbulk_decoded_bytes':0,'nonbulk_cap_bytes':536870912,
        'bulk_decoded_bytes':0,'bulk_cap_bytes':8589934592,'stopped_sources':[],
        'remote_root':REMOTE,'max_combined_workers':2,'old_ledgers_reset':False,
        'early_utility_notes':['Read-only local/config inspection; one malformed nested-shell redirection corrected before any connection attempt']})


def reserve(name,seconds,stage):
    book=json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status']=='ACTIVE' and datetime.now(timezone.utc)<DEADLINE
    assert not any(r['name']==name for r in book['jobs'])
    if stage!='utility':
        assert stage in book['stage_caps_seconds']
        assert book['stage_reserved_seconds'][stage]+seconds<=book['stage_caps_seconds'][stage]
        assert book['worker_reserved_seconds']+book['utility_reserved_seconds']+seconds<=57600
        book['worker_reserved_seconds']+=seconds;book['stage_reserved_seconds'][stage]+=seconds
    else:
        assert sum(r['cpu_limit_seconds'] for r in book['jobs'] if r['stage']=='utility')+seconds<=3600,'Utility sub-reservations exhausted'
    book['jobs'].append({'name':name,'stage':stage,'cpu_reserved_seconds':0 if stage=='utility' else seconds,
                         'cpu_limit_seconds':seconds,'status':'ADMITTED','utc':now()})
    save(PRIVATE/'ledger.json',book)


def archive_code(path):
    raw=path.read_bytes();target=PRIVATE/'code'/(hashlib.sha256(raw).hexdigest()+'.py')
    target.parent.mkdir(exist_ok=True)
    if not target.exists():target.write_bytes(raw)


class LocalGuard(OSGuard):
    def __init__(self,name,cpu_seconds=60,wall=120,stage='utility',memory_mib=256):
        reserve(name,cpu_seconds,stage)
        self.receipt=PRIVATE/(name+'-resource.json');assert not self.receipt.exists()
        self.started,self.cpu=time.monotonic(),time.process_time()
        self.wall_limit=min(wall,(DEADLINE-datetime.now(timezone.utc)).total_seconds())
        self.cpu_limit=cpu_seconds;self.ram_limit=memory_mib*1024**2
        assert memory_mib<=1024
        self.completed=threading.Event();self.lock=threading.Lock()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
            os.environ[key]='1'
        cpu=self._limit_process()
        entry=Path(sys.argv[0]).resolve()
        self.base={'schema':'curaloop.r0dq.local-resource.v1','pid':os.getpid(),'start_utc':now(),
            'cpu_affinity':[cpu],'cpu_limit_seconds':cpu_seconds,'wall_limit_seconds':self.wall_limit,
            'memory_limit_bytes':self.ram_limit,'descendants_allowed':False,'deadline_utc':DEADLINE.isoformat(),
            'entry_source_sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),
            'core_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'stage':stage}
        for path in [entry,Path(__file__),ROOT/'tools/resource_guard_v1.py']:archive_code(path)
        self._write('RUNNING');threading.Thread(target=self._watch,daemon=True).start()


def metadata_request(name,url,kind='release_metadata',max_bytes=2097152):
    """One exact HTTPS attempt, no redirect/retry; no record endpoints."""
    import urllib.request
    import urllib.error
    from urllib.parse import urlparse
    parsed=urlparse(url)
    assert parsed.scheme=='https' and parsed.netloc=='ftp.ebi.ac.uk'
    assert parsed.path.startswith('/pub/databases/chembl/ChEMBLdb/releases/chembl_37/')
    assert parsed.path.rsplit('/',1)[-1] in {'checksums.txt','README','LICENSE','chembl_37_schema_documentation.html','chembl_37_release_notes.txt'}
    book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE'
    assert len(book['http_attempts'])<96 and name not in book['stopped_sources']
    assert not any(r['name']==name for r in book['http_attempts'])
    record={'name':name,'url':url,'kind':kind,'status':'ADMITTED','utc':now()}
    book['http_attempts'].append(record);save(PRIVATE/'ledger.json',book)
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self,*args,**kwargs):raise RuntimeError('Unexpected redirect; source STOP')
    try:
        with urllib.request.build_opener(NoRedirect).open(url,timeout=30) as response:
            raw=response.read(max_bytes+1)
            record.update(http_status=response.status,decoded_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())
        book['nonbulk_decoded_bytes']+=len(raw)
        assert len(raw)<=max_bytes and book['nonbulk_decoded_bytes']<=536870912
        path=PRIVATE/(name+'.bin');path.write_bytes(raw)
        record.update(status='PASS',output_path=str(path.relative_to(ROOT)))
        return raw
    except Exception as exc:
        record.update(status='STOP',error_type=type(exc).__name__,error=str(exc))
        book['stopped_sources'].append(name)
        raise
    finally:save(PRIVATE/'ledger.json',book)
