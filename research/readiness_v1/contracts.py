"""Strict metadata observations and prospective benchmark gates."""

import hashlib
import json
import math
import re


class MetadataError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def strict_json(raw, byte_limit=2 * 1024**2):
    if not isinstance(raw, bytes) or len(raw) > byte_limit:
        raise MetadataError('Metadata byte bound exceeded')
    depth = 0
    quoted = escaped = False
    try:
        text = raw.decode('utf-8')
    except UnicodeError as exc:
        raise MetadataError('Invalid UTF-8') from exc
    for value in text:
        if quoted:
            if escaped:
                escaped = False
            elif value == '\\':
                escaped = True
            elif value == '"':
                quoted = False
        elif value == '"':
            quoted = True
        elif value in '[{':
            depth += 1
            if depth > 32:
                raise MetadataError('Metadata nesting bound exceeded')
        elif value in ']}':
            depth -= 1
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                raise MetadataError('Duplicate JSON key: ' + key)
            out[key] = value
        return out
    def constant(value):
        raise MetadataError('Nonfinite JSON constant: ' + value)
    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise MetadataError('Overflowing/nonfinite JSON number')
        return parsed
    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant, parse_float=finite_float)
    except (ValueError, RecursionError, UnicodeError) as exc:
        raise MetadataError(str(exc)) from exc
    return result


def positive_int(value):
    return type(value) is int and value > 0


def observe(mapping, key, pointer, validator=None):
    if key not in mapping:
        state, value = 'ABSENT', None
    elif mapping[key] is None:
        state, value = 'NULL', None
    else:
        value = mapping[key]
        state = 'VALUE' if validator is None or validator(value) else 'INVALID'
    return {'state': state, 'value': value, 'source_pointer': pointer}


def normalize_description(raw, requested_aid, retrieval_utc):
    obj = strict_json(raw)
    if type(obj) is not dict or set(obj) != {'PC_AssayContainer'}:
        raise MetadataError('Unsupported metadata envelope')
    containers = obj['PC_AssayContainer']
    if type(containers) is not list or len(containers) != 1 or type(containers[0]) is not dict:
        raise MetadataError('Expected one metadata container')
    if set(containers[0]) != {'assay'} or type(containers[0]['assay']) is not dict:
        raise MetadataError('Unexpected container payload')
    assay = containers[0]['assay']
    if set(assay) != {'descr'} or type(assay['descr']) is not dict:
        raise MetadataError('Data-bearing or unsupported assay payload')
    descr = assay['descr']
    aid = descr.get('aid')
    if type(aid) is not dict or not positive_int(aid.get('id')) or str(aid['id']) != requested_aid:
        raise MetadataError('Missing, invalid or wrong AID')
    definition_field = observe(descr, 'results', '/PC_AssayContainer/0/assay/descr/results', lambda value: type(value) is list)
    definitions = definition_field['value'] if definition_field['state'] == 'VALUE' else []
    if definition_field['state'] == 'INVALID' or len(definitions) > 2000:
        raise MetadataError('Invalid readout definitions')
    for item in definitions:
        if type(item) is not dict or not positive_int(item.get('tid')) or type(item.get('name')) is not str:
            raise MetadataError('Readout definition missing TID/name')
        if set(item) & {'sid', 'cid', 'data', 'values', 'value'}:
            raise MetadataError('Unexpected compound result content')
    pointer = '/PC_AssayContainer/0/assay/descr'
    targets = observe(descr, 'target', pointer + '/target', lambda value: type(value) is list)
    provider = observe(descr, 'aid_source', pointer + '/aid_source', lambda value: type(value) is dict)
    name = observe(descr, 'name', pointer + '/name', lambda value: type(value) is str and bool(value.strip()))
    return {'requested_aid': requested_aid, 'observed_aid': aid['id'], 'retrieval_utc': retrieval_utc,
            'response_sha256': hashlib.sha256(raw).hexdigest(),
            'version': observe(aid, 'version', pointer + '/aid/version', positive_int),
            'revision': observe(descr, 'revision', pointer + '/revision', positive_int),
            'last_data_change': observe(descr, 'last-data-change', pointer + '/last-data-change'),
            'date_meaning': 'LastDataChange_IS_NOT_ASSUMED_SI_LAST_MODIFICATION',
            'name': name, 'targets': targets, 'provider': provider,
            'readout_definitions_field': definition_field,
            'readout_definitions': [
                {'tid': item['tid'], 'name': item['name'],
                 'unit': observe(item, 'unit', pointer + '/results/' + str(i) + '/unit'),
                 'unit_enum_meaning': 'NOT_DECODED_WITHOUT_PINNED_SCHEMA'}
                for i, item in enumerate(definitions)],
            'metadata_endpoint_only': True, 'activity_rows_processed': 0,
            'scientific_plan_ready': False,
            'unresolved': ['Readout/phenotype choice and qualifier interpretation',
                           'Measured/censored/untested compound coverage', 'Provider row rights',
                           'Biological-family independence and reserved-panel overlap']}


