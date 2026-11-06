"""Format complete preservation metadata without rewriting retained originals."""

import hashlib
import json
from pathlib import Path

from tools.goal4r2a_remote_v1 import LOCAL, PACKET, write_new


def main():
    full = LOCAL / 'remote-return/full-v1'
    proof = json.loads((full / 'local-verification-with-manifest.json').read_text())
    assert proof['status'] == 'PASS_LOCAL_ALL_FILES_VERIFIED'
    assert proof['manifest_unchanged_during_verification']
    sources = {'local-full-return-verification-v1.json': full / 'local-verification-with-manifest.json',
               'local-verification-resources-v1.json': full / 'verification-resources.json'}
    for name, path in sources.items():
        original = path.read_bytes()
        clean = original.replace(b'\r\n', b'\n')
        assert json.loads(original) == json.loads(clean)
        with (PACKET / name).open('xb') as handle:
            handle.write(clean)
    audit = json.loads((PACKET / 'si-metadata-audit-v1.json').read_text())
    records = []
    for attempt in ('si-toc-v1', 'si-metadata-v1'):
        raw_path = full / 'files/runs' / attempt / 'selected-pages.json'
        raw = raw_path.read_bytes()
        preview = (LOCAL / (attempt + '-pages.json')).read_bytes()
        expected = audit['input_text_sha256']['selected-pages.json:' + attempt]
        assert hashlib.sha256(raw).hexdigest() == expected
        assert preview == raw + b'\n' and json.loads(preview) == json.loads(raw)
        records.append({'attempt': attempt, 'raw_restored_sha256': expected,
                        'preview_is_exact_original_plus_one_lf': True})
    write_new(PACKET / 'si-input-provenance-v1.json', {
        'status': 'PASS_RAW_RETURNED_TEXT_IDENTITIES_AND_QUALIFIED_PREVIEWS',
        'records': records, 'original_full_return_unchanged': True,
        'raw_pdf_or_extracted_text_republished': False})
    print('PASS: complete proof copied; raw input hashes match SI audit; previews are original plus one LF.')


if __name__ == '__main__':
    main()
