from haval_engine.pack import write_scenarios_json
from haval_engine.pack.matrix import PERSONA_TOTAL_S, PERSONA_TTFT, scenarios
from haval_engine.grading.engine import grade_seed
from haval_engine.grading.validators import validate_fixture
from haval_engine.pack.fixture_data import fixtures, write_fixtures
from haval_engine.pack.weights import forty_sixty, weighted_quality


def test_playbooks_cover_every_phase1_persona():
    from haval_engine.pack.playbook_asks import parse_all_playbooks

    books = parse_all_playbooks()
    personas = {row["persona"] for row in scenarios()}
    assert personas <= set(books)
    for name in personas:
        for tier in ("Light", "Balanced", "Heavy"):
            assert (books.get(name) or {}).get(tier), (name, tier)


def test_sixty_scenarios_and_one_attempt():
    rows = scenarios()
    assert len(rows) == 60
    ids = [r["id"] for r in rows]
    assert len(set(ids)) == 60
    businesses = {r["business"] for r in rows}
    assert businesses == {"Consumer", "Gaming", "Commercial"}
    assert sum(1 for r in rows if r["business"] == "Consumer") == 24
    assert sum(1 for r in rows if r["business"] == "Gaming") == 12
    assert sum(1 for r in rows if r["business"] == "Commercial") == 24
    for row in rows:
        assert row["attempts"] == 1
        assert row["total_s"] == PERSONA_TOTAL_S[row["persona"]][row["intensity"]]
        assert row["ttft_s"] == PERSONA_TTFT[row["persona"]][row["intensity"]]
        assert row["total_s"] <= 210
        assert abs(sum(row["weights"].values()) - 1.0) < 1e-6
        assert set(row["weights"]) <= set(row["dimensions"]) or set(row["weights"]) == set(row["dimensions"])


def test_forty_sixty_and_explicit_g_rd_h():
    w = forty_sixty("I", ["I", "S"])
    assert w["I"] == 0.4
    assert abs(w["S"] - 0.6) < 1e-9
    g = next(r for r in scenarios() if r["id"] == "G-RD-H")
    assert g["alias"] == "GAM-RGD-H-001"
    assert g["weights"] == {"P": 0.40, "R": 0.25, "I": 0.20, "S": 0.15}


def test_writer_heavy_nr_and_wall_windows():
    row = next(r for r in scenarios() if r["id"] == "C-WC-H")
    assert row["total_s"] == 90
    assert row["total_s"] * 1.5 == 135
    assert row["total_s"] * 2 == 180


def test_support_is_tighter_than_engineering():
    support_h = next(r for r in scenarios() if r["id"] == "B-CS-H")
    eng_h = next(r for r in scenarios() if r["id"] == "B-EN-H")
    assert support_h["total_s"] == 120
    assert eng_h["total_s"] == 210


def test_developer_scenarios_score_chat_text_not_hidden_execution():
    from haval_engine.grading.engine import grade_output

    for sid in ("G-RD-L", "G-RD-B", "G-RD-H", "B-EN-L", "B-EN-B", "B-EN-H"):
        row = next(r for r in scenarios() if r["id"] == sid)
        assert row["grader"] != "code"
        assert not (row.get("code_tests") or "").strip()
        stub = "Here is a generic function with no required names.\nI started Docker and hit Play."
        g = grade_output(row, stub)
        assert not g["passed"], (sid, g)


def test_sandbox_kills_infinite_loop():
    import time

    from haval_engine.grading.sandbox import run_python_snippet

    t0 = time.perf_counter()
    result = run_python_snippet("while True:\n    pass\n", timeout=1)
    elapsed = time.perf_counter() - t0
    assert result["ok"] is False
    assert elapsed < 8
    assert "timeout" in str(result.get("error") or "").lower() or result.get("error")


def test_every_scenario_good_passes_bad_fails():
    write_fixtures()
    write_scenarios_json()
    failed = []
    for row in scenarios():
        good = grade_seed(row, "good")
        bad = grade_seed(row, "bad")
        if not good["passed"]:
            failed.append((row["id"], "good", good))
        if bad["passed"]:
            failed.append((row["id"], "bad-should-fail", bad))
        if bad["Q"] >= good["Q"]:
            failed.append((row["id"], "bad-not-worse", good, bad))
    assert not failed, failed[:8]


def test_fixtures_validate():
    write_fixtures()
    for name, body in fixtures().items():
        ok, reason = validate_fixture(body)
        assert ok, (name, reason)


def test_weighted_quality_ignores_na():
    assert weighted_quality({"I": 100, "S": 50}, {"I": 0.4, "S": 0.6}) == 70.0
