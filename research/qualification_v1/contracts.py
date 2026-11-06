"""Strict, outcome-aware contracts; no policy/model fitting or final-role assignment."""

import hashlib
import math
import re
import shlex
from collections import Counter

from research.readiness_v1.contracts import MetadataError, strict_json


class QualificationError(ValueError):
    pass


def positive_id(value):
    if type(value) is int:
        return value > 0
    return type(value) is str and bool(re.fullmatch(r'[1-9][0-9]*', value))


def programme_rights(record, policy, notices_checked=False):
    category = record.get('project_category_raw')
    if type(category) is not int or category not in (1, 2):
        return 'QUARANTINE_PROGRAMME_NOT_SUPPORTED'
    if policy.get('intended_use') != 'INTERNAL_NONCOMMERCIAL_COMPUTATIONAL_QUALIFICATION':
        return 'QUARANTINE_INTENDED_USE'
    if not notices_checked or record.get('restriction_flags'):
        return 'QUARANTINE_NOTICE_REVIEW'
    if not any(p.get('category') == category and p.get('url', '').startswith('https://grants.nih.gov/')
               for p in policy.get('policy_evidence', [])):
        return 'QUARANTINE_POLICY_EVIDENCE'
    return 'INTERNAL_RESEARCH_USE_SUPPORTED_BY_MLP_POLICY'


def parse_source_script(text):
    tokens = shlex.split(text, comments=True, posix=True)
    if tokens[:2] != ['python', 'pubchem_retrieve.py']:
        raise QualificationError('Unsupported source command; never execute it')
    allowed = {'--AID', '--AID_DR', '--list_of_sd_cols', '--list_of_dr_cols', '--transform_dr', '--save_dir'}
    out, current = {}, None
    for token in tokens[2:]:
        if token.startswith('--'):
            if token not in allowed or token in out:
                raise QualificationError('Unsupported or duplicate source option')
            current = token
            out[current] = []
        elif current is None or token in (';', '&&', '|', '>', '<'):
            raise QualificationError('Unsupported source token')
        else:
            out[current].append(token)
    for required in ('--AID', '--list_of_sd_cols', '--list_of_dr_cols', '--transform_dr', '--save_dir'):
        if not out.get(required):
            raise QualificationError('Missing required source option')
    for key in ('--AID', '--transform_dr', '--save_dir', '--AID_DR'):
        if key in out and len(out[key]) != 1:
            raise QualificationError('Scalar source option is not scalar')
    primary = out['--AID'][0]
    confirmation = out.get('--AID_DR', [primary])[0]
    if not positive_id(primary) or not positive_id(confirmation):
        raise QualificationError('Invalid source AID')
    if out['--transform_dr'][0] not in ('pXC50', 'minus', 'no'):
        raise QualificationError('Unknown source transform')
    return {'primary_aid': primary, 'confirmation_aid': confirmation,
            'primary_columns': out['--list_of_sd_cols'], 'confirmation_columns': out['--list_of_dr_cols'],
            'source_transform': out['--transform_dr'][0]}


def bind_columns(definitions, names):
    if type(definitions) is not list or type(names) is not list or not names:
        raise QualificationError('Missing readout definition/selection')
    if any(type(d) is not dict for d in definitions):
        raise QualificationError('Malformed readout definition')
    bindings = []
    for name in names:
        matches = [d for d in definitions if d.get('name') == name]
        if (len(matches) != 1 or type(matches[0].get('tid')) is not int or not positive_id(matches[0].get('tid'))
                or type(matches[0].get('type')) is not int or matches[0]['type'] not in (1, 2, 3, 4)):
            raise QualificationError('Missing/ambiguous source readout binding')
        d = matches[0]
        if ('unit' in d and d['unit'] is not None
                and (type(d['unit']) is not int or d['unit'] not in {*range(1, 28), 254, 255})):
            raise QualificationError('Malformed unit enum')
        if 'sunit' in d and d['sunit'] is not None and type(d['sunit']) is not str:
            raise QualificationError('Malformed custom unit')
        bindings.append({'name': name, 'tid': d['tid'], 'type': d.get('type'),
                         'unit_present': 'unit' in d, 'unit': d.get('unit'),
                         'sunit_present': 'sunit' in d, 'sunit': d.get('sunit')})
    if len({r['tid'] for r in bindings}) != len(bindings):
        raise QualificationError('Duplicate selected readout')
    return bindings


