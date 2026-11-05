"""Integer-time scheduler reference v1, not an application-engine replacement.

Only Observation crosses the policy boundary. Task owns private fixture outcomes;
snapshots reference its identity and retain only public events and action history.
"""

import hashlib
import json
import math
from dataclasses import asdict, dataclass, field
from typing import Any

VERSION = "curaloop.research.integer-events.v1"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def integer(value: int, minimum: int, name: str) -> None:
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}.")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    features: tuple[float, ...]

    def __post_init__(self) -> None:
        if (
            not isinstance(self.candidate_id, str)
            or not self.candidate_id
            or not isinstance(self.features, tuple)
            or not self.features
        ):
            raise ValueError("Candidate needs an ID and immutable public features.")
        if any(type(x) not in (int, float) or not math.isfinite(x) for x in self.features):
            raise ValueError("Public features must be finite numbers.")


@dataclass(frozen=True)
class Task:
    task_id: str
    candidates: tuple[Candidate, ...]
    durations: tuple[tuple[str, int], ...]
    costs: tuple[tuple[str, int], ...]
    _outcomes: tuple[tuple[str, bool], ...] = field(repr=False)
    missing_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if (
            not isinstance(self.task_id, str)
            or not self.task_id
            or not isinstance(self.candidates, tuple)
        ):
            raise ValueError("Task needs a versioned identity and immutable candidates.")
        ids = {c.candidate_id for c in self.candidates}
        if len(ids) != len(self.candidates):
            raise ValueError("Duplicate candidate IDs.")
        if len({len(c.features) for c in self.candidates}) > 1:
            raise ValueError("Feature dimensions differ.")
        for name, values in (
            ("duration", self.durations),
            ("cost", self.costs),
            ("outcome", self._outcomes),
        ):
            if not isinstance(values, tuple) or any(
                not isinstance(v, tuple) or len(v) != 2 for v in values
            ):
                raise ValueError("Task tables must be immutable pairs.")
            if len(values) != len(ids) or {v[0] for v in values} != ids:
                raise ValueError(f"{name} table must match candidates exactly.")
        for _, duration in self.durations:
            integer(duration, 0, "Duration")
        for _, cost in self.costs:
            integer(cost, 1, "Cost")
        if any(type(v) is not bool for _, v in self._outcomes):
            raise ValueError("Fixture outcomes must be Boolean.")
        if (
            not isinstance(self.missing_ids, tuple)
            or len(set(self.missing_ids)) != len(self.missing_ids)
            or not set(self.missing_ids) <= ids
        ):
            raise ValueError("Missing IDs must be unique task candidates.")

    @property
    def resource_sha256(self) -> str:
        # Resource identity is for evaluator restoration, never policy observation.
        return hashlib.sha256(canonical(asdict(self)).encode()).hexdigest()


@dataclass(frozen=True)
class Scenario:
    budget: int
    capacity: int
    deadline: int | None
    initial_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        integer(self.budget, 0, "Budget")
        integer(self.capacity, 1, "Capacity")
        if self.deadline is not None:
            integer(self.deadline, 0, "Deadline")
        if not isinstance(self.initial_ids, tuple) or len(set(self.initial_ids)) != len(
            self.initial_ids
        ):
            raise ValueError("Initial IDs must be an immutable unique sequence.")


@dataclass(frozen=True)
class Result:
    candidate_id: str
    active: bool
    delivered_at: int


@dataclass(frozen=True)
class Observation:
    time: int
    deadline: int | None
    remaining_time: int | None
    candidates: tuple[Candidate, ...]
    eligible_ids: tuple[str, ...]
    pending_ids: tuple[str, ...]
    initial_results: tuple[Result, ...]
    delivered_results: tuple[Result, ...]
    missing_ids: tuple[str, ...]
    cost_quotes: tuple[tuple[str, int], ...]
    slots: int
    uncommitted: int


@dataclass(frozen=True)
class Event:
    sequence: int
    time: int
    kind: str
    candidate_id: str | None = None
    request_id: str | None = None
    cost: int = 0
    active: bool | None = None


@dataclass(frozen=True)
class _Request:
    request_id: str
    candidate_id: str
    due: int
    cost: int


