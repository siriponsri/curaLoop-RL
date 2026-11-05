"""Trusted schema canary on an already quarantined development-only source task."""

import gzip
import hashlib
import io
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"


def main():
    out = ROOT / "docs/evidence/plan-a-20261105-v1/schema-canary-v1.json"
    if out.exists():
        raise FileExistsError(out)
    policy = json.loads((ROOT / "research/configs/goal3_access_policy_v1.json").read_text())
    assert policy["known_exposure"][0]["task_id"] == "CHEMBL1614128"
    assert policy["known_exposure"][0]["required_role"] == "DEVELOPMENT_ONLY_NOT_FINAL"
    name = "fs-mol/train/CHEMBL1614128.jsonl.gz"
    headers = json.loads((RAW / "header-audit-v2.json").read_text())
    row = next(r for r in headers["members"] if r["name"] == name)
    if row["kind"] != "file" or row["bytes"] > 64 * 1024**2:
        raise ValueError("Schema source entry exceeds its safe bound.")
    started, cpu = time.perf_counter(), time.process_time()
    with (RAW / "fsmol.tar").open("rb") as handle:
        handle.seek(row["data_offset"])
        data = handle.read(row["bytes"])
    if len(data) != row["bytes"]:
        raise ValueError("Truncated source member.")
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as handle:
        first = handle.readline(4 * 1024**2 + 1)
    if len(first) > 4 * 1024**2:
        raise ValueError("Schema row exceeds line bound.")
    record = json.loads(first)
    schema = {key: type(value).__name__ for key, value in record.items()}
    nested_keys = {key: sorted(value) for key, value in record.items() if isinstance(value, dict)}
    result = {
        "status": "PASS_SCHEMA_ONLY_DEVELOPMENT_CANARY",
        "source_task": "CHEMBL1614128",
        "required_role": "DEVELOPMENT_ONLY_NOT_FINAL",
        "member": name,
        "compressed_bytes": len(data),
        "member_sha256": hashlib.sha256(data).hexdigest(),
        "top_level_schema": schema,
        "nested_keys_only": nested_keys,
        "rows_trusted_parsed": 1,
        "outcome_values_emitted": False,
        "final_task_access": False,
        "agent_visible_compound_outcomes": False,
        "wall_seconds": time.perf_counter() - started,
        "cpu_seconds": time.process_time() - cpu,
    }
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
