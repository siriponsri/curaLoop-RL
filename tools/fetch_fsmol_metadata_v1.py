"""Fetch only pinned outcome-free metadata; reject unexpected outcome columns."""

import csv
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "92aa95daba3f43863227e65be85a07b4a2ee754f"
BASE = f"https://raw.githubusercontent.com/microsoft/FS-Mol/{PIN}/"
FILES = {
    "train_proteins.csv": (
        "datasets/targets/train_proteins.csv",
        "46e77bfe73fedac4631783df38734fefbce388d9cf24aa292eaa5b513627f924",
    ),
    "valid_proteins.csv": ("datasets/targets/valid_proteins.csv", None),
    "test_proteins.csv": (
        "datasets/targets/test_proteins.csv",
        "abf45d6f45624967885cfed522d72b0bf96ff06dffeae4eea7bf5de02c36733b",
    ),
    "fsmol-0.1.json": ("datasets/fsmol-0.1.json", None),
    "LICENSE": ("LICENSE", None),
}
EXPECTED_COLUMNS = (
    "chembl_id,target_id,confidence,component_synonym,type_synonym,protein_class_desc,pref_name,"
    "EC_super_class,EC_super_class_name,protein_family,protein_super_family,EC_name,"
    "reliable_target_EC,reliable_target_protein_desc,reliable_target_EC_super,reliable_target_protein_super"
).split(",")


def main():
    folder = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/source-metadata-v1"
    if folder.exists():
        raise FileExistsError("Preserve the existing source cache.")
    folder.mkdir()
    started, cpu = time.perf_counter(), time.process_time()
    receipts = []
    total = 0
    try:
        for name, (relative, expected) in FILES.items():
            url = BASE + relative
            before = time.perf_counter()
            request = urllib.request.Request(
                url, headers={"User-Agent": "CuraLoop-RL-PlanA-source-audit/1"}
            )
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(2_000_001)
                status = response.status
            total += len(data)
            if len(data) > 2_000_000 or total > 10_000_000:
                raise ValueError("Bounded metadata payload cap reached.")
            actual = hashlib.sha256(data).hexdigest()
            if expected and actual != expected:
                raise ValueError("Pinned metadata digest mismatch: " + name)
            row = {
                "name": name,
                "url": url,
                "http_status": status,
                "bytes": len(data),
                "sha256": actual,
                "wall_seconds": time.perf_counter() - before,
            }
            if name.endswith(".csv"):
                reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
                if reader.fieldnames != EXPECTED_COLUMNS:
                    raise ValueError("Metadata header differs; do not inspect rows: " + name)
                row["rows"] = sum(1 for _ in reader)
                row["outcome_columns"] = False
            (folder / name).write_bytes(data)
            receipts.append(row)
            print(json.dumps(row), flush=True)
    except Exception as error:
        receipts.append(
            {
                "status": "FAILED_STOP_NO_RETRY",
                "error_type": type(error).__name__,
                "message": str(error),
                "bytes_received_including_failures": total,
            }
        )
        raise
    finally:
        (folder / "requests.json").write_text(
            json.dumps(
                {
                    "requests": receipts,
                    "bytes": total,
                    "attempts": len(receipts),
                    "source_commit": PIN,
                    "wall_seconds": time.perf_counter() - started,
                    "cpu_seconds": time.process_time() - cpu,
                    "assay_rows_downloaded": False,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
