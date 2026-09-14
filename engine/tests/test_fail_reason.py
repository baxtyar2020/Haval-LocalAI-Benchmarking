from haval_engine.scoring.fail_reason import (
    classify_error,
    customer_fail_line,
    fail_payload,
    phase1_all_hardware,
    phase1_all_roles_too_slow,
    phase1_any_role_continues,
    summarize_failures,
)
from haval_engine.scoring.pipeline import evaluate_match


def test_classify_thinking_http_400():
    assert classify_error("HTTP 400: Bad Request", thinking=True, total_s=0.02) == "thinking"
    assert classify_error("HTTP 400: invalid think", thinking=False, total_s=0.02) == "thinking"


def test_classify_hardware_oom():
    assert classify_error("cuda malloc failed: out of memory", thinking=False, total_s=1.2) == "hardware"
    assert (
        classify_error(
            "llama-server process has terminated: exit status 1: cudaMalloc failed: out of memory",
            thinking=False,
            total_s=12.2,
        )
        == "hardware"
    )


def test_classify_timeout():
    assert classify_error("wall_timeout", thinking=False, total_s=90) == "timeout"


def test_summarize_fast_400_thinking():
    fail = summarize_failures(
        [
            {"ok": 0, "error": "HTTP 400: Bad Request", "total_s": 0.012},
            {"ok": 0, "error": "HTTP 400: Bad Request", "total_s": 0.018},
        ],
        thinking=True,
    )
    assert fail["kind"] == "thinking"
    line = customer_fail_line(fail)
    assert "thinking turned on" in line.lower()
    assert "HTTP 400" not in line
    assert "milliseconds" not in line.lower()


def test_customer_hardware_copy_is_plain():
    line = customer_fail_line(fail_payload("hardware"))
    assert "too large for this PC" in line
    assert "not the model" in line.lower()
    assert "cuda" not in line.lower()
    assert "ROCm" not in line


def test_all_roles_too_slow():
    scores = [
        {"persona": "Everyday Organizer", "internal": "Slow", "successful": 1},
        {"persona": "Everyday Organizer", "internal": "Slow", "successful": 1},
        {"persona": "Engineer & Software Developer", "internal": "Slow", "successful": 1},
        {"persona": "Engineer & Software Developer", "internal": "Slow", "successful": 1},
    ]
    assert phase1_all_roles_too_slow(scores, ["Everyday Organizer", "Engineer & Software Developer"]) is True
    scores[2]["internal"] = "Fast"
    assert phase1_all_roles_too_slow(scores, ["Everyday Organizer", "Engineer & Software Developer"]) is False
    assert phase1_any_role_continues(scores, ["Everyday Organizer", "Engineer & Software Developer"]) is True


def test_role_times_heavy_fast_is_not_too_slow():
    scores = [
        {"persona": "Everyday Organizer", "intensity": "Light", "internal": "Slow", "successful": 1, "actual_s": 42, "expected_s": 25},
        {"persona": "Everyday Organizer", "intensity": "Balanced", "internal": "OK", "successful": 1, "actual_s": 53, "expected_s": 45},
        {"persona": "Everyday Organizer", "intensity": "Heavy", "internal": "Fast", "successful": 1, "actual_s": 23, "expected_s": 90},
    ]
    assert phase1_all_roles_too_slow(scores, ["Everyday Organizer"]) is False
    assert phase1_any_role_continues(scores, ["Everyday Organizer"]) is True


def test_all_hardware_attempts():
    atts = [
        {"ok": 0, "error": "cudaMalloc failed: out of memory", "total_s": 12},
        {"ok": 0, "error": "unable to allocate ROCm0 buffer", "total_s": 12},
    ]
    assert phase1_all_hardware(atts) is True
    atts[1] = {"ok": 1, "error": None, "total_s": 8}
    assert phase1_all_hardware(atts) is False


def test_evaluate_match_uses_fail_why():
    result = evaluate_match(
        finish=0,
        answer=None,
        fail_why=customer_fail_line(fail_payload("hardware")),
    )
    assert result["label"] == "Failed"
    assert "too large for this PC" in result["why"]
