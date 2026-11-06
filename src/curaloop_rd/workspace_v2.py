"""Versioned bilingual view of an existing, immutable metadata report.

Rendering grants no new source access, experiment or external-delivery authority.
"""
import base64
import hashlib
import html
import json
from pathlib import Path
import shutil
import re
from urllib.parse import urlparse
from .contracts_v2 import validate_report

LABELS = {
    'Evidence workspace': 'พื้นที่ตรวจสอบหลักฐาน', 'Evidence': 'หลักฐาน',
    'Readiness plan': 'แผนเตรียมความพร้อม', 'Export': 'ส่งออก',
    'Report': 'รายงาน', 'Revision': 'รุ่น', 'Metadata report': 'รายงานข้อมูลกำกับ',
    'Inspect the declared endpoint and its source.': 'ตรวจข้อมูล endpoint ที่ประกาศและแหล่งอ้างอิง',
    'Source question': 'คำถามต้นฉบับ', 'Declared fields': 'ฟิลด์ที่ประกาศ',
    'Field': 'ฟิลด์', 'Value': 'ค่า', 'State': 'สถานะ',
    'Source locator': 'ตำแหน่งในข้อมูลต้นฉบับ', 'Inspect citation': 'ตรวจแหล่งอ้างอิง',
    'Source record': 'ระเบียนต้นฉบับ', 'Source SHA256': 'SHA256 ของแหล่งข้อมูล',
    'Open source URL': 'เปิด URL ต้นฉบับ', 'Receipt SHA256': 'SHA256 ของหลักฐานการรับข้อมูล',
    'Local preview only': 'ตัวอย่างบนเครื่องเท่านั้น',
    'No external delivery has occurred.': 'ยังไม่มีการส่งออกไปยังระบบภายนอก',
    'Review the metadata and its limits before planning an experiment.': 'ตรวจข้อมูลกำกับและข้อจำกัดก่อนวางแผนทดลอง',
    'Molecular experiments': 'การทดลองโมเลกุล', 'Not released': 'ยังไม่อนุมัติให้เริ่ม',
    'Qualified molecular replay': 'การจำลองโมเลกุลที่ผ่านเกณฑ์',
    'Unmet': 'ยังไม่ผ่านเกณฑ์', 'Next actions': 'ขั้นตอนถัดไป',
    'Review the declared metadata and intended-use limits.': 'ตรวจข้อมูลที่ประกาศและขอบเขตการใช้งาน',
    'Define and qualify a scientific endpoint/population before any molecular experiment.': 'กำหนดและตรวจสอบ endpoint กับประชากรศึกษาก่อนเริ่มการทดลองโมเลกุล',
    'Download readiness plan': 'ดาวน์โหลดแผนเตรียมความพร้อม',
    'Portable files': 'ไฟล์สำหรับส่งต่อ', 'JSON report': 'รายงาน JSON',
    'Markdown report': 'รายงาน Markdown', 'Preview receipt': 'หลักฐานตัวอย่างบนเครื่อง',
    'Handoff manifest': 'บัญชีไฟล์ส่งต่อ',
    'Original source text, identifiers and values remain unchanged in both languages.': 'ข้อความต้นฉบับ รหัส และค่าจากแหล่งข้อมูลคงเดิมทั้งสองภาษา',
    'Scope and limits': 'ขอบเขตและข้อจำกัด',
    'Cached metadata only; no activity outcomes.': 'ข้อมูลกำกับที่เก็บไว้เท่านั้น ไม่มีผลกิจกรรม',
    'All sources were exposed during development.': 'ทุกแหล่งข้อมูลเคยใช้ระหว่างพัฒนาแล้ว',
    'Historical row equivalence and commercial permission are unresolved.': 'ยังไม่ยืนยันว่าตรงกับข้อมูลย้อนหลังรายแถวหรือมีสิทธิ์ใช้เชิงพาณิชย์',
    'No live model or autonomous experiment was evaluated.': 'ยังไม่ได้ประเมินโมเดลที่เชื่อมต่อจริงหรือการทดลองอัตโนมัติ',
    'Language': 'ภาษา', 'Skip to content': 'ข้ามไปเนื้อหา',
    'Endpoint unresolved': 'ยังไม่ยืนยัน endpoint',
    'Historical identity unresolved': 'ยังไม่ยืนยันข้อมูลย้อนหลังตรงรุ่น',
    'Rights unresolved': 'ยังไม่ยืนยันสิทธิ์การใช้งาน',
    'Required source unavailable': 'ยังไม่มีแหล่งข้อมูลที่จำเป็น',
    'Obtain the source-declared unit or definition.': 'ขอหน่วยหรือนิยามที่แหล่งข้อมูลประกาศ',
    'Consult the study owner before a material endpoint change.': 'ปรึกษาเจ้าของการศึกษาก่อนเปลี่ยน endpoint ที่มีสาระสำคัญ',
    'Obtain independent provenance of the exact historical snapshot before reconstruction claims.': 'ขอหลักฐานที่มาอิสระของข้อมูลย้อนหลังรุ่นที่ตรงกัน ก่อนอ้างว่าสร้างข้อมูลเดิมได้',
    'Obtain intended-use clearance before redistribution or commercial packaging.': 'ยืนยันสิทธิ์ตามวัตถุประสงค์ก่อนแจกจ่ายหรือจัดทำผลิตภัณฑ์เชิงพาณิชย์',
    'Obtain the missing permitted source through an owner-approved route.': 'ขอแหล่งข้อมูลที่ยังขาดผ่านช่องทางที่เจ้าของอนุมัติ',
    'Keep unsupported conclusions blocked; do not retry automatically.': 'คงข้อสรุปที่ยังไม่มีหลักฐานไว้ในสถานะหยุด ไม่ลองซ้ำอัตโนมัติ',
    'Readout ID': 'รหัส readout', 'Readout name': 'ชื่อ readout',
    'Value type code': 'รหัสประเภทค่า', 'Unit code': 'รหัสหน่วยจากต้นฉบับ',
    'Present': 'มีค่า', 'Not declared': 'ไม่ได้ประกาศ',
    'Null in source': 'ต้นฉบับระบุ null', 'Unresolved': 'ยังไม่ยืนยัน',
    'Cached metadata': 'ข้อมูลกำกับที่เก็บไว้',
    'Source-declared metadata, not an activity result.': 'ข้อมูลกำกับที่แหล่งข้อมูลประกาศ ไม่ใช่ผลกิจกรรม',
    'Select a field to follow its evidence trail.': 'เลือกฟิลด์เพื่อติดตามหลักฐานอ้างอิง',
    'Selected source locator': 'ตำแหน่งอ้างอิงของฟิลด์ที่เลือก',
    'Exact readout identifier in the source schema.': 'รหัส readout ที่ตรงตามโครงสร้างข้อมูลต้นฉบับ',
    'Readout name as declared by the provider.': 'ชื่อ readout ตามที่ผู้ให้ข้อมูลประกาศ',
    'Raw value-type code retained.': 'คงรหัสประเภทค่าตามต้นฉบับ',
    'Raw unit code retained; no conversion.': 'คงรหัสหน่วยตามต้นฉบับ ไม่มีการแปลงหน่วย',
    'Original provider metadata.': 'ข้อมูลกำกับต้นฉบับจากผู้ให้ข้อมูล',
    'Open navigation': 'เปิดเมนู',
}

