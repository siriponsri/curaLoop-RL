"""Return allowlisted metadata summaries; full response text stays in private return."""

import base64
import hashlib
import json

from tools.goal4r2a2_remote_v1 import LOCAL, PACKET, REMOTE, write_new
from tools.remote_goal4_control_v1 import ssh_script


def main():
    source = '''
import base64,hashlib,json
from pathlib import Path
root=Path(REMOTE)
assert root.resolve()==root
files={
 'metadata-register-v1.json':root/'runs/metadata-acquire-v1/results.json',
 'metadata-resources-v1.json':root/'runs/metadata-acquire-v1/resources.json',
 'contract-results-v1.json':root/'runs/contracts-v1/results.json',
 'contract-resources-v1.json':root/'runs/contracts-v1/resources.json',
 'contract-checks-v1.log':root/'runs/contracts-v1/checks.log',
 'probe-resources-v1.json':root/'runs/metadata-probe-v1/resources.json',
 'remote-launch-ledger-v1.json':root/'launch-ledger.json',
}
out={}
for name,path in files.items():
 assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(root)
 assert path.stat().st_size<1024*1024
 data=path.read_bytes()
 out[name]={'sha256':hashlib.sha256(data).hexdigest(),'base64':base64.b64encode(data).decode()}
receipts=[]
for run in ['metadata-probe-v1','metadata-acquire-v1']:
 for path in sorted((root/'runs'/run).glob('request-*.json')):
  assert not path.is_symlink() and path.stat().st_size<65536
  r=json.loads(path.read_text())
  v=r['result']
  receipts.append({'receipt_path':path.relative_to(root).as_posix(),
   'receipt_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
   'requested_aid':r['requested_aid'],'request_utc':r['request_utc'],
   'method':r['request']['method'],'base_url':r['request']['base_url'],
   'path':r['request']['path'],'params':r['request']['params'],
   'ok':v.get('ok'),'status_code':v.get('status_code'),
   'content_type':v.get('content_type'),'error':v.get('error'),
   'response_bytes':r['response_bytes'],'response_sha256':r['response_sha256']})
print(json.dumps({'files':out,'request_receipts':receipts}))
'''
    transferred = json.loads(ssh_script('REMOTE=' + repr(REMOTE) + '\n' + source))
    hashes = {}
    for name, row in transferred['files'].items():
        if '/' in name or '\\' in name:
            raise ValueError('Unexpected public aggregate name')
        data = base64.b64decode(row['base64'], validate=True)
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Transferred metadata checksum differs')
        with (PACKET / name).open('xb') as handle:
            handle.write(data)
        hashes[name] = row['sha256']
    write_new(PACKET / 'request-receipts-v1.json', {
        'status': 'DESCRIPTION_REQUESTS_ONLY', 'raw_semantics': 'HTTP-decoded text saved as UTF-8; not wire bytes',
        'receipts': transferred['request_receipts']})
    for version in ('probe-v1', 'contracts-v1'):
        freeze = json.loads((LOCAL / (version + '.json')).read_text())
        write_new(PACKET / ('source-freeze-' + version + '.json'), freeze)
    write_new(PACKET / 'aggregate-transfer-v1.json', {
        'status': 'PASS_ALLOWLISTED_METADATA_AND_ENGINEERING_AGGREGATES', 'sha256': hashes,
        'activity_rows_included': False, 'full_protocol_text_included': False,
        'benchmark_task_or_gold_rows_included': False,
        'raw_responses_retained_privately_in_full_task_return': True})
    print(json.dumps({'status': 'PASS_ALLOWLISTED_METADATA_AGGREGATES', 'files': len(hashes),
                      'request_receipts': len(transferred['request_receipts'])}))


if __name__ == '__main__':
    main()
