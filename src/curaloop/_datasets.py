"""Read the attributed historical benchmark resource; private labels remain here."""

import gzip
import json
import random
from dataclasses import asdict
from functools import lru_cache
from hashlib import sha256
from pathlib import Path

from .domain import Candidate, ExperimentResult, PublicDataset, Scenario, canonical_json, digest


@lru_cache(maxsize=1)
def hiv_resource() -> dict:
    root = Path(__file__).with_name("resources")
    payload = (root / "hiv_replay_v1.json.gz").read_bytes()
    manifest = json.loads((root / "hiv_manifest.json").read_text(encoding="utf-8"))
    if sha256(payload).hexdigest() != manifest["resource_sha256"]:
        raise ValueError("HIV benchmark resource hash mismatch; restore the original file.")
    return {"records": json.loads(gzip.decompress(payload)), "manifest": manifest}


def build_hiv_fixture(scenario: Scenario):
    from ._oracle import TruthStore
    resource = hiv_resource()
    records = sorted(resource["records"], key=lambda r: r["compound_id"])[:scenario.candidate_count]
    candidates = []
    labels = {}
    for r in records:
        bits = set(r["morgan_on_bits"])
        candidates.append(Candidate(r["compound_id"], tuple(int(i in bits) for i in range(1024)),
                                    r["canonical_smiles"], r["scaffold_id"]))
        labels[r["compound_id"]] = bool(r["active"])
    public = [asdict(c) for c in candidates]
    dataset = PublicDataset(
        scenario.dataset, tuple(candidates), "DeepChem-HIV-sha256-" + resource["manifest"]["source_sha256"][:12],
        digest({"features": public, "private_labels": labels}), digest(public),
        assay_id="NCI_DTP_HIV_active_CA_or_CM_vs_CI",
        data_origin="HISTORICAL_PUBLIC_DATA",
        label_semantics="Historical NCI DTP screen: CA and CM mapped to active=1; CI to inactive=0; not clinical efficacy.",
        terms_status="REVIEWED_ALLOWED", metadata_json=canonical_json(resource["manifest"]),
    )
    rng = random.Random(scenario.seed + 913)
    initial_ids = sorted(rng.sample(sorted(labels), scenario.initial_count))
    initial = tuple(ExperimentResult(f"seed-{i + 1:03d}", c, dataset.assay_id, 0, labels[c],
                                    source_type="HISTORICAL_PUBLIC_DATA",
                                    quality_flag="PREEXISTING_UNIFORM_RANDOM") for i, c in enumerate(initial_ids))
    missing = frozenset(c for c in labels if int.from_bytes(
        sha256(f"missing:{scenario.seed}:{c}".encode()).digest()[:4], "big"
    ) % 100 < scenario.missing_percent)
    return dataset, TruthStore(labels, missing, source_type="HISTORICAL_PUBLIC_DATA"), initial
