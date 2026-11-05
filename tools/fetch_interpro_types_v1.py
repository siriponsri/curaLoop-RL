"""Snapshot typed InterPro ancestry metadata for shared protein entries only."""

import argparse
import hashlib
import http.client
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--phase", choices=("canary", "bulk", "resume"), required=True)
    args = p.parse_args()
    folder = RAW / ("interpro-types-" + args.phase + "-v1")
    if folder.exists():
        raise FileExistsError(folder)
    folder.mkdir()
    ids = (
        ["IPR029058"]
        if args.phase == "canary"
        else json.loads((RAW / "shared-interpro-ids-v1.json").read_text())
    )
    records, entries, total = [], [], 0
    if args.phase == "resume":
        old_folder = RAW / "interpro-types-bulk-v1"
        previous = json.loads((old_folder / "requests.json").read_text())
        for record in previous["requests"]:
            if record["status"] != 200:
                continue
            data = (
                old_folder / f"{record['accession']}-attempt{record['attempt']}.json"
            ).read_bytes()
            if hashlib.sha256(data).hexdigest() != record["sha256"]:
                raise ValueError("Existing typed metadata cache differs.")
            metadata = json.loads(data)["metadata"]
            entries.append(
                {
                    "accession": metadata["accession"],
                    "type": metadata["type"],
                    "name": metadata.get("name"),
                    "hierarchy": metadata.get("hierarchy"),
                    "source_sha256": record["sha256"],
                    "version_headers": record["version_headers"],
                }
            )
        done = {e["accession"] for e in entries}
        ids = [a for a in ids if a not in done]
    started, cpu = time.perf_counter(), time.process_time()
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    try:
        for index, accession in enumerate(ids):
            if not accession.startswith("IPR") or not accession[3:].isdigit():
                raise ValueError("Invalid InterPro identity.")
            url = f"https://www.ebi.ac.uk/interpro/api/entry/interpro/{accession}/"
            for attempt in range(2):
                before = time.perf_counter()
                req = urllib.request.Request(
                    url, headers={"User-Agent": "CuraLoop-RL-PlanA-protein-family-audit/1"}
                )
                status, data, error, headers = None, b"", None, {}
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        status, headers = response.status, dict(response.headers)
                        data = response.read(200001)
                except urllib.error.HTTPError as exc:
                    status, data, error = exc.code, exc.read(64000), type(exc).__name__
                except (
                    TimeoutError,
                    urllib.error.URLError,
                    http.client.HTTPException,
                    ConnectionError,
                ) as exc:
                    error = type(exc).__name__
                total += len(data)
                record = {
                    "url": url,
                    "accession": accession,
                    "attempt": attempt + 1,
                    "status": status,
                    "bytes": len(data),
                    "error": error,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "wall_seconds": time.perf_counter() - before,
                    "version_headers": {
                        k: v
                        for k, v in headers.items()
                        if "version" in k.lower() or "release" in k.lower()
                    },
                }
                records.append(record)
                (folder / f"{accession}-attempt{attempt + 1}.json").write_bytes(data)
                if status in (401, 403) or len(data) > 200000 or total > 20000000:
                    raise RuntimeError("Access/payload guard; stop origin, no bypass.")
                if status == 200:
                    version = {k.lower(): v for k, v in record["version_headers"].items()}
                    if (
                        version.get("interpro-version") != "110.0"
                        or version.get("interpro-version-minor") != "0"
                    ):
                        raise ValueError("Missing/drifting InterPro110.0 annotation version.")
                    body = json.loads(data)
                    metadata = body.get("metadata", {})
                    if metadata.get("accession") != accession or not metadata.get("type"):
                        raise ValueError("Unexpected typed InterPro identity/schema.")
                    entries.append(
                        {
                            "accession": accession,
                            "type": metadata["type"],
                            "name": metadata.get("name"),
                            "hierarchy": metadata.get("hierarchy"),
                            "source_sha256": record["sha256"],
                            "version_headers": record["version_headers"],
                        }
                    )
                    break
                if attempt == 1 or (
                    status is not None and status < 500 and status not in (202, 429)
                ):
                    raise RuntimeError(
                        f"InterPro metadata unavailable status={status},error={error}"
                    )
                time.sleep(2)
            if index % 10 == 0 or index + 1 == len(ids):
                print(
                    json.dumps(
                        {
                            "stage": args.phase,
                            "entries": len(entries),
                            "requested": len(ids),
                            "bytes": total,
                        }
                    ),
                    flush=True,
                )
            time.sleep(0.5)
        (folder / "entries.json").write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        if args.phase == "canary":
            print(json.dumps(entries, indent=2))
    finally:
        (folder / "requests.json").write_text(
            json.dumps(
                {
                    "requests": records,
                    "bytes": total,
                    "entries": len(entries),
                    "requested": len(ids),
                    "source_sha256_at_start": source_sha,
                    "wall_seconds": time.perf_counter() - started,
                    "cpu_seconds": time.process_time() - cpu,
                    "assay_activity_requested": False,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
