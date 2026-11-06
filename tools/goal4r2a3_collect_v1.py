"""Copy closed allowlists of qualification aggregates; raw responses remain private."""

import argparse
import base64
import hashlib
import json

from tools.goal4r2a3_remote_v1 import LOCAL, PACKET, REMOTE, write_new
from tools.remote_goal4_control_v1 import ssh_script

PHASES = {
    'audit': {'metadata-audit-results-v1.json': 'results.json', 'metadata-audit-resources-v1.json': 'resources.json',
              'qualification-checks-v1.log': 'checks.log', 'qualification-check-results-v1.json': 'checks.json',
              'protection-summary-v1.json': 'protection-summary.json', 'source-binding-register-v1.json': 'source-binding-register.json',
              'rights-register-v1.json': 'rights-register.json', 'xref-request-plan-v1.json': 'xref-requests.json'},
    'xref': {'xref-results-v1.json': 'results.json', 'xref-resources-v1.json': 'resources.json',
             'network-boundary-checks-v1.json': 'network-boundary-checks.json',
             'family-overlay-v1.json': 'family-overlay.json', 'pair-metadata-gates-v1.json': 'pair-metadata-gates.json',
             'xref-metadata-receipts-v1.json': 'metadata-request-receipts.json'},
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', choices=PHASES, required=True)
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--bundle', required=True)
    args = parser.parse_args()
    assert args.attempt.replace('-', '').isalnum() and args.bundle.replace('-', '').isalnum()
    source = '''
import base64,hashlib,json
from pathlib import Path
root=Path(REMOTE);run=root/'runs'/ATTEMPT
assert run.resolve()==run and run.parent==root/'runs'
out={}
for name,rel in FILES.items():
 path=run/rel
 assert path.is_file() and not path.is_symlink() and path.stat().st_size<=2*1024**2
 raw=path.read_bytes()
 out[name]={'base64':base64.b64encode(raw).decode(),'sha256':hashlib.sha256(raw).hexdigest()}
print(json.dumps(out))
'''
    prefix = 'REMOTE=' + repr(REMOTE) + '\nATTEMPT=' + repr(args.attempt) + '\nFILES=' + repr(PHASES[args.phase]) + '\n'
    records = json.loads(ssh_script(prefix + source))
    hashes = {}
    for name, row in records.items():
        raw = base64.b64decode(row['base64'], validate=True)
        assert hashlib.sha256(raw).hexdigest() == row['sha256']
        with (PACKET / name).open('xb') as f:
            f.write(raw)
        hashes[name] = row['sha256']
    write_new(PACKET / ('source-freeze-' + args.bundle + '.json'), json.loads((LOCAL / (args.bundle + '.json')).read_text()))
    write_new(PACKET / ('aggregate-transfer-' + args.phase + '-v1.json'), {
        'status': 'PASS_CLOSED_ALLOWLIST_TRANSFER', 'sha256': hashes, 'activity_values_included': False,
        'protected_canonical_structures_included': False, 'full_return_pending': True})
    print(json.dumps({'status': 'PASS_ALLOWLISTED_QUALIFICATION_METADATA', 'files': len(hashes)}))


if __name__ == '__main__':
    main()
