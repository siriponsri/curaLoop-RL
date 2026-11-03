"""Public UI/CLI facade and matched comparisons. No full label table is exposed."""

import json
import platform
import subprocess
import sys
from dataclasses import asdict, replace
from functools import lru_cache
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from . import ALGORITHM_VERSION, SIMULATOR_VERSION, __version__
from .domain import BASELINES, Scenario, Selection, digest
from .engine import Campaign
from .evaluation import curve_from_events, event_rows, metrics_from_events

LIMITATIONS = [
    "Personal independent prototype; not an official GPO project or endorsed system.",
    "Data origin and assay semantics are dataset-specific; retrospective labels are not drug efficacy evidence.",
    "Cost, capacity, delay and missingness are SYNTHETIC_ASSUMPTION; no currency or actual savings.",
    "Seed labels are common preexisting sunk cost and excluded from new hits. Only synthetic seeds are stratified.",
    "Logistic probabilities are uncalibrated; closeness to 0.5 is a heuristic, not validated uncertainty.",
    "Single-seed comparisons illustrate behavior. Multi-seed variability on one assay is not cross-target validation.",
    "Learned controllers train on synthetic tasks only; no validated pharmaceutical transfer, lab integration, Digital Twin or GMP/clinical use.",
    "Built-in policy process separation is not an OS sandbox for hostile code or reconstructed synthetic truth.",
]


@lru_cache(maxsize=1)
def code_identity() -> dict:
    root = Path(__file__).resolve().parents[2]
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL, timeout=3
        ).strip()
        dirty = bool(
            subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=root, text=True, timeout=3
            ).strip()
        )
    except (OSError, subprocess.SubprocessError):
        marker = root / "SOURCE_COMMIT.txt"
        build_info = Path(__file__).with_name("resources") / "build_info.json"
        if marker.exists():
            sha, dirty = marker.read_text().strip(), None
        elif build_info.exists():
            info = json.loads(build_info.read_text(encoding="utf-8"))
            sha, dirty = info["source_commit"], info["source_working_tree_dirty"]
        else:
            sha, dirty = "UNCOMMITTED", None
    source_hash = digest(
        {p.name: p.read_text(encoding="utf-8") for p in sorted(Path(__file__).parent.glob("*.py"))}
    )
    return {"repo_git_sha": sha, "working_tree_dirty": dirty, "source_sha256": source_hash}


def dependency_versions() -> dict:
    result = {}
    for name in ("numpy", "pandas", "scikit-learn", "streamlit", "altair"):
        try:
            result[name] = version(name)
        except PackageNotFoundError:
            result[name] = "NOT_INSTALLED"
    return result


