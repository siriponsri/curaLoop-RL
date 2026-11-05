"""One bounded attempt for remaining shared entries; preserve unavailable IDs."""

import hashlib
import http.client
import json
import time
import urllib.error
import urllib.request

from research.benchmark_v3.families import RAW


def cached_types():
    entries, failed = {}, set()
    for phase in ("canary", "bulk", "resume", "finish"):
        folder = RAW / ("interpro-types-" + phase + "-v1")
        path = folder / "requests.json"
        if not path.exists():
            continue
        for record in json.loads(path.read_text())["requests"]:
            aid = record["accession"]
            if record["status"] != 200 or record["error"]:
                failed.add(aid)
                continue
            data = (folder / f"{aid}-attempt{record['attempt']}.json").read_bytes()
            headers = {k.lower(): v for k, v in record["version_headers"].items()}
            if (
                hashlib.sha256(data).hexdigest() != record["sha256"]
                or headers.get("interpro-version") != "110.0"
                or headers.get("interpro-version-minor") != "0"
            ):
                raise ValueError("Unverified InterPro cached response.")
            m = json.loads(data)["metadata"]
            if m["accession"] != aid:
                raise ValueError("InterPro identity mismatch.")
            entry = {
                "accession": aid,
                "type": m["type"],
                "name": m["name"],
                "hierarchy": m.get("hierarchy"),
                "source_sha256": record["sha256"],
                "release": "110.0",
            }
            if aid in entries and entries[aid]["type"] != entry["type"]:
                raise ValueError("Cached types disagree.")
            entries[aid] = entry
    return entries, failed - set(entries)


def main():
    folder = RAW / "interpro-types-finish-v1"
    entries, blocked = cached_types()
    folder.mkdir(exist_ok=False)
    required = set(json.loads((RAW / "shared-interpro-ids-v1.json").read_text()))
    pending = sorted(required - set(entries) - blocked)
    started, cpu = time.perf_counter(), time.process_time()
    source_sha = hashlib.sha256(__import__("pathlib").Path(__file__).read_bytes()).hexdigest()
    records, total = [], 0
    try:
        for aid in pending:
            status, data, error, headers = None, b"", None, {}
            url = f"https://www.ebi.ac.uk/interpro/api/entry/interpro/{aid}/"
            before = time.perf_counter()
            try:
                with urllib.request.urlopen(
                    urllib.request.Request(
                        url, headers={"User-Agent": "CuraLoop-RL-PlanA-family-audit/1"}
                    ),
                    timeout=25,
                ) as response:
                    status, headers = response.status, dict(response.headers)
                    data = response.read(200001)
            except urllib.error.HTTPError as exc:
                status, data, error = exc.code, exc.read(64000), type(exc).__name__
            except (
                urllib.error.URLError,
                TimeoutError,
                http.client.HTTPException,
                ConnectionError,
            ) as exc:
                error = type(exc).__name__
            total += len(data)
            record = {
                "accession": aid,
                "url": url,
                "attempt": 1,
                "status": status,
                "error": error,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "version_headers": {k: v for k, v in headers.items() if "version" in k.lower()},
                "wall_seconds": time.perf_counter() - before,
            }
            records.append(record)
            (folder / f"{aid}-attempt1.json").write_bytes(data)
            if status in (401, 403) or total > 5_000_000 or len(data) > 200000:
                raise RuntimeError("Origin access/payload guard; no bypass.")
            print(
                json.dumps(
                    {
                        "accession": aid,
                        "status": status,
                        "error": error,
                        "remaining": len(pending) - len(records),
                    }
                ),
                flush=True,
            )
            time.sleep(0.5)
    finally:
        (folder / "requests.json").write_text(
            json.dumps(
                {
                    "requests": records,
                    "bytes": total,
                    "requested": len(pending),
                    "blocked_previous_unavailable": sorted(blocked),
                    "source_sha256_at_start": source_sha,
                    "cpu_seconds": time.process_time() - cpu,
                    "wall_seconds": time.perf_counter() - started,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    entries, failed = cached_types()
    print(
        json.dumps(
            {
                "cached_typed_entries": len(entries),
                "unavailable": sorted(required - set(entries)),
                "previous_failed_not_retried": sorted(blocked),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
