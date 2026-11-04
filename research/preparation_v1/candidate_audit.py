"""Public metadata/CID/structure-only audit with an explicit no-outcome URL guard."""

import hashlib
import json
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, unquote, urlparse
from urllib.request import urlopen

from rdkit import Chem, DataStructs, rdBase
from rdkit.Chem import rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

from .candidates import CANDIDATES

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "research/raw_data/candidate-audit-20261104-v1"
PACKET = ROOT / "docs/evidence/design-preparation-20261104-v1"
SAMPLE_N = 200


def sha(data):
    return hashlib.sha256(data).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def validate_url(url):
    p = urlparse(url)
    if (
        p.scheme != "https"
        or p.hostname != "pubchem.ncbi.nlm.nih.gov"
        or p.username
        or p.password
        or p.fragment
    ):
        raise ValueError("Only this public HTTPS metadata API is allowed.")
    path, query = unquote(p.path), parse_qs(p.query)
    if re.fullmatch(r"/rest/pug/assay/aid/\d+/(description|cids)/JSON", path):
        if path.endswith("/cids/JSON") and query == {"cids_type": ["all"]}:
            return "cids"
        if path.endswith("/description/JSON") and not query:
            return "description"
    if (
        re.fullmatch(r"/rest/pug/compound/cid/[\d,]+/property/IsomericSMILES/JSON", path)
        and not query
    ):
        return "structures"
    raise ValueError(
        "Outcome endpoints, outcome-filtered membership and unknown query options are forbidden."
    )


def project_payload(kind, data):
    if kind == "description":
        assert set(data) == {"PC_AssayContainer"}
        assay = data["PC_AssayContainer"][0]["assay"]
        if set(assay) != {"descr"}:
            raise ValueError(
                "Unexpected assay data section; quarantine response and record exposure incident."
            )
        d = assay["descr"]
        # Do not read result prose, protocols, comments or activity summaries.
        return {
            k: d.get(k)
            for k in ("aid", "aid_source", "name", "revision", "target", "activity_outcome_method")
        }
    if kind == "cids":
        assert set(data) == {"InformationList"}
        rows = data["InformationList"]["Information"]
        assert all(set(r) <= {"AID", "CID"} for r in rows)
        return sorted({cid for row in rows for cid in row.get("CID", [])})
    if kind == "structures":
        assert set(data) == {"PropertyTable"}
        rows = data["PropertyTable"]["Properties"]
        assert all(set(row) == {"CID", "SMILES"} for row in rows)
        return rows
    raise ValueError("Unknown projection.")


class Fetcher:
    def __init__(self):
        self.receipts, self.bytes, self.blocked, self.started = [], 0, False, time.monotonic()
        self.limits = json.loads((ROOT / "research/configs/design_sensitivity_v1.json").read_text())

    def get(self, url):
        kind = validate_url(url)
        if (
            self.blocked
            or len(self.receipts) >= self.limits["max_audit_http_requests"]
            or self.bytes >= self.limits["max_audit_http_payload_bytes_before_next_request"]
            or time.monotonic() - self.started > self.limits["max_audit_http_wall_seconds"]
        ):
            raise ValueError(
                "Access or prespecified request/byte/wall budget stopped further retrieval."
            )
        time.sleep(0.55)
        receipt = {
            "url": url,
            "kind": kind,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        }
        try:
            with urlopen(url, timeout=20) as response:
                raw = response.read(self.limits["max_audit_response_bytes"] + 1)
                self.bytes += len(raw)
                if len(raw) > self.limits["max_audit_response_bytes"]:
                    raise ValueError("Response exceeds the per-file metadata budget.")
                projected = project_payload(kind, json.loads(raw))
                filename = sha(url.encode()) + ".json"
                (RAW / filename).write_bytes(raw)
                receipt.update(
                    status="PASS",
                    bytes=len(raw),
                    sha256=sha(raw),
                    raw_file=filename,
                    content_type=response.headers.get("Content-Type"),
                )
                return projected
        except Exception as error:
            if isinstance(error, HTTPError) and error.code in (401, 403):
                self.blocked = True
            receipt.update(
                status="FAIL",
                error=type(error).__name__ + ": " + str(error),
                no_retry_or_bypass=True,
            )
            raise
        finally:
            self.receipts.append(receipt)
            save(PACKET / "request-receipts.json", self.receipts)


