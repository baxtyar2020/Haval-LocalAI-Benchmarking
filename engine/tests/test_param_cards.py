from haval_engine.models.param_cards import (
    cached_params,
    confirm_name,
    is_checked,
    parse_library_param_cards,
    pick_card,
    remember_checked,
)


LLAMA4_README = """
<div>
<pre>ollama run llama4:scout</pre>
109B parameter MoE model with 17B active parameters
<pre>ollama run llama4:maverick</pre>
400B parameter MoE model with 17B active parameters
</div>
"""


def test_parse_llama4_library_card():
    cards = parse_library_param_cards(LLAMA4_README, slug="llama4")
    mav = pick_card(cards, "llama4:maverick")
    scout = pick_card(cards, "llama4:scout")
    assert mav is not None
    assert mav["total"] == "400B"
    assert mav["active"] == "17B"
    assert mav["moe"] is True
    assert scout is not None
    assert scout["total"] == "109B"
    assert scout["active"] == "17B"


def test_parse_active_out_of_total():
    html = "This is a 21B active parameters out of 236B mixture-of-experts model."
    cards = parse_library_param_cards(html, slug="deepseek-coder-v2")
    pack = pick_card(cards, "deepseek-coder-v2:236b") or pick_card(cards, "deepseek-coder-v2")
    assert pack is not None
    assert pack["total"] == "236B"
    assert pack["active"] == "21B"


def test_checked_overwrites_wrong_active(tmp_path, monkeypatch):
    monkeypatch.setattr("haval_engine.models.param_cards._cache_path", lambda: tmp_path / "ollama-params.json")
    remember_checked("llama4:maverick", {"total": "401.6B", "active": "401.6B", "moe": False})
    assert cached_params("llama4:maverick")["active"] == "401.6B"
    remember_checked("llama4:maverick", {"total": "400B", "active": "17B", "moe": True})
    got = cached_params("llama4:maverick")
    assert got["active"] == "17B"
    assert got["total"] == "400B"
    assert got["checked"] is True
    assert is_checked("llama4:maverick")


def test_confirm_name_checks_installed_when_page_has_no_active(tmp_path, monkeypatch):
    monkeypatch.setattr("haval_engine.models.param_cards._cache_path", lambda: tmp_path / "ollama-params.json")

    def fake_fetch(url: str, timeout: float = 10) -> str:
        return "<html>Mixture-of-Experts code language model. parameters236B</html>"

    monkeypatch.setattr("haval_engine.ollama.registry._fetch", fake_fetch)
    pack = confirm_name("deepseek-coder-v2:236b")
    assert pack is not None
    assert pack["active"] == "21B"
    assert pack["total"] == "236B"
    assert is_checked("deepseek-coder-v2:236b")
    assert cached_params("deepseek-coder-v2:236b")["active"] == "21B"
