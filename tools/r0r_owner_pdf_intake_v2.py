"""Fixed owner-three-paper intake; no network, purchase, polling or retry."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import re
import unicodedata
from r0r_chembl_core_v1 import Guard, PRIVATE, ROOT, save, DEADLINE
from r0r_owner_methods_mask_v2 import extract_pdf, safety_checks


def run(filename, guard_factory=Guard, local_resource_repair=False):
    metadata = json.loads((PRIVATE/'owner-file-metadata-v1.json').read_text())['records']
    matches = [row for row in metadata if row['filename'] == filename]
    if len(matches) != 1:
        raise ValueError('Only the five owner-supplied files are admitted')
    expected = matches[0]
    path = ROOT/expected['source_path']
    assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve())
    assert 0 < path.stat().st_size <= 4*1024**2
    book = json.loads((PRIVATE/'ledger.json').read_text())
    assert book['status'] == 'ACTIVE' and datetime.now(timezone.utc) < DEADLINE
    assert book['worker_reserved_seconds'] + book['utility_charge_seconds'] + 20 <= 3600
    assert book['decoded_bytes'] + path.stat().st_size <= 32*1024**2
    previous = [row for row in book.get('local_source_intakes', []) if row.get('source_path') == expected['source_path']]
    if previous:
        # This is an operator-controlled repair of local processing, never a
        # network-source retry. Keep the failed attempt and its charge intact.
        assert local_resource_repair and len(previous) == 1
        assert previous[0]['status'] == 'FAILED_RESOURCE_LIMIT_NO_MASKED_OUTPUT'
        assert previous[0]['source_sha256'] == expected['source_sha256']
        assert 'output_path' not in previous[0]
        failed = json.loads((PRIVATE/previous[0]['failure_receipt']).read_text())
        assert failed['status'] == 'FAIL_RESOURCE_LIMIT'
    previous_extracts = sum(row['kind'] in ('methods_xml', 'methods_pdf') for row in book['attempts'])
    assert previous_extracts + len(book.get('local_source_intakes', [])) < 12
    guard = guard_factory('owner-v2-'+filename.replace('.pdf',''), wall=60, cpu_seconds=20)
    record = {key: expected[key] for key in ['filename','document_id','source_part','expected_doi','source_path']}
    record.update(status='RESERVED', started_utc=datetime.now(timezone.utc).isoformat(),
                  cpu_reserved_seconds=20, owner_supplied=True,
                  rights_scope='Internal methods review only; redistribution/commercial use not inferred')
    if previous:
        record.update(local_processing_repair=True,
                      previous_failure_receipt=previous[0]['failure_receipt'],
                      network_source_retry=False, previous_charge_retained=True)
    book.setdefault('local_source_intakes', []).append(record)
    book['worker_reserved_seconds'] += 20
    save(PRIVATE/'ledger.json', book)
    try:
        import fitz
        stat = path.stat()
        with path.open('rb') as stream:
            raw = stream.read(4*1024**2+1)
        book['decoded_bytes'] += len(raw)
        digest = hashlib.sha256(raw).hexdigest()
        record.update(source_bytes=len(raw), source_sha256=digest)
        save(PRIVATE/'ledger.json', book)
        assert digest == expected['source_sha256'] and len(raw) == stat.st_size
        assert path.stat().st_size == stat.st_size and path.stat().st_mtime_ns == stat.st_mtime_ns
        assert raw.startswith(b'%PDF') and b'%%EOF' in raw[-4096:]
        assert len(raw) <= 4*1024**2 and book['decoded_bytes'] <= 32*1024**2
        with fitz.open(stream=raw, filetype='pdf') as pdf:
            front = ' '.join(pdf[i].get_text() for i in range(min(2, len(pdf))))
        compact = ''.join(front.split()).lower()
        doi_match = expected['expected_doi'].lower() in compact
        record['doi_in_front_matter'] = doi_match
        if expected['source_part'] == 'main':
            assert doi_match, 'Fixed main-article DOI mismatch'
            record['association_status'] = 'MAIN_DOI_VERIFIED'
        else:
            # SI may omit a DOI. Check the already exposed bibliographic title,
            # emitting only overlap counts, never the unmasked front matter.
            source_docs = json.loads((PRIVATE/'accepted-projection-index-v1.json').read_text())['source_docs']
            title = next(row['title'] for row in source_docs if row['document_chembl_id'] == expected['document_id'])
            tokens = lambda s: set(re.findall(r'[a-z]{4,}', unicodedata.normalize('NFKD', s).lower()))
            wanted, seen = tokens(title), tokens(front)
            shared = len(wanted & seen)
            title_match = shared >= 6 and shared / max(1, len(wanted)) >= .8
            record.update(title_token_count=len(wanted), shared_title_tokens=shared,
                          title_token_match=title_match,
                          association_status='OWNER_LINKED_TITLE_MATCHED_NOT_PUBLISHER_AUTHENTICATED' if title_match else 'OWNER_LINKED_ASSOCIATION_UNVERIFIED')
        checks = safety_checks()
        if expected['source_part'] == 'supplement' and not record.get('title_token_match') and not doi_match:
            output = {'status':'QUARANTINE_SOURCE_ASSOCIATION', 'paragraphs':[]}
        else:
            output = extract_pdf(raw, supplement=expected['source_part'] == 'supplement')
        output_path = PRIVATE/('owner-v2-'+filename.replace('.pdf','')+'-masked.json')
        save(output_path, output)
        module = ROOT/'tools/r0r_owner_methods_mask_v2.py'
        module_bytes = module.read_bytes()
        module_hash = hashlib.sha256(module_bytes).hexdigest()
        (PRIVATE/'code'/(module_hash+'.py')).write_bytes(module_bytes)
        record.update(status=output['status'], output_path=str(output_path.relative_to(ROOT)),
                      output_sha256=hashlib.sha256(output_path.read_bytes()).hexdigest(),
                      mask_module_sha256=module_hash, safety_checks=checks,
                      finished_utc=datetime.now(timezone.utc).isoformat(),
                      unmasked_article_copied_to_private_root=False,
                      reference_review='PENDING_OWNER_REVIEW')
        save(PRIVATE/'ledger.json', book)
        guard.finish(record['status'], charged_to='20-second additional worker reservation')
        print(json.dumps({key: record.get(key) for key in ['filename','status','association_status','title_token_count','shared_title_tokens']}))
        print(json.dumps({key: output.get(key) for key in ['retained_paragraph_count','boundary_start','boundary_end','end_at_supplement_eof']}))
    except Exception as exc:
        record.update(status='STOP_LOCAL_SOURCE', error_type=type(exc).__name__)
        save(PRIVATE/'ledger.json', book)
        guard.finish('STOP_LOCAL_SOURCE', error_type=type(exc).__name__)
        raise RuntimeError('Local source stopped; retained receipt and reservation') from None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('filename')
    run(parser.parse_args().filename)
