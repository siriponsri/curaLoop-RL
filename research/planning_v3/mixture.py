"""Conditional finite-parameter label mixtures and certified rank screening.

No private assay resource is accepted here. All certificates concern this
immutable finite approximation, rather than a biological calibration claim.
"""

from itertools import product

import numpy as np

TOL = 1e-12


def normalized(weights):
    result = np.array(weights, dtype=float, copy=True)
    if (
        result.ndim != 1
        or not len(result)
        or not np.isfinite(result).all()
        or (result < 0).any()
        or abs(result.sum() - 1) > 1e-10
    ):
        raise ValueError("Mixture weights must be finite, nonnegative and normalized.")
    result /= result.sum()
    result.setflags(write=False)
    return result


def weighted_top(scores, omega):
    """Optimized partial selection followed by sorting retained ranks."""
    scores, omega = np.asarray(scores), np.asarray(omega)
    if (
        not np.isfinite(scores).all()
        or not np.isfinite(omega).all()
        or (omega < 0).any()
        or np.any(omega[1:] > omega[:-1] + TOL)
    ):
        raise ValueError("Finite scores/nonnegative nonincreasing queue weights required.")
    k = min(len(scores), len(omega), int(np.count_nonzero(omega > 0)))
    if not k:
        return 0.0
    selected = np.partition(scores, len(scores) - k)[-k:]
    selected.sort()
    return float(np.dot(omega[:k], selected[::-1]))


def top_indices(scores, eligible, count):
    """Partial-select, then sort retained candidates with deterministic ID ties."""
    ids = np.asarray(eligible, dtype=int)
    count = min(count, len(ids))
    if count <= 0:
        return ()
    values = np.asarray(scores)[ids]
    if count < len(ids):
        cutoff = np.partition(values, len(ids) - count)[len(ids) - count]
        strict = ids[values > cutoff]
        ties = np.sort(ids[values == cutoff])[: count - len(strict)]
        ids = np.concatenate((strict, ties))
    order = np.lexsort((ids, -np.asarray(scores)[ids]))
    return tuple(int(i) for i in ids[order][:count])


class Mixture:
    def __init__(self, probabilities, weights):
        self.p = np.array(probabilities, dtype=float, copy=True)
        self.w = normalized(weights)
        if (
            self.p.ndim != 2
            or self.p.shape[0] != len(self.w)
            or not self.p.shape[1]
            or not np.isfinite(self.p).all()
            or (self.p < 0).any()
            or (self.p > 1).any()
        ):
            raise ValueError("Rectangular parameter-by-candidate probabilities in[0,1] required.")
        self.p.setflags(write=False)
        self.mu = self.w @ self.p
        self.mu.setflags(write=False)
        self._sigma = self._span = None

    def prepare_screening(self):
        # Dense/Greedy references never pay for bounds they do not use.
        if self._sigma is None:
            self._sigma = np.sqrt(self.w @ ((self.p - self.mu) ** 2))
            reachable = self.p[self.w > 0]
            self._span = reachable.max(axis=0) - reachable.min(axis=0)
            self._sigma.setflags(write=False)
            self._span.setflags(write=False)

    def _q(self, weights):
        q = normalized(weights)
        if len(q) != len(self.w) or np.any(q[self.w == 0] != 0):
            raise ValueError("Conditional mixture must stay on positive prior support.")
        return q

    def label_branches(self, ids):
        ids = tuple(ids)
        if len(ids) != len(set(ids)) or any(
            type(i) is not int or not 0 <= i < self.p.shape[1] for i in ids
        ):
            raise ValueError("Unique eligible observation indices required.")
        branches = []
        with np.errstate(divide="ignore"):
            log_prior = np.log(self.w)
            for labels in product((0, 1), repeat=len(ids)):
                log_weight = log_prior.copy()
                for i, y in zip(ids, labels):
                    log_weight += np.log(self.p[:, i] if y else 1 - self.p[:, i])
                scale = log_weight.max()
                if not np.isfinite(scale):
                    continue
                scaled = np.exp(log_weight - scale)
                total = scaled.sum()
                mass = float(np.exp(scale) * total)
                if mass:
                    branches.append((labels, mass, scaled / total))
        if abs(sum(mass for _, mass, _ in branches) - 1) > 1e-10:
            raise AssertionError("Joint-label branch probability does not conserve mass.")
        return tuple(branches)

    def intervals(self, weights, eligible):
        q = self._q(weights)
        ids = np.asarray(eligible, dtype=int)
        return self._intervals(q, ids)

    def _intervals(self, q, ids):
        self.prepare_screening()
        difference = q - self.w
        tv = 0.5 * np.abs(difference).sum()
        positive = self.w > 0
        with np.errstate(over="ignore", divide="ignore", invalid="ignore"):
            chi = np.sum(difference[positive] ** 2 / self.w[positive])
        deviation = self._span[ids] * tv
        if np.isfinite(chi):
            deviation = np.minimum(deviation, self._sigma[ids] * np.sqrt(chi))
        return np.maximum(0, self.mu[ids] - deviation), np.minimum(1, self.mu[ids] + deviation)

    def dense_batch(self, branches):
        """branches=(q,eligible_indices,post-event omega); full batched Q@P."""
        if not branches:
            return np.empty(0), []
        q = np.stack([self._q(row[0]) for row in branches])
        scores = q @ self.p
        values = np.array(
            [weighted_top(scores[row, ids], omega) for row, (_, ids, omega) in enumerate(branches)]
        )
        return values, [
            {"eligible": len(ids), "exact_refined": len(ids), "dense_fallback": False}
            for _, ids, _ in branches
        ]

    def screened_batch(self, branches, dense_fallback_fraction=0.7):
        if not 0 <= dense_fallback_fraction <= 1:
            raise ValueError("Invalid frozen dense-fallback fraction.")
        values, diagnostics = np.zeros(len(branches)), []
        fallback_rows, fallback_q = [], []
        for row, (weights, eligible, omega) in enumerate(branches):
            q = self._q(weights)
            ids = np.asarray(eligible, dtype=int)
            omega = np.asarray(omega)
            k = min(len(ids), len(omega), int(np.count_nonzero(omega > 0)))
            if not k:
                diagnostics.append(
                    {
                        "eligible": len(ids),
                        "exact_refined": 0,
                        "dense_fallback": False,
                        "lower": 0.0,
                        "upper": 0.0,
                    }
                )
                continue
            lo, hi = self._intervals(q, ids)
            lower, upper = weighted_top(lo, omega), weighted_top(hi, omega)
            cutoff = np.partition(lo, len(lo) - k)[len(lo) - k]
            keep = ids[hi >= cutoff - TOL]  # Strict elimination, with conservative slack.
            fallback = len(keep) >= dense_fallback_fraction * len(ids)
            diagnostics.append(
                {
                    "eligible": len(ids),
                    "exact_refined": len(ids) if fallback else len(keep),
                    "kept_by_bounds": len(keep),
                    "dense_fallback": fallback,
                    "lower": lower,
                    "upper": upper,
                }
            )
            if fallback:
                fallback_rows.append(row)
                fallback_q.append(q)
            else:
                values[row] = weighted_top(q @ self.p[:, keep], omega)
        if fallback_rows:
            scores = np.stack(fallback_q) @ self.p
            for index, row in enumerate(fallback_rows):
                _, ids, omega = branches[row]
                values[row] = weighted_top(scores[index, ids], omega)
        for value, record in zip(values, diagnostics):
            if not record["lower"] - 1e-10 <= value <= record["upper"] + 1e-10:
                raise AssertionError("Exact tail falls outside finite-model interval.")
        return values, diagnostics
