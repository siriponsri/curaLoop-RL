"""One-time extraction of preserved, tested Docker I/O into a new worker."""

import ast
from pathlib import Path

source = Path("tools/agent_rd_remote_worker_v1.py").read_text()
tree = ast.parse(source)
names = {"UnixConnection", "api", "execute", "docker", "stamp", "cpu_seconds", "http"}
selected = [
    ast.get_source_segment(source, n)
    for n in tree.body
    if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names
]
assert len(selected) == len(names)
imports = [
    ast.get_source_segment(source, n)
    for n in tree.body
    if isinstance(n, (ast.Import, ast.ImportFrom))
]
header = '''"""Owned GPU worker; Docker I/O reused from preserved AgentRD source."""

'''
header += "\n".join(imports)
header += """

TASK = Path.home() / "curaloop-tasks/lr-dc2-local-20261113-v1"
NAME = "curaloop-dc2-local-model-20261113-v1"
MODEL = "hf.co/scb10x/typhoon2.1-gemma3-12b-gguf:Q4_K_M"
DIGEST = "ab914ef406c9a78e2a8893eaa3b0ef78049f6c4e2703626433028e838d3a168b"
GPU = "GPU-277ccc57-c3e5-0731-cd49-f4f8695f7089"
IMAGE = "sha256:a61a8fd395dbb931cc8cb1b5da7a2510746575c87113fdc45b647ee59ef7f808"
API_VERSION = None

"""
path = Path("tools/dc2_local_model_worker_v1.py")
assert not path.exists()
path.write_text(header + "\n\n".join(selected) + "\n", encoding="utf-8")
