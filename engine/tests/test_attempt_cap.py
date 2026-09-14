from haval_engine.bench.orchestrator import attempt_wall_s
from haval_engine.ollama.client import output_is_stuck


def test_engineer_heavy_wall_is_budget_not_triple():
    assert attempt_wall_s({"total_s": 210}) == 420
    assert attempt_wall_s({"total_s": 30}) == 60
    assert attempt_wall_s({}) == 180
    assert attempt_wall_s({"total_s": 30}, think=True) == 180


def test_repeat_loop_detected():
    unit = "abcdefghij" * 8  # 80 chars
    assert output_is_stuck(unit * 6) is True
    assert output_is_stuck("A short unique answer about leases.") is False
    assert output_is_stuck("aa" * 250) is True
