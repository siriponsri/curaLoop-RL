"""Audit staged A2 identities and metadata receipts; does not rerun scientific work."""

import csv
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from tools.goal4r2a2_remote_v1 import LOCAL, PACKET, ROOT, write_new

BASE = '19979f12bb5a07cabf4624cd8a2940e663953614'


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    assert git('branch', '--show-current').decode().strip() == 'main'
    assert git('rev-parse', 'HEAD').decode().strip() == BASE
    staged = git('diff', '--cached', '--name-only', '-z').decode().strip('\0').split('\0')
    assert staged and all(staged)
    top = {'.gitattributes', 'AGENTS.md', 'README.md', 'START_HERE.md', 'HANDOFF_TO_CODEX.md',
           'docs/README.md', 'docs/CONTINUATION.md', 'docs/00_project/CLAIM_LEDGER.md',
           'docs/06_execution/GOAL_TRACKER.md', 'tests/research/test_readiness_v1.py'}
    def allowed(name):
        return (name in top or name.startswith('docs/evidence/goal4r2a2-20261106-v1/')
                or name.startswith('research/readiness_v1/') and name.endswith('.py')
                or name.startswith(('docs/03_research/GOAL4R2A2_', 'docs/06_execution/GOAL4R2A2_')) and name.endswith('.md')
                or name.startswith(('research/configs/goal4r2a2_', 'research/manifests/goal4r2a2_')) and name.endswith('.json')
                or name.startswith(('tools/goal4r2a2_', 'tools/verify_goal4r2a2_')) and name.endswith('.py'))
    assert all(allowed(name) for name in staged), 'Unexpected staged scope'
    assert all(not any(part in {'.local', 'raw_data', 'private-tools', '__pycache__'}
                       for part in Path(name).parts) for name in staged)
    assert all(Path(name).suffix not in {'.zip', '.pdf', '.jsonl', '.pyc'} for name in staged)
    assert subprocess.run(['git', 'diff', '--cached', '--check'], cwd=ROOT).returncode == 0
    source_checks = []
    for freeze_name in ('source-freeze-probe-v1.json', 'source-freeze-contracts-v1.json'):
        freeze = json.loads((PACKET / freeze_name).read_text())
        for row in freeze['files']:
            name = row['path']
            if name == 'private-tools/pubchem_rest_request.py':
                private = LOCAL / name
                returned = LOCAL / 'remote-return/full-v1/files' / name
                assert sha(private.read_bytes()) == sha(returned.read_bytes()) == row['sha256']
                source_checks.append({'path': name, 'mode': 'PRIVATE_RETURN_HASH_NOT_GIT_INPUT', 'sha256': row['sha256']})
            else:
                assert sha((ROOT / name).read_bytes()) == sha(git('show', ':' + name)) == row['sha256'], name
                source_checks.append({'path': name, 'mode': 'WORKTREE_AND_GIT_INDEX_EXACT', 'sha256': row['sha256']})
    frozen = {
        'research/configs/goal4r2a_cases_v1.json': 'a0aa21eb13ac38262fc951a1632fba18207627a5ab522e7534626ffd7446ff92',
        'docs/evidence/goal4r1-20261105-v1/results-v1.json': '81d85b936d6d702c873ed0762a30d967f0a23b9a540eccc1a0ff31e6ffc99bc3',
        'docs/03_research/GOAL4_RESULTS_V1.md': '322f48f3ce7923b3d222323b218c2353ac4da9ee31b44bf0d8bac2a38f198e38',
        'docs/06_execution/PLAN_A_CLOSEOUT_20261105.md': '88a0e2e1ec656c2e2b0a19d92b99229a9e15734027c11858d66c96e2ff3eb61b',
        'tools/remote_task_archive_v1.py': '1401547bdfd9d7ecd353a907684f293b08514706ba7481782eef2e9e1ecda667'}
    for name, digest in frozen.items():
        assert sha((ROOT / name).read_bytes()) == sha(git('show', BASE + ':' + name)) == sha(git('show', ':' + name)) == digest
    review = json.loads((PACKET / 'review-record-v1.json').read_text())
    assert all(row['status'] == 'PASS_SCOPED_READ_ONLY_REVIEW' for row in review['reviews'])
    for row in review['reviews']:
        for name, digest in row['reviewed_sha256'].items():
            assert sha((ROOT / name).read_bytes()) == sha(git('show', ':' + name)) == digest, name
    cases = json.loads((ROOT / 'research/configs/goal4r2a2_cases_v1.json').read_text())
    checks = json.loads((PACKET / 'contract-results-v1.json').read_text())
    assert checks['checks'] == 10 and sorted(checks['actual_executed_case_ids']) == sorted(c['id'] for c in cases['cases'])
    receipts = json.loads((PACKET / 'request-receipts-v1.json').read_text())['receipts']
    plan = json.loads((ROOT / 'research/configs/goal4r2a2_requests_v1.json').read_text())
    assert len(receipts) == 107 and len([r for r in receipts if not r['params']]) == 105
    assert all(r['method'] == 'GET' and r['base_url'] == plan['base_url']
               and r['requested_aid'] in plan['allowed_aids']
               and r['path'] == 'assay/aid/' + r['requested_aid'] + '/description/JSON'
               and r['ok'] and r['status_code'] == 200 for r in receipts)
    audit = json.loads((PACKET / 'readiness-audit-v1.json').read_text())
    assert audit['current_aids_observed'] == 105 and audit['provider_count'] == 11
    assert audit['date_field_states'] == {'ABSENT': 105}
    assert audit['selector_control']['current_published_invalid_responses_byte_equal'] is True
    assert sha((PACKET / 'readout-definitions-v1.csv').read_bytes()) == audit['readout_csv_sha256']
    with (PACKET / 'readout-definitions-v1.csv').open(encoding='utf-8', newline='') as f:
        definitions = list(csv.DictReader(f))
    assert len(definitions) == len({(r['aid'], r['tid']) for r in definitions}) == 3287
    proof = json.loads((PACKET / 'local-verification-v2.json').read_text())
    assert proof['file_count'] == 244 and proof['bytes'] == 4919055
    deleted = json.loads((PACKET / 'remote-delete-v1.json').read_text())
    assert deleted['stdout_json_record_count'] == 2 and deleted['tree_sha256'] == proof['tree_sha256']
    assert json.loads((PACKET / 'remote-absence-v1.json').read_text())['status'] == 'PASS_SCOPED_ROOTS_ABSENT'
    package = json.loads((PACKET / 'package-check-v1.json').read_text())
    assert package['status'] == 'PASS'
    links = 0
    pending = {PACKET / 'release-audit-v1.json'}
    for name in staged:
        if name.endswith('.md'):
            text = (ROOT / name).read_text(encoding='utf-8')
            assert not re.search('[\u0e00-\u0e7f]', text), name
            text = re.sub(r'```.*?```', '', text, flags=re.S)
            for target in re.findall(r'!?\[[^\]]*\]\(([^)]+)\)', text):
                target = target.strip().split(' "')[0].strip('<>')
                if re.match(r'^(https?://|mailto:|data:)', target):
                    continue
                file_target = unquote(target).partition('#')[0]
                linked = ((ROOT / name).parent / file_target).resolve() if file_target else ROOT / name
                assert linked.exists() or linked in pending, (name, target)
                links += 1
    for name in staged:
        if name.endswith('.py'):
            compile((ROOT / name).read_bytes(), name, 'exec')
    report = {'status': 'PASS_STAGED_A2_SOURCE_AND_EVIDENCE_AUDIT', 'utc': datetime.now(timezone.utc).isoformat(),
        'base_main': BASE, 'audited_staged_paths': staged, 'source_checks': source_checks,
        'prior_frozen_sha256': frozen, 'ten_actual_cases_passed': True,
        'description_request_count': len(receipts), 'readout_definitions': len(definitions),
        'new_and_updated_markdown_local_links_checked': links, 'english_markdown_check': 'PASS_NO_THAI_CHARACTERS',
        'private_raw_and_benchmark_rows_excluded': True, 'complete_return_before_deletion': True,
        'package_check': 'PASS', 'scientific_campaign_or_native_benchmark': 'NOT_RUN',
        'publication': 'SEPARATE_POST_COMMIT_LIVE_VERIFICATION_REQUIRED',
        'own_report_excluded_from_own_input': True}
    write_new(PACKET / 'release-audit-v1.json', report)
    print(json.dumps({k: v for k, v in report.items() if k not in ('source_checks', 'audited_staged_paths', 'prior_frozen_sha256')}, indent=2))


if __name__ == '__main__':
    main()
