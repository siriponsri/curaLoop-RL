"""Additive cached-metadata repair. No network access or activity dispatcher."""

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict

from .audit import write_new
from .contracts import QualificationError, family_gate
from .network import read

TOKEN = re.compile(r'(N[P]_\d+\.\d+|X[P]_\d+\.\d+|YP_\d+\.\d+|WP_\d+\.\d+)(?: \[([A-Z0-9]+)-(\d+)\])?')
REQUIRED = {'Entry', 'Reviewed', 'Organism (ID)', 'Protein names', 'Protein families',
            'Sequence similarities', 'InterPro', 'RefSeq'}


def refseq_tokens(entry, text):
    """Full-token validation; an isoform suffix never substitutes for a version."""
    parsed = []
    for token in text.split(';'):
        token = token.strip()
        if not token:
            continue
        match = TOKEN.fullmatch(token)
        if not match or (match[2] is not None and match[2] != entry):
            raise QualificationError('Malformed or foreign-parent RefSeq token')
        parsed.append({'accession_version': match[1], 'isoform_tag':
                       match[2] + '-' + match[3] if match[2] else None})
    return parsed


def validate_cached(raw, receipt, specification, roster, release):
    request = receipt['request']
    headers = {k.lower(): v for k, v in receipt['transport']['headers'].items()}
    digest = hashlib.sha256(raw).hexdigest()
    if (request['base_url'] != 'https://rest.uniprot.org'
            or request['method'] != 'GET' or request['path'] != specification['path']
            or request['params'] != specification['params']
            or roster['path'] != specification['path'] or roster['params'] != specification['params']
            or receipt['request_utc'] != roster['utc']
            or receipt['response_sha256'] != digest or roster['sha256'] != digest
            or receipt['response_bytes'] != len(raw) or roster['bytes'] != len(raw)
            or headers.get('x-uniprot-release') != release
            or not receipt['result'].get('ok')):
        raise QualificationError('Cached response identity, size, release or request differs')
    reader = csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter='\t')
    if set(reader.fieldnames or []) != REQUIRED or len(reader.fieldnames) != len(REQUIRED):
        raise QualificationError('Cached TSV projection differs')
    rows = list(reader)
    if any(set(r) != REQUIRED or any(type(v) is not str for v in r.values())
           or not re.fullmatch(r'[1-9][0-9]*', r['Organism (ID)']) for r in rows):
        raise QualificationError('Malformed cached TSV row width, value or taxonomy')
    if (len(rows) > len(specification['expected_accessions'])
            or len({r['Entry'] for r in rows}) != len(rows)
            or any(r['Entry'] not in specification['expected_accessions'] or r['Reviewed'] != 'reviewed' for r in rows)):
        raise QualificationError('Cached protein roster differs')
    return rows


def retired_supplement(root, config):
    source = root / 'private-inputs/source-evidence'
    raw = (source / 'IPR050332-metadata-v1.json').read_bytes()
    receipt = read(source / 'IPR050332-receipt-v1.json')
    pin = config['supplemental_interpro']
    data = json.loads(raw)
    headers = {k.lower(): v for k, v in receipt['headers'].items()}
    if (len(raw) != 302 or hashlib.sha256(raw).hexdigest() != pin['response_sha256']
            or receipt['sha256'] != pin['response_sha256'] or receipt['status'] != 410
            or receipt['url'] != pin['url'] or headers.get('interpro-version') != '111.0'
            or data['accession'].upper() != pin['accession'] or data['type'] != 'family'
            or data['deletion_date'] != pin['deleted']):
        raise QualificationError('Retired family protection supplement differs')
    return {pin['accession']: 'family'}


