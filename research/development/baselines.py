"""Fixed acquisition controls consuming public Observation only, never a Task."""

import hashlib
import json
import random
import time
from collections import Counter

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from research.event_time import Observation

METHODS = ("random", "frozen_greedy", "greedy", "nearest_hit", "diversity", "pending_penalty")


def tanimoto(a: int, b: int) -> float:
    union = (a | b).bit_count()
    return (a & b).bit_count() / union if union else 1.0


class Selector:
    """One instance per campaign; no fitted state is shared across methods/runs."""

    def __init__(self, method: str, seed: int, pending_lambda: float = 0.2):
        if method not in METHODS or not 0 <= pending_lambda <= 1:
            raise ValueError("Unknown method or invalid development coefficient.")
        self.method, self.seed, self.pending_lambda = method, seed, pending_lambda
        self.model = None
        self.initialized = False
        self.signature = None
        self.features = None
        self.packed = None
        self.stats = {
            "fit_attempts": 0,
            "fit_successes": 0,
            "prediction_calls": 0,
            "decisions": 0,
            "fit_wall_seconds": 0.0,
            "predict_wall_seconds": 0.0,
            "selection_wall_seconds": 0.0,
            "fallback_requests": 0,
            "fallback_reasons": Counter(),
            "selected_requests": 0,
            "learned_controller_requests": 0,
            "controller_fallback_requests": 0,
            "controller_status": "NOT_APPLICABLE_FIXED_ACQUISITION",
        }

    def _random_scores(self, ids, obs, signature):
        # No method name: matched Greedy/penalty arms share one-class fallback draws.
        key = json.dumps(
            [self.seed, obs.time, signature, self.stats["decisions"]], sort_keys=True
        ).encode()
        rng = random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))
        order = list(ids)
        rng.shuffle(order)
        return {cid: float(len(ids) - i) for i, cid in enumerate(order)}

    def choose(self, obs: Observation) -> tuple[tuple[str, ...], dict]:
        start = time.perf_counter()
        ids = tuple(sorted(obs.eligible_ids))
        if not ids or obs.slots <= 0:
            raise ValueError("Call selector only at a feasible public decision.")
        self.stats["decisions"] += 1
        if self.features is None:
            self.features = {
                c.candidate_id: np.asarray(c.features, dtype=np.float64) for c in obs.candidates
            }
            self.packed = {
                cid: sum(1 << i for i, value in enumerate(x) if value > 0.5)
                for cid, x in self.features.items()
            }
        known = sorted(obs.initial_results + obs.delivered_results, key=lambda r: r.candidate_id)
        signature = tuple((r.candidate_id, r.active) for r in known)
        fallback = None
        probabilities = {}
        if self.method == "random":
            scores = self._random_scores(ids, obs, signature)
        elif self.method in ("nearest_hit", "diversity"):
            reference = (
                [r.candidate_id for r in known if r.active]
                if self.method == "nearest_hit"
                else [r.candidate_id for r in known]
            )
            if not reference:
                fallback = (
                    "NO_DELIVERED_ACTIVE"
                    if self.method == "nearest_hit"
                    else "NO_REVEALED_REFERENCE"
                )
                scores = self._random_scores(ids, obs, signature)
            else:
                similarities = {
                    cid: max(tanimoto(self.packed[cid], self.packed[r]) for r in reference)
                    for cid in ids
                }
                scores = (
                    similarities
                    if self.method == "nearest_hit"
                    else {cid: 1 - s for cid, s in similarities.items()}
                )
        else:
            should_fit = not self.initialized or (
                self.method != "frozen_greedy" and self.signature != signature
            )
            if should_fit:
                self.initialized = True
                self.signature = signature
                self.stats["fit_attempts"] += 1
                if len({r.active for r in known}) < 2:
                    self.model = None
                else:
                    self.model = make_pipeline(
                        StandardScaler(),
                        LogisticRegression(
                            solver="liblinear", C=1.0, max_iter=500, random_state=self.seed
                        ),
                    )
                    t = time.perf_counter()
                    self.model.fit(
                        np.asarray([self.features[r.candidate_id] for r in known]),
                        [r.active for r in known],
                    )
                    self.stats["fit_wall_seconds"] += time.perf_counter() - t
                    self.stats["fit_successes"] += 1
            if self.model is None:
                fallback = (
                    "FROZEN_INITIAL_ONE_CLASS"
                    if self.method == "frozen_greedy"
                    else "ONE_CLASS_RANDOM"
                )
                scores = self._random_scores(ids, obs, signature)
            else:
                t = time.perf_counter()
                values = self.model.predict_proba(np.asarray([self.features[cid] for cid in ids]))[
                    :, 1
                ]
                self.stats["predict_wall_seconds"] += time.perf_counter() - t
                self.stats["prediction_calls"] += 1
                if not np.isfinite(values).all():
                    raise ValueError("Nonfinite predictor scores.")
                probabilities = dict(zip(ids, map(float, values)))
                scores = dict(probabilities)
                if self.method == "pending_penalty" and obs.pending_ids:
                    for cid in ids:
                        scores[cid] -= self.pending_lambda * max(
                            tanimoto(self.packed[cid], self.packed[p]) for p in obs.pending_ids
                        )
        ranking = sorted(ids, key=lambda cid: (-scores[cid], cid))
        chosen = []
        balance = obs.uncommitted
        costs = dict(obs.cost_quotes)
        for cid in ranking:
            if len(chosen) < obs.slots and costs[cid] <= balance:
                chosen.append(cid)
                balance -= costs[cid]
        if not chosen:
            raise ValueError("No affordable request despite a feasible observation.")
        self.stats["selected_requests"] += len(chosen)
        if fallback:
            self.stats["fallback_requests"] += len(chosen)
            self.stats["fallback_reasons"][fallback] += len(chosen)
        self.stats["selection_wall_seconds"] += time.perf_counter() - start
        trace = {
            "time": obs.time,
            "pending_ids": list(obs.pending_ids),
            "known_labels": len(known),
            "known_actives": sum(r.active for r in known),
            "fallback_reason": fallback,
            "chosen": [
                {
                    "candidate_id": cid,
                    "score": scores[cid],
                    "predicted_probability": probabilities.get(cid),
                }
                for cid in chosen
            ],
            "fit_successes_so_far": self.stats["fit_successes"],
        }
        return tuple(chosen), trace

    def report(self):
        return {**self.stats, "fallback_reasons": dict(self.stats["fallback_reasons"])}
