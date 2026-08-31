from haval_engine.phase2.parse import extract_choice, extract_number, math_matches, reasoning_matches
from haval_engine.phase2.runner import MATH_PROMPT, REASONING_PROMPT


def test_prompts_match_havalllmphase2():
    assert REASONING_PROMPT.startswith(
        "Answer the following multiple choice question. Reply with ONLY the letter (A, B, C, or D)."
    )
    assert MATH_PROMPT.startswith(
        "Solve the following math problem. Give ONLY the numerical answer, nothing else."
    )


def test_extract_last_number_not_first_working():
    text = "Compute 18 * (25 - 7).\n18 * 18 = 324"
    assert extract_number(text) == 324
    assert math_matches(text, 324)


def test_extract_labeled_answer_first_number_after_answer():
    text = "Working: 18 times 18.\nAnswer: 324"
    assert extract_number(text) == 324
    assert math_matches(text, 324)


def test_answer_colon_fraction_takes_leading_integer():
    assert extract_number("Answer: 1/13") == 1
    assert not math_matches("Answer: 1/13", 0.0769230769, 0.001)


def test_last_number_when_no_answer_label():
    text = "x^2 - 5x + 6 = 0 so the sum is 5"
    assert extract_number(text) == 5
    assert math_matches(text, 324) is False
    assert math_matches(text, 5)


def test_answer_is_letter():
    assert extract_choice("The answer is B") == "B"
    assert reasoning_matches("The answer is B", "B")


def test_bare_letter_casefold_via_extract():
    assert extract_choice("b") == "B"
    assert reasoning_matches("b", "B")
    assert reasoning_matches("B", "B")


def test_option_echo_at_start_takes_a():
    text = "A) Some Z are Y\nB) Some Z are not Y\nAnswer: B"
    assert extract_choice(text) == "A"


def test_trailing_letter_when_text_does_not_start_with_option():
    assert extract_choice("I think the right one is\nC") == "C"
