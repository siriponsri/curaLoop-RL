"""Download private reading copies from the fixed literature register, not data."""

import argparse
import concurrent.futures
import hashlib
import html
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'docs/02_literature/literature_manifest.json'
ROOM = Path.home() / 'Documents/ChatGPT/Drug Discovery/literature'
HOSTS = {'arxiv.org', 'papers.neurips.cc', 'proceedings.mlr.press', 'www.jmlr.org',
         'pmc-oa-opendata.s3.amazonaws.com', 'www.nature.com'}


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    with path.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False)
        f.write('\n')


def validate(path, record):
    with path.open('rb') as f:
        assert f.read(5) == b'%PDF-', 'NOT_A_PDF'
    with fitz.open(path) as doc:
        assert not doc.is_encrypted and 1 <= len(doc) <= 1000
        first = '\n'.join(doc[i].get_text() for i in range(min(2, len(doc))))
        page_count = len(doc)
    def words(value):
        return set(re.findall('[a-z]{3,}', value.lower()))
    expected = words(record['title']) - {'the', 'and', 'for', 'with', 'from', 'using', 'through'}
    overlap = len(expected & words(first)) / max(1, len(expected))
    digest = sha(path)
    assert overlap >= .60, 'PAPER_TITLE_REQUIRES_REVIEW'
    result = {'sha256': digest, 'bytes': path.stat().st_size, 'pages': page_count,
              'expected_pages_match': page_count == record['pages'],
              'historical_hash_match': digest == record['pdf_sha256'],
              'title_word_overlap': overlap, 'pdf_structure_and_title': 'PASS'}
    if digest == record['pdf_sha256']:
        result['status'] = 'PASS_EXACT_REGISTERED_PDF'
    else:
        result['status'] = 'VALID_PDF_DIFFERENT_BYTES_REVIEW_VERSION'
    return result


def download(record):
    name = record['private_reading_filename']
    assert Path(name).name == name and name.endswith('.pdf')
    result = {'id': record['id'], 'title': record['title'], 'filename': name,
              'historical_sha256': record['pdf_sha256'], 'attempts': []}
    url = record.get('download_url')
    if not url:
        return dict(result, status='AWAITING_LAWFUL_SOURCE_OR_OWNER_COPY',
                    landing=record.get('landing'), note='Historical supplied copy not found locally; no source invented')
    parsed = urlparse(url)
    assert parsed.scheme == 'https' and parsed.hostname in HOSTS and not parsed.username
    if parsed.hostname == 'arxiv.org':
        version = re.search(r'(\d{4}\.\d{4,5}v\d+)', record['version_note'])
        assert version
        url = 'https://arxiv.org/pdf/' + version.group(1)
    # Legacy cookie-error query text is not a reusable document address.
    if parsed.hostname == 'www.nature.com':
        url = url.split('?', 1)[0]
    result['requested_url'] = url
    target = ROOM / 'pdfs' / name
    assert not target.exists()
    limit = min(64 * 1024**2, max(12 * 1024**2, record['pdf_bytes'] * 2))
    max_time = min(300, max(70, int(record['pdf_bytes'] / 65000) + 45))
    for attempt in range(1, 3):
        partial = ROOM / 'partials' / (record['id'] + '-attempt-' + str(attempt) + '.part')
        cmd = ['rtk', 'proxy', 'curl.exe', '--location', '--fail', '--silent', '--show-error',
               '--connect-timeout', '10', '--max-time', str(max_time), '--max-filesize', str(limit),
               '--output', str(partial), '--write-out',
               'http=%{http_code} bytes=%{size_download} seconds=%{time_total}', url]
        started = time.monotonic()
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=max_time + 15)
            info = {'attempt': attempt, 'exit_code': r.returncode,
                    'transport': r.stdout.decode(errors='replace'),
                    'error': r.stderr.decode(errors='replace')[-1800:],
                    'elapsed_seconds': time.monotonic() - started,
                    'partial_bytes': partial.stat().st_size if partial.exists() else 0}
        except subprocess.TimeoutExpired:
            info = {'attempt': attempt, 'exit_code': 'PARENT_TIMEOUT',
                    'elapsed_seconds': time.monotonic() - started,
                    'partial_bytes': partial.stat().st_size if partial.exists() else 0}
        result['attempts'].append(info)
        save(ROOM / 'logs' / (record['id'] + '-attempt-' + str(attempt) + '.json'), info)
        if info['exit_code'] == 0:
            try:
                verified = validate(partial, record)
                partial.replace(target)
                return dict(result, **verified)
            except Exception as exc:
                return dict(result, status='FAIL_PDF_OR_IDENTITY_VERIFICATION', error=str(exc))
        # Never retry a denied, rate-limited or missing resource. One retry is
        # reserved for a transport failure, not access-control circumvention.
        if any('http=' + code in info.get('transport', '') for code in ('401', '403', '404', '429')):
            break
        if info['exit_code'] not in (28, 35, 56, 'PARENT_TIMEOUT'):
            break
    return dict(result, status='DOWNLOAD_FAILED_PRESERVED_ERROR')


