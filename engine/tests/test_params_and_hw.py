from haval_engine.hardware import _looks_discrete_gpu, _parse_smi_usage, _smi_vram_gb
from haval_engine.models.params import parse_params
from haval_engine.report.context import _identity, build_context


def test_parse_moe_and_dense():
    moe = parse_params("48B-A3B")
    assert moe["total"] == "48B"
    assert moe["active"] == "3B"
    assert moe["moe"] is True
    gemma = parse_params("gemma4:26b")
    assert gemma["total"] == "26B"
    assert gemma["active"] == "3.8B"
    assert gemma["moe"] is True
    mix = parse_params("mixtral:8x7b")
    assert mix["total"] == "56B"
    assert mix["active"] == "7B"


def test_known_cards_from_installed_names():
    coder = parse_params("qwen3-coder:30b")
    assert coder["total"] == "30B"
    assert coder["active"] == "3.3B"
    coder_next = parse_params("qwen3-coder-next:latest")
    assert coder_next["total"] == "80B"
    assert coder_next["active"] == "3B"
    assert coder_next["moe"] is True
    nxt = parse_params("qwen3-next:80b")
    assert nxt["total"] == "80B"
    assert nxt["active"] == "3.9B"
    oss = parse_params("gpt-oss:120b")
    assert oss["active"] == "5.1B"
    q38 = parse_params("qwen3.8:27b-bf16")
    assert q38["total"] == "27B"
    assert q38["active"] == "27B"
    assert q38["moe"] is False
    flash = parse_params("bluehawana/deepseek-v4-flash:iq2_m")
    assert flash["total"] == "284B"
    assert flash["active"] == "13B"
    maverick = parse_params("401.6B", "llama4:maverick")
    assert maverick["total"] == "400B"
    assert maverick["active"] == "17B"
    assert maverick["moe"] is True
    coder_v2 = parse_params("235.7B", "deepseek-coder-v2:236b")
    assert coder_v2["total"] == "236B"
    assert coder_v2["active"] == "21B"
    scout = parse_params("llama4:scout")
    assert scout["total"] == "109B"
    assert scout["active"] == "17B"
    from haval_engine.models.params import total_b_value
    from haval_engine.models.library import _params_size_sort_key

    assert total_b_value("1B") < total_b_value("80B")
    ordered = sorted(
        [
            {"params_total": "80B", "display_name": "B"},
            {"params_total": "26B", "display_name": "A"},
            {"params_total": "—", "display_name": "Z"},
        ],
        key=_params_size_sort_key,
    )
    assert [r["display_name"] for r in ordered] == ["A", "B", "Z"]


def test_identity_uses_catalog_moe():
    ident = _identity("qwen3-next:80b")
    assert ident["total"] == "80B"
    assert ident["active"] == "3.9B"
    assert ident["arch"] == "MoE"
    coder_next = _identity("qwen3-coder-next:latest")
    assert coder_next["display"] == "Qwen 3 Coder Next"
    assert coder_next["total"] == "80B"
    assert coder_next["active"] == "3B"


def test_identity_from_ollama_name():
    ident = _identity("hf.co/someone/Kimi-Linear-48B-A3B-Instruct-GGUF:Q4_K_S")
    assert ident["total"] == "48B"
    assert ident["active"] == "3B"


def test_report_computer_name_and_unified_memory():
    run = {
        "id": "hw-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": "{}",
    }
    ctx = build_context(
        run,
        [],
        [],
        {
            "computer_name": "DESKTOP-HAVAL1",
            "cpu": "Test CPU",
            "gpu": "AMD Radeon Graphics",
            "ram_gb": 32,
            "unified_memory": True,
        },
    )
    assert ctx["product"] == "DESKTOP-HAVAL1"
    assert ctx["unified_memory"] is True
    assert ctx["mem_kind"] == "Unified memory"
    assert ctx["mem_value"] == "32 GB"
    assert ctx["models"][0]["ident"]["total"] == "26B"
    assert ctx["models"][0]["ident"]["active"] == "3.8B"


def test_report_dedicated_vram_tile():
    run = {
        "id": "dgpu-run",
        "status": "completed",
        "models_json": '["gemma4:26b"]',
        "summary_json": "{}",
    }
    ctx = build_context(
        run,
        [],
        [],
        {
            "computer_name": "WORKSTATION-9",
            "cpu": "Test CPU",
            "gpu": "NVIDIA GeForce RTX 4070",
            "ram_gb": 32,
            "vram_gb": 12,
            "unified_memory": False,
        },
    )
    assert ctx["product"] == "WORKSTATION-9"
    assert ctx["unified_memory"] is False
    assert ctx["mem_kind"] == "System memory"
    assert ctx["ram"] == "32 GB"
    assert "12 GB" in ctx["gpu_vram_label"]


def test_parse_smi_usage():
    vram, util = _parse_smi_usage("12345, 49140, 12\n23456, 49140, 8")
    assert vram == 36
    assert util == 10
    empty, none_u = _parse_smi_usage("")
    assert empty is None
    assert none_u is None


def test_smi_and_igpu():
    from haval_engine.hardware import gpu_card_copy, round_up_half

    assert _smi_vram_gb("NVIDIA GeForce RTX 4070, 12282 MiB") == 12.0
    assert _looks_discrete_gpu("AMD Radeon Graphics") is False
    assert _looks_discrete_gpu("NVIDIA GeForce RTX 4050 Laptop GPU") is True
    assert round_up_half(98.2) == 98.5
    assert round_up_half(98.9) == 99.0
    dual = gpu_card_copy(
        "NVIDIA RTX A6000, 49140 MiB\nNVIDIA RTX A6000, 49140 MiB",
        "",
    )
    assert dual["title"].startswith("2")
    assert "A6000" in dual["title"]
    assert dual["count"] == 2


def test_headline_is_pc_first():
    run = {
        "id": "head-run",
        "status": "completed",
        "models_json": '["llama3.2:1b"]',
        "summary_json": "{}",
    }
    ctx = build_context(run, [], [], {"cpu": "CPU", "gpu": "GPU", "ram_gb": 32, "computer_name": "DESKTOP-X"})
    assert ctx["headline"].startswith("How this PC performed on Llama 3.2")
    assert "1B" in ctx["headline"]
    from haval_engine.report.context import headline_for_run

    assert headline_for_run(run) == ctx["headline"]
    assert "active parameters" in ctx["headline"]
    assert "billion" not in ctx["headline"]
    assert "<em>" in ctx["headline_html"]
    html = __import__("haval_engine.report.render", fromlist=["render_html"]).render_html(ctx)
    assert "Each persona tag" not in html
    assert "Hover the label" not in html
    assert "of consumer use cases are a fit" not in html
    assert "of use cases are" in html
    assert "are not a fit" not in html
