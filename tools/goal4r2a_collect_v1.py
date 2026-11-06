"""Copy only allowlisted engineering aggregates and synthetic demo outputs."""

import base64
import hashlib
import json

from tools.goal4r2a_remote_v1 import LOCAL, PACKET, REMOTE, write_new
from tools.remote_goal4_control_v1 import ssh_script


def main():
    source = '''
import base64,hashlib,json
from pathlib import Path
root=Path(REMOTE)
run=root/'runs/cases-v1'
results=json.loads((run/'results.json').read_text())
demo=Path(results['demo']['report']['folder'])
assert demo.resolve()==demo and demo.is_relative_to(run)
files={'case-results-v1.json':run/'results.json','case-resources-v1.json':run/'resources.json',
       'case-checks-v1.log':run/'tests.log','metadata-audit-v1.json':run/'metadata-audit.json',
       'demo-report.md':demo/'report.md','demo-bundle.json':demo/'bundle.json','demo-manifest.json':demo/'manifest.json',
       'remote-launch-ledger-v1.json':root/'launch-ledger.json','pdf-inspection-v1.json':root/'runs/pdf-v1/pdf-inspection.json'}
out={}
for name,path in files.items():
 assert path.is_file() and not path.is_symlink() and path.stat().st_size<512*1024
 data=path.read_bytes()
 out[name]={'sha256':hashlib.sha256(data).hexdigest(),'base64':base64.b64encode(data).decode()}
print(json.dumps(out))
'''
    files = json.loads(ssh_script('REMOTE=' + repr(REMOTE) + '\n' + source))
    hashes = {}
    for name, row in files.items():
        data = base64.b64decode(row['base64'], validate=True)
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            raise ValueError('Transferred aggregate checksum differs')
        with (PACKET / name).open('xb') as handle:
            handle.write(data)
        hashes[name] = row['sha256']
    freeze = json.loads((LOCAL / 'bundle-v1.json').read_text())
    write_new(PACKET / 'source-freeze-v1.json', freeze)
    write_new(PACKET / 'aggregate-transfer-v1.json', {'status': 'PASS_ALLOWLISTED_ENGINEERING_AGGREGATES', 'sha256': hashes,
              'activity_rows_included': False, 'owner_pdf_text_included': False})
    print(json.dumps({'status': 'PASS_ALLOWLISTED_ENGINEERING_AGGREGATES', 'files': len(hashes)}, indent=2))


if __name__ == '__main__':
    main()
