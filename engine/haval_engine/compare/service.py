from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from haval_engine.compare.html import build_comparison_html
from haval_engine.compare.merge import merge_runs
from haval_engine.compare.models import MeasuredRun
from haval_engine.compare.parse import load_run_file, parse_report_html, validate_source_html
from haval_engine.data.store import RunStore, runs_dir
from haval_engine.ollama.runtime import load_settings
from haval_engine.report.context import headline_for_run
from haval_engine.report.render import copy_run_exports, report_html_path


def list_compare_sources(store: RunStore) -> list[dict]:
    rows = []
    for run in store.list_runs(limit=200):
        if (run.get("status") or "") != "completed":
            continue
        try:
            summary = json.loads(run.get("summary_json") or "{}")
        except json.JSONDecodeError:
            summary = {}
        if summary.get("kind") == "comparison":
            continue
        html_path = report_html_path(run["id"])
        parsed = _try_parse_saved(html_path, run) if html_path.is_file() else None
        rows.append(_source_row(run, parsed))
    return rows


def _source_row(run: dict, parsed: MeasuredRun | None) -> dict:
    try:
        models = json.loads(run.get("models_json") or "[]")
    except json.JSONDecodeError:
        models = []
    model_name = ""
    if isinstance(models, list) and models:
        model_name = str(models[0] or "")
    try:
        summary = json.loads(run.get("summary_json") or "{}")
    except json.JSONDecodeError:
        summary = {}
    final = None
    for item in summary.get("models") or []:
        if isinstance(item, dict) and item.get("final") is not None:
            final = item.get("final")
            break
    return {
        "id": run["id"],
        "started_at": run.get("started_at"),
        "status": run.get("status"),
        "model_name": (parsed.model_name if parsed and parsed.model_name else model_name) or "Unknown",
        "size_line": _size(parsed) if parsed else "",
        "final": parsed.final if parsed and parsed.final is not None else final,
        "machine": parsed.machine if parsed else "",
        "headline": headline_for_run(run),
    }


def _size(run: MeasuredRun) -> str:
    tot = run.total_b
    act = run.active_b
    bits = []
    if tot is not None:
        bits.append(f"{tot:g}B total")
    if act is not None:
        bits.append(f"{act:g}B active")
    if run.arch:
        bits.append(run.arch)
    return " · ".join(bits)


def _try_parse_saved(path: Path, run: dict) -> MeasuredRun | None:
    try:
        parsed = load_run_file(path)
        if not parsed.run_id:
            parsed.run_id = run["id"]
        return parsed
    except (OSError, ValueError):
        return None


def build_from_inputs(store: RunStore, run_ids: list[str], uploads: list[tuple[str, str]]) -> tuple[str, Path]:
    measured: list[MeasuredRun] = []
    for rid in run_ids:
        row = store.get(rid)
        if not row or (row.get("status") or "") != "completed":
            raise ValueError(f"Missing completed report: {rid}")
        path = report_html_path(rid)
        if not path.is_file():
            raise ValueError(f"Missing completed report: {rid}")
        parsed = load_run_file(path)
        parsed.run_id = rid
        parsed.source_label = rid
        measured.append(parsed)
    for name, html in uploads:
        err = validate_source_html(html)
        if err:
            raise ValueError(err)
        parsed = parse_report_html(html, name)
        measured.append(parsed)
    if len(measured) < 2:
        raise ValueError("Select at least two reports.")
    columns = merge_runs(measured)
    if len(columns) < 2:
        raise ValueError("Select reports from at least two different models.")
    html_out = build_comparison_html(columns, source_count=len(measured))
    run_id = datetime.now(timezone.utc).strftime("compare-%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
    names = [c.model_name for c in columns]
    store.conn.execute(
        "INSERT INTO runs (id, started_at, ended_at, status, models_json, summary_json) VALUES (?, ?, ?, ?, ?, ?)",
        (
            run_id,
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            "completed",
            json.dumps(names),
            json.dumps(
                {
                    "kind": "comparison",
                    "source_run_ids": list(run_ids),
                    "models": names,
                    "headline": f"Comparison · {len(columns)} models",
                }
            ),
        ),
    )
    store.conn.commit()
    folder = runs_dir() / run_id
    folder.mkdir(parents=True, exist_ok=True)
    dest = folder / "report.html"
    dest.write_text(html_out, encoding="utf-8")
    sidecar = {
        "kind": "comparison",
        "source_run_ids": list(run_ids),
        "models": names,
    }
    (folder / "comparison.json").write_text(json.dumps(sidecar, indent=2), encoding="utf-8")
    extra = (load_settings().get("default_report_dir") or "").strip()
    if extra:
        try:
            copy_run_exports(run_id, extra)
        except OSError:
            pass
    return run_id, dest