def write_index(records, source_sha):
    summary = {'created_utc': datetime.now(timezone.utc).isoformat(), 'source_manifest': str(SOURCE),
               'source_manifest_sha256': source_sha, 'main_expected': 28, 'supplements_expected': 1,
               'private_reading_only_no_pdf_redistribution_in_git': True, 'records': records}
    save(ROOM / 'download-status.json', summary)
    rows = []
    for row in sorted(records, key=lambda x: x['id']):
        title = html.escape(row['title'])
        if (ROOM / 'pdfs' / row['filename']).exists():
            title = '<a href="pdfs/' + html.escape(row['filename']) + '">' + title + '</a>'
        rows.append('<tr><td>' + row['id'] + '</td><td>' + title + '</td><td>' +
                    html.escape(row['status']) + '</td></tr>')
    body = ('<!doctype html><html lang="en"><meta charset="utf-8"><title>CuraLoop literature reading room</title>'
            '<style>body{font:16px system-ui;max-width:1100px;margin:48px auto;padding:0 24px;color:#20242b}'
            'table{border-collapse:collapse;width:100%}td,th{text-align:left;padding:12px;border-bottom:1px solid #ddd}'
            'a{color:#8b482f}td:last-child{font-size:12px}</style><h1>CuraLoop literature reading room</h1>'
            '<p>Private reading copies. Downloaded files are distinct from papers read or independently reproduced.</p>'
            '<p>Expected: 28 main papers and one supplement. Original historical register is preserved.</p>'
            '<table><thead><tr><th>ID</th><th>Paper</th><th>Current status</th></tr></thead><tbody>' +
            ''.join(rows) + '</tbody></table></html>')
    (ROOM / 'OPEN-READING-ROOM.html').write_text(body, encoding='utf-8', newline='\n')


def main():
    global ROOM
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOM,
                        help='A fresh reading directory outside this repository')
    ROOM = parser.parse_args().output.resolve()
    if ROOM.is_relative_to(ROOT):
        parser.error('Reading copies must remain outside the public repository')
    # One local core; two network transfers, not two model-training workers.
    try:
        import psutil
        process = psutil.Process()
        process.cpu_affinity([process.cpu_affinity()[0]])
    except (ImportError, AttributeError):
        pass
    ROOM.mkdir(exist_ok=False)
    for name in ('pdfs', 'partials', 'logs', 'extracted'):
        (ROOM / name).mkdir()
    raw = SOURCE.read_bytes()
    source_sha = hashlib.sha256(raw).hexdigest()
    (ROOM / 'source-literature-manifest.json').write_bytes(raw)
    manifest = json.loads(raw)
    records = manifest['records'] + manifest.get('supplemental_records', [])
    assert len(manifest['records']) == 28 and len(records) == 29
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(download, row) for row in records]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            results.append(row)
            write_index(results, source_sha)
            print(json.dumps({'id': row['id'], 'status': row['status'], 'bytes': row.get('bytes'),
                              'completed_records': len(results)}), flush=True)
    assert sha(SOURCE) == source_sha
    counts = {status: sum(r['status'] == status for r in results) for status in sorted({r['status'] for r in results})}
    print(json.dumps({'status': 'INITIAL_DOWNLOAD_PASS_COMPLETE', 'counts': counts, 'room': str(ROOM)}), flush=True)


if __name__ == '__main__':
    main()
