"""Methods-only PDF blocks, with source locations and conservative masking.

Full PDF text is trusted-parser memory only. This is not semantic adjudication.
V1 XML extraction and its historical outputs remain unchanged.
"""
import re
import unicodedata

START = re.compile(r'^(?:experimental section|experimental procedures|materials and methods|methods)[.:]?$', re.I)
END = re.compile(r'^(?:results(?: and discussion)?|discussion|conclusions?|acknowledg(?:e)?ments?|supporting information(?: available)?|references)(?:[.:].*)?$', re.I)
EXCLUDE = re.compile(r'\b(?:results?|table|figure|fig\.?|showed|shown|exhibited|displayed|potent|selectiv\w*|yield|nmr|spectr\w*|characteriz\w*|observed|revealed|improved|enhanced)\b', re.I)
PROCEDURE = re.compile(r'\b(?:incubat\w*|measur\w*|determin\w*|perform\w*|assay\w*|using|added|mix\w*|transfect\w*|cultur\w*|binding|prepared|calculat\w*)\b', re.I)
BIOLOGY = re.compile(r'\b(?:assay\w*|cells?|receptor\w*|protein\w*|ligand\w*|binding|perforin|erythrocyt\w*|hemoly\w*|haemoly\w*|radioligand\w*|ic50|ec50|camp|inositol|cytotox\w*|lysis|lytic|membranes?)\b', re.I)


def mask_numbers(text):
    text = unicodedata.normalize('NFKC', text)
    for label, token in [('IC50', 'ICFIFTYTOKEN'), ('EC50', 'ECFIFTYTOKEN')]:
        text = re.sub(label, token, text, flags=re.I)
    text = re.sub(r'[+-]?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?', '[NUMBER]', text)
    return text.replace('ICFIFTYTOKEN', 'IC50').replace('ECFIFTYTOKEN', 'EC50')


def extract_blocks(blocks, supplement=False):
    """Consume (page, block, text) in native PDF reading order, never emit raw."""
    active = False
    finished = False
    paragraphs = []
    dropped = 0
    start_location = None
    end_location = None
    for page, block, raw in blocks:
        retained = []
        for line in raw.splitlines():
            line = ' '.join(line.split())
            if not active:
                if START.fullmatch(line):
                    active = True
                    start_location = {'page': page, 'block': block}
                continue
            if END.fullmatch(line):
                finished = True
                end_location = {'page': page, 'block': block}
                break
            retained.append(line)
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', ' '.join(retained)).strip()
        if text:
            if EXCLUDE.search(text) or not PROCEDURE.search(text) or not BIOLOGY.search(text):
                dropped += 1
            else:
                paragraphs.append({'pdf_page': page, 'pdf_block': block,
                                   'masked_text': mask_numbers(text)})
        if finished:
            break
    # A supplement can end at EOF after an explicit methods heading. No implicit
    # all-document or "looks like methods" fallback is allowed.
    bounded = start_location is not None and (finished or supplement)
    if not bounded:
        paragraphs = []
    paragraphs = paragraphs[:40]
    return {'status': ('MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED' if paragraphs else
                       'QUARANTINE_NO_ADMISSIBLE_METHODS' if bounded else
                       'QUARANTINE_UNVERIFIED_PDF_SECTION_BOUNDARIES'),
            'boundary_start': start_location, 'boundary_end': end_location,
            'end_at_supplement_eof': bool(bounded and not finished and supplement),
            'retained_paragraph_count': len(paragraphs), 'dropped_block_count': dropped,
            'paragraphs': paragraphs, 'unmasked_results_or_tables_emitted': False,
            'all_semantic_outcome_leakage_ruled_out': False,
            'numeric_masking_can_remove_necessary_protocol_information': True,
            'native_pdf_reading_order_independently_verified': False}


def extract_pdf(raw, supplement=False):
    import fitz
    with fitz.open(stream=raw, filetype='pdf') as document:
        blocks = [(index + 1, block[5], block[4])
                  for index, page in enumerate(document)
                  for block in page.get_text('blocks', sort=False) if block[6] == 0]
    return extract_blocks(blocks, supplement=supplement)


def safety_checks():
    fixture = [(1, 0, 'Results\nSECRET_RESULT 42 nM'),
               (2, 1, 'Experimental Section'),
               (2, 2, 'Cells were incubated for 10 minutes and IC50 was determined.'),
               (2, 3, 'Table 1\nSECRET_TABLE 77 nM\nBinding assay was performed.'),
               (2, 4, 'Binding assays showed SECRET_SEMANTIC high potency.'),
               (3, 0, 'References'),
               (3, 1, 'SECRET_AFTER 99 nM binding assay was performed.')]
    output = extract_blocks(fixture)
    text = str(output['paragraphs'])
    assert output['status'] == 'MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED'
    assert output['retained_paragraph_count'] == 1 and 'IC50' in text
    assert all(token not in text for token in ['SECRET', '10', '42', '77', '99'])
    assert extract_blocks(fixture[:1])['paragraphs'] == []
    assert extract_blocks(fixture[1:3])['paragraphs'] == []
    assert extract_blocks(fixture[1:3], supplement=True)['end_at_supplement_eof']
    assert '[NUMBER]' in mask_numbers('assay ١٢ and ₁₂ EC50')
    assert not re.search(r'\d', mask_numbers('١٢ ₁₂ 4.2e-9'))
    return {'status': 'PASS', 'cases': 5, 'independent_semantic_review': 'NOT_RUN'}
