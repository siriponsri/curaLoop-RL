"""One public-event label recourse followed by full-budget fixed-list search."""

from dataclasses import dataclass
from itertools import combinations

import numpy as np

from .mixture import Mixture
from .queue import completion_weights, next_events, residual_law, validate_law


@dataclass(frozen=True)
class PublicState:
    horizon: int
    budget: int
    used: frozenset[int]
    pending: tuple[tuple[int, int], ...]  # candidate index, public elapsed age


class RecoursePlanner:
    def __init__(self, model: Mixture, law, capacity):
        self.model = model
        self.law = validate_law(law)
        if type(capacity) is not int or not 1 <= capacity <= 2:
            raise ValueError("Constructed prototype supports one or two assay workers.")
        self.capacity = capacity
        self.n = model.p.shape[1]

    def validate(self, state):
        if any(type(x) is not int or x < 0 for x in (state.horizon, state.budget)):
            raise ValueError("Nonnegative integer horizon/budget required.")
        if not isinstance(state.used, frozenset) or any(
            type(i) is not int or not 0 <= i < self.n for i in state.used
        ):
            raise ValueError("Invalid immutable accepted/observed index set.")
        if len(state.pending) > self.capacity or len({i for i, _ in state.pending}) != len(
            state.pending
        ):
            raise ValueError("Invalid pending capacity/identity.")
        for i, age in state.pending:
            if i not in state.used:
                raise ValueError("Every pending candidate must already be accepted.")
            residual_law(self.law, age)

    def rank(self, ids):
        return sorted(ids, key=lambda i: (-self.model.mu[i], i))

    def actions(self, state, shortlist=4, allow_wait=True):
        self.validate(state)
        if not state.horizon:
            return []
        ids = [i for i in range(self.n) if i not in state.used]
        slots = min(self.capacity - len(state.pending), state.budget, len(ids))
        exploit = self.rank(ids)
        if shortlist is None:
            chosen = ids
        else:
            if type(shortlist) is not int or shortlist < self.capacity:
                raise ValueError("Shortlist must retain the full greedy root action.")
            eps = 1e-15
            p = np.clip(self.model.p, eps, 1 - eps)
            mean = np.clip(self.model.mu, eps, 1 - eps)

            def entropy(x):
                return -x * np.log(x) - (1 - x) * np.log1p(-x)

            information = entropy(mean) - self.model.w @ entropy(p)
            info = sorted(ids, key=lambda i: (-information[i], i))
            chosen = list(exploit[: self.capacity])
            for i in info + exploit:
                if len(chosen) >= shortlist:
                    break
                if i not in chosen:
                    chosen.append(i)
            chosen = sorted(chosen)
        actions = [()] if allow_wait and state.pending else []
        actions += [
            a for size in range(1, min(slots, len(chosen)) + 1) for a in combinations(chosen, size)
        ]
        greedy = tuple(sorted(exploit[:slots]))
        actions.sort(key=lambda action: (action != greedy, -len(action), action))
        return actions

    def validate_action(self, state, action):
        self.validate(state)
        action = tuple(action)
        if (
            len(set(action)) != len(action)
            or len(action) > state.budget
            or len(action) + len(state.pending) > self.capacity
            or any(type(i) is not int or not 0 <= i < self.n or i in state.used for i in action)
            or (action and not state.horizon)
            or (not action and not state.pending)
        ):
            raise ValueError("Infeasible root action.")

    def _root(
        self,
        state,
        action,
        suppress_pending_information=False,
        timing_blind_tail=False,
        count_budget_proxy=False,
    ):
        if count_budget_proxy and timing_blind_tail:
            raise ValueError("Count-budget and timing-blind-tail proxies are separate arms.")
        action = tuple(action)
        self.validate_action(state, action)
        pending = tuple(sorted(state.pending + tuple((i, 0) for i in action)))
        used = state.used | frozenset(action)
        eligible = tuple(i for i in range(self.n) if i not in used)
        budget = min(state.budget - len(action), len(eligible))
        # Every accepted job contributes direct reward once, even with no tail.
        direct = sum(
            self.model.mu[i]
            * (
                1.0
                if count_budget_proxy
                else sum(
                    p for duration, p in residual_law(self.law, age) if duration <= state.horizon
                )
            )
            for i, age in pending
        )
        rows, probabilities = [], []
        if not budget or not state.horizon:
            return direct, rows, probabilities
        old_pending = {i for i, _ in state.pending}
        for delta, delivered, remaining, event_probability in next_events(
            self.law, pending, max(self.law) if count_budget_proxy else state.horizon
        ):
            # No-delivery censoring is terminal. It NEVER releases reservations.
            if not delivered or (not count_budget_proxy and delta >= state.horizon):
                continue
            omega = (
                (1.0,) * budget
                if timing_blind_tail or count_budget_proxy
                else completion_weights(
                    self.law,
                    state.horizon - delta,
                    self.capacity,
                    tuple(age for _, age in remaining),
                    budget,
                )
            )
            if not any(omega):
                continue
            conditioned = tuple(
                i for i in delivered if not suppress_pending_information or i not in old_pending
            )
            for _, label_probability, q in self.model.label_branches(conditioned):
                rows.append((q, eligible, omega))
                probabilities.append(event_probability * label_probability)
        return float(direct), rows, probabilities

    def evaluate_actions(self, state, actions, screened=False, **ablations):
        rows, owners, probabilities = [], [], []
        values = []
        for index, action in enumerate(actions):
            direct, branches, branch_probabilities = self._root(state, action, **ablations)
            values.append(direct)
            rows.extend(branches)
            owners.extend([index] * len(branches))
            probabilities.extend(branch_probabilities)
        if screened:
            tails, diagnostics = self.model.screened_batch(rows)
        else:
            tails, diagnostics = self.model.dense_batch(rows)
        for owner, probability, tail in zip(owners, probabilities, tails):
            values[owner] += probability * tail
        return values, {
            "branches": len(rows),
            "branch_diagnostics": diagnostics,
            "objective": (
                "expected_additional_count_budget_PROXY"
                if ablations.get("count_budget_proxy")
                else "deadline_direct_plus_count_tail_PROXY"
                if ablations.get("timing_blind_tail")
                else "expected_additional_delivered_positives_fixed_list_recourse"
            ),
            "ablations": ablations,
            "certificate_scope": "Finite-mixture supplied-root objective only; timing-blind is a proxy; not unrestricted optimal planning or whole-campaign H(T)",
        }

    def choose(self, state, screened=False, shortlist=4, allow_wait=True, **ablations):
        actions = self.actions(state, shortlist, allow_wait)
        if not actions:
            return (), {"forced_or_terminal": True, "actions": [], "gap": 0.0}
        values, trace = self.evaluate_actions(state, actions, screened, **ablations)
        best = 0
        for i, value in enumerate(values):
            if value > values[best] + 1e-12:
                best = i
        return actions[best], {
            **trace,
            "actions": [{"action": a, "value": v} for a, v in zip(actions, values)],
            "selected_value": values[best],
            "gap": max(values) - values[best],
            "numerical_tie_tolerance": 1e-12,
            "shortlist_relative": shortlist is not None,
        }
