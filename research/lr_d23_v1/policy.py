"""One frozen residual UPDATE/REUSE mechanism over the existing State engine."""

import copy

import numpy as np

from research.d1_v1.controls import DiagnosticState

FEATURE_NAMES = (
    "remaining_fraction", "cpu_remaining_fraction", "stale_labels_over_B", "cached_margin",
    "eligible_cached_std", "observed_positive_fraction", "recent_brier", "model_available",
)
NO_HISTORY_KEEP = (0, 1, 3, 4)


class Gate:
    def __init__(self, artifact):
        assert artifact["schema"] == "curaloop.lr_d23.gate.v1"
        self.artifact = artifact
        self.keep = np.asarray(artifact["feature_indices"], dtype=int)
        self.mean = np.asarray(artifact["mean"], dtype=float)
        self.scale = np.asarray(artifact["scale"], dtype=float)
        self.coef = np.asarray(artifact["coefficients"], dtype=float)
        self.intercept = float(artifact["intercept"])
        assert len(self.keep) == len(self.mean) == len(self.scale) == len(self.coef)
        assert (self.scale > 0).all() and all(np.isfinite(v).all() for v in (self.mean, self.scale, self.coef))
        assert np.isfinite(self.intercept)

    def predict(self, features):
        return float(self.coef @ ((np.asarray(features)[self.keep] - self.mean) / self.scale) + self.intercept)


class ResidualState(DiagnosticState):
    def __init__(self, *args, gate_artifact=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.residual_gate = Gate(gate_artifact) if gate_artifact else None
        self.gate_log = []
        self.pending_gate_decision = None

    def residual_features(self, clock):
        eligible = self.eligible()
        scores = self.model.p[eligible] if eligible else np.array([.5])
        top = sorted(eligible, key=lambda i: (-float(self.model.p[i]), int(self.tie[i])))[:2]
        margin = float(self.model.p[top[0]] - self.model.p[top[1]]) if len(top) > 1 else 0.
        n = len(self.observed)
        return np.array([
            (self.budget - self.deliveries) / max(1, self.budget),
            max(0., clock.remaining()) / clock.cap,
            self.stale() / max(1, self.budget), margin, float(np.std(scores)),
            sum(self.observed.values()) / n if n else .5,
            float(np.mean(self.errors[-8:])) if self.errors else .25, float(self.ready()),
        ])

    def choose_operation(self, policy, clock, parameter=None, gate=None, restricted=()):
        if policy != "D23":
            return super().choose_operation(policy, clock, parameter, gate, restricted)
        assert self.residual_gate is not None
        base = "UPDATE" if self.stale() >= 2 else "REUSE"
        gain = self.residual_gate.predict(self.residual_features(clock))
        assert np.isfinite(gain), "NONFINITE_GATE_VALUE"
        proposed = "UPDATE" if gain > .25 else "REUSE" if gain < -.25 else base
        feasible = [op for op in ("REUSE", "UPDATE")
                    if op not in restricted and clock.enough(self.estimated_cost(op))]
        chosen = proposed if proposed in feasible else "REUSE" if "REUSE" in feasible else None
        if chosen != proposed:
            self.feasibility_fallbacks += 1
        row = {"deliveries_before": self.deliveries, "incumbent_operation": base,
               "predicted_update_minus_reuse": gain, "proposed_operation": proposed,
               "chosen_operation": chosen, "override_requested": proposed != base,
               "feasibility_fallback": chosen != proposed, "delivered": False}
        self.gate_log.append(row)
        self.pending_gate_decision = len(self.gate_log) - 1
        return chosen, None

    def accept(self, *args, **kwargs):
        super().accept(*args, **kwargs)
        if self.pending_gate_decision is not None:
            row = self.gate_log[self.pending_gate_decision]
            assert row["deliveries_before"] == self.deliveries - 1
            row["delivered"] = True
            row["actual_operation"] = self.trace[-1]["actual_operation"]
            self.pending_gate_decision = None

    def snapshot(self, clock):
        value = super().snapshot(clock)
        value.update(initial_decided=self.initial_decided, interruptions=self.interruptions,
                     feasibility_fallbacks=self.feasibility_fallbacks, gate_log=copy.deepcopy(self.gate_log))
        return value

    @classmethod
    def restore_residual(cls, pool, kind, seed, n0, budget, snapshot, similarity, neighbors,
                         control, gate_artifact=None):
        value = cls.restore(pool, kind, seed, n0, budget, snapshot, similarity, neighbors)
        value.control = control
        value.initial_decided = snapshot.get("initial_decided", False)
        value.interruptions = snapshot.get("interruptions", 0)
        value.feasibility_fallbacks = snapshot.get("feasibility_fallbacks", 0)
        value.residual_gate = Gate(gate_artifact) if gate_artifact else None
        value.gate_log = copy.deepcopy(snapshot.get("gate_log", []))
        value.pending_gate_decision = None
        return value


def selector(control):
    if control in ("candidate_v0", "candidate_v1", "no_history_v1"):
        return "D23", None
    return {"G1": ("G1", None), "Gk2": ("Gk", 2), "Gk4": ("Gk", 4),
            "T_k4_tau0.05": ("T", (4, .05)), "frozen_cache_greedy": ("REUSE", None),
            "nearest_hit": ("REUSE", None)}[control]
