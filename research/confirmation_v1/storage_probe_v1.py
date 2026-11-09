"""Opaque streaming compression-size measurement; no label parsing or archive."""

import json
import os
import sys
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code-v2"))
from research.m2_costed_v2.guard import CostedGuard, new  # noqa: E402


def main():
    permit = json.loads(Path(sys.argv[1]).read_text())
    root = Path(permit["task_root"])
    assert root == Path.home() / "curaloop-tasks/lr-cf1-20261109-v1" and root.resolve() == root
    job = root / "jobs" / permit["attempt"]
    guard = CostedGuard(job / "resource.json", permit)
    try:
        new(job / "kernel-proof.json", guard.kernel_proof())
        total, models, file_count = [0, 0], [0, 0], 0
        for parent, dirs, files in os.walk(root, followlinks=False):
            for name in dirs + files:
                assert not (Path(parent) / name).is_symlink()
            for name in files:
                path = Path(parent) / name
                compression = zlib.compressobj(1, zlib.DEFLATED, 31)
                raw, compressed = 0, 0
                with path.open("rb") as stream:
                    for block in iter(lambda: stream.read(1048576), b""):
                        raw += len(block)
                        compressed += len(compression.compress(block))
                compressed += len(compression.flush())
                total[0] += raw
                total[1] += compressed
                if path.relative_to(root).parts[0] == "models":
                    models[0] += raw
                    models[1] += compressed
                file_count += 1
        new(job / "result.json", {"status": "PASS_OPAQUE_COMPRESSION_SIZE_CALIBRATION",
            "regular_file_bytes": total[0], "independent_gzip_stream_bytes": total[1],
            "first_seed_model_bytes": models[0], "first_seed_model_gzip_bytes": models[1],
            "file_count": file_count, "compression_level": 1, "archive_created": False,
            "confirmation_values_analyzed": False, "final16_access": False})
        guard.finish("PASS")
    except BaseException as error:
        new(job / "failure.json", {"type": type(error).__name__, "message": str(error)[:200]})
        guard.finish("FAIL")
        raise


if __name__ == "__main__":
    main()
