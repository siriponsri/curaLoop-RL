"""Acquire an authenticated CPU-only subset of the published Python3.8 environment."""
# ruff: noqa: E402

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.confirmation_v1.common import PUBLIC, TASK, finish, new, read, sha, start
from tools.cf1_source_inventory_v1 import fetch

PACKAGES = {"numpy": "1.22.3", "scipy": "1.8.1", "scikit-learn": "1.0.2", "pandas": "1.4.4",
            "lightgbm": "3.1.1", "rdkit": "2022.9.4", "joblib": "1.2.0", "threadpoolctl": "3.1.0",
            "python-dateutil": "2.8.2", "pytz": "2022.7.1", "six": "1.16.0", "Pillow": "9.3.0"}


def main():
    release = read(TASK / "source/runtime-release-20230116.json")
    name = "cpython-3.8.16+20230116-x86_64-unknown-linux-gnu-install_only.tar.gz"
    assets = {a["name"]: a for a in release["assets"]}
    checksum = fetch(assets[name + ".sha256"]["browser_download_url"], "runtime/python38.sha256", 1024).decode().split()[0]
    assert len(checksum) == 64
    body = fetch(assets[name]["browser_download_url"], "runtime/python38.tar.gz", assets[name]["size"])
    assert len(body) == assets[name]["size"] and hashlib.sha256(body).hexdigest() == checksum
    wheels = TASK / "dependency-wheels-v1"
    wheels.mkdir()
    command = ["rtk", "proxy", sys.executable, "-m", "pip", "--isolated", "download", "--no-cache-dir",
               "--disable-pip-version-check", "--only-binary=:all:", "--no-deps", "--python-version", "38",
               "--abi", "cp38", "--platform", "manylinux2014_x86_64", "--implementation", "cp", "--dest", str(wheels)]
    command += [f"{package}=={version}" for package, version in PACKAGES.items()]
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    new(TASK / "dependency-download-response-v1.json", {"exit_code": result.returncode, "stdout": result.stdout, "stderr": result.stderr})
    assert result.returncode == 0, "PRESERVE_PARTIAL_WHEEL_DOWNLOAD_AND_INSPECT"
    files = []
    for package, version in PACKAGES.items():
        metadata = json.loads(fetch(f"https://pypi.org/pypi/{package}/{version}/json", "dependency-metadata/" + package + ".json"))
        candidates = {r["filename"]: r for r in metadata["urls"]}
        found = [p for p in wheels.iterdir() if p.name in candidates]
        assert len(found) == 1
        path = found[0]
        expected = candidates[path.name]["digests"]["sha256"]
        assert sha(path) == expected and path.stat().st_size == candidates[path.name]["size"]
        files.append({"package": package, "version": version, "path": path.relative_to(TASK).as_posix(),
                      "filename": path.name, "sha256": expected, "bytes": path.stat().st_size})
    assert len(files) == len(PACKAGES) == len(list(wheels.iterdir()))
    summary = {"status": "PASS_AUTHENTICATED_CPU_ONLY_RUNTIME_INPUTS", "python": {"version": "3.8.16",
        "path": "source/runtime/python38.tar.gz", "sha256": checksum, "bytes": len(body)}, "wheels": files,
        "gpu_packages_requested": False, "environment_installed": False, "model_fits": 0,
        "source_python_patch_matches": True, "whole_author_environment_reproduced": False}
    new(TASK / "dependency-inputs-v1.json", summary)
    new(PUBLIC / "dependency-inputs-v1.json", summary)
    print({"status": summary["status"], "python_bytes": len(body), "wheel_count": len(files), "wheel_bytes": sum(r["bytes"] for r in files)})


if __name__ == "__main__":
    guard = start("cpu-runtime-dependency-acquisition", 300, 1200, orchestration=True)
    try:
        main()
        finish("cpu-runtime-dependency-acquisition", guard, "PASS_DEPENDENCY_INPUTS_NOT_INSTALLED")
    except BaseException:
        finish("cpu-runtime-dependency-acquisition", guard, "FAIL")
        raise
