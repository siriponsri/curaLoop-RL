"""Generate the final bounded transport repair without altering prior attempts."""

import ast
from pathlib import Path

source = Path("tools/dc2_local_native_recover_v2.py").read_text(encoding="utf-8")
node = next(
    n
    for n in ast.parse(source).body
    if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == "INSTALL" for t in n.targets)
)
program = r"""
import base64,hashlib,importlib.util,json
from pathlib import Path
root=Path.home()/'curaloop-tasks/lr-dc2-local-20261113-v1'
p=json.load(__import__('sys').stdin)
raw=base64.b64decode(p['source_b64'],validate=True)
assert hashlib.sha256(raw).hexdigest()==p['source_sha256']
assert hashlib.sha256((root/'native-worker-v1.py').read_bytes()).hexdigest()==p['previous_sha256']
assert not (root/'native-worker-v2.py').exists()
spec=importlib.util.spec_from_file_location('owned_io',root/'worker.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.authority()
name='curaloop-dc2-local-native-20261113-v1'
assert not any('/'+name in r['Names'] for r in m.api('GET','/containers/json?all=1'))
target=root/'native-v1/control/2/failed-start-container-inspection.json'
v=json.loads(target.read_text())
assert v['Config']['Labels']['curaloop.task']=='lr-dc2-local-20261113-v1'
assert v['Config']['Labels']['curaloop.purpose']=='native-reference'
assert v['Image']=='sha256:6ff506466f8b1e981719b468cc0023b8ef000b983cdec0eafe119d01f379e31d'
assert not v['State']['Running'] and v['State']['StartedAt'].startswith('0001-')
(root/'native-worker-v2.py').write_bytes(raw)
assert hashlib.sha256((root/'native-worker-v2.py').read_bytes()).hexdigest()==p['source_sha256']
print(json.dumps({'status':'PASS_BYTE_EXACT_VERSIONED_TRANSPORT_AND_PRIOR_OWNED_ABSENCE','original_state':v['State'],'reference_process_started':False,'original_worker_preserved':True,'prior_exact_removal_had_already_occurred':True,'new_worker_sha256':p['source_sha256']}))
"""
lines = source.splitlines(keepends=True)
source = (
    "".join(lines[: node.lineno - 1])
    + "INSTALL = "
    + repr(program)
    + "\n"
    + "".join(lines[node.end_lineno :])
)
old = '"source": WORKER.read_text(encoding="utf-8")'
assert source.count(old) == 1
source = source.replace(old, '"source_b64": base64.b64encode(WORKER.read_bytes()).decode("ascii")')
for old in (
    "native-qualification-v2",
    "native-dependency-repair-v2",
    "native-mount-failure-repair-v2",
    "native-reference-qualification-v2",
    "native-reference-{identity:03d}-v2",
):
    assert old in source, old
    source = source.replace(old, old[:-2] + "v3")
target = Path("tools/dc2_local_native_recover_v3.py")
assert not target.exists()
target.write_text(source, encoding="utf-8", newline="\n")
