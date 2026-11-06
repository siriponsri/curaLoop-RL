"""Parse only published assay-ID/version metadata; no activity-row ingestion."""

import argparse
import hashlib
import json
import os
import re
import resource
import threading
import time
from datetime import date, datetime, timezone
from pathlib import Path

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
            if (time.process_time() - cpu > 120 or time.monotonic() - start > 600
                    or datetime.now(timezone.utc) >= datetime(2026, 11, 6, 11, 57, 53, tzinfo=timezone.utc)):
                os._exit(124)
    threading.Thread(target=watch, daemon=True).start()
    status = 'FAIL'
    try:
        manifest = json.loads((ROOT / (args.bundle + '.json')).read_text())
        for row in manifest['files']:
            assert hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256']
        registry = json.loads((ROOT / 'research/manifests/goal4r2a_mfpcba_metadata_v1.json').read_text())
        expected_pairs = set()
        for script in registry['source_script_names']:
            ids = script.removesuffix('.sh').split('-')
            expected_pairs.add((ids[-1], ids[0]))
        toc_path = ROOT / 'runs/si-toc-v1/selected-pages.json'
        table_path = ROOT / 'runs/si-metadata-v1/selected-pages.json'
        toc, pages = json.loads(toc_path.read_text()), json.loads(table_path.read_text())
        pairs = []
        for line in toc['3'].splitlines():
            match = re.fullmatch(r'(\d+)\s+(-|\d+)\s+\d[\d,]*(?:\s+.+)', line.strip())
            if match:
                sd, dr = match.groups()
                pairs.append((sd, sd if dr == '-' else dr))
        if len(pairs) != 60 or len(set(pairs)) != 60 or set(pairs) != expected_pairs:
            raise ValueError('Published Table S2 stage pairs differ from source definitions')
        versions = []
        for number in ('46', '47'):
            for line in pages[number].splitlines():
                match = re.fullmatch(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d{4})\s+(\d{1,2})\s+(\d{1,2})', line.strip())
                if match:
                    aid, version, revision, year, month, day = map(int, match.groups())
                    versions.append({'aid': str(aid), 'version': version, 'revision': revision,
                                     'last_modified': date(year, month, day).isoformat(),
                                     'source_location': 'SI Table S19, PDF page ' + number})
        expected_aids = {aid for pair in expected_pairs for aid in pair}
        if len(versions) != len({r['aid'] for r in versions}) or {r['aid'] for r in versions} != expected_aids:
            raise ValueError('Table S19 does not cover each defined AID exactly once')
        proof = json.loads((ROOT / 'docs/evidence/goal4r2a-20261106-v1/si-tools-intake-v1.json').read_text())
        result = {'status': 'PASS_PUBLISHED_STAGE_PAIRS_AND_VERSION_METADATA',
                  'paper_doi': '10.1021/acs.jcim.2c01569', 'si_pdf_sha256': proof['owner_pdf_sha256'],
                  'published_stage_pairs_checked': len(pairs), 'unique_aids_with_version_revision_date': len(versions),
                  'source_names_corroborated_by_table_s2': True, 'versions': sorted(versions, key=lambda r: int(r['aid'])),
                  'input_text_sha256': {p.name + ':' + p.parent.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                        for p in (toc_path, table_path)},
                  'actual_retrieved_assay_rows_match_published_versions': 'NOT_RUN_NO_ACTIVITY_ROWS',
                  'biological_groups_certified': 0, 'pilot_datasets_cleared': 0,
                  'actual_eligible_count': 'UNKNOWN', 'activity_rows_read': False,
                  'source_code_paper_reconstruction_differences_resolved': False}
        (output / 'si-metadata-audit.json').write_text(json.dumps(result, indent=2) + '\n')
        status = 'PASS'
        print(json.dumps({k: v for k, v in result.items() if k != 'versions'}))
    finally:
        done.set()
        receipt = {'status': status, 'cpu_seconds': time.process_time() - cpu,
                   'wall_seconds': time.monotonic() - start, 'cpu_affinity': [cpuid],
                   'start_utc': datetime.fromtimestamp(time.time() - (time.monotonic() - start), timezone.utc).isoformat(),
                   'finish_utc': datetime.now(timezone.utc).isoformat(), 'cpu_ceiling': 120, 'wall_ceiling': 600}
        with (output / 'resources.json').open('x') as handle:
            json.dump(receipt, handle, indent=2)


if __name__ == '__main__':
    main()
