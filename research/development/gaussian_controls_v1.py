"""Fixed Tanimoto Gaussian-surrogate controls using only public observations.

Gaussian regression on binary labels is an approximation, not a calibrated
Bernoulli posterior or a reproduction/theoretical guarantee of GP-BUCB.
"""

import time

import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Kernel

from .baselines import Selector

GP_METHODS = ("gp_mean", "gp_ucb_blind", "gp_ucb_pending")
GP_PARAMETERS = {
    "kernel": "binary Tanimoto, unit amplitude",
    "alpha": 0.1,
    "kappa": 1.0,
    "optimizer": None,
    "normalize_y": False,
    "batch": "one joint top-k ranking; no within-batch conditioning",
}


def tanimoto_gram(features):
    x = np.asarray(features, dtype=np.float64)
    if x.ndim != 2 or not np.isin(x, (0, 1)).all():
        raise ValueError("This kernel accepts binary public fingerprints only.")
    cross = x @ x.T
    count = x.sum(axis=1)
    union = count[:, None] + count[None, :] - cross
    return np.divide(cross, union, out=np.ones_like(cross), where=union != 0)


class IndexedTanimoto(Kernel):
    """Use an immutable public Gram matrix with sklearn's existing GP backend."""

    def __init__(self, gram):
        self.gram = gram

    def __call__(self, x, y=None, eval_gradient=False):
        a = np.asarray(x[:, 0], dtype=int)
        b = a if y is None else np.asarray(y[:, 0], dtype=int)
        k = self.gram[np.ix_(a, b)]
        if eval_gradient:
            return k, np.empty((*k.shape, 0))
        return k

    def diag(self, x):
        return np.diag(self.gram)[np.asarray(x[:, 0], dtype=int)]

    def is_stationary(self):
        return False


def pending_variance(covariance, n_eligible, alpha=0.1):
    """Schur conditioning on pending locations with no pending outcome input."""
    s = np.asarray(covariance)
    blind = np.diag(s)[:n_eligible].copy()
    var = blind.copy()
    if len(s) > n_eligible:
        cross = s[:n_eligible, n_eligible:]
        pp = s[n_eligible:, n_eligible:] + alpha * np.eye(len(s) - n_eligible)
        var -= np.einsum("ij,ji->i", cross, np.linalg.solve(pp, cross.T))
    if not np.isfinite(var).all() or np.any(var < -1e-8) or np.any(var > blind + 1e-8):
        raise ValueError("Invalid Gaussian variance reduction.")
    return np.maximum(var, 0)


class GaussianSelector(Selector):
    def __init__(self, method, seed):
        if method not in GP_METHODS:
            raise ValueError("Unknown Gaussian control.")
        super().__init__("greedy", seed)
        self.method = method
        self.indices = None
        self.gram = None
        self.stats["gaussian_covariance_calls"] = 0

    def choose(self, obs):
        started = time.perf_counter()
        ids = tuple(sorted(obs.eligible_ids))
        if not ids or obs.slots <= 0:
            raise ValueError("No feasible public decision.")
        self.stats["decisions"] += 1
        if self.indices is None:
            candidates = sorted(obs.candidates, key=lambda c: c.candidate_id)
            self.indices = {c.candidate_id: i for i, c in enumerate(candidates)}
            self.gram = tanimoto_gram([c.features for c in candidates])
            self.gram.flags.writeable = False
        known = sorted(obs.initial_results + obs.delivered_results, key=lambda r: r.candidate_id)
        signature = tuple((r.candidate_id, r.active) for r in known)
        if not self.initialized or signature != self.signature:
            self.initialized, self.signature = True, signature
            self.stats["fit_attempts"] += 1
            self.model = None
            if len({r.active for r in known}) == 2:
                t = time.perf_counter()
                self.model = GaussianProcessRegressor(
                    kernel=IndexedTanimoto(self.gram),
                    alpha=0.1,
                    optimizer=None,
                    normalize_y=False,
                    random_state=self.seed,
                )
                self.model.fit(
                    np.array([[self.indices[r.candidate_id]] for r in known]),
                    np.array([float(r.active) for r in known]),
                )
                self.stats["fit_wall_seconds"] += time.perf_counter() - t
                self.stats["fit_successes"] += 1
        fallback = "ONE_CLASS_RANDOM" if self.model is None else None
        means, stds, blind_stds = {}, {}, {}
        if fallback:
            scores = self._random_scores(ids, obs, signature)
        else:
            t = time.perf_counter()
            pending = tuple(sorted(obs.pending_ids)) if self.method == "gp_ucb_pending" else ()
            query = ids + pending
            mean, cov = self.model.predict(
                np.array([[self.indices[c]] for c in query]), return_cov=True
            )
            blind_var = np.maximum(np.diag(cov)[: len(ids)], 0)
            var = pending_variance(cov, len(ids))
            self.stats["prediction_calls"] += 1
            self.stats["gaussian_covariance_calls"] += 1
            self.stats["predict_wall_seconds"] += time.perf_counter() - t
            means = dict(zip(ids, map(float, mean[: len(ids)])))
            stds = dict(zip(ids, map(float, np.sqrt(var))))
            blind_stds = dict(zip(ids, map(float, np.sqrt(blind_var))))
            scores = {c: means[c] + (0 if self.method == "gp_mean" else stds[c]) for c in ids}
            if not all(np.isfinite(v) for v in scores.values()):
                raise ValueError("Nonfinite Gaussian acquisition score.")
        balance, chosen = obs.uncommitted, []
        costs = dict(obs.cost_quotes)
        for cid in sorted(ids, key=lambda c: (-scores[c], c)):
            if len(chosen) < obs.slots and costs[cid] <= balance:
                chosen.append(cid)
                balance -= costs[cid]
        if not chosen:
            raise ValueError("No feasible affordable acquisition.")
        self.stats["selected_requests"] += len(chosen)
        if fallback:
            self.stats["fallback_requests"] += len(chosen)
            self.stats["fallback_reasons"][fallback] += len(chosen)
        self.stats["selection_wall_seconds"] += time.perf_counter() - started
        trace = {
            "time": obs.time,
            "pending_ids": list(obs.pending_ids),
            "known_labels": len(known),
            "known_actives": sum(r.active for r in known),
            "fallback_reason": fallback,
            "fit_successes_so_far": self.stats["fit_successes"],
            "chosen": [
                {
                    "candidate_id": c,
                    "score": scores[c],
                    "gaussian_mean": means.get(c),
                    "gaussian_std": stds.get(c),
                    "blind_gaussian_std": blind_stds.get(c),
                    "predicted_probability": None,
                }
                for c in chosen
            ],
        }
        return tuple(chosen), trace