def select_ids(aid, ids, n=SAMPLE_N):
    return sorted(set(ids), key=lambda cid: sha(f"feature-audit-v1:20261104:{aid}:{cid}".encode()))[
        :n
    ]


def canonical(smiles):
    with rdBase.BlockLogs():
        mol = Chem.MolFromSmiles(smiles)
    return None if mol is None else Chem.MolToSmiles(mol, isomericSmiles=True)


def reference_structures():
    # Existing exposed source files only; activity columns never enter this audit.
    raw = ROOT / "research/raw_data/ncats-development-20261104"
    all_ncats = set()
    for assay in ("ahr", "pparg", "p53"):
        all_ncats.update(
            filter(
                None,
                (
                    canonical(line.split("\t")[0])
                    for line in (raw / (assay + ".smiles")).read_text().splitlines()
                ),
            )
        )
    subsets = set()
    for assay in ("ahr", "pparg", "p53"):
        subsets.update(
            r["canonical_smiles"]
            for r in json.loads((raw / "prepared-v1" / (assay + ".json")).read_text())["records"]
        )
    import gzip

    hiv = json.loads(
        gzip.decompress((ROOT / "src/curaloop/resources/hiv_replay_v1.json.gz").read_bytes())
    )
    return {
        "all_previously_retrieved_NCATS_structures": all_ncats,
        "three_exposed_600_subsets_union": subsets,
        "HIV_regression_1200": {r["canonical_smiles"] for r in hiv},
    }


def overlap(structures, reference, generator):
    keys = sorted(set(structures))
    query = [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in keys]
    results = {}
    for name, ref in reference.items():
        fingerprints = ref["fingerprints"]
        maxima = [
            max(DataStructs.BulkTanimotoSimilarity(fp, fingerprints), default=0) for fp in query
        ]
        results[name] = {
            "reference_n": len(ref["structures"]),
            "exact_canonical_matches": len(set(keys) & ref["structures"]),
            "queries_nearest_tanimoto_ge_0_8": sum(v >= 0.8 for v in maxima),
            "mean_nearest_tanimoto": sum(maxima) / len(maxima) if maxima else None,
            "max_nearest_tanimoto": max(maxima, default=None),
        }
    return results


