from __future__ import annotations

import os
import traceback
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from haval_engine import __version__
from haval_engine.auth import require_token
from haval_engine.bench import router as bench_router
from haval_engine.doctor import router as doctor_router
from haval_engine.doctor.service import SERVICE
from haval_engine.models import router as models_router
from haval_engine.pack.routes import router as pack_router
from haval_engine.ollama.runtime import load_settings, save_settings
from haval_engine.paths import support_log_path
from haval_engine.report import router as report_router

STARTED_AT = datetime.now(timezone.utc).isoformat()

app = FastAPI(title="Haval LocalAI Bench Engine", version=__version__)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:1420", "http://127.0.0.1:1420", "tauri://localhost", "https://tauri.localhost"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1|tauri\.localhost)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(doctor_router, dependencies=[Depends(require_token)])
app.include_router(models_router, dependencies=[Depends(require_token)])
app.include_router(pack_router, dependencies=[Depends(require_token)])
app.include_router(bench_router, dependencies=[Depends(require_token)])
app.include_router(report_router, dependencies=[Depends(require_token)])


@app.on_event("startup")
def _kickoff_doctor() -> None:
    SERVICE.run_async(repair=False)


@app.exception_handler(Exception)
async def unhandled_exception(_request: Request, exc: Exception) -> JSONResponse:
    try:
        with support_log_path().open("a", encoding="utf-8") as fh:
            fh.write(f"\n[{datetime.now(timezone.utc).isoformat()}] engine request error: {exc!r}\n")
            traceback.print_exc(file=fh)
    except OSError:
        pass
    return JSONResponse(status_code=500, content={"detail": "The Bench Engine hit an internal error. See support.log."})


@app.get("/health")
def health(_: None = Depends(require_token)) -> dict:
    return {
        "ok": True,
        "service": "haval-bench-engine",
        "version": __version__,
        "started_at": STARTED_AT,
        "port": int(os.environ.get("HAVAL_ENGINE_PORT", "8765")),
    }


@app.get("/bench/readiness")
def bench_readiness(_: None = Depends(require_token)) -> dict:
    snap = SERVICE.snapshot()
    return snap.get("gate") or {"ready": False, "reasons": ["Doctor has not finished yet."]}


class SettingsPatch(BaseModel):
    default_report_dir: str | None = Field(default=None)


def _prefs() -> dict:
    raw = (load_settings().get("default_report_dir") or "").strip()
    return {"default_report_dir": raw}


@app.get("/settings")
def get_settings(_: None = Depends(require_token)) -> dict:
    return _prefs()


@app.post("/settings")
def patch_settings(payload: SettingsPatch, _: None = Depends(require_token)) -> dict:
    if payload.default_report_dir is not None:
        save_settings({"default_report_dir": payload.default_report_dir.strip()})
    return _prefs()
