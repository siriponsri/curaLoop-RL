"""Bounded outcome-free ChEMBL37 metadata mapping; no activity endpoint exists here."""

import hashlib
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API = "https://www.ebi.ac.uk/chembl/api/data/"
CACHE = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1/chembl37-mapping-v1"
ALLOWED = {"status", "assay", "target", "target_component", "protein_classification"}


class MetadataCache:
    def __init__(self):
        CACHE.mkdir(exist_ok=True)
        self.ledger = CACHE / "requests.jsonl"
        self.records = (
            [json.loads(x) for x in self.ledger.read_text().splitlines()]
            if self.ledger.exists()
            else []
        )
        self.bytes = sum(x["bytes"] for x in self.records)
        self.next_call = 0.0

    def get(self, endpoint, fields=None, collection=None, filters=None, force_tag=None):
        if endpoint not in ALLOWED:
            raise ValueError("Only non-activity metadata endpoints are allowed.")
        params = dict(filters or {})
        if fields:
            params["only"] = ",".join(fields)
        if collection:
            params["limit"] = 1000
        url = API + endpoint + ".json"
        if params:
            url += "?" + urllib.parse.urlencode(sorted(params.items()), safe=",")
        key = hashlib.sha256((url + (force_tag or "")).encode()).hexdigest()
        path = CACHE / (key + ".json")
        previous = [r for r in self.records if r["cache_key"] == key and r["status"] == 200]
        if previous:
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != previous[-1]["sha256"]:
                raise ValueError("Cached source bytes changed.")
            body = json.loads(raw)
        else:
            if path.exists():
                raise ValueError("Unreceipted response exists; inspect rather than overwrite.")
            for attempt in range(2):
                if self.bytes >= 118_000_000 or len(self.records) >= 1000:
                    raise RuntimeError("Metadata byte/request cap reached.")
                if time.monotonic() < self.next_call:
                    time.sleep(min(1, self.next_call - time.monotonic()))
                started = time.perf_counter()
                req = urllib.request.Request(
                    url, headers={"User-Agent": "CuraLoop-RL-PlanA-outcome-free-metadata/1"}
                )
                status, raw, error = None, b"", None
                try:
                    with urllib.request.urlopen(req, timeout=30) as response:
                        status = response.status
                        raw = response.read(2_000_001)
                except urllib.error.HTTPError as exc:
                    status, raw, error = exc.code, exc.read(64000), type(exc).__name__
                except (TimeoutError, urllib.error.URLError) as exc:
                    error = type(exc).__name__
                self.bytes += len(raw)
                record = {
                    "url": url,
                    "cache_key": key,
                    "attempt": attempt + 1,
                    "status": status,
                    "bytes": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "error": error,
                    "wall_seconds": time.perf_counter() - started,
                }
                with self.ledger.open("a", encoding="utf-8") as out:
                    out.write(json.dumps(record) + "\n")
                self.records.append(record)
                self.next_call = time.monotonic() + 0.5
                if status in (401, 403):
                    raise RuntimeError("Access denied: stop this origin; no bypass.")
                if len(raw) > 2_000_000 or self.bytes > 118_000_000:
                    raise RuntimeError("Response/cumulative payload cap reached.")
                if status == 200:
                    path.write_bytes(raw)
                    body = json.loads(raw)
                    break
                if attempt == 1 or (status is not None and status < 500 and status != 429):
                    raise RuntimeError(f"Metadata request failed: status={status},error={error}")
                time.sleep(2)
        if collection:
            if collection not in body or not isinstance(body[collection], list):
                raise ValueError("Unexpected metadata collection.")
            if len(body[collection]) > 1000 or body.get("page_meta", {}).get("next"):
                raise ValueError("Batch did not fit declared bounded page.")
            return body[collection]
        return body


def chunks(values, size):
    for start in range(0, len(values), size):
        yield values[start : start + size]


def write_once(name, value):
    path = CACHE / name
    encoded = json.dumps(value, sort_keys=True, indent=2).encode()
    if path.exists():
        if path.read_bytes() != encoded:
            raise ValueError("Existing normalized metadata differs: " + name)
    else:
        path.write_bytes(encoded)


