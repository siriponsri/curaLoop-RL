"""Actual tabular Q-learning and contextual sample-average bandit training.

Controllers choose among the three fixed acquisition strategies. Training uses
synthetic tasks only. Frozen JSON checkpoints are evaluated via policy processes.
"""

import json
import random
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from .domain import BASELINES, Scenario, Selection, digest
from .engine import Campaign
from .evaluation import metrics_from_events
from .policy_worker import choose, controller_state


def public_vector(obs: dict) -> np.ndarray:
    known = obs["revealed_assay_results"]
    return np.asarray([
        obs["budget_remaining_units"] / max(1, obs["budget_total_units"]),
        sum(r["active"] is True for r in known) / max(1, len(known)),
        min(1, len(known) / 120),
        len(obs["pending_candidate_ids"]) / max(1, len(obs["pending_candidate_ids"]) + obs["slots_available"]),
    ], dtype=np.float32)


class ScreeningEnv(gym.Env):
    """Gymnasium environment: action=random/greedy/uncertainty; reward=new hits−0.01 cost."""
    metadata = {"render_modes": []}

    def __init__(self, scenario: Scenario | None = None):
        self.scenario = scenario or Scenario(candidate_count=96, budget_units=18, batch_size=3)
        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Box(0, 1, shape=(4,), dtype=np.float32)
        self._campaign = None

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        scenario = replace(self.scenario, seed=int(seed)) if seed is not None else self.scenario
        self._campaign = Campaign(scenario, "random")
        self.action_space.seed(seed)
        obs = self._campaign.observe().to_dict()
        return public_vector(obs), {"state_key": controller_state(obs), "observation": obs}

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError("Action must be 0=random, 1=greedy or 2=uncertainty.")
        if self._campaign is None:
            raise RuntimeError("Call reset() before step().")
        if self._campaign.done:
            raise RuntimeError("Episode already terminated; call reset().")
        before = metrics_from_events(self._campaign.events, self.scenario.budget_units,
                                     self.scenario.assay_cost_units)
        observation = self._campaign.observe().to_dict()
        observation["current_policy_id"] = BASELINES[int(action)]
        selections = tuple(Selection(**d) for d in choose(observation))
        if selections:
            self._campaign.submit(selections)
        # Complete due events until a fresh decision is possible; never peek at outcomes.
        while self._campaign.pending and (
            not self._campaign.observe().slots_available or
            not self._campaign.observe().eligible_candidate_ids or
            self._campaign.remaining < self.scenario.assay_cost_units
        ):
            self._campaign.advance(max(1, min(r.due_at_step for r in self._campaign.pending) - self._campaign.step))
        after = metrics_from_events(self._campaign.events, self.scenario.budget_units,
                                    self.scenario.assay_cost_units)
        reward = after["confirmed_hits"] - before["confirmed_hits"] - 0.01 * (after["spent_units"] - before["spent_units"])
        obs = self._campaign.observe().to_dict()
        return public_vector(obs), float(reward), self._campaign.done, False, {
            "state_key": controller_state(obs), "observation": obs,
            "confirmed_hits": after["confirmed_hits"], "spent_units": after["spent_units"],
        }


@lru_cache(maxsize=2)
def load_checkpoint(policy: str) -> dict:
    if policy not in ("q_learning", "contextual_bandit"):
        raise ValueError("Unknown learned controller.")
    path = Path(__file__).with_name("resources") / f"{policy}.json"
    if not path.exists():
        raise ValueError("No trained checkpoint. Run: python -m curaloop.learning")
    checkpoint = json.loads(path.read_text(encoding="utf-8"))
    expected = checkpoint.pop("checkpoint_sha256")
    if digest(checkpoint) != expected or checkpoint["status"] not in ("RL_TRAINED", "BANDIT_TRAINED"):
        raise ValueError("Checkpoint integrity/status check failed.")
    checkpoint["checkpoint_sha256"] = expected
    return checkpoint


def train_controllers(episodes: int = 160, training_seed: int = 20261103,
                      output: Path | None = None) -> dict:
    if not 1 <= episodes <= 10000:
        raise ValueError("Episodes must be in [1, 10000].")
    output = output or Path(__file__).with_name("resources")
    output.mkdir(parents=True, exist_ok=True)
    summaries = {}
    for policy in ("q_learning", "contextual_bandit"):
        rng = random.Random(training_seed)
        values, counts, rewards = {}, {}, []
        for episode in range(episodes):
            scenario = Scenario(dataset="synthetic_shift_v1" if episode % 2 else "synthetic_linear_v1",
                                candidate_count=96, initial_count=12, budget_units=(12, 18, 24)[episode % 3],
                                batch_size=3, delay_steps=episode % 3, missing_percent=10 if episode % 4 == 0 else 0)
            env = ScreeningEnv(scenario)
            _, info = env.reset(seed=10000 + episode)
            state = info["state_key"]
            total = 0
            done = False
            while not done:
                q = values.setdefault(state, [0.0, 0.0, 0.0])
                count = counts.setdefault(state, [0, 0, 0])
                epsilon = max(0.1, 1 - episode / max(1, episodes * 0.85))
                action = rng.randrange(3) if rng.random() < epsilon else max(range(3), key=lambda a: (q[a], -a))
                _, reward, done, _, next_info = env.step(action)
                next_state = next_info["state_key"]
                count[action] += 1
                if policy == "q_learning":
                    target = reward + (0 if done else 0.95 * max(values.get(next_state, [0, 0, 0])))
                    q[action] += 0.2 * (target - q[action])
                else:
                    q[action] += (reward - q[action]) / count[action]
                total += reward
                state = next_state
            rewards.append(total)
            env.close()
        checkpoint = {
            "schema_version": "1.1", "policy_id": policy,
            "status": "RL_TRAINED" if policy == "q_learning" else "BANDIT_TRAINED",
            "algorithm": "tabular Q-learning" if policy == "q_learning" else "contextual epsilon-greedy sample-average bandit",
            "training_episodes": episodes, "training_rng_seed": training_seed,
            "training_dataset_names": ["synthetic_linear_v1", "synthetic_shift_v1"],
            "training_episode_seeds": list(range(10000, 10000 + episodes)),
            "training_data_origin": "SYNTHETIC_ONLY", "real_assay_labels_used_in_training": False,
            "state_definition": "remaining budget tertile, observed positive-rate bin, known-count bin, two-class flag, pending flag",
            "action_definition": list(BASELINES), "reward": "new delivered active hits - 0.01 * newly settled cost units",
            "alpha": 0.2 if policy == "q_learning" else "1/N(state, action)",
            "gamma": 0.95 if policy == "q_learning" else 0.0,
            "epsilon": "max(0.1, 1 - episode/(episodes*0.85))", "values": values, "counts": counts,
            "episode_returns": rewards, "unseen_state_fallback": "greedy",
            "validation_status": "NO_PHARMACEUTICAL_TRANSFER_CLAIM",
        }
        checkpoint["checkpoint_sha256"] = digest(checkpoint)
        (output / f"{policy}.json").write_text(json.dumps(checkpoint, sort_keys=True, indent=2), encoding="utf-8")
        summaries[policy] = {k: v for k, v in checkpoint.items() if k not in ("values", "counts", "episode_returns", "training_episode_seeds")}
        summaries[policy]["mean_training_return"] = sum(rewards) / len(rewards)
    load_checkpoint.cache_clear()
    return summaries


if __name__ == "__main__":
    print(json.dumps(train_controllers(), indent=2))
