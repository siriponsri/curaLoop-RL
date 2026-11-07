"""Allow entity digits, never numerical protocol conditions or outcomes."""
import re
import unicodedata
from r0r_owner_methods_mask_v2 import START,END,EXCLUDE,PROCEDURE,BIOLOGY

ENTITY=re.compile(r'(?<![A-Za-z0-9])(?:'
    r'COS[- ]?7|HEK[- ]?293T?|PC[- ]?3|KHYG[- ]?1|K[- ]?562|CHO(?:[- ]?K1)?|HeLa|Sf9|Jurkat|SRBC|'
    r'(?:sigma[- ]?|[\u03c3\u03c2])[- ]?[12]|5[- ]?HT[1-7][A-F]?|GHS[- ]?R[- ]?1a|'
    r'[ACDEFGHIKLMNPQRSTVWY]\d{1,4}[ACDEFGHIKLMNPQRSTVWY]|'
    r'(?:Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)[- ]?\d{1,4}(?:[.:]\d{1,3})?'
    r')(?![A-Za-z0-9]|[.:]\d)')
OUTCOME=re.compile(r'\b(?:showed|exhibited|displayed|potent|selectiv\w*|result\w*|increased|decreased|enhanced|reduced|active compounds?|inactive)\b|(?:IC50|EC50|Ki|Kd)\s*(?:of\s*)?[=<>~\u2248\u2264\u2265]\s*\d|\d\s*(?:nM|uM|\u03bcM|%)',re.I)
FLAGS={
    'radioligand_binding':r'radioligand|competition binding|ligand[ -]binding|displacement',
    'cell_lysis':r'\b(?:lysis|lytic|cytolys\w*|cytotox\w*)\b',
    'perforin':r'\bperforin\b',
    'inositol_turnover':r'inositol|phosphatidylinositol',
    'sre_reporter':r'SRE|serum response',
    'mutant_context':r'\bmutant\w*|\bmutations?|\bsubstitut\w*',
    'wild_type_context':r'wild[ -]?type|\bWT\b',
    'constitutive_context':r'constitutive|basal signal',
    'agonist_context':r'\bagonis\w*',
    'inverse_agonist_context':r'inverse[ -]agonis\w*',
    'mt_tetrazolium_growth':r'\bMTT\b|antiproliferative|cell growth',
    'lipid_preparation':r'lipid|phosphatidylserine|Triton',
}


def alpha(index):
    result=''
    while True:
        result=chr(65+index%26)+result;index=index//26-1
        if index<0:return result


def mask(text):
    text=unicodedata.normalize('NFKC',text)
    entities=[]
    def replace(match):
        entities.append(match.group())
        return 'ZENTITYTOKEN'+alpha(len(entities)-1)+'END'
    text=ENTITY.sub(replace,text)
    text=re.sub('IC50','ZICFIFTYTOKENEND',text,flags=re.I)
    text=re.sub('EC50','ZECFIFTYTOKENEND',text,flags=re.I)
    text=re.sub(r'[+-]?\d+(?:[.,]\d+)?(?:[eE][+-]?\d+)?','[NUMBER]',text)
    for i,entity in enumerate(entities):text=text.replace('ZENTITYTOKEN'+alpha(i)+'END',entity)
    text=text.replace('ZICFIFTYTOKENEND','IC50').replace('ZECFIFTYTOKENEND','EC50')
    return text,sorted(set(entities))


def description_features(text):
    # Do not emit a complete description, even masked. A numeric condition or
    # result-bearing clause is quarantined before deriving any context flags.
    normalized=unicodedata.normalize('NFKC',text or '')
    clauses=list(re.finditer(r'[^;\n]+',normalized))
    admitted=[];dropped=0;spans=[]
    for clause in clauses:
        value=clause.group()
        if OUTCOME.search(value):dropped+=1
        elif value.strip():
            admitted.append(value)
            spans.extend({'text':m.group(),'start':clause.start()+m.start(),'end':clause.start()+m.end()} for m in ENTITY.finditer(value))
    text=' '.join(admitted)
    return {'entities':sorted(set(m.group() for m in ENTITY.finditer(text))),
            'entity_spans':spans,'span_coordinates':'NFKC-normalized original description',
            'context_flags':[key for key,pattern in FLAGS.items() if re.search(pattern,text,re.I)],
            'admitted_clauses':len(admitted),'quarantined_clauses':dropped,
            'complete_description_emitted':False,'unmatched_semantics':'UNRESOLVED'}


def pdf_methods(raw):
    import fitz
    paragraphs=[];dropped=0;start=None;end=None;active=False;finished=False
    with fitz.open(stream=raw,filetype='pdf') as pdf:
        for index,page in enumerate(pdf):
            for block in page.get_text('blocks',sort=False):
                if block[6]!=0:continue
                retained=[]
                for line in block[4].splitlines():
                    line=' '.join(line.split())
                    if not active:
                        if START.fullmatch(line):active=True;start={'page':index+1,'block':block[5]}
                        continue
                    if END.fullmatch(line):finished=True;end={'page':index+1,'block':block[5]};break
                    retained.append(line)
                text=re.sub(r'(\w)-\s+(\w)',r'\1\2',' '.join(retained)).strip()
                if text:
                    if EXCLUDE.search(text) or not PROCEDURE.search(text) or not BIOLOGY.search(text):dropped+=1
                    else:
                        masked,entities=mask(text)
                        paragraphs.append({'pdf_page':index+1,'pdf_block':block[5],
                                           'masked_text':masked,'permitted_entities':entities})
                if finished:break
            if finished:break
    bounded=start is not None and end is not None
    if not bounded:paragraphs=[]
    return {'status':'MASKED_METHODS_DRAFT_AVAILABLE' if paragraphs else 'QUARANTINE_NO_ADMITTED_BOUNDARIES_OR_METHODS',
            'boundary_start':start,'boundary_end':end,'paragraphs':paragraphs[:40],
            'dropped_blocks':dropped,'numeric_conditions_unmasked':False,
            'independent_semantic_review':'NOT_RUN'}


def safety_checks():
    source='HEK293 and COS7 cells with A204E mutant were incubated for 30 min at 37 C. IC50 = 4.2 nM.'
    masked,entities=mask(source)
    assert {'HEK293','COS7','A204E'}<=set(entities)
    remainder=ENTITY.sub('',masked).replace('IC50','').replace('EC50','')
    assert not re.search(r'\d',remainder)
    assert '4.2' not in masked and '30' not in masked and '37' not in masked
    assert description_features('Binding in HEK293 cells; IC50 = 4.2 nM')['quarantined_clauses']==1
    blocked=description_features('HEK293 cells showed increased potency at 4.2 nM')
    assert blocked['entities']==[] and blocked['context_flags']==[]
    assert ENTITY.fullmatch('A204E') and not ENTITY.fullmatch('4.2nM')
    assert mask('sigma1 and sigma2 receptor IC50')[0]=='sigma1 and sigma2 receptor IC50'
    assert mask('HEK293T; ١٢; ₁₂')[0]=='HEK293T; [NUMBER]; [NUMBER]'
    assert description_features('mutant Asn7.49 and Ser4.57')['entities']==['Asn7.49','Ser4.57']
    assert not ENTITY.search('Asn7.49123')
    assert description_features('mutant Asn7:49 and Ser4:57')['entities']==['Asn7:49','Ser4:57']
    return {'status':'PASS','cases':8,'semantic_leakage_guaranteed_absent':False}
