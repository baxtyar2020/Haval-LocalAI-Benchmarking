from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from haval_engine.data.store import RunStore, runs_dir
from haval_engine.report.context import headline_for_run
from haval_engine.report.render import generate_report, report_html_path, report_pdf_path, try_pdf

router = APIRouter(prefix="/reports", tags=["reports"])
_store = RunStore()


def _open_path(path) -> None:
    import os

    os.startfile(path)  # type: ignore[attr-defined]


@router.post("/{run_id}/render")
def render_report(run_id: str) -> dict:
    if not _store.get(run_id):
        raise HTTPException(status_code=404, detail="Run not found")
    path = generate_report(run_id)
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
