"""Inspect tar headers only. Never read an assay member or extract a file."""

import argparse
import hashlib
import json
import ntpath
import tarfile
import time
from collections import Counter
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]


def unsafe_name(name):
    parts = PurePosixPath(name).parts
    return (
        not name
        or "\\" in name
        or PurePosixPath(name).is_absolute()
        or ".." in parts
        or bool(ntpath.splitdrive(name)[0])
        or any(":" in p for p in parts)
    )


def inspect(archive, max_members=20000, max_member_bytes=2 * 1024**3, max_total_bytes=16 * 1024**3):
    started, cpu = time.perf_counter(), time.process_time()
    rows, issues, counts = [], [], Counter()
    total = 0
    with tarfile.open(archive, "r:") as handle:
        for member in handle:
            if len(rows) >= max_members:
                issues.append({"name": member.name, "reason": "MEMBER_COUNT_CAP"})
                break
            kind = "file" if member.isfile() else "directory" if member.isdir() else "UNSUPPORTED"
            row = {
                "name": member.name,
                "bytes": member.size,
                "kind": kind,
                "header_offset": member.offset,
                "data_offset": member.offset_data,
            }
            rows.append(row)
            counts[kind] += 1
            if unsafe_name(member.name) or kind == "UNSUPPORTED":
                issues.append({"name": member.name, "reason": "UNSAFE_PATH_OR_ENTRY"})
            if member.size < 0 or member.size > max_member_bytes:
                issues.append({"name": member.name, "reason": "MEMBER_SIZE_CAP"})
            if member.isfile():
                total += member.size
            if total > max_total_bytes:
                issues.append({"name": member.name, "reason": "TOTAL_MEMBER_BYTES_CAP"})
                break
    return {
        "status": "PASS_HEADER_AUDIT" if not issues else "FAIL_HEADER_AUDIT",
        "archive_bytes": archive.stat().st_size,
        "members": rows,
        "member_count": len(rows),
        "counts": dict(counts),
        "stored_member_bytes": total,
        "issues": issues,
        "member_content_read": False,
        "extracted": False,
        "limits": {
            "max_members": max_members,
            "max_member_bytes": max_member_bytes,
            "max_total_bytes": max_total_bytes,
        },
        "gzip_expanded_bytes": "NOT_INSPECTED; compressed members require separate bounded streaming",
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--archive",
        type=Path,
        default=ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/fsmol.tar",
    )
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--max-members", type=int, default=20000)
    args = p.parse_args()
    if args.output.exists():
        raise FileExistsError("Preserve existing audit; use a distinct output.")
    if not 1 <= args.max_members <= 50000:
        raise ValueError("Header-only member limit must be between1and50000.")
    result = inspect(args.archive, max_members=args.max_members)
    result["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result["access_policy_sha256"] = hashlib.sha256(
        (ROOT / "research/configs/goal3_access_policy_v1.json").read_bytes()
    ).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "members"}, indent=2))
    print("FIRST_HEADERS", json.dumps(result["members"][:12]))
    if result["issues"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
