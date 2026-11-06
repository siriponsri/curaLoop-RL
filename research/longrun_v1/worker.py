"""One immutable, bounded LR-BC attempt. Detailed failures stay in private outputs."""

import argparse
import hashlib
import json
import os
import traceback
from pathlib import Path, PurePosixPath


def write_new(path, value):
    with Path(path).open('x', encoding='utf-8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())


def public_failure(error):
    return {'status': 'FAIL', 'error_type': type(error).__name__,
            'details': 'RETAINED_PRIVATELY', 'scientific_performance_evidence': False}


def verify_bundle(root, manifest_path, digest):
    raw = manifest_path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('Bundle manifest differs')
    manifest = json.loads(raw)
    paths = []
    for row in manifest['files']:
        path = PurePosixPath(row['path'])
        if path.is_absolute() or '..' in path.parts or '\\' in row['path']:
            raise ValueError('Unsafe bundle member')
        full = root / row['path']
        if full.is_symlink() or not full.resolve().is_relative_to(root.resolve()):
            raise ValueError('Bundle link or escape')
        payload = full.read_bytes()
        if len(payload) != row['bytes'] or hashlib.sha256(payload).hexdigest() != row['sha256']:
            raise ValueError('Pinned source or input differs')
        paths.append(row['path'])
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    if len(paths) != len(set(paths)) or actual != set(paths) | {'bundle.json'}:
        raise ValueError('Bundle inventory differs')
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--permit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--mode', choices=['fixtures', 'native', 'presence'], required=True)
    args = parser.parse_args()
    root = Path.cwd()
    permit = json.loads(args.permit.read_text())
    if args.output.name != permit['attempt'] or not args.output.is_dir():
        raise ValueError('Exclusive supervisor-created output partition required')
    from .guard import ResourceGuard
    guard = ResourceGuard(args.output / 'resources.json', permit)
    status = 'FAIL'
    try:
        verify_bundle(root, root / 'bundle.json', permit['bundle_sha256'])
        if args.mode == 'fixtures':
            from .fixtures import run
            result = run(root, args.output, json.loads((root / 'research/configs/lrbc_execution_v1.json').read_text()))
        elif args.mode == 'native':
            import numpy as np
            from rdkit import Chem, rdBase
            from rdkit.Chem import rdFingerprintGenerator
            molecule = Chem.MolFromSmiles('CCO')
            generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=128)
            fingerprint = generator.GetFingerprintAsNumPy(molecule)
            assert fingerprint.shape == (128,) and int(np.sum(fingerprint)) > 0
            result = {'status': 'PASS', 'native_canary': 'SYNTHETIC_ETHANOL_FINGERPRINT',
                      'numpy_version': np.__version__, 'rdkit_version': rdBase.rdkitVersion,
                      'source_requests': 0, 'scientific_performance_evidence': False}
        else:
            from .presence import project
            plan = json.loads((root / 'inputs/presence-request.json').read_text())
            result = project((root / 'inputs/native-submit.json').read_bytes(), plan)
        # Verify single-process policy by attempting creation, with no command run.
        if os.name != 'nt':
            try:
                child = os.fork()
            except PermissionError:
                result['native_child_creation_denied'] = True
            else:
                if child == 0:
                    os._exit(122)
                os.waitpid(child, 0)
                raise AssertionError('Child prohibition not active')
        else:
            import subprocess, sys
            try:
                subprocess.run([sys.executable, '-c', 'raise SystemExit(122)'], check=False)
            except OSError:
                result['native_child_creation_denied'] = True
            else:
                raise AssertionError('Windows child prohibition not active')
        write_new(args.output / 'result.json', result)
        status = 'PASS'
    except BaseException as error:
        (args.output / 'failure-private.txt').write_text(traceback.format_exc(), encoding='utf-8')
        write_new(args.output / 'failure.json', public_failure(error))
    finally:
        guard.finish(status)
    raise SystemExit(0 if status == 'PASS' else 1)


if __name__ == '__main__':
    main()
