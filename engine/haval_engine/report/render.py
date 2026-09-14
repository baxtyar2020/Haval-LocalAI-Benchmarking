from __future__ import annotations

import json
import shutil
from pathlib import Path

from jinja2 import Environment, select_autoescape

from haval_engine.data.store import RunStore, runs_dir
from haval_engine.doctor.service import SERVICE
from haval_engine.report.context import build_context, status_class
from haval_engine.winproc import run_hidden

HERE = Path(__file__).resolve().parent


def _plain(path: Path) -> Path:
    text = str(path)
    if text.startswith("\\\\?\\"):
        text = text[4:]
    return Path(text)


def _asset_text(name: str) -> str:
    try:
        from importlib.resources import files

        return (files("haval_engine.report") / name).read_text(encoding="utf-8")
    except Exception:
        return (_plain(HERE) / name).read_text(encoding="utf-8")


def _env() -> Environment:
    env = Environment(autoescape=select_autoescape(["html", "j2"]))
    env.filters["sclass"] = status_class
    return env


def report_html_path(run_id: str) -> Path:
    return runs_dir() / run_id / "report.html"


def report_pdf_path(run_id: str) -> Path:
    return runs_dir() / run_id / "report.pdf"


def render_html(context: dict) -> str:
    context = dict(context)
    context["css"] = _asset_text("style.css")
    return _env().from_string(_asset_text("report.html.j2")).render(**context)


def copy_run_exports(run_id: str, dest: str) -> None:
    folder = Path(dest.strip())
    if not str(folder):
        return
    folder.mkdir(parents=True, exist_ok=True)
    stem = f"Haval-LocalAI-Bench-{run_id}"
    html = report_html_path(run_id)
    if html.is_file():
        shutil.copy2(html, folder / f"{stem}.html")
    xlsx = runs_dir() / run_id / "results.xlsx"
    if xlsx.is_file():
        shutil.copy2(xlsx, folder / f"{stem}.xlsx")
    pdf = report_pdf_path(run_id)
    if pdf.is_file():
        shutil.copy2(pdf, folder / f"{stem}.pdf")


def generate_report(run_id: str, store: RunStore | None = None) -> Path:
    store = store or RunStore()
    run = store.get(run_id)
    if not run:
        raise FileNotFoundError(run_id)
    try:
        summary = json.loads(run.get("summary_json") or "{}")
    except json.JSONDecodeError:
        summary = {}
    path = report_html_path(run_id)
    if path.is_file():
        return path
    if summary.get("kind") == "comparison":
        raise FileNotFoundError(run_id)
    from haval_engine.hardware import computer_name

    hardware = dict(SERVICE.snapshot().get("hardware") or {})
    hardware.setdefault("computer_name", computer_name())
    html = render_html(build_context(run, store.scenario_scores_for(run_id), store.attempts_for(run_id), hardware))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    try:
        summary = json.loads(run.get("summary_json") or "{}")
        dest = (summary.get("report_dir") or "").strip()
        if dest:
            copy_run_exports(run_id, dest)
    except Exception:
        pass
    return path


def try_pdf(run_id: str) -> Path | None:
    html = report_html_path(run_id)
    pdf = report_pdf_path(run_id)
    if not html.exists():
        generate_report(run_id)
    edge = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
    if not edge.exists():
        edge = Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")
    if not edge.exists():
        return None
    try:
        run_hidden(
            [str(edge), "--headless", "--disable-gpu", f"--print-to-pdf={pdf}", str(html)],
            timeout=60,
        )
    except Exception:
        return None
    return pdf if pdf.exists() else None
