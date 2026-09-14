from haval_engine.compare.html import build_comparison_html, pick_winners
from haval_engine.compare.merge import merge_runs
from haval_engine.compare.models import MeasuredRun, PersonaRow
from haval_engine.compare.parse import avg_task_seconds, parse_report_html, validate_source_html


def _run(**kwargs) -> MeasuredRun:
    defaults = dict(
        run_id="20260901-010000-aaaaaa",
        source_label="a",
        machine="DESKTOP-UB6CBK3",
        model_name="Gemma 4 26B",
        model_key="gemma-4-26b-26b-3.8b",
        arch="MoE",
        total_b=26,
        active_b=3.8,
        tok_s=40.2,
        ttft_s=1.2,
        mean_s=9,
        phase1=90,
        phase2=88,
        final=89,
        capabilities={
            "Reasoning": 80,
            "Coding": 85,
            "Instruction following": 90,
            "Structured output": 88,
            "Math": 70,
        },
        personas=[
            PersonaRow("Consumer", "Everyday Organizer", 8, 9, 3, 90, 88, 89, "Excellent"),
        ],
    )
    defaults.update(kwargs)
    return MeasuredRun(**defaults)


FIXTURE = """<!DOCTYPE html>
<html><head><title>How this PC performed on Gemma 4 26B</title></head>
<body>
Haval LocalAI Bench
<div><b class="tile-name">DESKTOP-UB6CBK3</b><span class="tile-accent">Windows 11 (build 26200)</span></div>
<div><b class="tile-name">NVIDIA RTX A6000</b><span class="tile-accent">48 GB VRAM</span></div>
<div><b class="tile-name">Threadripper</b></div>
<div><b class="tile-name">System memory</b><span class="tile-accent">128 GB</span></div>
<p>Thinking was disabled for every generate call on this run.</p>
<table>
<thead><tr><th>Model</th><th>Architecture</th><th>Total / Active</th><th>Quant.</th><th>Model Bytes</th><th>Tok/s</th><th>TTFT</th><th>Mean completion</th><th>Phase 1</th><th>Phase 2</th><th>Final</th><th>Finish</th></tr></thead>
<tbody><tr><td>Gemma 4 26B</td><td>MoE</td><td>26B total · 3.8B active</td><td>Q4_K_M</td><td>~15 GB</td><td>40.2</td><td>1.2 sec</td><td>0:09</td><td>90</td><td>88</td><td>89</td><td>100</td></tr></tbody>
</table>
<table>
<thead><tr><th>Business</th><th>Persona</th><th>Light</th><th>Balanced</th><th>Heavy</th><th>Phase 1</th><th>Phase 2</th><th>Final</th><th>Match</th></tr></thead>
<tbody>
<tr><td>Consumer</td><td>Everyday Organizer</td><td>0:08</td><td>0:09</td><td>0:03</td><td>90</td><td>88</td><td>89</td><td>Excellent</td></tr>
<tr><td>Commercial</td><td>Engineer &amp; Software Developer</td><td>0:11</td><td>0:18</td><td>0:20</td><td>91</td><td>90</td><td>90</td><td>Excellent</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>Model</th><th>Category</th><th>Correct</th><th>Total</th><th>Score</th></tr></thead>
<tbody>
<tr><td>Gemma 4 26B</td><td>Reasoning</td><td>8</td><td>10</td><td>80</td></tr>
<tr><td>Gemma 4 26B</td><td>Coding</td><td>9</td><td>10</td><td>85</td></tr>
<tr><td>Gemma 4 26B</td><td>Instruction following</td><td>9</td><td>10</td><td>90</td></tr>
<tr><td>Gemma 4 26B</td><td>Structured output</td><td>8</td><td>10</td><td>88</td></tr>
<tr><td>Gemma 4 26B</td><td>Math</td><td>7</td><td>10</td><td>70</td></tr>
</tbody>
</table>
<footer>Run 20260901-010147-aacacd · completed</footer>
</body></html>
"""


def test_parse_fixture_html():
    run = parse_report_html(FIXTURE, "gemma.html")
    assert run.model_name == "Gemma 4 26B"
    assert run.machine == "DESKTOP-UB6CBK3"
    assert run.total_b == 26
    assert run.active_b == 3.8
    assert run.tok_s == 40.2
    assert run.ttft_s == 1.2
    assert run.mean_s == 9
    assert run.final == 89
    assert run.thinking is False
    assert run.capabilities["Coding"] == 85
    names = {p.name for p in run.personas}
    assert "Everyday Organizer" in names
    assert "Engineer & Software Developer" in names
    org = next(p for p in run.personas if p.name == "Everyday Organizer")
    assert org.light_s == 8
    assert org.heavy_s == 3


