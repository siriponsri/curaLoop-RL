"""Resource-bounded first-page/source-identity inspection of an owner PDF."""

import argparse
import hashlib
import json
import os
import resource
import sys
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path('/home/chaw/curaloop-rl/goal4r2a-20261106-v1')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--attempt', required=True)
    parser.add_argument('--bundle', required=True)
    args = parser.parse_args()
    assert Path.cwd().resolve() == ROOT and ROOT.resolve() == ROOT and ROOT.stat().st_uid == os.getuid()
    assert args.attempt.replace('-', '').isalnum()
    output = ROOT / 'runs' / args.attempt
    output.mkdir(parents=True, exist_ok=False)
    start, cpu = time.monotonic(), time.process_time()
    cpuid = max(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {cpuid})
    os.nice(19)
    resource.setrlimit(resource.RLIMIT_CPU, (121, 122))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2, 512 * 1024**2))
    done = threading.Event()
    def watch():
        while not done.wait(.25):
            if (time.monotonic() - start >= 600 or time.process_time() - cpu >= 120
                    or datetime.now(timezone.utc) >= datetime(2026, 11, 6, 11, 57, 53, tzinfo=timezone.utc)):
                os._exit(124)
    threading.Thread(target=watch, daemon=True).start()
    status = 'FAIL'
    try:
        manifest = json.loads((ROOT / (args.bundle + '.json')).read_text())
        for row in manifest['files']:
            path = ROOT / row['path']
            if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
                raise ValueError('Source changed before PDF inspection')
        proof = json.loads((ROOT / 'docs/evidence/goal4r2a-20261106-v1/pdf-tools-intake-v1.json').read_text())
        inputs = ROOT / 'metadata-input'
        pdf, archive = inputs / 'owner.pdf', inputs / 'pypdf-6.10.0.zip'
        assert hashlib.sha256(pdf.read_bytes()).hexdigest() == proof['owner_pdf_sha256']
        assert hashlib.sha256(archive.read_bytes()).hexdigest() == proof['reader_archive_sha256']
        vendor = output / 'vendor'
        with zipfile.ZipFile(archive) as zipped:
            assert len(zipped.infolist()) == proof['reader_files'] <= 500
            assert len(set(zipped.namelist())) == len(zipped.namelist())
            assert sum(i.file_size for i in zipped.infolist()) < 10 * 1024**2
            for info in zipped.infolist():
                rel = PurePosixPath(info.filename)
                assert not rel.is_absolute() and '..' not in rel.parts and '\\' not in info.filename and not info.is_dir()
                path = vendor / info.filename
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open('xb') as handle:
                    handle.write(zipped.read(info))
        sys.dont_write_bytecode = True
        sys.path.insert(0, str(vendor))
        import pypdf
        assert pypdf.__version__ == '6.10.0'
        reader = pypdf.PdfReader(pdf)
        if reader.is_encrypted:
            raise ValueError('Encrypted input not permitted')
        # First page only: identify the supplied file before deciding what to inspect.
        first = reader.pages[0].extract_text()
        (output / 'first-page.txt').write_text(first, encoding='utf-8')
        result = {'status': 'PASS_FIRST_PAGE_IDENTITY_INSPECTION', 'pages': len(reader.pages),
                  'title': str(reader.metadata.title), 'pdf_sha256': proof['owner_pdf_sha256'],
                  'pages_extracted': [1], 'bulk_activity_tables_read': False,
                  'reader_version': pypdf.__version__, 'scientific_campaigns': 0}
        (output / 'pdf-inspection.json').write_text(json.dumps(result, indent=2) + '\n')
        status = 'PASS'
        print(json.dumps(result))
    finally:
        done.set()
        result = {'status': status, 'cpu_seconds': time.process_time() - cpu,
                  'wall_seconds': time.monotonic() - start, 'cpu_affinity': [cpuid],
                  'start_utc': datetime.fromtimestamp(time.time() - (time.monotonic() - start), timezone.utc).isoformat(),
                  'finish_utc': datetime.now(timezone.utc).isoformat(), 'cpu_ceiling': 120,
                  'wall_ceiling': 600, 'dependency_installation': 'NONE_EXISTING_BUNDLED_SOURCE_COPY'}
        with (output / 'resources.json').open('x') as handle:
            json.dump(result, handle, indent=2)


if __name__ == '__main__':
    main()
