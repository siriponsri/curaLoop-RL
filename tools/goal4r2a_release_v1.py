"""Verify reviewed/frozen bytes in the worktree and Git index before publication."""

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from tools.goal4r2a_remote_v1 import PACKET, ROOT, write_new


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def main():
    expected = {}
    for version in ('v1', 'v2', 'v3'):
        freeze = json.loads((PACKET / ('source-freeze-' + version + '.json')).read_text())
        for row in freeze['files']:
            if row['path'] in expected and expected[row['path']] != row['sha256']:
                raise ValueError('Additive bundles changed an already frozen source')
            expected[row['path']] = row['sha256']
    expected.update(json.loads((PACKET / 'independent-review-v1.json').read_text())['reviewed_document_sha256'])
    expected.update({
        'docs/evidence/goal4r2a-20261106-v1/si-metadata-audit-v1.json': 'a821005838e29b61751adea8c1200c3f5e268b821ce3a518723d1877544cb6ec',
        'docs/evidence/goal4r1-20261105-v1/results-v1.json': '81d85b936d6d702c873ed0762a30d967f0a23b9a540eccc1a0ff31e6ffc99bc3',
        'docs/03_research/GOAL4_RESULTS_V1.md': '322f48f3ce7923b3d222323b218c2353ac4da9ee31b44bf0d8bac2a38f198e38',
        'docs/06_execution/PLAN_A_CLOSEOUT_20261105.md': '88a0e2e1ec656c2e2b0a19d92b99229a9e15734027c11858d66c96e2ff3eb61b',
    })
    failures = []
    for name, digest in expected.items():
        for kind, raw in [('worktree', (ROOT / name).read_bytes()), ('Git index', git('show', ':' + name))]:
            if hashlib.sha256(raw).hexdigest() != digest:
                failures.append(kind + ' differs: ' + name)
    staged = [name for name in git('diff', '--cached', '--name-only', '-z').decode().split('\0') if name]
    for name in staged:
        if name.startswith(('.local/', 'research/raw_data/', '.ssh/')) or Path(name).suffix.lower() in {
            '.pdf', '.zip', '.tar', '.gz', '.npz', '.pyc', '.dll', '.so', '.exe'}:
            failures.append('Private or binary publication payload: ' + name)
        if len(git('show', ':' + name)) > 5 * 1024**2:
            failures.append('Unexpected large artifact: ' + name)
    result = {'status': 'PASS_REVIEWED_AND_EXECUTED_GIT_IDENTITIES' if not failures else 'FAIL',
              'utc': datetime.now(timezone.utc).isoformat(), 'identities_checked': len(expected),
              'expected_sha256': expected, 'staged_files_at_check': len(staged),
              'failures': failures, 'scientific_or_runtime_tests_repeated': False,
              'private_pdfs_data_and_reader_sources_staged': False if not failures else 'SEE_FAILURES',
              'limits': ['Publication is checked separately against live remote main after commit']}
    write_new(PACKET / 'release-integrity-v1.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'expected_sha256'}, indent=2))
    return bool(failures)


if __name__ == '__main__':
    raise SystemExit(main())
