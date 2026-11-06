"""Evidence reports support unresolved fields and useful blocked dispositions."""

import hashlib
import json


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def field(record, key):
    return {'state': 'ABSENT', 'value': None} if key not in record else {
        'state': 'NULL' if record[key] is None else 'VALUE', 'value': record[key]}


def claim(key, value, source_id, source_sha256, locator, *, state='VALUE', inference_rule=None):
    if state not in ('VALUE', 'ABSENT', 'NULL', 'UNRESOLVED') or not locator:
        raise ValueError('Explicit evidence state and locator required')
    result = {'key': key, 'state': state, 'value': value,
              'evidence': {'source_id': source_id, 'source_sha256': source_sha256, 'locator': locator}}
    if inference_rule:
        if inference_rule != 'NLM_PUBLIC_HOSTING_NOT_RIGHTS_CERTIFICATE':
            raise ValueError('Unknown bounded inference rule')
        result['inference_rule'] = inference_rule
    return result


def report(question, claims, disposition, limits, source_ledger):
    if not claims or len({c['key'] for c in claims}) != len(claims):
        raise ValueError('Unique atomic claims required')
    if disposition not in ('METADATA_REPORT', 'BLOCKED_ENDPOINT_UNRESOLVED', 'BLOCKED_HISTORICAL_IDENTITY',
                            'BLOCKED_RIGHTS_UNRESOLVED', 'BLOCKED_REQUIRED_SOURCE'):
        raise ValueError('Unapproved disposition')
    if set(source_ledger) != {c['evidence']['source_id'] for c in claims}:
        raise ValueError('Every claim source needs exactly one portable citation entry')
    body = {'schema': 'curaloop.evidence-report.v2', 'question': question, 'claims': claims, 'source_ledger': source_ledger,
            'disposition': disposition, 'limits': limits, 'scope': 'CACHED_REAL_METADATA_ONLY',
            'scientific_results': None, 'external_delivery': False, 'live_agent': False}
    return dict(body, report_sha256=digest(body))


def validate_report(value):
    body = {k: v for k, v in value.items() if k != 'report_sha256'}
    if value.get('report_sha256') != digest(body):
        raise ValueError('Report identity changed')
    if report(value['question'], value['claims'], value['disposition'], value['limits'], value['source_ledger']) != value:
        raise ValueError('Report fields differ from the versioned contract')
    for c in value['claims']:
        e = c['evidence']
        if claim(c['key'], c['value'], e['source_id'], e['source_sha256'], e['locator'], state=c['state'],
                 inference_rule=c.get('inference_rule')) != c:
            raise ValueError('Malformed atomic claim')
    return value
