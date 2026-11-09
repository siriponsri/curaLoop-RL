"""Two small control adapters over frozen State/run accounting."""

import time

from research.m2_costed_v2.engine import ComputeInterrupt, State


class DiagnosticState(State):
    def __init__(self, *args, control, **kwargs):
        self.control = control
        self.initial_decided = False
        super().__init__(*args, **kwargs)

    def cold(self):
        return False if self.control == "nearest_hit" else super().cold()

    def initialize_model(self, clock):
        if self.control == "nearest_hit":
            return True
        if self.control != "frozen_cache_greedy":
            return super().initialize_model(clock)
        if self.initial_decided:
            return True
        # Only the initial information may train this arm. One-class stays frozen.
        if super().cold():
            self.initial_decided = True
            return True
        success = super().initialize_model(clock)
        self.initial_decided = True
        return success

    def execute(self, op, policy, clock):
        if self.control != "nearest_hit":
            return super().execute(op, policy, clock)
        if not clock.enough(self.estimated_cost("REUSE")):
            return None, "NO_CPU"
        started = time.process_time()
        try:
            clock.arm()
            active = [i for i, label in self.observed.items() if label == 1]
            eligible = self.eligible()
            if active:
                scores = self.similarity[:, active].max(axis=1)
                chosen = min(eligible, key=lambda i: (-float(scores[i]), int(self.tie[i])))
                actual = "NEAREST_HIT"
            else:
                chosen = min(eligible, key=lambda i: int(self.tie[i]))
                actual = "NO_ACTIVE_SEEDED_FALLBACK"
        except ComputeInterrupt:
            self.interruptions += 1
            return None, "INTERRUPTED_NEAREST_HIT"
        finally:
            clock.disarm()
            self.costs["REUSE"] = .5 * self.costs["REUSE"] + .5 * max(.00001, time.process_time() - started)
            self.operation_counts["REUSE"] += 1
        return chosen, actual


def selector(control):
    return {"frozen_cache_greedy": ("REUSE", None), "nearest_hit": ("REUSE", None),
            "G1": ("G1", None), "Gk_k4": ("Gk", 4), "T_k4_tau0.05": ("T", (4, .05))}[control]
