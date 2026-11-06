"""Metadata-first network phases; activity requires a later reviewed release manifest."""

import csv
import hashlib
import importlib.util
import io
import json
import os
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone

from .audit import write_new
from .contracts import QualificationError, family_gate
from .transport import BoundedTransport


def read(path):
    return json.loads(path.read_text())


def save_ledger(path, ledger):
    temp = path.with_suffix('.tmp')
    with temp.open('w', encoding='utf-8', newline='\n') as f:
        json.dump(ledger, f, indent=2, allow_nan=False)
        f.write('\n')
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


class Client:
    def __init__(self, root, output, service, specifications):
        self.root, self.output, self.service = root, output, service
        self.policy = read(root / 'research/configs/goal4r2a3_policy_v1.json')
        self.ledger_path = root / 'network-ledger.json'
        self.ledger = read(self.ledger_path) if self.ledger_path.exists() else {'requests': [], 'stopped_services': []}
        if service in self.ledger['stopped_services'] or any(r['status'] == 'RESERVED' for r in self.ledger['requests']):
            raise QualificationError('Stopped service or unresolved network reservation')
        used = sum(r['service'] == service for r in self.ledger['requests'])
        limit = self.policy['maximum_uniprot_metadata_requests' if service == 'uniprot' else 'maximum_pug_requests']
        remaining = limit - used
        byte_remaining = self.policy['cumulative_response_byte_ceiling'] - sum(r['charged_decoded_bytes'] for r in self.ledger['requests'])
        if remaining <= 0 or byte_remaining <= 0:
            raise QualificationError('Cumulative network envelope exhausted')
        url = 'https://rest.uniprot.org' if service == 'uniprot' else 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
        self.guard = BoundedTransport(url, specifications, remaining,
                                      min(self.policy['response_byte_ceiling'], byte_remaining), byte_remaining,
                                      interval=self.policy['minimum_interval_seconds'])
        source = root / 'private-inputs/private-tools' / (service + '_rest_request.py' if service == 'uniprot' else 'pubchem_rest_request.py')
        if hashlib.sha256(source.read_bytes()).hexdigest() != self.policy['pubchem_client_sha256']:
            raise QualificationError('Pinned skill client bytes differ')
        spec = importlib.util.spec_from_file_location(service + '_skill_client', source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.client = self.guard.bind(module)

    def stop(self, reason):
        self.guard.failed = True
        if self.service not in self.ledger['stopped_services']:
            self.ledger['stopped_services'].append(self.service)
        self.ledger.setdefault('stop_events', []).append({'service': self.service, 'reason': reason,
                                                         'utc': datetime.now(timezone.utc).isoformat()})
        save_ledger(self.ledger_path, self.ledger)

    def request(self, specification, name):
        output = self.output / (name + '.txt')
        if output.exists():
            raise QualificationError('Request artifact already exists')
        # Reserve a request and its maximum incoming bytes durably before dispatch.
        record = {'service': self.service, 'path': specification['path'], 'params': specification.get('params', {}),
                  'utc': datetime.now(timezone.utc).isoformat(), 'status': 'RESERVED',
                  'charged_decoded_bytes': self.guard.byte_limit, 'output': output.relative_to(self.root).as_posix()}
        self.ledger['requests'].append(record)
        save_ledger(self.ledger_path, self.ledger)
        payload = {'base_url': self.guard.base_url, 'path': specification['path'], 'params': specification.get('params', {}),
                   'method': 'GET', 'response_format': 'text', 'save_raw': True,
                   'raw_output_path': str(output), 'timeout_sec': self.policy['per_request_timeout_seconds'], 'max_items': 1}
        receipt = {'request': payload, 'request_utc': record['utc']}
        try:
            result = self.client.execute(payload)
            receipt['result'] = result
            if not result.get('ok'):
                raise QualificationError('Source request failed; no retry/fallback')
            trace = self.guard.attempts[-1]
            data = output.read_bytes()
            assert len(data) == trace['decoded_bytes_observed'] and hashlib.sha256(data).hexdigest() == trace['decoded_sha256']
            record.update(status='COMPLETED', charged_decoded_bytes=trace['decoded_bytes_observed'])
            receipt.update(response_sha256=trace['decoded_sha256'], response_bytes=len(data), transport=trace)
            return data, receipt
        except Exception as error:
            observed = self.guard.attempts[-1]['decoded_bytes_observed'] if self.guard.attempts else 0
            record.update(status='FAILED', charged_decoded_bytes=observed, error_type=type(error).__name__)
            self.guard.failed = True
            if self.service not in self.ledger['stopped_services']:
                self.ledger['stopped_services'].append(self.service)
            receipt.update(error_type=type(error).__name__, transport=self.guard.attempts[-1] if self.guard.attempts else None)
            raise
        finally:
            save_ledger(self.ledger_path, self.ledger)
            write_new(self.output / (name + '-receipt.json'), receipt)


def family_overlay(root, proteins, protection):
    from research.benchmark_v3.families import normalize, family_annotation
    from research.benchmark_v3.family_closure import ambiguity_reason, iprs
    source = root / 'private-inputs/protection-inputs'
    registry = read(source / 'family-registry-v3.json')
    types = {}
    type_path = source / 'interpro-ftp-entries110-curl-v2/body'
    if hashlib.sha256(type_path.read_bytes()).hexdigest() != '1d247a42670d4a2913cec9f2a58813135c736d65128c1078d9c5eac797ffef1c':
        raise QualificationError('Pinned family type listing differs')
    for line in type_path.read_text().splitlines()[1:]:
        accession, kind, _ = line.split('\t', 2)
        types[accession] = kind.lower().replace(' ', '_')
    cached = read(source / 'uniprot-family-bulk-v1/families.json') + read(source / 'uniprot-family-exposure-v1/families.json')
    cached_by_acc = {r['Entry']: r for r in cached}
    protected_names = {normalize(n) for r in registry['family_records'] if r['family_id'] in protection['family_ids'] for n in r['broad_names_merged']}
    protected_iprs = {i for a in protection['uniprot_accessions'] for i in iprs(cached_by_acc[a])
                      if types.get(i) in ('family', 'homologous_superfamily')}
    current_by_acc = {p['Entry']: p for p in proteins}
    unresolved_current_anchors = []
    for accession in protection['uniprot_accessions']:
        current = current_by_acc.get(accession)
        annotation = family_annotation(current) if current else None
        if not current or not annotation or ambiguity_reason(current) or any(i not in types for i in iprs(current)):
            unresolved_current_anchors.append(accession)
            continue
        protected_names.update(annotation[1])
        protected_iprs.update(i for i in iprs(current) if types.get(i) in ('family', 'homologous_superfamily'))
    family_sets = defaultdict(set)
    for row in registry['assays']:
        family_sets[row['uniprot_accession']].add(row['family_id'])
    known = {a: next(iter(f)) for a, f in family_sets.items() if len(f) == 1}
    result = {}
    for protein in proteins:
        a = protein['Entry']
        verdict = family_gate({a}, known, protection, True)
        annotation = family_annotation(protein)
        if verdict.startswith('NO_KNOWN'):
            if unresolved_current_anchors:
                verdict = 'QUARANTINE_CURRENT_PROTECTED_ANNOTATION_UNRESOLVED'
            elif not annotation or ambiguity_reason(protein) or any(i not in types for i in iprs(protein)):
                verdict = 'QUARANTINE_UNRESOLVED_CURRENT_ANNOTATION'
            elif set(annotation[1]) & protected_names or iprs(protein) & protected_iprs:
                verdict = 'QUARANTINE_SHARED_PROTECTED_FAMILY_OR_SUPERFAMILY'
        result[a] = {'accession': a, 'family_id': known.get(a), 'verdict': verdict,
                     'tax_id': protein['Organism (ID)'], 'refseq': [s.strip() for s in protein['RefSeq'].split(';') if s.strip()]}
    return result, {'current_protected_anchors': len(protection['uniprot_accessions']),
                    'unresolved_current_anchors': unresolved_current_anchors,
                    'frozen_and_current_protection_union': True}


def crossrefs(root, output):
    audit = root / 'runs/metadata-audit-v1'
    assert read(audit / 'results.json')['status'] == 'PASS_METADATA_PROTECTION_AND_TWELVE_CASES'
    plan = read(audit / 'xref-requests.json')
    client = Client(root, output, 'uniprot', plan['requests'])
    proteins, receipts, release = [], [], None
    required = {'Entry', 'Reviewed', 'Organism (ID)', 'Protein names', 'Protein families',
                'Sequence similarities', 'InterPro', 'RefSeq'}
    try:
        for i, spec in enumerate(plan['requests']):
            raw, receipt = client.request(spec, 'xref-' + str(i).zfill(3))
            headers = {k.lower(): v for k, v in receipt['transport']['headers'].items()}
            current = headers.get('x-uniprot-release')
            if not current or release not in (None, current):
                raise QualificationError('Missing/drifting current protein metadata release')
            release = current
            reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t')
            if set(reader.fieldnames or []) != required or len(reader.fieldnames) != len(required):
                raise QualificationError('Protein metadata projection differs')
            rows = list(reader)
            if len(rows) > len(spec['expected_accessions']) or len({r['Entry'] for r in rows}) != len(rows):
                raise QualificationError('Protein metadata duplicate/excess rows')
            if any(r['Entry'] not in spec['expected_accessions'] or r['Reviewed'] != 'reviewed' for r in rows):
                raise QualificationError('Unapproved/unreviewed protein metadata')
            proteins.extend(rows)
            receipts.append({'path': receipt['request']['path'], 'params': receipt['request']['params'],
                             'utc': receipt['request_utc'], 'sha256': receipt['response_sha256'], 'bytes': receipt['response_bytes']})
    except Exception as error:
        client.stop('METADATA_ACCESS_OR_SCHEMA_FAILURE')
        write_new(output / 'results.json', {'status': 'NO_GO_METADATA_ACCESS_OR_SCHEMA', 'error_type': type(error).__name__,
                    'completed_queries': len(receipts), 'activity_requests': 0, 'scientific_campaigns': 0})
        raise
    write_new(output / 'protein-metadata-private.json', {'records': proteins, 'release': release})
    protection = read(audit / 'protection-private.json')
    overlay, protection_status = family_overlay(root, proteins, protection)
    exact, bases = defaultdict(set), defaultdict(set)
    for a, record in overlay.items():
        for ref in record['refseq']:
            exact[ref].add(a)
            bases[ref.split('.')[0]].add(a)
    descriptions = {r['aid']: r for r in read(root / 'private-inputs/description-metadata-input-v1.json')['records']}
    aidhistory = []
    for aid, descriptor in descriptions.items():
        targets = descriptor.get('target_metadata')
        verdict, resolved = 'QUARANTINE_UNRESOLVED_TARGET_OR_FAMILY', []
        if type(targets) is list and len(targets) == 1:
            target = targets[0]
            accession = target.get('mol_id', {}).get('protein_accession')
            matches = exact.get(accession, set()) or ({accession} if accession in overlay else set())
            if not matches and type(accession) is str:
                # Base-accession matches can block a reserved protein, but cannot
                # establish unprotected version equivalence.
                base = bases.get(accession.split('.')[0], set())
                if base & set(protection['uniprot_accessions']):
                    verdict = 'QUARANTINE_PROTECTED_PROTEIN_BASE_ACCESSION'
            if len(matches) == 1:
                a = next(iter(matches))
                org = target.get('organism', {}).get('org', {})
                taxa = {str(r['tag']['id']) for r in org.get('db', []) if r.get('db') == 'taxon' and type(r.get('tag')) is dict and 'id' in r['tag']}
                if taxa == {overlay[a]['tax_id']}:
                    verdict, resolved = overlay[a]['verdict'], [a]
        aidhistory.append({'aid': aid, 'resolved_accessions': resolved, 'target_family_gate': verdict,
                           'family_id': overlay[resolved[0]]['family_id'] if resolved else None})
    by_aid = {r['aid']: r for r in aidhistory}
    pairs = read(audit / 'source-binding-register.json')['records']
    admitted = []
    for pair in pairs:
        pair['target_family_gate'] = [by_aid[pair[key]] for key in ('primary_aid', 'confirmation_aid')]
        allowed = (pair['binding_status'] == 'EXACT_NAME_TID_UNIT_BINDING' and pair['both_programme_rights_supported']
                   and all(g['target_family_gate'] == 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY' for g in pair['target_family_gate']))
        pair['metadata_admitted'] = allowed
        if allowed:
            admitted.append(pair)
    salt = read(root / 'research/configs/goal4r2a3_policy_v1.json')['selection_salt']
    admitted.sort(key=lambda p: hashlib.sha256((salt + ':' + p['script']).encode()).hexdigest())
    selected = admitted[:12]
    write_new(output / 'family-overlay.json', {'release': release, 'aid_records': aidhistory,
               'protection_status': protection_status,
               'verdict_counts': dict(Counter(r['target_family_gate'] for r in aidhistory)),
               'independence_claim': 'NO_KNOWN_SHARED_FROZEN_IDENTITIES_NOT_EVOLUTIONARY_CERTIFICATION'})
    write_new(output / 'pair-metadata-gates.json', {'records': pairs, 'selected': selected,
               'selection': 'FROZEN_HASH_ORDER_BEFORE_ACTIVITY', 'activity_rows': 0})
    report = {'status': 'PASS_XREF_AND_PROTECTED_FAMILY_METADATA_GATES', 'queries': len(receipts), 'release': release,
              'reviewed_proteins': len(proteins), 'aid_family_verdicts': dict(Counter(r['target_family_gate'] for r in aidhistory)),
              'metadata_admitted_pairs': len(admitted), 'selected_pairs': len(selected),
              'selected_known_family_components': len({r['family_id'] for p in selected for r in p['target_family_gate']}),
              'activity_requests': 0, 'scientific_campaigns': 0}
    write_new(output / 'metadata-request-receipts.json', {'records': receipts})
    write_new(output / 'results.json', report)
    return report


def execute(mode, root, output):
    if mode == 'xref':
        try:
            from .network_checks import run
            run(root, output)
            return crossrefs(root, output)
        except Exception as error:
            # Includes post-download overlay/projection failures. No subsequent
            # worker may silently resume the stopped metadata source.
            path = root / 'network-ledger.json'
            ledger = read(path) if path.exists() else {'requests': [], 'stopped_services': []}
            if 'uniprot' not in ledger['stopped_services']:
                ledger['stopped_services'].append('uniprot')
            ledger.setdefault('stop_events', []).append({'service': 'uniprot', 'reason': 'XREF_PHASE_FAILED',
                    'error_type': type(error).__name__, 'utc': datetime.now(timezone.utc).isoformat()})
            save_ledger(path, ledger)
            raise
    raise QualificationError('Activity/identifier intake is disabled until its separate reviewed manifest')