class RunService:
    def __init__(self, scenario: Scenario | None = None, policy: str = "greedy"):
        self.scenario = scenario or Scenario()
        self.policy = policy
        self.__campaign = Campaign(self.scenario, policy)

    @property
    def observation(self):
        return self.__campaign.observe()

    @property
    def dataset(self):
        return self.__campaign.dataset

    @property
    def requests(self):
        return self.__campaign.requests

    @property
    def results(self):
        return self.__campaign.results

    @property
    def initial_results(self):
        return self.__campaign.initial_results

    @property
    def events(self):
        return self.__campaign.events

    @property
    def pending(self):
        return self.__campaign.pending

    @property
    def done(self) -> bool:
        return self.__campaign.done

    @property
    def metrics(self) -> dict:
        return metrics_from_events(
            self.events, self.scenario.budget_units, self.scenario.assay_cost_units
        )

    @property
    def curve(self) -> list[dict]:
        return curve_from_events(self.events, self.scenario.budget_units)

    def next_batch(self):
        return self.__campaign.next_batch()

    def advance(self, steps: int = 1) -> None:
        self.__campaign.advance(steps)

    def finish(self) -> None:
        self.__campaign.finish()

    @classmethod
    def restore(cls, report: dict) -> "RunService":
        """Validate and reconstruct a public snapshot, including pending requests.

        Replays accepted public actions against a fresh private backend. No serialized
        truth or pickle is accepted. Corrupt or incompatible logs fail closed.
        """
        m = report["manifest"]
        restored = cls(Scenario(**m["scenario_config"]), m["policy_id"])
        if restored.dataset.sha256 != m["dataset"]["sha256"]:
            raise ValueError("Dataset hash differs from exported report.")
        groups = {}
        for request in report["requests"]:
            groups.setdefault(request["batch_id"], []).append(request)
        campaign = restored.__campaign
        # A v0.1 lifecycle-description typo called even historical data synthetic.
        # Preserve that exact legacy event when reconciling old snapshots. It is
        # descriptive metadata only; labels, schedules and budget are untouched.
        if (
            report.get("events")
            and report["events"][0].get("event_type") == "RUN_STARTED"
            and report["events"][0].get("explanation")
            == "Original synthetic fixture; no live laboratory."
        ):
            campaign._events = (
                replace(campaign.events[0], explanation=report["events"][0]["explanation"]),
            ) + campaign.events[1:]
        for requests in groups.values():
            step = requests[0]["scheduled_at_step"]
            if step < campaign.step:
                raise ValueError("Non-monotonic request history.")
            if step > campaign.step:
                campaign.advance(step - campaign.step)
            campaign.submit(
                tuple(
                    Selection(
                        r["compound_id"],
                        r["explanation"],
                        r["predicted_probability"],
                        model_status=r["model_status"],
                    )
                    for r in requests
                )
            )
        final_step = report["metrics"]["step"]
        if final_step > campaign.step:
            campaign.advance(final_step - campaign.step)
        if report["events"][-1]["event_type"] == "RUN_STOPPED":
            if not campaign.done:
                raise ValueError("Export claims a stopped campaign with pending work.")
            campaign.finish()
        actual = restored.report()
        for key in ("events", "requests", "delivered_results", "metrics", "curve"):
            if actual[key] != report[key]:
                raise ValueError(f"Public snapshot cannot be reconciled: {key}.")
        return restored

    def report(self) -> dict:
        controller = None
        if self.policy in ("q_learning", "contextual_bandit"):
            from .learning import load_checkpoint

            controller = {
                k: v
                for k, v in load_checkpoint(self.policy).items()
                if k not in ("values", "counts", "episode_returns")
            }
        return {
            "manifest": {
                "schema_version": "1.1",
                "run_id": self.observation.run_id,
                "scenario_id": self.scenario.scenario_id,
                **code_identity(),
                "package_version": __version__,
                "algorithm_version": ALGORITHM_VERSION,
                "simulator_version": SIMULATOR_VERSION,
                "python_version": sys.version.split()[0],
                "platform": platform.system(),
                "dependency_versions": dependency_versions(),
                "dataset": {
                    "name": self.dataset.name,
                    "release": self.dataset.release,
                    "sha256": self.dataset.sha256,
                    "feature_sha256": self.dataset.feature_sha256,
                    "assay_id": self.dataset.assay_id,
                    "label_semantics": self.dataset.label_semantics,
                    "terms_status": self.dataset.terms_status,
                    "source": (
                        json.loads(self.dataset.metadata_json).get(
                            "source_url", "Historical public assay; see dataset_provenance."
                        )
                        if self.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
                        else "Original in-process synthetic generator; no external data."
                    ),
                    "preprocessing": "StandardScaler fitted only to revealed training rows.",
                },
                "data_origin": self.dataset.data_origin,
                "scenario_origin": "SYNTHETIC_ASSUMPTION",
                "policy_id": self.policy,
                "seed": self.scenario.seed,
                "budget_units": self.scenario.budget_units,
                "batch_size": self.scenario.batch_size,
                "initial_label_ids": [r.compound_id for r in self.initial_results],
                "initial_labels_budget_rule": "PREEXISTING_SUNK_COST",
                "initial_label_selection": (
                    "Uniform random without using labels"
                    if self.dataset.data_origin == "HISTORICAL_PUBLIC_DATA"
                    else "Deterministic synthetic-only stratification; disclosed oracle intervention."
                ),
                "algorithm_status": controller["status"] if controller else "BASELINE_IMPLEMENTED",
                "controller": controller,
                "digital_twin_maturity": "RETROSPECTIVE_SIMULATOR",
                "scenario_config": asdict(self.scenario),
                "finished": self.done,
                "scheduler": "At most batch_size concurrent pending assays; settle each result at its due step.",
                "cost_note": "Reserve on request; settle on delivery or missing outcome; no refunds.",
                "delay_note": "Integer simulated steps; deterministic nonnegative per-candidate jitter.",
                "dataset_provenance": json.loads(self.dataset.metadata_json),
                "limitations": LIMITATIONS
                + (
                    [
                        "Legacy RUN_STARTED description retained for exact replay; dataset origin and hashes identify the real source."
                    ]
                    if self.events[0].explanation
                    == "Original synthetic fixture; no live laboratory."
                    else []
                ),
            },
            "initial_results": [asdict(r) for r in self.initial_results],
            "requests": [asdict(r) for r in self.requests],
            "delivered_results": [asdict(r) for r in self.results],
            "events": event_rows(self.events),
            "metrics": self.metrics,
            "curve": self.curve,
        }


def compare(scenario: Scenario, policies: tuple[str, ...] = BASELINES) -> list[dict]:
    reports = []
    for policy in policies:
        run = RunService(scenario, policy)
        run.finish()
        reports.append(run.report())
    manifests = [r["manifest"] for r in reports]
    for key in ("dataset", "initial_label_ids", "scenario_config", "algorithm_version"):
        if any(m[key] != manifests[0][key] for m in manifests[1:]):
            raise RuntimeError("Comparison parity failed for " + key)
    return reports


def evaluate_seeds(scenario: Scenario, seeds: list[int]) -> dict:
    if len(seeds) != len(set(seeds)) or not seeds:
        raise ValueError("Provide one or more distinct paired seeds.")
    runs = [r for seed in seeds for r in compare(replace(scenario, seed=seed))]
    return {
        "schema_version": "1.1",
        "evaluation": "PAIRED_SYNTHETIC_SEEDS",
        "seeds": seeds,
        "runs": runs,
        "limitations": LIMITATIONS,
    }