def main():
    if RAW.exists() or PACKET.exists():
        raise ValueError("Preserve existing audit attempts; use a new version.")
    RAW.mkdir(parents=True)
    PACKET.mkdir(parents=True)
    (PACKET / ".gitattributes").write_text(
        "*.json whitespace=trailing-space,space-before-tab,cr-at-eol\n*.csv whitespace=trailing-space,space-before-tab,cr-at-eol\n*.xml whitespace=trailing-space,space-before-tab,cr-at-eol\n",
        newline="\n",
    )
    started, cpu = time.perf_counter(), time.process_time()
    git_commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    generator = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=1024)
    refs = {
        name: {
            "structures": keys,
            "fingerprints": [generator.GetFingerprint(Chem.MolFromSmiles(s)) for s in sorted(keys)],
        }
        for name, keys in reference_structures().items()
    }
    fetcher, records = Fetcher(), []
    for candidate in CANDIDATES:
        aid = candidate["aid"]
        row = {
            **candidate,
            "role": "METADATA_FEATURE_AUDIT_ONLY_NO_FINAL_ROLE_ASSIGNED",
            "outcome_values_requested": False,
            "family_annotation": "PROVISIONAL_MANUAL_GROUPING; requires domain review",
            "label_mapping": "Prospective PubChem enum inactive(1)/active(2), other outcomes quarantined; not NCATS CSV 0/1",
            "label_eligibility_counts": "NOT_INSPECTED",
            "final_eligibility": "NOT_CLEARED",
        }
        try:
            row["metadata"] = fetcher.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/description/JSON"
            )
            ids = fetcher.get(
                f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/assay/aid/{aid}/cids/JSON?cids_type=all"
            )
            chosen = select_ids(aid, ids)
            if not chosen:
                raise ValueError("No unfiltered compound membership; no structural audit possible.")
            row["all_unfiltered_cid_count"] = len(ids)
            row["label_blind_sample_cids"] = chosen
            properties = (
                fetcher.get(
                    "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/"
                    + ",".join(map(str, chosen))
                    + "/property/IsomericSMILES/JSON"
                )
                if chosen
                else []
            )
            assert {r["CID"] for r in properties} == set(chosen)
            structures = [canonical(r["SMILES"]) for r in properties]
            valid = sorted(set(filter(None, structures)))
            row.update(
                sample_n=len(chosen),
                sample_valid_unique=len(valid),
                sample_invalid=sum(s is None for s in structures),
                sample_structure_sha256=sha(json.dumps(valid, separators=(",", ":")).encode()),
                overlaps=overlap(valid, refs, generator),
                nonempty_sample_scaffolds=len(
                    {MurckoScaffold.MurckoScaffoldSmiles(mol=Chem.MolFromSmiles(s)) for s in valid}
                    - {""}
                ),
                status="FEATURE_AUDIT_PASS",
            )
            row["source_rights"] = (
                "NCATS_PROVIDER_PUBLIC_DOMAIN_STATEMENT; exact PubChem response has no file license; prepared-release/structure rights closure still required"
                if candidate["source_program"].startswith("NCATS")
                else "LIT_PREPARED_FILE_TERMS_UNRESOLVED; direct PubChem response requires depositor-specific review; no blanket license inferred"
            )
            row["exclusion_or_gate"] = (
                "EXCLUDE_FINAL_SHARED_DEVELOPMENT_TARGET"
                if candidate["provisional_planning_family"] in ("exposed_PPARG", "exposed_TP53")
                else "EXCLUDE_PENDING_VDR_PHENOTYPE_RESOLUTION"
                if candidate["short_name"] == "VDR"
                else "RIGHTS_ENDPOINT_FAMILY_FULL_POOL_AND_LABEL_SEAL_GATES_OPEN"
            )
        except Exception as error:
            row.update(
                status="AUDIT_PARTIAL_OR_FAILED", error=type(error).__name__ + ": " + str(error)
            )
        records.append(row)
        save(PACKET / "candidate-audit.json", {"status": "IN_PROGRESS", "records": records})
        print(f"{row['status']} AID={aid} {candidate['short_name']}", flush=True)
    result = {
        "status": "COMPLETE_WITH_EXPLICIT_GATES",
        "records": records,
        "candidate_count": len(records),
        "feature_audits_complete": sum(r["status"] == "FEATURE_AUDIT_PASS" for r in records),
        "reference_structure_counts": {n: len(r["structures"]) for n, r in refs.items()},
        "rdkit_version": rdBase.rdkitVersion,
        "sample_size_limit": SAMPLE_N,
        "source_commit": git_commit,
        "source_lf_sha256": {
            name: sha((ROOT / name).read_text().encode())
            for name in (
                "research/preparation_v1/candidate_audit.py",
                "research/preparation_v1/candidates.py",
            )
        },
        "configuration": "research/configs/design_sensitivity_v1.json",
        "reference_file_sha256": {
            name: sha((ROOT / name).read_bytes())
            for name in ["src/curaloop/resources/hiv_replay_v1.json.gz"]
            + [
                f"research/raw_data/ncats-development-20261104/{a}.smiles"
                for a in ("ahr", "pparg", "p53")
            ]
            + [
                f"research/raw_data/ncats-development-20261104/prepared-v1/{a}.json"
                for a in ("ahr", "pparg", "p53")
            ]
        },
        "method": "SHA256 rank aid/CID; no activity filter or value; RDKit isomeric canonical; salts/tautomers retained; radius2/1024 nonchiral Morgan",
        "outcome_value_endpoints_requested": 0,
        "final_roles_assigned": 0,
        "published_aggregate_exposure": "LIT-PCBA provider landing-page class totals were visible in prior review and current metadata discovery; not used for inclusion, ranking, power inputs or thresholds. No compound outcomes retrieved.",
        "rights_limits": "Primary source metadata is not a grant to redistribute a prepared dataset. Full raw feature/metadata responses remain ignored.",
        "wall_seconds": time.perf_counter() - started,
        "process_cpu_seconds": time.process_time() - cpu,
        "network_bytes": fetcher.bytes,
        "requests": len(fetcher.receipts),
        "paid_calls": 0,
        "gpu_jobs": 0,
        "reviewer": "Same implementer; not independent legal/biological/statistical review",
        "final_protocol_frozen": False,
    }
    save(PACKET / "candidate-audit.json", result)
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
