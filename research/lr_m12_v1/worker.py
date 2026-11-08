"""Permit-guarded LR-M12 worker; fixed handlers, no arbitrary script execution."""

import hashlib
import json
import os
import sys
from pathlib import Path

from research.lr_m12_v1.guard import M12Guard, write_new

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canary(arguments, task_root):
    if arguments.get('numeric_libraries') is False:
        return {'status': 'PASS_GUARDED_METADATA_CANARY', 'numeric_libraries_loaded': False,
                'scientific_dataset_access': False}
    import numpy as np
    import scipy
    from threadpoolctl import threadpool_info

    value = float(np.array([1.0, 2.0]) @ np.array([3.0, 4.0]))
    assert value == 11
    pools = threadpool_info()
    assert all(p['num_threads'] == 1 for p in pools)
    return {'status': 'PASS_GUARDED_CPU_ONLY_CANARY', 'numpy': np.__version__,
            'scipy': scipy.__version__, 'blas_threads': [p['num_threads'] for p in pools],
            'scientific_dataset_access': False}


def prepare_inputs(arguments, task_root):
    assert os.name == 'nt', 'Initial admitted-input projection is local-only'
    prior_path = ROOT / 'research/configs/goal4r1_protocol_v1.json'
    prior = json.loads(prior_path.read_text())
    cohort_protocol = json.loads((ROOT / 'research/configs/goal4_protocol_v1.json').read_text())
    cohort_path = ROOT / cohort_protocol['cohort_manifest']
    assert sha(cohort_path) == cohort_protocol['cohort_manifest_sha256']
    cohort = json.loads(cohort_path.read_text())
    protection_path = ROOT / '.local/r0r-chembl-20261107-v1/protection-index-private.json'
    assert arguments['protection_sha256'] == 'a189e3064b28e09e0099db0dd81ee80b08475ccf39b134bdec37ccd341789520'
    assert sha(protection_path) == arguments['protection_sha256']
    protection = json.loads(protection_path.read_text())
    assert protection['outcome_values_present'] is False
    protected = set(protection['canonical_smiles'])
    final_assays, final_families = set(protection['assay_ids']), set(protection['family_ids'])
    by_id = {a['assay_id']: a for a in cohort['selected_assays'] if a['role'] == 'development'}
    records = []
    for task in prior['tasks']:
        tid = task['task_id']
        entry = by_id[tid]
        assert task['role'] == entry['role'] == 'development'
        feature_path = cohort_path.parent / entry['feature_file']
        assert feature_path.parent.resolve() == cohort_path.parent.resolve()
        assert sha(feature_path) == entry['feature_sha256']
        feature = json.loads(feature_path.read_text())
        assert feature['role'] == 'development' and feature['task_id'] == tid
        ids = {row['candidate_id'] for row in feature['records']}
        assert len(ids) == len(feature['records']) == task['rows']
        assert all(row['candidate_id'] == 's-' + hashlib.sha256(row['canonical_smiles'].encode()).hexdigest()
                   for row in feature['records'])
        conflict = (bool(protected & {row['canonical_smiles'] for row in feature['records']})
                    or tid in final_assays or feature['family_id'] in final_families)
        if conflict:
            records.append({'task_id': tid, 'status': 'WITHHELD_PROTECTION_CONFLICT',
                            'label_file_decoded': False})
            continue
        source = ROOT / '.local/goal4r1-20261105-v1/private-inputs' / (tid + '.json')
        assert sha(source) == task['sha256']  # opaque authentication before decode
        payload = json.loads(source.read_text())
        assert payload['task_id'] == tid and payload['role'] == 'development'
        assert payload['family_id'] == task['family_id'] == feature['family_id']
        assert {r['candidate_id'] for r in payload['records']} == ids
        assert len(payload['records']) == task['rows']
        public_by_id = {r['candidate_id']: r for r in feature['records']}
        assert all(type(r['active']) is bool and r['morgan_on_bits'] == public_by_id[r['candidate_id']]['morgan_on_bits']
                   for r in payload['records'])
        dest = task_root / 'inputs/development' / (tid + '.json')
        write_new(dest, payload)
        records.append({'task_id': tid, 'status': 'ADMITTED_EXPOSED_DEVELOPMENT', 'rows': task['rows'],
                        'feature_sha256': entry['feature_sha256'], 'source_sha256': task['sha256'],
                        'input_sha256': sha(dest), 'input_relative': dest.relative_to(task_root).as_posix(),
                        'label_file_decoded': True})
    result = {'schema': 'curaloop.lr_m12.admitted_inputs.v1', 'tasks': records,
              'protection_sha256': sha(protection_path), 'protection_before_label_decode': True,
              'reserved_final_feature_or_outcome_decode': False, 'old_exposed_validation_prepared': False}
    write_new(task_root / 'inputs/manifest-v1.json', result)
    return result


def main():
    permit_path = Path(sys.argv[1])
    permit = json.loads(permit_path.read_text())
    assert permit['schema'] == 'curaloop.lr_m12.permit.v1'
    assert permit['release_utc'] == '2026-11-08T05:10:46Z'
    assert permit['deadline_utc'] == '2026-11-11T05:10:46Z'
    task_root = Path(permit['task_root']).resolve()
    assert task_root.name == 'lr-m12-20261108-v1'
    assert permit['handler'] in ('canary', 'prepare_inputs', 'build_bundle', 'checks', 'adapter_diagnostics')
    for path, expected in permit['code_sha256'].items():
        assert sha(ROOT / path) == expected, 'LR_M12_CODE_PIN_MISMATCH'
    job_root = task_root / 'jobs' / permit['attempt']
    guard = M12Guard(job_root / 'resource.json', permit)
    try:
        proof = guard.kernel_proof()
        write_new(job_root / 'kernel-proof.json', proof)
        if permit['handler'] == 'build_bundle':
            from research.lr_m12_v1.bundling import build_bundle
            result = build_bundle(permit['arguments'], task_root)
        elif permit['handler'] == 'checks':
            from research.lr_m12_v1.checks import run_checks
            result = run_checks(permit['arguments'], task_root)
        elif permit['handler'] == 'adapter_diagnostics':
            from research.lr_m12_v1.diagnostics import adapter_diagnostics
            result = adapter_diagnostics(permit['arguments'], task_root)
        else:
            result = {'canary': canary, 'prepare_inputs': prepare_inputs}[permit['handler']](permit['arguments'], task_root)
        write_new(job_root / 'result.json', result)
        guard.finish('PASS')
        print(json.dumps({'job': permit['attempt'], 'status': 'PASS'}))
    except BaseException as exc:
        write_new(job_root / 'failure.json', {'type': type(exc).__name__, 'message': str(exc)[:240]})
        guard.finish('FAIL')
        raise


if __name__ == '__main__':
    main()
