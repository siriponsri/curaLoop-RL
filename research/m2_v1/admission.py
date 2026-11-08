"""Outcome-blind six-pool admission under the local M2 resource permit."""
import hashlib
import json
import os
import sys
from pathlib import Path

from research.longrun_v1.guard import ResourceGuard

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(1048576), b''):
            h.update(b)
    return h.hexdigest()


def new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, allow_nan=False); f.write('\n')


class M2Guard(ResourceGuard):
    def _write(self, status):
        self.base = dict(self.base, schema='curaloop.m2.resources.v1',
                         release_utc=self.permit['release_utc'],
                         reservation_seconds=self.permit['reservation_seconds'])
        super()._write(status)

    def kernel_proof(self):
        if os.name == 'nt':
            return {'mechanism':self.child_policy,'affinity':self._windows_affinity(),
                    'memory_bytes':self.ram_limit,'process_cpu_seconds':self.cpu_limit}
        cg=Path('/sys/fs/cgroup'+next(s.split('::',1)[1] for s in Path('/proc/self/cgroup').read_text().splitlines() if s.startswith('0::')))
        proof={k:(cg/k).read_text().strip() for k in ('cpu.max','memory.max','memory.swap.max')}
        assert proof['cpu.max']=='100000 100000' and proof['memory.max']==str(self.ram_limit) and proof['memory.swap.max']=='0'
        return proof


def admit(task):
    scope = json.loads((ROOT / 'research/manifests/m2_data_scope_20261108_v1.json').read_text())
    cfg = json.loads((ROOT / 'research/configs/goal4_protocol_v1.json').read_text())
    manifest = ROOT / cfg['cohort_manifest']
    assert sha(manifest) == scope['expected_feature_manifest_sha256'] == cfg['cohort_manifest_sha256']
    cohort = json.loads(manifest.read_text())
    expected_ids = {t['task_id'] for t in scope['tasks']}
    selected = {e['assay_id']: e for e in cohort['selected_assays'] if e['role'] == 'development'}
    assert set(selected) == expected_ids
    protection_path = ROOT / '.local/r0r-chembl-20261107-v1/protection-index-private.json'
    assert sha(protection_path) == scope['expected_protection_metadata_sha256']
    protection = json.loads(protection_path.read_text())
    assert protection['outcome_values_present'] is False
    protected = set(protection['canonical_smiles'])
    assays, groups = set(protection['assay_ids']), set(protection['family_ids'])
    pools, canonical_groups = {}, {}
    for t in scope['tasks']:
        tid = t['task_id']; entry = selected[tid]
        path = (manifest.parent / entry['feature_file']).resolve()
        assert path.parent == manifest.parent.resolve() and not path.is_symlink()
        assert sha(path) == t['expected_feature_sha256'] == entry['feature_sha256']
        feature = json.loads(path.read_text())
        assert feature['task_id'] == tid and feature['role'] == 'development'
        group = next(g['id'] for g in scope['groups'] if tid in g['assays'])
        assert feature['family_id'] == entry['family_id'] == group
        assert tid not in assays and group not in groups
        records = feature['records']
        assert len(records) == t['rows'] == len({r['candidate_id'] for r in records})
        assert not protected.intersection(r['canonical_smiles'] for r in records)
        for r in records:
            assert 'active' not in r and 'pchembl_value' not in r and 'standard_value' not in r
            assert r['candidate_id'] == 's-' + hashlib.sha256(r['canonical_smiles'].encode()).hexdigest()
            assert all(type(bit) is int and 0 <= bit < 1024 for bit in r['morgan_on_bits'])
            canonical_groups.setdefault(r['canonical_smiles'], set()).add(group)
        # Authenticate opaque allowlisted label files without decoding.
        source = ROOT / t['private_input_path']
        assert source.resolve().parent == (ROOT / '.local/lr-m12-20261108-v1/inputs/development').resolve()
        assert not source.is_symlink() and sha(source) == t['expected_input_sha256']
        pools[tid] = {'group': group, 'records': records, 'source_feature': str(path.relative_to(ROOT)),
                      'source_input': t['private_input_path'], 'input_sha256': t['expected_input_sha256']}
    shared = {c for c,g in canonical_groups.items() if len(g) > 1}
    summary = []
    for tid,pool in pools.items():
        retained = [r['candidate_id'] for r in pool['records'] if r['canonical_smiles'] not in shared]
        pool['training_candidate_ids'] = retained
        summary.append({'task_id': tid, 'component_id': pool['group'], 'evaluation_rows': len(pool['records']),
                        'training_rows': len(retained), 'removed_training_rows': len(pool['records'])-len(retained)})
    coverage = all(s['training_rows'] >= 48 for s in summary)
    new(task / 'admission/features-and-mask-private.json', {'pools': pools})
    result = {'status': 'PASS_OUTCOME_BLIND_ADMISSION' if coverage else 'STOP_TRAINING_COVERAGE',
              'tasks': summary, 'canonical_structures': len(canonical_groups),
              'cross_component_canonical_structures': len(shared),
              'minimum_training_rows': 48, 'training_mask_outcome_blind': True,
              'evaluation_pools_unchanged': True, 'opaque_input_hashes_verified': True,
              'protected_metadata_checked': True, 'labels_decoded': False,
              'final_feature_label_presence_decoded': False,
              'private_mask_sha256': sha(task / 'admission/features-and-mask-private.json')}
    new(task / 'admission/summary.json', result)
    return result


def main():
    permit = json.loads(Path(sys.argv[1]).read_text())
    assert permit['schema'] == 'curaloop.m2.permit.v1' and permit['host'] == 'local'
    assert permit['memory_bytes'] == 536870912
    task = ROOT / '.local/m2-selective-compute-20261108-v1'
    job = task / 'jobs' / permit['attempt']
    guard = M2Guard(job / 'resource.json', permit)
    try:
        result = admit(task)
        new(job / 'result.json', result)
        guard.finish('PASS')
        print(json.dumps(result))
    except BaseException as e:
        new(job / 'failure.json', {'type':type(e).__name__,'message':str(e)[:240]})
        guard.finish('FAIL')
        raise


if __name__ == '__main__':
    main()
