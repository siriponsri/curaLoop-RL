"""Built-in policy subprocess: JSON in, JSON out. No oracle or engine references.

Launched using Python -I in an empty temporary directory. The import guard is
defense in depth for our fixed built-ins, not arbitrary-code containment.
"""

import importlib.abc
import json
import math
import random
import sys


class DenyPrivateImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "curaloop" or fullname.startswith("curaloop."):
            raise ImportError("Policy worker cannot import simulator internals.")
        return None


def controller_state(obs: dict) -> str:
    known = [r for r in obs["revealed_assay_results"] if r["active"] is not None]
    rate = sum(r["active"] for r in known) / max(1, len(known))
    budget_fraction = obs["budget_remaining_units"] / max(1, obs["budget_total_units"])
    return ":".join(map(str, (
        min(2, int(budget_fraction * 3)), 0 if rate < 0.05 else 1 if rate < 0.3 else 2,
        0 if len(known) < 12 else 1 if len(known) < 36 else 2,
        int(len({r["active"] for r in known}) >= 2), int(bool(obs["pending_candidate_ids"])),
    )))


def choose(obs: dict) -> list[dict]:
    ids = sorted(obs["eligible_candidate_ids"])
    n = min(obs["slots_available"], obs["budget_remaining_units"] // obs["assay_cost_units"], len(ids))
    if n <= 0:
        return []
    policy = obs["current_policy_id"]
    if policy in ("q_learning", "contextual_bandit"):
        checkpoint = json.loads(obs["controller_json"])
        state = controller_state(obs)
        values = checkpoint["values"].get(state)
        action = max(range(3), key=lambda a: (values[a], -a)) if values is not None else 1
        strategy = ("random", "greedy", "uncertainty")[action]
        decisions = choose({**obs, "current_policy_id": strategy})
        prefix = f"{policy}: state={state}; strategy={strategy}; " + ("learned. " if values is not None else "UNSEEN_STATE_GREEDY_FALLBACK. ")
        for decision in decisions:
            decision["explanation"] = prefix + decision["explanation"]
        return decisions
    if policy not in ("random", "greedy", "uncertainty"):
        raise ValueError("Unsupported built-in policy")
    # Tie-breaking and random ranking depend only on public state; not on run hashes.
    rng = random.Random(obs["seed"] + obs["step"] * 1009 + len(obs["revealed_assay_results"]) * 37)
    known = sorted((r for r in obs["revealed_assay_results"] if r["active"] is not None),
                   key=lambda r: r["compound_id"])
    classes = {r["active"] for r in known}
    fallback = policy != "random" and len(classes) < 2
    if policy == "random" or fallback:
        selected = rng.sample(ids, n)
        status = "FALLBACK_RANDOM_ONE_CLASS" if fallback else "NOT_USED_RANDOM"
        reason = ("Fallback: fewer than two observed classes; uniform random, no prediction."
                  if fallback else "Uniform random sample of eligible candidates; no outcome prediction.")
        return [{"compound_id": c, "explanation": reason, "predicted_probability": None,
                 "acquisition_score": None, "model_status": status} for c in selected]
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    features = obs["available_features"]
    model = make_pipeline(StandardScaler(), LogisticRegression(
        solver="liblinear", C=1.0, max_iter=500, random_state=obs["seed"]
    ))
    model.fit([features[r["compound_id"]] for r in known], [r["active"] for r in known])
    probabilities = model.predict_proba([features[c] for c in ids])[:, 1]
    scored = []
    for c, p in zip(ids, probabilities):
        p = float(p)
        if not math.isfinite(p):
            raise ValueError("Non-finite model output")
        score = p if policy == "greedy" else 1 - 2 * abs(p - 0.5)
        scored.append((c, p, score))
    scored.sort(key=lambda row: (-row[2], row[0]))
    return [{"compound_id": c,
             "explanation": (f"Greedy: high predicted P(active)={p:.3f}." if policy == "greedy"
                             else f"Uncertainty: P(active)={p:.3f}, close to 0.5; score={score:.3f}."),
             "predicted_probability": p, "acquisition_score": score,
             "model_status": "FITTED_LOGISTIC_UNCALIBRATED"} for c, p, score in scored[:n]]


if __name__ == "__main__":
    sys.meta_path.insert(0, DenyPrivateImports())
    observation = json.load(sys.stdin)
    json.dump(choose(observation), sys.stdout, allow_nan=False)
