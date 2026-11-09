"""Versioned namespace adaptation of the verified D1 complete-return procedure."""
# ruff: noqa: E402

import hashlib
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.lr_d23_v1.common import (
    TASK, authority, ledger_save, new, orchestration_start, read, sha, utility_finish,
)
from tools.lrd23_remote_v1 import book


def implementation():
    release, _ = authority()
    source_path = ROOT / "tools/d1_return_v1.py"
    assert sha(source_path) == "ae24a17392ce9c9058190dff8415ae767a223f6034131ab7fcd50e566f3ab14b"
    # The old source is read, never edited; its hash is retained in the receipt.
    source = source_path.read_text(encoding="utf-8")
    source = source.replace("d1-operation-headroom-20261109-v1", "lr-d23-20261109-v1")
    source = source.replace("curaloop-d1-", "curaloop-lrd23-")
    source = source.replace("curaloop.d1.", "curaloop.lr_d23.")
    source = source.replace("2026-11-10T10:39:56.772249+00:00", release["deadline_utc"])
    source = source.replace("docs/evidence/d1-20261109-v1", "docs/evidence/lr-d23-20261109-v1")
    # Exact legacy public path spelling is checked below before any action.
    module = types.ModuleType("_lrd23_private_return")
    module.__file__ = __file__
    exec(compile(source, str(source_path) + "[LR-D23 namespace]", "exec"), vars(module))
    assert module.LOCAL == TASK and module.REMOTE.endswith("/lr-d23-20261109-v1")
    assert module.PUBLIC == ROOT / "docs/evidence/lr-d23-20261109-v1", module.PUBLIC
    return module, hashlib.sha256(source_path.read_bytes()).hexdigest()


def prepare():
    release, ledger = authority()
    assert not any(b["status"] == "RESERVED" for b in ledger["bookings"].values())
    _, source_sha = implementation()
    common = {"wall_seconds": 600}
    book("return-export-v1", "return", 69, "utilities_handoff", 1, 180, common)
    book("return-fetch-v1", "return", 69, "utilities_handoff", 1, 210, common)
    book("return-verify-v1", "return", 0, "utilities_handoff", 1, 180,
         dict(common, host="local", memory_bytes=1073741824))
    book("remote-exact-cleanup-v1", "return", 69, "utilities_handoff", 1, 90, {"wall_seconds": 120})
    new(TASK / "return-adaptation-v1.json", {"status": "PASS_SCOPED_ADAPTATION", "legacy_source_sha256": source_sha,
                                           "deadline_utc": release["deadline_utc"], "old_source_edited": False})


def run(action):
    module, _ = implementation()
    name = {"export": "return-export-v1", "fetch": "return-fetch-v1", "verify": "return-verify-v1",
            "cleanup": "remote-exact-cleanup-v1"}[action]
    if action == "verify":
        module.verify()
    else:
        guard = orchestration_start("local-return-" + action, 120, 1900 if action == "fetch" else 720)
        try:
            getattr(module, action)()
            utility_finish("local-return-" + action, guard, "PASS")
        except BaseException:
            utility_finish("local-return-" + action, guard, "FAIL")
            raise
    ledger = read(TASK / "ledger.json")
    ledger["bookings"][name]["status"] = "PASS"
    resource = TASK / "jobs" / name / "resource.json"
    ledger["bookings"][name]["resource_sha256"] = sha(resource) if resource.exists() else None
    ledger_save(ledger)


if __name__ == "__main__":
    action = sys.argv[1]
    assert action in ("prepare", "export", "fetch", "verify", "cleanup")
    prepare() if action == "prepare" else run(action)
