"""Owner-released qualification account; no historical account is writable."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = ROOT / '.local/lr-sar30-qual-20261114-v1'
PUBLIC = ROOT / 'docs/evidence/lr-sar30-qual-20261114-v1'
RELEASE = ROOT / 'research/manifests/lr_sar30_qualification_release_20261114_v1.json'

def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def save_ledger(value):
    p = ACCOUNT / 'ledger.json'
    q = p.with_suffix('.tmp')
    q.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8', newline='\n')
    os.replace(q, p)

def authority():
    r = json.loads(RELEASE.read_text(encoding='utf-8'))
    l = json.loads((ACCOUNT / 'ledger.json').read_text(encoding='utf-8'))
    assert digest(RELEASE) == l['release_sha256']
    assert l['status'].startswith('ACTIVE'), 'Closed account cannot restart'
    assert datetime.now(timezone.utc) < datetime.fromisoformat(r['deadline_utc'])
    return r, l

def init():
    assert not RELEASE.exists() and not ACCOUNT.exists(), 'Never reset an account'
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    assert head == 'de3ceea1fc1d4cdff8f52c313cdc8c4f06fbc243'
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'main'
    prior = ROOT / '.local/lr-sar1-20261114-v1/ledger.json'
    previous = json.loads(prior.read_text(encoding='utf-8'))
    assert previous['status'] == 'CLOSED_NO_GO_STATIC_API_FREE_COVERAGE' and not previous['active_jobs']
    old_release = ROOT / 'research/manifests/lr_sar1_release_20261114_v1.json'
    pins = json.loads(old_release.read_text(encoding='utf-8'))['preservation_pins'].copy()
    for p in [prior, old_release, ROOT / 'docs/evidence/lr-sar1-20261114-v1/delivery-audit-v1.json',
              ROOT / 'docs/08_agent_rd/SAR30_FEASIBILITY_PUBLICATION_AND_NEXT_DESIGN_20261114.md',
              ROOT / 'docs/08_agent_rd/SAR30_CANDIDATE_PLANNING_INVENTORY_20261114.csv']:
        pins[p.relative_to(ROOT).as_posix()] = digest(p)
    assert all((ROOT / k).is_file() and digest(ROOT / k) == v for k, v in pins.items())
    now = datetime.now(timezone.utc).replace(microsecond=0)
    r = dict(schema='curaloop.sar30.qualification.release.v1', status='OWNER_RELEASED',
             base_commit=head, start_utc=now.isoformat(), deadline_utc=(now+timedelta(hours=48)).isoformat(),
             cpu_cap_seconds=57600, gpu_allocated_cap_seconds=7200,
             max_combined_cpu_equivalents=4, local_cpu_equivalents=1, remote_cpu_equivalents=3,
             max_gpu_workers=1, local_memory_bytes=2*1024**3, remote_memory_bytes=32*1024**3,
             dependency_download_cap_bytes=30*1024**3, task_owned_disk_cap_bytes=100*1024**3,
             model_download_cap_bytes=0, scientific_input_download_authorized=False,
             stage_caps_seconds={'control':3600,'static':7200,'environment':10800,'native':25200,'report_delivery':10800},
             native_reference_attempts_per_task_max=1, scientific_reruns_authorized=False,
             minimum_locked_native_valid_tasks=24, minimum_locked_source_clusters=12,
             minimum_locked_domains=3, maximum_lineage_share=0.25, public_check_coverage_fraction_min=0.5,
             role_rule='SAR30-development-v1 SHA256 ascending eligible lineage; <=2 candidates, non-old-development domain; accept first two with distinct domains; quarantine entire lineage',
             meaningful_check_rule='Public task states a reproducible algorithmic/numerical requirement with observable artifact or legal input probe; not existence/schema alone; no hidden target values or native tolerances',
             early_stop_rule='If a conservatively optimistic upper bound cannot reach a readiness floor, stop scientific work before native execution; retain all 30 rows and NOT_RUN reasons',
             reference_environment_rule='One source-compatible preparation, fixed before reference execution; no outcome-driven environment/reference retries',
             owner_instruction='Approve 30-task qualification: 16 CPU-hours + 2 GPU-hours / 48 hours, 4 CPU/1 GPU, dr-train allowed; stop/report failure without repeated trials; owner review before full study or manuscript; propose stronger impact direction; open long goal',
             remote_root='/home/chaw/curaloop-tasks/lr-sar30-qual-20261114-v1',
             preservation_pins=pins, prior_accounts_reusable=False, agent_inference_authorized=False,
             manuscript_writing_authorized=False, main_commit_push_authorized=True, new_subagents=False,
             final16_access=False, private_cf1_rows_access=False, old_hidden_outcomes_access=False,
             paid_api_or_rental=False, public_deployment=False, external_team_writes=False,
             manuscript_submission=False, primary_journal='Empirical Software Engineering',
             backup_journal='Journal of Systems and Software')
    write_new(RELEASE, r)
    write_new(PUBLIC / 'release-v1.json', r)
    write_new(ACCOUNT / 'ledger.json', dict(schema='curaloop.sar30.ledger.v1', status='ACTIVE_STATIC',
        release_sha256=digest(RELEASE), deadline_utc=r['deadline_utc'], active_jobs=[],
        reservations=[dict(id='control-preparation-v1',stage='control',cpu_seconds=3600,
                           gpu_allocated_seconds=0,status='RETAINED_UNMETERED_CONTROL_ALLOWANCE',
                           scope='Authority/read-only repository inspection, worker preparation, bounded SSH metadata and orchestration; not measured host use')]))
    print(json.dumps({'status':'ACTIVE_STATIC', 'start_utc':r['start_utc'], 'deadline_utc':r['deadline_utc'], 'pins':len(pins)}))

def verify():
    r = json.loads(RELEASE.read_text(encoding='utf-8'))
    failed = [k for k,v in r['preservation_pins'].items() if not (ROOT/k).is_file() or digest(ROOT/k)!=v]
    print(json.dumps({'status':'FAIL' if failed else 'PASS','pins':len(r['preservation_pins']),'failed':failed}))
    return int(bool(failed))

if __name__ == '__main__':
    p=argparse.ArgumentParser(); p.add_argument('action',choices=['init','verify']); a=p.parse_args()
    raise SystemExit(init() if a.action=='init' else verify())
