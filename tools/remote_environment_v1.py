"""Read-only environment capability probe, excluding secrets and other projects."""

import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import sys

packages = {}
for name in ("numpy", "scipy", "scikit-learn", "threadpoolctl", "joblib", "psutil"):
    try:
        packages[name] = importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        packages[name] = None
print(
    json.dumps(
        {
            "host": platform.node(),
            "python": sys.version,
            "executable": sys.executable,
            "packages": packages,
            "venv_available": importlib.util.find_spec("venv") is not None,
            "allowed_cpus": sorted(os.sched_getaffinity(0)),
            "nice": os.getpriority(os.PRIO_PROCESS, 0),
            "free_disk_bytes": shutil.disk_usage("/home/chaw/curaloop-rl").free,
        },
        indent=2,
    )
)