def protected_identity_index(versions, registry):
    expected_top = {'task_id', 'role', 'family_id', 'family', 'source_role', 'source_member',
                    'member_sha256', 'records', 'outcome_values_present'}
    expected_record = {'candidate_id', 'canonical_smiles', 'source_row', 'morgan_on_bits', 'scaffold'}
    canonical, groups, source_count, positions = set(), set(), 0, 0
    for feature in versions:
        if (set(feature) != expected_top or feature['role'] != 'final'
                or feature['outcome_values_present'] is not False or type(feature['records']) is not list):
            raise QualificationError('Not a verified label-free reserved feature artifact')
        groups.add(feature['family_id'])
        source_count += 1
        for row in feature['records']:
            if set(row) != expected_record or type(row['canonical_smiles']) is not str or not row['canonical_smiles']:
                raise QualificationError('Unexpected protected feature fields')
            value = row['canonical_smiles']
            if row['candidate_id'] != 's-' + hashlib.sha256(value.encode()).hexdigest():
                raise QualificationError('Protected canonical identity mismatch')
            canonical.add(value)
            positions += 1
    protected_assays = [r for r in registry['assays'] if r['family_id'] in groups]
    return {'canonical_smiles': sorted(canonical), 'family_ids': sorted(groups),
            'assay_ids': sorted({r['assay_id'] for r in protected_assays}),
            'uniprot_accessions': sorted({r['uniprot_accession'] for r in protected_assays}),
            'versioned_feature_files': source_count, 'record_positions': positions,
            'unique_canonical_structures': len(canonical), 'outcome_values_present': False}


def family_gate(resolved_accessions, known_families, protected, resolved):
    if resolved is not True or type(resolved_accessions) is not set or not resolved_accessions:
        return 'QUARANTINE_UNRESOLVED_TARGET_OR_FAMILY'
    if resolved_accessions & set(protected['uniprot_accessions']):
        return 'QUARANTINE_PROTECTED_PROTEIN'
    if any(a not in known_families for a in resolved_accessions):
        return 'QUARANTINE_UNRESOLVED_TARGET_OR_FAMILY'
    groups = {known_families[a] for a in resolved_accessions}
    return 'QUARANTINE_PROTECTED_FAMILY' if groups & set(protected['family_ids']) else 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY'


def sample_ids(ids, salt, limit, excluded=None):
    if type(limit) is not int or not 1 <= limit <= 128 or type(salt) is not str or not salt:
        raise QualificationError('Invalid frozen sampling bound')
    if any(not positive_id(i) for i in ids):
        raise QualificationError('Invalid sample identifier')
    unique = {str(i) for i in ids} - {str(i) for i in (excluded or [])}
    return sorted(unique, key=lambda i: hashlib.sha256((salt + ':' + i).encode()).hexdigest())[:limit]


def exact_sid_filter(ids, allowed, limit=128):
    if (type(ids) is not list or not ids or len(ids) > limit
            or any(type(i) is not str or not positive_id(i) for i in ids)
            or len(set(ids)) != len(ids) or not set(ids) <= set(allowed)):
        raise QualificationError('Invalid or unapproved exact SID filter')
    return {'sid': ','.join(ids)}


