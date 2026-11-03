#!/usr/bin/env python3
"""Download a small curated list of license-checked original OA PDFs via the
official NCBI PMC Open Access service.

This is NOT a site scraper. It uses the PMC OA web service, honors the record's
license and available retraction metadata, throttles requests, and logs exact download and
SHA256 results. PDFs outside the OA subset remain link-only.

Example:
    python scripts/fetch_oa_papers.py --manifest papers/papers_manifest.json --out papers/pdf
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import tarfile
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

import requests

OA_SERVICE = 'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi'
MAX_ARTICLE_BYTES = 65 * 1024 * 1024
MAX_PACKAGE_BYTES = 100 * 1024 * 1024


def permission_ok(license_name: str, include_nc: bool = False) -> bool:
    """Conservative automated redistribution gate; check article-specific terms."""
    name = ' '.join(license_name.upper().replace('_', '-').split())
    if 'CC0' in name or 'CC ZERO' in name:
        return True
    # Exact classes only: BY-SA or unrecognized combinations need manual review.
    if re.fullmatch(r'CC BY(?: [1-9][0-9]*(?:\.[0-9]+)?)?', name):
        return True
    if re.fullmatch(r'CC BY-NC(?: [1-9][0-9]*(?:\.[0-9]+)?)?', name):
        return bool(include_nc)
    return False


def official_url(asset: str) -> str:
    """Convert PMC OA `ftp://` URLs into official https:// URLs."""
    raw = asset.strip().lstrip('/')
    if raw.startswith('ftp://') or raw.startswith('https://'):
        parsed = urlsplit(raw)
        if parsed.hostname != 'ftp.ncbi.nlm.nih.gov':
            raise ValueError('OA service returned unexpected asset host')
        if not parsed.path.startswith('/pub/pmc/'):
            raise ValueError('Unexpected asset path')
        return 'https://ftp.ncbi.nlm.nih.gov' + parsed.path
    raise ValueError('No official PMC asset URL')


def fetch_bytes(session: requests.Session, url: str, max_bytes: int, timeout: int) -> bytes:
    chunks = []
    length = 0
    with session.get(url, stream=True, timeout=timeout) as response:
        response.raise_for_status()
        # A redirect should not move to an unrelated download host.
        destination = urlsplit(response.url)
        if destination.hostname not in {'ftp.ncbi.nlm.nih.gov', 'www.ncbi.nlm.nih.gov'}:
            raise ValueError('Unexpected redirect host: ' + str(destination.hostname))
        for chunk in response.iter_content(chunk_size=128 * 1024):
            if not chunk:
                continue
            length += len(chunk)
            if length > max_bytes:
                raise ValueError('Download exceeds configured maximum bytes')
            chunks.append(chunk)
    return b''.join(chunks)


def pdf_from_archive(data: bytes) -> bytes:
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        pdfs = [m for m in archive.getmembers() if m.isfile() and m.name.lower().endswith('.pdf')]
        if not pdfs:
            raise ValueError('No PDF in official OA package')

        def preference(m: tarfile.TarInfo) -> tuple[int, int]:
            filename = m.name.lower()
            unwanted = ('supplement', 'additional', 'esm', 'supporting', 'si_', 'appendix')
            return (sum(token in filename for token in unwanted), len(filename))

        for member in sorted(pdfs, key=preference):
            if member.size > MAX_ARTICLE_BYTES:
                continue
            obj = archive.extractfile(member)
            if obj is None:
                continue
            content = obj.read(MAX_ARTICLE_BYTES + 1)
            if valid_pdf(content):
                return content
    raise ValueError('No valid article PDF in OA package')


def valid_pdf(data: bytes) -> bool:
    return len(data) >= 2048 and b'%PDF-' in data[:1024] and b'%%EOF' in data[-8192:]


def lookup(session: requests.Session, pmcid: str, timeout: int) -> dict:
    response = session.get(OA_SERVICE, params={'id': pmcid, 'tool': 'curaloop_rl_oa_research_pack'}, timeout=timeout)
    response.raise_for_status()
    root = ET.fromstring(response.content)
    record = root.find('.//record')
    if record is None:
        raise ValueError('No OA service record, PDF is link-only')
    links = {link.attrib.get('format'): link.attrib.get('href') for link in record.findall('./link')}
    return {
        'license': record.attrib.get('license', 'unknown'),
        'retracted': record.attrib.get('retracted', 'unknown'),
        'links': links,
    }


