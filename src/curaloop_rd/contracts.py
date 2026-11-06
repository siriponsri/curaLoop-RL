"""Typed records for inspectable offline planning; values are never assay results."""

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from decimal import Decimal

from . import VERSION


class WorkflowError(ValueError):
    def __init__(self, code, detail):
        self.code = code
        super().__init__(f"{code}: {detail}")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def identity(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def number(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise WorkflowError("INVALID_NUMBER", name)
    return value


@dataclass(frozen=True)
class Source:
    source_id: str
    citation: str
    version: str
    locator: str
    role: str
    available: bool
    target: str
    endpoint: str
    unit: str
    measurement_status: str
    statement: str
    synthetic: bool = True

    def gate(self):
        # Inspect authority metadata before exposing the source payload.
        if type(self.source_id) is not str or type(self.role) is not str:
            raise WorkflowError("INVALID_SOURCE", "String identity and role required")
        if self.role == "final_reserved" or self.source_id in {"fixture_reserved", "alias_fixture_reserved"}:
            raise WorkflowError("RESERVED_EVIDENCE", self.source_id)
        if self.role not in ("development_fixture", "public_metadata"):
            raise WorkflowError("EXPOSURE_UNCLEARED", self.source_id)
        if type(self.available) is not bool or type(self.synthetic) is not bool:
            raise WorkflowError("INVALID_SOURCE", "Boolean authority fields required")
        if not self.available:
            raise WorkflowError("SOURCE_UNAVAILABLE", self.source_id)
        fields = (self.source_id, self.citation, self.version, self.locator, self.target,
                  self.endpoint, self.unit, self.statement)
        if any(type(value) is not str or not value.strip() or len(value) > 8192 for value in fields):
            raise WorkflowError("INVALID_SOURCE", "Missing or oversized provenance field")
        if self.measurement_status not in {
            "measured_exact", "tested_censored", "default_filled", "missing", "untested",
            "predicted", "metadata_only",
        }:
            raise WorkflowError("INVALID_SOURCE", "Unknown measurement status")

    def public(self):
        self.gate()
        value = asdict(self)
        return {**value, "record_sha256": identity(value)}


@dataclass(frozen=True)
class Brief:
    question: str
    target: str
    endpoint: str
    unit: str
    source_ids: tuple[str, ...]
    request_count: int
    unit_cost: float
    budget: float

    def check(self):
        for value in (self.question, self.target, self.endpoint, self.unit):
            if type(value) is not str or not value.strip() or len(value) > 8192:
                raise WorkflowError("INVALID_BRIEF", "Nonempty bounded text required")
        if type(self.request_count) is not int or not 1 <= self.request_count <= 10000:
            raise WorkflowError("INVALID_BRIEF", "Positive bounded integer count required")
        number(self.unit_cost, "unit cost")
        number(self.budget, "budget")
        if (type(self.source_ids) is not tuple or not self.source_ids or len(self.source_ids) > 256
                or any(type(key) is not str for key in self.source_ids)
                or len(set(self.source_ids)) != len(self.source_ids)):
            raise WorkflowError("INVALID_BRIEF", "Unique evidence IDs required")
        if Decimal(str(self.unit_cost)) * self.request_count > Decimal(str(self.budget)):
            raise WorkflowError("BUDGET_EXCEEDED", "Planned requests exceed budget")


def search_evidence(catalogue, query):
    """Search a supplied offline catalogue; no external source is contacted."""
    words = query.casefold().split()
    found = []
    for source in catalogue.values():
        if source.role == "final_reserved":
            continue
        source.gate()
        text = (source.target + " " + source.endpoint + " " + source.citation).casefold()
        if all(word in text for word in words):
            found.append(source.public())
    return sorted(found, key=lambda r: r["source_id"])


def inspect_source(catalogue, source_id):
    if source_id not in catalogue:
        raise WorkflowError("SOURCE_UNAVAILABLE", source_id)
    return catalogue[source_id].public()


def draft_plan(brief, catalogue):
    brief.check()
    records = [inspect_source(catalogue, key) for key in brief.source_ids]
    if any((r["target"], r["endpoint"], r["unit"]) !=
           (brief.target, brief.endpoint, brief.unit) for r in records):
        raise WorkflowError("ENDPOINT_CONFLICT", "Target, phenotype and units must match exactly")
    limitations = sorted({r["measurement_status"] for r in records
                          if r["measurement_status"] != "measured_exact"})
    plan = {
        "schema": VERSION,
        "question": brief.question,
        "target": brief.target,
        "endpoint": brief.endpoint,
        "unit": brief.unit,
        "request_count": brief.request_count,
        "unit_cost": brief.unit_cost,
        "budget": brief.budget,
        "planned_cost": float(Decimal(str(brief.unit_cost)) * brief.request_count),
        "cost_semantics": "ILLUSTRATIVE_NOT_MEASURED_LAB_COST",
        "evidence": records,
        "limitations": limitations,
        "execution": "OFFLINE_PROPOSAL_ONLY_NO_MEASUREMENTS_ORDERED",
        "synthetic_fixture_present": any(r["synthetic"] for r in records),
        "confirmed_hits": None,
    }
    return {**plan, "plan_sha256": identity(plan)}


def validate_plan(plan):
    """Validate content identity and all declared fields again at the boundary."""
    if type(plan) is not dict or type(plan.get("evidence")) is not list:
        raise WorkflowError("INVALID_PLAN", "Plan object with evidence list required")
    body = {key: value for key, value in plan.items() if key != "plan_sha256"}
    if plan.get("schema") != VERSION or identity(body) != plan.get("plan_sha256"):
        raise WorkflowError("PLAN_IDENTITY_MISMATCH", "Plan content changed")
    try:
        records = [Source(**{k: v for k, v in r.items() if k != "record_sha256"})
                   for r in plan["evidence"]]
        for record, raw in zip(records, plan["evidence"]):
            if record.public() != raw:
                raise WorkflowError("SOURCE_IDENTITY_MISMATCH", record.source_id)
        catalogue = {record.source_id: record for record in records}
        if len(catalogue) != len(records):
            raise WorkflowError("INVALID_SOURCE", "Duplicate source ID")
        brief = Brief(plan["question"], plan["target"], plan["endpoint"], plan["unit"],
                      tuple(r.source_id for r in records), plan["request_count"],
                      plan["unit_cost"], plan["budget"])
        if draft_plan(brief, catalogue) != plan:
            raise WorkflowError("PLAN_IDENTITY_MISMATCH", "Derived plan fields differ")
    except (KeyError, TypeError, AttributeError) as exc:
        raise WorkflowError("INVALID_PLAN", str(exc)) from exc
    return plan
