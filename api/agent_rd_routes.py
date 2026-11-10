"""Additive localhost mission API; no changes to simulator storage/schema."""

import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, StrictInt

from curaloop_rd.agent_rd.contracts import MissionSpec, digest
from curaloop_rd.agent_rd.dossier import export_dossier
from curaloop_rd.agent_rd.engine import MissionEngine
from curaloop_rd.agent_rd.provider import RELEASE
from curaloop_rd.agent_rd.store import MissionConflict, MissionStore


class MissionAction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_revision: StrictInt
    action: Literal["resume", "export"]


def install_agent_routes(app, root):
    root = Path(root)
    app.state.agent_executor = None
    app.state.agent_store = None
    try:
        store = MissionStore(root / "missions")
    except (ValueError, OSError) as exc:
        unavailable = APIRouter(prefix="/api/v1/agent")
        detail = "Agent storage unavailable; existing simulator storage is unaffected: " + type(exc).__name__

        @unavailable.api_route("/{path:path}", methods=["GET", "POST"])
        def unavailable_agent(path: str):
            raise HTTPException(503, detail)

        app.include_router(unavailable)
        return
    engine = MissionEngine(store)
    executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="curaloop-agent")
    lock = threading.RLock()
    active = set()
    router = APIRouter(prefix="/api/v1/agent")
    app.state.agent_executor = executor
    app.state.agent_store = store
    for summary in store.list()["items"]:
        if summary["state"] not in ("COMPLETED", "ABSTAINED", "FAILED", "CANCELLED", "INTERRUPTED_RECOVERABLE"):
            store.update(summary["mission_id"], summary["revision"], "INTERRUPTED_RECOVERABLE",
                         "Previous process stopped; no model call or export was automatically repeated")

    def read(identity):
        try:
            return store.read(identity)
        except FileNotFoundError as exc:
            raise HTTPException(404, "Mission not found") from exc
        except (ValueError, OSError, KeyError) as exc:
            raise HTTPException(503, "Mission unavailable; original record retained: " + str(exc)) from exc

    def submit(identity):
        with lock:
            if identity in active or len(active) >= 4:
                raise HTTPException(429, "The bounded local mission queue is full or this mission is already active")
            active.add(identity)

        def work():
            try:
                engine.run(identity)
            except Exception as exc:
                row = store.read(identity)
                if row["state"] not in ("COMPLETED", "ABSTAINED", "FAILED"):
                    store.update(identity, row["revision"], "FAILED", "Controller failure; no replacement result",
                                 error=type(exc).__name__ + ": " + str(exc)[:800])
            finally:
                with lock:
                    active.discard(identity)
        executor.submit(work)

    @router.get("/missions")
    def list_missions():
        return store.list()

    @router.get("/runtime")
    def runtime_status():
        import json
        try:
            release = json.loads(RELEASE.read_text(encoding="utf-8"))
            ledger = json.loads(RELEASE.with_name("ledger.json").read_text(encoding="utf-8"))
            active_session = ledger["status"] == "ACTIVE" and datetime.now(timezone.utc) < datetime.fromisoformat(release["deadline_utc"])
            return {"authorization_active": active_session, "evaluation_locked": RELEASE.with_name("evaluation.lock").exists(),
                    "model": release["model"], "provider_health": "NOT_PROBED", "paid_fallback": False}
        except (OSError, ValueError, KeyError):
            return {"authorization_active": False, "evaluation_locked": False, "model": None, "provider_health": "NOT_PROBED", "paid_fallback": False}

    @router.post("/missions", status_code=202)
    def create_mission(spec: MissionSpec, request: Request):
        if request.query_params:
            raise HTTPException(422, "Unexpected mission query fields")
        if spec.mode == "agent" and ((root / "evaluation.lock").exists() or RELEASE.with_name("evaluation.lock").exists()):
            raise HTTPException(409, "Locked evaluation is using the model; ad-hoc missions are temporarily disabled")
        with lock:
            if len(active) >= 4:
                raise HTTPException(429, "The bounded local mission queue is full")
            row = store.create(spec, system="B0" if spec.mode == "deterministic" else "P")
            submit(row["mission_id"])
        return row

    @router.get("/missions/{identity}")
    def get_mission(identity: str):
        return read(identity)

    @router.post("/missions/{identity}/action")
    def mission_action(identity: str, request: MissionAction):
        row = read(identity)
        if row["revision"] != request.expected_revision:
            raise HTTPException(409, "Stale mission revision; refresh before repeating an action")
        if request.action == "resume":
            if row["spec"]["mode"] == "agent" and RELEASE.with_name("evaluation.lock").exists():
                raise HTTPException(409, "Locked evaluation is using the model; resume after the research batch")
            if row["state"] != "INTERRUPTED_RECOVERABLE":
                raise HTTPException(409, "Only an interrupted mission can resume; failed attempts are retained")
            try:
                with lock:
                    if len(active) >= 4 or identity in active:
                        raise HTTPException(429, "The bounded local mission queue is full")
                    store.update(identity, row["revision"], "QUEUED", "Explicit owner resume; completed call IDs are reconciled")
                    submit(identity)
            except MissionConflict as exc:
                raise HTTPException(409, str(exc)) from exc
            return read(identity)
        try:
            value = export_dossier(row, root / "dossiers")
            return {"mission_id": identity, "files": value["files"], "manifest": value["manifest"],
                    "external_delivery": False, "base_url": f"/api/v1/agent/missions/{identity}/dossier/"}
        except (ValueError, OSError) as exc:
            raise HTTPException(422, str(exc)) from exc

    @router.get("/missions/{identity}/dossier/{filename}")
    def dossier_file(identity: str, filename: str):
        if filename not in ("dossier.json", "trace.json", "report-en.html", "report-th.html", "manifest.json"):
            raise HTTPException(404, "Unknown dossier file")
        row = read(identity)
        if row["released"] is None:
            raise HTTPException(409, "No completed report")
        target = root / "dossiers" / (identity + "-" + digest(row["released"])[:16])
        if not target.is_dir() or target.is_symlink():
            raise HTTPException(404, "Export the completed dossier explicitly first")
        try:
            export_dossier(row, root / "dossiers")
        except (ValueError, OSError) as exc:
            raise HTTPException(503, str(exc)) from exc
        return FileResponse(target / filename, filename=filename if filename.endswith("json") else None)

    app.include_router(router)
