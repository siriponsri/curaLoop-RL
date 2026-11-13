"""CSV -> actual RDKit descriptors/filter -> immutable local report bundle."""

import csv
import hashlib
import html
import json
import platform
import time
import zipfile
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from . import chemistry
from .chemistry import FilterSpec, compute
from .evidence import EvidenceLedger, Requirement


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def write_csv(path, fields, rows):
    with Path(path).open("x", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: "; ".join(v) if isinstance(v, list) else v for k, v in row.items()})


def build_bundle(folder, csv_text, spec):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    (folder / "input.csv").write_text(csv_text, encoding="utf-8", newline="")
    write_json(folder / "parameters.json", asdict(spec))
    result = compute(csv_text, spec)
    result["created_utc"] = datetime.now(timezone.utc).isoformat()
    result["tools"] = {
        "python": platform.python_version(),
        "rdkit": result["rdkit_version"],
        "chemistry_source_sha256": sha(Path(chemistry.__file__)),
        "workflow_source_sha256": sha(Path(__file__)),
    }
    fields = [
        "row",
        "compound_id",
        "smiles",
        "canonical_smiles",
        "molecular_weight",
        "logp",
        "tpsa",
        "hbd",
        "hba",
        "selected",
        "filter_reasons",
    ]
    write_csv(folder / "descriptors.csv", fields, result["compounds"])
    write_csv(folder / "selected.csv", fields, [r for r in result["compounds"] if r["selected"]])
    write_csv(
        folder / "rejected.csv", ["row", "compound_id", "smiles", "reason"], result["rejected"]
    )
    write_json(folder / "report.json", result)
    body = "".join(
        "<tr>"
        + "".join(
            "<td>" + html.escape(str(row[k])) + "</td>"
            for k in (
                "compound_id",
                "canonical_smiles",
                "molecular_weight",
                "logp",
                "tpsa",
                "selected",
            )
        )
        + "</tr>"
        for row in result["compounds"]
    )
    markup = (
        "<!doctype html><html lang='en'><meta charset='utf-8'><title>CuraLoop local molecular analysis</title>"
        "<style>body{font:16px system-ui;margin:40px;color:#272229}table{border-collapse:collapse;width:100%}"
        "td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}code{white-space:pre-wrap}</style>"
        "<h1>Local molecular analysis</h1><p>Actual RDKit calculations. Physicochemical filtering only; no assay or efficacy prediction.</p>"
        "<h2>Recorded filter</h2><code>"
        + html.escape(json.dumps(result["parameters"], indent=2))
        + "</code>"
        "<p>Counts: " + html.escape(json.dumps(result["counts"])) + "</p>"
        "<table><thead><tr><th>Compound</th><th>Canonical SMILES</th><th>MW (g/mol)</th><th>LogP</th><th>TPSA (Å²)</th><th>Selected</th></tr></thead><tbody>"
        + body
        + "</tbody></table><p>Rejected rows and reasons are retained in rejected.csv. Source and output hashes are in manifest.json.</p></html>"
    )
    (folder / "report.html").write_text(markup, encoding="utf-8")
    common = ("input.csv", "parameters.json", "report.json")
    validator_code = sha(Path(__file__))
    requirements = [
        Requirement(
            "row-accounting",
            "Every input row is valid or explicitly rejected",
            common + ("descriptors.csv", "rejected.csv"),
            "row-accounting-v1:" + validator_code,
        ),
        Requirement(
            "selection",
            "Selected rows match the recorded descriptor thresholds",
            common + ("descriptors.csv", "selected.csv"),
            "selection-v1:" + validator_code,
        ),
        Requirement(
            "units",
            "Report retains the declared descriptor units",
            common,
            "units-v1:" + validator_code,
        ),
    ]
    ledger = EvidenceLedger(folder, requirements)
    validate_bundle(folder, ledger)
    write_json(folder / "evidence.json", ledger.export())
    files = {
        p.name: {"sha256": sha(p), "bytes": p.stat().st_size}
        for p in sorted(folder.iterdir())
        if p.is_file()
    }
    manifest = {
        "schema": "curaloop.local-agent.bundle.v1",
        "files": files,
        "created_utc": result["created_utc"],
        "toolchain": result["tools"],
        "evidence_ready": ledger.completion()["ready"],
        "scientific_native_success": "NOT_ASSESSED_LOCAL_PRODUCT_WORKFLOW",
        "limitations": result["limitations"],
    }
    write_json(folder / "manifest.json", manifest)
    with zipfile.ZipFile(folder / "bundle.zip", "x", compression=zipfile.ZIP_DEFLATED) as output:
        for name in [*files, "manifest.json"]:
            output.write(folder / name, arcname=name)
    return {
        "manifest_sha256": sha(folder / "manifest.json"),
        "bundle_sha256": sha(folder / "bundle.zip"),
        "counts": result["counts"],
        "evidence": ledger.completion(),
        "result": result,
    }