def reconcile(events: tuple[Event, ...], budget: int, at_time: int) -> dict:
    """Recalculate exposure, discoveries and left-step time area from public events."""
    integer(budget, 0, "Budget")
    integer(at_time, 0, "Endpoint time")
    pending: dict[str, tuple[str, int]] = {}
    used: set[str] = set()
    accepted_requests: set[str] = set()
    spent = hits = delivered = missing = seed_hits = area = previous_time = 0
    for n, e in enumerate(events):
        if e.sequence != n or type(e.time) is not int or not previous_time <= e.time <= at_time:
            raise ValueError("Invalid event order/time.")
        area += (e.time - previous_time) * hits
        previous_time = e.time
        if e.kind == "INITIAL_LABEL":
            if (
                type(e.active) is not bool
                or not e.candidate_id
                or e.candidate_id in used
                or e.cost != 0
                or e.time != 0
            ):
                raise ValueError("Invalid initial label.")
            used.add(e.candidate_id)
            seed_hits += int(e.active)
        elif e.kind == "REQUEST_ACCEPTED":
            if (
                not e.request_id
                or not e.candidate_id
                or e.request_id in accepted_requests
                or e.candidate_id in used
            ):
                raise ValueError("Duplicate or invalid accepted request.")
            integer(e.cost, 1, "Accepted cost")
            if e.active is not None:
                raise ValueError("A request cannot reveal an outcome.")
            pending[e.request_id] = (e.candidate_id, e.cost)
            accepted_requests.add(e.request_id)
            used.add(e.candidate_id)
        elif e.kind in ("RESULT_DELIVERED", "RESULT_MISSING"):
            if pending.get(e.request_id) != (e.candidate_id, e.cost):
                raise ValueError("Unmatched or duplicate settlement.")
            if e.kind == "RESULT_DELIVERED":
                if type(e.active) is not bool:
                    raise ValueError("Delivered result needs a Boolean label.")
                delivered += 1
                hits += int(e.active)
            else:
                if e.active is not None:
                    raise ValueError("A missing outcome cannot contain a label.")
                missing += 1
            spent += pending.pop(e.request_id)[1]
        elif e.kind != "TIME_ADVANCED" or e.active is not None or e.cost:
            raise ValueError("Unsupported event or hidden label.")
        if spent + sum(v[1] for v in pending.values()) > budget:
            raise ValueError("Event ledger overspends budget.")
    area += (at_time - previous_time) * hits
    reserved = sum(v[1] for v in pending.values())
    return {
        "time": at_time,
        "new_hits": hits,
        "seed_hits": seed_hits,
        "delivered": delivered,
        "missing": missing,
        "pending": len(pending),
        "spent": spent,
        "reserved": reserved,
        "uncommitted": budget - spent - reserved,
        "accepted_exposure": spent + reserved,
        "time_discovery_area": area,
    }