def test_reject_non_haval_and_comparison():
    assert validate_source_html("<html><body>hello</body></html>") == "Not a Haval bench report"
    compare = FIXTURE.replace("Haval LocalAI Bench", "Haval LocalAI Bench Cross-model comparison")
    assert validate_source_html(compare) == "Not a Haval bench report"


def test_merge_partials_union_newest_evidence():
    old_full = _run(
        run_id="20260801-000000-aaaaaa",
        final=80,
        ttft_s=5.0,
        personas=[
            PersonaRow("Consumer", "Everyday Organizer", 8, 9, 3, 80, 80, 80, "Strong"),
            *[PersonaRow("Consumer", f"P{i}", 1, 1, 1) for i in range(19)],
        ],
    )
    assert old_full.persona_count == 20
    new_partial = _run(
        run_id="20260901-000000-bbbbbb",
        final=92,
        ttft_s=1.1,
        personas=[
            PersonaRow("Commercial", "Engineer & Software Developer", 11, 18, None, 90, 90, 90, "Excellent"),
        ],
    )
    newer_full = _run(
        run_id="20260902-000000-cccccc",
        final=91,
        ttft_s=1.4,
        personas=[
            PersonaRow("Consumer", "Everyday Organizer", 8, 9, 3, 91, 91, 91, "Excellent"),
            *[PersonaRow("Consumer", f"P{i}", 1, 1, 1) for i in range(19)],
        ],
    )
    merged = merge_runs([old_full, new_partial, newer_full])
    assert len(merged) == 1
    col = merged[0]
    assert col.final == 91
    assert col.ttft_s == 1.4
    names = {p.name for p in col.personas}
    assert "Everyday Organizer" in names
    assert "Engineer & Software Developer" in names
    org = next(p for p in col.personas if p.name == "Everyday Organizer")
    assert org.final == 91


def test_comparison_html_contract():
    a = _run()
    b = _run(
        run_id="20260901-020000-bbbbbb",
        model_name="llama3.2:1b",
        model_key="llama-3-2-1b-1b-1b",
        arch="Dense",
        total_b=1,
        active_b=1,
        tok_s=120,
        ttft_s=0.1,
        mean_s=1,
        phase1=40,
        phase2=20,
        final=30,
        capabilities={
            "Reasoning": 10,
            "Coding": 12,
            "Instruction following": 40,
            "Structured output": 20,
            "Math": 5,
        },
        personas=[
            PersonaRow("Consumer", "Everyday Organizer", 1, 1, None),
        ],
    )
    html = build_comparison_html([a, b], source_count=2)
    assert "Haval LocalAI · LLM size comparison on one PC" in html
    assert "Cross-model comparison" in html
    assert (
        '<th>Model</th><th>Size</th><th>Active</th><th>Tok/s</th>'
        '<th class="task-est">Total estimated response per task</th>'
    ) in html
    assert "<th>TTFT</th>" not in html
    assert "<th>Mean reply</th>" not in html
    assert "<th>Final</th>" not in html
    assert "<th>Size / active</th>" not in html
    assert ">26B<" in html
    assert ">3.8B<" in html
    assert "MoE" not in html.split("02 · Scoreboard", 1)[1].split("03 · Capability pack", 1)[0]
    assert "The measure below is <b>Minute:Second</b> estimate." in html
    assert "01 · What each size actually won" in html
    assert "02 · Scoreboard" in html
    assert "03 · Capability pack" in html
    assert "04 · Time anatomy" in html
    assert "05 · Estimate total respond time per task" in html
    assert "06 · Model quality" in html
    assert "3:20" in html
    assert html.count(">Light<") == 0
    assert "Phase 1</th>" not in html
    assert "Phase 2</th>" not in html
    assert "Finish</th>" not in html
    assert "24 / 88" not in html
    banned = [
        "Read the wait first",
        "How the estimate is built",
        "Source notes",
        "One number per model",
        "Instruction following is the tax",
        "Score is percent correct",
        "Green row = recommended",
        "For chat work, the first token",
        "Phase 2 is the same capability pack",
        "Em dashes mean",
        "F = ½ P1",
        "xAI",
        "Elon",
        "Grok",
    ]
    for phrase in banned:
        assert phrase not in html
    assert "—" in html


