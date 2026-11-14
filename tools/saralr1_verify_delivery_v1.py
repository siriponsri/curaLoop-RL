"""Read-only closed evidence, exact staged/committed bytes and main push verifier."""
import argparse,json,subprocess,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.saralr1_control_v1 import ROOT,ACCOUNT,PUBLIC,RELEASE,digest
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def main():
 p=argparse.ArgumentParser();p.add_argument('--index',action='store_true');p.add_argument('--delivered',action='store_true');a=p.parse_args()
 r=json.loads(RELEASE.read_text());l=json.loads((ACCOUNT/'ledger.json').read_text());audit=json.loads((PUBLIC/'delivery-audit-v1.json').read_text())
 assert l['status']=='CLOSED_NO_GO_ENGINEERING_ACCEPTANCE' and not l['active_jobs']
 assert digest(ACCOUNT/'ledger.json')==digest(PUBLIC/'closed-resource-ledger-v1.json')==audit['closed_ledger_sha256']
 assert digest(RELEASE)==audit['release_sha256']==l['release_sha256']
 assert all(digest(ROOT/k)==v for k,v in r['preservation_pins'].items())
 assert all(digest(ROOT/k)==v for k,v in audit['evidence_sha256'].items())
 assert digest(ROOT/'docs/08_agent_rd/LR_SARA_LR1_FINAL_OWNER_REPORT_20261114.md')==audit['report_sha256']
 source=json.loads((PUBLIC/'source-identity-v1.json').read_text());assert all(digest(ROOT/k)==v for k,v in source['current_sources'].items())
 for row in source['executed_jobs']:
  path=ROOT/row['path'];assert digest(path)==row['sha256'] and digest(path.parent/'resources.json')==row['resource_receipt_sha256']
 assert git('branch','--show-current').decode().strip()=='main';checked=[]
 if a.index or a.delivered:
  names=(git('diff','--cached','--name-only','-z') if a.index else git('diff','HEAD^','HEAD','--name-only','-z')).decode().split('\0')
  exact={'AGENTS.md','tools/.gitattributes','research/manifests/.gitattributes',RELEASE.relative_to(ROOT).as_posix(),
   'docs/08_agent_rd/SARA_TARGETED_PATCH_CONTINUATION_PROPOSAL_20261114.md','docs/08_agent_rd/LONG_RUN_SARA_PATCH_TO_RESULTS_PROPOSAL_20261114.md','docs/08_agent_rd/LR_SARA_LR1_FINAL_OWNER_REPORT_20261114.md'}
  for name in filter(None,names):
   assert name in exact or name.startswith('docs/evidence/lr-sara-lr1-20261114-v1/') or (name.startswith('tools/saralr1_') and name.endswith('.py')),name
   assert git('show',(':' if a.index else 'HEAD:')+name)==(ROOT/name).read_bytes(),name;checked.append(name)
  assert checked
 result=dict(status='PASS_CLOSED_EVIDENCE_AND_INDEX' if a.index else 'PASS_CLOSED_EVIDENCE',preservation_pins=len(r['preservation_pins']),exact_files=len(checked))
 if a.delivered:
  assert not git('status','--porcelain').strip();head=git('rev-parse','HEAD').decode().strip();remote=git('ls-remote','origin','refs/heads/main').decode().split()[0];assert head==remote
  result.update(status='PASS_ACTUAL_MAIN_DELIVERY',head=head,remote_main=remote,closed_ledger_sha256=digest(ACCOUNT/'ledger.json'))
  with (ACCOUNT/'actual-main-git-receipt-v1.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(result))
if __name__=='__main__':main()
