from haval_engine.scoring.pipeline import (
    combine_phases,
    match_label,
    havalllmphase2_quality_total,
    persona_phase2_score,
    phase1_score,
    reliability,
    speed_band,
)


def test_finish_three_attempts():
    assert reliability(3, 3) == 100
    assert reliability(2, 3) == 200 / 3
    assert reliability(0, 0) is None


def test_speed_bands():
    assert speed_band(7, 10) == "Fast"
    assert speed_band(10, 10) == "Fast"
    assert speed_band(13, 10) == "OK"
    assert speed_band(14, 10) == "OK"
    assert speed_band(15, 10) == "Slow"
    assert speed_band(20, 10) == "Slow"
    assert speed_band(None, 10) == "—"


def test_role_speed_first_look_stops_at_fast():
    from haval_engine.scoring.pipeline import role_speed_band

    # Everyday Organizer: expected avg 53.3s. Real report times.
    assert role_speed_band([42, 53, 23], [25, 45, 90], heavy_actual=23) == "Fast"
    # Average over expected, but Heavy still under the average expected.
    assert role_speed_band([80, 80, 40], [25, 45, 90], heavy_actual=40) == "Fast"


def test_role_speed_second_look():
    from haval_engine.scoring.pipeline import role_speed_band

    expected = [25, 45, 90]  # avg 53.3; 1.5× ≈ 80; 2× ≈ 107
    assert role_speed_band([70, 80, 60], expected, heavy_actual=60) == "Fast"
    assert role_speed_band([90, 95, 85], expected, heavy_actual=85) == "OK"
    assert role_speed_band([120, 130, 110], expected, heavy_actual=110) == "Slow"


def test_slow_at_1_5x_is_not_recommended():
    assert match_label(finish=100, answer=92, speed="Slow") == "Not Recommended"
    assert match_label(finish=100, answer=92, speeds=["Fast", "OK", "Slow"]) == "Not Recommended"


def test_phase1_slow_perfect_is_not_excellent():
    from haval_engine.scoring.rules import load_ruleset

    load_ruleset.cache_clear()
    score = phase1_score(
        content=100,
        speed="Slow",
        answers=[100, 100, 100],
        successful=3,
        attempted=3,
        headrooms=[0.2, 0.2, 0.2],
        tok_s=[40, 40, 40],
    )
    assert score is not None
    assert score < 48
    assert match_label(finish=100, answer=score, speed="Slow") == "Not Recommended"


def test_phase1_failed_content_not_rescued_by_speed():
    from haval_engine.scoring.rules import load_ruleset

    load_ruleset.cache_clear()
    score = phase1_score(
        content=25,
        speed="Fast",
        answers=[25, 25, 25],
        successful=3,
        attempted=3,
        headrooms=[0.2, 0.2, 0.2],
        tok_s=[80, 80, 80],
    )
    assert score is not None
    assert score < 48


def test_phase1_fast_correct_stays_high():
    from haval_engine.scoring.rules import load_ruleset

    load_ruleset.cache_clear()
    score = phase1_score(
        content=100,
        speed="Fast",
        answers=[100, 100, 100],
        successful=3,
        attempted=3,
        headrooms=[0.2, 0.2, 0.2],
        tok_s=[40, 40, 40],
    )
    assert score is not None
    assert score >= 88


def test_match_label_six_bands():
    assert match_label(finish=100, answer=92) == "Excellent"
    assert match_label(finish=100, answer=80) == "Strong"
    assert match_label(finish=100, answer=68) == "Acceptable"
    assert match_label(finish=100, answer=55) == "Marginal Match"
    assert match_label(finish=100, answer=20) == "Not Recommended"
    assert match_label(finish=0, answer=99) == "Failed"


def test_havalllmphase2_renormalizes_without_multilingual():
    total = havalllmphase2_quality_total(
        {"reasoning": 100, "coding": 100, "instructionFollowing": 100, "structuredOutput": 100, "math": 100}
    )
    assert total == 100
    half = havalllmphase2_quality_total(
        {"reasoning": 50, "coding": 50, "instructionFollowing": 50, "structuredOutput": 50, "math": 50}
    )
    assert half == 50


def test_persona_phase2_weights_engineer_toward_coding():
    cats = {"reasoning": 0, "coding": 100, "instructionFollowing": 0, "structuredOutput": 0, "math": 0}
    eng = persona_phase2_score("Engineer & Software Developer", cats)
    writer = persona_phase2_score("Writer & Communicator", cats)
    assert eng is not None and writer is not None
    assert eng > writer


def test_combine_phases_50_50():
    assert combine_phases(100, 0) == 50
    assert combine_phases(0, 100) == 50


def test_critical_floor_blocks_strong_without_coding():
    from haval_engine.scoring.pipeline import evaluate_match

    cats = {"reasoning": 90, "coding": 20, "instructionFollowing": 90, "structuredOutput": 90, "math": 90}
    result = evaluate_match(
        finish=100,
        answer=90,
        personas=["Engineer & Software Developer"],
        phase2_pct=cats,
        content=90,
        speeds=["Fast"],
    )
    assert result["label"] != "Excellent"
    assert result["label"] != "Strong"
    assert result["blocked_by"] == "coding"
    assert "coding" in result["why"].lower()


def test_excellent_tooltip_names_reasoning_and_coding():
    from haval_engine.scoring.pipeline import evaluate_match

    cats = {"reasoning": 90, "coding": 88, "instructionFollowing": 80, "structuredOutput": 80, "math": 40}
    result = evaluate_match(
        finish=100,
        answer=92,
        personas=["Technical Hobbyist"],
        phase2_pct=cats,
        content=90,
        speeds=["Fast", "Fast", "Fast"],
    )
    assert result["label"] == "Excellent"
    assert "fast" in result["why"].lower()
    assert "coding" in result["why"].lower()


def test_zero_floor_skips_coding_for_writer():
    from haval_engine.scoring.pipeline import evaluate_match

    cats = {"reasoning": 90, "coding": 0, "instructionFollowing": 90, "structuredOutput": 90, "math": 0}
    result = evaluate_match(
        finish=100,
        answer=92,
        personas=["Writer & Communicator"],
        phase2_pct=cats,
        content=90,
        speeds=["Fast"],
    )
    assert result["blocked_by"] != "coding"
    assert result["label"] in {"Excellent", "Strong", "Acceptable"}


def test_engineer_coding_floor_from_role_sheet():
    from haval_engine.scoring.pipeline import evaluate_match

    cats = {"reasoning": 90, "coding": 50, "instructionFollowing": 90, "structuredOutput": 90, "math": 90}
    result = evaluate_match(
        finish=100,
        answer=90,
        personas=["Engineer & Software Developer"],
        phase2_pct=cats,
        content=90,
        speeds=["Fast"],
    )
    assert result["blocked_by"] == "coding"
    assert result["label"] == "Not Recommended"


def test_product_math_floor_from_updated_sheet():
    from haval_engine.scoring.pipeline import evaluate_match
    from haval_engine.scoring.rules import load_ruleset

    load_ruleset.cache_clear()
    floors = load_ruleset()["persona_phase2_floors"]["Research & Product Professional"]
    assert floors["math"] == 30
    assert floors["coding"] == 0
    cats = {"reasoning": 90, "coding": 0, "instructionFollowing": 90, "structuredOutput": 90, "math": 20}
    result = evaluate_match(
        finish=100,
        answer=90,
        personas=["Research & Product Professional"],
        phase2_pct=cats,
        content=90,
        speeds=["Fast"],
    )
    assert result["blocked_by"] == "math"
    assert result["label"] == "Not Recommended"
