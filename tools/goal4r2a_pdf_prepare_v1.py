"""Package an existing pure-Python PDF reader and owner input without installing."""

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = Path('C:/Users/User/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/Lib/site-packages')


def main():
    output = ROOT / '.local/goal4r2a-20261106-v1/pdf-input'
    output.mkdir(parents=True, exist_ok=True)
    files = [p for p in (SITE / 'pypdf').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    files += list((SITE / 'pypdf-6.10.0.dist-info/licenses').rglob('*'))
    files = [p for p in files if p.is_file()]
    archive = output / 'pypdf-6.10.0.zip'
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as handle:
        for path in sorted(files):
            handle.writestr(path.relative_to(SITE).as_posix(), path.read_bytes())
    pdf = ROOT / 'research/raw_data/external-benchmarks/mf-pcba-2023/metadata/ci2c01569.pdf'
    result = {'status': 'PREPARED_EXISTING_BUNDLED_READER_NO_INSTALL', 'reader_version': '6.10.0',
              'reader_source': 'Codex primary runtime 26.1104.11149',
              'reader_archive_bytes': archive.stat().st_size,
              'reader_archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
              'reader_files': len(files), 'license_files': [p.relative_to(SITE).as_posix() for p in files if 'licenses' in p.parts],
              'owner_pdf_bytes': pdf.stat().st_size, 'owner_pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
              'owner_pdf_local': str(pdf.relative_to(ROOT)), 'pdf_contents_read_locally': False}
    if not result['license_files']:
        raise ValueError('Reader license must accompany copied sources')
    target = ROOT / 'docs/evidence/goal4r2a-20261106-v1/pdf-tools-intake-v1.json'
    with target.open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
