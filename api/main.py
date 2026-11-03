"""Local FastAPI application; in-memory, isolated sessions over the existing engine."""

import hashlib
import json
import threading
from concurrent.futures import ThreadPoolExecutor
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


@dataclass
class Session:
    run: RunService
    revision: int = 0
    lock: threading.Lock = field(default_factory=threading.Lock)


def public_view(session_id: str, session: Session) -> dict:
    obs = session.run.observation
    return {
        "session_id": session_id,
        "revision": session.revision,
        "done": session.run.done,
        "report": session.run.report(),
        "pending": [asdict(r) for r in session.run.pending],
        "eligible_count": len(obs.eligible_candidate_ids),
        "can_select": bool(
            not session.run.done
            and obs.eligible_candidate_ids
            and obs.slots_available
            and obs.budget_remaining_units >= obs.assay_cost_units
        ),
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


def create_app() -> FastAPI:
    app = FastAPI(
        title="CuraLoop-RL Local API",
        version="0.2.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
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
        session = app.state.sessions.get(session_id)
        if session is None:
            raise HTTPException(
                404,
                "Session unavailable. Sessions live in memory; create or resume a run after restart.",
            )
        return session

    @app.get("/api/v1/health")
    def health():
        return {
            "status": "ok",
            "service": "curaloop-local",
            "version": "0.2.0",
            "sessions_persistent": False,
        }

    @app.get("/api/v1/meta")
    def meta():
        return {
            **code_identity(),
            "frontend_build_sha256": frontend_identity(),
            "web_version": "0.2.0",
            "engine_version": __version__,
            "limitations": LIMITATIONS,
            "digital_twin_maturity": "RETROSPECTIVE_SIMULATOR",
            "molecule_rendering": find_spec("rdkit") is not None,
            "session_note": "In-memory local sessions. Export JSON to resume after server restart.",
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
        session = Session(RunService(body.scenario.domain(), body.policy))
        with app.state.registry_lock:
            if len(app.state.sessions) >= 40:
                raise HTTPException(
                    429, "40 local sessions reached. Close an old run or restart after exporting."
                )
            session_id = uuid4().hex
            app.state.sessions[session_id] = session
        return public_view(session_id, session)

    @app.get("/api/v1/runs/{session_id}", response_model=RunView)
    def read_run(session_id: str):
        session = get_session(session_id)
        with session.lock:
            return public_view(session_id, session)

    @app.delete("/api/v1/runs/{session_id}", status_code=204)
    def delete_run(session_id: str):
        session = get_session(session_id)
        with session.lock, app.state.registry_lock:
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
            run = session.run
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
                session.run = RunService(run.scenario, run.policy)
            else:
                session.run = RunService.restore(run.report())
            session.revision += 1
            return public_view(session_id, session)
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
            report = session.run.report()
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
            restored = RunService.restore(body["runs"][0])
        except (ValueError, TypeError, KeyError, IndexError) as exc:
            raise HTTPException(422, str(exc)) from exc
        with app.state.registry_lock:
            if len(app.state.sessions) >= 40:
                raise HTTPException(429, "Local session limit reached.")
            session_id = uuid4().hex
            session = Session(restored)
            app.state.sessions[session_id] = session
        return public_view(session_id, session)

    def execute_comparison(job_id: str, body: CompareInput):
        job = app.state.jobs[job_id]
        job["status"] = "running"
        try:
            job["reports"] = compare(body.scenario.domain(), tuple(body.policies))
            job["status"] = "completed"
        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)

    @app.post("/api/v1/comparisons", status_code=202)
    def comparisons(body: CompareInput):
        with app.state.registry_lock:
            if sum(j["status"] in ("queued", "running") for j in app.state.jobs.values()) >= 2:
                raise HTTPException(429, "Two CPU comparison jobs are already running.")
            if len(app.state.jobs) >= 20:
                raise HTTPException(
                    429, "Comparison history limit reached; export then restart to clear."
                )
            job_id = uuid4().hex
            app.state.jobs[job_id] = {
                "job_id": job_id,
                "status": "queued",
                "scenario": body.scenario.model_dump(),
                "policies": body.policies,
                "reports": [],
                "error": None,
            }
        app.state.executor.submit(execute_comparison, job_id, body)
        return {"job_id": job_id, "status": "queued"}

    @app.get("/api/v1/comparisons/{job_id}")
    def comparison(job_id: str):
        job = app.state.jobs.get(job_id)
        if job is None:
            raise HTTPException(404, "Comparison unavailable after restart.")
        return job

    @app.get("/api/v1/comparisons/{job_id}/export")
    def export_comparison(job_id: str, format: Literal["json", "csv"] = "json"):
        job = app.state.jobs.get(job_id)
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