def value_state(value, concentration=False, comment=None):
    if value is None:
        return {'state': 'NULL', 'value': None}
    if type(value) in (int, float):
        if not math.isfinite(value):
            raise QualificationError('Nonfinite observation')
        state = ('INVALID_NONPOSITIVE_CONCENTRATION' if concentration and value <= 0
                 else 'QUALIFIER_REVIEW' if comment else 'EXACT_NUMERIC')
        return {'state': state, 'value': value}
    if type(value) is bool:
        return {'state': 'BOOLEAN', 'value': value}
    if type(value) is not str:
        return {'state': 'INVALID_TYPE', 'value': None}
    match = re.fullmatch(r'\s*(<=|>=|<|>)\s*([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)\s*', value)
    if match:
        bound = float(match[2])
        if not math.isfinite(bound):
            raise QualificationError('Nonfinite censor bound')
        return {'state': 'CENSORED', 'relation': match[1], 'bound': bound, 'value': value}
    return {'state': 'EMPTY_TEXT' if not value.strip() else 'QUALITATIVE_OR_UNRESOLVED_TEXT', 'value': value}


def normalize_observations(raw, aid, allowed_sids, bindings, *, role, expected_version, expected_revision):
    if role != 'DEVELOPMENT_EXPOSED':
        raise QualificationError('Explicit development exposure role required')
    if (type(expected_version) is not int or expected_version <= 0
            or type(expected_revision) is not int or expected_revision <= 0):
        raise QualificationError('Expected source version/revision must be explicit')
    obj = strict_json(raw, byte_limit=16 * 1024**2)
    if type(obj) is not dict or set(obj) != {'PC_AssayContainer'}:
        raise QualificationError('Unsupported observation envelope')
    containers = obj['PC_AssayContainer']
    if type(containers) is not list or len(containers) != 1:
        raise QualificationError('Expected one assay response')
    container = containers[0]
    if type(container) is not dict or set(container) - {'assay', 'data'}:
        raise QualificationError('Unexpected assay fields')
    descriptor = container.get('assay', {}).get('descr')
    if (type(descriptor) is not dict or type(descriptor.get('aid', {}).get('id')) is not int
            or str(descriptor.get('aid', {}).get('id')) != aid):
        raise QualificationError('Wrong or missing returned assay identity')
    if (type(descriptor['aid'].get('version')) is not int or type(descriptor.get('revision')) is not int
            or descriptor['aid']['version'] != expected_version or descriptor['revision'] != expected_revision):
        raise QualificationError('Missing or drifting assay version/revision metadata')
    if bind_columns(descriptor.get('results'), [b['name'] for b in bindings]) != bindings:
        raise QualificationError('Selected readout identity/type/unit drift')
    rows = container.get('data')
    if type(rows) is not list or len(rows) > len(allowed_sids) * 4:
        raise QualificationError('Missing or excessive observation rows')
    # Check every identifier before touching any outcome/readout value.
    for row in rows:
        if type(row) is not dict or not positive_id(row.get('sid')) or str(row['sid']) not in allowed_sids:
            raise QualificationError('Unexpected or protected row identifier; values not interpreted')
    by_tid = {b['tid']: b for b in bindings}
    declared_tids = {d['tid'] for d in descriptor['results']}
    normalized = []
    for row in rows:
        sid = str(row['sid'])
        if 'comment' in row and row['comment'] is not None and type(row['comment']) is not str:
            raise QualificationError('Malformed result comment')
        comment_state = ('ABSENT' if 'comment' not in row else 'NULL' if row['comment'] is None
                         else 'EMPTY_TEXT' if not row['comment'].strip() else 'VALUE')
        for field in ('outcome', 'version'):
            if field in row and row[field] is not None:
                if type(row[field]) is not int or (field == 'outcome' and row[field] not in (1, 2, 3, 4, 5)) or (field == 'version' and row[field] < 0):
                    raise QualificationError('Invalid result outcome/version type')
        cells = row.get('data', [])
        if type(cells) is not list:
            raise QualificationError('Invalid typed readout list')
        seen, selected = set(), {}
        for cell in cells:
            tid = cell.get('tid') if type(cell) is dict else None
            if type(tid) is not int or not positive_id(tid) or tid in seen or tid not in declared_tids:
                raise QualificationError('Invalid/duplicate readout identity')
            seen.add(tid)
            if tid not in by_tid:
                continue  # Other declared columns remain raw/private, not scientific endpoints.
            value = cell.get('value')
            if type(value) is not dict or len(value) != 1 or not set(value) <= {'ival', 'fval', 'bval', 'sval'}:
                raise QualificationError('Invalid typed observation')
            kind, item = next(iter(value.items()))
            expected = {1: 'fval', 2: 'ival', 3: 'bval', 4: 'sval'}.get(by_tid[tid]['type'])
            if kind != expected:
                raise QualificationError('Readout value/type mismatch')
            if item is not None and not (
                    kind == 'fval' and type(item) in (int, float)
                    or kind == 'ival' and type(item) is int
                    or kind == 'bval' and type(item) is bool
                    or kind == 'sval' and type(item) is str):
                raise QualificationError('Typed observation payload differs')
            qualifier = 'UNRESOLVED_NULL_COMMENT' if comment_state == 'NULL' else row.get('comment')
            state = value_state(item, concentration=by_tid[tid].get('unit') in (4, 5, 6, 7, 8, 14), comment=qualifier)
            selected[str(tid)] = {**state, 'unit_present': by_tid[tid]['unit_present'], 'unit': by_tid[tid]['unit'], 'type': kind}
        for tid, binding in by_tid.items():
            if str(tid) not in selected:
                selected[str(tid)] = {'state': 'MISSING_TID', 'unit_present': binding['unit_present'], 'unit': binding['unit']}
        normalized.append({'sid': sid, 'source_outcome': row.get('outcome'), 'outcome_present': 'outcome' in row,
                           'outcome_state': 'ABSENT' if 'outcome' not in row else 'NULL' if row['outcome'] is None else 'VALUE',
                           'result_version': row.get('version'),
                           'result_version_state': 'ABSENT' if 'version' not in row else 'NULL' if row['version'] is None else 'VALUE',
                           'comment_present': 'comment' in row, 'comment_state': comment_state, 'readouts': selected})
    return {'aid': aid, 'role': role, 'assay_version': expected_version, 'assay_revision': expected_revision,
            'records': normalized, 'returned_sids': sorted({r['sid'] for r in normalized}, key=int),
            'historical_rows_equivalent': 'NOT_CERTIFIED', 'source_sha256': hashlib.sha256(raw).hexdigest()}


