"""Loopback FastAPI adapter with durable public snapshots over the existing engine."""

import hashlib
import json
import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from functools import lru_cache
from importlib.util import find_spec
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, StrictInt, model_validator

from curaloop import __version__
from curaloop.domain import BASELINES, DATASETS, POLICIES, Scenario
from curaloop.export import csv_report, json_report
from curaloop.learning import load_checkpoint
from curaloop.service import LIMITATIONS, RunService, code_identity, compare
from curaloop_rd.confirmation_study import StudyUnavailable, comparison_brief
from curaloop_rd.confirmation_study import view as confirmation_view

from .storage import (
    RECOVERY_HELP,
    SCHEMA_VERSION,
    CapacityError,
    SnapshotStore,
    StaleRevision,
    StorageError,
    decode,
)

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = "hiv_moleculenet_replay_v1"


class ScenarioInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset: Literal["hiv_moleculenet_replay_v1", "synthetic_linear_v1", "synthetic_shift_v1"] = (
        HISTORICAL
    )
    seed: StrictInt = Field(42, ge=0, le=2**32 - 1)
    candidate_count: StrictInt = Field(1200, ge=0, le=2000)
    initial_count: StrictInt = Field(48, ge=0, le=2000)
    budget_units: StrictInt = Field(30, ge=0, le=10000)
    batch_size: StrictInt = Field(5, ge=1, le=100)
    delay_steps: StrictInt = Field(2, ge=0, le=100)
    assay_cost_units: StrictInt = Field(1, ge=1, le=100)
    delay_jitter: StrictInt = Field(0, ge=0, le=20)
    missing_percent: StrictInt = Field(0, ge=0, le=100)

    @model_validator(mode="after")
    def domain_validation(self):
        Scenario(**self.model_dump())
        return self

    def domain(self) -> Scenario:
        return Scenario(**self.model_dump())


class CreateRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: ScenarioInput = Field(default_factory=ScenarioInput)
    policy: Literal["random", "greedy", "uncertainty", "q_learning", "contextual_bandit"] = "greedy"


class Mutation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: StrictInt = Field(ge=0)
    steps: StrictInt = Field(1, ge=1, le=1000)


class CompareInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    scenario: ScenarioInput
    policies: list[
        Literal["random", "greedy", "uncertainty", "q_learning", "contextual_bandit"]
    ] = Field(default_factory=lambda: list(BASELINES), min_length=1, max_length=5)

    @model_validator(mode="after")
    def unique(self):
        if len(self.policies) != len(set(self.policies)):
            raise ValueError("Duplicate policies are not allowed.")
        return self


class RunView(BaseModel):
    session_id: str
    revision: int
    done: bool
    report: dict
    pending: list[dict]
    eligible_count: int
    can_select: bool
    persistence: dict = Field(default_factory=dict)


class RecoverRun(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str
    revision: StrictInt = Field(ge=0)


@dataclass
class Session:
    run: RunService
    revision: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)
    snapshot: dict = field(default_factory=dict)
    persistence: dict = field(default_factory=dict)


def public_view(session_id: str, session: Session) -> dict:
    obs = session.run.observation
    return {
        "session_id": session_id,
        "revision": session.revision,
        "done": session.run.done,
        "report": session.snapshot or session.run.report(),
        "pending": [asdict(r) for r in session.run.pending],
        "eligible_count": len(obs.eligible_candidate_ids),
        "can_select": bool(
            not session.run.done
            and obs.eligible_candidate_ids
            and obs.slots_available
            and obs.budget_remaining_units >= obs.assay_cost_units
        ),
        "persistence": session.persistence,
    }


@lru_cache(maxsize=256)
def molecule_svg(smiles: str) -> str:
    from rdkit import Chem
    from rdkit.Chem.Draw import rdMolDraw2D

    molecule = Chem.MolFromSmiles(smiles)
    if molecule is None:
        raise ValueError("Canonical structure could not be rendered.")
    drawer = rdMolDraw2D.MolDraw2DSVG(380, 260)
    drawer.drawOptions().clearBackground = False
    rdMolDraw2D.PrepareAndDrawMolecule(drawer, molecule)
    drawer.FinishDrawing()
    return drawer.GetDrawingText()


