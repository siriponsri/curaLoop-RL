"""Exact read-only live status for the current D1 calibration/control PID."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.d1_remote_v1 import configure, transport

name = sys.argv[1]
assert name in ("calibration", "controls")
configure()
code = '''import json,os
from pathlib import Path
p=Path('/home/chaw/curaloop-tasks/d1-operation-headroom-20261109-v1/jobs')/__NAME__
r=json.loads((p/'resource.json').read_text());pid=r['pid'];proc=Path('/proc')/str(pid)
live=proc.exists();ticks=(proc/'stat').read_text().split() if live else None
if live:
 command=(proc/'cmdline').read_bytes()
 assert b'research.d1_v1.worker' in command and str(p/'permit.json').encode() in command
print(json.dumps({'live_exact_pid':live,'pid':pid,'contexts_completed':len(list(p.glob('context-*.json'))),
 'controls_completed':len(list(p.glob('control-*.json')))//2,
 'process_cpu_seconds':(int(ticks[13])+int(ticks[14]))/os.sysconf('SC_CLK_TCK') if live else None,
 'result_exists':(p/'result.json').exists()}))
'''.replace("__NAME__", repr(name))
response = transport.remote(code, timeout=30)
assert response.returncode == 0, response.stderr.decode()[-300:]
print(json.dumps(json.loads(response.stdout)))
