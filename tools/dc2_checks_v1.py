"""No-fix controller preflight, no model/data/tool execution."""

import importlib.util
import subprocess
import sys

from dc2_admin_v1 import PUBLIC, ROOT, TASK, preserve, read, write


def main():
    release = read(TASK / "release.json")
    preserve(release)
    paths = [p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "tools").glob("dc2_*.py"))]
    result = subprocess.run([sys.executable, "-m", "ruff", "check", *paths], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    packages = {p: importlib.util.find_spec(p) is not None for p in ("pyarrow", "pandas", "requests", "rdkit")}
    write(PUBLIC / "local-controller-preflight-v1.json", {
        "status": "PASS_NO_FIX_CONTROLLER_PREFLIGHT", "python_files": paths,
        "available_packages": packages, "new_package_installed": False,
        "historical_preservation": True, "new_inference": False})
    print({"status": "PASS", "available_packages": packages})


if __name__ == "__main__":
    main()
