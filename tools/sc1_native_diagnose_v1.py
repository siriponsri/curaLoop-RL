"""Read only the three failed selected-validation stderr files; never rerun tests."""
import base64
import json
import subprocess
from tools.sc1_control_v1 import ACCOUNT, write_new
from tools.sc1_native_transport_v1 import SSH


def main():
    program = '''import json
from pathlib import Path
root=Path('/home/chaw/curaloop-tasks/lr-sc1-20261113-v1/control/qualify')
out={}
for identity in ('70.6','70.8','10.7'):
    path=root/('gold-'+identity+'.stderr.txt')
    if not path.is_file() or path.stat().st_size>16384:raise RuntimeError('Unexpected log identity/size')
    out[identity]=path.read_text()
print(json.dumps(out))
'''
    code = base64.b64encode(program.encode()).decode()
    command = "python3 -c \"import base64;exec(base64.b64decode('" + code + "'))\""
    p = subprocess.run(SSH + [command], capture_output=True, text=True, encoding="utf-8", timeout=40)
    record = {"returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr, "test_reruns": 0, "test_outcomes_opened": False}
    write_new(ACCOUNT / "native-diagnostic-v1.json", record)
    print(json.dumps(record))
    if p.returncode:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
