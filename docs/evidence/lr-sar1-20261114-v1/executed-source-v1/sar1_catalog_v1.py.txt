"""G0 census: public metadata and evaluator syntax; no gold/reference execution."""
from __future__ import annotations

import ast
import csv
import io
import json
import zipfile
from collections import Counter
from pathlib import PurePosixPath

import pyarrow.parquet as pq
from tools.sar1_control_v1 import ACCOUNT, PUBLIC, ROOT, authority, digest, write_new


def normalize_repo(value):
    return value.strip().lower().removeprefix('https://github.com/').removeprefix('http://github.com/').removesuffix('/').removesuffix('.git')


def syntax_info(raw):
    tree = ast.parse(raw.decode('utf-8-sig'))
    imports, aliases = set(), {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                imports.add(item.name.split('.')[0])
                aliases[item.asname or item.name.split('.')[0]] = item.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
            for item in node.names:
                aliases[item.asname or item.name] = node.module + '.' + item.name
    functions = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    reachable, pending, calls = set(), ['eval'] if 'eval' in functions else [], set()
    while pending:
        name = pending.pop()
        if name in reachable:
            continue
        reachable.add(name)
        for node in ast.walk(functions[name]):
            if isinstance(node, ast.Call):
                call = ast.unparse(node.func)
                prefix, _, tail = call.partition('.')
                qualified = aliases.get(prefix, prefix) + ('.' + tail if tail else '')
                calls.add(qualified)
                if call in functions:
                    pending.append(call)
    judge_markers = ('gpt4_visual_judge', 'openai.', 'anthropic.', 'litellm.',
                     'gpt4o', 'gpt_4', 'gpt4vision', 'visual_judge', 'chatcompletion')
    judge_calls = sorted(c for c in calls if any(m in c.lower() for m in judge_markers))
    # Imports alone are a review flag, not proof that a mandatory judge runs.
    external_imports = sorted(n for n in imports if any(m in n.lower() for m in
                              ('openai', 'anthropic', 'litellm', 'gpt4', 'judge')))
    dynamic = sorted(c for c in calls if c in {'eval', 'exec', '__import__', 'importlib.import_module'})
    return {'imports': sorted(imports), 'eval_entrypoint_present': 'eval' in functions,
            'reachable_call_names': sorted(calls), 'reachable_external_judge_calls': judge_calls,
            'external_import_review_flags': external_imports, 'dynamic_review_flags': dynamic}


def main():
    authority()
    folder = ACCOUNT / 'catalog-v1'
    folder.mkdir(parents=True, exist_ok=False)
    annotation = ROOT / '.local/lr-dc2-20261111-v1/dataset-intake-v1/verified.parquet'
    expected = 'c6f937863a220bd1762a00c20a0f79cc8dfca900b819bdb552150310731ae147'
    assert digest(annotation) == expected, 'Retained annotation bytes changed'
    archive = ROOT / 'research/raw_data/external-benchmarks/scienceagentbench-verified-20260430/benchmark_verified.zip'
    assert archive.stat().st_size == 1769478786
    archive_hash = digest(archive)
    assert archive_hash == '46e715d3b2196d459d2dff52aa487f506a95ec44b44262e82208d086ea879610'
    cols = ['instance_id', 'domain', 'github_name', 'subtask_categories',
            'eval_script_name', 'output_fname', 'dataset_folder_tree']
    rows = pq.read_table(annotation, columns=cols).to_pylist()
    assert len(rows) == 102 and len({r['instance_id'] for r in rows}) == 102
    # Historical development tasks 2/3 and author-visible reference exposures 1/11.
    exposure_ids = {1: 'AUTHOR_VISIBLE_REFERENCE_IN_PAPER', 11: 'REPORTED_BBBC002_REFERENCE_EXPOSURE',
                    2: 'EXISTING_DEVELOPMENT_ROLE', 3: 'EXISTING_DEVELOPMENT_ROLE'}
    dev_repos = {normalize_repo(r['github_name']) for r in rows if r['instance_id'] in (2, 3)}
    author_exposed_repos = {normalize_repo(r['github_name']) for r in rows if r['instance_id'] in (1, 11)}
    catalog = []
    with zipfile.ZipFile(archive) as stream:
        index = {info.filename: info for info in stream.infolist()}
        assert all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts for n in index)
        for row in sorted(rows, key=lambda r: r['instance_id']):
            name = 'benchmark/eval_programs/' + row['eval_script_name']
            assert name in index and index[name].file_size <= 1024**2
            raw = stream.read(name, pwd=b'scienceagentbench')
            # Only AST metadata leaves the evaluator boundary; no constants/targets or code are printed.
            try:
                syntax = syntax_info(raw)
            except (SyntaxError, UnicodeDecodeError) as error:
                syntax = {'parse_error_type': type(error).__name__,
                          'eval_entrypoint_present': False, 'reachable_external_judge_calls': [],
                          'external_import_review_flags': [], 'dynamic_review_flags': []}
            repo = normalize_repo(row['github_name'])
            excluded = []
            if repo in dev_repos:
                excluded.append('DEVELOPMENT_REPOSITORY_LINEAGE')
            if repo in author_exposed_repos:
                excluded.append('AUTHOR_REFERENCE_EXPOSED_REPOSITORY_LINEAGE')
            if syntax['reachable_external_judge_calls']:
                excluded.append('REACHABLE_EXTERNAL_MODEL_JUDGE')
            unknown = []
            if not syntax['eval_entrypoint_present']:
                unknown.append('UNRESOLVED_NATIVE_ENTRYPOINT')
            if syntax['external_import_review_flags'] and not syntax['reachable_external_judge_calls']:
                unknown.append('EXTERNAL_IMPORT_NEEDS_REACHABILITY_REVIEW')
            if syntax['dynamic_review_flags']:
                unknown.append('DYNAMIC_EXECUTION_REVIEW')
            catalog.append({'instance_id': row['instance_id'], 'domain': row['domain'],
                            'repository_lineage': repo, 'eval_script_name': row['eval_script_name'],
                            'output_suffix': PurePosixPath(row['output_fname']).suffix.lower(),
                            'evaluator_sha256': __import__('hashlib').sha256(raw).hexdigest(),
                            'evaluator_syntax': syntax, 'exposure_note': exposure_ids.get(row['instance_id']),
                            'rights_status': 'SOURCE_SPECIFIC_REVIEW_PENDING',
                            'native_environment': 'NOT_QUALIFIED', 'exclusion_reasons': excluded,
                            'unknown_reasons': unknown, 'native_reference_execution': 'NOT_RUN',
                            'candidate_model_execution': 'NOT_RUN'})
    potential = [r for r in catalog if not r['exclusion_reasons']]
    ready_syntax = [r for r in potential if not r['unknown_reasons']]
    upper_bound = {'tasks': len(potential), 'repository_lineages': len({r['repository_lineage'] for r in potential}),
                   'domains': len({r['domain'] for r in potential})}
    impossible = upper_bound['tasks'] < 60 or upper_bound['repository_lineages'] < 15 or upper_bound['domains'] < 3
    record = {'status': 'STATIC_CENSUS_COMPLETE_NATIVE_QUALIFICATION_NOT_RUN',
              'tasks_inspected': 102, 'archive_sha256': archive_hash,
              'annotation_sha256': expected, 'reference_bodies_or_expected_values_read': False,
              'evaluator_bodies_shown_to_author_or_model': False,
              'official_evaluator_executed': False, 'model_calls': 0, 'gpu_allocated_seconds': 0,
              'exclusion_counts': dict(Counter(x for r in catalog for x in r['exclusion_reasons'])),
              'unknown_counts': dict(Counter(x for r in potential for x in r['unknown_reasons'])),
              'conservative_potential_upper_bound': upper_bound,
              'syntax_only_candidates': len(ready_syntax),
              'coverage_potentially_impossible_from_static_census': impossible,
              'upper_bound_scope': 'No rights/environment/new-development/shared-data verification yet; optimistic count includes UNKNOWN rows; not admission',
              'catalog': catalog}
    write_new(folder / 'census-v1.json', record)
    write_new(PUBLIC / 'static-census-v1.json', record)
    csv_path = PUBLIC / 'static-census-v1.csv'
    with csv_path.open('x', encoding='utf-8', newline='') as output:
        fields = ['instance_id', 'domain', 'repository_lineage', 'eval_script_name',
                  'output_suffix', 'exposure_note', 'exclusion_reasons', 'unknown_reasons',
                  'native_environment', 'native_reference_execution', 'candidate_model_execution']
        writer = csv.DictWriter(output, fieldnames=fields)
        writer.writeheader()
        for row in catalog:
            writer.writerow({k: ';'.join(row[k]) if isinstance(row[k], list) else row[k] for k in fields})
    print(json.dumps({k: v for k, v in record.items() if k != 'catalog'}, indent=2))


if __name__ == '__main__':
    main()
