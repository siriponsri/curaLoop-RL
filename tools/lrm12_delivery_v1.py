"""Validate LR-M12 scope, immutable execution evidence and English delivery."""

import argparse
import ast
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / 'docs/evidence/lr-m12-20261108-v1'
PRIVATE = ROOT / '.local/lr-m12-20261108-v1'
BASE = 'cf1f58fc592e07c63a0101ae3c69813815ebba60'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    result = subprocess.run(['rtk', 'proxy', 'git', *args], cwd=ROOT, capture_output=True, check=True)
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, required=True)
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    target = PUBLIC / f'delivery-validation-v{args.revision}.json'
    assert not target.exists()
    status = json.loads((ROOT / 'research/configs/lr_m12_status_20261108_v1.json').read_text())
    assert status['m1_status'] == 'COMPLETE_INVESTIGATION_NO_GO'
    assert status['m2_status'] == 'NOT_RUN_GATE_NOT_PASSED' and not status['scientific_release_open']
    ledger = json.loads((PRIVATE / 'ledger.json').read_text())
    assert ledger['status'] == 'CLOSED_OWNER_CHECKPOINT' and ledger['m2_release'] is False
    assert ledger['attempted_campaigns'] == 0 and len(ledger['jobs']) == 14
    assert all(r['state'] == 'PASS' for r in ledger['jobs'])
    assert sum(ledger['bucket_reserved_seconds'].values()) == 7320 <= ledger['cpu_cap_seconds'] == 86400
    assert ledger['bucket_reserved_seconds']['m2_main'] == ledger['bucket_reserved_seconds']['m2_ablations_reproduction'] == 0
    assert json.loads((PUBLIC / 'ledger-closeout-v1.json').read_text()) == ledger
    for row in json.loads((PUBLIC / 'old-ledgers-unchanged-v1.json').read_text())['ledgers']:
        assert sha(ROOT / row['path']) == row['sha256']
    freeze = json.loads((PUBLIC / 'm1-freeze-v2.json').read_text())
    for name, digest in freeze['code_sha256'].items():
        assert sha(ROOT / name) == digest, name
    summary = json.loads((PUBLIC / 'm1-summary-v1.json').read_text())
    assert summary['timing_calls'] == 36 and summary['diagnostic_cases'] == 12
    assert summary['m2_campaigns'] == 0 and not summary['reserved_final_feature_label_or_presence_decode']
    assert summary['variants']['confidence_min']['deviations_from_greedy'] == 0
    checks = json.loads((PUBLIC / 'constructed-checks-v1.json').read_text())
    assert checks['count'] == len(checks['checks']) == 17 and not checks['actual_molecular_data_access']
    proof = json.loads((PUBLIC / 'complete-return-verified-v1.json').read_text())
    assert proof['file_count'] == 2424 and proof['total_bytes'] == 231827380
    assert proof['all_code_dependency_input_output_regular_files_returned'] is True
    for name, pin in proof['export_file_pins'].items():
        path = PRIVATE / 'remote-return/export' / name
        assert sha(path) == pin['sha256'] and path.stat().st_size == pin['bytes']
    absence = json.loads((PUBLIC / 'fresh-absence-v1.json').read_text())
    assert absence['status'] == 'PASS_FRESH_EXACT_ABSENCE' and len(absence['paths']) == 2
    unchanged = []
    for name in ('docs/01_paper/05_results.md', 'docs/01_paper/09_declarations.md',
                 'research/configs/method_first_status_20261108_v1.json',
                 'research/configs/lr_m12_proposal_20261108_v1.json',
                 'docs/06_execution/LR_M12_PROPOSAL_20261108.md'):
        old = git('rev-parse', BASE + ':' + name).decode().strip()
        current = git('hash-object', '--path', name, name).decode().strip()
        assert old == current, name
        unchanged.append({'path': name, 'git_blob': old})
    tracked = git('diff', '--name-only', BASE).decode().splitlines()
    untracked = git('ls-files', '--others', '--exclude-standard').decode().splitlines()
    names = sorted(set(tracked + untracked))
    names = [name for name in names if not re.search(r'/delivery-validation-v\d+\.json$', name)]
    links, chapters = 0, 0
    document_pins, code_pins = {}, {}
    for name in names:
        assert not name.startswith(('.local/', 'research/raw_data/', 'frontend/', 'src/'))
        path = ROOT / name
        assert path.is_file()
        if path.suffix == '.py':
            ast.parse(path.read_text(encoding='utf-8'))
            code_pins[name] = sha(path)
        elif path.suffix == '.md':
            body = path.read_text(encoding='utf-8')
            assert not re.search('[\u0e00-\u0e7f]', body), name
            for link in re.findall(r'\]\(([^\n]+?)\)', body):
                link = link.strip('<>')
                if link.startswith('#') or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', link):
                    continue
                assert (path.parent / link.split('#', 1)[0]).resolve().exists(), (name, link)
                links += 1
            document_pins[name] = sha(path)
        elif path.suffix == '.json':
            json.loads(path.read_text(encoding='utf-8'))
    manuscript = (ROOT / 'docs/01_paper/MANUSCRIPT.md').read_text(encoding='utf-8')
    for chapter in sorted((ROOT / 'docs/01_paper').glob('[0-9][0-9]_*.md')):
        fragment = re.sub(r'^(#{1,5}) ', r'#\1 ', chapter.read_text(encoding='utf-8').strip(), flags=re.M)
        assert fragment in manuscript, chapter.name
        chapters += 1
    assert chapters == 10
    checkpoint = None
    if args.checkpoint:
        checkpoint = git('rev-parse', args.checkpoint).decode().strip()
        for name in names:
            assert git('rev-parse', checkpoint + ':' + name).decode().strip() == git(
                'hash-object', '--path', name, name).decode().strip(), name
        for name, digest in freeze['code_sha256'].items():
            assert hashlib.sha256(git('show', checkpoint + ':' + name)).hexdigest() == digest, name
    result = {'status': 'PASS_LR_M12_DELIVERY_CHECKS', 'utc': datetime.now(timezone.utc).isoformat(),
              'starting_checkpoint': BASE, 'verified_content_checkpoint': checkpoint,
              'm1_gate': summary['m1_gate'], 'm2': 'NOT_RUN', 'chapters': chapters,
              'existing_local_document_links': links, 'document_sha256': document_pins,
              'new_code_sha256': code_pins, 'unchanged_historical_records': unchanged,
              'retained_seconds': 7320, 'active_owned_jobs': 0,
              'independent_semantic_scientific_review': 'NOT_RUN',
              'application_runtime_browser_build': 'NOT_RUN_NO_PRODUCT_RUNTIME_CHANGE',
              'passed_checks_are_not_scientific_go': True}
    with target.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2)
        f.write('\n')
    print(json.dumps({'status': result['status'], 'documents': len(document_pins),
                      'new_python_files': len(code_pins), 'links': links,
                      'checkpoint': checkpoint, 'm2': 'NOT_RUN'}))


if __name__ == '__main__':
    main()
