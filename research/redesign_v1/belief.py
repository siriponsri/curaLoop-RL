"""Two declared repairs with public-only proper-prior joint probability draws."""

import hashlib
import json
from dataclasses import dataclass

import numpy as np
from scipy.linalg import cho_solve, solve_triangular
from scipy.optimize import minimize
from scipy.special import expit

from research.planning_v3.belief import PublicDesign, fit_mixture, make_design, objective
from research.planning_v3.mixture import Mixture

VARIANTS = ("anchor_original", "anchor_normalized", "tanimoto_gp")


def similarity(a, b):
    return (a & b).bit_count() / (a | b).bit_count() if a | b else 1.0


def tanimoto(packed):
    return np.array([[similarity(a, b) for b in packed] for a in packed], dtype=float)


@dataclass(frozen=True)
class GPDesign:
    ids: tuple
    packed: tuple
    kernel: np.ndarray
    prior_chol: np.ndarray
    feature_sha256: str


def design_for(ids, packed, variant):
    if variant not in VARIANTS:
        raise ValueError("Unknown fixed predictor variant.")
    if variant == "tanimoto_gp":
        if (not ids or len(ids) != len(packed) or len(ids) > 600 or len(set(ids)) != len(ids)
            or any(type(cid) is not str or not cid for cid in ids)
            or any(type(bits) is not int or bits < 0 or bits.bit_length() > 1024 for bits in packed)):
            raise ValueError("Unique public IDs and paired Morgan1024 fingerprints required.")
        rows = sorted(zip(ids, packed))
        ids, packed = tuple(r[0] for r in rows), tuple(r[1] for r in rows)
        digest = hashlib.sha256(json.dumps(["goal4r1-direct-tanimoto-v1", list(zip(ids, [format(b, "x") for b in packed]))],
                                          separators=(",", ":")).encode()).hexdigest()
        kernel = 4.0 + tanimoto(packed) + np.eye(len(ids)) * 1e-8
        chol = np.linalg.cholesky(kernel)
        kernel.setflags(write=False)
        chol.setflags(write=False)
        return GPDesign(ids, packed, kernel, chol, digest)
    base = make_design(ids, packed, 64)
    if len(base.ids) > 600:
        raise ValueError("Public pool exceeds frozen size limit.")
    if variant == "anchor_original":
        return base
    digest = hashlib.sha256(json.dumps(["goal4r1-design-v1", variant, base.feature_sha256],
                                      separators=(",", ":")).encode()).hexdigest()
    if variant == "anchor_normalized":
        x = base.x.copy()
        x[:, 1:] /= 8.0
        x.setflags(write=False)
        return PublicDesign(base.ids, base.packed, x, base.anchor_indices, digest)
    raise AssertionError("Unreachable frozen variant.")


def observed_laplace(kernel, indices, labels):
    """Whiten observed latent coordinates; posterior covariance is approximate."""
    koo = kernel[np.ix_(indices, indices)]
    lo = np.linalg.cholesky(koo)
    precision = np.ones(len(indices))
    result = minimize(objective, np.zeros(len(indices)), args=(lo, labels, precision),
                      jac=True, method="L-BFGS-B",
                      options={"maxiter": 100, "ftol": 1e-12, "gtol": 1e-8, "maxls": 30})
    if not result.success or not np.isfinite(result.x).all():
        return None, {"fallback": "GP_OPTIMIZER_DID_NOT_CONVERGE_PRIOR",
                      "optimizer_iterations": int(result.nit)}
    beta = result.x
    p = expit(lo @ beta)
    hessian = np.eye(len(indices)) + lo.T @ ((p * (1 - p))[:, None] * lo)
    lh = np.linalg.cholesky(hessian)
    # A maps an observed latent draw to the conditional full-pool prior mean.
    a = cho_solve((lo, True), kernel[indices, :]).T
    return (lo, lh, beta, a), {"fallback": None, "optimizer_iterations": int(result.nit),
                             "gradient_max_abs": float(np.max(np.abs(result.jac)))}


def fit_joint(design, known, seed, variant, hypotheses=128):
    if variant not in VARIANTS or hypotheses != 128:
        raise ValueError("Fixed variant and M128 required.")
    if variant != "tanimoto_gp":
        model, trace = fit_mixture(design, known, seed, hypotheses)
        return model, dict(trace, predictor_variant=variant)
    if type(design) is not GPDesign or type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Public GP design and unsigned32-bit seed required.")
    known = sorted(tuple(known))
    if len({cid for cid, _ in known}) != len(known) or any(
        cid not in design.ids or type(y) is not bool for cid, y in known
    ):
        raise ValueError("Only unique explicit known Boolean labels accepted.")
    index = {cid: i for i, cid in enumerate(design.ids)}
    indices = [index[cid] for cid, _ in known]
    labels = np.array([float(y) for _, y in known])
    key = ["goal4r1-gp-function-draw-v1", seed, design.feature_sha256, known]
    draw_seed = int(hashlib.sha256(json.dumps(key, separators=(",", ":")).encode()).hexdigest()[:16], 16)
    rng = np.random.default_rng(draw_seed)

    def antithetic(width):
        base = rng.standard_normal((64, width))
        value = np.empty((128, width))
        value[0::2], value[1::2] = base, -base
        return value

    prior = antithetic(len(design.ids)) @ design.prior_chol.T
    detail = {"fallback": None, "optimizer_iterations": 0}
    latent = prior
    if indices:
        try:
            state, detail = observed_laplace(design.kernel, indices, labels)
            if state is not None:
                lo, lh, beta, a = state
                beta_draw = beta + solve_triangular(lh.T, antithetic(len(indices)).T, lower=False).T
                observed_draw = beta_draw @ lo.T
                # Independent prior/observed-posterior draws implement the
                # Gaussian conditional simulation identity, retaining covariance.
                latent = prior + (observed_draw - prior[:, indices]) @ a.T
        except np.linalg.LinAlgError:
            detail = {"fallback": "GP_CHOLESKY_FAILURE_PRIOR", "optimizer_iterations": 0}
    probabilities = np.clip(expit(latent), 1e-9, 1 - 1e-9)
    return Mixture(probabilities, np.full(128, 1 / 128)), {
        **detail, "predictor_variant": variant, "model": "Tanimoto logistic Bernoulli GP Laplace finite function mixture",
        "hypotheses": 128, "known_count": len(known), "known_active_count": int(labels.sum()),
        "one_class_start_retained": len(set(labels.tolist())) < 2, "draw_seed": draw_seed,
        "source_of_labels": "Explicit known-label argument only", "calibration_established": False,
    }
