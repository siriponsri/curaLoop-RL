"""Value-free native-assay presence projection, after complete identity validation."""

import json
from research.qualification_v1.contracts import strict_json, bind_columns, positive_id


def project(raw, request):
    obj = strict_json(raw, byte_limit=16 * 1024**2)
    if type(obj) is not dict or set(obj) != {'PC_AssaySubmit'}:
        raise ValueError('Native submit envelope required')
    submit = obj['PC_AssaySubmit']
    if type(submit) is not dict or set(submit) != {'assay', 'data'}:
        raise ValueError('Native submit fields differ')
    descr = submit['assay']['descr']
    if (type(descr['aid']['id']) is not int or type(descr['aid']['version']) is not int
            or type(descr['revision']) is not int or not positive_id(descr['aid']['id'])
            or str(descr['aid']['id']) != request['aid'] or descr['aid']['version'] != request['version']
            or descr['revision'] != request['revision']):
        raise ValueError('Exact assay version and revision required')
    wanted = request['sids']
    if (type(wanted) is not list or not wanted or len(wanted) != len(set(wanted))
            or any(type(v) is not str or not positive_id(v) for v in wanted)):
        raise ValueError('Exact unique requested identifiers required')
    rows = submit['data']
    if type(rows) is not list:
        raise ValueError('Row list required')
    # Complete identifier pass BEFORE any readout data access, including presence.
    identifiers = []
    for row in rows:
        if type(row) is not dict or type(row.get('sid')) is not int or str(row['sid']) not in wanted:
            raise ValueError('Unexpected row identifier; readouts not inspected')
        identifiers.append(str(row['sid']))
    if len(identifiers) != len(set(identifiers)) or set(identifiers) != set(wanted):
        raise ValueError('Complete unique row coverage required')
    results = descr['results']
    if type(results) is not list or any(type(r) is not dict or type(r.get('tid')) is not int
                                        or not positive_id(r['tid']) for r in results):
        raise ValueError('Positive declared TID identities required')
    tids = [r['tid'] for r in results]
    if len(tids) != len(set(tids)):
        raise ValueError('Duplicate result definition')
    if not request['bindings'] or bind_columns(results, [b['name'] for b in request['bindings']]) != request['bindings']:
        raise ValueError('Nonempty exact selected readout definitions required')
    counts = {str(b['tid']): 0 for b in request['bindings']}
    complete = 0
    for row in rows:
        data = row.get('data', [])
        if type(data) is not list or any(type(c) is not dict or type(c.get('tid')) is not int for c in data):
            raise ValueError('Readout cell shape differs')
        cell_tids = [c['tid'] for c in data]
        if len(cell_tids) != len(set(cell_tids)) or not set(cell_tids) <= set(tids):
            raise ValueError('Duplicate row readout')
        for tid in counts:
            counts[tid] += int(int(tid) in cell_tids)
        complete += int(all(int(tid) in cell_tids for tid in counts))
    return {'status': 'PASS_VALUE_FREE_PRESENCE_ONLY', 'aid': request['aid'],
            'version': request['version'], 'revision': request['revision'], 'validated_rows': len(rows),
            'selected_readouts': [{'tid': b['tid'], 'name': b['name'], 'present_rows': counts[str(b['tid'])],
                                   'missing_rows': len(rows) - counts[str(b['tid'])]} for b in request['bindings']],
            'rows_with_all_selected_tids': complete, 'readout_values_or_outcomes_inspected': False,
            'eligibility_established': False, 'additional_source_requests': 0}
