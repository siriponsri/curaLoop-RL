"""Append-only CF1 adaptation of the authenticated complete private return."""
# ruff: noqa: E402

import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import (
    PUBLIC,
    REMOTE,
    TASK,
    authority,
    finish,
    new,
    read,
    save,
    sha,
    start,
)
from tools.cf1_remote_v1 import book


def implementation():
    release, _ = authority()
    path = ROOT / "tools/d1_return_v1.py"
    assert sha(path) == "ae24a17392ce9c9058190dff8415ae767a223f6034131ab7fcd50e566f3ab14b"
    source = path.read_text(encoding="utf-8")
    source = source.replace("d1-operation-headroom-20261109-v1", "lr-cf1-20261109-v1")
    source = source.replace("curaloop-d1-", "curaloop-cf1-")
    source = source.replace("curaloop.d1.", "curaloop.cf1.")
    source = source.replace("2026-11-10T10:39:56.772249+00:00", release["deadline_utc"])
    # The release permits <=8GiB of all owned remote artifacts, including export.
    # Compression is streaming; no data or member is dropped to meet that cap.
    source = source.replace("sum(r['bytes'] for r in rows)<4*1024**3", "sum(r['bytes'] for r in rows)<8*1024**3")
    source = source.replace("assert archive.stat().st_size<1024**3", "assert sum(r['bytes'] for r in rows)+archive.stat().st_size<8*1024**3")
    source = source.replace("manifest['archive_bytes']<1024**3", "manifest['archive_bytes']<8*1024**3")
    source = source.replace("with tarfile.open(archive,'x:gz',compresslevel=1) as tf:\n  for row in rows:tf.add(root/row['path'],arcname=row['path'],recursive=False)",
        """limit=8*1024**3-sum(r['bytes'] for r in rows)-32*1024**2
 assert limit>0
 class LimitedWriter:
  def __init__(self,raw):self.raw=raw
  def write(self,data):
   assert self.raw.tell()+len(data)<=limit,'OWNED_ARTIFACT_PLUS_EXPORT_CAP'
   return self.raw.write(data)
  def tell(self):return self.raw.tell()
  def flush(self):return self.raw.flush()
 with archive.open('xb') as raw:
  with tarfile.open(fileobj=LimitedWriter(raw),mode='w:gz',compresslevel=1) as tf:
   for row in rows:tf.add(root/row['path'],arcname=row['path'],recursive=False)""")
    source = source.replace("permit['wall_seconds'] == 600", "permit['wall_seconds'] == 1800")
    source = source.replace("cpu=permit['cpu'], wall=600", "cpu=permit['cpu'], wall=1800")
    module = types.ModuleType("_cf1_private_return")
    module.__file__ = __file__
    exec(compile(source, str(path) + "[CF1 namespace]", "exec"), vars(module))
    assert module.LOCAL == TASK and module.REMOTE == REMOTE and module.PUBLIC == PUBLIC
    return module, sha(path)


def prepare():
    _, ledger = authority()
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    _, source_sha = implementation()
    for name, cpu in (("return-export-v1", 600), ("return-fetch-v1", 300),
                      ("return-verify-v1", 600), ("remote-exact-cleanup-v1", 180)):
        extra = {"wall_seconds": 1800, "release_utc": ledger["release_utc"]}
        if name == "return-verify-v1":
            extra.update(host="local", memory_bytes=1073741824)
        book(name, "return", cpu, "utilities_return_handoff_delivery", processor=0 if name == "return-verify-v1" else 69, extra=extra)
    new(TASK / "return-adaptation-v1.json", {"status": "PASS_SCOPED_COMPLETE_RETURN_ADAPTATION",
        "legacy_source_sha256": source_sha, "legacy_source_edited": False,
        "deadline_utc": ledger["deadline_utc"], "all_owned_artifact_cap_bytes": 8 * 1024**3})


def run(action):
    module, _ = implementation()
    name = {"export": "return-export-v1", "fetch": "return-fetch-v1", "verify": "return-verify-v1",
            "cleanup": "remote-exact-cleanup-v1"}[action]
    if action == "verify":
        module.verify()
    else:
        guard = start("return-local-" + action, 300, 2100,
                      bucket="utilities_return_handoff_delivery", orchestration=True)
        try:
            getattr(module, action)()
            finish("return-local-" + action, guard, "PASS_COMPLETE_RETURN_" + action.upper())
        except BaseException:
            finish("return-local-" + action, guard, "FAIL")
            raise
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name]["status"] = "PASS"
    resource = TASK / "jobs" / name / "resource.json"
    ledger["bookings"][name]["resource_sha256"] = sha(resource) if resource.exists() else None
    save(ledger)


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("prepare", "export", "fetch", "verify", "cleanup")
    prepare() if action == "prepare" else run(action)
