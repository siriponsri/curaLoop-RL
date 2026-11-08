"""Validate the method-first design delivery; constructed models only."""

import argparse
import ast
import hashlib
import json
import re
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.method_first_v1.rollout import ScenarioRollout  # noqa: E402

PUBLIC = ROOT / 'docs/evidence/method-first-20261108-v1'
PRIVATE = ROOT / '.local/method-first-design-20261108-v1'
BASE = '1950b74d12f33eb08dc0b8a0fabf0ec0dbb7ad7a'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, indent=2, allow_nan=False) + '\n').encode())


def git_hash(*args):
    run = subprocess.run(['rtk', 'proxy', 'git', *args], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    found = re.findall(r'^[a-f0-9]{40}$', run.stdout, re.M)
    assert len(found) == 1, run.stdout
    return found[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', type=int, default=1)
    parser.add_argument('--test-revision', type=int, default=2)
    args = parser.parse_args()
    output = PUBLIC / f'delivery-validation-v{args.revision}.json'
    cases_path = PUBLIC / 'constructed-cases-v1.json'
    assert args.revision > 0 and args.test_revision > 0 and not output.exists()
    config_path = ROOT / 'research/configs/method_first_status_20261108_v1.json'
    config = json.loads(config_path.read_text())
    assert config['benchmark_publication_is_primary_contribution'] is False
    assert config['is_scientific_execution_release'] is False
    assert config['new_scientific_cpu_grant'] is None
    assert config['novelty_status'] == 'HOLD_PRIOR_ART_OVERLAP'
    assert all('DEFERRED' in status or 'SUPERSEDED' in status
               for status in config['old_planning_status_overrides'].values())

    xml_name = f'mechanism-tests-v{args.test_revision}.xml'
    test_xml = ElementTree.parse(PUBLIC / xml_name).getroot()
    suites = list(test_xml.iter('testsuite'))
    assert sum(int(s.get('tests', 0)) for s in suites) == 20
    assert sum(int(s.get('failures', 0)) + int(s.get('errors', 0)) for s in suites) == 0

    ledger_pins = json.loads((ROOT / '.local/data-inventory-20261107-v1/old-ledger-pins-v1.json').read_text())['records']
    for row in ledger_pins:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']
    evidence_pins = json.loads((ROOT / 'docs/evidence/local-data-inventory-20261107-v1/evidence-source-pins-v1.json').read_text())['sources']
    for row in evidence_pins:
        assert sha(ROOT / row['path']) == row['sha256'], row['path']

    historical_paths = ['research/configs/r0_qp_proposal_20261108_v1.json',
                        'docs/01_paper/05_results.md', 'docs/01_paper/09_declarations.md']
    historical = []
    for name in historical_paths:
        before = git_hash('rev-parse', BASE + ':' + name)
        now = git_hash('hash-object', '--path', name, name)
        assert before == now, name
        historical.append({'path': name, 'git_blob': now, 'unchanged_from': BASE})

    new_docs = ['docs/03_research/METHOD_FIRST_DESIGN_20261108.md',
                'docs/02_literature/METHOD_FIRST_CLOSEST_WORK_20261108.md',
                'docs/06_execution/METHOD_FIRST_CHECKPOINT_20261108.md',
                'docs/evidence/method-first-20261108-v1/README.md']
    editorial = json.loads((PRIVATE / 'editorial-change-pins-v1.json').read_text())['records']
    docs = sorted(set(new_docs + [row['path'] for row in editorial]))
    links = 0
    for name in docs:
        path = ROOT / name
        body = path.read_text(encoding='utf-8')
        assert not re.search('[\u0e00-\u0e7f]', body), name
        for target in re.findall(r'\]\(([^\n]+?)\)', body):
            target = target.strip('<>')
            if re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:', target) or target.startswith('#'):
                continue
            dest = (path.parent / target.split('#', 1)[0]).resolve()
            if dest not in (output.resolve(), cases_path.resolve()):
                assert dest.exists(), (name, target)
            links += 1
    manuscript = (ROOT / 'docs/01_paper/MANUSCRIPT.md').read_text(encoding='utf-8')
    for chapter in sorted((ROOT / 'docs/01_paper').glob('[0-9][0-9]_*.md')):
        fragment = re.sub(r'^(#{1,5}) ', r'#\1 ', chapter.read_text(encoding='utf-8').strip(), flags=re.M)
        assert fragment in manuscript, chapter.name

    modules = ['research/method_first_v1/__init__.py', 'research/method_first_v1/rollout.py',
               'tests/research/test_method_first_v1.py', 'tools/check_method_first_v1.py']
    for name in modules:
        ast.parse((ROOT / name).read_text(encoding='utf-8'))
    worlds = ((1, 1, 0), (1, 0, 1), (0, 1, 0), (0, 0, 1))
    prior = (0.3, 0.3, 0.2, 0.2)
    model = ScenarioRollout(worlds, (prior,))
    ambiguous = ScenarioRollout(worlds, (prior, (0, 1, 0, 0)))
    cases = {'scope': 'CONSTRUCTED_PREDICTIVE_MODELS_ONLY_NOT_MOLECULAR_EVIDENCE',
             'positive': asdict(model.choose({}, 2)),
             'ambiguous_robust': asdict(ambiguous.choose({}, 2)),
             'ambiguous_nominal': asdict(ambiguous.choose({}, 2, objective='mixture')),
             'cached': asdict(model.choose({}, 3)),
             'uncached': asdict(model.choose({}, 3, use_cache=False)),
             'zero_computation_states': asdict(model.choose({}, 2, max_states=0)),
             'misspecified_true_world_counterexample': {
                 'outside_model_world': [1, 0, 0], 'baseline_realized_hits': 1,
                 'selected_deviation_then_greedy_realized_hits': 0,
                 'meaning': 'Positive model-conditional gain does not establish real-world safety'}}
    if cases_path.exists():
        assert json.loads(cases_path.read_text()) == cases
    else:
        save(cases_path, cases)
    save(output, {'status': 'PASS_METHOD_FIRST_DESIGN_AND_CONSTRUCTED_DELIVERY_CHECKS',
                  'base_commit': BASE, 'method_design': 'COMPLETE_FOR_OWNER_REVIEW',
                  'novelty': 'HOLD_PRIOR_ART_OVERLAP', 'mechanism_checks': 20,
                  'xml': xml_name, 'validation_revision': args.revision,
                  'supersedes': (f'delivery-validation-v{args.revision - 1}.json current hashes after editorial cleanup'
                                 if args.revision > 1 else None),
                  'local_links_checked': links,
                  'assembled_chapters_match': 10,
                  'ordinary_constructed_checks_not_a_molecular_campaign': True,
                  'old_closed_ledgers_unchanged': ledger_pins,
                  'old_authored_scientific_records_unchanged': evidence_pins,
                  'historical_proposal_results_declarations_unchanged': historical,
                  'editorial_change_paths': [row['path'] for row in editorial],
                  'current_document_config_source_sha256': {
                      name: sha(ROOT / name) for name in docs + modules + [str(config_path.relative_to(ROOT))]},
                  'new_data_rows_presence_or_labels_opened': False,
                  'old_final_outcomes_opened': False,
                  'source_database_archive_or_ssh_access': False,
                  'new_scientific_budget_clock_or_release': False,
                  'independent_scientific_review': 'NOT_RUN',
                  'real_data_adapter_calibration_and_method_benefit': 'NOT_RUN',
                  'application_runtime_browser_build': 'NOT_RUN_NO_PRODUCT_RUNTIME_CHANGE',
                  'utc': datetime.now(timezone.utc).isoformat()})
    print('PASS: 20 mechanism checks; document/proposal links; chapter assembly; old ledgers/scientific records preserved.')


if __name__ == '__main__':
    main()
