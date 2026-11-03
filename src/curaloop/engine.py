"""Budget scheduler and append-only simulated experiment lifecycle."""

from dataclasses import asdict
from hashlib import sha256

from ._oracle import TruthStore, build_fixture
from .domain import (
    POLICIES,
    Event,
    ExperimentRequest,
    ExperimentResult,
    PolicyObservation,
    Scenario,
    Selection,
    digest,
)
from .policies import propose


class Campaign:
    """One independent run. Only delivery can turn hidden truth into public results."""

    def __init__(self, scenario: Scenario, policy: str):
        if policy not in POLICIES:
            raise ValueError("Unknown policy.")
        self.scenario = scenario
        self.policy = policy
        self.dataset, oracle, self.initial_results = build_fixture(scenario)
        self.__oracle: TruthStore = oracle
        self.run_id = "run-" + digest({"scenario": asdict(scenario), "policy": policy,
                                       "dataset": self.dataset.sha256})[:20]
        self._step = 0
        self._spent = 0
        self._pending: dict[str, ExperimentRequest] = {}
        self._requests: tuple[ExperimentRequest, ...] = ()
        self._results: tuple[ExperimentResult, ...] = ()
        self._events: tuple[Event, ...] = ()
        self._stopped = False
        self._emit("RUN_STARTED", explanation="Original synthetic fixture; no live laboratory.")
        for r in self.initial_results:
            self._emit("INITIAL_LABEL", compound_id=r.compound_id, request_id=r.request_id,
                       delivered_active=r.active, explanation=r.quality_flag)

    @property
    def step(self) -> int:
        return self._step

    @property
    def events(self) -> tuple[Event, ...]:
        return self._events

    @property
    def requests(self) -> tuple[ExperimentRequest, ...]:
        return self._requests

    @property
    def results(self) -> tuple[ExperimentResult, ...]:
        return self._results

    @property
    def pending(self) -> tuple[ExperimentRequest, ...]:
        return tuple(sorted(self._pending.values(), key=lambda r: (r.due_at_step, r.request_id)))

    @property
    def spent(self) -> int:
        return self._spent

    @property
    def reserved(self) -> int:
        return sum(r.cost_units for r in self._pending.values())

    @property
    def remaining(self) -> int:
        return self.scenario.budget_units - self.spent - self.reserved

    @property
    def done(self) -> bool:
        obs = self.observe()
        return not self.pending and (
            not obs.eligible_candidate_ids or self.remaining < self.scenario.assay_cost_units
        )

    def _emit(self, event_type: str, **kwargs) -> None:
        self._events += (Event(
            "1.1", f"{self.run_id}:e{len(self._events):05d}", self.run_id,
            self.scenario.scenario_id, self.policy, event_type, self.step,
            data_origin=self.dataset.data_origin, **kwargs,
        ),)

    def observe(self) -> PolicyObservation:
        used = {r.compound_id for r in self._requests} | {
            r.compound_id for r in self.initial_results
        }
        return PolicyObservation(
            "1.1", self.run_id, self.scenario.scenario_id, self.step,
            tuple(sorted(c.compound_id for c in self.dataset.candidates if c.compound_id not in used)),
            tuple(sorted((c.compound_id, c.features) for c in self.dataset.candidates)),
            self.initial_results + tuple(r for r in self.results if r.active is not None),
            tuple(sorted(r.compound_id for r in self.pending)), self.remaining, self.policy,
            self.scenario.seed, self.scenario.batch_size - len(self.pending),
            self.scenario.assay_cost_units,
            self.scenario.budget_units,
        )

    def suggest(self) -> tuple[Selection, ...]:
        if self.done:
            return ()
        return propose(self.observe())

    def submit(self, selections: tuple[Selection, ...]) -> tuple[ExperimentRequest, ...]:
        """Validate the whole batch first. Rejection changes only the public rejection log."""
        ids = [s.compound_id for s in selections]
        obs = self.observe()
        error = None
        if not ids:
            error = "No candidates selected."
        elif self._stopped:
            error = "Run already stopped."
        elif len(ids) != len(set(ids)):
            error = "Duplicate candidates in batch."
        elif not set(ids) <= set(obs.eligible_candidate_ids):
            error = "Unknown, already tested, initial, or pending candidate."
        elif len(ids) > obs.slots_available:
            error = "Batch capacity exhausted; advance simulated time."
        elif len(ids) * self.scenario.assay_cost_units > self.remaining:
            error = "Insufficient remaining budget."
        if error:
            self._emit("REQUEST_REJECTED", explanation=error)
            raise ValueError(error)
        batch_id = f"{self.run_id}:b{len(self.requests):04d}"
        requests = []
        for selection in selections:
            c = selection.compound_id
            jitter = int.from_bytes(sha256(
                f"delay:{self.scenario.seed}:{c}".encode()
            ).digest()[:4], "big") % (self.scenario.delay_jitter + 1)
            request = ExperimentRequest(
                f"{self.run_id}:q{len(self._requests):04d}", batch_id, c, self.dataset.assay_id,
                self.step, self.step + self.scenario.delay_steps + jitter,
                self.scenario.assay_cost_units, selection.explanation,
                selection.predicted_probability, selection.model_status,
            )
            self.__oracle.register(request)
            self._requests += (request,)
            self._pending[request.request_id] = request
            self._emit("REQUEST_ACCEPTED", compound_id=c, request_id=request.request_id,
                       due_at_step=request.due_at_step, cost_units=request.cost_units,
                       explanation=request.explanation)
            self._emit("RESULT_PENDING", compound_id=c, request_id=request.request_id,
                       due_at_step=request.due_at_step)
            requests.append(request)
        self._deliver_due()
        self._check_budget()
        return tuple(requests)

    def next_batch(self) -> tuple[ExperimentRequest, ...]:
        selections = self.suggest()
        return self.submit(selections) if selections else ()

    def _deliver_due(self) -> None:
        for request in self.pending:
            if request.due_at_step > self.step:
                continue
            result = self.__oracle.deliver(request.request_id, self.step)
            del self._pending[request.request_id]
            self._spent += request.cost_units
            self._results += (result,)
            self._emit("RESULT_MISSING" if result.active is None else "RESULT_DELIVERED",
                       compound_id=request.compound_id, request_id=request.request_id,
                       due_at_step=request.due_at_step, cost_units=request.cost_units,
                       delivered_active=result.active, explanation=result.quality_flag)

    def advance(self, steps: int = 1) -> None:
        if type(steps) is not int or not 1 <= steps <= 1000:
            raise ValueError("Advance steps must be an integer in [1, 1000].")
        if self._stopped:
            return
        for _ in range(steps):
            self._step += 1
            self._emit("CLOCK_ADVANCED")
            self._deliver_due()
        self._check_budget()

    def _check_budget(self) -> None:
        if min(self.spent, self.reserved, self.remaining) < 0 or (
            self.spent + self.reserved + self.remaining != self.scenario.budget_units
        ):
            raise RuntimeError("Budget invariant violated.")

    def finish(self) -> None:
        # At most one request per non-seed candidate, plus the maximum configured delay.
        limit = self.scenario.candidate_count * (self.scenario.delay_steps + self.scenario.delay_jitter + 2) + 2
        for _ in range(limit):
            if self.done:
                if not self._stopped:
                    self._emit("RUN_STOPPED", explanation="Budget or eligible candidate pool exhausted.")
                    self._stopped = True
                return
            obs = self.observe()
            if obs.slots_available and obs.eligible_candidate_ids and self.remaining >= obs.assay_cost_units:
                self.next_batch()
            elif self.pending:
                self.advance(max(1, min(r.due_at_step for r in self.pending) - self.step))
            else:
                raise RuntimeError("No valid simulation transition.")
        raise RuntimeError("Simulation safety limit reached.")
