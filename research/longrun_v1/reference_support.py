"""Independent source locator checks and exact authored-reference claim scoring."""

import csv
import hashlib
import io
import json


def verify_reference(root, registry, item):
    e = item['evidence']
    record = registry[e['source_id']]
    raw = (root / record['path']).read_bytes()
    if hashlib.sha256(raw).hexdigest() != e['source_sha256'] or e['source_sha256'] != record['sha256']:
        raise ValueError('Reference source identity differs')
    locator = e['locator']
    if locator.startswith('/'):
        obj = json.loads(raw)
        parts = [v.replace('~1', '/').replace('~0', '~') for v in locator.split('/')[1:]]
        parent = obj
        for part in parts[:-1]:
            parent = parent[int(part)] if type(parent) is list else parent[part]
        key = parts[-1]
        if item['state'] == 'ABSENT':
            if type(parent) is not dict or key in parent or item['value'] is not None:
                raise ValueError('Reference missing leaf is not absent')
        else:
            value = parent[int(key)] if type(parent) is list else parent[key]
            if type(value) is not type(item['value']) or value != item['value']:
                raise ValueError('Reference value/type differs at source locator')
    elif locator == 'TSV line 26, Entry/Reviewed/RefSeq':
        rows = list(csv.DictReader(io.StringIO(raw.decode()), delimiter='\t'))
        row = rows[24]
        if (row['Entry'] != item['value'] or row['Reviewed'] != 'reviewed'
                or 'NP_002084.2 [P49841-2]' not in [v.strip() for v in row['RefSeq'].split(';')]):
            raise ValueError('Reference exact reviewed protein mapping differs')
    elif locator == 'lines 25,27':
        lines = raw.decode().splitlines()
        if (item.get('inference_rule') != 'NLM_PUBLIC_HOSTING_NOT_RIGHTS_CERTIFICATE'
                or item['state'] != 'UNRESOLVED' or item['value'] != 'NOT_ESTABLISHED_BY_PUBLIC_HOSTING'
                or 'copyright' not in lines[24].lower() or 'responsib' not in lines[26].lower()):
            raise ValueError('Reviewed policy inference support differs')
    else:
        raise ValueError('Unreviewed reference locator')


def score(value, reference, registry):
    def encoded(item):
        return json.dumps(item, sort_keys=True, separators=(',', ':'), allow_nan=False)
    required = {encoded(c) for c in reference['claims']}
    actual = [encoded(c) for c in value['claims']]
    seen = set(actual)
    missing = len(required - seen)
    unsupported = len(seen - required) + len(actual) - len(seen)
    ledger = value.get('source_ledger', {})
    source_ids = {c['evidence']['source_id'] for c in reference['claims']}
    citations_correct = set(ledger) == source_ids and all(ledger[sid] == {
        'sha256': registry[sid]['sha256'], 'citation': registry[sid]['citation'],
        'measurement_status': 'METADATA_ONLY'} for sid in source_ids)
    return {'correct': missing == unsupported == 0 and citations_correct
                       and value['disposition'] == reference['disposition'],
            'mandatory_claims': len(required), 'missing_claims': missing,
            'unsupported_claims': unsupported, 'source_ledger_correct': citations_correct}
