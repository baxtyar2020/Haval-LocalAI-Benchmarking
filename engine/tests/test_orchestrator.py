from unittest.mock import patch

from haval_engine.pack.matrix import scenarios as build_scenarios

called: dict = {}


def _fake_generate(model, prompt, num_predict=4096, timeout=None, cancel=None, think=False, **_kwargs):
    if int(num_predict or 0) <= 24:
        return {
            "ok": True,
            "ttft_ms": 50,
            "total_ms": 200,
            "tok_s": 20.0,
            "eval_count": 1,
            "prompt_eval_count": 8,
            "load_duration_ns": 1e8,
            "text": "ready",
            "error": None,
        }
    assert num_predict == 4096
    called["think"] = think
    sid = None
    for row in build_scenarios():
        if row["id"] in prompt or row["prompt"][:40] in prompt:
            sid = row["id"]
            seed = row["seeds"]["good"]
            break
    else:
        seed = build_scenarios()[0]["seeds"]["good"]
    return {
        "ok": True,
        "ttft_ms": 400,
        "total_ms": 2000,
        "tok_s": 40.0,
        "eval_count": 80,
        "prompt_eval_count": 100,
        "load_duration_ns": 1e9,
        "text": seed,
        "error": None,
    }


def test_one_scenario_one_attempt(tmp_path, monkeypatch):
    monkeypatch.setenv("HAVAL_BENCH_MAX_SCENARIOS", "1")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.bench.orchestrator import BenchRunner

    runner = BenchRunner()
    with (
        patch("haval_engine.bench.orchestrator.ollama.generate_stream", side_effect=_fake_generate),
        patch("haval_engine.bench.orchestrator.ollama.ps", return_value={"models": []}),
        patch("haval_engine.bench.orchestrator.ollama.unload"),
        patch("haval_engine.bench.orchestrator.DOCTOR.snapshot", return_value={"gate": {"environment_ready": True}}),
        patch("haval_engine.bench.orchestrator.load_settings", return_value={"selected_models": ["stub:model"], "thinking": False}),
    ):
        started = runner.start()
        assert started["ok"]
        runner._thread.join(timeout=30)
    snap = runner.status()
    assert snap["state"] == "idle"
    assert snap.get("open_report") == started["run_id"]
    assert called["think"] is False
    scores = runner.store.scenario_scores_for(started["run_id"])
    assert len(scores) == 1
    assert scores[0]["attempted"] == 1
    assert scores[0]["successful"] == 1
    attempts = runner.store.attempts_for(started["run_id"])
    assert len(attempts) == 1
    from haval_engine.paths import app_data_dir

    folder = app_data_dir() / "runs" / started["run_id"]
    assert (folder / "results.xlsx").is_file()
    assert not (folder / "attempts.csv").exists()
    assert not (folder / "quality.csv").exists()
