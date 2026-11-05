"""Role-checked private evaluator using unchanged scheduler/accounting helpers."""

import hashlib
import time
from dataclasses import asdict

from research.event_time import Campaign, Scenario, canonical
from research.study_v1.campaign import initial_ids, make_task, observation_key, support_law

from .policy import session


def run_campaign(payload, seed, operation, arm, protocol):
    if payload.get("role") != "development":
        raise ValueError("4R1 campaign selection population is development only.")
    started, cpu = time.perf_counter(), time.process_time()
    task = make_task(payload, seed, operation)
    initial = initial_ids(payload, seed, 16)
    engine = Campaign(task, Scenario(12, operation["capacity"], operation["deadline"], initial))
    begin = time.process_time()
    policy = session(engine.observe(), arm, seed, support_law(operation), operation["capacity"])
    policy_cpu = time.process_time() - begin
    decisions, optional, forced = [], 0, 0
    for _ in range(64):
        if engine.done:
            break
        obs = engine.observe()
        if not obs.eligible_ids:
            if not engine.wait():
                raise RuntimeError("Campaign made no progress.")
            forced += 1
            continue
        begin = time.process_time()
        action, trace = policy.select(obs)
        policy_cpu += time.process_time() - begin
        decisions.append({"public_state_sha256": observation_key(obs), "trace": trace})
        if action:
            engine.submit(action)
            policy.record_acceptance(action, obs.time)
        else:
            optional += 1
            if not engine.wait():
                raise RuntimeError("Optional WAIT made no progress.")
    else:
        raise RuntimeError("Fixed event cap exceeded.")
    engine.advance_to(operation["deadline"])
    metrics = engine.metrics
    if metrics["accepted_exposure"] > 12 or metrics["spent"] + metrics["reserved"] != metrics["accepted_exposure"]:
        raise AssertionError("Budget did not reconcile.")
    scientific = {"metrics": metrics, "initial_ids": initial,
                  "decisions": [{"time": d["trace"]["time"], "chosen": d["trace"]["chosen"],
                                 "state": d["public_state_sha256"]} for d in decisions],
                  "events": [asdict(e) for e in engine.events]}
    return {"status": "PASS", "task_id": payload["task_id"], "role": payload["role"],
            "family_id": payload["family_id"], "seed": seed, "operation": operation["id"],
            "operation_role": operation["role"], "arm": arm, "hypotheses": 128,
            "metrics": metrics, "optional_waits": optional, "forced_waits": forced,
            "policy_setup_seconds": policy.setup_seconds,
            "policy_wall_seconds": policy.setup_seconds + sum(d["trace"]["policy_seconds"] for d in decisions),
            "policy_cpu_seconds": policy_cpu, "run_wall_seconds": time.perf_counter() - started,
            "run_cpu_seconds": time.process_time() - cpu, "learned_action_share": 0,
            "scientific": scientific, "scientific_sha256": hashlib.sha256(canonical(scientific).encode()).hexdigest(),
            "decisions": decisions}
