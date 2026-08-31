import shutil
from pathlib import Path


def test_list_runs_drops_deleted_folders(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.data.store import RunStore, runs_dir

    store = RunStore()
    rid = store.create_run(["stub:model"])
    store.set_status(rid, "completed", {"thinking": False})
    store.export_results(rid)
    folder = runs_dir() / rid
    assert (folder / "results.xlsx").is_file()
    shutil.rmtree(folder)
    listed = store.list_runs()
    assert listed == []
    assert store.get(rid) is None


def test_running_run_is_kept_without_artifacts(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.data.store import RunStore, runs_dir

    store = RunStore()
    rid = store.create_run(["stub:model"])
    shutil.rmtree(runs_dir() / rid)
    listed = store.list_runs()
    assert any(r["id"] == rid for r in listed)


def test_purge_run_removes_folder_and_row(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.data.store import RunStore, runs_dir

    store = RunStore()
    rid = store.create_run(["stub:model"])
    store.set_status(rid, "completed", {"thinking": False})
    store.export_results(rid)
    folder = runs_dir() / rid
    (folder / "report.html").write_text("<html></html>", encoding="utf-8")
    assert folder.is_dir()
    ok, msg = store.purge_run(rid)
    assert ok, msg
    assert store.get(rid) is None
    assert not folder.exists()
    assert store.list_runs() == []
    ok2, _ = store.purge_run("../secret")
    assert ok2 is False
