"""Public-input policy execution against an isolated private scheduler."""

import hashlib
import json
import math
import time
from dataclasses import asdict
from fractions import Fraction

from research.event_time import Campaign, Candidate, Scenario, Task, canonical
from research.planning_v3.policy import PolicySession


def keyed_uniform(seed, namespace, *public_keys):
    value = int(hashlib.sha256(canonical([namespace, seed, *public_keys]).encode()).hexdigest()[:16], 16)
    return (value >> 11) * 2**-53


def support_law(operation):
    weights = sorted((int(k), Fraction(str(v))) for k, v in operation["law"].items())
    if any(d <= 0 or p <= 0 for d, p in weights) or sum(p for _, p in weights) != 1:
        raise ValueError("Positive normalized rational duration law required.")
    denominator = math.lcm(*(p.denominator for _, p in weights))
    if denominator > 32:
        raise ValueError("Public duration support exceeds the frozen bound.")
    return tuple(d for d, p in weights for _ in range(int(p * denominator)))


def initial_ids(payload, seed, count):
    ids = [r["candidate_id"] for r in payload["records"]]
    if len(set(ids)) != len(ids) or type(seed) is not int or not 0 <= seed < 2**32:
        raise ValueError("Invalid public study IDs/seed.")
    if not 0 <= count < len(ids):
        raise ValueError("Initial subset must leave a nonempty search pool.")
    return tuple(sorted(ids, key=lambda cid: keyed_uniform(seed, "goal4-initial-v1", payload["task_id"], cid))[:count])


def make_task(payload, seed, operation):
    if payload["role"] not in ("development", "validation"):
        raise ValueError("Forbidden study task role.")
    if any(type(r["active"]) is not bool for r in payload["records"]):
        raise ValueError("Private source outcomes must be Boolean.")
    candidates, durations, outcomes = [], [], []
    law = support_law(operation)
    for record in sorted(payload["records"], key=lambda r: r["candidate_id"]):
        cid = record["candidate_id"]
        bits = set(record["morgan_on_bits"])
        if any(type(bit) is not int or not 0 <= bit < 1024 for bit in bits):
            raise ValueError("Invalid public binary fingerprint.")
        candidates.append(Candidate(cid, tuple(int(i in bits) for i in range(1024))))
        u = keyed_uniform(seed, "goal4-private-duration-v1", payload["task_id"], operation["id"], cid)
        chosen = law[int(u * len(law))]
        durations.append((cid, chosen))
        outcomes.append((cid, record["active"]))
    return Task(payload["task_id"], tuple(candidates), tuple(durations),
                tuple((c.candidate_id, 1) for c in candidates), tuple(outcomes))


def observation_key(obs):
    # Public labels only; a hidden resource/outcome vector never enters this hash.
    state = {
        "time": obs.time, "deadline": obs.deadline, "eligible": obs.eligible_ids,
        "pending": obs.pending_ids, "initial": [asdict(r) for r in obs.initial_results],
        "delivered": [asdict(r) for r in obs.delivered_results], "missing": obs.missing_ids,
        "slots": obs.slots, "uncommitted": obs.uncommitted,
    }
    return hashlib.sha256(canonical(state).encode()).hexdigest()


def run_campaign(payload, seed, operation, method, hypotheses, protocol):
    started, cpu_start = time.perf_counter(), time.process_time()
    task = make_task(payload, seed, operation)
    initial = initial_ids(payload, seed, protocol["initial_labels"])
    scenario = Scenario(protocol["budget"], operation["capacity"], operation["deadline"], initial)
    engine = Campaign(task, scenario)
    begin = time.process_time()
    policy = PolicySession(engine.observe(), method, seed, support_law(operation),
                           operation["capacity"], hypotheses)
    policy_cpu = time.process_time() - begin
    decisions, optional_waits, forced_waits = [], 0, 0
    for _ in range(64):
        if engine.done:
            break
        obs = engine.observe()
        if not obs.eligible_ids:
            if not engine.wait():
                raise RuntimeError("Nonterminal campaign made no public progress.")
            forced_waits += 1
            continue
        begin = time.process_time()
        action, trace = policy.select(obs)
        policy_cpu += time.process_time() - begin
        decisions.append({"public_state_sha256": observation_key(obs), "trace": trace})
        if action:
            engine.submit(action)
            policy.record_acceptance(action, obs.time)
        else:
            optional_waits += 1
            if not engine.wait():
                raise RuntimeError("Optional WAIT made no progress.")
    else:
        raise RuntimeError("Frozen campaign event cap exceeded.")
    engine.advance_to(operation["deadline"])
    metrics = engine.metrics
    if metrics["accepted_exposure"] > protocol["budget"] or metrics["spent"] + metrics["reserved"] != metrics["accepted_exposure"]:
        raise AssertionError("Cost ledger did not reconcile.")
    scientific = {"metrics": metrics, "initial_ids": initial,
                  "decisions": [{"time": d["trace"]["time"], "chosen": d["trace"]["chosen"],
                                 "state": d["public_state_sha256"]} for d in decisions],
                  "events": [asdict(e) for e in engine.events]}
    return {
        "status": "PASS", "task_id": payload["task_id"], "role": payload["role"],
        "family_id": payload["family_id"], "seed": seed, "operation": operation["id"],
        "operation_role": operation["role"], "method": method, "hypotheses": hypotheses,
        "metrics": metrics, "optional_waits": optional_waits, "forced_waits": forced_waits,
        "policy_setup_seconds": policy.setup_seconds,
        "policy_wall_seconds": policy.setup_seconds + sum(d["trace"]["policy_seconds"] for d in decisions),
        "policy_cpu_seconds": policy_cpu, "run_wall_seconds": time.perf_counter() - started,
        "run_cpu_seconds": time.process_time() - cpu_start,
        "learned_action_share": 0, "scientific": scientific,
        "scientific_sha256": hashlib.sha256(canonical(scientific).encode()).hexdigest(),
        "decisions": decisions,
    }
