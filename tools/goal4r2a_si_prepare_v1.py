"""Identify the separate owner SI, keeping the first article input unchanged."""

import hashlib
import json
from pathlib import Path

from tools.goal4r2a_remote_v1 import LOCAL, PACKET, ROOT


def main():
    pdf = ROOT / 'research/raw_data/external-benchmarks/mf-pcba-2023/metadata/ci2c01569_si_001.pdf'
    data = pdf.read_bytes()
    if not data.startswith(b'%PDF-') or not 1024 < len(data) < 16 * 1024**2:
        raise ValueError('Expected bounded PDF container')
    proof = json.loads((PACKET / 'pdf-tools-intake-v1.json').read_text())
    result = {**proof, 'status': 'PASS_OWNER_SEPARATE_SI_CONTAINER_IDENTITY_PENDING',
              'owner_pdf_local': str(pdf.relative_to(ROOT)), 'owner_pdf_bytes': len(data),
              'owner_pdf_sha256': hashlib.sha256(data).hexdigest()}
    with (PACKET / 'si-tools-intake-v1.json').open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(result, handle, indent=2)
        handle.write('\n')
    old = (ROOT / 'tools/goal4r2a_pdf_probe_v1.py').read_text()
    updated = old.replace('pdf-tools-intake-v1.json', 'si-tools-intake-v1.json').replace("inputs / 'owner.pdf'", "inputs / 'owner-si.pdf'")
    updated = updated.replace("parser.add_argument('--bundle', required=True)", "parser.add_argument('--bundle', required=True)\n    parser.add_argument('--pages', default='1,2,3')")
    updated = updated.replace("# First page only: identify the supplied file before deciding what to inspect.\n        first = reader.pages[0].extract_text()\n        (output / 'first-page.txt').write_text(first, encoding='utf-8')", "selected = [int(value) for value in args.pages.split(',')]\n        assert len(selected) <= 12 and len(set(selected)) == len(selected) and all(1 <= value <= len(reader.pages) for value in selected)\n        text = {str(value): reader.pages[value-1].extract_text() for value in selected}\n        (output / 'selected-pages.json').write_text(json.dumps(text, indent=2), encoding='utf-8')")
    updated = updated.replace("'pages_extracted': [1]", "'pages_extracted': selected")
    target = ROOT / 'tools/goal4r2a_si_inspect_v1.py'
    with target.open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(updated)
    LOCAL.joinpath('controller-history').mkdir(exist_ok=True)
    with (LOCAL / 'controller-history/before-si-mode-v1.py').open('xb') as handle:
        handle.write((ROOT / 'tools/goal4r2a_remote_v1.py').read_bytes())
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