@lru_cache(maxsize=1)
def frontend_identity():
    """Content identity of the built local frontend, separate from engine source."""
    folder = ROOT / "frontend" / "dist"
    if not folder.exists():
        return None
    digest = hashlib.sha256()
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        digest.update(path.relative_to(folder).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


@lru_cache(maxsize=1)
def api_identity() -> str:
    """Adapter/storage source identity, kept separate from scientific-engine source."""
    digest = hashlib.sha256()
    for path in sorted(Path(__file__).parent.glob("*.py")):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


IDENTITY_FIELDS = (
    "repo_git_sha",
    "working_tree_dirty",
    "source_sha256",
    "package_version",
    "algorithm_version",
    "simulator_version",
    "python_version",
    "platform",
    "dependency_versions",
)

SCIENTIFIC_MANIFEST_FIELDS = (
    "schema_version",
    "run_id",
    "scenario_id",
    "algorithm_version",
    "simulator_version",
    "dataset",
    "data_origin",
    "scenario_origin",
    "policy_id",
    "seed",
    "budget_units",
    "batch_size",
    "initial_label_ids",
    "initial_labels_budget_rule",
    "initial_label_selection",
    "algorithm_status",
    "controller",
    "digital_twin_maturity",
    "scenario_config",
    "finished",
    "dataset_provenance",
    "scheduler",
    "cost_note",
    "delay_note",
)


def creation_identity(report: dict) -> dict:
    return {key: report["manifest"][key] for key in IDENTITY_FIELDS if key in report["manifest"]}


def reconcile(report: dict) -> RunService:
    if not isinstance(report, dict) or not isinstance(report.get("manifest"), dict):
        raise ValueError("Public snapshot must contain a manifest object.")
    for key, kind in (
        ("requests", list),
        ("events", list),
        ("metrics", dict),
        ("curve", list),
        ("initial_results", list),
        ("delivered_results", list),
    ):
        if not isinstance(report.get(key), kind):
            raise ValueError(f"Public snapshot has an invalid {key} section.")
        if kind is list and any(not isinstance(row, dict) for row in report[key]):
            raise ValueError(f"Public snapshot {key} records must be objects.")
    if report["manifest"].get("schema_version") != "1.1":
        raise ValueError("Unsupported public snapshot schema; expected 1.1.")
    restored = RunService.restore(report)
    actual = restored.report()
    if report["initial_results"] != actual["initial_results"]:
        raise ValueError("Public snapshot cannot be reconciled: initial_results.")
    # RunService owns reconstruction; this boundary additionally checks metadata
    # that its event reconciliation does not compare. Only execution identity and
    # explanatory limitations may differ between the stored and current report.
    for key in SCIENTIFIC_MANIFEST_FIELDS:
        if report["manifest"].get(key) != actual["manifest"][key]:
            raise ValueError(f"Public snapshot has inconsistent scientific metadata: {key}.")
    return restored


def reconcile_job(job: dict) -> dict:
    try:
        if job.get("status") not in ("queued", "running", "completed", "failed", "interrupted"):
            raise ValueError("Invalid saved comparison status.")
        body = CompareInput(scenario=job["scenario"], policies=job["policies"])
        if not isinstance(job.get("job_id"), str) or not isinstance(job.get("reports"), list):
            raise ValueError("Invalid saved comparison structure.")
        if job["status"] == "completed":
            if len(job["reports"]) != len(body.policies):
                raise ValueError("Completed comparison has an incomplete policy set.")
            for policy, report in zip(body.policies, job["reports"], strict=True):
                restored = reconcile(report)
                if restored.policy != policy or restored.scenario != body.scenario.domain():
                    raise ValueError("Saved comparison conditions differ between policies.")
        elif job["reports"]:
            raise ValueError("An unfinished comparison cannot claim completed reports.")
    except (ValueError, TypeError, KeyError, IndexError, RuntimeError) as exc:
        raise StorageError("Saved comparison cannot be reconciled. " + RECOVERY_HELP) from exc
    return job


def create_app(storage_path: str | Path | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        app.state.executor.shutdown(wait=True)

    app = FastAPI(
        title="CuraLoop-RL Local API",
        version="0.3.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type"],
        allow_credentials=False,
    )
    app.state.sessions = {}
    app.state.jobs = {}
    app.state.registry_lock = threading.Lock()
    app.state.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="curaloop-local")
    app.state.storage_error = None
    app.state.recovery_issues = []
    try:
        app.state.storage = SnapshotStore(
            storage_path
            or os.environ.get("CURALOOP_STORAGE_PATH")
            or ROOT / ".local/curaloop.sqlite3"
        )
        # A process restart cannot prove whether an unfinished CPU job completed.
        # Preserve its record and require an explicit new comparison; never resubmit it.
        for row in app.state.storage.job_records():
            try:
                job = reconcile_job(decode(row["snapshot"], row["checksum"]))
                if job["job_id"] != row["job_id"]:
                    raise StorageError("Saved comparison identifier differs. " + RECOVERY_HELP)
                if job["status"] in ("queued", "running"):
                    previous = job["status"]
                    job.update(
                        status="interrupted",
                        reports=[],
                        error=(
                            "The server stopped before this comparison committed. No completed result "
                            "was saved. Run a new comparison explicitly; this job was not replayed."
                        ),
                    )
                    app.state.storage.update_job(job, previous)
            except (StorageError, ValueError, TypeError, KeyError) as exc:
                app.state.recovery_issues.append(
                    {"kind": "comparison", "id": row["job_id"], "message": str(exc)}
                )
    except StorageError as exc:
        app.state.storage = None
        app.state.storage_error = str(exc)

    def storage() -> SnapshotStore:
        if app.state.storage is None:
            raise HTTPException(503, app.state.storage_error)
        return app.state.storage

    @app.exception_handler(StorageError)
    async def storage_failure(_request: Request, exc: StorageError):
        status = (
            409
            if isinstance(exc, StaleRevision)
            else 429
            if isinstance(exc, CapacityError)
            else 503
        )
        return JSONResponse({"detail": str(exc)}, status_code=status)

    def saved_session(row: dict) -> Session:
        report = decode(row["snapshot"], row["checksum"])
        try:
            run = reconcile(report)
            original = json.loads(row["creation_identity"])
            if not isinstance(original, dict):
                raise ValueError("Creation identity must be an object.")
        except (ValueError, TypeError, KeyError, IndexError, RuntimeError) as exc:
            raise StorageError("Saved campaign cannot be reconciled. " + RECOVERY_HELP) from exc
        return Session(
            run,
            revision=row["revision"],
            snapshot=report,
            persistence={
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "creation_identity": original,
                "recovered": True,
                "identity_note": "Creation identity is retained; actions after recovery use the current implementation.",
            },
        )

    def add_session(run: RunService, identity: dict | None = None) -> dict:
        report = run.report()
        session_id = uuid4().hex
        storage().create_run(session_id, report, identity or creation_identity(report))
        row = storage().run_record(session_id)
        session = Session(
            run,
            snapshot=report,
            persistence={
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "creation_identity": json.loads(row["creation_identity"]),
                "recovered": False,
                "identity_note": "Creation identity is retained; actions after recovery use the current implementation.",
            },
        )
        with app.state.registry_lock:
            app.state.sessions[session_id] = session
        return public_view(session_id, session)

    def get_job(job_id: str) -> dict | None:
        job = storage().job(job_id)
        if job is None:
            return None
        if job.get("job_id") != job_id:
            raise StorageError("Saved comparison identifier differs. " + RECOVERY_HELP)
        if app.state.jobs.get(job_id) != job:
            reconcile_job(job)
            app.state.jobs[job_id] = job
        return job

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        host = request.headers.get("host", "").split(":")[0]
        if host not in ("127.0.0.1", "localhost", "testserver"):
            return JSONResponse({"detail": "Localhost host only."}, status_code=403)
        origin = request.headers.get("origin")
        if origin and origin not in (
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ):
            return JSONResponse({"detail": "External origin refused."}, status_code=403)
        if int(request.headers.get("content-length", "0")) > 10_000_000:
            return JSONResponse({"detail": "Request exceeds 10 MB."}, status_code=413)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    def get_session(session_id: str) -> Session:
        row = storage().run_record(session_id)
        if row is None:
            raise HTTPException(
                404,
                "Saved campaign was not found. Open another saved campaign or import a single-run JSON.",
            )
        with app.state.registry_lock:
            session = app.state.sessions.get(session_id)
            # Check the bytes even when a decoded engine is cached, so corruption is visible.
            decode(row["snapshot"], row["checksum"])
            if session is None or session.revision != row["revision"]:
                session = saved_session(row)
                app.state.sessions[session_id] = session
            return session

    @app.get("/api/v1/health")
    def health():
        return {
            "status": "degraded" if app.state.storage_error else "ok",
            "service": "curaloop-local",
            "version": "0.3.0",
            "sessions_persistent": app.state.storage is not None,
            "storage_status": "unavailable" if app.state.storage_error else "ok",
            "storage_error": app.state.storage_error,
        }

    @app.get("/api/v1/meta")
    def meta():
        return {
            **code_identity(),
            "frontend_build_sha256": frontend_identity(),
            "api_source_sha256": api_identity(),
            "web_version": "0.3.0",
            "engine_version": __version__,
            "limitations": LIMITATIONS,
            "digital_twin_maturity": "RETROSPECTIVE_SIMULATOR",
            "molecule_rendering": find_spec("rdkit") is not None,
            "session_note": "Campaigns and comparisons are saved locally in SQLite. Single-run JSON remains portable recovery; comparison JSON and CSV cannot resume one campaign.",
            "storage": {
                "schema_version": SCHEMA_VERSION,
                "status": "unavailable" if app.state.storage_error else "ok",
                "error": app.state.storage_error,
                "recovery_help": RECOVERY_HELP,
            },
            "test_evidence": {
                "historical_python_tests": 79,
                "historical_claim": "Previous v0.1 evidence; new rebuild verification is recorded separately in docs/evidence/web-v2.",
            },
        }

    @app.get("/api/v1/datasets")
    def datasets():
        return [
            {
                "id": d,
                "name": "MoleculeNet HIV"
                if d == HISTORICAL
                else d.replace("_v1", "").replace("_", " "),
                "data_origin": "HISTORICAL_PUBLIC_DATA" if d == HISTORICAL else "SYNTHETIC_ONLY",
                "candidate_count": 1200 if d == HISTORICAL else 240,
                "default_initial_count": 48 if d == HISTORICAL else 12,
                "feature_description": "Morgan radius 2 · 1024 bits"
                if d == HISTORICAL
                else "12 numerical synthetic descriptors",
            }
            for d in DATASETS
        ]

    @app.get("/api/v1/policies")
    def policies():
        rows = []
        for p in POLICIES:
            cp = load_checkpoint(p) if p not in BASELINES else None
            rows.append(
                {
                    "id": p,
                    "status": cp["status"] if cp else "BASELINE_IMPLEMENTED",
                    "training_episodes": cp["training_episodes"] if cp else None,
                    "checkpoint_sha256": cp["checkpoint_sha256"] if cp else None,
                    "warning": "Synthetic training only; historical replay used unseen-state Greedy fallback."
                    if cp
                    else None,
                }
            )
        return rows

    @app.post("/api/v1/runs", response_model=RunView, status_code=201)
    def create_run(body: CreateRun):
        return add_session(RunService(body.scenario.domain(), body.policy))

    @app.get("/api/v1/runs")
    def saved_runs():
        items, issues = [], []
        for row in storage().run_records():
            try:
                session = get_session(row["session_id"])
                report = session.snapshot
                items.append(
                    {
                        "session_id": row["session_id"],
                        "revision": row["revision"],
                        "dataset": report["manifest"]["scenario_config"]["dataset"],
                        "policy": report["manifest"]["policy_id"],
                        "done": session.run.done,
                        "pending_assays": report["metrics"]["pending_assays"],
                        "spent_units": report["metrics"]["spent_units"],
                        "updated_at": row["updated_at"],
                    }
                )
            except StorageError as exc:
                issues.append({"kind": "run", "id": row["session_id"], "message": str(exc)})
        return {
            "items": items,
            "recovery_issues": issues,
            "storage": {"schema_version": SCHEMA_VERSION, "status": "ok"},
        }

    @app.get("/api/v1/runs/{session_id}/revisions")
    def saved_revisions(session_id: str):
        if storage().run_record(session_id) is None:
            raise HTTPException(404, "Saved campaign was not found.")
        return {"session_id": session_id, "items": storage().revisions(session_id)}

    @app.post("/api/v1/recovery/runs", response_model=RunView, status_code=201)
    def recover_revision(body: RecoverRun):
        report = storage().revision_report(body.session_id, body.revision)
        if report is None:
            raise HTTPException(404, "Saved revision was not found.")
        try:
            run = reconcile(report)
        except (ValueError, TypeError, KeyError, IndexError, RuntimeError) as exc:
            raise HTTPException(
                422, "Saved revision cannot be reconciled. " + RECOVERY_HELP
            ) from exc
        # Recovery always creates an independent campaign. It never rolls back or
        # rewrites a newer committed campaign, including a corrupt current row.
        return add_session(run, creation_identity(report))

    @app.get("/api/v1/runs/{session_id}", response_model=RunView)
    def read_run(session_id: str):
        session = get_session(session_id)
        with session.lock:
            return public_view(session_id, session)

    @app.delete("/api/v1/runs/{session_id}", status_code=204)
    def delete_run(session_id: str):
        # Explicit removal must also work for an unreconcilable saved snapshot.
        # Look up a cached lock without rebuilding scientific state, then retain
        # the same session-lock -> registry-lock ordering used by normal removal.
        with app.state.registry_lock:
            cached = app.state.sessions.get(session_id)
        lock = cached.lock if cached is not None else threading.Lock()
        with lock, app.state.registry_lock:
            if storage().run_record(session_id) is None:
                raise HTTPException(404, "Saved campaign was not found.")
            storage().delete_run(session_id)
            app.state.sessions.pop(session_id, None)
        return Response(status_code=204)

    @app.post("/api/v1/runs/{session_id}/{action}", response_model=RunView)
    def mutate(
        session_id: str,
        action: Literal["select", "advance", "finish", "reset", "replay"],
        body: Mutation,
    ):
        session = get_session(session_id)
        if not session.lock.acquire(blocking=False):
            raise HTTPException(409, "This run is busy; wait for the current action.")
        try:
            if session.revision != body.expected_revision:
                raise HTTPException(
                    409, "Stale action rejected. Refresh the run; it was not charged twice."
                )
            # Only a public snapshot is cloned. Mutating a candidate before the
            # transaction commits keeps both cache and disk unchanged on failure.
            run = reconcile(session.snapshot)
            if action == "select":
                obs = run.observation
                if (
                    run.done
                    or not obs.slots_available
                    or not obs.eligible_candidate_ids
                    or obs.budget_remaining_units < obs.assay_cost_units
                ):
                    raise HTTPException(
                        409,
                        "No selection is available; advance pending feedback or change the scenario.",
                    )
                run.next_batch()
            elif action == "advance":
                if not run.pending:
                    raise HTTPException(409, "No pending feedback to advance.")
                run.advance(body.steps)
            elif action == "finish":
                run.finish()
            elif action == "reset":
                run = RunService(run.scenario, run.policy)
            else:
                run = reconcile(session.snapshot)
            report = run.report()
            storage().update_run(session_id, body.expected_revision, report)
            session.run = run
            session.snapshot = report
            session.revision += 1
            session.persistence["updated_at"] = storage().run_record(session_id)["updated_at"]
            return public_view(session_id, session)
        except StorageError:
            raise
        except (ValueError, RuntimeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        finally:
            session.lock.release()

    @app.get("/api/v1/runs/{session_id}/candidates")
    def candidates(
        session_id: str,
        search: str = Query("", max_length=120),
        status: Literal["all", "eligible", "seed", "pending", "delivered", "missing"] = "all",
        sort: Literal["id", "feature_count"] = "id",
        descending: bool = False,
        page: int = Query(1, ge=1),
        page_size: int = Query(12, ge=1, le=100),
    ):
        session = get_session(session_id)
        with session.lock:
            run = session.run
            known = {r.compound_id: r for r in run.initial_results + run.results}
            seeds = {r.compound_id for r in run.initial_results}
            pending = {r.compound_id for r in run.pending}
            requests = {r.compound_id: r for r in run.requests}
            rows = []
            for c in run.dataset.candidates:
                result = known.get(c.compound_id)
                state = (
                    "seed"
                    if c.compound_id in seeds
                    else "pending"
                    if c.compound_id in pending
                    else ("missing" if result.active is None else "delivered")
                    if result
                    else "eligible"
                )
                if search.lower() not in c.compound_id.lower() or status not in ("all", state):
                    continue
                r = requests.get(c.compound_id)
                rows.append(
                    {
                        "compound_id": c.compound_id,
                        "status": state,
                        "canonical_smiles": c.canonical_smiles,
                        "scaffold_id": c.scaffold_id,
                        "feature_count": len(c.features),
                        "feature_nonzero": sum(v != 0 for v in c.features),
                        "public_features_preview": list(c.features[:8]),
                        "revealed_active": result.active if result else None,
                        "predicted_probability": r.predicted_probability if r else None,
                        "explanation": r.explanation if r else None,
                    }
                )
            rows.sort(
                key=lambda r: (
                    r["feature_nonzero"] if sort == "feature_count" else r["compound_id"],
                    r["compound_id"],
                ),
                reverse=descending,
            )
            total = len(rows)
            return {
                "items": rows[(page - 1) * page_size : page * page_size],
                "total": total,
                "page": page,
                "page_size": page_size,
            }

    @app.get("/api/v1/runs/{session_id}/molecules/{compound_id}.svg")
    def molecule(session_id: str, compound_id: str):
        session = get_session(session_id)
        candidate = next(
            (c for c in session.run.dataset.candidates if c.compound_id == compound_id), None
        )
        if candidate is None:
            raise HTTPException(404, "Unknown compound.")
        if not candidate.canonical_smiles:
            raise HTTPException(404, "Synthetic descriptors have no molecular structure.")
        if find_spec("rdkit") is None:
            raise HTTPException(
                501, "Optional RDKit is unavailable; numerical descriptors still work."
            )
        return Response(molecule_svg(candidate.canonical_smiles), media_type="image/svg+xml")

    @app.get("/api/v1/runs/{session_id}/export")
    def export_run(session_id: str, format: Literal["json", "csv"] = "json"):
        session = get_session(session_id)
        with session.lock:
            report = session.snapshot
            payload = json_report([report]) if format == "json" else csv_report([report])
        return Response(
            payload.encode("utf-8-sig" if format == "csv" else "utf-8"),
            media_type="application/json" if format == "json" else "text/csv",
            headers={"Content-Disposition": f'attachment; filename="curaloop-run.{format}"'},
        )

    @app.post("/api/v1/resume", response_model=RunView, status_code=201)
    def resume(body: dict):
        try:
            if len(body.get("runs", [])) != 1:
                raise ValueError("Resume requires a single-run public JSON export.")
            restored = reconcile(body["runs"][0])
        except (ValueError, TypeError, KeyError, IndexError, RuntimeError) as exc:
            raise HTTPException(422, str(exc)) from exc
        return add_session(restored, creation_identity(body["runs"][0]))

    def execute_comparison(job_id: str, body: CompareInput):
        try:
            job = storage().job(job_id)
            job["status"] = "running"
            storage().update_job(job, "queued")
            job["reports"] = compare(body.scenario.domain(), tuple(body.policies))
            job["status"] = "completed"
            storage().update_job(job, "running")
        except Exception as exc:
            try:
                current = storage().job(job_id)
                if current and current["status"] in ("queued", "running"):
                    previous = current["status"]
                    current.update(status="failed", reports=[], error=str(exc))
                    storage().update_job(current, previous)
            except (StorageError, HTTPException):
                logging.getLogger(__name__).exception(
                    "Comparison could not commit its failure state"
                )

    @app.post("/api/v1/comparisons", status_code=202)
    def comparisons(body: CompareInput):
        job_id = uuid4().hex
        storage().create_job(
            {
                "job_id": job_id,
                "status": "queued",
                "scenario": body.scenario.model_dump(),
                "policies": body.policies,
                "reports": [],
                "error": None,
            }
        )
        try:
            app.state.executor.submit(execute_comparison, job_id, body)
        except RuntimeError as exc:
            job = storage().job(job_id)
            job.update(status="failed", error="The local comparison executor is unavailable.")
            storage().update_job(job, "queued")
            raise HTTPException(503, job["error"]) from exc
        return {"job_id": job_id, "status": "queued"}

    @app.get("/api/v1/comparisons")
    def saved_comparisons():
        items, issues = [], []
        for row in storage().job_records():
            try:
                items.append(get_job(row["job_id"]))
            except StorageError as exc:
                issues.append({"kind": "comparison", "id": row["job_id"], "message": str(exc)})
        return {"items": items, "recovery_issues": issues}

    @app.get("/api/v1/comparisons/{job_id}")
    def comparison(job_id: str):
        job = get_job(job_id)
        if job is None:
            raise HTTPException(404, "Saved comparison was not found.")
        return job

    @app.delete("/api/v1/comparisons/{job_id}", status_code=204)
    def delete_comparison(job_id: str):
        job = storage().job(job_id)
        if job is None:
            raise HTTPException(404, "Saved comparison was not found.")
        if not storage().delete_job(job_id):
            raise HTTPException(409, "A queued or running comparison cannot be removed.")
        return Response(status_code=204)

    @app.get("/api/v1/comparisons/{job_id}/export")
    def export_comparison(job_id: str, format: Literal["json", "csv"] = "json"):
        job = get_job(job_id)
        if job is None:
            raise HTTPException(404, "Unknown comparison.")
        if job["status"] != "completed":
            raise HTTPException(409, "Wait until the real comparison completes.")
        payload = json_report(job["reports"]) if format == "json" else csv_report(job["reports"])
        return Response(
            payload.encode("utf-8-sig" if format == "csv" else "utf-8"),
            media_type="application/json" if format == "json" else "text/csv",
            headers={"Content-Disposition": f'attachment; filename="curaloop-comparison.{format}"'},
        )

    @app.get("/api/v1/studies/cf1")
    def cf1_study(request: Request, campaign: str = "equal", budget_percent: int = 10):
        if set(request.query_params) - {"campaign", "budget_percent"} or len(request.query_params.multi_items()) != len(request.query_params):
            raise HTTPException(status_code=422, detail="Unexpected or repeated study filters")
        try:
            return confirmation_view(campaign, budget_percent)
        except StudyUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/studies/cf1/export")
    def cf1_brief(request: Request, campaign: str = "equal", budget_percent: int = 10,
                  ranker: str = "mvsa", operator: str = "top_ranked", locale: str = "en"):
        if set(request.query_params) - {"campaign", "budget_percent", "ranker", "operator", "locale"} or len(request.query_params.multi_items()) != len(request.query_params):
            raise HTTPException(status_code=422, detail="Unexpected or repeated study filters")
        try:
            brief = comparison_brief(campaign, budget_percent, ranker, operator, locale)
            return Response(json.dumps(brief, ensure_ascii=False, allow_nan=False), media_type="application/json",
                            headers={"Content-Disposition": 'attachment; filename="curaloop-cf1-comparison.json"'})
        except StudyUnavailable as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/v1/evidence")
    def evidence():
        summary = json.loads((ROOT / "docs/evidence/hiv-benchmark/summary.json").read_text())
        predictor = {
            k: v
            for k, v in summary["predictor_benchmark"].items()
            if k not in ("train_ids", "test_ids")
        }
        return {
            "recorded_release": "v0.1",
            "label": "Recorded historical benchmark; not a new execution by opening this page.",
            "statistics": summary["statistics"],
            "seeds": summary["seeds"],
            "scenario": summary["scenario_template"],
            "predictor": predictor,
            "controller_historical_fallback": "300 / 300 requests for each learned controller",
            "source_links": [
                {"title": "MoleculeNet paper", "url": "https://doi.org/10.1039/C7SC02664A"},
                {
                    "title": "TDC dataset & license",
                    "url": "https://tdcommons.ai/single_pred_tasks/hts/#hiv",
                },
            ],
            "controllers": [
                {
                    k: v
                    for k, v in load_checkpoint(p).items()
                    if k not in ("values", "counts", "training_episode_seeds")
                }
                for p in ("q_learning", "contextual_bandit")
            ],
        }

    static = ROOT / "frontend/dist"
    if static.exists():
        app.mount("/assets", StaticFiles(directory=static / "assets"), name="web-assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str):
            if path.startswith("api/"):
                raise HTTPException(404, "Unknown API endpoint.")
            file = (static / path).resolve()
            if static.resolve() in file.parents and file.is_file():
                return FileResponse(file)
            return FileResponse(static / "index.html")

    return app


app = create_app()