def compare_version(record, expected):
    if not positive_int(expected.get('version')) or not positive_int(expected.get('revision')):
        raise MetadataError('Invalid published version identity')
    fields = {}
    for key in ('version', 'revision'):
        obs = record[key]
        fields[key] = ('MATCH' if obs['value'] == expected[key] else 'DIFFERENT') if obs['state'] == 'VALUE' else 'INDETERMINATE'
    pair = ('DIFFERENT' if 'DIFFERENT' in fields.values() else
            'MATCH_OBSERVED_VERSION_METADATA' if set(fields.values()) == {'MATCH'} else 'INDETERMINATE')
    return {'version_revision_verdict': pair, 'per_field': fields,
            'date_verdict': 'NOT_COMPARABLE_OR_ABSENT',
            'complete_publication_tuple': 'INDETERMINATE',
            'published_last_modification': expected['last_modified'],
            'historical_activity_rows_equivalent': 'NOT_CERTIFIED'}


def registry_coverage(records, expected_aids):
    actual = [r['requested_aid'] for r in records]
    if len(actual) != len(set(actual)) or len(expected_aids) != len(set(expected_aids)):
        raise MetadataError('Duplicate roster identity')
    if not set(actual).issubset(expected_aids):
        raise MetadataError('Unexpected roster identity')
    missing = sorted(set(expected_aids) - set(actual), key=int)
    return {'description_roster_complete': not missing, 'observed_records': len(records),
            'expected_records': len(expected_aids), 'missing_aids': missing,
            'eligible_scientific_cohort': 'UNKNOWN'}


def benchmark_blockers(manifest):
    blockers = []
    if manifest['native_output'] != manifest['curaloop_current_output']:
        blockers.append('OUTPUT_OBJECTIVE_MISMATCH')
    if manifest['commercial_data_reuse'] != 'CLEARED_FOR_INTENDED_USE':
        blockers.append('COMMERCIAL_DATA_REUSE_NOT_CLEARED')
    if manifest['native_full_stack_cpu_readiness'] != 'VERIFIED':
        blockers.append('NATIVE_RUNTIME_NOT_VERIFIED')
    if manifest['prospective_split']['status'] != 'FROZEN_VERIFIED_ROSTER':
        blockers.append('HOLDOUT_ROSTER_NOT_FROZEN')
    return blockers


def prospective_role(group, exposed_groups, groups_resolved, salt):
    if (groups_resolved is not True or type(group) is not str or not group
            or type(exposed_groups) is not set or any(type(item) is not str for item in exposed_groups)
            or type(salt) is not str or not salt or group in exposed_groups):
        return 'QUARANTINE'
    value = int(hashlib.sha256((salt + ':' + group).encode()).hexdigest(), 16) % 100
    return 'development' if value < 20 else 'validation' if value < 40 else 'evaluation'


def verify_manifest(manifest, expected_digest):
    if digest(manifest) != expected_digest:
        raise MetadataError('Changed exposure/split manifest')
    return True


def feasibility_f1(feasible, attempted, solved, rule):
    """Synthetic metric concordance diagnostic, not a benchmark evaluation."""
    if not len(feasible) == len(attempted) == len(solved) or not feasible:
        raise MetadataError('Equal nonempty synthetic arrays required')
    if rule not in ('pinned_code_attempt', 'card_full_solution'):
        raise MetadataError('Unknown metric definition')
    if any(type(v) is not bool for v in feasible + attempted + solved):
        raise MetadataError('Boolean synthetic flags required')
    positive_feasible = attempted if rule == 'pinned_code_attempt' else [a and s for a, s in zip(attempted, solved)]
    tp = sum(f and p for f, p in zip(feasible, positive_feasible))
    fp = sum(not f and a for f, a in zip(feasible, attempted))
    fn = sum(f and not p for f, p in zip(feasible, positive_feasible))
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.