class Campaign:
    """Trusted scheduler/oracle. Policies receive observe(), never this object."""

    def __init__(self, task: Task, scenario: Scenario):
        ids = {c.candidate_id for c in task.candidates}
        if not set(scenario.initial_ids) <= ids or set(scenario.initial_ids) & set(
            task.missing_ids
        ):
            raise ValueError("Initial labels must be known, nonmissing task candidates.")
        self._task = task
        self.scenario = scenario
        self.time = 0
        self._pending: dict[str, _Request] = {}
        self._used = set(scenario.initial_ids)
        self._events: list[Event] = []
        self._journal: list[dict] = []
        self._request_count = 0
        for cid in sorted(scenario.initial_ids):
            self._emit("INITIAL_LABEL", candidate_id=cid, active=dict(task._outcomes)[cid])

    def _emit(self, kind: str, **fields) -> None:
        self._events.append(Event(len(self._events), self.time, kind, **fields))

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    @property
    def metrics(self) -> dict:
        return reconcile(self.events, self.scenario.budget, self.time)

    def observe(self) -> Observation:
        def results(kind):
            return tuple(
                Result(e.candidate_id, e.active, e.time) for e in self._events if e.kind == kind
            )

        money = self.metrics
        costs = dict(self._task.costs)
        slots = self.scenario.capacity - len(self._pending)
        at_deadline = self.scenario.deadline is not None and self.time >= self.scenario.deadline
        eligible = tuple(
            sorted(
                c.candidate_id
                for c in self._task.candidates
                if c.candidate_id not in self._used
                and slots > 0
                and costs[c.candidate_id] <= money["uncommitted"]
                and not at_deadline
            )
        )
        return Observation(
            self.time,
            self.scenario.deadline,
            None if self.scenario.deadline is None else self.scenario.deadline - self.time,
            tuple(sorted(self._task.candidates, key=lambda c: c.candidate_id)),
            eligible,
            tuple(sorted(self._pending)),
            results("INITIAL_LABEL"),
            results("RESULT_DELIVERED"),
            tuple(e.candidate_id for e in self._events if e.kind == "RESULT_MISSING"),
            tuple(sorted(self._task.costs)),
            slots,
            money["uncommitted"],
        )

    @property
    def done(self) -> bool:
        if self.scenario.deadline is not None and self.time >= self.scenario.deadline:
            return True
        return not self._pending and not self.observe().eligible_ids

    def submit(self, candidate_ids: tuple[str, ...]) -> None:
        if (
            not isinstance(candidate_ids, tuple)
            or not candidate_ids
            or len(set(candidate_ids)) != len(candidate_ids)
        ):
            raise ValueError("Submit a nonempty unique tuple of candidate IDs.")
        obs = self.observe()
        if len(candidate_ids) > obs.slots or not set(candidate_ids) <= set(obs.eligible_ids):
            raise ValueError(
                "Unknown, seeded, used, pending, unaffordable or capacity/deadline-infeasible action."
            )
        costs, durations = dict(self._task.costs), dict(self._task.durations)
        if sum(costs[cid] for cid in candidate_ids) > obs.uncommitted:
            raise ValueError("Batch exceeds uncommitted budget.")
        # Validation is complete before any acceptance, time, or cost mutation.
        for cid in candidate_ids:
            request = _Request(
                f"r{self._request_count:06d}", cid, self.time + durations[cid], costs[cid]
            )
            self._request_count += 1
            self._pending[cid] = request
            self._used.add(cid)
            self._emit(
                "REQUEST_ACCEPTED",
                candidate_id=cid,
                request_id=request.request_id,
                cost=request.cost,
            )
        self._journal.append({"action": "submit", "ids": list(candidate_ids)})
        self._deliver_due()
        self.metrics  # Reconcile every accepted transition, including zero-duration batches.

    def _deliver_due(self) -> None:
        # No policy callback occurs between any of this timestamp's settlements.
        due = sorted(
            (r for r in self._pending.values() if r.due <= self.time), key=lambda r: r.request_id
        )
        outcomes = dict(self._task._outcomes)
        for request in due:
            missing = request.candidate_id in self._task.missing_ids
            self._emit(
                "RESULT_MISSING" if missing else "RESULT_DELIVERED",
                candidate_id=request.candidate_id,
                request_id=request.request_id,
                cost=request.cost,
                active=None if missing else outcomes[request.candidate_id],
            )
            del self._pending[request.candidate_id]

    def advance_to(self, target: int) -> None:
        integer(target, 0, "Target time")
        if target < self.time or (
            self.scenario.deadline is not None and target > self.scenario.deadline
        ):
            raise ValueError("Time cannot reverse or pass the frozen deadline.")
        if target == self.time:
            return
        self._journal.append({"action": "advance_to", "time": target})
        while self._pending and min(r.due for r in self._pending.values()) <= target:
            self.time = min(r.due for r in self._pending.values())
            self._emit("TIME_ADVANCED")
            self._deliver_due()
        if self.time != target:
            self.time = target
            self._emit("TIME_ADVANCED")
        self.metrics

    def wait(self) -> bool:
        if not self._pending or self.done:
            return False
        target = min(r.due for r in self._pending.values())
        if self.scenario.deadline is not None:
            target = min(target, self.scenario.deadline)
        self.advance_to(target)
        return True

    def snapshot(self) -> dict:
        # Canonical JSON roundtrip returns independent primitive values.
        return json.loads(
            canonical(
                {
                    "schema_version": VERSION,
                    "resource_sha256": self._task.resource_sha256,
                    "scenario": asdict(self.scenario),
                    "journal": self._journal,
                    "events": [asdict(e) for e in self._events],
                    "metrics": self.metrics,
                }
            )
        )

    @classmethod
    def restore(cls, task: Task, snapshot: dict) -> "Campaign":
        """Replay public actions against an explicitly supplied exact resource."""
        try:
            if (
                snapshot["schema_version"] != VERSION
                or snapshot["resource_sha256"] != task.resource_sha256
            ):
                raise ValueError("Snapshot schema or task resource identity differs.")
            cfg = dict(snapshot["scenario"])
            cfg["initial_ids"] = tuple(cfg["initial_ids"])
            restored = cls(task, Scenario(**cfg))
            for action in snapshot["journal"]:
                if (
                    set(action) == {"action", "ids"}
                    and action["action"] == "submit"
                    and isinstance(action["ids"], list)
                ):
                    restored.submit(tuple(action["ids"]))
                elif set(action) == {"action", "time"} and action["action"] == "advance_to":
                    restored.advance_to(action["time"])
                else:
                    raise ValueError("Unsupported restoration action.")
            if canonical(restored.snapshot()) != canonical(snapshot):
                raise ValueError("Snapshot does not reconcile with its public action history.")
            return restored
        except (KeyError, TypeError, AttributeError, OverflowError) as error:
            raise ValueError("Malformed research snapshot.") from error


def keyed_duration(
    task_id: str, seed: int, candidate_id: str, assay_type: str, values: tuple[int, ...] = (1, 2, 4)
) -> int:
    """Label-independent common random numbers, stable across policy request order."""
    integer(seed, 0, "Schedule seed")
    if not values or not isinstance(values, tuple):
        raise ValueError("Specify an immutable nonempty duration distribution.")
    for value in values:
        integer(value, 0, "Duration value")
    if not all(isinstance(x, str) and x for x in (task_id, candidate_id, assay_type)):
        raise ValueError("Schedule keys must be nonempty strings.")
    key = canonical([task_id, seed, candidate_id, assay_type]).encode()
    return values[int.from_bytes(hashlib.sha256(key).digest(), "big") % len(values)]
