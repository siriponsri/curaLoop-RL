"""Verify the requested official archive bytes without opening assay members."""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/fsmol.tar"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Preserve the existing receipt; use a new output.")
    report = {
        "status": "BLOCKED",
        "file": str(args.file),
        "expected_bytes": 4871086080,
        "expected_md5": "0ad8f73db6bb8415b023538d514138dc",
        "archive_members_opened": False,
        "labels_inspected": False,
    }
    if not args.file.is_file():
        report["reason"] = "OWNER_DOWNLOAD_NOT_PRESENT"
    elif args.file.stat().st_size != report["expected_bytes"]:
        report.update(status="FAIL", reason="SIZE_MISMATCH", actual_bytes=args.file.stat().st_size)
    else:
        md5, sha = hashlib.md5(usedforsecurity=False), hashlib.sha256()
        with args.file.open("rb") as handle:
            for block in iter(lambda: handle.read(4 * 1024 * 1024), b""):
                md5.update(block)
                sha.update(block)
        report.update(actual_md5=md5.hexdigest(), sha256=sha.hexdigest())
        report["status"] = "PASS" if md5.hexdigest() == report["expected_md5"] else "FAIL"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
