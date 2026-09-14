from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from haval_engine.models.library import LIBRARY

router = APIRouter(prefix="/models", tags=["models"])


class DownloadBody(BaseModel):
    name: str


class SelectBody(BaseModel):
    name: str
    selected: bool


@router.get("/preferred")
def preferred_models() -> dict:
    import json

    from haval_engine.paths import config_dir

    path = config_dir() / "preferred-models.json"
    if not path.exists():
        return {"version": "missing", "models": []}
    return json.loads(path.read_text(encoding="utf-8"))


@router.get("/library")
def library(
    filter: str = Query(default="Installed"),
    q: str = Query(default=""),
) -> dict:
    return LIBRARY.snapshot(filter_name=filter, query=q)


@router.get("/jobs")
def download_jobs() -> dict:
    return {"jobs": LIBRARY.jobs_public()}


@router.get("/search")
def search(q: str = Query(default="")) -> dict:
    return LIBRARY.snapshot(filter_name="Search Ollama", query=q)


def _jobs_payload(job: dict | None = None) -> dict:
    payload: dict = {"jobs": LIBRARY.jobs_public()}
    if job is not None:
        payload["job"] = job
    return payload


@router.post("/downloads")
def start_download(body: DownloadBody) -> dict:
    try:
        job = LIBRARY.enqueue(body.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _jobs_payload(job)


@router.post("/downloads/{job_id}/cancel")
def cancel_download(job_id: str) -> dict:
    job = LIBRARY.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Download not found")
    return _jobs_payload(job)


@router.post("/downloads/{job_id}/retry")
def retry_download(job_id: str) -> dict:
    job = LIBRARY.retry(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Download not found")
    return _jobs_payload(job)


@router.post("/select")
def select_model(body: SelectBody) -> dict:
    selected = LIBRARY.set_selected(body.name, body.selected)
    return {"selected": selected}


@router.post("/remove")
def remove_model(
    body: DownloadBody,
    filter: str = Query(default="Installed"),
    q: str = Query(default=""),
) -> dict:
    ok, msg = LIBRARY.remove(body.name)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    snap = LIBRARY.snapshot(filter_name=filter, query=q)
    return {"ok": True, "message": msg, **snap}
