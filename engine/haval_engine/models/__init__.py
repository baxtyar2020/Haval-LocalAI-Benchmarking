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


@router.get("/search")
def search(q: str = Query(default="")) -> dict:
    return LIBRARY.snapshot(filter_name="Search Ollama", query=q)


@router.post("/downloads")
def start_download(body: DownloadBody) -> dict:
    try:
        return LIBRARY.enqueue(body.name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/downloads/{job_id}/cancel")
def cancel_download(job_id: str) -> dict:
    job = LIBRARY.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Download not found")
    return job


@router.post("/downloads/{job_id}/retry")
def retry_download(job_id: str) -> dict:
    job = LIBRARY.retry(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Download not found")
    return job


@router.post("/select")
def select_model(body: SelectBody) -> dict:
    selected = LIBRARY.set_selected(body.name, body.selected)
    return {"selected": selected}


@router.post("/remove")
def remove_model(body: DownloadBody) -> dict:
    ok, msg = LIBRARY.remove(body.name)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {"ok": True, "message": msg}
