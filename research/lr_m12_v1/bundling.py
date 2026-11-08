"""Authenticated offline dependencies plus admitted development pools only."""

import hashlib
import io
import json
import tarfile
from pathlib import Path

from research.lr_m12_v1.guard import write_new

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
    return digest.hexdigest()


def build_bundle(arguments, task_root):
    old = ROOT / '.local/goal4r1-20261105-v1/remote-return/full-v1'
    old_manifest = old / 'manifest.json'
    assert sha(old_manifest) == '15ebe921421336e0c1179f851bd929efddc0e5e0d5b69519706d70568b2b0f95'
    records = json.loads(old_manifest.read_text())['files']
    marker = '.venv/lib/python3.12/site-packages/'
    wanted = ('numpy', 'numpy.libs', 'numpy-2.3.5.dist-info', 'scipy', 'scipy.libs',
              'scipy-1.17.0.dist-info', 'threadpoolctl.py', 'threadpoolctl-3.6.0.dist-info')
    selected = []
    for row in records:
        name = row['path']
        if not name.startswith(marker):
            continue
        relative = name[len(marker):]
        if relative.split('/', 1)[0] not in wanted or '__pycache__' in relative or relative.endswith('.pyc'):
            continue
        path = old / 'files' / name
        assert path.is_file() and not path.is_symlink() and path.stat().st_size == row['bytes']
        assert sha(path) == row['sha256'], 'OFFLINE_VENDOR_HASH_MISMATCH'
        selected.append((path, 'vendor/' + relative, row['sha256']))
    assert selected and sum(p.stat().st_size for p, _, _ in selected) <= 1024**3
    code_paths = sorted((ROOT / 'research/lr_m12_v1').glob('*.py'))
    code_paths += [ROOT / p for p in (
        'research/__init__.py', 'research/longrun_v1/__init__.py', 'research/longrun_v1/guard.py',
        'research/redesign_v1/__init__.py', 'research/redesign_v1/belief.py',
        'research/planning_v3/__init__.py', 'research/planning_v3/belief.py', 'research/planning_v3/mixture.py')]
    pins = {}
    for path in code_paths:
        rel = path.relative_to(ROOT).as_posix()
        digest = sha(path)
        pins[rel] = digest
        selected.append((path, 'code-v1/' + rel, digest))
    inputs = json.loads((task_root / 'inputs/manifest-v1.json').read_text())
    for row in inputs['tasks']:
        if row['status'] == 'ADMITTED_EXPOSED_DEVELOPMENT':
            path = task_root / row['input_relative']
            assert sha(path) == row['input_sha256']
            selected.append((path, row['input_relative'], row['input_sha256']))
    manifest_path = task_root / 'inputs/manifest-v1.json'
    selected.append((manifest_path, 'inputs/manifest-v1.json', sha(manifest_path)))
    assert not any('..' in Path(name).parts for _, name, _ in selected)
    assert all(not name.startswith('inputs/') or name == 'inputs/manifest-v1.json'
               or name.startswith('inputs/development/') for _, name, _ in selected)
    manifest = {'schema': 'curaloop.lr_m12.transport.v1', 'python_abi': 'CPython3.12_Linux',
                'files': [{'path': name, 'bytes': path.stat().st_size, 'sha256': digest}
                          for path, name, digest in selected], 'code_sha256': pins,
                'reserved_final_data_included': False}
    archive = task_root / 'transport-v1.tar.gz'
    with tarfile.open(archive, 'x:gz', compresslevel=1) as stream:
        for path, name, _ in selected:
            stream.add(path, arcname=name, recursive=False)
        data = (json.dumps(manifest, indent=2) + '\n').encode()
        info = tarfile.TarInfo('transport-manifest-v1.json')
        info.size = len(data)
        info.mode = 0o600
        stream.addfile(info, io.BytesIO(data))
    result = {'status': 'PASS_AUTHENTICATED_OFFLINE_BUNDLE', 'file_count': len(selected),
              'source_bytes': sum(p.stat().st_size for p, _, _ in selected),
              'archive_bytes': archive.stat().st_size, 'archive_sha256': sha(archive),
              'archive_relative': archive.relative_to(task_root).as_posix(),
              'source_manifest_sha256': sha(old_manifest), 'code_sha256': pins,
              'final_data_included': False}
    write_new(task_root / 'transport-manifest-v1.json', manifest)
    return result