def fetch_pdf(session: requests.Session, asset_links: dict, timeout: int) -> tuple[bytes, str]:
    reasons = []
    for asset_type in ('pdf', 'tgz'):
        href = asset_links.get(asset_type)
        if not href:
            continue
        url = official_url(href)
        try:
            data = fetch_bytes(session, url, MAX_ARTICLE_BYTES if asset_type == 'pdf' else MAX_PACKAGE_BYTES, timeout)
            pdf = data if asset_type == 'pdf' else pdf_from_archive(data)
            if not valid_pdf(pdf):
                raise ValueError('Asset is not a valid original PDF')
            return pdf, url
        except (requests.RequestException, OSError, ValueError, tarfile.TarError) as exc:
            reasons.append(f'{asset_type}: {exc}')
    raise ValueError('; '.join(reasons) or 'No PDF/tgz OA links')


def run() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=Path('papers/papers_manifest.json'))
    parser.add_argument('--out', type=Path, default=Path('papers/pdf'))
    parser.add_argument('--include-nc', action='store_true', help='Include noncommercial CC BY-NC licensed originals')
    parser.add_argument('--limit', type=int, default=0, help='Limit number of auto-eligible articles for a smoke test')
    parser.add_argument('--dry-run', action='store_true', help='Print references without sending network requests')
    parser.add_argument('--timeout', type=int, default=40)
    parser.add_argument('--pause', type=float, default=1.0, help='Seconds between OA article requests')
    args = parser.parse_args()
    if args.timeout <= 0 or args.pause < 0 or args.limit < 0:
        parser.error('Positive timeout and nonnegative pause/limit required')

    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    papers = manifest['papers']
    eligible = [p for p in papers if p.get('auto_fetch') and p.get('pmcid')]
    if args.limit:
        eligible = eligible[:args.limit]
    if args.dry_run:
        print(f'DRY RUN: {len(eligible)} OA candidates; {len(papers)} references total')
        for p in eligible:
            print(p['id'], p['pmcid'], p['article_url'])
        print('No PDFs downloaded and no rights checked in dry-run mode.')
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update({'User-Agent': 'CuraLoop-RL-OpenAccessResearch/0.1 (single-article rights-aware downloader)'})
    report = {
        'NOTICE': 'Downloaded items are for local reading only by default. License and retraction metadata are best-effort; manually verify article identity, status and redistribution terms before sharing any binary.',
        'started_at_utc': datetime.now(timezone.utc).isoformat(),
        'manifest': str(args.manifest),
        'license_policy': 'CC0 and CC BY allowed; CC BY-NC allowed only with --include-nc; ND and unidentified licenses skipped',
        'results': [],
    }
    for i, p in enumerate(eligible):
        pid = p['id']
        name = f"{pid}_{p['pmcid']}.pdf"
        output = args.out / name
        row = {'id': pid, 'pmcid': p['pmcid'], 'article_url': p['article_url'], 'status': 'NOT_RUN'}
        try:
            detail = lookup(session, p['pmcid'], args.timeout)
            row['recorded_license'] = detail['license']
            row['retraction_status'] = detail['retracted']
            row['retraction_check_level'] = 'METADATA_ONLY_NOT_INDEPENDENTLY_VERIFIED'
            if str(detail['retracted']).lower() in ('yes', 'true'):
                row['status'] = 'SKIPPED_RETRACTED'
            elif not permission_ok(detail['license'], args.include_nc):
                row['status'] = 'SKIPPED_LICENSE'
            else:
                content, source = fetch_pdf(session, detail['links'], args.timeout)
                # Never overwrite a downloaded PDF with unrelated content.
                with tempfile.NamedTemporaryFile(dir=args.out, prefix='tmp_', suffix='.pdf', delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = Path(tmp.name)
                tmp_path.replace(output)
                row.update({'status': 'DOWNLOADED', 'file': str(output),
                            'sha256': hashlib.sha256(content).hexdigest(), 'size_bytes': len(content),
                            'source_asset_url': source})
        except (requests.RequestException, ET.ParseError, OSError, ValueError, KeyError, tarfile.TarError) as exc:
            row.update({'status': 'FAILED', 'error': str(exc)[:500]})
        report['results'].append(row)
        print(f"{pid} {row['status']}: {row.get('recorded_license', 'no license returned')}")
        if i < len(eligible) - 1:
            time.sleep(args.pause)

    report['ended_at_utc'] = datetime.now(timezone.utc).isoformat()
    report['downloaded_count'] = sum(x['status'] == 'DOWNLOADED' for x in report['results'])
    report['candidate_count'] = len(eligible)
    report_path = args.out.parent / 'download_report.json'
    report_path.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print('Report:', report_path, 'downloaded:', report['downloaded_count'])
    return 0 if report['downloaded_count'] else 1


if __name__ == '__main__':
    sys.exit(run())
