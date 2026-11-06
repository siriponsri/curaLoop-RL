"""Collect published SI metadata aggregates without republishing PDF text."""

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
files={'si-metadata-audit-v1.json':root/'runs/si-audit-v1/si-metadata-audit.json',
       'si-toc-inspection-v1.json':root/'runs/si-toc-v1/pdf-inspection.json',
       'si-selected-inspection-v1.json':root/'runs/si-metadata-v1/pdf-inspection.json',
       'remote-launch-ledger-v2.json':root/'launch-ledger.json'}
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
        assert hashlib.sha256(data).hexdigest() == row['sha256']
        with (PACKET / name).open('xb') as handle:
            handle.write(data)
        hashes[name] = row['sha256']
    for version in ('v2', 'v3'):
        write_new(PACKET / ('source-freeze-' + version + '.json'), json.loads((LOCAL / ('bundle-' + version + '.json')).read_text()))
    write_new(PACKET / 'si-aggregate-transfer-v1.json', {'status': 'PASS_PUBLISHED_METADATA_TRANSFER',
              'sha256': hashes, 'raw_pdf_or_text_republished': False, 'activity_rows_included': False})
    print(json.dumps({'status': 'PASS_PUBLISHED_METADATA_TRANSFER', 'files': len(files)}))


if __name__ == '__main__':
    main()
