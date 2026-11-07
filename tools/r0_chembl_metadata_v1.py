"""Bounded, single-response metadata retrieval for the released phase R0.

Reuses only the generic OS limiter method of resource_guard_v1.Guard; its
historical deadline/constructor is never invoked or modified. This phase has
its own explicit deadline, reservations and fresh receipts.
"""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

from resource_guard_v1 import Guard as HistoricalGuard

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/r0-chembl-20261107-v1'
DEADLINE = datetime(2026, 11, 7, 9, 43, 17, tzinfo=timezone.utc)
MAX_RESPONSE = 2 * 1024**2
MAX_TOTAL = 16 * 1024**2
ALLOWED = {
    'chembl35-directory': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/',
    'chembl35-license': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/LICENSE',
    'chembl35-readme': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/README',
    'chembl35-checksums': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/checksums.txt',
    'chembl35-schema': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/schema_documentation.txt',
    'chembl35-attribution': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_35/REQUIRED.ATTRIBUTION',
    'chembl-current-status': 'https://www.ebi.ac.uk/chembl/api/data/status.json',
    'chembl37-status-final': 'https://www.ebi.ac.uk/chembl/api/data/status.json',
    'chembl37-directory': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/',
    'chembl37-readme': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/README',
    'chembl37-license': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/LICENSE',
    'chembl37-schema': 'https://ftp.ebi.ac.uk/pub/databases/chembl/ChEMBLdb/releases/chembl_37/schema_documentation.txt',
    'chembl37-B-ids': 'https://www.ebi.ac.uk/chembl/api/data/assay.json?assay_type=B&confidence_score=9&src_id=1&limit=25&order_by=assay_chembl_id&only=assay_chembl_id,document_chembl_id,target_chembl_id,assay_type,confidence_score,src_id',
    'chembl37-F-ids': 'https://www.ebi.ac.uk/chembl/api/data/assay.json?assay_type=F&confidence_score=9&src_id=1&limit=25&order_by=assay_chembl_id&only=assay_chembl_id,document_chembl_id,target_chembl_id,assay_type,confidence_score,src_id',
}
followup_registry = PRIVATE / 'allowed-followup-v1.json'
if followup_registry.exists():
    extra = json.loads(followup_registry.read_text(encoding='utf-8'))
    for name, url in extra.items():
        parsed = urllib.parse.urlparse(url)
        if (parsed.scheme != 'https' or parsed.netloc != 'www.ebi.ac.uk' or
            parsed.path not in ('/chembl/api/data/assay.json', '/chembl/api/data/document.json',
                                '/chembl/api/data/target.json', '/chembl/api/data/status.json',
                                '/chembl/api/data/target_component.json',
                                '/chembl/api/data/protein_classification.json')):
            raise RuntimeError('Invalid follow-up metadata URL')
        ALLOWED[name] = url

def now():
    return datetime.now(timezone.utc).isoformat()

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

