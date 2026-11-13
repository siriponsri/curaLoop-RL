"""Additive local molecular workflow API, using the existing single agent queue."""

import csv
import json
import sqlite3
import threading
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from curaloop_rd.local_agent_v1.chemistry import validate_csv
from curaloop_rd.local_agent_v1.engine import LocalWorkflowEngine
from curaloop_rd.local_agent_v1.provider import configured_provider
from curaloop_rd.local_agent_v1.store import TERMINAL, JobConflict, JobStore
from curaloop_rd.local_agent_v1.workflow import inspect_bundle


class Parameters(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    molecular_weight_max: float = Field(500, gt=0, le=2000, strict=True)
    logp_max: float = Field(5, ge=-20, le=20, strict=True)
    tpsa_max: float = Field(140, ge=0, le=1000, strict=True)


class CreateWorkflow(BaseModel):
    model_config = ConfigDict(extra="forbid")
    csv_text: str = Field(min_length=1, max_length=1024**2)
    goal: str = Field(default="Apply the recorded physicochemical limits", max_length=2000)
    parameters: Parameters = Field(default_factory=Parameters)
    mode: Literal["deterministic", "agent"] = "deterministic"
    locale: Literal["en", "th"] = "en"


class JobAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: StrictInt = Field(ge=0)


def install_local_workflow_routes(app, root):
    try:
        store = JobStore(root)
        store.recover_interrupted()
    except (OSError, ValueError, sqlite3.Error):
        unavailable = APIRouter(prefix="/api/v1/local-workflow")

        @unavailable.api_route("/{path:path}", methods=["GET", "POST"])
        def storage_unavailable(path: str):
            raise HTTPException(
                503,
                "Local workflow storage needs review; original files and other workspaces are retained",
            )

        app.state.local_workflow_store = None
        app.state.local_workflow_provider = None
        app.include_router(unavailable)
        return
    app.state.local_workflow_store = store
    try:
        app.state.local_workflow_provider = configured_provider()
    except (OSError, ValueError):
        app.state.local_workflow_provider = None
    executor = app.state.agent_executor or app.state.executor
    lock = threading.RLock()
    active = {}
    router = APIRouter(prefix="/api/v1/local-workflow")

    def read(identity):
        try:
            return store.read(identity)
        except FileNotFoundError as error:
            raise HTTPException(404, "Workflow not found") from error
        except ValueError as error:
            raise HTTPException(422, str(error)) from error

    def submit(identity):
        with lock:
            if active:
                raise HTTPException(
                    429, "A local workflow is already running; finish or cancel it first"
                )

            def work():
                try:
                    return LocalWorkflowEngine(store, app.state.local_workflow_provider).run(
                        identity
                    )
                except Exception as error:
                    row = store.read(identity)
                    if row["state"] not in TERMINAL:
                        store.update(
                            identity,
                            row["revision"],
                            detail="Unexpected controller failure retained",
                            state="CANCELLED" if row["state"] == "CANCEL_REQUESTED" else "FAILED",
                            error=type(error).__name__ + ": " + str(error)[:800],
                            process=None,
                        )

            future = executor.submit(work)
            active[identity] = future

            def finished(_):
                with lock:
                    active.pop(identity, None)

            future.add_done_callback(finished)

    def artifact(identity):
        row = read(identity)
        if row["state"] != "COMPLETED" or row["result"] is None:
            raise HTTPException(409, "This workflow has no completed verified result")
        folder = store.folder(identity) / f"attempt-{row['attempt']}" / "artifacts"
        try:
            inspect_bundle(folder, row["result"]["manifest_sha256"], row["result"]["bundle_sha256"])
        except (OSError, ValueError, KeyError) as error:
            raise HTTPException(
                409,
                "Saved artifacts or evidence changed; original record retained. No automatic rerun.",
            ) from error
        return row, folder

    @router.get("/runtime")
    def runtime():
        provider = app.state.local_workflow_provider
        ready = provider is not None and provider.available()
        return {
            "deterministic_available": True,
            "model_session_authorized": ready,
            "model_health": "NOT_PROBED",
            "paid_fallback": False,
            "research_comparison": "NOT_RUN_NATIVE_ADMISSION_NOT_PASSED",
            "scope": "Local physicochemical workflow; no assay or efficacy prediction",
        }

    @router.get("/tools")
    def tools():
        return {
            "tools": [
                {
                    "id": "compound_csv",
                    "description": "Validate compound_id and smiles rows; retain explicit rejection reasons",
                },
                {
                    "id": "rdkit_descriptors",
                    "description": "Compute actual molecular descriptors and apply recorded numeric limits",
                    "parameters": Parameters.model_json_schema(),
                },
                {
                    "id": "local_report",
                    "description": "Collect verified CSV, report, manifest and current evidence as a local ZIP",
                },
            ],
            "external_connectors": "NOT_IMPLEMENTED",
            "arbitrary_code_upload": False,
        }

    @router.get("/jobs")
    def list_jobs():
        return {"items": store.list()}

    @router.post("/jobs", status_code=202)
    def create(body: CreateWorkflow, request: Request):
        if request.query_params:
            raise HTTPException(422, "Unexpected workflow query fields")
        if body.mode == "agent":
            provider = app.state.local_workflow_provider
            if provider is None or not provider.available():
                raise HTTPException(
                    503, "No authorized local model session; choose deterministic mode explicitly"
                )
        try:
            validate_csv(body.csv_text)
            with lock:
                if active:
                    raise HTTPException(429, "A local workflow is already running")
                row = store.create(body.model_dump())
                submit(row["job_id"])
            return row
        except (ValueError, csv.Error) as error:
            raise HTTPException(422, str(error)) from error

    @router.get("/jobs/{identity}")
    def detail(identity: str):
        row = read(identity)
        if row["state"] == "COMPLETED":
            _, folder = artifact(identity)
            return {
                **row,
                "data": json.loads((folder / "report.json").read_text(encoding="utf-8")),
                "events": store.history(identity),
            }
        return {**row, "data": None, "events": store.history(identity)}

    @router.post("/jobs/{identity}/cancel")
    def cancel(identity: str, body: JobAction):
        with lock:
            row = read(identity)
            if row["revision"] != body.expected_revision or row["state"] in TERMINAL:
                raise HTTPException(409, "Workflow changed or is already terminal")
            future = active.get(identity)
            queued = future is not None and future.cancel()
            try:
                return store.update(
                    identity,
                    row["revision"],
                    detail="Explicit cancellation requested",
                    state="CANCELLED" if queued else "CANCEL_REQUESTED",
                )
            except JobConflict as error:
                raise HTTPException(409, str(error)) from error

    @router.post("/jobs/{identity}/resume")
    def resume(identity: str, body: JobAction):
        with lock:
            row = read(identity)
            if row["revision"] != body.expected_revision or row["state"] not in (
                "INTERRUPTED",
                "CANCELLED",
            ):
                raise HTTPException(
                    409, "Only an explicitly reviewed interrupted/cancelled workflow can resume"
                )
            if active:
                raise HTTPException(429, "A local workflow is already running")
            if row["spec"]["mode"] == "agent":
                provider = app.state.local_workflow_provider
                if provider is None or not provider.available():
                    raise HTTPException(503, "An authorized local model session is required")
            row = store.update(
                identity,
                row["revision"],
                detail="Explicit new attempt; preserve all prior attempts and any valid typed plan",
                state="QUEUED",
                error=None,
            )
            submit(identity)
            return row

    @router.get("/jobs/{identity}/artifacts/{name}")
    def collect(identity: str, name: str):
        allowed = {
            "input.csv",
            "parameters.json",
            "descriptors.csv",
            "selected.csv",
            "rejected.csv",
            "report.json",
            "report.html",
            "manifest.json",
            "evidence.json",
            "bundle.zip",
        }
        if name not in allowed:
            raise HTTPException(404, "Unknown artifact")
        _, folder = artifact(identity)
        headers = {
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; sandbox",
        }
        return FileResponse(
            folder / name,
            filename=("curaloop-workflow-" + identity[:8] + ".zip")
            if name == "bundle.zip"
            else name,
            headers=headers,
        )

    @router.get("/jobs/{identity}/structures/{index}")
    def structure(identity: str, index: int):
        _, folder = artifact(identity)
        data = json.loads((folder / "report.json").read_text(encoding="utf-8"))["compounds"]
        if not 0 <= index < len(data):
            raise HTTPException(404, "Compound not found")
        from rdkit import Chem
        from rdkit.Chem.Draw import rdMolDraw2D

        mol = Chem.MolFromSmiles(data[index]["canonical_smiles"])
        draw = rdMolDraw2D.MolDraw2DSVG(340, 220)
        draw.DrawMolecule(mol)
        draw.FinishDrawing()
        return Response(
            draw.GetDrawingText(),
            media_type="image/svg+xml",
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": "default-src 'none'; sandbox",
            },
        )

    app.include_router(router)
