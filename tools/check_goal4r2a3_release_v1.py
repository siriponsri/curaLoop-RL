"""Audit staged source identities against the complete opaque A3 return proof."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/evidence/goal4r2a3-20261106-v1'
RETURN = ROOT / '.local/goal4r2a3-20261106-v1/remote-return/full-v1'
BUNDLES = ['audit-v1', 'xref-v1', 'reconcile-v1', 'reconcile-v2', 'identifiers-v3',
           'observations-v2', 'offline-submit-v2']


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    failures, checked, historical = [], [], []
    proof = read(RETURN / 'local-verification-with-manifest.json')
    manifest = read(RETURN / 'manifest.json')
    assert proof['status'] == 'PASS_LOCAL_ALL_FILES_VERIFIED' and proof['manifest_unchanged_during_verification']
    assert proof['manifest_sha256'] == sha((RETURN / 'manifest.json').read_bytes())
    assert proof['file_count'] == manifest['file_count'] == 1963
    assert proof['bytes'] == manifest['bytes'] == 689826056
    assert read(PACKET / 'remote-absence-v1.json')['status'] == 'PASS_SCOPED_ROOTS_ABSENT'
    inventory = {r['path']: r for r in manifest['files']}
    for bundle in BUNDLES:
        freeze = read(PACKET / ('source-freeze-' + bundle + '.json'))
        private_manifest_path = RETURN / 'files' / (bundle + '.json')
        assert sha(private_manifest_path.read_bytes()) == inventory[bundle + '.json']['sha256']
        assert read(private_manifest_path) == freeze
        assert inventory[bundle + '.zip']['sha256'] == freeze['archive_sha256']
        historical.append({'bundle': bundle, 'files': len(freeze['files']), 'archive_sha256': freeze['archive_sha256']})
    final = read(PACKET / 'source-freeze-offline-submit-v2.json')
    for row in final['files']:
        name = row['path']
        if name.startswith('private-inputs/'):
            continue
        path = ROOT / name
        if not path.is_file() or sha(path.read_bytes()) != row['sha256']:
            failures.append('Current public source differs from final executed bundle: ' + name)
            continue
        try:
            staged = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            failures.append('Public source missing from Git index: ' + name)
            continue
        if sha(staged) != row['sha256']:
            failures.append('Staged public bytes differ from executed bytes: ' + name)
        checked.append({'path': name, 'sha256': row['sha256']})
    local_proof_sources = {
        'tools/verify_goal4r2a3_return_v1.py': proof['base_verifier_sha256'],
        'tools/verify_goal4r2a3_return_v2.py': proof['enhanced_verifier_sha256'],
        'tools/goal4r2a3_guard_v1.py': read(PACKET / 'preservation-resources-v1.json')['guard_source_sha256'],
    }
    for name, expected in local_proof_sources.items():
        staged = subprocess.check_output(['git', 'show', ':' + name], cwd=ROOT)
        if sha(staged) != expected or sha((ROOT / name).read_bytes()) != expected:
            failures.append('Staged local preservation source differs from executed proof: ' + name)
        checked.append({'path': name, 'sha256': expected})
    names = subprocess.check_output(['git', 'diff', '--cached', '--name-only', '-z'], cwd=ROOT).decode().split('\0')
    for name in filter(None, names):
        if name.startswith(('.local/', 'research/raw_data/', '.ssh/')):
            failures.append('Private data path staged: ' + name)
    budget = read(PACKET / 'budget-closeout-v1.json')
    assert budget['conservative_charge_cpu_seconds'] == 19800 <= budget['a3_cap_cpu_seconds'] <= budget['b_cap_cpu_seconds']
    assert budget['completed_pubchem_requests'] == 24 and budget['completed_uniprot_requests'] == 27
    assert budget['named_distinct_engineering_cases'] == 29 and budget['case_executions'] == 32
    assert read(PACKET / 'offline-submit-results-v1.json')['network_ledger_unchanged_sha256'] == budget['network_ledger_sha256']
    report = {'status': 'PASS' if not failures else 'FAIL', 'failures': failures,
              'staged_source_byte_checks': checked, 'preserved_executed_bundles': historical,
              'complete_return_file_count': proof['file_count'], 'tree_sha256': proof['tree_sha256'],
              'private_scientific_values_deserialized': False, 'paired_qualification': 'NOT_RUN',
              'scientific_advancement': 'NO_GO', 'complete_return_reread_basis': 'UNCHANGED_MANIFEST_AND_PRIOR_FULL_REREAD_PROOF',
              'new_scientific_tests_or_network_calls': 0}
    with args.output.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(report, handle, indent=2); handle.write('\n')
    print(json.dumps({'status': report['status'], 'staged_source_files': len(checked),
                      'preserved_bundles': len(historical), 'failures': failures}, indent=2))
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
