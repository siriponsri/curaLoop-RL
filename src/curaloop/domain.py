"""Immutable public contracts. Hidden truth does not belong in this module."""

import json
import math
from dataclasses import asdict, dataclass
from hashlib import sha256

DATASETS = ("hiv_moleculenet_replay_v1", "synthetic_linear_v1", "synthetic_shift_v1")
BASELINES = ("random", "greedy", "uncertainty")
POLICIES = BASELINES + ("q_learning", "contextual_bandit")


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Scenario:
    dataset: str = "synthetic_linear_v1"
    seed: int = 42
    candidate_count: int = 240
    initial_count: int = 12
    budget_units: int = 30
    batch_size: int = 5
    delay_steps: int = 2
    assay_cost_units: int = 1
    delay_jitter: int = 0
    missing_percent: int = 0

    def __post_init__(self) -> None:
        if self.dataset not in DATASETS:
            raise ValueError("Unsupported dataset; only the two original synthetic fixtures are enabled.")
        limits = {
            "seed": (0, 2**32 - 1), "candidate_count": (0, 2000),
            "initial_count": (0, self.candidate_count), "budget_units": (0, 10000),
            "batch_size": (1, 100), "delay_steps": (0, 100),
            "assay_cost_units": (1, 100), "delay_jitter": (0, 20),
            "missing_percent": (0, 100),
        }
        for name, (lower, upper) in limits.items():
            value = getattr(self, name)
            if type(value) is not int or not lower <= value <= upper:
                raise ValueError(f"{name} must be an integer in [{lower}, {upper}].")
        if self.dataset == "hiv_moleculenet_replay_v1" and self.candidate_count > 1200:
            raise ValueError("The bundled HIV replay pool has 1200 molecules. Rebuild it for larger studies.")

    @property
    def scenario_id(self) -> str:
        return "scenario-" + digest(asdict(self))[:16]


@dataclass(frozen=True, slots=True)
class Candidate:
    compound_id: str
    features: tuple[float, ...]
    canonical_smiles: str | None = None
    scaffold_id: str | None = None

    def __post_init__(self) -> None:
        if not self.compound_id or not isinstance(self.features, tuple) or not self.features:
            raise ValueError("A candidate needs an ID and an immutable nonempty feature tuple.")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
               for v in self.features):
            raise ValueError("Features must contain finite numbers only.")


@dataclass(frozen=True, slots=True)
class PublicDataset:
    name: str
    candidates: tuple[Candidate, ...]
    release: str
    sha256: str
    feature_sha256: str
    assay_id: str = "fictional_binary_assay_v1"
    data_origin: str = "SYNTHETIC_ONLY"
    label_semantics: str = "Fictional active/inactive outcome; no biological efficacy meaning."
    terms_status: str = "ORIGINAL_SYNTHETIC"
    metadata_json: str = "{}"

    def __post_init__(self) -> None:
        ids = [c.compound_id for c in self.candidates]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate candidate IDs.")
        if len({len(c.features) for c in self.candidates}) > 1:
            raise ValueError("Inconsistent feature dimensions.")


@dataclass(frozen=True, slots=True)
class ExperimentRequest:
    request_id: str
    batch_id: str
    compound_id: str
    assay_id: str
    scheduled_at_step: int
    due_at_step: int
    cost_units: int
    explanation: str
    predicted_probability: float | None = None
    model_status: str = "NOT_USED"

    def __post_init__(self) -> None:
        if any(not isinstance(v, str) or not v for v in (
            self.request_id, self.batch_id, self.compound_id, self.assay_id
        )):
            raise ValueError("Experiment identifiers must be nonempty strings.")
        if any(type(v) is not int or v < 0 for v in (self.scheduled_at_step, self.due_at_step)):
            raise ValueError("Experiment times must be nonnegative integer steps.")
        if self.due_at_step < self.scheduled_at_step:
            raise ValueError("An experiment cannot be due before its request.")
        if type(self.cost_units) is not int or self.cost_units <= 0:
            raise ValueError("Experiment cost must be a positive integer.")
        if self.predicted_probability is not None and (
            not math.isfinite(self.predicted_probability) or not 0 <= self.predicted_probability <= 1
        ):
            raise ValueError("Predicted probability must be finite in [0, 1].")


@dataclass(frozen=True, slots=True)
class ExperimentResult:
    request_id: str
    compound_id: str
    assay_id: str
    delivered_at_step: int
    active: bool | None
    source_type: str = "SYNTHETIC_ONLY"
    quality_flag: str = "OK"


@dataclass(frozen=True, slots=True)
class PolicyObservation:
    schema_version: str
    run_id: str
    scenario_id: str
    step: int
    eligible_candidate_ids: tuple[str, ...]
    available_features: tuple[tuple[str, tuple[float, ...]], ...]
    revealed_assay_results: tuple[ExperimentResult, ...]
    pending_candidate_ids: tuple[str, ...]
    budget_remaining_units: int
    current_policy_id: str
    seed: int
    slots_available: int
    assay_cost_units: int
    budget_total_units: int
    controller_json: str | None = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result["available_features"] = dict(self.available_features)
        return result


@dataclass(frozen=True, slots=True)
class Selection:
    compound_id: str
    explanation: str
    predicted_probability: float | None = None
    acquisition_score: float | None = None
    model_status: str = "NOT_USED"


@dataclass(frozen=True, slots=True)
class Event:
    schema_version: str
    event_id: str
    run_id: str
    scenario_id: str
    policy_id: str
    event_type: str
    step: int
    compound_id: str | None = None
    request_id: str | None = None
    due_at_step: int | None = None
    cost_units: int = 0
    delivered_active: bool | None = None
    explanation: str = ""
    data_origin: str = "SYNTHETIC_ONLY"
    scenario_origin: str = "SYNTHETIC_ASSUMPTION"

    def __post_init__(self) -> None:
        if self.delivered_active is not None and self.event_type not in (
            "INITIAL_LABEL", "RESULT_DELIVERED"
        ):
            raise ValueError("Unrevealed events cannot contain a label.")
