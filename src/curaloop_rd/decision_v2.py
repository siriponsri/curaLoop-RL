"""Deterministic metadata decisions shared by both evaluation arms."""

from .contracts_v2 import claim, report


def decide(brief, catalogue):
    kind = brief['kind']
    records = {key: catalogue.inspect(key) for key in brief['source_ids']}
    claims = []
    def add(key, value, source, locator, state='VALUE', inference_rule=None):
        claims.append(claim(key, value, source, records[source]['sha256'], locator, state=state, inference_rule=inference_rule))
    if kind == 'endpoint':
        sid = brief['source_ids'][0]
        r = records[sid]
        selected = [v for v in r['readouts'] if v['tid'] == brief['tid']]
        if len(selected) != 1:
            raise ValueError('Unique requested readout required')
        readout = selected[0]
        for key in ('tid', 'name', 'type'):
            add(key, readout[key], sid, readout['locator'] + '/' + key)
        add('unit', readout['unit']['value'], sid, readout['locator'] + '/unit', readout['unit']['state'])
        disposition = 'METADATA_REPORT' if readout['unit']['state'] == 'VALUE' else 'BLOCKED_ENDPOINT_UNRESOLVED'
    elif kind == 'historical':
        a, b = brief['source_ids'][:2]
        for key, sid in (('published_selector', a), ('invalid_selector', b)):
            add(key, records[sid]['requested_version'], sid, '/request/params/version')
        for prefix, sid in (('published', a), ('invalid', b)):
            add(prefix + '_response_sha256', records[sid]['response_sha256'], sid, '/response_sha256')
            add(prefix + '_http_status', records[sid]['http_status'], sid, '/result/status_code')
        disposition = 'BLOCKED_HISTORICAL_IDENTITY'
    elif kind == 'identity':
        desc, proteins = brief['source_ids']
        target = records[desc]['targets'][0]
        accession = target['accession']
        # Token matching, never substring/name matching (NP_1 must not match NP_10).
        matches = [r for r in records[proteins]['proteins']
                   if any(part.strip().split(' ')[0] == accession for part in r['refseq'].split(';'))
                   and r['reviewed'] == 'reviewed']
        if len(matches) != 1:
            raise ValueError('Unique reviewed exact accession mapping required')
        add('target_refseq', accession, desc, target['locator'])
        add('uniprot_accession', matches[0]['entry'], proteins, matches[0]['locator'] + ', Entry/Reviewed/RefSeq')
        disposition = 'METADATA_REPORT'
    elif kind == 'rights':
        sid = brief['source_ids'][0]
        add('commercial_clearance', records[sid]['copyright_clearance'], sid, records[sid]['locator'], 'UNRESOLVED',
            'NLM_PUBLIC_HOSTING_NOT_RIGHTS_CERTIFICATE')
        disposition = 'BLOCKED_RIGHTS_UNRESOLVED'
    elif kind == 'unavailable':
        sid = brief['source_ids'][0]
        for i, item in enumerate(records[sid]['unavailable']):
            add('required_source_' + str(i), item['status'], sid, item['locator'] + '/status')
        disposition = 'BLOCKED_REQUIRED_SOURCE'
    else:
        raise ValueError('Unsupported bounded metadata intent')
    return report(brief['question'], claims, disposition,
                  ['CACHED_METADATA_NOT_ACTIVITY', 'ALL_CASE_SOURCES_DEVELOPMENT_EXPOSED',
                   'NO_HISTORICAL_ROW_EQUIVALENCE_OR_COMMERCIAL_CLEARANCE', 'NO_EXTERNAL_DELIVERY'],
                  {sid: {'sha256': records[sid]['sha256'], 'citation': records[sid]['citation'],
                         'measurement_status': 'METADATA_ONLY'} for sid in sorted({c['evidence']['source_id'] for c in claims})})
