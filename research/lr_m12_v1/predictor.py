"""Public features and delivered labels only; no evaluator or dataset imports."""

import hashlib
from dataclasses import dataclass

import numpy as np

from research.redesign_v1.belief import GPDesign, design_for, fit_joint, tanimoto


@dataclass(frozen=True)
class PublicPool:
    ids: tuple
    packed: tuple
    provenance: str


@dataclass(frozen=True)
class PredictiveBundle:
    ids: tuple
    probabilities: np.ndarray  # model x latent function x candidate
    known_ids: frozenset
    provenance: str
    fitting_details: tuple


def public_pool(rows):
    if not rows or len(rows) > 600:
        raise ValueError('PUBLIC_POOL_SIZE')
    if any(set(row) != {'candidate_id', 'morgan_on_bits'} for row in rows):
        raise ValueError('FORBIDDEN_NONPUBLIC_FEATURE_FIELD')
    ids, packed = [], []
    for row in sorted(rows, key=lambda value: value['candidate_id']):
        bits = row['morgan_on_bits']
        if len(set(bits)) != len(bits) or any(type(b) is not int or not 0 <= b < 1024 for b in bits):
            raise ValueError('INVALID_PUBLIC_FINGERPRINT')
        ids.append(row['candidate_id'])
        packed.append(sum(1 << b for b in bits))
    if len(set(ids)) != len(ids):
        raise ValueError('DUPLICATE_PUBLIC_ID')
    digest = hashlib.sha256(repr(tuple(zip(ids, packed))).encode()).hexdigest()
    return PublicPool(tuple(ids), tuple(packed), digest)


def fit_predictive(pool, delivered, seed):
    if type(pool) is not PublicPool or type(seed) is not int:
        raise ValueError('TYPED_PUBLIC_POOL_AND_SEED_REQUIRED')
    known = tuple(sorted(delivered))
    if len({cid for cid, _ in known}) != len(known) or any(
            cid not in pool.ids or type(y) is not bool for cid, y in known):
        raise ValueError('EXPLICIT_UNIQUE_DELIVERED_BOOLEAN_LABELS_REQUIRED')
    design = design_for(pool.ids, pool.packed, 'tanimoto_gp')
    similarity = tanimoto(design.packed)
    draws, details = [], []
    for index, scale in enumerate((0.5, 1.0, 2.0)):
        kernel = 4.0 + scale * similarity + np.eye(len(pool.ids)) * 1e-8
        kernel.setflags(write=False)
        chol = np.linalg.cholesky(kernel)
        chol.setflags(write=False)
        provenance = hashlib.sha256((pool.provenance + '|scale|' + str(scale)).encode()).hexdigest()
        variant = GPDesign(design.ids, design.packed, kernel, chol, provenance)
        mixture, trace = fit_joint(variant, known, seed + index * 1009, 'tanimoto_gp')
        draws.append(mixture.p)
        details.append(dict(trace, tanimoto_scale=scale))
    probabilities = np.stack(draws)
    probabilities.setflags(write=False)
    provenance = hashlib.sha256(repr((pool.provenance, known, seed, (0.5, 1.0, 2.0))).encode()).hexdigest()
    return PredictiveBundle(design.ids, probabilities, frozenset(cid for cid, _ in known),
                            provenance, tuple(details))
