"""Public-Observation adapter. No Task, private resource, due time or file input."""

import time

import numpy as np

from research.event_time import Observation

from .belief import fit_mixture, make_design
from .controls import CountProxyScheduler, greedy_rollout_values, sample_distribution, uniform
from .mixture import top_indices
from .queue import completion_weights, residual_law, validate_law
from .recourse import PublicState, RecoursePlanner

METHODS = (
    "random",
    "nearest_hit",
    "frozen_greedy",
    "greedy",
    "parameter_ts",
    "fingerprint_rf",
    "count_ens",
    "cpe_scheduler",
    "greedy_rollout",
    "event_dense",
    "event_screened",
    "no_wait",
    "no_pending_information",
    "timing_blind_tail",
)


class PolicySession:
    def __init__(self, first_observation, method, seed, law, capacity=2, hypotheses=32):
        started = time.perf_counter()
        if (
            type(first_observation) is not Observation
            or first_observation.time != 0
            or first_observation.pending_ids
        ):
            raise ValueError("Policy initialization needs initial public Observation only.")
        if method not in METHODS or type(seed) is not int or not 0 <= seed < 2**32:
            raise ValueError("Unknown frozen method or invalid explicit experiment seed.")
        if type(capacity) is not int or not 1 <= capacity <= 2 or hypotheses not in (32, 64, 128):
            raise ValueError("Unsupported study capacity/hypotheses.")
        self.method, self.seed, self.law = method, seed, validate_law(law)
        self.capacity, self.hypotheses = capacity, hypotheses
        self.candidates = first_observation.candidates
        self.ids = tuple(c.candidate_id for c in self.candidates)
        if len(self.ids) > 600 or len(self.ids) != len(set(self.ids)):
            raise ValueError("Public cohort exceeds600or has duplicate IDs.")
        self.index = {cid: i for i, cid in enumerate(self.ids)}
        self.initial = {r.candidate_id: r.active for r in first_observation.initial_results}
        self.initial_budget = first_observation.uncommitted
        if type(self.initial_budget) is not int or not 0 <= self.initial_budget <= 12:
            raise ValueError("Research study unit-cost budget must be at most12.")
        self.launched, self.seen = {}, {}
        self.seen_missing = set()
        self.last_time = 0
        self.last_proposal = None
        self.random_order = sorted(
            self.ids, key=lambda cid: uniform(seed, "random-finite-pool-v1", cid)
        )
        self.packed, self.design = None, None
        self.frozen_model, self.frozen_trace = None, None
        self.scheduler = None
        completion_weights.cache_clear()  # No cross-campaign warm-cache advantage.
        if method != "random":
            packed = []
            for candidate in self.candidates:
                if len(candidate.features) != 1024 or any(
                    value not in (0, 1) for value in candidate.features
                ):
                    raise ValueError(
                        "Research adapter accepts public binary Morgan1024features only."
                    )
                packed.append(sum(1 << i for i, value in enumerate(candidate.features) if value))
            self.packed = tuple(packed)
            if method not in ("nearest_hit", "fingerprint_rf"):
                self.design = make_design(self.ids, self.packed, 64)
                if self.design.ids != self.ids:
                    raise ValueError("Observation candidate order must be stable sorted IDs.")
            if method == "frozen_greedy":
                self.frozen_model, self.frozen_trace = fit_mixture(
                    self.design, sorted(self.initial.items()), seed, hypotheses
                )
            if method == "cpe_scheduler":
                self.scheduler = CountProxyScheduler(self.law, capacity, 20000)
        self._public_state(first_observation)
        self.setup_seconds = time.perf_counter() - started

    def _public_state(self, obs):
        if type(obs) is not Observation or obs.candidates != self.candidates:
            raise ValueError("Policy accepts the unchanged public feature cohort only.")
        if (
            obs.deadline is None
            or obs.remaining_time != obs.deadline - obs.time
            or obs.time < self.last_time
        ):
            raise ValueError("Bounded monotone public clock required.")
        if {r.candidate_id: r.active for r in obs.initial_results} != self.initial:
            raise ValueError("Initial public information changed.")
        results = obs.initial_results + obs.delivered_results
        known = {r.candidate_id: r.active for r in results}
        if len(known) != len(results) or any(
            r.candidate_id not in self.index
            or type(r.active) is not bool
            or not 0 <= r.delivered_at <= obs.time
            for r in results
        ):
            raise ValueError("Invalid public delivered/initial label history.")
        for result in obs.delivered_results:
            if (
                result.candidate_id not in self.launched
                or result.delivered_at - self.launched[result.candidate_id] not in self.law
            ):
                raise ValueError("Delivered label lacks a public acceptance/time provenance.")
        if any(cid not in known or known[cid] != value for cid, value in self.seen.items()):
            raise ValueError("Delivered labels cannot disappear/change.")
        missing, pending = set(obs.missing_ids), set(obs.pending_ids)
        if (
            missing & known.keys()
            or pending & (known.keys() | missing)
            or not self.seen_missing <= missing
        ):
            raise ValueError("Public result/pending partitions overlap or regress.")
        if (
            not (pending | missing) <= self.launched.keys()
            or known.keys() | pending | missing != self.initial.keys() | self.launched.keys()
        ):
            raise ValueError("Public acceptance/result ledger does not reconcile.")
        if obs.slots != self.capacity - len(
            pending
        ) or obs.uncommitted != self.initial_budget - len(self.launched):
            raise ValueError("Public capacity or unit-cost commitments do not reconcile.")
        if dict(obs.cost_quotes) != {cid: 1 for cid in self.ids}:
            raise ValueError("This research prototype supports unit costs only.")
        unused = set(self.ids) - (known.keys() | pending | missing)
        expected = (
            unused if obs.slots > 0 and obs.uncommitted > 0 and obs.remaining_time > 0 else set()
        )
        if set(obs.eligible_ids) != expected:
            raise ValueError("Public eligibility changed outside the common feasibility rule.")
        ages = tuple(sorted((self.index[cid], obs.time - self.launched[cid]) for cid in pending))
        for _, age in ages:
            residual_law(self.law, age)
        self.seen, self.seen_missing, self.last_time = known, missing, obs.time
        used = frozenset(self.index[cid] for cid in known.keys() | pending | missing)
        return PublicState(obs.remaining_time, obs.uncommitted, used, ages), sorted(known.items())

    def record_acceptance(self, action, at_time):
        if (
            self.last_proposal != (tuple(action), at_time)
            or not action
            or any(cid in self.launched or cid in self.initial for cid in action)
        ):
            raise ValueError("Record only the latest successfully accepted public proposal.")
        self.launched.update({cid: at_time for cid in action})
        self.last_proposal = None

    def select(self, obs):
        started = time.perf_counter()
        state, known = self._public_state(obs)
        eligible = set(obs.eligible_ids)
        count = min(obs.slots, obs.uncommitted, len(eligible))
        trace = {
            "method": self.method,
            "time": obs.time,
            "model_trace": None,
            "fallback": None,
            "learned_controller_action": False,
            "learned_action_share": 0,
        }
        action = ()
        if not count:
            trace["forced_or_terminal"] = True
        elif self.method == "random":
            action = tuple(cid for cid in self.random_order if cid in eligible)[:count]
        elif self.method == "nearest_hit":
            hits = [self.index[cid] for cid, y in known if y]
            if not hits:
                action = tuple(cid for cid in self.random_order if cid in eligible)[:count]
                trace["fallback"] = "NO_DELIVERED_ACTIVE_RANDOM"
            else:

                def similarity(cid):
                    b = self.packed[self.index[cid]]
                    return max(
                        (b & self.packed[h]).bit_count() / (b | self.packed[h]).bit_count()
                        if b | self.packed[h]
                        else 1
                        for h in hits
                    )

                action = tuple(sorted(eligible, key=lambda cid: (-similarity(cid), cid))[:count])
        elif self.method == "fingerprint_rf":
            from sklearn.ensemble import RandomForestClassifier

            features = np.array([c.features for c in self.candidates], dtype=np.float32)
            if known:
                estimator = RandomForestClassifier(
                    n_estimators=128, max_features="sqrt", n_jobs=1, random_state=self.seed
                )
                estimator.fit(
                    features[[self.index[cid] for cid, _ in known]], [y for _, y in known]
                )
                probabilities = estimator.predict_proba(features)
                positive = (
                    list(estimator.classes_).index(True) if True in estimator.classes_ else None
                )
                scores = (
                    probabilities[:, positive] if positive is not None else np.zeros(len(self.ids))
                )
            else:
                scores = np.full(len(self.ids), 0.5)
                trace["fallback"] = "RF_EMPTY_HISTORY_CONSTANT_0_5"
            action = tuple(
                sorted(eligible, key=lambda cid: (-scores[self.index[cid]], cid))[:count]
            )
        else:
            if self.method == "frozen_greedy":
                model, model_trace = self.frozen_model, self.frozen_trace
            else:
                model, model_trace = fit_mixture(self.design, known, self.seed, self.hypotheses)
            trace["model_trace"] = model_trace
            if model_trace["fallback"]:
                trace["fallback"] = model_trace["fallback"]
            planner = RecoursePlanner(model, self.law, self.capacity)
            if self.method in ("greedy", "frozen_greedy", "parameter_ts", "cpe_scheduler"):
                scores = model.mu
                if self.method == "parameter_ts":
                    theta = sample_distribution(
                        tuple(enumerate(model.w)), uniform(model_trace["draw_seed"], "parameter-TS")
                    )
                    scores = model.p[theta]
                if self.method == "cpe_scheduler":
                    count, trace["planning"] = self.scheduler.choose_size(
                        state.horizon,
                        min(state.budget, len(eligible)),
                        tuple(age for _, age in state.pending),
                        len(obs.delivered_results),
                    )
                action = tuple(
                    self.ids[i]
                    for i in top_indices(scores, sorted(self.index[cid] for cid in eligible), count)
                )
            elif self.method == "greedy_rollout":
                actions = planner.actions(state, 4)
                values, detail = greedy_rollout_values(
                    planner, state, actions, model_trace["draw_seed"], 16, 16
                )
                best = 0
                for i, value in enumerate(values):
                    if value > values[best] + 1e-12:
                        best = i
                action = tuple(self.ids[i] for i in actions[best])
                trace["planning"] = {**detail, "root_values": values, "root_actions": actions}
            else:
                chosen, trace["planning"] = planner.choose(
                    state,
                    screened=self.method == "event_screened",
                    shortlist=4,
                    allow_wait=self.method != "no_wait",
                    suppress_pending_information=self.method == "no_pending_information",
                    timing_blind_tail=self.method == "timing_blind_tail",
                    count_budget_proxy=self.method == "count_ens",
                )
                action = tuple(self.ids[i] for i in chosen)
        if not set(action) <= eligible or len(action) > min(obs.slots, obs.uncommitted):
            raise AssertionError("Policy escaped the common public feasible action set.")
        if not action and count and not obs.pending_ids:
            raise AssertionError("Optional WAIT without a pending experiment.")
        trace.update(chosen=action, policy_seconds=time.perf_counter() - started)
        self.last_proposal = (action, obs.time) if action else None
        return action, trace
