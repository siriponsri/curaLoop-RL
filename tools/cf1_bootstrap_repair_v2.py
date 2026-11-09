"""Same authenticated bundle, bounded read and retained-root technical retry."""
# ruff: noqa: E402

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import TASK, finish, new, read, start
from tools import cf1_remote_v1 as remote
from tools import m2c_remote_v2 as transport


def main():
    inspected = read(TASK / "bootstrap-terminal-inspection-v1.json")
    assert inspected["unit"]["MainPID"] == "0" and inspected["unit"]["ActiveState"] == "failed"
    assert all(p.startswith("jobs/bootstrap/") for p in inspected["files"])
    name = "bootstrap-retry-v2"
    archive = TASK / "transport-technical-v1.tar.gz"
    remote.book(name, "bootstrap", 60, "technical_retry_reserve", extra={"wall_seconds": 1200,
        "arguments": {"archive_bytes": archive.stat().st_size, "archive_sha256": remote.sha(archive)}})
    remote.configure()
    original = transport.BOOTSTRAP
    try:
        body = original.replace("manifest['biological_inputs_included'] is False", "manifest['biological_inputs_included'] is True")
        body = body.replace("'biological_inputs_included':False", "'biological_inputs_included':True")
        old = "  for block in iter(lambda:sys.stdin.buffer.read(1048576),b''):\n   count+=len(block);assert count<=permit['arguments']['archive_bytes'];archive.write(block);h.update(block)"
        fixed = "  remaining=permit['arguments']['archive_bytes']\n  while remaining:\n   block=sys.stdin.buffer.read(min(1048576,remaining));assert block,'TRUNCATED_TRANSPORT';remaining-=len(block)\n   count+=len(block);assert count<=permit['arguments']['archive_bytes'];archive.write(block);h.update(block)"
        assert old in body
        transport.BOOTSTRAP = body.replace(old, fixed)
        code, permit = transport.render_dispatch("bootstrap", name)
    finally:
        transport.BOOTSTRAP = original
    code = code.replace("m2-costed-20261108-v2", "lr-cf1-20261109-v1")
    code = code.replace("curaloop-m2c-20261108-v1-", "curaloop-cf1-20261109-v1-")
    creation = "if True:root.mkdir(parents=True,exist_ok=False);root.chmod(0o700)"
    assert creation in code
    code = code.replace(creation, "assert root.is_dir() and not root.is_symlink()")
    assert len(code.encode()) * 4 / 3 < 26000 and "curaloop-tasks/m2-" not in code
    compile(code, "<bounded-cf1-bootstrap-repair>", "exec")
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    with archive.open("rb") as stream:
        result = transport.remote(code, stdin=stream, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-response.json", {"exit_code": result.returncode,
                                      "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0
    import json
    value = json.loads(result.stdout)
    assert remote.settle(name, value) == "PASS"
    print("PASS bounded transport on retained task root; original failed attempt retained")


if __name__ == "__main__":
    guard = start("bootstrap-repair-transport-v2", 180, 1400,
                  bucket="utilities_return_handoff_delivery", orchestration=True)
    try:
        main()
        finish("bootstrap-repair-transport-v2", guard, "PASS_BOUNDED_BOOTSTRAP_REPAIR")
    except BaseException:
        finish("bootstrap-repair-transport-v2", guard, "FAIL")
        raise
