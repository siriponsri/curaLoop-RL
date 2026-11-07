"""Fresh local-only design-review accounting; old phase constructors stay closed."""
from datetime import datetime,timezone
import hashlib,json,os,sys,threading,time
from pathlib import Path
from resource_guard_v1 import Guard as OSGuard

ROOT=Path(__file__).resolve().parents[1]
PRIVATE=ROOT/'.local/r0-design-review-20261107-v1'
PUBLIC=ROOT/'docs/evidence/r0-design-review-20261107-v1'
RELEASE=datetime(2026,11,7,14,29,34,tzinfo=timezone.utc)
DEADLINE=datetime(2026,11,7,22,29,34,tzinfo=timezone.utc)
BASE='a53210024a43239ad46f52f7a7d0770f055de2f9'

def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,value):
    path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_suffix(path.suffix+'.tmp')
    with tmp.open('wb') as f:f.write((json.dumps(value,indent=2,allow_nan=False)+'\n').encode());f.flush();os.fsync(f.fileno())
    tmp.replace(path)
def initialize():
    assert not PRIVATE.exists() and not PRIVATE.is_symlink()
    old=ROOT/'.local/chembl-taskfirst-dqr-20261107-v1/ledger.json';assert json.loads(old.read_text())['status']=='CLOSED'
    PRIVATE.mkdir(parents=True)
    release={'schema':'curaloop.r0-design-review.release.v1','base_commit':BASE,
        'selected_proposal':'docs/06_execution/R0DQR_OWNER_DECISION_20261107.md, option A',
        'proposal_sha256':sha(ROOT/'docs/06_execution/R0DQR_OWNER_DECISION_20261107.md'),
        'release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),'cpu_cap_seconds':3600,
        'local_cpu_workers':1,'memory_max_bytes':1024**3,'old_dqr_ledger_sha256':sha(old),
        'existing_returned_artifacts_only':True,'new_source_http':False,'ssh':False,
        'new_activity_records_values_or_presence_flags':False,'old_final_outcomes':False,
        'model_fitting':False,'new_qualification_or_split':False,'automatic_next_phase':False,
        'normal_english_main_delivery':'Previously authorized; Git delivery is not scientific-source intake'}
    save(PRIVATE/'release.json',release);save(ROOT/'research/manifests/r0_design_review_release_20261107_v1.json',release)
    save(PRIVATE/'ledger.json',{'status':'ACTIVE','release_utc':RELEASE.isoformat(),'deadline_utc':DEADLINE.isoformat(),
        'cpu_cap_seconds':3600,'utility_reserved_seconds':900,'worker_reserved_seconds':0,
        'stage_caps_seconds':{'review':1800,'validation':900},'stage_reserved_seconds':{'review':0,'validation':0},
        'jobs':[],'source_http_requests':0,'ssh_connections':0,'new_records_or_source_queries':0,
        'all_old_clocks_ledgers_and_stops_unchanged':True})
def reserve(name,cpu,stage):
    book=json.loads((PRIVATE/'ledger.json').read_text());assert book['status']=='ACTIVE' and datetime.now(timezone.utc)<DEADLINE
    assert not any(j['name']==name for j in book['jobs'])
    if stage=='utility':assert sum(j['cpu_limit_seconds'] for j in book['jobs'] if j['stage']=='utility')+cpu<=900
    else:
        assert book['stage_reserved_seconds'][stage]+cpu<=book['stage_caps_seconds'][stage]
        assert book['worker_reserved_seconds']+900+cpu<=3600
        book['stage_reserved_seconds'][stage]+=cpu;book['worker_reserved_seconds']+=cpu
    book['jobs'].append({'name':name,'stage':stage,'cpu_limit_seconds':cpu,'status':'ADMITTED','utc':now()});save(PRIVATE/'ledger.json',book)
def archive_code(path):
    target=PRIVATE/'code'/(sha(path)+'.py');target.parent.mkdir(exist_ok=True)
    if not target.exists():target.write_bytes(path.read_bytes())
class Guard(OSGuard):
    def __init__(self,name,cpu=60,stage='review',wall=180,memory_mib=256):
        reserve(name,cpu,stage);self.receipt=PRIVATE/(name+'-resource.json');assert not self.receipt.exists()
        self.started,self.cpu=time.monotonic(),time.process_time();self.cpu_limit=cpu;self.ram_limit=memory_mib*1024**2
        self.wall_limit=min(wall,(DEADLINE-datetime.now(timezone.utc)).total_seconds());assert 0<self.wall_limit and memory_mib<=1024
        self.completed=threading.Event();self.lock=threading.Lock()
        for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
        core=self._limit_process();entry=Path(sys.argv[0]).resolve()
        self.base={'schema':'curaloop.r0-design-review.resource.v1','pid':os.getpid(),'start_utc':now(),
            'cpu_affinity':[core],'cpu_limit_seconds':cpu,'wall_limit_seconds':self.wall_limit,'memory_limit_bytes':self.ram_limit,
            'descendants_allowed':False,'deadline_utc':DEADLINE.isoformat(),'stage':stage,
            'entry_source_sha256':sha(entry),'guard_source_sha256':sha(Path(__file__))}
        for path in [entry,Path(__file__),ROOT/'tools/resource_guard_v1.py']:archive_code(path)
        self._write('RUNNING');threading.Thread(target=self._watch,daemon=True).start()
if __name__=='__main__':initialize();print(json.dumps({'status':'OWNER_RELEASED_LOCAL_DESIGN_REVIEW','deadline_utc':DEADLINE.isoformat()}))
