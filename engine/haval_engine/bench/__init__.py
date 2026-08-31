from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from haval_engine.bench.orchestrator import RUNNER
from haval_engine.report.context import headline_for_run
from haval_engine.data.store import RunStore
from haval_engine.ollama.runtime import load_settings, save_settings

router = APIRouter(prefix="/bench", tags=["bench"])
_store = RunStore()


class ThinkingBody(BaseModel):
    thinking: bool = False


class StartBody(BaseModel):
    thinking: bool | None = None
    model: str | None = None
    personas: list[str] | None = None
    report_dir: str | None = None


@router.get("/status")
def bench_status() -> dict:
    return RUNNER.status()


@router.get("/prefs")
def bench_prefs() -> dict:
    return {"thinking": bool(load_settings().get("thinking", False))}


@router.post("/prefs")
def set_bench_prefs(body: ThinkingBody) -> dict:
    save_settings({"thinking": bool(body.thinking)})
    return {"thinking": bool(load_settings().get("thinking", False))}


@router.post("/start")
def bench_start(body: StartBody | None = None) -> dict:
    payload = body or StartBody()
    extras: dict = {}
    if payload.thinking is not None:
        extras["thinking"] = bool(payload.thinking)
    if payload.model:
        extras["selected_models"] = [payload.model.strip()]
    if extras:
        save_settings(extras)
    result = RUNNER.start(personas=payload.personas, report_dir=payload.report_dir)
    if not result.get("ok"):
        raise HTTPException(status_code=400, detail=result.get("error") or "Cannot start")
    return result


@router.post("/pause")
def bench_pause() -> dict:
    return RUNNER.pause()


@router.post("/stop")
def bench_stop() -> dict:
    return RUNNER.stop()


def _runs_for_ui() -> list[dict]:
    rows = []
    for row in _store.list_runs():
        item = dict(row)
        item["headline"] = headline_for_run(item)
        rows.append(item)
    return rows


@router.get("/runs")
def list_runs() -> dict:
    return {"runs": _runs_for_ui()}


@router.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    row = _store.get(run_id)
    if not row:
        raise HTTPException(status_code=404, detail="Run not found")
    run = dict(row)
    run["headline"] = headline_for_run(run)
    return {
        "run": run,
        "scenarios": _store.scenario_scores_for(run_id),
        "attempts": _store.attempts_for(run_id)[-40:],
    }
