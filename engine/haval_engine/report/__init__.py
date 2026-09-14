from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from haval_engine.data.store import RunStore, runs_dir
from haval_engine.report.context import headline_for_run
from haval_engine.report.render import generate_report, report_html_path, report_pdf_path, try_pdf

router = APIRouter(prefix="/reports", tags=["reports"])
_store = RunStore()


class CompareUpload(BaseModel):
    name: str
    html: str


class CompareRequest(BaseModel):
    run_ids: list[str] = Field(default_factory=list)
    uploads: list[CompareUpload] = Field(default_factory=list)


@router.get("/compare/sources")
def compare_sources() -> dict:
    from haval_engine.compare.service import list_compare_sources
    from haval_engine.hardware import computer_name

    return {"runs": list_compare_sources(_store), "this_machine": computer_name()}


@router.post("/compare")
def run_compare(payload: CompareRequest) -> dict:
    from haval_engine.compare.service import build_from_inputs

    uploads = [(u.name, u.html) for u in payload.uploads]
    try:
        run_id, path = build_from_inputs(_store, payload.run_ids, uploads)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Comparison could not be built.") from exc
    return {"ok": True, "run_id": run_id, "html_path": str(path)}


def _open_path(path) -> None:
    import os

    os.startfile(path)  # type: ignore[attr-defined]


@router.post("/{run_id}/render")
def render_report(run_id: str) -> dict:
    if not _store.get(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    try:
        path = generate_report(run_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report could not be created: {exc}") from exc
    pdf = try_pdf(run_id)
    return {"html_path": str(path), "pdf_path": str(pdf) if pdf else None, "folder": str(path.parent)}


@router.post("/{run_id}/open")
def open_report(run_id: str) -> dict:
    if not _store.get(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    path = generate_report(run_id)
    try:
        _open_path(path)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return {"ok": True, "html_path": str(path)}


@router.get("/{run_id}/html")
def get_html(run_id: str) -> HTMLResponse:
    path = report_html_path(run_id)
    if not path.exists():
        if not _store.get(run_id):
            raise HTTPException(status_code=404, detail="Run not found")
        path = generate_report(run_id)
    return HTMLResponse(path.read_text(encoding="utf-8"))


@router.get("/{run_id}/paths")
def report_paths(run_id: str) -> dict:
    html = report_html_path(run_id)
    pdf = report_pdf_path(run_id)
    folder = runs_dir() / run_id
    return {
        "html_path": str(html) if html.exists() else None,
        "pdf_path": str(pdf) if pdf.exists() else None,
        "folder": str(folder) if folder.exists() else None,
    }


@router.post("/{run_id}/delete")
def delete_report(run_id: str) -> dict:
    from haval_engine.bench.orchestrator import RUNNER

    snap = RUNNER.status()
    if snap.get("run_id") == run_id and snap.get("state") in {"running", "paused"}:
        raise HTTPException(status_code=409, detail="Stop the benchmark before deleting this report.")
    if not _store.get(run_id):
        raise HTTPException(status_code=404, detail="Report not found")
    ok, msg = _store.purge_run(run_id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    return {
        "ok": True,
        "message": msg,
        "runs": [{**row, "headline": headline_for_run(row)} for row in _store.list_runs()],
    }
