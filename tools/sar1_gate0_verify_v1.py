"""Read-only verification of initial G0 census; no reference/agent rerun."""
from __future__ import annotations
import ast
import hashlib
import json
import urllib.request
import zipfile
from collections import Counter
from tools.sar1_control_v1 import ACCOUNT, PUBLIC, ROOT, authority, digest, write_new, save_ledger
from tools.sar1_catalog_v1 import syntax_info


def main():
    authority()
    source = PUBLIC / 'static-census-v1.json'
    census = json.loads(source.read_text(encoding='utf-8'))
    rows = census['catalog']
    assert len(rows) == len({r['instance_id'] for r in rows}) == 102
    checks = []
    fixtures = [
        ('direct_judge', 'from gpt4_visual_judge import score_figure as score\ndef eval():\n return score(None, None)\n', True),
        ('local_helper_judge', 'import gpt4_visual_judge as judge\ndef helper():\n return judge.score_figure(None, None)\ndef eval():\n return helper()\n', True),
        ('unused_judge_function', 'import gpt4_visual_judge as judge\ndef unused():\n return judge.score_figure(None, None)\ndef eval():\n return True\n', False),
        ('deterministic', 'def eval():\n return True, {}\n', False),
    ]
    for name, code, expected in fixtures:
        actual = bool(syntax_info(code.encode())['reachable_external_judge_calls'])
        assert actual == expected, name
        checks.append({'name': name, 'status': 'PASS'})
    # Independently verify a real score_figure call exists in every classified evaluator.
    direct_calls = []
    archive = ROOT / 'research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip'
    with zipfile.ZipFile(archive) as stream:
        for row in rows:
            if 'REACHABLE_EXTERNAL_MODEL_JUDGE' not in row['exclusion_reasons']:
                continue
            raw = stream.read('benchmark/eval_programs/' + row['eval_script_name'], pwd=b'scienceagentbench')
            assert hashlib.sha256(raw).hexdigest() == row['evaluator_sha256']
            tree = ast.parse(raw.decode('utf-8-sig'))
            entry = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'eval')
            calls = [n for n in ast.walk(entry) if isinstance(n, ast.Call)]
            score_calls = [ast.unparse(n.func) for n in calls
                           if ast.unparse(n.func).split('.')[-1] == 'score_figure']
            assert score_calls, 'No direct score_figure call in eval: ' + str(row['instance_id'])
            direct_calls.append({'instance_id': row['instance_id'], 'direct_score_figure_calls': len(score_calls),
                                 'evaluator_sha256': row['evaluator_sha256']})
    assert len(direct_calls) == 64
    # Public upstream helper; never import/execute it or transmit images/API credentials.
    url = 'https://raw.githubusercontent.com/OSU-NLP-Group/ScienceAgentBench/c26e151ed601ba109dc4d35e057ff8e73fec469d/gpt4_visual_judge.py'
    folder = ACCOUNT / 'g0-source-verification-v1'
    folder.mkdir(parents=True, exist_ok=False)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'CuraLoop-LR-SAR1/1.0'}), timeout=30) as response:
        raw = response.read(1024 * 1024 + 1)
    assert len(raw) <= 1024 * 1024
    helper = folder / 'official-gpt4-visual-judge.py.txt'
    helper.write_bytes(raw)
    tree = ast.parse(raw.decode('utf-8-sig'))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'score_figure')
    client_calls = sorted({ast.unparse(n.func) for n in ast.walk(function) if isinstance(n, ast.Call)
                           and ast.unparse(n.func).endswith('chat.completions.create')})
    assert client_calls, 'Official helper is not the presumed external judge'
    source_receipt = {'url': url, 'bytes': len(raw), 'sha256': digest(helper),
                      'official_commit': 'c26e151ed601ba109dc4d35e057ff8e73fec469d',
                      'external_client_calls': client_calls, 'helper_imported_or_executed': False,
                      'paid_model_requests': 0}
    write_new(PUBLIC / 'external-judge-source-verification-v1.json', source_receipt)
    candidates = [r for r in rows if not r['exclusion_reasons']]
    no_judge = [r for r in rows if 'REACHABLE_EXTERNAL_MODEL_JUDGE' not in r['exclusion_reasons']]
    gate = {
        'status': 'NO_GO_STATIC_API_FREE_COVERAGE', 'stage': 'G0',
        'reason': '64/102 official eval entrypoints directly invoke the external visual score_figure helper; only 38 lack that dependency even before exposure exclusions, below 60 locked tasks',
        'tasks_inspected': 102, 'external_judge_tasks': 64,
        'no_external_judge_tasks_before_exposure_exclusions': len(no_judge),
        'potential_candidates_after_existing_exposure_roles': len(candidates),
        'potential_repository_lineages': len({r['repository_lineage'] for r in candidates}),
        'potential_domains': len({r['domain'] for r in candidates}),
        'required_locked_tasks': 60, 'required_source_clusters': 15, 'required_domains': 3,
        'candidate_native_qualification': 'NOT_RUN', 'rights_certification': 'NOT_COMPLETED',
        'native_success_claim': False, 'checker_or_agent_effect': 'NOT_ESTIMABLE',
        'reference_or_gold_values_read': False, 'model_calls': 0, 'gpu_allocated_seconds': 0,
        'scientific_retry': False, 'verification_scope': 'Same retained census/evaluator AST plus public helper source and constructed classifier tests; no scientific program executed',
        'census_sha256': digest(source), 'classifier_checks': checks,
        'external_judge_calls_in_entrypoint': direct_calls,
        'domain_counts_no_judge_before_exclusions': dict(Counter(r['domain'] for r in no_judge)),
        'source_verification': source_receipt,
        'scope_limit': 'Static eligibility under the approved no-paid-judge policy; does not establish native success, full transitive API freedom, or benchmark defects',
        'next_work': 'Stop science; owner report, Thai journal review, preservation/resource audit and authorized main delivery only',
        'new_manuscript_authorized': False,
    }
    assert len(no_judge) == 38 and len(candidates) == 30
    write_new(PUBLIC / 'gate0-v1.json', gate)
    write_new(ACCOUNT / 'gate0-v1.json', gate)
    _, ledger = authority()
    ledger['status'] = 'ACTIVE_CLOSEOUT_FAILED_G0'
    ledger['failed_gate'] = 'G0'
    ledger['scientific_work_stopped'] = True
    save_ledger(ledger)
    print(json.dumps({k: v for k, v in gate.items() if k not in ('external_judge_calls_in_entrypoint',)}, indent=2))


if __name__ == '__main__':
    main()
