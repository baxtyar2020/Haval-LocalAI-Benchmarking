from haval_engine.bench.display_text import phase1_question, phase2_question
from haval_engine.pack.matrix import scenarios as build_scenarios
from haval_engine.phase2 import load_json


def test_every_phase1_scenario_has_plain_text():
    ids = {row["id"] for row in build_scenarios()}
    for row in build_scenarios():
        text = phase1_question(row)
        assert text, row["id"]
        assert "WEEK_PLAN" not in text
        assert "FAMILY_MONTH" not in text
        assert "```json" not in text.lower()
    assert len(ids) == 60
def test_phase1_display_uses_ask_matrix_not_the_generate_prompt():
    from haval_engine.pack.ask_blurbs import parse_role_blurbs

    books = parse_role_blurbs()
    assert len(books) == 20
    casual = books["Casual Gamer"]["Light"]
    assert casual.startswith("I have about 90 minutes")
    for row in build_scenarios():
        shown = phase1_question(row)
        blurb = books[row["persona"]][row["intensity"]]
        assert shown == blurb
        assert shown != row["prompt"]


def test_phase2_structured_has_no_json():
    for item in load_json("structured-output.json"):
        text = phase2_question("structuredOutput", item)
        assert text
        assert "{" not in text and "}" not in text
        assert "JSON" not in text
        assert "TypeScript" not in text
