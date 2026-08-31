from __future__ import annotations

import re

_MOE_A = re.compile(
    r"(?P<total>[\d.]+)\s*B\s*[-_/]\s*A\s*(?P<active>[\d.]+)\s*B",
    re.IGNORECASE,
)
_MOE_COMPACT = re.compile(
    r"(?P<total>[\d.]+)B-A(?P<active>[\d.]+)B",
    re.IGNORECASE,
)
_MIXTRAL = re.compile(r"(?P<experts>\d+)\s*[x×]\s*(?P<active>[\d.]+)\s*B", re.IGNORECASE)
_DENSE = re.compile(r"(?P<n>[\d.]+)\s*B\b", re.IGNORECASE)

# Official cards (total / active per token). Match the model id, pull tag, or HF path.
# Sources: Google Gemma 4 card, Qwen HF cards, OpenAI gpt-oss card, Moonshot Kimi Linear, DeepSeek V4 Flash.
_KNOWN: tuple[tuple[re.Pattern[str], str, str, bool], ...] = (
    (re.compile(r"kimi[-_/ ]?linear|48b[-_]?a3b", re.I), "48B", "3B", True),
    (re.compile(r"qwen3-coder-next|qwen3_coder_next|coder-next", re.I), "80B", "3B", True),
    (re.compile(r"qwen3-coder(?!-next)|qwen3_coder(?!_next)|coder-30b-a3b", re.I), "30B", "3.3B", True),
    (re.compile(r"qwen3-next|qwen3_next|80b[-_]?a3b", re.I), "80B", "3.9B", True),
    (re.compile(r"gpt-oss[:\s/_-]*120|gptoss[:\s/_-]*120", re.I), "120B", "5.1B", True),
    (re.compile(r"gpt-oss[:\s/_-]*20\b|gptoss[:\s/_-]*20\b", re.I), "21B", "3.6B", True),
    (re.compile(r"gemma[-_]?4[:\s_-]*26|26b[-_]?a4b", re.I), "26B", "3.8B", True),
    (re.compile(r"gemma[-_]?4[:\s_-]*31", re.I), "31B", "31B", False),
    (re.compile(r"gemma[-_]?4[:\s_-]*12", re.I), "12B", "12B", False),
    (re.compile(r"gemma[-_]?4[:\s_-]*e4b|gemma4:e4b", re.I), "4.5B", "4.5B", False),
    (re.compile(r"gemma[-_]?4[:\s_-]*e2b|gemma4:e2b", re.I), "2.3B", "2.3B", False),
    (re.compile(r"qwen3\.8[:\s/_-]*27|qwen3[._]8-27", re.I), "27B", "27B", False),
    (re.compile(r"deepseek[-_/ ]?v4[-_/ ]?flash", re.I), "284B", "13B", True),
    (re.compile(r"llama3\.2[:\s/_-]*1b|llama-3\.2-1b", re.I), "1B", "1B", False),
    (re.compile(r"llama3\.2[:\s/_-]*3b|llama-3\.2-3b", re.I), "3B", "3B", False),
)


def format_b(value: float | int | str | None) -> str:
    if value is None or value == "":
        return "—"
    try:
        n = float(str(value).strip().upper().rstrip("B"))
    except (TypeError, ValueError):
        text = str(value).strip()
        return text if text else "—"
    if n <= 0:
        return "—"
    if abs(n - round(n)) < 0.05:
        return f"{int(round(n))}B"
    return f"{n:.1f}B".replace(".0B", "B")


def total_b_value(label: object) -> float | None:
    """Numeric billions from a Total column like ``80B`` or ``3.9B``. Missing → None."""
    text = str(label or "").strip().upper().replace(",", "")
    if not text or text in {"—", "-", "N/A"}:
        return None
    m = re.search(r"([\d.]+)\s*B\b", text) or re.search(r"([\d.]+)", text)
    if not m:
        return None
    try:
        n = float(m.group(1))
    except ValueError:
        return None
    return n if n > 0 else None


def _from_count(n: int | float) -> str:
    if n >= 1_000_000_000:
        return format_b(n / 1_000_000_000)
    if n >= 1_000_000:
        return format_b(n / 1_000_000_000)
    return format_b(n)


def _pack(total: str, active: str, moe: bool) -> dict:
    return {
        "total": total,
        "active": active,
        "moe": moe,
        "label": f"{total} total · {active} active",
    }


def lookup_known(*sources: object) -> dict | None:
    blob = " ".join(str(s) for s in sources if s not in (None, ""))
    if not blob.strip():
        return None
    for pattern, total, active, moe in _KNOWN:
        if pattern.search(blob):
            return _pack(total, active, moe)
    return None


def parse_params(*sources: object) -> dict:
    """Return total/active parameter labels in billions.

    Known MoE cards override Ollama's dense ``parameter_size`` (e.g. gemma4:26b
    is 26B total / 3.8B active, not a dense 26B).
    """
    known = lookup_known(*sources)
    if known:
        return known

    blob = " ".join(str(s) for s in sources if s not in (None, "")).replace(",", " ")
    if not blob.strip():
        return {"total": "—", "active": "—", "moe": False, "label": "—"}

    compact = blob.replace(" ", "")
    m = _MOE_A.search(blob) or _MOE_COMPACT.search(compact)
    if m:
        return _pack(format_b(m.group("total")), format_b(m.group("active")), True)

    mx = _MIXTRAL.search(blob)
    if mx:
        experts = float(mx.group("experts"))
        active_n = float(mx.group("active"))
        return _pack(format_b(experts * active_n), format_b(active_n), True)

    for source in sources:
        if isinstance(source, (int, float)) and source > 1000:
            total = _from_count(float(source))
            return _pack(total, total, False)

    d = _DENSE.search(blob)
    if d:
        total = format_b(d.group("n"))
        return _pack(total, total, False)

    return {"total": "—", "active": "—", "moe": False, "label": "—"}