def replicate_state(records):
    if not records:
        return 'NO_RETURNED_OBSERVATION_NOT_PROOF_UNTESTED'
    signatures = {repr((r.get('source_outcome'), r.get('readouts'))) for r in records}
    return 'CONFLICTING_REPLICATES' if len(signatures) > 1 else 'CONSISTENT_OBSERVATION'


def coverage(sampled, returned, eligible, listed_total=None):
    if not set(eligible) <= set(returned) <= set(sampled):
        raise QualificationError('Coverage sets are inconsistent')
    return {'listed_total': listed_total, 'sampled': len(set(sampled)), 'returned': len(set(returned)),
            'eligible': len(set(eligible)), 'unreturned_sampled': len(set(sampled) - set(returned)),
            'unreturned_is_not_assumed_untested': True}


def public_aggregate(observations, sampled):
    if observations.get('role') != 'DEVELOPMENT_EXPOSED':
        raise QualificationError('Only declared development qualification can be reported')
    records = observations['records']
    counts = Counter(cell['state'] for row in records for cell in row['readouts'].values())
    return {'aid': observations['aid'], 'role': 'DEVELOPMENT_EXPOSED', 'record_count': len(records),
            'sampled_sid_count': len(sampled), 'returned_sid_count': len(observations['returned_sids']),
            'readout_state_counts': dict(counts), 'source_sha256': observations['source_sha256'],
            'raw_outcomes_or_values_included': False, 'scientific_campaigns': 0,
            'historical_rows_equivalent': 'NOT_CERTIFIED'}
