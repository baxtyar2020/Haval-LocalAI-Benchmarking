from __future__ import annotations

from collections import Counter, defaultdict

from haval_engine.scoring.pipeline import role_speed_band

_HARDWARE = (
    "out of memory",
    "oom",
    "not enough memory",
    "failed to allocate",
    "cuda malloc",
    "cudamalloc",
    "unable to allocate",
    "ggml_gallocr",
    "mmap",
    "std::bad_alloc",
    "killed",
    "requires more",
    "model is too large",
)

_MESSAGES = {
    "hardware": (
        "This model is too large for this PC’s available memory. "
        "Try a smaller model. This result reflects a hardware limitation, not the model’s quality."
    ),
    "too_slow": (
        "This model can run on this PC, but it is too slow for every role you selected. "
        "That wait is not acceptable for those roles."
    ),
    "thinking": (
        "This model cannot run with thinking turned on. "
        "Try the same model with thinking off. This is not a quality score."
    ),
    "refused": (
        "The model never started an answer on this PC. "
        "Try another model. This is not a quality score."
    ),
    "timeout": (
        "This model did not finish answers in the time allowed on this PC. "
        "Try a smaller or faster model."
    ),
    "empty": "The model returned no usable answer to grade.",
    "unreachable": "Ollama was not running, so this test could not start. Open Doctor and try again.",
    "cancelled": "This run was stopped before it finished. Saved results are only what completed.",
    "unknown": "This run did not produce answers we can grade.",
}


def classify_error(err: str | None, *, thinking: bool = False, total_s: float | None = None) -> str:
    e = str(err or "").strip().lower()
    if not e or e in {"incomplete", "no_attempt"}:
        return "empty"
    if "cancel" in e:
        return "cancelled"
    if e in {"wall_timeout", "repeat_loop", "output_cap"} or "timeout" in e or "timed out" in e:
        return "timeout"
    if any(k in e for k in _HARDWARE):
        return "hardware"
    if "think" in e and any(k in e for k in ("400", "invalid", "unknown", "unsupported", "not support")):
        return "thinking"
    if any(k in e for k in ("10061", "connection refused", "failed to establish", "winerror 10061", "not answering")):
        return "unreachable"
    if "400" in e or "bad request" in e:
        if thinking and (total_s is None or total_s < 0.5):
            return "thinking"
        return "refused"
    if "404" in e:
        return "refused"
    return "unknown"


def fail_payload(kind: str) -> dict:
    kind = kind if kind in _MESSAGES else "unknown"
    text = _MESSAGES[kind]
    return {"kind": kind, "headline": text, "detail": "", "sample": "", "count": 0, "message": text}


def summarize_failures(attempts: list[dict], *, thinking: bool = False) -> dict | None:
    fails = [a for a in attempts if not a.get("ok")]
    if not fails:
        return None
    kinds = [
        classify_error(a.get("error"), thinking=thinking, total_s=_as_float(a.get("total_s")))
        for a in fails
    ]
    kind = Counter(kinds).most_common(1)[0][0]
    out = fail_payload(kind)
    out["count"] = len(fails)
    return out


def customer_fail_line(fail: dict | None) -> str:
    if not fail:
        return "This run did not produce answers we can grade."
    return str(fail.get("message") or fail.get("headline") or _MESSAGES["unknown"])


def phase1_all_hardware(attempts: list[dict], *, thinking: bool = False) -> bool:
    rows = [a for a in attempts if a]
    if not rows:
        return False
    return all(
        (not a.get("ok"))
        and classify_error(a.get("error"), thinking=thinking, total_s=_as_float(a.get("total_s"))) == "hardware"
        for a in rows
    )


def phase1_all_roles_too_slow(scores: list[dict], personas: list[str] | None = None) -> bool:
    if not scores:
        return False
    by_persona: dict[str, list[dict]] = defaultdict(list)
    for row in scores:
        name = str(row.get("persona") or "")
        if name:
            by_persona[name].append(row)
    wanted = [p for p in (personas or list(by_persona)) if p in by_persona]
    if not wanted:
        return False
    return all(_persona_too_slow(by_persona[p]) for p in wanted)


def phase1_any_role_continues(scores: list[dict], personas: list[str] | None = None) -> bool:
    """Phase 2 runs if any selected role produced a Fast or OK answer."""
    if not scores:
        return False
    by_persona: dict[str, list[dict]] = defaultdict(list)
    for row in scores:
        name = str(row.get("persona") or "")
        if name:
            by_persona[name].append(row)
    wanted = [p for p in (personas or list(by_persona)) if p in by_persona] or list(by_persona)
    return any(_persona_continues(by_persona.get(p) or []) for p in wanted)


def _persona_continues(rows: list[dict]) -> bool:
    if not any((r.get("successful") or 0) > 0 for r in rows):
        return False
    return _persona_speed(rows) in {"Fast", "OK"}


def _persona_too_slow(rows: list[dict]) -> bool:
    if not rows:
        return False
    if not any((r.get("successful") or 0) > 0 for r in rows):
        return False
    return _persona_speed(rows) == "Slow"


def _persona_speed(rows: list[dict]) -> str:
    stored = [str(r.get("role_speed") or "") for r in rows if r.get("role_speed")]
    if stored:
        return stored[0]
    actuals: list[float | None] = []
    expecteds: list[float | None] = []
    heavy_actual = None
    for r in rows:
        act = _as_float(r.get("actual_s") if r.get("actual_s") is not None else r.get("total_s"))
        exp = _as_float(r.get("expected_s"))
        if act is None or exp is None:
            continue
        actuals.append(act)
        expecteds.append(exp)
        if str(r.get("intensity") or "") == "Heavy":
            heavy_actual = act
    if actuals and expecteds:
        return role_speed_band(actuals, expecteds, heavy_actual)
    bands = [str(r.get("internal") or "—") for r in rows]
    if all(b == "Slow" for b in bands):
        return "Slow"
    if any(b == "Fast" for b in bands):
        return "Fast"
    if any(b == "OK" for b in bands):
        return "OK"
    return "—"


def _as_float(value: object) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None