def validate_bundle(folder, ledger):
    folder = Path(folder)
    report = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    params = json.loads((folder / "parameters.json").read_text(encoding="utf-8"))
    snapshots = {r: ledger.snapshot(r) for r in ledger.requirements}
    with (folder / "descriptors.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with (folder / "rejected.csv").open(encoding="utf-8", newline="") as stream:
        rejected = list(csv.DictReader(stream))
    with (folder / "selected.csv").open(encoding="utf-8", newline="") as stream:
        selected = list(csv.DictReader(stream))
    with (folder / "input.csv").open(encoding="utf-8-sig", newline="") as stream:
        original = list(csv.DictReader(stream))
    counts = report["counts"]
    accounted = len(rows) + len(rejected) == len(original) == counts["input_rows"]
    accounted &= len(rows) == counts["valid"] and len(rejected) == counts["rejected"]
    original_rows = Counter(
        (str(i), (r.get("compound_id") or "").strip(), (r.get("smiles") or "").strip())
        for i, r in enumerate(original, 2)
    )
    exported_rows = Counter((r["row"], r["compound_id"], r["smiles"]) for r in rows + rejected)
    accounted &= original_rows == exported_rows
    wanted = [
        r
        for r in rows
        if float(r["molecular_weight"]) <= params["molecular_weight_max"]
        and float(r["logp"]) <= params["logp_max"]
        and float(r["tpsa"]) <= params["tpsa_max"]
    ]
    chosen = {r["compound_id"] for r in selected}
    selected_ok = wanted == selected and len(chosen) == len(selected) == counts["selected"]
    selected_ok &= all(r["selected"] == "True" for r in wanted)
    units_ok = report["units"] == {
        "molecular_weight": "g/mol",
        "logp": "dimensionless",
        "tpsa": "angstrom^2",
    }
    for identity, passed in (
        ("row-accounting", accounted),
        ("selection", selected_ok),
        ("units", units_ok),
    ):
        ledger.record(
            identity,
            "satisfied" if passed else "failed",
            "Public exported-file check passed" if passed else "Public exported-file check failed",
            checked_bindings=snapshots[identity],
        )
    return ledger.completion()


def inspect_bundle(folder, expected_manifest_sha256, expected_bundle_sha256=None):
    folder = Path(folder)
    if sha(folder / "manifest.json") != expected_manifest_sha256:
        raise ValueError("Stored manifest identity changed")
    if expected_bundle_sha256 is not None and sha(folder / "bundle.zip") != expected_bundle_sha256:
        raise ValueError("Download bundle identity changed")
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name, identity in manifest["files"].items():
        if Path(name).name != name or sha(folder / name) != identity["sha256"]:
            raise ValueError("A recorded artifact changed: " + name)
    ledger = EvidenceLedger.restore(
        folder, json.loads((folder / "evidence.json").read_text(encoding="utf-8"))
    )
    if any(
        r.validator_version.rpartition(":")[2] != sha(Path(__file__))
        for r in ledger.requirements.values()
    ):
        raise ValueError("Evidence needs revalidation under the current validator code version")
    if not ledger.completion()["ready"]:
        raise ValueError("Evidence is no longer current")
    return manifest


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("request")
    parser.add_argument("output")
    args = parser.parse_args()
    started_cpu, started_wall = time.process_time(), time.monotonic()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    result = build_bundle(args.output, request["csv_text"], FilterSpec(**request["parameters"]))
    print(
        json.dumps(
            {
                "status": "PASS_ACTUAL_RDKIT_BUNDLE",
                "manifest_sha256": result["manifest_sha256"],
                "bundle_sha256": result["bundle_sha256"],
                "tool_cpu_seconds": time.process_time() - started_cpu,
                "tool_wall_seconds": time.monotonic() - started_wall,
                "counts": result["counts"],
                "evidence": result["evidence"],
            }
        )
    )
