"""Check generation against public observations, never evaluator gold."""

import math

from .contracts import LIMITS


def verify(report, evidence, derived):
    errors = []
    allowed = {"action", "values", "limitations", "reason", "evidence_id"}
    if not isinstance(report, dict) or set(report) - allowed:
        return {"valid": False, "errors": ["REPORT_SCHEMA"], "verified_values": 0}
    action = report.get("action")
    if action not in ("answer", "abstain"):
        return {"valid": False, "errors": ["FINAL_ACTION_REQUIRED"], "verified_values": 0}
    values = report.get("values", {})
    limits = report.get("limitations", [])
    if not isinstance(values, dict) or not isinstance(limits, list) or any(v not in LIMITS for v in limits):
        return {"valid": False, "errors": ["REPORT_FIELDS"], "verified_values": 0}
    if action == "abstain":
        if "evidence_id" in report and report["evidence_id"] != evidence["evidence_id"]:
            errors.append("EVIDENCE_ID_MISMATCH")
        if values or report.get("reason") not in ("forbidden_scope", "insufficient_evidence", "source_unavailable"):
            errors.append("ABSTENTION_HAS_CLAIMS_OR_NO_REASON")
        if report.get("reason") == "source_unavailable" and evidence["status"] != "source_unavailable":
            errors.append("FALSE_SOURCE_UNAVAILABLE")
        return {"valid": not errors, "errors": errors, "verified_values": 0}
    if evidence["status"] != "available":
        errors.append("SOURCE_UNAVAILABLE_CANNOT_ANSWER")
    if report.get("evidence_id") != evidence["evidence_id"]:
        errors.append("EVIDENCE_ID_MISMATCH")
    if "development_only" not in limits:
        errors.append("DEVELOPMENT_SCOPE_MISSING")
    if not values and not limits:
        errors.append("EMPTY_ANSWER")
    expected = {**evidence["values"], **derived.get("values", {})}
    verified = 0
    for key, value in values.items():
        if key not in expected:
            errors.append("UNSUPPORTED_KEY:" + str(key))
        elif type(value) not in (float, int) or not math.isfinite(value) or abs(value - expected[key]) > .0005000001:
            errors.append("WRONG_VALUE:" + str(key))
        else:
            verified += 1
    return {"valid": not errors, "errors": errors, "verified_values": verified}
