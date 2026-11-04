"""Finite-world dispatch/wait planning with an independently testable relaxation.

Worlds are hypothetical posterior scenarios, not the evaluator's private Task.
Bounds apply exactly to this finite model, not to an underlying biological law.
All costs are one, durations strictly positive, and rewards are delivered labels.
"""

from dataclasses import dataclass
from itertools import combinations
from time import perf_counter


@dataclass(frozen=True)
class State:
    time: int
    budget: int
    used: int
    pending: tuple[tuple[int, int], ...]  # candidate index, public launch time
    completed: int = 0  # new campaign results already delivered, excluding seeds


class FinitePlanner:
    def __init__(self, labels, durations, capacity, deadline):
        self.labels = tuple(tuple(row) for row in labels)
        self.durations = tuple(tuple(row) for row in durations)
        self.capacity, self.deadline = capacity, deadline
        if not self.labels or len(self.labels) != len(self.durations):
            raise ValueError("World tables must be nonempty and paired.")
        self.n = len(self.labels[0])
        if not self.n or any(len(r) != self.n for r in self.labels + self.durations):
            raise ValueError("Rectangular, nonempty world tables required.")
        if any(type(x) is not bool for row in self.labels for x in row):
            raise ValueError("Labels must be Boolean, not missing/continuous scores.")
        if any(type(d) is not int or d < 1 for row in self.durations for d in row):
            raise ValueError("Only strictly positive integer duration support is supported.")
        if type(capacity) is not int or capacity < 1 or deadline < 0:
            raise ValueError("Invalid capacity/deadline.")
        self.full = (1 << len(self.labels)) - 1
        self.bits = tuple(
            sum(int(self.labels[w][c]) << w for w in range(len(self.labels))) for c in range(self.n)
        )
        self.nodes = 0
        self.cache = {}

    @staticmethod
    def worlds(mask):
        while mask:
            bit = mask & -mask
            yield bit.bit_length() - 1
            mask ^= bit

    def rank(self, state, mask):
        return sorted(
            (c for c in range(self.n) if not state.used >> c & 1),
            key=lambda c: (-(self.bits[c] & mask).bit_count(), c),
        )

    def actions(self, state, mask, shortlist=None):
        count = min(self.capacity - len(state.pending), state.budget)
        ids = self.rank(state, mask)
        if shortlist is not None:
            ids = ids[:shortlist]
        actions = [()] if state.pending else []
        if state.time < self.deadline:
            actions += [a for k in range(1, min(count, len(ids)) + 1) for a in combinations(ids, k)]
        return actions

    def launch(self, state, action):
        if (
            len(set(action)) != len(action)
            or len(action) > state.budget
            or len(action) + len(state.pending) > self.capacity
            or any(c < 0 or c >= self.n or state.used >> c & 1 for c in action)
            or (action and state.time >= self.deadline)
        ):
            raise ValueError("Infeasible action.")
        if not action and not state.pending:
            raise ValueError("WAIT needs a pending result.")
        return State(
            state.time,
            state.budget - len(action),
            state.used | sum(1 << c for c in action),
            tuple(sorted(state.pending + tuple((c, state.time) for c in action))),
            state.completed,
        )

    def branches(self, state, mask):
        """Group worlds by the next PUBLIC timestamp and delivered labels.

        No continuation is chosen separately for each private world. Observing
        a timestamp also conditions durations; pending clocks are never reset.
        """
        groups = {}
        for w in self.worlds(mask):
            next_time = min(
                (start + self.durations[w][c] for c, start in state.pending), default=self.deadline
            )
            if next_time > self.deadline:
                key = (self.deadline, ())
            else:
                results = tuple(
                    (c, self.labels[w][c])
                    for c, start in state.pending
                    if start + self.durations[w][c] == next_time
                )
                key = (next_time, results)
            groups[key] = groups.get(key, 0) | (1 << w)
        for (t, results), submask in sorted(groups.items()):
            delivered = {c for c, _ in results}
            child = State(
                t,
                state.budget,
                state.used,
                tuple(p for p in state.pending if p[0] not in delivered),
                state.completed + len(results),
            )
            yield submask.bit_count() / mask.bit_count(), sum(y for _, y in results), child, submask

    def after(self, state, action, mask, optimal=False, metric="hits"):
        launched = self.launch(state, action)
        immediate = state.completed * len(action) if metric == "cpe" else 0
        value = float(immediate)
        for probability, hits, child, submask in self.branches(launched, mask):
            gain = hits if metric == "hits" else 0
            value += probability * (gain + self.value(child, submask, optimal, metric))
        return value

    def value(self, state, mask, optimal=False, metric="hits"):
        key = (state, mask, optimal, metric)
        if key in self.cache:
            return self.cache[key]
        self.nodes += 1
        if state.time >= self.deadline or (not state.pending and not state.budget):
            answer = 0.0
        elif optimal:
            choices = self.actions(state, mask)
            answer = max((self.after(state, a, mask, True, metric) for a in choices), default=0.0)
        else:
            count = min(self.capacity - len(state.pending), state.budget)
            action = tuple(self.rank(state, mask)[:count])
            answer = (
                self.after(state, action, mask, False, metric) if action or state.pending else 0.0
            )
        self.cache[key] = answer
        return answer

    def upper(self, state, action, mask, kind="content"):
        launched = self.launch(state, action)
        if kind == "cardinality":
            return float(
                len(launched.pending) + min(launched.budget, self.n - launched.used.bit_count())
            )
        if kind != "content":
            raise ValueError("Unknown upper bound.")
        total = 0.0
        for w in self.worlds(mask):
            durations, labels = self.durations[w], self.labels[w]
            due = [(c, start + durations[c]) for c, start in launched.pending]
            direct = sum(labels[c] for c, finish in due if finish <= self.deadline)
            horizon = self.deadline - launched.time
            # Occupied processing is mandatory even for inactive/late pending jobs.
            work = self.capacity * horizon - sum(
                min(horizon, max(0, finish - launched.time)) for _, finish in due
            )
            earliest = launched.time if len(due) < self.capacity else min(t for _, t in due)
            feasible = sorted(
                durations[c]
                for c in range(self.n)
                if not launched.used >> c & 1
                and labels[c]
                and durations[c] <= self.deadline - earliest
            )
            count = 0
            for d in feasible:
                if count == launched.budget or d > work:
                    break
                work -= d
                count += 1
            total += direct + count
        return total / mask.bit_count()

    def choose(self, state, shortlist=3, bound=None, metric="hits"):
        actions = self.actions(state, self.full, shortlist)
        if not actions:
            return (), {"actions": [], "nodes": 0, "pruned": 0, "gap": 0.0}
        greedy = tuple(
            self.rank(state, self.full)[: min(self.capacity - len(state.pending), state.budget)]
        )
        # Baseline first establishes a real feasible lower bound. Ties keep it.
        actions.sort(key=lambda a: (a != greedy, -len(a), a))
        best, best_value = actions[0], float("-inf")
        traces, pruned = [], 0
        bound_seconds = rollout_seconds = 0.0
        for action in actions:
            started = perf_counter()
            upper = self.upper(state, action, self.full, bound) if bound else None
            bound_seconds += perf_counter() - started
            if upper is not None and upper < best_value - 1e-12:
                pruned += 1
                traces.append({"action": action, "upper": upper, "lower": None, "pruned": True})
                continue
            started = perf_counter()
            lower = self.after(state, action, self.full, metric=metric)
            rollout_seconds += perf_counter() - started
            if upper is not None and lower > upper + 1e-9:
                raise AssertionError("Invalid planning upper bound.")
            if lower > best_value + 1e-12:
                best, best_value = action, lower
            traces.append({"action": action, "upper": upper, "lower": lower, "pruned": False})
        upper_values = [r["upper"] for r in traces if r["upper"] is not None]
        return best, {
            "actions": traces,
            "nodes": self.nodes,
            "pruned": pruned,
            "chosen_lower": best_value,
            "bound_seconds": bound_seconds,
            "rollout_seconds": rollout_seconds,
            "gap": max(upper_values) - best_value if upper_values else None,
            "gap_scope": "finite-model shortlisted root actions; all-action continuation relaxation",
        }
