"""Private evaluator metrics; no query outcomes enter a fitted predictor."""

import hashlib
import math
import time

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score

from research.study_v1.campaign import initial_ids

from .belief import VARIANTS, design_for, fit_joint, similarity
from .policy import knn_scores

PREDICTORS = VARIANTS + ("fingerprint_rf", "tanimoto_knn", "nearest_hit")


def pair_ids(ids, packed, query):
    """Up to32 feature-nearest pairs then ID-hash-ranked pairs; labels unused."""
    pairs = set()
    anchors = sorted(query, key=lambda i: hashlib.sha256(ids[i].encode()).hexdigest())[:32]
    for i in anchors:
        j = min((j for j in query if j != i), key=lambda j: (-similarity(packed[i], packed[j]), ids[j]))
        pairs.add(tuple(sorted((i, j))))
    remaining = ((i, j) for a, i in enumerate(query) for j in query[a + 1:] if (i, j) not in pairs)
    ranked = sorted(remaining, key=lambda ij: hashlib.sha256((ids[ij[0]] + ":" + ids[ij[1]]).encode()).hexdigest())
    pairs.update(ranked[:max(0, 64 - len(pairs))])
    return tuple(sorted(pairs))


def joint_scores(model, pairs, outcomes):
    # Product marginals is exact under the finite model; permutations only stress
    # finite draw dependence and must not be called exact independent sampling.
    if not np.all(model.w == 1 / len(model.w)):
        raise ValueError("Secondary permutation stress test requires uniform pre-fantasy weights.")
    shuffled = model.p.copy()
    rng = np.random.default_rng(20261105)
    for j in range(shuffled.shape[1]):
        shuffled[:, j] = shuffled[rng.permutation(len(model.w)), j]
    values = []
    for i, j in pairs:
        yi, yj = outcomes[i], outcomes[j]
        pi = model.p[:, i] if yi else 1 - model.p[:, i]
        pj = model.p[:, j] if yj else 1 - model.p[:, j]
        si = shuffled[:, i] if yi else 1 - shuffled[:, i]
        sj = shuffled[:, j] if yj else 1 - shuffled[:, j]
        joint = float(model.w @ (pi * pj))
        independent = float(model.w @ pi) * float(model.w @ pj)
        stress = float(model.w @ (si * sj))
        conditional = joint / float(model.w @ pi)
        values.append((-math.log(max(joint, 1e-30)), -math.log(max(independent, 1e-30)),
                       -math.log(max(stress, 1e-30)), -math.log(max(conditional, 1e-30))))
    mean = np.mean(values, axis=0)
    return {"pair_count": len(pairs), "joint_log_loss": float(mean[0]),
            "product_marginal_log_loss": float(mean[1]), "permuted_log_loss": float(mean[2]),
            "conditional_second_label_log_loss": float(mean[3]),
            "conditional_is_derived_from_joint_not_independent_evidence": True,
            "permutation_exact_independence": False}


def diagnose(payload, seed, support, predictor):
    if payload.get("role") != "development" or predictor not in PREDICTORS or support not in (16, 28):
        raise ValueError("Only frozen exposed-development diagnosis accepted.")
    started, cpu = time.perf_counter(), time.process_time()
    rows = sorted(payload["records"], key=lambda r: r["candidate_id"])
    ids = tuple(r["candidate_id"] for r in rows)
    packed = tuple(sum(1 << bit for bit in r["morgan_on_bits"]) for r in rows)
    chosen = set(initial_ids(payload, seed, support))
    heldback = set(initial_ids(payload, seed, 28))
    query = [i for i, r in enumerate(rows) if r["candidate_id"] not in heldback]
    known = [(r["candidate_id"], r["active"]) for r in rows if r["candidate_id"] in chosen]
    detail, joint, model = {"fallback": None}, None, None
    if predictor in VARIANTS:
        design = design_for(ids, packed, predictor)
        model, detail = fit_joint(design, known, seed, predictor)
        scores = model.mu
    elif predictor == "tanimoto_knn":
        scores = knn_scores(packed, ids, known)
    elif predictor == "fingerprint_rf":
        x = np.array([[int(bits >> bit & 1) for bit in range(1024)] for bits in packed], dtype=np.float32)
        train = [i for i, cid in enumerate(ids) if cid in chosen]
        rf = RandomForestClassifier(n_estimators=128, max_features="sqrt", n_jobs=1, random_state=seed)
        rf.fit(x[train], [rows[i]["active"] for i in train])
        p = rf.predict_proba(x)
        scores = p[:, list(rf.classes_).index(True)] if True in rf.classes_ else np.zeros(len(ids))
    else:
        hits = [i for i, r in enumerate(rows) if r["candidate_id"] in chosen and r["active"]]
        if hits:
            scores = np.array([max(similarity(bits, packed[h]) for h in hits) for bits in packed])
        else:
            # Same fixed random-order fallback as the campaign nearest-hit arm;
            # values encode ranks only, never probabilities.
            from research.planning_v3.controls import uniform
            scores = np.array([uniform(seed, "random-finite-pool-v1", cid) for cid in ids])
            scores = -scores
            detail["fallback"] = "NO_DELIVERED_ACTIVE_RANDOM"
    fit_cpu, fit_wall = time.process_time() - cpu, time.perf_counter() - started
    y = np.array([float(rows[i]["active"]) for i in query])
    probabilities = np.clip(scores[query], 1e-9, 1 - 1e-9) if predictor != "nearest_hit" else None
    ranked = sorted(query, key=lambda i: (-scores[i], ids[i]))[:12]
    if model is not None:
        pairs = pair_ids(ids, packed, query)
        joint = joint_scores(model, pairs, [r["active"] for r in rows])
    return {"status": "PASS", "task_id": payload["task_id"], "family_id": payload["family_id"],
            "role": "development", "seed": seed, "support": support, "predictor": predictor,
            "query_n": len(query), "support_active_count": sum(v for _, v in known),
            "average_precision": float(average_precision_score(y, scores[query])) if y.any() else None,
            "undefined_ap_reason": None if y.any() else "NO_QUERY_POSITIVES",
            "top12_precision": float(np.mean([rows[i]["active"] for i in ranked])),
            "brier": float(np.mean((probabilities - y)**2)) if probabilities is not None else None,
            "log_loss": float(-np.mean(y*np.log(probabilities)+(1-y)*np.log1p(-probabilities))) if probabilities is not None else None,
            "joint": joint, "model_trace": detail, "fit_cpu_seconds": fit_cpu, "fit_wall_seconds": fit_wall,
            "run_cpu_seconds": time.process_time() - cpu, "run_wall_seconds": time.perf_counter() - started,
            "support_ids_sha256": hashlib.sha256("\n".join(sorted(chosen)).encode()).hexdigest(),
            "query_ids_sha256": hashlib.sha256("\n".join(ids[i] for i in query).encode()).hexdigest(),
            "marginal_calibration_established": False, "joint_calibration_established": False}