def esc(value):
    return html.escape(str(value), quote=True)

def label(text):
    if text not in LABELS:
        raise ValueError('Unknown interface label')
    return '<span data-i18n="'+esc(text)+'">'+esc(text)+'</span>'

def render_workspace(source, target, font):
    source, target, font = Path(source), Path(target), Path(font)
    if source.resolve()==target.resolve() or target.exists() or target.is_symlink():
        raise ValueError('A distinct new output directory is required')
    report_bytes=(source/'report.json').read_bytes()
    report=validate_report(json.loads(report_bytes))
    preview=json.loads((source/'preview.json').read_text())
    plan=json.loads((source/'readiness-plan.json').read_text())
    if report['scope']!='CACHED_REAL_METADATA_ONLY' or report['external_delivery'] or report['live_agent']:
        raise ValueError('Cached metadata-only report required')
    if preview['report_sha256']!=report['report_sha256'] or plan['report_sha256']!=report['report_sha256']:
        raise ValueError('Report, plan and preview identities differ')
    if plan['molecular_experiments_released'] is not False or preview['delivered'] is not False or preview['destination']!='LOCAL_PREVIEW_ONLY':
        raise ValueError('Unreleased local-preview boundary required')
    if font.is_symlink() or font.read_bytes()[:4] not in (b'\x00\x01\x00\x00',b'OTTO'):
        raise ValueError('Local TrueType/OpenType font required')
    target.mkdir(parents=True)
    for name in ['report.json','report.md','preview.json','readiness-plan.json']:
        shutil.copyfile(source/name,target/name)
    rows=[]
    for position,claim in enumerate(report['claims']):
        evidence=claim['evidence']
        value=(claim['value'] if isinstance(claim['value'],str) else json.dumps(claim.get('value'),ensure_ascii=False)) if claim['state']=='VALUE' else claim['state']
        field_name={'tid':'Readout ID','name':'Readout name','type':'Value type code','unit':'Unit code'}.get(claim['key'])
        state_name={'VALUE':'Present','ABSENT':'Not declared','NULL':'Null in source','UNRESOLVED':'Unresolved'}[claim['state']]
        rows.append('<tr><th scope="row"><button class="claim-select" type="button" data-select-index="'+str(position)+'" aria-pressed="false">'+(label(field_name) if field_name else esc(claim['key']))+'</button></th><td class="value">'+esc(value)+'</td><td>'+label(state_name)+'</td><td><details><summary>'+label('Inspect citation')+'</summary><p>'+esc(evidence['source_id'])+' · '+esc(claim['key'])+' · '+esc(claim['state'])+'</p><code>'+esc(evidence['locator'])+'</code><p class="digest">'+esc(evidence['source_sha256'])+'</p></details></td></tr>')
    sources=[]
    for key, item in report['source_ledger'].items():
        citation=item['citation']
        url=citation.get('url','')
        if not isinstance(url,str):
            url=json.dumps(url,ensure_ascii=False)
        parsed=urlparse(url)
        safe=(parsed.scheme=='https' and parsed.hostname in {'pubchem.ncbi.nlm.nih.gov','pmc.ncbi.nlm.nih.gov','www.ncbi.nlm.nih.gov','rest.uniprot.org','www.uniprot.org'} and not parsed.username and not parsed.password)
        link=('<a href="'+esc(url)+'" target="_blank" rel="noreferrer">'+label('Open source URL')+' ↗</a>') if safe else '<p class="digest">'+esc(url)+'</p>'
        receipt=label('Not declared') if 'receipt_sha256' not in citation else label('Null in source') if citation['receipt_sha256'] is None else esc(citation['receipt_sha256'])
        sources.append('<div class="source" data-source-id="'+esc(key)+'"><strong>'+esc(key)+'</strong><details><summary>'+label('Inspect citation')+'</summary><dl><dt>'+label('Source SHA256')+'</dt><dd class="digest">'+esc(item['sha256'])+'</dd><dt>'+label('Receipt SHA256')+'</dt><dd class="digest">'+receipt+'</dd></dl></details>'+link+'</div>')
    font_data=base64.b64encode(font.read_bytes()).decode()
    language_json=json.dumps(LABELS,ensure_ascii=False).replace('<','\\u003c')
    assets=Path(__file__).parent/'resources'
    document=(assets/'workspace_v2.html').read_text(encoding='utf-8')
    css=(assets/'workspace_v2.css').read_text(encoding='utf-8').replace('__FONT__',font_data)
    script=(assets/'workspace_v2.js').read_text(encoding='utf-8')
    text_keys={'SKIP':'Skip to content','EVIDENCE':'Evidence','PLAN':'Readiness plan','EXPORT':'Export','LOCAL':'Local preview only','NO_DELIVERY':'No external delivery has occurred.','TITLE':'Evidence workspace','SUBTITLE':'Inspect the declared endpoint and its source.','DOWNLOAD':'Download readiness plan','REPORT':'Report','REVISION':'Revision','METADATA':'Metadata report','QUESTION':'Source question','FIELDS':'Declared fields','FIELD':'Field','VALUE':'Value','STATE':'State','LOCATOR':'Source locator','ORIGINAL':'Original source text, identifiers and values remain unchanged in both languages.','SOURCE':'Source record','REVIEW':'Review the metadata and its limits before planning an experiment.','MOLECULAR':'Molecular experiments','NOT_RELEASED':'Not released','REPLAY':'Qualified molecular replay','UNMET':'Unmet','NEXT':'Next actions','LIMITS':'Scope and limits','FILES':'Portable files','JSON':'JSON report','MD':'Markdown report','PREVIEW':'Preview receipt','MANIFEST':'Handoff manifest'}
    replacements={k:label(v) for k,v in text_keys.items()}
    dispositions={'METADATA_REPORT':'Metadata report','BLOCKED_ENDPOINT_UNRESOLVED':'Endpoint unresolved','BLOCKED_HISTORICAL_IDENTITY':'Historical identity unresolved','BLOCKED_RIGHTS_UNRESOLVED':'Rights unresolved','BLOCKED_REQUIRED_SOURCE':'Required source unavailable'}
    replacements['METADATA']=label(dispositions[report['disposition']])
    replacements.update(FONT=font_data,HASH_SHORT=esc(report['report_sha256'][:16]),HASH=esc(report['report_sha256']),REV=str(preview['revision']),QUESTION_TEXT=esc(report['question']),ROWS=''.join(rows),SOURCES=''.join(sources),ACTIONS=''.join('<li>'+label(a)+'</li>' for a in plan['next_actions']),LIMIT_ROWS=''.join('<li>'+label(a)+'</li>' for a in ['Cached metadata only; no activity outcomes.','All sources were exposed during development.','Historical row equivalence and commercial permission are unresolved.','No live model or autonomous experiment was evaluated.']),TRANSLATIONS=language_json)
    initial=next((c for c in report['claims'] if c['key']=='name' and c['state']=='VALUE'),report['claims'][0])
    initial_name={'tid':'Readout ID','name':'Readout name','type':'Value type code','unit':'Unit code'}.get(initial['key'])
    structured=initial['state']=='VALUE' and isinstance(initial['value'],(dict,list))
    initial_value=(initial['value'] if isinstance(initial['value'],str) else json.dumps(initial['value'],ensure_ascii=False,indent=2 if structured else None)) if initial['state']=='VALUE' else '—'
    initial_type='structured' if structured else 'long' if len(str(initial_value))>64 else 'scalar'
    hints={'tid':'Exact readout identifier in the source schema.','name':'Readout name as declared by the provider.','type':'Raw value-type code retained.','unit':'Raw unit code retained; no conversion.'}
    replacements.update(CSS=css,SCRIPT=script,
        CACHED=label('Cached metadata'),METADATA_VALUE=label('Source-declared metadata, not an activity result.'),
        INITIAL_HINT=label(hints.get(initial['key'],'Original provider metadata.')),
        LOGO_DATA='data:image/png;base64,'+base64.b64encode((assets/'logo-v2.png').read_bytes()).decode(),
        SELECT_FIELD=label('Select a field to follow its evidence trail.'),SELECTED_LOCATOR=label('Selected source locator'),
        INITIAL_LABEL=label(initial_name) if initial_name else esc(initial['key']),INITIAL_VALUE=esc(initial_value),INITIAL_TYPE=initial_type,
        INITIAL_KEY=esc(initial['key']),INITIAL_SOURCE=esc(initial['evidence']['source_id']),
        INITIAL_LOCATOR=esc(initial['evidence']['locator']),
        CLAIMS_JSON=json.dumps(report['claims'],ensure_ascii=False).replace('<','\\u003c'))
    document=re.sub(r'__(\w+)__',lambda match:replacements[match.group(1)],document)
    (target/'workspace.html').write_text(document,encoding='utf-8',newline='\n')
    shutil.copyfile(font.parent/'OFL.txt',target/'OFL.txt')
    files=[{'path':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(target.iterdir())]
    manifest={'schema':'curaloop.workspace-handoff.v2','renderer':'workspace_v2','report_sha256':report['report_sha256'],'source_report_bytes_sha256':hashlib.sha256(report_bytes).hexdigest(),'external_delivery':False,'files':files}
    (target/'handoff-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    return manifest
