"""Process-isolated, allowlisted built-in policy runner."""

import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

from .domain import POLICIES, PolicyObservation, Selection, canonical_json


def propose(observation: PolicyObservation) -> tuple[Selection, ...]:
    if observation.current_policy_id not in POLICIES:
        raise ValueError("Unknown policy. Only reviewed built-in policies can run.")
    if observation.slots_available <= 0 or not observation.eligible_candidate_ids:
        return ()
    if observation.current_policy_id in ("q_learning", "contextual_bandit"):
        from .learning import load_checkpoint
        observation = replace(observation, controller_json=canonical_json(
            load_checkpoint(observation.current_policy_id)))
    worker = Path(__file__).with_name("policy_worker.py").resolve()
    env = {k: v for k, v in os.environ.items() if k in (
        "SYSTEMROOT", "WINDIR", "PATH", "TEMP", "TMP", "TMPDIR", "LANG"
    )}
    env.update({"OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1", "MKL_NUM_THREADS": "1"})
    with tempfile.TemporaryDirectory(prefix="curaloop-policy-") as cwd:
        process = subprocess.run(
            [sys.executable, "-I", str(worker)], input=canonical_json(observation.to_dict()),
            text=True, encoding="utf-8", capture_output=True, cwd=cwd, env=env, timeout=45,
            check=False,
        )
    if process.returncode:
        raise RuntimeError(f"Policy worker failed: {process.stderr[-1500:]}")
    decisions = tuple(Selection(**r) for r in json.loads(process.stdout))
    ids = [r.compound_id for r in decisions]
    if len(ids) > observation.slots_available or len(ids) != len(set(ids)) or not set(ids) <= set(
        observation.eligible_candidate_ids
    ):
        raise RuntimeError("Policy worker returned an invalid selection.")
    return decisions
