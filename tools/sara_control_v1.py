"""Fresh route-A authority, finite attempts and resource reservations."""
from __future__ import annotations
import argparse,hashlib,json,os,subprocess
from datetime import datetime,timedelta,timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ACCOUNT=ROOT/'.local/lr-sara-20261114-v1'
PUBLIC=ROOT/'docs/evidence/lr-sara-20261114-v1'
RELEASE=ROOT/'research/manifests/lr_sara_release_20261114_v1.json'

def digest(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def write_new(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2,ensure_ascii=False);f.write('\n')

def save(l):
    p=ACCOUNT/'ledger.json';q=p.with_suffix('.tmp');q.write_text(json.dumps(l,indent=2)+'\n',encoding='utf-8',newline='\n');os.replace(q,p)

def authority(stage=None):
    r=json.loads(RELEASE.read_text());l=json.loads((ACCOUNT/'ledger.json').read_text())
    assert digest(RELEASE)==l['release_sha256'] and l['status'].startswith('ACTIVE')
    now=datetime.now(timezone.utc)
    assert now<datetime.fromisoformat(r['deadline_utc'])
    if stage=='technical':assert now<datetime.fromisoformat(r['technical_deadline_utc'])
    if l['status'].startswith('ACTIVE_CLOSEOUT'):assert stage in (None,'analysis_return')
    return r,l

def reserve(identity,stage,cpu,gpu=0,remote=False,scope=''):
    r,l=authority(stage)
    assert not any(b['id']==identity for b in l['reservations']), 'Never replay a retained attempt'
    assert cpu>0 and gpu>=0
    for name,value in [('cpu',cpu),('gpu_allocated',gpu)]:
        key=name+'_seconds';cap=r['stage_caps_seconds'][stage][name]
        assert sum(b[key] for b in l['reservations'] if b['stage']==stage)+value<=cap
        assert sum(b[key] for b in l['reservations'])+value<=r[name+'_cap_seconds']
    if remote:
        assert not any(b.get('remote') and b['id'] in l['active_jobs'] for b in l['reservations'])
    l['reservations'].append(dict(id=identity,stage=stage,cpu_seconds=cpu,gpu_allocated_seconds=gpu,
        remote=remote,status='RESERVED',scope=scope,started_utc=datetime.now(timezone.utc).isoformat()))
    l['active_jobs'].append(identity);save(l)

def settle(identity,status,**fields):
    l=json.loads((ACCOUNT/'ledger.json').read_text());b=next(b for b in l['reservations'] if b['id']==identity)
    assert identity in l['active_jobs'];b.update(status=status,finished_utc=datetime.now(timezone.utc).isoformat(),**fields)
    l['active_jobs'].remove(identity);save(l)

def init():
    assert not ACCOUNT.exists() and not RELEASE.exists()
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    assert head=='94d3ab79b1d0f229a9f6efe3c1e51d1617670fa9'
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='main'
    prior=ROOT/'.local/lr-sar30-qual-20261114-v1/ledger.json'
    previous=json.loads(prior.read_text());assert previous['status']=='CLOSED_NO_GO_FIXED_ENVIRONMENT_QUALIFICATION' and not previous['active_jobs']
    old_release=ROOT/'research/manifests/lr_sar30_qualification_release_20261114_v1.json'
    pins=json.loads(old_release.read_text())['preservation_pins'].copy()
    paths=[prior,old_release,ROOT/'docs/08_agent_rd/HARNESS_REPAIR_VS_CORE_BENCH_DECISION_20261114.md',
           ROOT/'docs/08_agent_rd/LR_SAR30_QUALIFICATION_OWNER_REPORT_20261114.md',
           ROOT/'docs/08_agent_rd/SAR30_HIGHER_IMPACT_DIRECTION_20261114.md']
    paths+=list((ROOT/'docs/evidence/lr-sar30-qual-20261114-v1').rglob('*'))
    paths+=list((ROOT/'tools').glob('sar30_*.py'))
    for p in paths:
        if p.is_file():pins[p.relative_to(ROOT).as_posix()]=digest(p)
    assert all((ROOT/k).is_file() and digest(ROOT/k)==v for k,v in pins.items())
    now=datetime.now(timezone.utc).replace(microsecond=0);end=now+timedelta(days=7);tech=now+timedelta(hours=36)
    r=dict(schema='curaloop.sara.release.v1',status='OWNER_RELEASED',base_commit=head,
        start_utc=now.isoformat(),deadline_utc=end.isoformat(),technical_deadline_utc=tech.isoformat(),
        start_bangkok=now.astimezone(timezone(timedelta(hours=7))).isoformat(),
        deadline_bangkok=end.astimezone(timezone(timedelta(hours=7))).isoformat(),
        technical_deadline_bangkok=tech.astimezone(timezone(timedelta(hours=7))).isoformat(),
        cpu_cap_seconds=288000,gpu_allocated_cap_seconds=93600,
        stage_caps_seconds={'technical':{'cpu':43200,'gpu_allocated':7200},
            'development':{'cpu':57600,'gpu_allocated':14400},
            'evaluation':{'cpu':115200,'gpu_allocated':57600},
            'analysis_return':{'cpu':72000,'gpu_allocated':14400}},
        max_combined_cpu_equivalents=4,local_cpu_equivalents=1,remote_cpu_equivalents=3,max_gpu_workers=1,
        local_memory_bytes=2*1024**3,remote_aggregate_memory_bytes=32*1024**3,
        task_owned_peak_disk_bytes=80*1024**3,dependency_network_receive_cap_bytes=20*1024**3,
        model_download_authorized=False,new_scientific_input_download_authorized=False,
        remote_root='/home/chaw/curaloop-tasks/lr-sara-20261114-v1',
        prior_return_bundle='.local/lr-sar30-qual-20261114-v1/remote-return-v1/owned-return.tar.gz',
        prior_return_bundle_sha256='4351f5c2675fc5580f163d9a5c19fb4e1dd49ae0f512aedb511ef919c00e8ca3',
        diagnostic_import_attempts_per_affected_lineage_max=1,diagnostic_task_ids=[22,26],
        correction_batches_max=1,native_reference_attempts_per_task_max=1,
        role_freeze_source='docs/evidence/lr-sar30-qual-20261114-v1/role-and-check-freeze-v1.json',
        locked_tasks_min=24,connected_source_clusters_min=12,domains_min=3,max_source_share=0.25,
        public_scientific_check_validated_fraction_min=0.5,
        primary_comparison='Prepared actions plus executable diagnostic checks versus same prepared actions alone',
        primary_seeds=2,secondary_four_cell_common_seed=1,llm_only_contextual_seeds=1,
        development_missions_max=16,locked_model_missions_max=182,
        provider_calls_per_mission_max=3,output_tokens_per_mission_max=4096,context_tokens_max=16384,
        cost_projection_contingency_fraction=0.25,
        model='Existing retained Typhoon2.1 Gemma3 12B Q4_K_M; identity/license/runtime verification before inference; no model search',
        owner_instruction='Approve route A: fresh 80 CPU-hours + 26 GPU-hours / 7 days; dr-train allowed; last harness correction; full study only after passed gates; stop failure; no automatic CORE-Bench migration; owner results before manuscript; commit/push main',
        primary_journal='Empirical Software Engineering',backup_journal='Journal of Systems and Software',
        preservation_pins=pins,prior_accounts_reusable=False,manuscript_writing_authorized=False,
        manuscript_submission=False,main_commit_push_authorized=True,new_subagents=False,
        final16_access=False,private_cf1_rows_access=False,old_hidden_outcomes_access=False,
        paid_api_or_rental=False,public_deployment=False,external_team_writes=False,core_bench_migration=False)
    write_new(RELEASE,r);write_new(PUBLIC/'release-v1.json',r)
    write_new(ACCOUNT/'ledger.json',dict(schema='curaloop.sara.ledger.v1',status='ACTIVE_DIAGNOSIS',release_sha256=digest(RELEASE),
        active_jobs=[],attempts={'diagnostic_imports':{},'correction_batch':None,'native_references':{},'provider_calls':{}},
        reservations=[dict(id='bootstrap-control-v1',stage='technical',cpu_seconds=3600,gpu_allocated_seconds=0,remote=False,
            status='RETAINED_UNMETERED_ADMINISTRATION',scope='Read-only authority/old-source inspection, release/worker preparation and bounded transport metadata; not measured whole-host use')]))
    print(json.dumps({k:r[k] for k in ['start_bangkok','technical_deadline_bangkok','deadline_bangkok']}|{'preservation_pins':len(pins)}))

def verify():
    r=json.loads(RELEASE.read_text());bad=[k for k,v in r['preservation_pins'].items() if not (ROOT/k).is_file() or digest(ROOT/k)!=v]
    print(json.dumps({'status':'FAIL' if bad else 'PASS','pins':len(r['preservation_pins']),'failed':bad}));return int(bool(bad))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['init','verify']);a=p.parse_args()
    raise SystemExit(init() if a.action=='init' else verify())
