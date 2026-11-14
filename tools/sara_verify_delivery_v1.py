"""Read-only verification of closed route-A evidence and exact main delivery bytes."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.sara_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,digest

def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)

def verify(index=False,delivered=False):
 r=json.loads(RELEASE.read_text());l=json.loads((ACCOUNT/'ledger.json').read_text());audit=json.loads((PUBLIC/'delivery-audit-v1.json').read_text())
 assert l['status']=='CLOSED_NO_GO_FINAL_CORRECTION_OPERATION_FAILED' and not l['active_jobs']
 assert digest(ACCOUNT/'ledger.json')==digest(PUBLIC/'closed-resource-ledger-v1.json')==audit['closed_ledger_sha256']
 assert digest(RELEASE)==l['release_sha256']==audit['release_sha256']
 assert all(digest(ROOT/k)==v for k,v in r['preservation_pins'].items())
 assert all(digest(ROOT/k)==v for k,v in audit['evidence_sha256'].items())
 assert digest(ROOT/'docs/08_agent_rd/LR_SARA_FINAL_OWNER_REPORT_20261114.md')==audit['report_sha256']
 sources=json.loads((PUBLIC/'source-identity-v1.json').read_text())
 for k,v in sources['current_sources'].items():assert digest(ROOT/k)==v,k
 for row in sources['executed_job_snapshots']:
  assert digest(ROOT/row['path'])==row['sha256']
  if 'resource_receipt_sha256' in row:assert digest((ROOT/row['path']).parent/'resources.json')==row['resource_receipt_sha256']
 assert len(json.loads((PUBLIC/'all-thirty-terminal-states-v1.json').read_text())['rows'])==30
 assert audit['native_references']==audit['native_scorer_calls']==audit['provider_calls']==audit['gpu_allocated_seconds']==0
 assert git('branch','--show-current').decode().strip()=='main'
 checked=[]
 if index or delivered:
  paths=(git('diff','--cached','--name-only','-z') if index else git('diff','HEAD^','HEAD','--name-only','-z')).decode().split('\0')
  exact={'AGENTS.md','tools/.gitattributes','research/manifests/.gitattributes',RELEASE.relative_to(ROOT).as_posix(),
   'docs/08_agent_rd/HARNESS_REPAIR_VS_CORE_BENCH_DECISION_20261114.md','docs/08_agent_rd/LR_SARA_FINAL_OWNER_REPORT_20261114.md'}
  for name in filter(None,paths):
   assert name in exact or name.startswith('docs/evidence/lr-sara-20261114-v1/') or (name.startswith('tools/sara_') and name.endswith('.py')),name
   expected=(ROOT/name).read_bytes();blob=git('show',(':' if index else 'HEAD:')+name)
   assert expected==blob,('Index/commit differs from audited disk bytes',name);checked.append(name)
  assert checked
 if delivered:
  assert not git('status','--porcelain').strip()
  head=git('rev-parse','HEAD').decode().strip();remote=git('ls-remote','origin','refs/heads/main').decode().split()[0]
  assert head==remote
  result=dict(status='PASS_ACTUAL_MAIN_PUSH_AND_CLOSED_EVIDENCE',head=head,remote_main=remote,preservation_pins=len(r['preservation_pins']),
   exact_delivered_files=len(checked),closed_ledger_sha256=digest(ACCOUNT/'ledger.json'))
 else:result=dict(status='PASS_CLOSED_EVIDENCE_AND_EXACT_INDEX' if index else 'PASS_CLOSED_EVIDENCE',preservation_pins=len(r['preservation_pins']),exact_index_files=len(checked))
 print(json.dumps(result));return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--index',action='store_true');p.add_argument('--delivered',action='store_true');args=p.parse_args()
 result=verify(args.index,args.delivered)
 if args.delivered:
  target=ACCOUNT/'actual-main-git-receipt-v1.json'
  with target.open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