class MetadataGuard(HistoricalGuard):
    def __init__(self, receipt):
        remaining = (DEADLINE - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            raise RuntimeError('R0 deadline exhausted')
        self.receipt = receipt
        self.started, self.cpu = time.monotonic(), time.process_time()
        self.wall_limit, self.cpu_limit = min(30.0, remaining), 60
        self.ram_limit = 256 * 1024**2
        self.completed, self.lock = threading.Event(), threading.Lock()
        self.cpu_id = self._limit_process()
        self.base = {'schema_version': 'curaloop.r0.metadata-resource.v1',
                     'pid': os.getpid(), 'start_utc': now(),
                     'deadline_utc': DEADLINE.isoformat(),
                     'cpu_affinity': [self.cpu_id],
                     'wall_limit_seconds': self.wall_limit,
                     'cpu_limit_seconds': self.cpu_limit,
                     'memory_limit_bytes': self.ram_limit,
                     'descendant_processes_allowed': False,
                     'python': sys.version,
                     'worker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                     'os_limiter_sha256': hashlib.sha256((ROOT / 'tools/resource_guard_v1.py').read_bytes()).hexdigest()}
        self._write('RUNNING')
        threading.Thread(target=self._watch, daemon=True).start()

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise RuntimeError('STOP_UNKNOWN_REDIRECT')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', choices=sorted(ALLOWED))
    args = parser.parse_args()
    PRIVATE.mkdir(parents=True, exist_ok=True)
    lock_path = PRIVATE / 'worker.lock'
    descriptor = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(descriptor)
    guard = None
    ledger_path = PRIVATE / 'ledger.json'
    try:
        ledger = (json.loads(ledger_path.read_text(encoding='utf-8'))
                  if ledger_path.exists() else {
                      'id': 'r0-chembl-20261107-v1', 'release_utc': '2026-11-07T05:43:17Z',
                      'deadline_utc': DEADLINE.isoformat(), 'cpu_cap_seconds': 1800,
                      'utility_charge_seconds': 300, 'worker_reserved_seconds': 0,
                      'decoded_bytes': 0, 'attempts': [], 'stopped_sources': []})
        if ledger.get('status') == 'CLOSED':
            raise RuntimeError('R0 source intake is CLOSED; new owner release required')
        if args.source in ledger['stopped_sources']:
            raise RuntimeError('Source STOP retained; no retry')
        if len(ledger['attempts']) >= 32 or ledger['decoded_bytes'] >= MAX_TOTAL:
            raise RuntimeError('Source budget exhausted')
        if ledger['utility_charge_seconds'] + ledger['worker_reserved_seconds'] + 60 > 1800:
            raise RuntimeError('CPU admission exhausted')
        if (DEADLINE - datetime.now(timezone.utc)).total_seconds() <= 0:
            raise RuntimeError('Absolute deadline exhausted')
        index = len(ledger['attempts']) + 1
        stem = f'{index:03d}-{args.source}'
        record = {'id': stem, 'source': args.source, 'url': ALLOWED[args.source],
                  'started_utc': now(), 'status': 'RESERVED', 'decoded_bytes': 0,
                  'reserved_cpu_seconds': 60}
        ledger['attempts'].append(record)
        ledger['worker_reserved_seconds'] += 60
        save(ledger_path, ledger)
        code_bytes = Path(__file__).read_bytes()
        code_path = PRIVATE / 'code' / (hashlib.sha256(code_bytes).hexdigest() + '.py')
        code_path.parent.mkdir(exist_ok=True)
        if not code_path.exists():
            code_path.write_bytes(code_bytes)
        guard = MetadataGuard(PRIVATE / f'{stem}-resource.json')
        # Record a source attempt only after the OS limiter is installed.
        time.sleep(1)
        request = urllib.request.Request(ALLOWED[args.source], headers={
            'User-Agent': 'CuraLoop-R0-metadata/1.0', 'Accept-Encoding': 'identity'})
        opener = urllib.request.build_opener(NoRedirect())
        record['status'] = 'STARTED'
        save(ledger_path, ledger)
        body = bytearray()
        with opener.open(request, timeout=25) as response:
            record['http_status'] = response.status
            record['content_type'] = response.headers.get('Content-Type', '')
            if response.headers.get('Content-Encoding', 'identity') != 'identity':
                raise RuntimeError('STOP_UNEXPECTED_ENCODING')
            length = response.headers.get('Content-Length')
            if length and int(length) > MAX_RESPONSE:
                raise RuntimeError('STOP_RESPONSE_SIZE')
            expected = ('application/json' if '/api/data/' in request.full_url else
                        'text/html' if args.source.endswith('directory') else 'text/plain')
            allowed_type = (expected in record['content_type'] or
                            (not args.source.endswith('directory') and
                             record['content_type'] in ('', 'application/octet-stream')))
            if not allowed_type:
                raise RuntimeError('STOP_UNEXPECTED_METADATA_CONTENT_TYPE')
            while True:
                part = response.read1(min(65536, MAX_RESPONSE + 1 - len(body)))
                if not part:
                    break
                body.extend(part)
                record['decoded_bytes'] += len(part)
                ledger['decoded_bytes'] += len(part)
                save(ledger_path, ledger)
                if len(body) > MAX_RESPONSE or ledger['decoded_bytes'] > MAX_TOTAL:
                    raise RuntimeError('STOP_BYTE_CAP')
        text = body.decode('utf-8')
        if '\x00' in text:
            raise RuntimeError('STOP_NON_TEXT_METADATA')
        raw_path = PRIVATE / f'{stem}.html'
        raw_path.write_bytes(body)
        record.update(status='PASS_METADATA_LISTING', finished_utc=now(),
                      sha256=hashlib.sha256(body).hexdigest(), raw_path=str(raw_path.relative_to(ROOT)))
        save(ledger_path, ledger)
        guard.finish('PASS_METADATA_LISTING', bytes=len(body))
        # Listing names are metadata; no linked data file is fetched.
        listing = body.decode('utf-8', errors='replace')
        output = {'record': record, 'links': re.findall(r'href="([^"]+)"', listing)}
        if args.source.endswith('status'):
            output['service_status'] = json.loads(text)
        elif '/api/data/' in request.full_url:
            payload = json.loads(text)
            output['collection_fields'] = sorted(payload)
            output['record_counts'] = {key: len(value) for key, value in payload.items() if isinstance(value, list)}
            output['record_field_names'] = {key: sorted(value[0]) for key, value in payload.items() if isinstance(value, list) and value and isinstance(value[0], dict)}
        print(json.dumps(output, indent=2))
    except Exception as exc:
        if 'record' in locals():
            record.update(status='STOP', error_type=type(exc).__name__, error=str(exc), finished_utc=now())
            if isinstance(exc, urllib.error.HTTPError):
                record['http_status'] = exc.code
            if record['status'] == 'STOP' and args.source not in ledger['stopped_sources']:
                ledger['stopped_sources'].append(args.source)
            save(ledger_path, ledger)
            if guard is not None:
                guard.finish('STOP', error_type=type(exc).__name__)
        print(json.dumps({'status': 'STOP', 'error_type': type(exc).__name__, 'error': str(exc)}, indent=2))
        return 2
    finally:
        lock_path.unlink(missing_ok=True)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
