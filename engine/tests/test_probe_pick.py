from haval_engine.doctor.probe_model import (
    DEFAULT_PROBE_MODEL,
    is_hidden_probe_model,
    pick_probe_model,
)


def test_hidden_probe_tag():
    assert is_hidden_probe_model(DEFAULT_PROBE_MODEL)
    assert is_hidden_probe_model("smollm:135m-instruct-v0.2-q2_K")
    assert not is_hidden_probe_model("smollm:360m")
    assert not is_hidden_probe_model("llama3.2:1b")


def test_does_not_treat_26b_as_probe():
    models = [{"name": "gemma4:26b", "size": 16 * 1024**3}]
    assert pick_probe_model(models, [DEFAULT_PROBE_MODEL]) is None


def test_prefers_installed_smollm_probe():
    models = [
        {"name": "gemma4:26b", "size": 16 * 1024**3},
        {"name": DEFAULT_PROBE_MODEL, "size": 88 * 1024**2},
        {"name": "llama3.2:1b", "size": 1_300_000_000},
    ]
    assert pick_probe_model(models, [DEFAULT_PROBE_MODEL]) == DEFAULT_PROBE_MODEL


def test_does_not_probe_user_1b_or_8b():
    models = [
        {"name": "llama3.2:1b", "size": 1_300_000_000},
        {"name": "llama3:8b", "size": 4 * 1024**3},
        {"name": "qwen2.5:3b", "size": 2 * 1024**3},
    ]
    assert pick_probe_model(models, []) is None
    assert pick_probe_model(models, ["llama3.2:1b"]) is None
