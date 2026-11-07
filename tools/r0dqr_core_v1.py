"""Fresh owner-approved R0-DQ-R metadata-only release and bounded accounting."""
from datetime import datetime,timezone
import hashlib,json,os,sys,threading,time
from pathlib import Path
from resource_guard_v1 import Guard as OSGuard

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/chembl-taskfirst-dqr-20261107-v1'
PUBLIC=ROOT/'docs/evidence/chembl-taskfirst-dqr-20261107-v1'
PRIOR=ROOT/'.local/chembl-taskfirst-dq-20261107-v1'
REMOTE='/home/chaw/curaloop-runs/chembl-taskfirst-dqr-20261107-v1'
HOST='100.77.149.83'
SSH_OPTIONS=['-o','BatchMode=yes','-o','StrictHostKeyChecking=yes','-o','UpdateHostKeys=no',
    '-o','ConnectTimeout=10','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=2']
RELEASE=datetime(2026,11,7,12,32,14,tzinfo=timezone.utc)
DEADLINE=datetime(2026,11,9,12,32,14,tzinfo=timezone.utc)
ARCHIVE_SHA='33c203740555f96067710cdfc1c3c55d890660e5908ec5cbf5817492c290d281'
DB_SHA='4be13df3b68e25dcd0bff44bf094033b5aebe98f415acdc8c1cdf380e0c15142'

def now():return datetime.now(timezone.utc).isoformat()
def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('wb') as stream:
        stream.write((json.dumps(obj,indent=2,allow_nan=False)+'\n').encode('utf-8'));stream.flush();os.fsync(stream.fileno())
    tmp.replace(path)
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024**2),b''):h.update(chunk)
    return h.hexdigest()
def initialize():
    assert not PRIVATE.exists() and not PRIVATE.is_symlink(),'Never reset/reuse a phase root'
    prior=json.loads((PRIOR/'ledger.json').read_text());assert prior['status']=='CLOSED'
    PRIVATE.mkdir(parents=True)
    release={'schema':'curaloop.r0dqr.release.v1','status':'OWNER_RELEASED',
        'base_commit':'a2cd28e681e2d9fcb5f4e04a7ab4a563deaae87a',
        'approved_proposal':'docs/06_execution/R0DQ_OWNER_DECISION_20261107.md# a',
        'proposal_sha256':sha(ROOT/'docs/06_execution/R0DQ_OWNER_DECISION_20261107.md'),
        'release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'cpu_cap_seconds':14400,'max_combined_cpu_workers':2,'remote_cpu_equivalent':1,'remote_memory_bytes':4*1024**3,
        'local_cpu_equivalent':1,'local_memory_max_bytes':1024**3,
        'new_bulk_http_downloads_authorized':False,'metadata_and_structure_access_authorized':True,
        'masked_methods_and_procedural_input_projection_authorized':True,
        'new_activity_numeric_value_or_presence_flag_access_authorized':False,
        'old_final_outcomes_authorized':False,'automatic_next_phase':False,
        'task_bounds':{'target_metadata_inventory':11055,'frame_targets':200,'frame_assays':4000,
            'candidate_bundles':120,'topology_rows':2000000,'canonical_molecule_ids':100000,'source_documents':12},
        'request_bounds':{'metadata':24,'methods':12,'nonbulk_bytes':128*1024**2,'bulk':0},
        'old_closed_ledger_sha256':sha(PRIOR/'ledger.json'),'old_roots_and_ledgers_reset':False}
    save(PRIVATE/'release.json',release);save(ROOT/'research/manifests/chembl_taskfirst_dqr_release_20261107_v1.json',release)
    save(PRIVATE/'ledger.json',{'id':PRIVATE.name,'status':'ACTIVE','release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'utility_reserved_seconds':1800,'worker_reserved_seconds':0,'cpu_cap_seconds':14400,
        'stage_caps_seconds':{'source_return':7200,'metadata':3600,'context':1800},
        'stage_reserved_seconds':{'source_return':0,'metadata':0,'context':0},
        'jobs':[],'http_attempts':[],'metadata_request_cap':24,'methods_request_cap':12,
        'nonbulk_bytes':0,'nonbulk_cap_bytes':128*1024**2,'bulk_http_attempts':0,'stopped_sources':[],
        'remote_root':REMOTE,'max_combined_cpu_workers':2,'new_activity_numeric_queries':0,
        'old_phase_charges_and_stops_reset':False})
def reserve(name,seconds,stage):
    book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE' and datetime.now(timezone.utc)<DEADLINE
    assert not any(r['name']==name for r in book['jobs'])
    if stage=='utility':assert sum(r['cpu_limit_seconds'] for r in book['jobs'] if r['stage']=='utility')+seconds<=1800
    else:
        assert book['stage_reserved_seconds'][stage]+seconds<=book['stage_caps_seconds'][stage]
        assert book['worker_reserved_seconds']+1800+seconds<=14400
        book['stage_reserved_seconds'][stage]+=seconds;book['worker_reserved_seconds']+=seconds
    book['jobs'].append({'name':name,'stage':stage,'cpu_limit_seconds':seconds,
        'cpu_reserved_seconds':0 if stage=='utility' else seconds,'status':'ADMITTED','utc':now()});save(PRIVATE/'ledger.json',book)
def archive_code(path):
    target=PRIVATE/'code'/(sha(path)+'.py');target.parent.mkdir(exist_ok=True)
    if not target.exists():target.write_bytes(path.read_bytes())

class LocalGuard(OSGuard):
    def __init__(self,name,cpu_seconds=30,wall=120,stage='utility',memory_mib=256):
        reserve(name,cpu_seconds,stage);self.receipt=PRIVATE/(name+'-resource.json');assert not self.receipt.exists()
        self.started,self.cpu=time.monotonic(),time.process_time();self.cpu_limit=cpu_seconds;self.ram_limit=memory_mib*1024**2
        self.wall_limit=min(wall,(DEADLINE-datetime.now(timezone.utc)).total_seconds());assert 0<memory_mib<=1024
        self.completed=threading.Event();self.lock=threading.Lock()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
        cpu=self._limit_process();entry=Path(sys.argv[0]).resolve()
        self.base={'schema':'curaloop.r0dqr.local-resource.v1','pid':os.getpid(),'start_utc':now(),
            'cpu_affinity':[cpu],'cpu_limit_seconds':cpu_seconds,'wall_limit_seconds':self.wall_limit,
            'memory_limit_bytes':self.ram_limit,'descendants_allowed':False,'deadline_utc':DEADLINE.isoformat(),
            'entry_source_sha256':sha(entry),'core_source_sha256':sha(Path(__file__)),'stage':stage}
        for path in [entry,Path(__file__),ROOT/'tools/resource_guard_v1.py']:archive_code(path)
        self._write('RUNNING');threading.Thread(target=self._watch,daemon=True).start()

if __name__=='__main__':
    initialize();print(json.dumps({'status':'OWNER_RELEASED_FRESH_R0DQR','release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat()}))
