"""Fail-closed contracts for offline confirmation-portfolio evidence.

These contracts do not admit data, fit a ranker, or authorize an evaluation.
The source's nonpositive label includes inconclusive results; it is never
renamed a confirmed inactive label here.
"""

from dataclasses import dataclass
from math import isfinite

GATE_NAMES = ("source", "rights", "roles", "observation_support", "resources", "mandatory_baselines")


class EvidenceError(ValueError):
    pass


@dataclass(frozen=True)
class ConfirmationObservation:
    observed: bool
    source_label: int | None

    def __post_init__(self):
        if type(self.observed) is not bool:
            raise EvidenceError("Observation presence must be explicit")
        if self.observed:
            if type(self.source_label) is not int or self.source_label not in (0, 1):
                raise EvidenceError("Observed source label must be binary")
        elif self.source_label is not None:
            raise EvidenceError("Missing confirmation cannot carry an imputed label")

    @property
    def state(self):
        if not self.observed:
            return "NOT_OBSERVED"
        return "SOURCE_CONFIRMED_POSITIVE" if self.source_label else "SOURCE_NONPOSITIVE_INACTIVE_OR_INCONCLUSIVE"


def confirmation_universe(primary_labels, observations, roles_admitted):
    """Evaluator-only support mask. A blocked role cannot release a universe."""
    if roles_admitted is not True:
        raise EvidenceError("Roles not admitted")
    if len(primary_labels) != len(observations):
        raise EvidenceError("Primary and confirmation rows differ")
    if any(type(value) is not int or value not in (0, 1) for value in primary_labels):
        raise EvidenceError("Primary labels must be explicit binary values")
    if any(not isinstance(obs, ConfirmationObservation) for obs in observations):
        raise EvidenceError("Untyped confirmation state")
    return tuple(i for i, (value, obs) in enumerate(zip(primary_labels, observations, strict=True))
                 if value == 1 and obs.observed)


def evaluate_selection(selected, universe, observations, structure_groups, evaluation_released):
    """Count H/D only after the external admission/reproduction gate.

    There is deliberately no ranker API here: hidden confirmation labels may
    reach this evaluator only. Groups must be fixed independently of outcomes.
    """
    if evaluation_released is not True:
        raise EvidenceError("Confirmation evaluation is not released")
    if len(observations) != len(structure_groups):
        raise EvidenceError("Structure and observation rows differ")
    if any(type(i) is not int for i in universe) or len(set(universe)) != len(universe):
        raise EvidenceError("Malformed supported universe")
    if any(i < 0 or i >= len(observations) or not observations[i].observed for i in universe):
        raise EvidenceError("Unsupported confirmation row in universe")
    if any(type(i) is not int for i in selected) or len(set(selected)) != len(selected):
        raise EvidenceError("Selection contains repeated or malformed positions")
    if not set(selected) <= set(universe):
        raise EvidenceError("Selection extends outside supported universe")
    if any(type(group) is not str or not group.strip() for group in structure_groups):
        raise EvidenceError("Empty scaffold needs a prespecified nonempty fallback group")
    positives = [i for i in selected if observations[i].source_label == 1]
    return {"confirmation_count": len(selected), "confirmed_positives": len(positives),
            "positive_structure_groups": len({structure_groups[i] for i in positives})}


def validate_report(report):
    """Prevent a pending offline card from presenting scientific measurements."""
    if report.get("schema") != "curaloop.confirmation.offline-report.v1":
        raise EvidenceError("Unknown report schema")
    if report.get("final16_access") is not False or report.get("new_selector_training") is not False:
        raise EvidenceError("Protected or new-method scope cannot be released by this card")
    if report.get("estimand") != "OBSERVATION_SUPPORTED_PRIMARY_HITS_ONLY":
        raise EvidenceError("Whole-primary-library value is unsupported")
    gates = report.get("gates", {})
    if set(gates) != set(GATE_NAMES) or any(type(v) is not bool for v in gates.values()):
        raise EvidenceError("All gates need explicit binary evidence dispositions")
    metrics = report.get("metrics", {})
    if set(metrics) != {"confirmed_positives", "positive_structure_groups"}:
        raise EvidenceError("Missing or unexpected outcome metric")
    if report.get("status") == "FEASIBILITY_COMPLETE":
        if not all(gates.values()):
            raise EvidenceError("Outcome report requires all admission and baseline gates")
        campaigns, blocks = report.get("campaigns"), report.get("source_experiment_blocks")
        if type(campaigns) is not int or not 4 <= campaigns <= 6 or type(blocks) is not int or blocks < 2:
            raise EvidenceError("Pilot campaign/block minimum not met")
        if any(type(v) is not int or v < 0 or not isfinite(v) for v in metrics.values()):
            raise EvidenceError("Measured counts must be finite nonnegative integers")
        if metrics["positive_structure_groups"] > metrics["confirmed_positives"]:
            raise EvidenceError("Positive groups cannot exceed positive compounds")
    elif report.get("status") in ("WAITING_INPUT", "ADMISSION_NOT_PASSED"):
        if any(v is not None for v in metrics.values()):
            raise EvidenceError("Unrun outcomes must remain null, including zero")
    else:
        raise EvidenceError("Unknown evidence status")
    return report