def main():
    started, cpu = time.perf_counter(), time.process_time()
    cache = MetadataCache()
    status = cache.get("status")
    if status.get("chembl_db_version") != "ChEMBL_37":
        raise ValueError("Current metadata release differs from declared ChEMBL37.")
    write_once("status-start.json", status)
    classes = cache.get("protein_classification", collection="protein_classifications")
    write_once("protein-classifications.json", classes)
    print(
        json.dumps(
            {
                "stage": "classification",
                "release": status["chembl_db_version"],
                "records": len(classes),
            }
        ),
        flush=True,
    )
    manifest = json.loads((CACHE.parent / "source-metadata-v1/fsmol-0.1.json").read_text())
    assay_ids = sorted({a for ids in manifest.values() for a in ids})
    assays = []
    for batch in chunks(assay_ids, 50):
        rows = cache.get(
            "assay",
            ("assay_chembl_id", "target_chembl_id", "confidence_score", "relationship_type"),
            "assays",
            {"assay_chembl_id__in": ",".join(batch)},
        )
        if not {r["assay_chembl_id"] for r in rows} <= set(batch):
            raise ValueError("Assay API ignored identity filter.")
        assays.extend(
            {
                k: r.get(k)
                for k in (
                    "assay_chembl_id",
                    "target_chembl_id",
                    "confidence_score",
                    "relationship_type",
                )
            }
            for r in rows
        )
        print(
            json.dumps(
                {
                    "stage": "assay",
                    "received": len(assays),
                    "requested_total": len(assay_ids),
                    "bytes": cache.bytes,
                }
            ),
            flush=True,
        )
    write_once("assays.json", assays)
    targets = []
    target_ids = sorted({r["target_chembl_id"] for r in assays if r.get("target_chembl_id")})
    for batch in chunks(target_ids, 25):
        rows = cache.get(
            "target",
            ("target_chembl_id", "target_type", "tax_id", "organism", "target_components"),
            "targets",
            {"target_chembl_id__in": ",".join(batch)},
        )
        if not {r["target_chembl_id"] for r in rows} <= set(batch):
            raise ValueError("Target API ignored identity filter.")
        for row in rows:
            components = [
                {
                    k: c.get(k)
                    for k in ("component_id", "accession", "component_type", "relationship")
                }
                for c in row.get("target_components", [])
            ]
            targets.append(
                {
                    **{
                        k: row.get(k)
                        for k in ("target_chembl_id", "target_type", "tax_id", "organism")
                    },
                    "components": components,
                }
            )
        print(
            json.dumps(
                {
                    "stage": "target",
                    "received": len(targets),
                    "requested_total": len(target_ids),
                    "bytes": cache.bytes,
                }
            ),
            flush=True,
        )
    write_once("targets.json", targets)
    component_ids = sorted(
        {
            c["component_id"]
            for t in targets
            for c in t["components"]
            if c.get("component_id") is not None
        }
    )
    components = []
    for batch in chunks(component_ids, 50):
        rows = cache.get(
            "target_component",
            ("component_id", "accession", "component_type", "protein_classifications"),
            "target_components",
            {"component_id__in": ",".join(map(str, batch))},
        )
        if not {r["component_id"] for r in rows} <= set(batch):
            raise ValueError("Component API ignored identity filter.")
        components.extend(
            {
                k: r.get(k)
                for k in ("component_id", "accession", "component_type", "protein_classifications")
            }
            for r in rows
        )
        print(
            json.dumps(
                {
                    "stage": "component",
                    "received": len(components),
                    "requested_total": len(component_ids),
                    "bytes": cache.bytes,
                }
            ),
            flush=True,
        )
    write_once("components.json", components)
    final_status = cache.get("status", force_tag="finish")
    if final_status.get("chembl_db_version") != status["chembl_db_version"]:
        raise ValueError("ChEMBL release changed during acquisition.")
    write_once(
        "summary.json",
        {
            "status": "PASS_OUTCOME_FREE_METADATA_ACQUISITION",
            "release": status["chembl_db_version"],
            "assays": len(assays),
            "requested_assays": len(assay_ids),
            "targets": len(targets),
            "components": len(components),
            "classification_records": len(classes),
            "http_attempts": len(cache.records),
            "payload_bytes": cache.bytes,
            "cpu_seconds": time.process_time() - cpu,
            "wall_seconds": time.perf_counter() - started,
            "activities_requested": False,
            "assay_member_contents_read": False,
        },
    )


if __name__ == "__main__":
    main()
