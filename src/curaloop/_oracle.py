"""Private simulator backend. Never imported by UI or policy workers.

This is an information boundary for trusted built-in code, not a security sandbox
against a malicious user with access to this open-source synthetic generator.
"""

import math
import random
from dataclasses import asdict
from hashlib import sha256

from .domain import Candidate, ExperimentRequest, ExperimentResult, PublicDataset, Scenario, digest


class TruthStore:
    __slots__ = ("__labels", "__requests", "__delivered", "__missing", "__source")

    def __init__(self, labels: dict[str, bool], missing_ids: frozenset[str] = frozenset(),
                 source_type: str = "SYNTHETIC_ONLY"):
        if any(type(y) is not bool for y in labels.values()):
            raise ValueError("Truth labels must be booleans.")
        self.__labels = labels.copy()
        self.__requests: dict[str, ExperimentRequest] = {}
        self.__delivered: set[str] = set()
        self.__missing = missing_ids
        self.__source = source_type

    def register(self, request: ExperimentRequest) -> None:
        if request.compound_id not in self.__labels:
            raise ValueError("Unknown oracle candidate.")
        if request.request_id in self.__requests or any(
            r.compound_id == request.compound_id for r in self.__requests.values()
        ):
            raise ValueError("Duplicate oracle request.")
        if request.due_at_step < request.scheduled_at_step or request.cost_units <= 0:
            raise ValueError("Invalid oracle request timing or cost.")
        self.__requests[request.request_id] = request

    def deliver(self, request_id: str, step: int) -> ExperimentResult:
        if request_id not in self.__requests:
            raise ValueError("A valid registered experiment is required before delivery.")
        request = self.__requests[request_id]
        if step < request.due_at_step:
            raise ValueError("Assay result is not due.")
        if request_id in self.__delivered:
            raise ValueError("Result already delivered.")
        self.__delivered.add(request_id)
        missing = request.compound_id in self.__missing
        return ExperimentResult(
            request_id, request.compound_id, request.assay_id, step,
            None if missing else self.__labels[request.compound_id],
            source_type=self.__source,
            quality_flag="MISSING_SYNTHETIC" if missing else "OK",
        )


def build_fixture(scenario: Scenario) -> tuple[PublicDataset, TruthStore, tuple[ExperimentResult, ...]]:
    """Create original toy 12D descriptors, private labels, and disclosed historical seeds.

    Synthetic-only stratification deliberately uses oracle knowledge; it is disclosed
    and never counts as a newly discovered hit or campaign expenditure.
    """
    if scenario.dataset == "hiv_moleculenet_replay_v1":
        from ._datasets import build_hiv_fixture
        return build_hiv_fixture(scenario)
    rng = random.Random(scenario.seed)
    candidates: list[Candidate] = []
    labels: dict[str, bool] = {}
    weights = (1.6, -1.3, 0.9, -0.6, 0.4, 0.2, 0, 0, 0, 0, 0, 0)
    for i in range(scenario.candidate_count):
        features = tuple(round(rng.gauss(0, 1), 8) for _ in range(12))
        latent = sum(w * x for w, x in zip(weights, features)) - 1.8
        if scenario.dataset == "synthetic_shift_v1":
            latent = 1.8 * features[0] * features[1] + 0.7 * features[2] - 1.6
        probability = 1 / (1 + math.exp(-max(-40, min(40, latent))))
        compound_id = f"CMP-{i + 1:04d}"
        candidates.append(Candidate(compound_id, features))
        labels[compound_id] = rng.random() < probability
    public_records = [asdict(c) for c in candidates]
    dataset = PublicDataset(
        scenario.dataset, tuple(candidates), "synthetic-generator-1.0.0",
        digest({"features": public_records, "private_labels": labels}), digest(public_records),
    )
    positive = [c for c, label in labels.items() if label]
    negative = [c for c, label in labels.items() if not label]
    seed_rng = random.Random(scenario.seed + 913)
    seed_rng.shuffle(positive)
    seed_rng.shuffle(negative)
    ids = positive[:scenario.initial_count // 2] + negative[:scenario.initial_count // 2]
    remainder = sorted(set(labels) - set(ids))
    seed_rng.shuffle(remainder)
    ids = sorted(ids + remainder[:scenario.initial_count - len(ids)])
    initial = tuple(ExperimentResult(
        f"seed-{i + 1:03d}", c, dataset.assay_id, 0, labels[c],
        quality_flag="PREEXISTING_SYNTHETIC_STRATIFIED",
    ) for i, c in enumerate(ids))
    missing = frozenset(c for c in labels if int.from_bytes(
        sha256(f"missing:{scenario.seed}:{c}".encode()).digest()[:4], "big"
    ) % 100 < scenario.missing_percent)
    return dataset, TruthStore(labels, missing), initial
