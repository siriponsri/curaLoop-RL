"""Outer-isolated fixed-alpha residual targets; no evaluation-driven selection."""

import numpy as np

from research.lr_d23_v1.policy import FEATURE_NAMES, NO_HISTORY_KEEP


def fit_gate(rows, heldout, allowed_components, round_index, no_history=False):
    from sklearn.linear_model import Ridge

    assert heldout not in allowed_components and len(allowed_components) == 3
    assert all(row["component"] in allowed_components and row["heldout"] == heldout
               and row["round"] == round_index for row in rows), "OUTER_FOLD_CONTAMINATION"
    if round_index == 1:
        assert all(heldout not in row["behavior_training_components"] for row in rows), "BEHAVIOR_POLICY_LEAKAGE"
    selected = [row for row in rows if row["eligible"]]
    groups = sorted({row["component"] for row in selected})
    if len(selected) < 30 or len(groups) < 2:
        raise ValueError("INSUFFICIENT_EXECUTED_SUPPORT")
    keep = list(NO_HISTORY_KEEP) if no_history else list(range(8))
    x = np.asarray([row["features"] for row in selected], dtype=float)[:, keep]
    y = np.asarray([row["update_minus_reuse"] for row in selected], dtype=float)
    counts = {g: sum(row["component"] == g for row in selected) for g in groups}
    weights = np.asarray([1 / counts[row["component"]] for row in selected])
    weights *= len(weights) / weights.sum()
    mean = np.average(x, axis=0, weights=weights)
    scale = np.sqrt(np.average((x - mean)**2, axis=0, weights=weights))
    scale = np.where(scale < 1e-12, 1., scale)
    model = Ridge(alpha=1., fit_intercept=True)
    model.fit((x - mean) / scale, y, sample_weight=weights)
    return {
        "schema": "curaloop.lr_d23.gate.v1", "heldout_component": heldout,
        "training_components": groups, "allowed_components": sorted(allowed_components),
        "round": round_index, "variant": "no_history" if no_history else "full",
        "training_states": len(selected), "assigned_states": len(rows), "component_counts": counts,
        "feature_names": list(FEATURE_NAMES), "feature_indices": keep,
        "mean": mean.tolist(), "scale": scale.tolist(), "coefficients": model.coef_.tolist(),
        "intercept": float(model.intercept_), "ridge_alpha": 1., "deadband": .25,
        "target": "terminal UPDATE-minus-REUSE under common Gk2 tail in round0, frozen v0 tail in round1",
        "training_tasks": sorted({row["task_id"] for row in selected}),
    }