def test_engineering_picks_quality_not_the_fast_midsize():
    gemma = _run(
        model_name="Gemma 4 26B",
        model_key="gemma-4-26b-26b-3.8b",
        total_b=26,
        active_b=3.8,
        ttft_s=1.1,
        final=89,
        phase2=88,
        capabilities={
            "Reasoning": 78,
            "Coding": 80,
            "Instruction following": 92,
            "Structured output": 88,
            "Math": 70,
        },
    )
    oss = _run(
        run_id="20260901-030000-cccccc",
        model_name="GPT-OSS 120B",
        model_key="gpt-oss-120b-120b-5.1b",
        arch="MoE",
        total_b=120,
        active_b=5.1,
        tok_s=40,
        ttft_s=5.7,
        mean_s=12,
        phase1=92,
        phase2=94,
        final=93,
        capabilities={
            "Reasoning": 94,
            "Coding": 96,
            "Instruction following": 88,
            "Structured output": 90,
            "Math": 91,
        },
    )
    wins = pick_winners([gemma, oss])
    assert wins.everyday and wins.everyday.model_key == gemma.model_key
    assert wins.coder and wins.coder.model_key == oss.model_key
    html = build_comparison_html([gemma, oss], source_count=2)
    assert "for software engineering" in html.lower() or "Software engineering" in html
    assert "Best for code and reasoning" in html
    assert "quality first" in html.lower()
    assert "Gemma 4 26B for chat and play" in html
    assert "GPT-OSS 120B for software engineering" in html
    assert "class=best" not in html


def test_avg_task_seconds_is_mean_of_role_estimates():
    personas = [
        PersonaRow("Consumer", "Everyday Organizer", 8, 9, 3),
        PersonaRow("Commercial", "Engineer & Software Developer", 1, 1, 1),
        PersonaRow("Consumer", "Incomplete", 2, 2, None),
    ]
    # (8+9+3)*10 = 200, (1+1+1)*10 = 30; incomplete skipped → 115s → 1:55
    assert avg_task_seconds(personas) == 115
    html = build_comparison_html(
        [_run(personas=personas[:2])],
        source_count=1,
    )
    board = html.split("02 · Scoreboard", 1)[1].split("03 · Capability pack", 1)[0]
    assert ">1:55<" in board
    assert "<th>TTFT</th>" not in board
    assert "<th>Mean reply</th>" not in board
    assert "<th>Final</th>" not in board
    ranks = html.split("05 · Estimate total respond time per task", 1)[1].split("<table>", 1)[0]
    assert "time-rank" in ranks
    assert ">1:55<" in ranks
    assert 'class="time-ranks"' in html
    assert 'class="grid time-ranks"' not in html


def test_time_rank_cards_fastest_to_slowest():
    fast = _run(
        model_name="llama3.2:1b",
        model_key="llama-3-2-1b-1b-1b",
        final=30,
        personas=[PersonaRow("Consumer", "Everyday Organizer", 1, 1, 1)],
    )
    slow = _run(
        run_id="20260901-040000-dddddd",
        model_name="Gemma 4 26B",
        final=89,
        personas=[PersonaRow("Consumer", "Everyday Organizer", 8, 9, 3)],
    )
    html = build_comparison_html([slow, fast], source_count=2)
    block = html.split("05 · Estimate total respond time per task", 1)[1].split("07 ·", 1)[0]
    table_at = block.find("<table>")
    assert table_at > 0
    before_table = block[:table_at]
    after_table = block[table_at:]
    assert before_table.index("Fastest") < before_table.index("06 · Model quality")
    assert before_table.index("06 · Model quality") < table_at
    assert "06 · Model quality" not in after_table
    ranks = before_table.split("06 · Model quality", 1)[0]
    assert ranks.index("llama3.2:1b") < ranks.index("Gemma 4 26B")
    assert "Fastest" in ranks
    assert "Slowest" in ranks
    assert ">0:30<" in ranks
    assert ">3:20<" in ranks
    quality = before_table.split("06 · Model quality", 1)[1]
    assert "Highest quality" in quality
    assert "Lowest quality" not in quality
    assert "Not recommended" in quality
    assert quality.index("Highest quality") < quality.index("Gemma 4 26B")
    assert quality.index("Not recommended") < quality.index("llama3.2:1b")
    assert "time-rank-val" not in quality
    assert ">89<" not in quality
    assert ">30<" not in quality

