"""Transfer only the checksummed owner PDF and existing reader to the new task."""

import hashlib
import json
import subprocess

from tools.goal4r2a_remote_v1 import HOST, LOCAL, OPTIONS, PACKET, REMOTE, ROOT, write_new
from tools.remote_goal4_control_v1 import ssh_script


def main():
    proof = json.loads((PACKET / 'pdf-tools-intake-v1.json').read_text())
    pdf = ROOT / proof['owner_pdf_local']
    archive = LOCAL / 'pdf-input/pypdf-6.10.0.zip'
    assert hashlib.sha256(pdf.read_bytes()).hexdigest() == proof['owner_pdf_sha256']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == proof['reader_archive_sha256']
    source = "import os; from pathlib import Path; root=Path(" + repr(REMOTE) + "); assert root.resolve()==root and root.stat().st_uid==os.getuid(); (root/'metadata-input').mkdir(mode=0o700,exist_ok=False)"
    ssh_script(source)
    subprocess.run(['scp', *OPTIONS, str(pdf), HOST + ':' + REMOTE + '/metadata-input/owner.pdf'], check=True)
    subprocess.run(['scp', *OPTIONS, str(archive), HOST + ':' + REMOTE + '/metadata-input/pypdf-6.10.0.zip'], check=True)
    write_new(PACKET / 'pdf-transfer-v1.json', {'status': 'PASS_PRIVATE_PDF_AND_READER_TRANSFER',
              'owner_pdf_sha256': proof['owner_pdf_sha256'],
              'reader_sha256': proof['reader_archive_sha256'], 'host_dependency_installation': False})
    print('PASS: checksummed owner input and existing reader transferred; no activity tables.')


if __name__ == '__main__':
    main()
