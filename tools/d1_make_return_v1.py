"""Derive the existing audited full-return workflow for the fresh D1 root."""
# ruff: noqa: E402 -- repository-only CLI import bootstrap.

import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.d1_v1.common import OLD, TASK, authority, new, read, sha


def main():
    release, _ = authority()
    source = (ROOT / "tools/m2c_return_v2.py").read_text(encoding="utf-8")
    source = source.replace("m2-costed-20261108-v2", "d1-operation-headroom-20261109-v1")
    source = source.replace("curaloop-m2c-20261108-v1-", "curaloop-d1-20261109-v1-")
    source = source.replace("curaloop-m2c-return", "curaloop-d1-return")
    source = source.replace("curaloop-m2c-exact", "curaloop-d1-exact")
    source = source.replace("2026-11-12T08:17:29+00:00", release["deadline_utc"])
    source = source.replace("2026-11-12T08:17:29Z", release["deadline_utc"])
    source = source.replace("curaloop.m2_costed.", "curaloop.d1.")
    target = ROOT / "tools/d1_return_v1.py"
    compile(source, str(target), "exec")
    with target.open("x", encoding="utf-8", newline="\n") as file:
        file.write(source)
    new(TASK / "return-tool-provenance.json", {
        "original": "tools/m2c_return_v2.py", "original_sha256": sha(ROOT / "tools/m2c_return_v2.py"),
        "derived": "tools/d1_return_v1.py", "derived_sha256": sha(target),
        "changes": "task namespace, owned unit prefixes, schema label and D1 absolute deadline only",
        "old_task_unchanged": True,
    })
    cpu = read(TASK / "remote-admission.json")["cpu"]
    for name, host, seconds, wall in (
        ("return-export-v1", "dr-train", 180, 600),
        ("return-fetch-v1", "local", 210, 1900),
        ("return-verify-v1", "local", 180, 600),
        ("remote-exact-cleanup-v1", "dr-train", 60, 120),
    ):
        new(TASK / "jobs" / name / "permit.json", {
            "attempt": name, "host": host, "token": secrets.token_hex(16),
            "cpu": cpu if host == "dr-train" else 0, "guard_cpu_seconds": seconds,
            "reservation_seconds": seconds, "wall_seconds": wall, "memory_bytes": 4294967296,
            "release_utc": release["release_utc"], "deadline_utc": release["deadline_utc"],
            "task_root": "/home/chaw/curaloop-tasks/d1-operation-headroom-20261109-v1",
            "bundle_sha256": sha(TASK / "transport-technical-v1.tar.gz"),
            "reservation_bucket": "utilities_setup_analysis_tests_return_report",
        })
    assert sha(OLD / "ledger.json") == release["old_m2_ledger_sha256"]
    print({"status": "PASS_VERSIONED_RETURN_TOOL_PREPARED", "utility_envelopes_seconds": 630})


if __name__ == "__main__":
    main()
