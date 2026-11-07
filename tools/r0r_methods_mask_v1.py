"""Conservative methods-only extraction before any article enters agent context."""
import copy
import re
import xml.etree.ElementTree as ET

def extract_masked_pdf_methods(raw):
    if not raw.startswith(b'%PDF'):
        raise ValueError('Not a publisher PDF')
    import fitz
    import html
    with fitz.open(stream=raw,filetype='pdf') as document:
        text='\n'.join(page.get_text() for page in document)
    return extract_masked_pdf_text(text)

def extract_masked_pdf_text(text):
    import html
    start=re.search(r'(?im)^\s*(?:EXPERIMENTAL PROCEDURES|MATERIALS AND METHODS|EXPERIMENTAL SECTION)[.:]?\s*$',text)
    finish=re.search(r'(?im)^\s*(?:RESULTS(?: AND DISCUSSION)?|DISCUSSION|CONCLUSIONS?|ACKNOWLEDGMENTS?|ACKNOWLEDGEMENTS?|SUPPORTING INFORMATION|REFERENCES)[.:]?\s*$',text[start.end():]) if start else None
    if not start or not finish:
        return {'status':'QUARANTINE_UNVERIFIED_PDF_SECTION_BOUNDARIES','paragraphs':[],
                'unmasked_results_or_tables_emitted':False,'all_semantic_outcome_leakage_ruled_out':False}
    methods=text[start.end():start.end()+finish.start()]
    paragraphs=[' '.join(part.split()) for part in re.split(r'\n\s*\n',methods) if part.strip()]
    xml='<article><body><sec><title>Methods</title>'+''.join('<p>'+html.escape(part)+'</p>' for part in paragraphs)+'</sec></body></article>'
    result=extract_masked_methods(xml.encode())
    result['pdf_section_layout_independently_verified']=False
    return result

def extract_masked_methods(raw):
    if b'<!ENTITY' in raw.upper():
        raise ValueError('Entity declarations rejected')
    root=ET.fromstring(raw)
    for element in root.iter():
        element.tag=element.tag.split('}')[-1]
    headings=re.compile(r'^(?:materials?\s+(?:and|&)\s+methods?|experimental(?:\s+(?:section|procedures?))?|methods?|biological\s+assays?)$',re.I)
    excluded=re.compile(r'\b(?:results?|table|figure|showed|exhibited|displayed|potent|selectiv\w*|yield|nmr|spectr\w*|characteriz\w*)\b',re.I)
    procedural=re.compile(r'\b(?:incubat\w*|measur\w*|determin\w*|perform\w*|assay\w*|purchas\w*|using|added|mix\w*|transfect\w*|cultured|binding)\b',re.I)
    candidates=[]
    seen=set()
    sections=0
    dropped=0
    for sec in root.findall('.//body//sec'):
        title=' '.join(sec.findtext('title','').split()).strip(' .:')
        if not headings.fullmatch(title):
            continue
        sections+=1
        cloned=copy.deepcopy(sec)
        for parent in cloned.iter():
            for child in list(parent):
                if child.tag in {'table-wrap','fig','supplementary-material','disp-formula'}:
                    parent.remove(child)
        for paragraph in cloned.findall('.//p'):
            text=' '.join(' '.join(paragraph.itertext()).split())
            if not text or text in seen:
                continue
            seen.add(text)
            if excluded.search(text) or not procedural.search(text):
                dropped+=1;continue
            # Preserve endpoint tokens, which are metadata, while masking every
            # other decimal numeral (including concentrations and compound IDs).
            for label,token in [('IC50','ICFIFTYTOKEN'),('EC50','ECFIFTYTOKEN')]:
                text=re.sub(label,token,text,flags=re.I)
            text=re.sub(r'[+-]?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?','[NUMBER]',text)
            text=text.replace('ICFIFTYTOKEN','IC50').replace('ECFIFTYTOKEN','EC50')
            candidates.append({'section':title,'masked_text':text})
    licenses=[' '.join(' '.join(node.itertext()).split()) for node in root.findall('.//license')]
    return {'status':'MASKED_METHODS_AVAILABLE_NOT_ADJUDICATED' if candidates else 'QUARANTINE_NO_ADMISSIBLE_METHODS',
            'eligible_section_count':sections,'retained_paragraph_count':len(candidates[:40]),
            'dropped_paragraph_count':dropped,'paragraphs':candidates[:40],
            'license_statements':licenses[:2],
            'unmasked_results_or_tables_emitted':False,
            'all_semantic_outcome_leakage_ruled_out':False,
            'numeric_masking_can_remove_necessary_protocol_information':True}

def safety_checks():
    raw=b'<article><body><sec><title>Results</title><p>SECRET_RESULT 42 nM</p></sec><sec><title>Materials and methods</title><p>Cells were incubated with 10 uM reagent and IC50 was determined.</p><table-wrap><p>SECRET_TABLE 77 nM</p></table-wrap></sec></body></article>'
    result=extract_masked_methods(raw)
    text=str(result['paragraphs'])
    assert 'SECRET_RESULT' not in text and 'SECRET_TABLE' not in text
    assert '42' not in text and '10' not in text and '77' not in text
    assert 'IC50' in text and '[NUMBER]' in text
    empty=extract_masked_methods(b'<article><body><sec><title>Results</title><p>No methods.</p></sec></body></article>')
    assert empty['status']=='QUARANTINE_NO_ADMISSIBLE_METHODS'
    try:extract_masked_methods(b'<!ENTITY x "abc"><article/>')
    except ValueError:pass
    else:raise AssertionError('Entity declaration admitted')
    return {'status':'PASS_OFFLINE_MASKING_CASES','cases':3,'scientific_reference_gold':False}
