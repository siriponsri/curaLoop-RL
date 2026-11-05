"""New predictor adapter; reuses frozen public-state validation and recourse."""

import time

import numpy as np

from research.planning_v3.mixture import top_indices
from research.planning_v3.policy import PolicySession
from research.planning_v3.recourse import RecoursePlanner

from .belief import design_for, fit_joint, similarity

JOINT_METHODS = ("greedy", "frozen_greedy", "event_dense", "no_wait", "no_pending_information", "timing_blind_tail")


def knn_scores(packed, ids, known, k=8):
    """Fixed similarity-weighted kNN with Beta(1,1) probability smoothing."""
    index = {cid: i for i, cid in enumerate(ids)}
    values = []
    for bits in packed:
        neighbors = sorted(((similarity(bits, packed[index[cid]]), cid, y) for cid, y in known),
                           key=lambda row: (-row[0], row[1]))[:k]
        total = sum(row[0] for row in neighbors)
        positive = sum(row[0] for row in neighbors if row[2])
        values.append((1 + positive) / (2 + total))
    return np.array(values)


class RepairSession(PolicySession):
    def __init__(self, observation, method, seed, law, capacity, variant):
        started = time.perf_counter()
        if method not in JOINT_METHODS and method != "tanimoto_knn":
            raise ValueError("Unsupported fixed diagnostic method.")
        # Base random initialization establishes the original public ledger and
        # does not fit/build an unused predictor. No module globals are patched.
        super().__init__(observation, "random", seed, law, capacity, 128)
        self.method, self.variant = method, variant
        packed = []
        for candidate in self.candidates:
            if len(candidate.features) != 1024 or any(type(v) is not int or v not in (0, 1) for v in candidate.features):
                raise ValueError("Public binary Morgan1024 only.")
            packed.append(sum(1 << i for i, v in enumerate(candidate.features) if v))
        self.packed = tuple(packed)
        if method != "tanimoto_knn":
            self.design = design_for(self.ids, self.packed, variant)
            if self.design.ids != self.ids:
                raise ValueError("Stable sorted candidate IDs required.")
            if method == "frozen_greedy":
                self.frozen_model, self.frozen_trace = fit_joint(self.design, sorted(self.initial.items()), seed, variant)
        self.setup_seconds = time.perf_counter() - started

    def select(self, obs):
        started = time.perf_counter()
        state, known = self._public_state(obs)
        eligible = set(obs.eligible_ids)
        count = min(obs.slots, obs.uncommitted, len(eligible))
        action = ()
        trace = {"method": self.method, "predictor_variant": self.variant, "time": obs.time,
                 "model_trace": None, "fallback": None, "learned_controller_action": False,
                 "learned_action_share": 0}
        if not count:
            trace["forced_or_terminal"] = True
        elif self.method == "tanimoto_knn":
            scores = knn_scores(self.packed, self.ids, known)
            action = tuple(self.ids[i] for i in top_indices(scores, sorted(self.index[c] for c in eligible), count))
        else:
            if self.method == "frozen_greedy":
                model, detail = self.frozen_model, self.frozen_trace
            else:
                model, detail = fit_joint(self.design, known, self.seed, self.variant)
            trace.update(model_trace=detail, fallback=detail["fallback"])
            if self.method in ("greedy", "frozen_greedy"):
                action = tuple(self.ids[i] for i in top_indices(model.mu, sorted(self.index[c] for c in eligible), count))
            else:
                planner = RecoursePlanner(model, self.law, self.capacity)
                chosen, trace["planning"] = planner.choose(
                    state, screened=False, shortlist=4, allow_wait=self.method != "no_wait",
                    suppress_pending_information=self.method == "no_pending_information",
                    timing_blind_tail=self.method == "timing_blind_tail", count_budget_proxy=False)
                action = tuple(self.ids[i] for i in chosen)
        if not set(action) <= eligible or len(action) > min(obs.slots, obs.uncommitted):
            raise AssertionError("Public feasibility escaped.")
        if not action and count and not obs.pending_ids:
            raise AssertionError("WAIT requires pending information.")
        trace.update(chosen=action, policy_seconds=time.perf_counter() - started)
        self.last_proposal = (action, obs.time) if action else None
        return action, trace


def session(observation, arm, seed, law, capacity):
    if "__" in arm:
        variant, method = arm.split("__", 1)
        if variant == "anchor_original":
            return PolicySession(observation, method, seed, law, capacity, 128)
        return RepairSession(observation, method, seed, law, capacity, variant)
    if arm == "tanimoto_knn":
        return RepairSession(observation, arm, seed, law, capacity, "none")
    if arm not in ("random", "nearest_hit", "fingerprint_rf"):
        raise ValueError("Unknown fixed control.")
    return PolicySession(observation, arm, seed, law, capacity, 128)
