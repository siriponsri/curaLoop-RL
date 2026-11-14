"""Fresh LR-SAR1 authority/account. Historical records are read-only inputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT = ROOT / '.local/lr-sar1-20261114-v1'
PUBLIC = ROOT / 'docs/evidence/lr-sar1-20261114-v1'
RELEASE = ROOT / 'research/manifests/lr_sar1_release_20261114_v1.json'
START = '2026-11-14T02:34:25+00:00'
DEADLINE = '2026-11-24T02:34:25+00:00'
STAGES = {
    'admission': (86400, 0), 'development': (86400, 28800),
    'evaluation': (288000, 230400), 'analysis_return': (86400, 14400),
    'owner_report_delivery': (28800, 0), 'gpu_contingency': (0, 14400),
}


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def save_ledger(ledger):
    path = ACCOUNT / 'ledger.json'
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(ledger, ensure_ascii=False, indent=2) + '\n',
                         encoding='utf-8', newline='\n')
    os.replace(temporary, path)


def authority():
    release = json.loads(RELEASE.read_text(encoding='utf-8'))
    ledger = json.loads((ACCOUNT / 'ledger.json').read_text(encoding='utf-8'))
    if digest(RELEASE) != ledger['release_sha256']:
        raise RuntimeError('Release identity changed')
    if not ledger['status'].startswith('ACTIVE'):
        raise RuntimeError('Account is not active; never reopen a closed account')
    if datetime.now(timezone.utc) >= datetime.fromisoformat(release['deadline_utc']):
        raise RuntimeError('Owner elapsed deadline reached')
    return release, ledger


def init():
    if RELEASE.exists() or (ACCOUNT / 'ledger.json').exists():
        raise RuntimeError('Account/release already exists; never reset')
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    if head != 'f42d8aa8edeb2ef40b73a2cdc040dcebda07ed6b' or branch != 'main':
        raise RuntimeError('Checkout changed; inspect authority before release')
    previous = ROOT / '.local/lr-sc1-20261113-v1/ledger.json'
    previous_ledger = json.loads(previous.read_text(encoding='utf-8'))
    if previous_ledger['status'] != 'CLOSED_NO_GO_NATIVE_EVALUATOR_READINESS' or previous_ledger['active_jobs']:
        raise RuntimeError('Previous account is not closed/settled')
    prior_release = ROOT / 'research/manifests/lr_sc1_release_20261113_v1.json'
    pins = json.loads(prior_release.read_text(encoding='utf-8'))['preservation_pins'].copy()
    failures = [name for name, expected in pins.items()
                if not (ROOT / name).is_file() or digest(ROOT / name) != expected]
    if failures:
        raise RuntimeError('Prior preservation mismatch: ' + repr(failures))
    extra = [str(previous.relative_to(ROOT)), str(prior_release.relative_to(ROOT)),
             'docs/evidence/lr-sc1-20261113-v1/delivery-audit-v1.json',
             'docs/08_agent_rd/SCIENTIFIC_AGENT_RELIABILITY_STUDY_PROPOSAL_20261114.md',
             'docs/08_agent_rd/SCIENTIFIC_AGENT_RELIABILITY_DIRECTION_DECISION_20261114.md',
             'docs/08_agent_rd/DEEP_RESEARCH_DIRECTION_REVIEW_20261114.md',
             'docs/08_agent_rd/LR_SAR1_RESULTS_DIRECTION_AND_PUBLICATION_REPORT_20261114.md',
             'docs/00_project/PROJECT_HISTORY_RESULTS_AND_HANDOVER_20261114.md',
             'docs/00_project/PROJECT_REPORT_INDEX_20261114.md',
             'docs/00_project/PROJECT_HISTORY_REPORT_AUDIT_20261114.json']
    for name in extra:
        pins[name.replace('\\', '/')] = digest(ROOT / name)
    release = {
        'schema': 'curaloop.lr-sar1.release.v1', 'status': 'OWNER_RELEASED',
        'base_commit': head, 'start_utc': START, 'deadline_utc': DEADLINE,
        'start_bangkok': '2026-11-14T09:34:25+07:00',
        'deadline_bangkok': '2026-11-24T09:34:25+07:00',
        'owner_instruction': 'Start LR-SAR1 under approved plan/resources; ESE primary, JSS backup; stop/report failed gates without repeated experiments; report results before any manuscript; also propose Thai journals',
        'cpu_cap_seconds': 576000, 'gpu_allocated_cap_seconds': 288000,
        'stage_caps_seconds': {k: {'cpu': v[0], 'gpu_allocated': v[1]} for k, v in STAGES.items()},
        'max_combined_cpu_equivalents': 4, 'local_cpu_equivalents': 1,
        'remote_cpu_equivalents': 3, 'max_gpu_workers': 1,
        'local_memory_bytes': 2147483648, 'remote_memory_bytes': 34359738368,
        'task_owned_disk_cap_bytes': 100 * 1024**3,
        'model_download_cap_bytes': 20 * 1024**3,
        'dependency_download_cap_bytes': 30 * 1024**3,
        'model': 'Qwen/Qwen2.5-Coder-7B-Instruct; official unquantized; revision fixed before inference',
        'benchmark': 'ScienceAgentBench verified 2026-04-30, retained snapshot only',
        'minimum_locked_tasks': 60, 'minimum_locked_source_clusters': 15,
        'minimum_locked_domains': 3, 'native_correction_batches_max': 1,
        'development_missions_max': 32, 'development_provider_calls_max': 96,
        'model_calls_per_mission_max': 3, 'output_tokens_per_mission_max': 4096,
        'context_tokens_max': 16384, 'locked_missions_max': 408,
        'locked_provider_calls_max': 1224,
        'remote_root': '/home/chaw/curaloop-tasks/lr-sar1-20261114-v1',
        'preservation_pins': pins, 'prior_accounts_reusable': False,
        'manuscript_writing_authorized': False, 'owner_results_checkpoint_required': True,
        'primary_journal': 'Empirical Software Engineering', 'backup_journal': 'Journal of Systems and Software',
        'thai_journal_review_requested': True, 'main_commit_push_authorized': True,
        'final16_access': False, 'private_cf1_rows_access': False,
        'old_hidden_outcomes_access': False, 'paid_api_or_rental': False,
        'public_deployment': False, 'external_team_writes': False,
        'manuscript_submission': False, 'new_subagents': False,
    }
    write_new(RELEASE, release)
    write_new(ACCOUNT / 'release.json', release)
    write_new(ACCOUNT / 'ledger.json', {
        'schema': 'curaloop.lr-sar1.ledger.v1', 'status': 'ACTIVE_G0',
        'release_sha256': digest(RELEASE), 'deadline_utc': DEADLINE,
        'reservations': [{'id': 'bootstrap-admin-v1', 'stage': 'admission',
                          'cpu_seconds': 3600, 'gpu_allocated_seconds': 0,
                          'status': 'RETAINED_UNMETERED_CONTROL_ALLOWANCE',
                          'scope': 'Initial repository/authority/preservation inspection, bounded source/journal review and orchestration preparation; not measured whole-host CPU'}],
        'active_jobs': [], 'prior_accounts_unchanged': True,
    })
    write_new(PUBLIC / 'release-v1.json', release)
    print(json.dumps({'status': 'ACTIVE_G0', 'deadline_bangkok': release['deadline_bangkok'],
                      'preservation_pins': len(pins), 'retained_admin_cpu_seconds': 3600,
                      'gpu_allocated_seconds': 0, 'manuscript_authorized': False}))


def verify():
    release = json.loads(RELEASE.read_text(encoding='utf-8'))
    failed = [name for name, expected in release['preservation_pins'].items()
              if not (ROOT / name).is_file() or digest(ROOT / name) != expected]
    print(json.dumps({'status': 'FAIL' if failed else 'PASS',
                      'preservation_pins': len(release['preservation_pins']), 'failed': failed}))
    return int(bool(failed))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=('init', 'verify'))
    args = parser.parse_args()
    raise SystemExit(init() if args.action == 'init' else verify())
