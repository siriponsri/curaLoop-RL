"""Fresh LR1 caps and finite-attempt accounting; no historical ledger mutation."""
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ACCOUNT=ROOT/'.local/lr-sara-lr1-20261114-v1'
PUBLIC=ROOT/'docs/evidence/lr-sara-lr1-20261114-v1'
RELEASE=ROOT/'research/manifests/lr_sara_lr1_release_20261114_v1.json'
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  while block:=f.read(1024**2):h.update(block)
 return h.hexdigest()
def write_new(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def save(l):
 p=ACCOUNT/'ledger.json';q=p.with_suffix('.tmp');q.write_text(json.dumps(l,indent=2)+'\n',encoding='utf-8',newline='\n');os.replace(q,p)
def authority(stage):
 r=json.loads(RELEASE.read_text());l=json.loads((ACCOUNT/'ledger.json').read_text());assert digest(RELEASE)==l['release_sha256']
 assert l['status'].startswith('ACTIVE');assert datetime.now(timezone.utc)<datetime.fromisoformat(r['deadlines_utc'][stage])
 if l['status'].startswith('ACTIVE_CLOSEOUT'):assert stage=='analysis_return'
 return r,l
def reserve(identity,stage,cpu,gpu=0,remote=False,scope=''):
 r,l=authority(stage);assert cpu>0 and gpu>=0 and not any(x['id']==identity for x in l['reservations'])
 for k,n in [('cpu_seconds','cpu'),('gpu_allocated_seconds','gpu_allocated')]:
  value=cpu if n=='cpu' else gpu
  assert sum(x[k] for x in l['reservations'] if x['stage']==stage)+value<=r['stage_caps_seconds'][stage][n]
  assert sum(x[k] for x in l['reservations'])+value<=r[n+'_cap_seconds']
 if remote:assert not any(x['id'] in l['active_jobs'] and x.get('remote') for x in l['reservations'])
 l['reservations'].append(dict(id=identity,stage=stage,cpu_seconds=cpu,gpu_allocated_seconds=gpu,remote=remote,status='RESERVED',scope=scope,started_utc=datetime.now(timezone.utc).isoformat()));l['active_jobs'].append(identity);save(l)
def settle(identity,status,**fields):
 l=json.loads((ACCOUNT/'ledger.json').read_text());assert identity in l['active_jobs'];b=next(x for x in l['reservations'] if x['id']==identity)
 b.update(status=status,finished_utc=datetime.now(timezone.utc).isoformat(),**fields);l['active_jobs'].remove(identity);save(l)
def stop(gate,reason):
 l=json.loads((ACCOUNT/'ledger.json').read_text());l.update(status='ACTIVE_CLOSEOUT_NO_GO',terminal_gate=gate,terminal_reason=reason);save(l)
