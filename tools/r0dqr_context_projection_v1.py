"""Conservative procedural projection; omitted context remains explicitly unknown."""
import copy,re,xml.etree.ElementTree as ET

OUTCOME=re.compile(r'\b(?:results?|showed|exhibited|displayed|increased|decreased|improved|enhanced|reduced|abolished|retained|inhibited|inhibits|activated|activates|fold|potent|potency|selectiv\w*|efficacy|efficien\w*|ranking|ranked|outperform\w*|table|figure|nmr|spectr\w*|yield)\b',re.I)
PROCEDURE=re.compile(r'\b(?:incubat\w*|buffer\w*|temperature|pH|cultured|transfect\w*|substrate|ATP|ADP|MgCl2|NaCl|KCl|duration|for\s+\d+\s*(?:min|hour|sec))\b',re.I)
IDENTIFIER=re.compile(r'\b(?:[A-Z][a-z]+-?\d+(?:[A-Z][a-z]*)?|[A-Z]{1,5}-?\d+(?:[A-Z])?|[A-Z]\d+[A-Z]|[A-Za-z]+\d+(?:[A-Za-z0-9-]*))\b')
PARAM_INPUT=re.compile(r'^(?:pH|temperature|(?:assay |incubation |reaction )?(?:time|duration)|(?:ATP|ADP|substrate|buffer|enzyme|protein|receptor|ligand|tracer|radioligand) concentration|concentration of (?:ATP|ADP|substrate|buffer|enzyme|protein|receptor|ligand|tracer|radioligand))$',re.I)
PARAM_VALUE=re.compile(r'^[\s+−\-\d.eEμuMmnpfKCA°/%:]+$')
ISOTOPE_IDENTIFIER=re.compile(r'\[(?:3H|14C|32P|35S|125I|131I|18F|11C)\]')
INPUT_CONDITION=re.compile(r'\b(?:(?:for|over|during|after)\s+\d+(?:\.\d+)?\s*(?:min(?:utes)?|s(?:econds)?|h(?:ours)?)\b|(?:at|temperature(?: of)?)\s+\d+(?:\.\d+)?\s*°?\s*[CK]\b|pH\s*(?:of|=)?\s*\d+(?:\.\d+)?\b|(?:ATP|ADP|NaCl|KCl|MgCl2|substrate|buffer|enzyme|radioligand|tracer)(?: concentration of| at|:|=)?\s+\d+(?:\.\d+)?\s*(?:μM|uM|mM|nM|M)\b)',re.I)

