from haval_engine.models.library import ModelLibrary


def _job(**kw):
    job = {"id": "j1", "name": "qwen3:8b", "state": "downloading", "pct": 12, "stage": "pull"}
    job.update(kw)
    return job


def test_downloading_stays_on_installed_list():
    lib = ModelLibrary()
    rows = lib._rows([], [], [_job()], [], "Installed", "")
    assert rows[0]["name"] == "qwen3:8b"
    assert rows[0]["download"]["state"] == "downloading"


def test_downloading_stays_on_empty_search():
    lib = ModelLibrary()
    rows = lib._rows([], [], [_job()], [], "Search Ollama", "")
    assert any(r["name"] == "qwen3:8b" for r in rows)


def test_downloading_filter_only_open_jobs():
    lib = ModelLibrary()
    jobs = [_job(), _job(id="j2", name="llama3:8b", state="completed")]
    rows = lib._rows(
        [{"name": "llama3:8b", "size": 1, "details": {}}],
        [],
        jobs,
        [],
        "Downloading",
        "",
    )
    assert [r["name"] for r in rows] == ["qwen3:8b"]


def test_jobs_public_does_not_need_installed_rows():
    lib = ModelLibrary()
    lib.jobs["j1"] = _job()
    rows = lib.jobs_public()
    assert rows[0]["id"] == "j1"
    assert rows[0]["state"] == "downloading"


def test_completed_download_appears_in_installed():
    lib = ModelLibrary()
    rows = lib._rows(
        [{"name": "qwen3:8b", "size": 100, "details": {}}],
        [],
        [_job(state="completed")],
        [],
        "Installed",
        "",
    )
    assert rows[0]["name"] == "qwen3:8b"
    assert rows[0]["installed"] is True
    assert not any((r.get("download") or {}).get("state") == "downloading" for r in rows)
