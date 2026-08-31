import json

from haval_engine.report.context import PERSONA_ORDER, build_context
from haval_engine.report.render import render_html


def test_report_has_twenty_personas_and_no_invented_copy():
    run = {
        "id": "test-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": "{}",
    }
    ctx = build_context(run, [], [], {"cpu": "Test CPU", "gpu": "Test GPU", "ram_gb": 32, "computer_name": "This PC"})
    html = render_html(ctx)
    assert "Best Enterprise" not in html
    assert "Commercial" in html
    assert "Hypothetical" not in html
    assert "Commercial" in html
    assert "How this PC performed" in html
    assert "This PC" in html
    assert "01A" not in html
    assert "10-page" not in html.lower()
    assert "Realistic customer scenario" not in html
    assert "Consumer" in html
    assert "Best Consumer Match" not in html
    assert len(ctx["models"][0]["personas"]) == 20
    for _, persona in PERSONA_ORDER:
        assert persona.replace("&", "&amp;") in html
    assert "Everyday Organizer" in html
    assert "Failed" in html
    assert "not invented" in html.lower() or "not invented" in html
    assert "Finish" in html
    assert "Q^0.60" not in html
    assert "Hardware zone" not in html
    assert "Insufficient Data" not in html
    assert "Operating envelope" not in html
    assert "Not this run" not in html
    assert "High-Capability" not in html
    assert "FAST / LIGHT" not in html
    assert "Tradeoff" not in html
    assert "Speed is not mixed in" not in html
    assert "MetriLLM" not in html
    assert "verdict" in html
    assert "never penalized" in html
    assert "Haval LocalAI Benchmarking" in html
    assert "How this has been calculated" in html
    assert "em dashes" in html.lower() or "—" in html


def test_report_slow_perfect_answer_is_not_excellent():
    run = {
        "id": "slow-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": "{}",
    }
    scores = [
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-L",
            "q": 100,
            "r": 100,
            "internal": "Slow",
            "successful": 3,
            "attempted": 3,
        },
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-B",
            "q": 100,
            "r": 100,
            "internal": "Slow",
            "successful": 3,
            "attempted": 3,
        },
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-H",
            "q": 100,
            "r": 100,
            "internal": "Slow",
            "successful": 3,
            "attempted": 3,
        },
    ]
    ctx = build_context(run, scores, [], {"cpu": "Test CPU", "gpu": "Test GPU", "ram_gb": 32})
    organizer = next(p for p in ctx["models"][0]["personas"] if p["persona"] == "Everyday Organizer")
    assert organizer["overall"] == "48"
    assert organizer["final"] == "Marginal Match"
    assert ctx["models"][0]["businesses"]["Consumer"]["customer"] == "Marginal Match"
    html = render_html(ctx)
    assert "Phase 2" in html
    assert "multilingual" in html.lower()
    assert "has-tip" in html
    assert organizer["why"]
    assert "04 · Business match" not in html
    assert 'id="match-tip"' in html
    assert "#match-tip" in html


def test_report_combines_phase2_into_persona_tag():
    run = {
        "id": "p2-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": json.dumps(
            {
                "models": [
                    {
                        "model": "gemma4:26b",
                        "phase2": {
                            "excluded": ["multilingual", "sensitivity"],
                            "pct": {
                                "reasoning": 20,
                                "coding": 20,
                                "instructionFollowing": 20,
                                "structuredOutput": 20,
                                "math": 20,
                            },
                            "total": 20,
                            "categories": {},
                        },
                    }
                ]
            }
        ),
    }
    scores = [
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-L",
            "q": 100,
            "r": 100,
            "internal": "Fast",
            "successful": 3,
            "attempted": 3,
        }
    ]
    ctx = build_context(run, scores, [], {"cpu": "Test CPU", "gpu": "Test GPU", "ram_gb": 32})
    organizer = next(p for p in ctx["models"][0]["personas"] if p["persona"] == "Everyday Organizer")
    assert organizer["phase2"] == "20"
    assert organizer["final"] != "Failed"


def test_persona_light_cell_is_mmss_not_score():
    run = {
        "id": "time-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": "{}",
    }
    scores = [
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-L",
            "q": 100,
            "r": 100,
            "internal": "Fast",
            "successful": 3,
            "attempted": 3,
        }
    ]
    attempts = [
        {"model": "gemma4:26b", "scenario_id": "C-EO-L", "ok": 1, "total_s": 125, "q": 100},
        {"model": "gemma4:26b", "scenario_id": "C-EO-L", "ok": 1, "total_s": 125, "q": 100},
        {"model": "gemma4:26b", "scenario_id": "C-EO-L", "ok": 1, "total_s": 125, "q": 100},
    ]
    ctx = build_context(run, scores, attempts, {"cpu": "Test CPU", "gpu": "Test GPU", "ram_gb": 32})
    organizer = next(p for p in ctx["models"][0]["personas"] if p["persona"] == "Everyday Organizer")
    assert organizer["light"] == "2:05"
    assert "Fast" not in organizer["light"]


def test_report_lists_only_selected_personas():
    run = {
        "id": "subset-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": json.dumps({"thinking": False, "personas": ["Everyday Organizer", "Engineer & Software Developer"]}),
    }
    scores = [
        {
            "model": "gemma4:26b",
            "scenario_id": "C-EO-L",
            "q": 100,
            "r": 100,
            "internal": "Fast",
            "successful": 3,
            "attempted": 3,
        },
        {
            "model": "gemma4:26b",
            "scenario_id": "B-EN-L",
            "q": 100,
            "r": 100,
            "internal": "Fast",
            "successful": 3,
            "attempted": 3,
        },
    ]
    ctx = build_context(run, scores, [], {"cpu": "Test CPU", "gpu": "Test GPU", "ram_gb": 32})
    names = [p["persona"] for p in ctx["models"][0]["personas"]]
    assert names == ["Everyday Organizer", "Engineer & Software Developer"]
    assert ctx["persona_count"] == 2
    assert ctx["winners"]["Gaming"]["skipped"] is True
    html = render_html(ctx)
    assert "Everyday Organizer" in html
    assert "Engineer &amp; Software Developer" in html
    assert "Casual Gamer" not in html
    assert "Student &amp; Learner" not in html

