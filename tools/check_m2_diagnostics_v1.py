"""Run local constructed checks; never load scientific records or contact a host."""

import ctypes
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/m2-diagnostics-20261109-v1"
SOURCE = [
    "research/m2_diagnostics_v1/__init__.py",
    "research/m2_diagnostics_v1/operations.py",
    "tests/research/test_m2_diagnostics_v1.py",
    "tools/check_m2_diagnostics_v1.py",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pin_one_cpu():
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetCurrentProcess.restype = ctypes.c_void_p
        kernel.GetProcessAffinityMask.argtypes = [
            ctypes.c_void_p, ctypes.POINTER(ctypes.c_size_t), ctypes.POINTER(ctypes.c_size_t),
        ]
        kernel.SetProcessAffinityMask.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        process = kernel.GetCurrentProcess()
        allowed, system = ctypes.c_size_t(), ctypes.c_size_t()
        if not kernel.GetProcessAffinityMask(process, ctypes.byref(allowed), ctypes.byref(system)):
            raise RuntimeError("CPU_AFFINITY_READ_FAILED")
        chosen = allowed.value & -allowed.value
        if not chosen or not kernel.SetProcessAffinityMask(process, chosen):
            raise RuntimeError("SINGLE_CPU_AFFINITY_FAILED")
        if not kernel.GetProcessAffinityMask(process, ctypes.byref(allowed), ctypes.byref(system)):
            raise RuntimeError("CPU_AFFINITY_READBACK_FAILED")
        if allowed.value != chosen:
            raise RuntimeError("CPU_AFFINITY_NOT_APPLIED")
        return {"mask": chosen, "cpu_count": 1}
    chosen = min(os.sched_getaffinity(0))
    os.sched_setaffinity(0, {chosen})
    if os.sched_getaffinity(0) != {chosen}:
        raise RuntimeError("CPU_AFFINITY_NOT_APPLIED")
    return {"cpu": chosen, "cpu_count": 1}


def preserved(pins):
    differences = [name for name, expected in pins.items() if sha(ROOT / name) != expected]
    if differences:
        raise RuntimeError("HISTORICAL_BYTES_CHANGED: " + repr(differences))


def main():
    os.chdir(ROOT)
    receipt = EVIDENCE / "verification-v1.json"
    if receipt.exists():
        raise RuntimeError("IMMUTABLE_RECEIPT_EXISTS_USE_NEW_EVIDENCE_VERSION")
    started = datetime.now(timezone.utc).isoformat()
    wall_start, cpu_start = time.monotonic(), time.process_time()
    affinity = pin_one_cpu()
    for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
        os.environ[key] = "1"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    pins = json.loads((EVIDENCE / "preservation-pins-v1.json").read_text())["pins"]
    preserved(pins)
    import pytest
    from threadpoolctl import threadpool_info, threadpool_limits

    result = pytest.main([
        "tests/research/test_m2_diagnostics_v1.py", "-q", "-p", "no:cacheprovider",
        "--junitxml=" + str(EVIDENCE / "constructed-tests-v1.xml"),
    ])
    # Check the environment limits really reached the libraries imported by tests.
    pools = threadpool_info()
    if not pools or any(pool["num_threads"] != 1 for pool in pools):
        raise RuntimeError("NUMERICAL_THREAD_LIMIT_NOT_VERIFIED")
    with threadpool_limits(limits=1):
        assert all(pool["num_threads"] == 1 for pool in threadpool_info())
    lint = subprocess.run(
        [sys.executable, "-B", "-m", "ruff", "check", *SOURCE],
        capture_output=True, text=True, check=False,
    )
    preserved(pins)
    docs = [
        ROOT / "docs/03_research/M2_D0_OPERATION_AUDIT_20261109.md",
        ROOT / "docs/06_execution/M2_DIAGNOSTIC_PLAN_20261109.md",
        EVIDENCE / "README.md",
    ]
    checked = 0
    for path in docs:
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            destination = (path.parent / unquote(target.split("#")[0])).resolve()
            if destination != receipt and not destination.is_file():
                raise RuntimeError("BROKEN_LOCAL_LINK: " + str(destination))
            checked += 1
    record = {
        "schema": "curaloop.m2_diagnostics.verification.v1",
        "status": "PASS" if result == 0 and lint.returncode == 0 else "FAIL",
        "started_utc": started, "completed_utc": datetime.now(timezone.utc).isoformat(),
        "base_commit": "bf59b103a789fa2832762abcdc6d5f7dc723466e",
        "python": sys.version, "platform": platform.platform(),
        "cpu_affinity": affinity,
        "threadpools": [{k: pool[k] for k in ("internal_api", "num_threads", "version")}
                        for pool in pools],
        "pytest_exit_code": int(result), "ruff_exit_code": lint.returncode,
        "ruff_output": lint.stdout + lint.stderr,
        "junit_xml": "constructed-tests-v1.xml",
        "local_links_checked": checked, "historical_files_hash_checked": len(pins),
        "historical_preservation": "PASS",
        "source_sha256": {name: sha(ROOT / name) for name in SOURCE},
        "wall_seconds": time.monotonic() - wall_start,
        "current_process_cpu_seconds": time.process_time() - cpu_start,
        "cpu_measurement_scope": "verification parent including in-process pytest; excludes ruff child",
        "scientific_records_or_outcomes_read": False,
        "new_scientific_grant_started": False, "old_ledger_reopened": False,
        "final_payloads_opened": False, "ssh_or_remote_job": False,
        "molecular_D1": "NOT_RUN", "linux_real_cpu_interrupt": "NOT_RUN",
        "independent_review": "NOT_RUN", "publication_or_push": "NOT_RUN",
    }
    with receipt.open("x", encoding="utf-8") as file:
        json.dump(record, file, indent=2)
        file.write("\n")
    print(json.dumps({"status": record["status"], "receipt": str(receipt),
                      "pytest_exit_code": int(result), "ruff_exit_code": lint.returncode}))
    return 0 if record["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
