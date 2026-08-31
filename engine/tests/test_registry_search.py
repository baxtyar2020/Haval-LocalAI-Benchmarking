from haval_engine.ollama.registry import (
    is_primary_tag,
    matching_slugs,
    name_matches_query,
    parse_library_slugs,
    parse_model_tags,
    quant_from_tag,
    search_models,
)


SEARCH_HTML = """
<a href="/library/qwen3">qwen3</a>
<a href="/library/qwen3-coder">coder</a>
<a href="/library/qwen3:8b">skip tagged</a>
<a href="/library/assets">skip</a>
"""

TAGS_HTML = """
<a href="/library/qwen3:8b">8b</a>
<a href="/library/qwen3:14b">14b</a>
<a href="/library/qwen3:30b-a3b">30b-a3b</a>
<a href="/library/qwen3:8b-q4_K_M">q4</a>
<a href="/library/qwen3:latest">latest</a>
<a href="/library/qwen3:8426a459-dd88-49cd-ae89-ece442e58ec5">uuid</a>
"""


def test_parse_search_and_tags():
    slugs = parse_library_slugs(SEARCH_HTML)
    assert slugs == ["qwen3", "qwen3-coder"]
    tags = parse_model_tags(TAGS_HTML, "qwen3")
    assert "8b" in tags
    assert "30b-a3b" in tags
    assert "8b-q4_K_M" in tags
    assert not any("8426" in t for t in tags)


def test_primary_and_quant():
    assert is_primary_tag("8b")
    assert is_primary_tag("30b-a3b")
    assert is_primary_tag("latest")
    assert not is_primary_tag("8b-q4_K_M")
    assert quant_from_tag("8b-q4_K_M").upper() == "Q4_K_M"
    assert quant_from_tag("Q4_K_XL").upper() == "Q4_K_XL"
    assert quant_from_tag("iq2_m") == "IQ2_M"
    assert quant_from_tag("fp16") == "FP16"
    from haval_engine.ollama.registry import precision_of

    assert precision_of(name="hf.co/x/Kimi:Q4_K_S") == "Q4_K_S"
    assert precision_of(tag="30b-a3b") == ""


def test_exact_tag_search_no_network():
    hits = search_models("qwen3:30b-a3b")
    assert hits[0]["name"] == "qwen3:30b-a3b"
    assert hits[0]["pull_command"] == "ollama pull qwen3:30b-a3b"
    assert hits[0]["params_total"] == "30B"
    assert hits[0]["params_active"] == "3B"
    assert hits[0]["params_moe"] is True


def test_hf_reference_search():
    hits = search_models("hf.co/someone/Kimi-Linear-48B-A3B-Instruct-GGUF:Q4_K_S")
    assert hits[0]["name"].startswith("hf.co/")
    assert hits[0]["params_total"] == "48B"
    assert hits[0]["params_active"] == "3B"
    assert hits[0]["pull_command"].startswith("ollama pull hf.co/")


def test_query_matches_name_not_related_listings():
    assert name_matches_query("gpt-oss", "gpt")
    assert name_matches_query("gpt-oss:20b", "gpt")
    assert name_matches_query("kimi-k2", "kimi")
    assert not name_matches_query("gemma4", "gpt")
    assert not name_matches_query("llama3.2", "kimi")
    assert not name_matches_query("openchat", "gpt")
    slugs = matching_slugs(
        ["gpt-oss", "gpt-oss-safeguard", "gemma4", "llama3.2", "deepseek-coder-v2", "kimi-k2"],
        "gpt",
    )
    assert slugs == ["gpt-oss", "gpt-oss-safeguard"]


def test_search_drops_unrelated_library_links(monkeypatch):
    search_html = """
    <a href="/library/gpt-oss">gpt-oss</a>
    <a href="/library/gemma4">gemma4</a>
    <a href="/library/llama3">llama</a>
    <a href="/library/gpt-oss-safeguard">safe</a>
    """

    def fake_fetch(url: str, timeout: float = 14) -> str:
        if "search" in url:
            return search_html
        if "gpt-oss-safeguard" in url:
            return '<a href="/library/gpt-oss-safeguard:20b">20b</a>'
        if "gpt-oss" in url:
            return '<a href="/library/gpt-oss:20b">20b</a>'
        return "<html></html>"

    monkeypatch.setattr("haval_engine.ollama.registry._fetch", fake_fetch)
    hits = search_models("gpt")
    names = [h["name"].lower() for h in hits]
    assert names
    assert all("gpt" in n.replace("-", "") for n in names)
    assert not any("gemma" in n or "llama" in n for n in names)
