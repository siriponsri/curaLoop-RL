"""Exposed real-metadata census with independently resolved authored references."""

import copy
import hashlib
import json
import sys
import time
import traceback


def execute(bundle, output):
    sys.path.insert(0, str(bundle / 'src'))
    from curaloop_rd.catalogue_v2 import Catalogue
    from curaloop_rd.contracts_v2 import canonical, digest, validate_report
    from curaloop_rd.decision_v2 import decide
    from curaloop_rd.workflow_v2 import Outbox, atomic_same, markdown
    from .reference_support import verify_reference, score
    config_path = bundle / 'research/configs/lrbc_workflow_cases_v1.json'
    config = json.loads(config_path.read_text())
    references = json.loads((bundle / 'research/configs/lrbc_workflow_references_v1.json').read_text())
    assert references['source_case_config_sha256'] == hashlib.sha256(config_path.read_bytes()).hexdigest()
    registry = json.loads((bundle / 'inputs/workflow-registry.json').read_text())
    for reference in references['cases'].values():
        for item in reference['claims']: verify_reference(bundle, registry, item)
    catalogue = Catalogue(bundle, registry)
    rows = []
    def simple(folder, value, interrupt=False):
        validate_report(value)
        atomic_same(folder / 'report.json', (canonical(value) + '\n').encode())
        if interrupt: raise InterruptedError('SYNTHETIC_INTERRUPT_AFTER_PERSIST')
        atomic_same(folder / 'report.md', markdown(value).encode())
        receipt = {'report_sha256': value['report_sha256'], 'destination': 'LOCAL_PREVIEW_ONLY', 'delivered': False, 'revision': 1}
        atomic_same(folder / 'preview.json', (canonical(receipt) + '\n').encode())
        return receipt
    for case in config['cases']:
        brief = {'question': case['question'], 'kind': case['kind'], 'source_ids': case.get('sources', [case.get('source')])}
        if 'tid' in case: brief['tid'] = case['tid']
        outcomes = {}
        for arm in ('simple', 'durable'):
            started, cpu, box = time.monotonic(), time.process_time(), None
            try:
                value = decide(brief, catalogue)  # Reference answers never enter either arm.
                root = output / arm
                box = Outbox(root) if arm == 'durable' else None
                recovered = False
                if case.get('fault'):
                    try:
                        if box: box.save(case['id'], value, 0, interrupt=True)
                        else: simple(root / case['id'], value, True)
                    except InterruptedError: recovered = True
                    else: raise AssertionError('Frozen fault not injected')
                receipt = box.save(case['id'], value, 0) if box else simple(root / case['id'], value)
                replay = box.save(case['id'], value, 1) if box else simple(root / case['id'], value)
                assert replay == receipt and len(list((root / case['id']).iterdir())) == 3
                outcomes[arm] = dict(score(value, references['cases'][case['id']], registry),
                     recovery_injected=bool(case.get('fault')), recovered=recovered, duplicate_artifacts=0,
                     report_sha256=value['report_sha256'], failure=None)
            except Exception as error:
                (output / (case['id'] + '-' + arm + '-error-private.txt')).write_text(traceback.format_exc(), encoding='utf-8')
                outcomes[arm] = {'correct': False, 'failure': type(error).__name__,
                    'mandatory_claims': len(references['cases'][case['id']]['claims']),
                    'missing_claims': len(references['cases'][case['id']]['claims']), 'unsupported_claims': 0,
                    'source_ledger_correct': False, 'recovery_injected': bool(case.get('fault')),
                    'recovered': False, 'duplicate_artifacts': None, 'report_sha256': None}
            finally:
                if box: box.close()
                outcomes[arm].update(cpu_seconds=time.process_time() - cpu, wall_seconds=time.monotonic() - started)
        row = {'id': case['id'], 'group': case['group'], 'arms': outcomes}
        rows.append(row)
        (output / (case['id'] + '-partial.json')).write_text(json.dumps(row, indent=2) + '\n', encoding='utf-8')
    checks = []
    try: catalogue.inspect('alias_final_reserved')
    except ValueError: checks.append('UNREGISTERED_ALIAS_DENIED_BEFORE_OPEN')
    else: raise AssertionError('Unregistered alias admitted')
    sample = decide({'question': 'Boundary metadata report', 'kind': 'endpoint', 'source_ids': ['D1259375'], 'tid': 2}, catalogue)
    box = Outbox(output / 'boundaries')
    try:
        box.save('boundary', sample, 0)
        try: box.save('boundary', sample, 0)
        except ValueError: checks.append('STALE_REVISION_DENIED')
        else: raise AssertionError('Stale revision admitted')
        changed = copy.deepcopy(sample); changed['question'] += ' valid changed content'
        changed['report_sha256'] = digest({k: v for k, v in changed.items() if k != 'report_sha256'})
        validate_report(changed)
        try: box.save('boundary', changed, 1)
        except ValueError: checks.append('VALID_CHANGED_CONTENT_CAS_DENIED')
        else: raise AssertionError('Changed content admitted')
    finally: box.close()
    reference = references['cases']['W03']
    wrong = copy.deepcopy(sample); wrong['claims'][0]['evidence']['locator'] += '/forged'
    assert not score(wrong, reference, registry)['correct'] and score(wrong, reference, registry)['unsupported_claims'] > 0
    checks.append('FORGED_LOCATOR_SCORED_UNSUPPORTED')
    wrong = copy.deepcopy(sample); extra = copy.deepcopy(wrong['claims'][0]); extra.update(key='extra_false_claim', value=999)
    wrong['claims'].append(extra)
    assert score(wrong, reference, registry)['unsupported_claims'] > 0
    checks.append('EXTRA_FALSE_CLAIM_SCORED_UNSUPPORTED')
    counts = {a: sum(r['arms'][a]['correct'] for r in rows) for a in ('simple', 'durable')}
    groups = sorted({r['group'] for r in rows})
    loo = [{'omitted_group': g, 'remaining_briefs': sum(r['group'] != g for r in rows),
            'durable_minus_simple_correct': sum(int(r['arms']['durable']['correct']) - int(r['arms']['simple']['correct'])
                                               for r in rows if r['group'] != g)} for g in groups]
    content = [{'id': r['id'], 'group': r['group'], 'hash': r['arms']['durable']['report_sha256'],
                'correct': r['arms']['durable']['correct']} for r in rows]
    return {'status': 'PASS' if all(counts[a] == len(rows) for a in counts) else 'FAIL_REFERENCE_CHECK',
            'briefs': len(rows), 'source_groups': len(groups), 'all_sources_exposed': True, 'correct_briefs': counts,
            'unsupported_claims': {a: sum(r['arms'][a]['unsupported_claims'] for r in rows) for a in counts},
            'missing_claims': {a: sum(r['arms'][a]['missing_claims'] for r in rows) for a in counts},
            'durable_wins': sum(r['arms']['durable']['correct'] and not r['arms']['simple']['correct'] for r in rows),
            'simple_wins': sum(r['arms']['simple']['correct'] and not r['arms']['durable']['correct'] for r in rows),
            'ties': sum(r['arms']['simple']['correct'] == r['arms']['durable']['correct'] for r in rows),
            'boundary_checks': checks, 'source_group_leave_one_out': loo,
            'content_signature_sha256': hashlib.sha256(canonical(content).encode()).hexdigest(), 'rows': rows,
            'new_source_requests': 0, 'live_llm_or_agent_evaluation': 'NOT_RUN', 'independent_benchmark': False,
            'shared_decision_code': True, 'research_or_business_advantage_established': False}