def family_overlay(root, proteins, protection, supplemental):
    from research.benchmark_v3.families import normalize, family_annotation
    from research.benchmark_v3.family_closure import ambiguity_reason, iprs
    source = root / 'private-inputs/protection-inputs'
    registry = read(source / 'family-registry-v3.json')
    path = source / 'interpro-ftp-entries110-curl-v2/body'
    if hashlib.sha256(path.read_bytes()).hexdigest() != '1d247a42670d4a2913cec9f2a58813135c736d65128c1078d9c5eac797ffef1c':
        raise QualificationError('Pinned InterPro110 types differ')
    types = {a: k.lower().replace(' ', '_') for a, k, _ in
             (line.split('\t', 2) for line in path.read_text().splitlines()[1:])}
    if set(supplemental) & set(types):
        raise QualificationError('Supplement may not overwrite frozen type listing')
    types.update(supplemental)  # Positive identity only, never a successor or hierarchy edge.
    cached = read(source / 'uniprot-family-bulk-v1/families.json') + read(source / 'uniprot-family-exposure-v1/families.json')
    cached_by_acc = {r['Entry']: r for r in cached}
    protected_names = {normalize(n) for r in registry['family_records'] if r['family_id'] in protection['family_ids'] for n in r['broad_names_merged']}
    protected_iprs = {i for a in protection['uniprot_accessions'] for i in iprs(cached_by_acc[a])
                      if types.get(i) in ('family', 'homologous_superfamily')}
    current_by_acc = {p['Entry']: p for p in proteins}
    unresolved = []
    for accession in protection['uniprot_accessions']:
        current = current_by_acc.get(accession)
        annotation = family_annotation(current) if current else None
        if not current or not annotation or ambiguity_reason(current) or any(i not in types for i in iprs(current)):
            unresolved.append(accession)
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
            if unresolved:
                verdict = 'QUARANTINE_CURRENT_PROTECTED_ANNOTATION_UNRESOLVED'
            elif not annotation or ambiguity_reason(protein) or any(i not in types for i in iprs(protein)):
                verdict = 'QUARANTINE_UNRESOLVED_CURRENT_ANNOTATION'
            elif set(annotation[1]) & protected_names or iprs(protein) & protected_iprs:
                verdict = 'QUARANTINE_SHARED_PROTECTED_FAMILY_OR_SUPERFAMILY'
        try:
            refs = refseq_tokens(a, protein['RefSeq'])
            ref_status = 'VALIDATED'
        except QualificationError:
            refs, ref_status = [], 'QUARANTINE_MALFORMED_REFSEQ'
        result[a] = {'accession': a, 'family_id': known.get(a), 'verdict': verdict,
                     'tax_id': protein['Organism (ID)'], 'refseq': refs, 'refseq_status': ref_status}
    return result, {'unresolved_current_anchors': unresolved,
                    'frozen_and_current_protection_union': True,
                    'retired_positive_protected_family_ids': sorted(set(supplemental) & protected_iprs),
                    'interpro110_listing_unchanged': True, 'ancestry_reconstructed': False}


def target_gate(descriptor, overlay, exact, bases, protection):
    verdict, resolved = 'QUARANTINE_UNRESOLVED_TARGET_OR_FAMILY', []
    targets = descriptor.get('target_metadata')
    if type(targets) is not list or len(targets) != 1:
        return verdict, resolved
    target = targets[0]
    accession = (target.get('mol_id') or {}).get('protein_accession')
    # Conflicting exact-version metadata cannot override a positive protected base identity.
    if type(accession) is str and bases.get(accession.split('.')[0], set()) & set(protection['uniprot_accessions']):
        return 'QUARANTINE_PROTECTED_PROTEIN_BASE_ACCESSION', []
    matches = exact.get(accession, set()) or ({accession} if accession in overlay else set())
    if len(matches) == 1:
        a = next(iter(matches))
        org = (target.get('organism') or {}).get('org') or {}
        taxa = {str(r['tag']['id']) for r in org.get('db', []) if r.get('db') == 'taxon' and type(r.get('tag')) is dict and 'id' in r['tag']}
        if taxa == {overlay[a]['tax_id']}:
            verdict, resolved = overlay[a]['verdict'], [a]
    return verdict, resolved


