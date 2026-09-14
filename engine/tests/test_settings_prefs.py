from haval_engine.ollama.runtime import load_settings, save_settings
from haval_engine.report import render as render_mod


def test_copy_run_exports_html_and_xlsx(tmp_path, monkeypatch):
    monkeypatch.setattr(render_mod, "runs_dir", lambda: tmp_path)
    rid = "run-1"
    run_dir = tmp_path / rid
    run_dir.mkdir()
    html = tmp_path / rid / "report.html"
    html.write_text("<html></html>", encoding="utf-8")
    (run_dir / "results.xlsx").write_bytes(b"xlsx")
    dest = tmp_path / "out"
    render_mod.copy_run_exports(rid, str(dest))
    assert (dest / f"Haval-LocalAI-Bench-{rid}.html").is_file()
    assert (dest / f"Haval-LocalAI-Bench-{rid}.xlsx").is_file()


def test_save_settings_keeps_default_report_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine import paths

    monkeypatch.setattr(paths, "app_data_dir", lambda: tmp_path / "Haval LocalAI Bench")
    (tmp_path / "Haval LocalAI Bench").mkdir()
    save_settings({"default_report_dir": str(tmp_path / "reports")})
    assert load_settings()["default_report_dir"] == str(tmp_path / "reports")
