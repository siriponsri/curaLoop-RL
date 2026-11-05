"""Public-feature anchors and delivered-label-only Laplace logistic mixtures."""

import hashlib
import json
from dataclasses import dataclass

import numpy as np
from scipy.linalg import solve_triangular
from scipy.optimize import minimize
from scipy.special import expit

from .mixture import Mixture


@dataclass(frozen=True)
class PublicDesign:
    ids: tuple[str, ...]
    packed: tuple[int, ...]
    x: np.ndarray
    anchor_indices: tuple[int, ...]
    feature_sha256: str


def make_design(ids, packed, anchor_count=64):
    if (
        len(ids) != len(packed)
        or not ids
        or len(set(ids)) != len(ids)
        or any(type(i) is not str or not i for i in ids)
    ):
        raise ValueError("Unique public IDs and paired fingerprints required.")
    if any(type(bits) is not int or bits < 0 or bits.bit_length() > 1024 for bits in packed):
        raise ValueError("Only public1024-bit Morgan fingerprints accepted.")
    if type(anchor_count) is not int or anchor_count < 1:
        raise ValueError("Positive anchor count required.")
    rows = sorted(zip(ids, packed))
    ids, packed = tuple(r[0] for r in rows), tuple(r[1] for r in rows)
    distances = np.full(len(ids), np.inf)
    features, anchors = [np.ones(len(ids))], []
    for _ in range(min(anchor_count, len(ids))):
        index = int(np.argmax(distances))
        anchors.append(index)
        similarities = np.array(
            [
                (bits & packed[index]).bit_count() / (bits | packed[index]).bit_count()
                if bits | packed[index]
                else 1
                for bits in packed
            ]
        )
        features.append(similarities)
        distances = np.minimum(distances, 1 - similarities)
        distances[anchors] = -1  # Equal fingerprints still get distinct anchor IDs.
    x = np.stack(features, axis=1)
    x.setflags(write=False)
    digest = hashlib.sha256(
        json.dumps(
            [
                "curaloop-public-design-v1",
                list(zip(ids, [format(b, "x") for b in packed])),
                anchors,
            ],
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return PublicDesign(ids, packed, x, tuple(anchors), digest)


def objective(beta, x, y, precision):
    z = x @ beta
    probability = expit(z)
    value = np.logaddexp(0, z).sum() - y @ z + 0.5 * np.dot(precision * beta, beta)
    gradient = x.T @ (probability - y) + precision * beta
    return float(value), gradient


def fit_mixture(design, known, seed, hypotheses):
    if type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Explicit unsigned32-bit experiment seed required.")
    if type(hypotheses) is not int or not 2 <= hypotheses <= 128 or hypotheses % 2:
        raise ValueError("Even finite support from2through128required; study uses32/64/128only.")
    known = sorted(tuple(known))
    if len({cid for cid, _ in known}) != len(known) or any(
        cid not in design.ids or type(y) is not bool for cid, y in known
    ):
        raise ValueError("Unique delivered/initial Boolean labels required.")
    index = {cid: i for i, cid in enumerate(design.ids)}
    x = design.x[[index[cid] for cid, _ in known]]
    y = np.array([float(value) for _, value in known])
    precision = np.ones(design.x.shape[1])
    precision[0] = 0.25  # Proper N(0,4) intercept; N(0,1) anchor coefficients.
    beta = np.zeros(len(precision))
    fallback = None
    iterations = 0
    if known:
        result = minimize(
            objective,
            beta,
            args=(x, y, precision),
            jac=True,
            method="L-BFGS-B",
            options={"maxiter": 100, "ftol": 1e-12, "gtol": 1e-8, "maxls": 30},
        )
        iterations = int(result.nit)
        if result.success and np.isfinite(result.x).all():
            beta = result.x
        else:
            fallback = "OPTIMIZER_DID_NOT_CONVERGE_PRIOR"
    if fallback:
        hessian = np.diag(precision)
    else:
        probability = expit(x @ beta)
        hessian = x.T @ ((probability * (1 - probability))[:, None] * x) + np.diag(precision)
    try:
        chol = np.linalg.cholesky(hessian)
    except np.linalg.LinAlgError:
        beta = np.zeros(len(precision))
        chol = np.diag(np.sqrt(precision))
        fallback = "CHOLESKY_FAILURE_PRIOR"
    key = ["curaloop-laplace-parameter-draw-v1", seed, design.feature_sha256, known]
    draw_seed = int(
        hashlib.sha256(json.dumps(key, separators=(",", ":")).encode()).hexdigest()[:16], 16
    )
    # Nested antithetic draws: changing M never changes earlier hypotheses.
    base = np.random.default_rng(draw_seed).standard_normal((64, len(precision)))
    normals = np.empty((128, len(precision)))
    normals[0::2], normals[1::2] = base, -base
    theta = beta + solve_triangular(chol.T, normals[:hypotheses].T, lower=False).T
    p = np.clip(expit(theta @ design.x.T), 1e-9, 1 - 1e-9)
    model = Mixture(p, np.full(hypotheses, 1 / hypotheses))
    return model, {
        "model": "proper-prior Laplace logistic finite parameter mixture",
        "known_count": len(known),
        "known_active_count": int(y.sum()),
        "hypotheses": hypotheses,
        "anchors": len(design.anchor_indices),
        "draw_seed": draw_seed,
        "optimizer_iterations": iterations,
        "fallback": fallback,
        "one_class_start_retained": len(set(y.tolist())) < 2,
        "source_of_labels": "Explicit known-label argument only; no private resource accepted",
        "calibration_established": False,
    }
