"""Fresh R0-R limits, receipts and outcome-excluding HTTP intake."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from resource_guard_v1 import Guard as OSGuard

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = ROOT / '.local/r0r-chembl-20261107-v1'
DEADLINE = datetime(2026, 11, 7, 14, 16, 25, tzinfo=timezone.utc)

def now():
    return datetime.now(timezone.utc).isoformat()

def save(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    with temporary.open('wb') as stream:
        stream.write((json.dumps(payload, indent=2, allow_nan=False) + '\n').encode('utf-8'))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)

class Guard(OSGuard):
    def __init__(self, name, wall=60):
        PRIVATE.mkdir(parents=True, exist_ok=True)
        self.receipt = PRIVATE / (name + '-resource.json')
        if self.receipt.exists():
            raise RuntimeError('Receipt exists; retain previous attempt')
        remaining = (DEADLINE - datetime.now(timezone.utc)).total_seconds()
        if remaining <= 0:
            raise RuntimeError('R0-R window exhausted')
        self.started, self.cpu = time.monotonic(), time.process_time()
        self.wall_limit, self.cpu_limit = min(wall, remaining), 60
        self.ram_limit = 512 * 1024**2
        self.completed, self.lock = threading.Event(), threading.Lock()
        cpu = self._limit_process()
        entry = Path(sys.argv[0]).resolve()
        self.base = {'schema':'curaloop.r0r.resource.v1', 'pid':os.getpid(), 'start_utc':now(),
                     'cpu_affinity':[cpu], 'cpu_limit_seconds':60,
                     'memory_limit_bytes':self.ram_limit, 'wall_limit_seconds':self.wall_limit,
                     'deadline_utc':DEADLINE.isoformat(), 'descendants_allowed':False,
                     'executable':sys.executable, 'python':sys.version,
                     'entry_source_sha256':hashlib.sha256(entry.read_bytes()).hexdigest(),
                     'core_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
        for path in (entry, Path(__file__), ROOT / 'tools/resource_guard_v1.py'):
            data = path.read_bytes()
            archive = PRIVATE / 'code' / (hashlib.sha256(data).hexdigest() + '.py')
            archive.parent.mkdir(exist_ok=True)
            if not archive.exists():
                archive.write_bytes(data)
        self._write('RUNNING')
        threading.Thread(target=self._watch, daemon=True).start()

def ledger():
    path = PRIVATE / 'ledger.json'
    if not path.exists():
        save(path, {'id':'r0r-chembl-20261107-v1','status':'ACTIVE',
                    'release_utc':'2026-11-07T06:16:25Z','deadline_utc':DEADLINE.isoformat(),
                    'cpu_cap_seconds':3600,'utility_charge_seconds':600,
                    'worker_reserved_seconds':0,'decoded_bytes':0,'attempts':[], 'stopped_sources':[]})
    return json.loads(path.read_text())

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise RuntimeError('Unknown redirect; STOP')

def validate_spec(spec):
    url = urllib.parse.urlparse(spec['url'])
    if url.scheme != 'https':
        raise ValueError('HTTPS required')
    parameters = urllib.parse.parse_qs(url.query)
    if url.netloc == 'www.ebi.ac.uk' and url.path == '/chembl/api/data/activity/schema.json':
        if parameters:
            raise ValueError('Schema metadata must not request records')
    elif url.netloc == 'www.ebi.ac.uk' and url.path.startswith('/chembl/api/data/'):
        resource = url.path.rsplit('/',1)[-1]
        allowed = {
            'activity.json': {'activity_id','assay_chembl_id','document_chembl_id','molecule_chembl_id','standard_type','standard_units'},
            'molecule.json': {'molecule_chembl_id','molecule_structures'},
            'status.json': set(),
        }
        if resource not in allowed:
            raise ValueError('Resource not admitted')
        if resource != 'status.json':
            projection = set(parameters.get('only',[''])[0].split(','))
            if projection != allowed[resource]:
                raise ValueError('Exact outcome-free projection required')
            if resource == 'activity.json':
                if set(parameters) != {'only','assay_chembl_id','limit','order_by'} or parameters['limit'] != ['20'] or parameters['order_by'] != ['activity_id']:
                    raise ValueError('Unapproved activity filter/order/limit')
    elif url.netloc == 'www.ebi.ac.uk' and url.path == '/europepmc/webservices/rest/search':
        if parameters.get('resultType') != ['lite'] or parameters.get('format') != ['json']:
            raise ValueError('Only abstract-free bibliographic lookup admitted')
    elif url.netloc == 'www.ebi.ac.uk' and url.path.startswith('/europepmc/webservices/rest/PMC') and url.path.endswith('/fullTextXML'):
        if spec.get('kind') != 'methods_xml':
            raise ValueError('Full text requires trusted methods extraction')
    elif url.netloc == 'api.openalex.org' and url.path.startswith('/works/https://doi.org/'):
        if parameters.get('select') != ['id,doi,open_access,best_oa_location,locations']:
            raise ValueError('Only abstract-free access/location metadata admitted')
    elif url.netloc == 'www.jbc.org' and url.path == '/article/S0021925820874535/pdf':
        if spec.get('kind') != 'methods_pdf':
            raise ValueError('Known publisher PDF requires trusted methods masking')
    elif url.netloc=='hdl.handle.net' and url.path in ('/api/handles/2292/9218','/api/handles/2292/9369','/api/handles/11586/133028','/api/handles/11586/133161'):
        if parameters:
            raise ValueError('Only fixed public repository-handle metadata admitted')
    elif url.netloc in ('researchspace.auckland.ac.nz','ricerca.uniba.it') and spec.get('kind')=='repository_html':
        if not url.path.startswith(('/handle/','/items/')) or parameters:
            raise ValueError('Only vetted public repository metadata pages admitted')
    else:
        raise ValueError('URL outside fixed source classes')

def fetch(name):
    specs = json.loads((PRIVATE / 'request-registry.json').read_text())
    spec = specs[name]
    validate_spec(spec)
    lock_path = PRIVATE / 'worker.lock'
    fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    guard = None
    book = ledger()
    record = None
    try:
        if book['status'] != 'ACTIVE' or name in book['stopped_sources']:
            raise RuntimeError('Closed intake or retained source STOP')
        if name != 'status-before':
            start_rows=[row for row in book['attempts'] if row['source']=='status-before' and row['status']=='PASS']
            if len(start_rows)!=1 or json.loads((ROOT/start_rows[0]['output_path']).read_text()).get('chembl_db_version')!='ChEMBL_37':
                raise RuntimeError('ChEMBL37 status prerequisite not established')
        if len(book['attempts']) >= 48 or book['decoded_bytes'] >= 32*1024**2:
            raise RuntimeError('Request/byte budget exhausted')
        if book['utility_charge_seconds'] + book['worker_reserved_seconds'] + 60 > 3600:
            raise RuntimeError('CPU reservation ceiling')
        if any(row['source'] == name for row in book['attempts']):
            raise RuntimeError('No duplicate source request/retry')
        ordinal = len(book['attempts']) + 1
        stem = f'{ordinal:03d}-{name}'
        guard = Guard(stem, wall=30)
        record = {'id':stem,'source':name,'url':spec['url'],'started_utc':now(),
                  'kind':spec.get('kind','json'),'status':'RESERVED','decoded_bytes':0,
                  'reserved_cpu_seconds':60}
        book['attempts'].append(record)
        book['worker_reserved_seconds'] += 60
        save(PRIVATE / 'ledger.json', book)
        time.sleep(1)
        request = urllib.request.Request(spec['url'], headers={'Accept-Encoding':'identity','User-Agent':'CuraLoop-R0R/1.0'})
        body = bytearray()
        cap = (4 if record['kind'].startswith('methods_') else 2) * 1024**2
        record['status'] = 'STARTED'
        save(PRIVATE / 'ledger.json', book)
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=25) as response:
            record['http_status'] = response.status
            record['content_type'] = response.headers.get('Content-Type','')
            if response.headers.get('Content-Encoding','identity') != 'identity':
                raise RuntimeError('Unexpected encoding')
            length = response.headers.get('Content-Length')
            if length and int(length) > cap:
                raise RuntimeError('Response cap before body')
            while True:
                part = response.read1(min(65536, cap+1-len(body)))
                if not part:
                    break
                body.extend(part)
                record['decoded_bytes'] += len(part)
                book['decoded_bytes'] += len(part)
                save(PRIVATE / 'ledger.json', book)
                if len(body)>cap or book['decoded_bytes']>32*1024**2:
                    raise RuntimeError('Decoded-byte ceiling')
        record['transit_sha256'] = hashlib.sha256(body).hexdigest()
        if record['kind']=='repository_html':
            from html.parser import HTMLParser
            class MetadataLinks(HTMLParser):
                def __init__(self):super().__init__();self.links=[];self.metadata=[]
                def handle_starttag(self,tag,attrs):
                    data=dict(attrs)
                    if tag=='a' and data.get('href') and any(token in data['href'].lower() for token in ('pdf','bitstream','download','fulltext')):
                        self.links.append(data['href'])
                    if tag=='meta' and any(token in data.get('name','').lower() for token in ('citation','identifier','rights','license')):
                        self.metadata.append({key:data.get(key) for key in ('name','content')})
            parser=MetadataLinks();parser.feed(body.decode('utf-8',errors='replace'))
            output={'links':parser.links,'metadata':parser.metadata,'raw_page_retained':False,'abstract_emitted':False}
            output_path=PRIVATE/(stem+'-links.json')
        elif record['kind'].startswith('methods_'):
            from r0r_methods_mask_v1 import extract_masked_methods, extract_masked_pdf_methods
            mask_path=ROOT/'tools/r0r_methods_mask_v1.py'
            mask_bytes=mask_path.read_bytes()
            record['mask_module_sha256']=hashlib.sha256(mask_bytes).hexdigest()
            (PRIVATE/'code'/(record['mask_module_sha256']+'.py')).write_bytes(mask_bytes)
            output = (extract_masked_methods(bytes(body)) if record['kind']=='methods_xml'
                      else extract_masked_pdf_methods(bytes(body)))
            if spec.get('expected_doi') and record['kind']=='methods_xml':
                import xml.etree.ElementTree as ET
                metadata_root=ET.fromstring(bytes(body))
                dois=[node.text for node in metadata_root.iter() if node.tag.split('}')[-1]=='article-id' and node.attrib.get('pub-id-type')=='doi']
                if spec['expected_doi'].lower() not in {value.lower() for value in dois if value}:
                    raise RuntimeError('Full-text DOI metadata does not match fixed source')
                record['full_text_doi_verified']=spec['expected_doi']
            output_path = PRIVATE / (stem + '-masked.json')
            record['unmasked_full_article_persisted'] = False
        else:
            output = json.loads(body)
            collection = {'activity.json':'activities','molecule.json':'molecules'}.get(urllib.parse.urlparse(spec['url']).path.rsplit('/',1)[-1])
            if collection:
                record['record_count_received']=len(output[collection])
                expected = set(urllib.parse.parse_qs(urllib.parse.urlparse(spec['url']).query)['only'][0].split(','))
                safe_aliases = {'type','units'} if collection == 'activities' else set()
                if any(not expected.issubset(row) or set(row) - expected - safe_aliases for row in output[collection]):
                    record['returned_field_names'] = sorted({key for row in output[collection] for key in row})
                    record['extra_field_names'] = sorted({key for row in output[collection] for key in row} - expected)
                    record['missing_field_names'] = sorted(expected - {key for row in output[collection] for key in row})
                    raise RuntimeError('Unexpected fields; projection rejected before agent view')
                if collection == 'activities':
                    if any(any(value is not None and not isinstance(value,str)
                               for key,value in row.items() if key in {'standard_type','standard_units','type','units'})
                           for row in output[collection]):
                        raise RuntimeError('Malformed readout metadata')
                    record['server_added_safe_metadata_aliases'] = sorted({key for row in output[collection] for key in row} & safe_aliases)
                maximum = 20 if collection == 'activities' else 240
                if len(output[collection]) > maximum:
                    raise RuntimeError('Record limit')
            if name.startswith('status-') and output.get('chembl_db_version')!='ChEMBL_37':
                raise RuntimeError('Unexpected ChEMBL release')
            output_path = PRIVATE / (stem + '.json')
        save(output_path, output)
        record.update(status='PASS', finished_utc=now(), output_path=str(output_path.relative_to(ROOT)),
                      output_sha256=hashlib.sha256(output_path.read_bytes()).hexdigest())
        save(PRIVATE / 'ledger.json', book)
        guard.finish('PASS', decoded_bytes=record['decoded_bytes'])
        # Never print scientific free text, values or molecular structures.
        print(json.dumps({'status':'PASS','source':name,'decoded_bytes':record['decoded_bytes'],
                          'collection_counts':{k:len(v) for k,v in output.items() if isinstance(v,list)}},indent=2))
        return 0
    except Exception as exc:
        if record is not None:
            record.update(status='STOP', error_type=type(exc).__name__, error=str(exc), finished_utc=now())
            if isinstance(exc, urllib.error.HTTPError):
                record['http_status'] = exc.code
            book['stopped_sources'].append(name)
            save(PRIVATE / 'ledger.json',book)
        if guard is not None:
            guard.finish('STOP',error_type=type(exc).__name__)
        print(json.dumps({'status':'STOP','source':name,'error_type':type(exc).__name__,'error':str(exc)}))
        return 2
    finally:
        lock_path.unlink(missing_ok=True)

if __name__ == '__main__':
    raise SystemExit(fetch(sys.argv[1]))
