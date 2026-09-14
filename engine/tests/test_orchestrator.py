from unittest.mock import patch
import json

from haval_engine.pack.matrix import scenarios as build_scenarios

called: dict = {}


def _fake_generate(model, prompt, num_predict=4096, timeout=None, cancel=None, think=False, **_kwargs):
    if int(num_predict or 0) <= 160:
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
    monkeypatch.setenv("HAVAL_BENCH_SKIP_PHASE2", "1")
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


def test_stop_mid_run_writes_partial_report(tmp_path, monkeypatch):
    monkeypatch.setenv("HAVAL_BENCH_MAX_SCENARIOS", "3")
    monkeypatch.setenv("HAVAL_BENCH_SKIP_PHASE2", "1")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.bench.orchestrator import BenchRunner
    from haval_engine.paths import app_data_dir

    runner = BenchRunner()
    scored = {"n": 0}

    def gen(model, prompt, num_predict=4096, timeout=None, cancel=None, think=False, **kwargs):
        if int(num_predict or 0) <= 160:
            return _fake_generate(model, prompt, num_predict=num_predict, think=think)
        scored["n"] += 1
        out = _fake_generate(model, prompt, num_predict=num_predict, think=think)
        if scored["n"] >= 1:
            runner._stop.set()
        return out

    with (
        patch("haval_engine.bench.orchestrator.ollama.generate_stream", side_effect=gen),
        patch("haval_engine.bench.orchestrator.ollama.ps", return_value={"models": []}),
        patch("haval_engine.bench.orchestrator.ollama.unload"),
        patch("haval_engine.bench.orchestrator.DOCTOR.snapshot", return_value={"gate": {"environment_ready": True}}),
        patch("haval_engine.bench.orchestrator.load_settings", return_value={"selected_models": ["stub:model"], "thinking": False}),
    ):
        started = runner.start()
        assert started["ok"]
        runner._thread.join(timeout=30)
    rid = started["run_id"]
    snap = runner.status()
    assert snap["state"] == "idle"
    assert snap.get("open_report") == rid
    run = runner.store.get(rid)
    assert run and run["status"] == "stopped"
    assert len(runner.store.attempts_for(rid)) == 1
    folder = app_data_dir() / "runs" / rid
    html = folder / "report.html"
    assert html.is_file()
    text = html.read_text(encoding="utf-8")
    assert "Incomplete measured run" in text
    listed = runner.store.list_runs()
    assert any(r["id"] == rid for r in listed)


def test_phase1_hardware_finishes_all_roles_then_skips_phase2(tmp_path, monkeypatch):
    monkeypatch.setenv("HAVAL_BENCH_MAX_SCENARIOS", "3")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.bench.orchestrator import BenchRunner

    runner = BenchRunner()
    p2 = {"called": 0}

    def oom(*_args, **_kwargs):
        return {
            "ok": False,
            "ttft_ms": None,
            "total_ms": 12000,
            "tok_s": 0,
            "text": "",
            "error": "cudaMalloc failed: out of memory",
        }

    def no_p2(*_args, **_kwargs):
        p2["called"] += 1
        return {}

    with (
        patch("haval_engine.bench.orchestrator.ollama.generate_stream", side_effect=oom),
        patch("haval_engine.bench.orchestrator.ollama.ps", return_value={"models": []}),
        patch("haval_engine.bench.orchestrator.ollama.unload"),
        patch("haval_engine.phase2.runner.run_quality_pack", side_effect=no_p2),
        patch("haval_engine.bench.orchestrator.DOCTOR.snapshot", return_value={"gate": {"environment_ready": True}}),
        patch("haval_engine.bench.orchestrator.load_settings", return_value={"selected_models": ["stub:model"], "thinking": False}),
    ):
        started = runner.start()
        assert started["ok"]
        runner._thread.join(timeout=30)
    rid = started["run_id"]
    assert runner.status()["state"] == "idle"
    assert len(runner.store.attempts_for(rid)) == 3
    assert p2["called"] == 0
    summary = json.loads((runner.store.get(rid) or {}).get("summary_json") or "{}")
    fail = (summary.get("models") or [{}])[0].get("fail") or {}
    assert fail.get("kind") == "hardware"


def test_phase1_one_role_ok_still_runs_phase2(tmp_path, monkeypatch):
    monkeypatch.setenv("HAVAL_BENCH_MAX_SCENARIOS", "2")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    from haval_engine.bench.orchestrator import BenchRunner

    runner = BenchRunner()
    p2 = {"called": 0}
    n = {"i": 0}

    def mixed(model, prompt, num_predict=4096, timeout=None, cancel=None, think=False, **kwargs):
        if int(num_predict or 0) <= 160:
            return _fake_generate(model, prompt, num_predict=num_predict, think=think)
        n["i"] += 1
        if n["i"] == 1:
            return {
                "ok": False,
                "ttft_ms": None,
                "total_ms": 12000,
                "tok_s": 0,
                "text": "",
                "error": "cudaMalloc failed: out of memory",
            }
        return _fake_generate(model, prompt, num_predict=num_predict, think=think)

    def yes_p2(*_args, **_kwargs):
        p2["called"] += 1
        return {"pack": "phase2-quality", "pct": {}, "total": 0}

    with (
        patch("haval_engine.bench.orchestrator.ollama.generate_stream", side_effect=mixed),
        patch("haval_engine.bench.orchestrator.ollama.ps", return_value={"models": []}),
        patch("haval_engine.bench.orchestrator.ollama.unload"),
        patch("haval_engine.phase2.runner.run_quality_pack", side_effect=yes_p2),
        patch("haval_engine.bench.orchestrator.DOCTOR.snapshot", return_value={"gate": {"environment_ready": True}}),
        patch("haval_engine.bench.orchestrator.load_settings", return_value={"selected_models": ["stub:model"], "thinking": False}),
    ):
        started = runner.start()
        assert started["ok"]
        runner._thread.join(timeout=30)
    assert runner.status()["state"] == "idle"
    assert p2["called"] == 1