def execute(root, output):
    config = read(root / 'research/configs/goal4r2a3_reconciliation_v2.json')
    from .reconciliation_checks_v2 import run
    run(root, output, config)
    audit, original = root / 'runs/metadata-audit-v1', root / 'runs/xref-metadata-v1'
    plan_path, roster_path = audit / 'xref-requests.json', original / 'metadata-request-receipts.json'
    for path, key in [(plan_path, 'original_request_plan_sha256'), (roster_path, 'original_response_roster_sha256')]:
        if hashlib.sha256(path.read_bytes()).hexdigest() != config[key]:
            raise QualificationError('Original metadata roster differs')
    plan, roster = read(plan_path)['requests'], read(roster_path)['records']
    ledger_path = root / 'network-ledger.json'
    before = ledger_path.read_bytes()
    ledger = json.loads(before)
    if len(plan) != 27 or len(roster) != 27 or ledger['stopped_services']:
        raise QualificationError('Cached metadata admission differs')
    ledger_rows = [r for r in ledger['requests'] if r['service'] == 'uniprot']
    if len(ledger_rows) != 27 or any(r['status'] != 'COMPLETED' for r in ledger_rows):
        raise QualificationError('Original metadata request ledger differs')
    proteins = []
    for i, (spec, expected, charged) in enumerate(zip(plan, roster, ledger_rows)):
        name = 'xref-' + str(i).zfill(3)
        raw_path = original / (name + '.txt')
        if (charged['output'] != raw_path.relative_to(root).as_posix()
                or charged['path'] != spec['path'] or charged['params'] != spec['params']
                or charged['charged_decoded_bytes'] != expected['bytes']):
            raise QualificationError('Cached network charge or output differs')
        proteins.extend(validate_cached(raw_path.read_bytes(), read(original / (name + '-receipt.json')),
                                         spec, expected, config['source_release']))
    if len({p['Entry'] for p in proteins}) != len(proteins):
        raise QualificationError('Duplicate proteins across cached batches')
    protection = read(audit / 'protection-private.json')
    overlay, state = family_overlay(root, proteins, protection, retired_supplement(root, config))
    exact, bases = defaultdict(set), defaultdict(set)
    for a, row in overlay.items():
        for ref in row['refseq']:
            exact[ref['accession_version']].add(a)
            bases[ref['accession_version'].split('.')[0]].add(a)
    aidhistory = []
    for descriptor in read(root / 'private-inputs/description-metadata-input-v1.json')['records']:
        verdict, resolved = target_gate(descriptor, overlay, exact, bases, protection)
        aidhistory.append({'aid': descriptor['aid'], 'resolved_accessions': resolved, 'target_family_gate': verdict,
                          'family_id': overlay[resolved[0]]['family_id'] if resolved else None})
    by_aid = {r['aid']: r for r in aidhistory}
    pairs = read(audit / 'source-binding-register.json')['records']
    admitted = []
    for pair in pairs:
        gates = [by_aid[pair[k]] for k in ('primary_aid', 'confirmation_aid')]
        pair['target_family_gate'] = gates
        pair['metadata_admitted'] = (pair['binding_status'] == 'EXACT_NAME_TID_UNIT_BINDING'
            and pair['both_programme_rights_supported'] and
            all(g['target_family_gate'] == 'NO_KNOWN_SHARED_FROZEN_FAMILY_IDENTITY' for g in gates))
        if pair['metadata_admitted']:
            admitted.append(pair)
    salt = read(root / 'research/configs/goal4r2a3_policy_v1.json')['selection_salt']
    admitted.sort(key=lambda p: hashlib.sha256((salt + ':' + p['script']).encode()).hexdigest())
    selected = admitted[:12]
    assert ledger_path.read_bytes() == before
    write_new(output / 'refseq-overlay-private.json', {'records': list(overlay.values())})
    write_new(output / 'family-overlay.json', {'release': config['source_release'], 'aid_records': aidhistory,
              'protection_status': state, 'verdict_counts': dict(Counter(r['target_family_gate'] for r in aidhistory)),
              'independence_claim': 'NO_KNOWN_SHARED_FROZEN_IDENTITIES_NOT_EVOLUTIONARY_CERTIFICATION'})
    write_new(output / 'pair-metadata-gates.json', {'records': pairs, 'selected': selected,
              'selection': 'FROZEN_HASH_ORDER_BEFORE_ACTIVITY', 'activity_rows': 0, 'supersedes_admission_only': ['xref-metadata-v1', 'cached-reconciliation-v1']})
    report = {'status': 'PASS_CACHED_METADATA_RECONCILIATION', 'cached_queries_verified': len(plan),
              'additional_uniprot_requests': 0, 'activity_requests': 0, 'scientific_campaigns': 0,
              'reviewed_proteins': len(proteins), 'metadata_admitted_pairs': len(admitted), 'selected_pairs': len(selected),
              'aid_family_verdicts': dict(Counter(r['target_family_gate'] for r in aidhistory)),
              'metadata_admission_may_change': True, 'scientific_population_frozen': False,
              'network_ledger_unchanged_sha256': hashlib.sha256(before).hexdigest()}
    write_new(output / 'results.json', report)
    return report
