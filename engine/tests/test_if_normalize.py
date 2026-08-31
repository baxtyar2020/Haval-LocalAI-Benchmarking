from haval_engine.grading.engine import grade_output
from haval_engine.grading.match import contains_phrase
from haval_engine.pack.matrix import scenarios


def _row(sid: str) -> dict:
    return next(r for r in scenarios() if r["id"] == sid)


def test_ram_and_clock_paraphrases():
    assert contains_phrase("Laptop A with 16 GB of RAM is the better pick.", "16gb")
    assert contains_phrase("Keep the 3:00 p.m. slot.", "3pm")
    assert contains_phrase("I would pick Laptop A for video editing.", "recommend")


def test_c_rs_l_paraphrase_still_grades_quality():
    row = _row("C-RS-L")
    paraphrased = (
        "A: 16GB, 1.3kg, $899, fits for travel. "
        "B is over budget. C is heavy and over $1100. Cheapest that fits is A."
    )
    good = grade_output(row, paraphrased)
    assert good["Q"] >= 75
    assert not good["hard_fail"]


def test_c_eo_l_numbered_list_not_json_hard_fail():
    row = _row("C-EO-L")
    assert not row["json_required"]
    out = grade_output(
        row,
        "Thu 6:00pm dentist\nNeed milk\nSat 11am soccer (moved from 9am)\nChanged: soccer to 11am.\nFridge: dentist Thursday.",
    )
    assert out["Q"] >= 75
    assert not out["hard_fail"]


def test_c_wc_l_keeps_time_without_saying_meeting():
    row = _row("C-WC-L")
    out = grade_output(
        row,
        "We missed the 12 May ship date by 4 days. Two engineers were out. The 3pm review on Thursday still stands.\nWord count: 28",
    )
    assert out["Q"] >= 75


def test_family_dinner_does_not_need_the_word_peanut():
    row = _row("C-FC-L")
    out = grade_output(
        row,
        "Who: Kid A. When: Thu 6:00pm. Where: field B. Snack: parent 2. Allergy: no peanuts in any snack.",
    )
    assert out["passed"]


def test_stardew_owned_titles_are_enough():
    row = _row("G-CG-L")
    out = grade_output(
        row,
        "Stardew: cozy farm in 90 minutes. Overcooked 2: light co-op. Rocket League: short matches. No new buy.",
    )
    assert out["passed"]


def test_tiny_wording_misses_still_count_as_answered():
    assert contains_phrase("Rocketleague and Overcooked2 tonight.", "rocket league")
    assert contains_phrase("Repairs were $1,400 last year.", "1400")
    assert contains_phrase("Keep the May 12 ship date.", "12 may")

    gamer_l = grade_output(
        _row("G-CG-L"),
        "Stardew Valley cozy. Overcooked2 kitchen. Rocketleague short matches. No new buy.",
    )
    assert gamer_l["checks"]["answered"]

    gamer_b = grade_output(
        _row("G-CG-B"),
        "Stardew: 1 load farm 2 water the crops 3 pet 4 ship 5 go to bed 6 quit.",
    )
    assert gamer_b["passed"]

    gamer_h = grade_output(
        _row("G-CG-H"),
        "Stardew: three 50-minute blocks with a rest between each. Fun, not min-max.",
    )
    assert gamer_h["checks"]["answered"]

    shop = grade_output(
        _row("C-RS-L"),
        "A is $899, 16 GB, yes it fit for travel. B over budget. C too heavy.",
    )
    assert shop["checks"]["answered"]

    writer = grade_output(
        _row("C-WC-L"),
        "We missed the May 12 ship date by four days. The 3pm Thursday review still stands.\nWord count: 24",
    )
    assert writer["checks"]["answered"]

    hobby = grade_output(
        _row("C-TH-L"),
        "You cannot add an int to a str. Smallest fix: use an f-string for n.",
    )
    assert hobby["checks"]["answered"]

    eng = grade_output(
        _row("B-EN-L"),
        "Python CLI using sha256 in chunks and sys.argv. Example: python dupes.py ./folder",
    )
    assert eng["checks"]["answered"]


def test_real_misses_still_fail():
    gamer_l = grade_output(_row("G-CG-L"), "Just play Elden Ring tonight.")
    assert not gamer_l["checks"]["answered"]
    gamer_b = grade_output(_row("G-CG-B"), "Here is the full Stardew wiki and overclock your GPU.")
    assert not gamer_b["passed"]
