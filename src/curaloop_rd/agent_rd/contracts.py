"""Closed public contracts. A mission never supplies a file, URL or permission."""

import hashlib
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from curaloop_rd.confirmation_study import BUDGETS, CAMPAIGNS, OPERATORS, RANKERS

LIMITS = {
    "development_only": "Exposed development evidence, not independent biological confirmation.",
    "missing_excluded": "Missing confirmation is excluded, never treated as inactive.",
    "nonpositive_mixed": "Source nonpositive includes inactive and inconclusive.",
    "seed_range_not_ci": "Five-seed ranges are conditional repetitions, not biological confidence intervals.",
    "one_component": "Six campaigns share one annotation-connected component.",
    "mechanical_d_equals_h": "Round-robin D=H is mechanical at these budgets.",
    "no_lab_or_clinical_value": "No measured laboratory savings, prospective efficacy or clinical benefit.",
    "aggregate_only": "No individual compounds or hidden/pending outcomes are available.",
    "commercial_rights_unconfirmed": "Commercial/raw-data redistribution clearance is not established.",
    "no_rl_result": "CF1 did not evaluate RL; the simulator is a separate retrospective study.",
}


class MissionSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: str = Field(min_length=8, max_length=2400)
    campaign: str = "equal"
    budgets: list[StrictInt] = Field(default_factory=lambda: [10], min_length=1, max_length=5)
    arms: list[str] = Field(default_factory=lambda: ["mvsa/top_ranked", "mvsa/cluster_round_robin"], min_length=1, max_length=18)
    locale: Literal["en", "th"] = "en"
    mode: Literal["agent", "deterministic"] = "agent"
    export_requested: bool = False

    @model_validator(mode="after")
    def fixed_scope(self):
        if self.campaign not in ("equal", *CAMPAIGNS):
            raise ValueError("Only admitted CF1 aggregate campaigns are available")
        if len(set(self.budgets)) != len(self.budgets) or any(v not in BUDGETS for v in self.budgets):
            raise ValueError("Choose distinct admitted budget percentages")
        allowed = {r + "/" + o for r in RANKERS for o in OPERATORS}
        if len(set(self.arms)) != len(self.arms) or any(v not in allowed for v in self.arms):
            raise ValueError("Unknown or repeated ranker/operator")
        return self


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


ANSWER_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "action": {"type": "string", "enum": ["answer", "abstain"]},
        "values": {"type": "object", "additionalProperties": {"type": "number"}},
        "limitations": {"type": "array", "items": {"type": "string", "enum": list(LIMITS)}},
        "reason": {"type": "string", "enum": ["none", "forbidden_scope", "insufficient_evidence", "source_unavailable"]},
        "evidence_id": {"type": "string"},
    }, "required": ["action"],
}

REPORT_SCHEMA = {"oneOf": [ANSWER_SCHEMA, *[{"type": "object", "properties": {"action": {"const": action}},
                 "required": ["action"], "additionalProperties": False} for action in ("read", "compute")]]}
