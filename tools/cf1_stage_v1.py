"""Append-only authenticated source/metadata staging inside the owned CF1 root."""
# ruff: noqa: E402

import json
import re
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import TASK, new, sha
from tools import cf1_remote_v1 as remote
from tools import m2c_remote_v2 as transport


def stage(name, files, bucket="utilities_return_handoff_delivery"):
    assert re.fullmatch(r"[a-z0-9-]+", name)
    assert all(source.resolve().is_relative_to(ROOT) for source, target in files)
    assert all(not Path(target).is_absolute() and ".." not in Path(target).parts for source, target in files)
    manifest = {"schema": "curaloop.cf1.append-only-stage.v1", "biological_inputs_included": False,
                "files": [{"path": target, "bytes": source.stat().st_size, "sha256": sha(source)} for source, target in files]}
    assert len({row["path"] for row in manifest["files"]}) == len(files) < 100
    assert sum(row["bytes"] for row in manifest["files"]) < 4 * 1024**2
    new(TASK / "stages" / (name + "-manifest.json"), manifest)
    archive = TASK / "stages" / (name + ".tar.gz")
    with tarfile.open(archive, "x:gz", compresslevel=1) as output:
        for source, target in files:
            output.add(source, arcname=target, recursive=False)
        output.add(TASK / "stages" / (name + "-manifest.json"), arcname="transport-manifest.json")
    remote.book(name, "bootstrap", 60, bucket, extra={"wall_seconds": 300,
        "bundle_sha256": sha(archive), "arguments": {"archive_bytes": archive.stat().st_size, "archive_sha256": sha(archive)}})
    remote.configure()
    original = transport.BOOTSTRAP
    try:
        old = "  for block in iter(lambda:sys.stdin.buffer.read(1048576),b''):\n   count+=len(block);assert count<=permit['arguments']['archive_bytes'];archive.write(block);h.update(block)"
        fixed = "  remaining=permit['arguments']['archive_bytes']\n  while remaining:\n   block=sys.stdin.buffer.read(min(1048576,remaining));assert block,'TRUNCATED_STAGE';remaining-=len(block)\n   count+=len(block);assert count<=permit['arguments']['archive_bytes'];archive.write(block);h.update(block)"
        assert old in original
        body = original.replace(old, fixed)
        target = "dest=(root/name).resolve()"
        assert target in body
        body = body.replace(target, "dest=(root/(" + repr("transport-" + name + "-manifest.json") + " if name=='transport-manifest.json' else name)).resolve()")
        transport.BOOTSTRAP = body
        code, permit = transport.render_dispatch("bootstrap", name)
    finally:
        transport.BOOTSTRAP = original
    code = code.replace("m2-costed-20261108-v2", "lr-cf1-20261109-v1")
    code = code.replace("curaloop-m2c-20261108-v1-", "curaloop-cf1-20261109-v1-")
    creation = "if True:root.mkdir(parents=True,exist_ok=False);root.chmod(0o700)"
    assert creation in code
    code = code.replace(creation, "assert root.is_dir() and not root.is_symlink()")
    assert len(code.encode()) * 4 / 3 < 26000
    compile(code, "<append-only-cf1-stage>", "exec")
    folder = TASK / "jobs" / name
    with (folder / "remote-command.py").open("x", encoding="utf-8", newline="\n") as file:
        file.write(code)
    with archive.open("rb") as stream:
        result = transport.remote(code, stdin=stream, timeout=permit["wall_seconds"] + 60)
    new(folder / "ssh-response.json", {"exit_code": result.returncode, "stdout": result.stdout.decode(), "stderr": result.stderr.decode()})
    assert result.returncode == 0
    assert remote.settle(name, json.loads(result.stdout)) == "PASS"
    return manifest