def project_text(text):
    if not text:return {'text':None,'omitted_sentences':0,'unclassified_numerals_masked':False,'complete_context_claim':False}
    accepted=[];dropped=0;masked=False
    for sentence in re.split(r'(?<=[.;])\s+',str(text)):
        if OUTCOME.search(sentence) or re.search(r'\b(?:Ki|Kd|IC50|EC50|pKi|pIC50)\b.{0,60}\b(?:was|were|is|of|equal|equals|than|found|yielded)\b',sentence,re.I) or re.search(r'\b(?:Ki|Kd|IC50|EC50|pIC50|pKi)\s*(?:was|were|of|=|<|>|:|approximately)\s*[+\-]?\d',sentence,re.I):
            dropped+=1;continue
        tokens={}
        def retain(match):
            token='ENTITYTOKEN'+chr(65+len(tokens)//26)+chr(65+len(tokens)%26);tokens[token]=match.group();return token
        # A methods heading alone does not make every number an input. Keep
        # only narrowly named procedural patterns and entity identifiers.
        sentence=ISOTOPE_IDENTIFIER.sub(retain,sentence)
        sentence=INPUT_CONDITION.sub(retain,sentence)
        sentence=IDENTIFIER.sub(retain,sentence)
        if re.search(r'\d',sentence):masked=True;sentence=re.sub(r'[+\-]?\d+(?:\.\d+)?(?:[eE][+\-]?\d+)?','[UNCLASSIFIED_NUMBER]',sentence)
        for key,value in tokens.items():sentence=sentence.replace(key,value)
        accepted.append(sentence)
    return {'text':' '.join(accepted) or None,'omitted_sentences':dropped,'unclassified_numerals_masked':masked,
        'complete_context_claim':False,'trusted_projection_not_semantic_gold':True}

def project_methods(raw):
    if b'<!ENTITY' in raw.upper():raise ValueError('Entity declarations denied')
    root=ET.fromstring(raw)
    for node in root.iter():node.tag=node.tag.split('}')[-1]
    headings=re.compile(r'^(?:materials?\s+(?:and|&)\s+methods?|experimental(?:\s+(?:section|procedures?))?|methods?|biological\s+assays?)$',re.I)
    blocked=re.compile(r'\b(?:results?|discussion|conclusions?|references|chemical synthesis|chemistry)\b',re.I)
    paragraphs=[];dropped=0
    for section in root.findall('.//body//sec'):
        title=' '.join(section.findtext('title','').split()).strip(' .:')
        if not headings.fullmatch(title):continue
        clone=copy.deepcopy(section)
        for parent in clone.iter():
            for child in list(parent):
                child_title=' '.join(child.findtext('title','').split())
                if child.tag in {'table-wrap','fig','supplementary-material','disp-formula'} or child.tag=='sec' and blocked.search(child_title):parent.remove(child)
        for para in clone.findall('.//p'):
            text=' '.join(' '.join(para.itertext()).split())
            if not re.search(r'\b(?:assay|binding|incubat\w*|transfect\w*|cells|receptor|enzyme|protein)\b',text,re.I):continue
            projected=project_text(text);dropped+=projected['omitted_sentences']
            if projected['text']:paragraphs.append({'section':title,**projected})
    dois=[]
    for node in root.findall('./front/article-meta/article-id'):
        if node.attrib.get('pub-id-type')=='doi':dois.append((node.text or '').strip().lower())
    licenses=[' '.join(' '.join(node.itertext()).split()) for node in root.findall('.//license')]
    return {'status':'PROJECTED_METHODS_PENDING_REVIEW' if paragraphs else 'QUARANTINE_NO_ADMISSIBLE_METHODS',
        'paragraphs':paragraphs[:40],'omitted_sentences':dropped,'article_dois':dois,'license_statements':licenses[:2],
        'tables_figures_and_result_sections_emitted':False,'complete_metadata_or_reference_gold_claim':False,
        'semantic_projection_requires_human_review':True}

def fixtures():
    example='<article><front><article-meta><article-id pub-id-type="doi">10.fixture/test</article-id></article-meta></front><body><sec><title>Results</title><p>SECRET_RESULT 42 nM</p></sec><sec><title>Materials and methods</title><p>COS-7 cells were incubated for 30 min at 37 C. IC50 was 12 nM. The mutant A123V showed increased activity.</p><table-wrap><p>SECRET_TABLE 77 nM</p></table-wrap></sec></body></article>'
    result=project_methods(example.encode());text=str(result['paragraphs'])
    assert 'COS-7' in text and '30 min' in text and '37 C' in text
    assert '12 nM' not in text and '42' not in text and '77' not in text and 'SECRET' not in text
    assert 'increased activity' not in text
    assert PARAM_INPUT.fullmatch('ATP concentration') and not PARAM_INPUT.fullmatch('inhibition')
    assert project_methods(b'<article><body><sec><title>Results</title><p>ASSAY SECRET 1 nM</p></sec></body></article>')['status']=='QUARANTINE_NO_ADMISSIBLE_METHODS'
    try:project_methods(b'<!ENTITY x "hidden"><article/>')
    except ValueError:pass
    else:raise AssertionError('Entity admitted')
    return {'status':'PASS_PROCEDURAL_PROJECTION_FIXTURES','checks':6,'real_sources_validated':False}
