"""Fetch reviewed protein-family annotations only, never assay activities."""

import argparse
import csv
import hashlib
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "research/raw_data/external-benchmarks/fs-mol-0.1"
FIELDS = "accession,reviewed,organism_id,protein_name,protein_families,cc_similarity,xref_interpro"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("canary", "bulk", "exposure"), required=True)
    args = parser.parse_args()
    folder = RAW / ("uniprot-family-" + args.phase + "-v1")
    if folder.exists():
        raise FileExistsError("Preserve this annotation attempt; use a new version.")
    folder.mkdir()
    started, cpu = time.perf_counter(), time.process_time()
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    if args.phase == "exposure":
        ids = ["Q02410"]
    elif args.phase == "canary":
        ids = ["O00763", "P00519", "P00734", "P00797", "P07550"]
    else:
        assays = json.loads((RAW / "chembl37-mapping-v1/assays.json").read_text())
        targets = {
            t["target_chembl_id"]: t
            for t in json.loads((RAW / "chembl37-mapping-v1/targets.json").read_text())
        }
        selected = {
            a["target_chembl_id"]
            for a in assays
            if a.get("confidence_score") == 9
            and a.get("relationship_type") == "D"
            and targets[a["target_chembl_id"]]["target_type"] == "SINGLE PROTEIN"
        }
        ids = sorted(
            {
                c["accession"]
                for tid in selected
                for c in targets[tid]["components"]
                if c["component_type"] == "PROTEIN"
                and c.get("accession")
                and "-" not in c["accession"]
            }
        )
    records, rows, total, release = [], [], 0, None
    try:
        for start in range(0, len(ids), 40):
            batch = ids[start : start + 40]
            query = "(" + " OR ".join("accession:" + a for a in batch) + ") AND reviewed:true"
            url = "https://rest.uniprot.org/uniprotkb/search?" + urllib.parse.urlencode(
                {"query": query, "format": "tsv", "fields": FIELDS, "size": 500}
            )
            before = time.perf_counter()
            request = urllib.request.Request(
                url, headers={"User-Agent": "CuraLoop-RL-PlanA-family-metadata/1"}
            )
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    headers = dict(response.headers)
                    data = response.read(2_000_001)
            except urllib.error.HTTPError as error:
                status, headers, data = error.code, dict(error.headers), error.read(64000)
            total += len(data)
            record = {
                "url": url,
                "status": status,
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "headers": {
                    k: v
                    for k, v in headers.items()
                    if k.lower()
                    in ("x-uniprot-release", "x-uniprot-release-date", "x-total-results", "link")
                },
                "wall_seconds": time.perf_counter() - before,
            }
            records.append(record)
            (folder / f"response-{start // 40:04d}.tsv").write_bytes(data)
            if status != 200 or len(data) > 2_000_000 or total > 20_000_000:
                raise RuntimeError("Source status/payload cap; no retry/bypass.")
            new_release = next(
                (v for k, v in headers.items() if k.lower() == "x-uniprot-release"), None
            )
            if not new_release or release not in (None, new_release):
                raise ValueError("Missing/drifting UniProt annotation release.")
            release = new_release
            reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")), delimiter="\t")
            if (
                not reader.fieldnames
                or "Protein families" not in reader.fieldnames
                or "Entry" not in reader.fieldnames
            ):
                raise ValueError("Family export schema differs.")
            received = list(reader)
            if len(received) > len(batch) or not {r["Entry"] for r in received} <= set(batch):
                raise ValueError("UniProt query returned unexpected accessions/page.")
            rows.extend(received)
            print(
                json.dumps(
                    {
                        "stage": args.phase,
                        "queried": min(start + 40, len(ids)),
                        "requested": len(ids),
                        "reviewed_rows": len(rows),
                        "bytes": total,
                        "release": release,
                        "columns": reader.fieldnames if args.phase == "canary" else None,
                    }
                ),
                flush=True,
            )
            time.sleep(0.5)
        (folder / "families.json").write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
        if args.phase == "canary":
            print(json.dumps(rows, indent=2))
    finally:
        (folder / "requests.json").write_text(
            json.dumps(
                {
                    "requests": records,
                    "total_bytes": total,
                    "requested_accessions": len(ids),
                    "reviewed_records": len(rows),
                    "release": release,
                    "wall_seconds": time.perf_counter() - started,
                    "cpu_seconds": time.process_time() - cpu,
                    "source_sha256_at_start": source_sha,
                    "assay_activity_or_outcomes_requested": False,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
