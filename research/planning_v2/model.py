"""Feature-only clusters and delivered-label-only posterior world construction."""

import random

from .finite import FinitePlanner, State


def clusters(candidates, count=12):
    """Deterministic farthest-first Morgan/Tanimoto partition; no labels."""
    bits = [sum(1 << i for i, x in enumerate(c.features) if x > 0.5) for c in candidates]
    centers, distance = [], [float("inf")] * len(bits)
    assignment = [0] * len(bits)
    for group in range(min(count, len(bits))):
        center = max(range(len(bits)), key=lambda i: (distance[i], -i))
        centers.append(center)
        for i, b in enumerate(bits):
            union = (b | bits[center]).bit_count()
            d = 1 - ((b & bits[center]).bit_count() / union if union else 1)
            if d < distance[i]:
                assignment[i], distance[i] = group, d
    return tuple(assignment), tuple(bits)


def build(obs, launched_at, groups, support, seed, worlds, capacity):
    """Independent Beta(.5,9.5) cluster latents, conditional on public results.

    This deliberately simple, uncalibrated model is shared by the acquisition
    arms. Rebuilding its empirical scenarios makes bounds local to a decision.
    Pending duration samples use D-age | D>age, never a restarted duration.
    """
    ids = [c.candidate_id for c in obs.candidates]
    index = {cid: i for i, cid in enumerate(ids)}
    known = obs.initial_results + obs.delivered_results
    counts = [[0.5, 9.5] for _ in range(max(groups) + 1)]
    for result in known:
        counts[groups[index[result.candidate_id]]][0 if result.active else 1] += 1
    rng = random.Random(seed)
    labels, durations = [], []
    for _ in range(worlds):
        p = [rng.betavariate(a, b) for a, b in counts]
        labels.append(tuple(rng.random() < p[g] for g in groups))
        row = [rng.choice(support) for _ in ids]
        for cid in obs.pending_ids:
            age = obs.time - launched_at[cid]
            residual = [d - age for d in support if d > age]
            if not residual:
                raise ValueError("Public pending age contradicts duration support.")
            row[index[cid]] = rng.choice(residual)
        durations.append(tuple(row))
    used = sum(1 << index[r.candidate_id] for r in known)
    used |= sum(1 << index[cid] for cid in obs.pending_ids)
    state = State(
        obs.time,
        obs.uncommitted,
        used,
        tuple(sorted((index[cid], obs.time) for cid in obs.pending_ids)),
        len(obs.delivered_results),
    )
    return FinitePlanner(labels, durations, capacity, obs.deadline), state
