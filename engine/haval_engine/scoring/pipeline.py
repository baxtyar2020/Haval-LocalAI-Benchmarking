from __future__ import annotations

from haval_engine.scoring.rules import load_ruleset


def reliability(successful: int, attempted: int) -> float | None:
    if attempted <= 0:
        return None
    return 100.0 * successful / attempted


def mean(values: list[float | None]) -> float | None:
    nums = [v for v in values if v is not None]
    if not nums:
        return None
    return sum(nums) / len(nums)


def speed_band(actual_s: float | None, target_s: float) -> str:
    if actual_s is None or target_s <= 0:
        return "—"
    if actual_s <= target_s:
        return "Fast"
    multiple = float(load_ruleset().get("speed_ok_multiple") or 1.5)
    # Under 1.5×: OK but very slow. At 1.5× or more: Slow → Not Recommended.
    if actual_s < target_s * multiple:
        return "OK"
    return "Slow"


def role_speed_band(
    actuals: list[float | None],
    expecteds: list[float | None],
    heavy_actual: float | None = None,
) -> str:
    """Phase 1 time for a whole role (Light + Balanced + Heavy), not one ask.

    First look: Fast if the average finish is at or under the average expected
    time, or if Heavy alone finished at or under that same average expected.
    Second look: under 1.5× expected average is still Fast; 1.5× through 2× is
    OK (very slow); over 2× is Slow / Not Recommended.
    """
    avg_a = mean(list(actuals))
    avg_e = mean(list(expecteds))
    if avg_a is None or avg_e is None or avg_e <= 0:
        return "—"
    if avg_a <= avg_e or (heavy_actual is not None and heavy_actual <= avg_e):
        return "Fast"
    ok_m = float(load_ruleset().get("speed_ok_multiple") or 1.5)
    wall_m = float(load_ruleset().get("speed_wall_multiple") or 2.0)
    if avg_a < avg_e * ok_m:
        return "Fast"
    if avg_a <= avg_e * wall_m:
        return "OK"
    return "Slow"


def speed_points(band: str | None) -> float | None:
    if not band:
        return None
    pts = load_ruleset().get("speed_points") or {"Fast": 100, "OK": 75, "Slow": 20}
    if band not in pts:
        return None
    return float(pts[band])


def consistency_score(answers: list[float | None], successful: int, attempted: int) -> float | None:
    if attempted <= 0:
        return None
    finish = 100.0 * successful / attempted
    nums = [v for v in answers if v is not None]
    if not nums:
        return 0.0
    if len(nums) == 1:
        return 0.6 * finish + 0.4 * float(nums[0])
    spread = max(nums) - min(nums)
    tightness = max(0.0, 100.0 - spread)
    return 0.5 * finish + 0.5 * tightness


def sustainability_score(headrooms: list[float | None], tok_s: list[float | None]) -> float:
    unknown = float(load_ruleset().get("sustainability_unknown") or 50)
    heads = [h for h in headrooms if h is not None]
    if heads:
        h = sum(heads) / len(heads)
        if h >= 0.15:
            mem = 100.0
        elif h >= 0.08:
            mem = 80.0
        elif h >= 0.03:
            mem = 55.0
        else:
            mem = 30.0
    else:
        mem = unknown
    toks = [t for t in tok_s if t is not None and t > 0]
    if len(toks) >= 2:
        avg = sum(toks) / len(toks)
        var = sum((t - avg) ** 2 for t in toks) / len(toks)
        std = var**0.5
        if avg > 0 and std / avg > 0.3:
            mem = min(mem, 60.0)
    return mem


def phase1_score(
    *,
    content: float | None,
    speed: str | None,
    answers: list[float | None],
    successful: int,
    attempted: int,
    headrooms: list[float | None],
    tok_s: list[float | None],
) -> float | None:
    """Mix content with smaller speed/consistency/sustainability terms.

    Phase 2 credits an item only if it is correct *and* on time. Phase 1 follows
    that: Slow (or a failed answer) cannot be rescued by Fast tokens or unknown RAM.
    """
    if content is None:
        return None
    w = load_ruleset().get("phase1_weights") or {}
    raw = float(content)
    band = speed or "—"
    # Overtime: Phase 2 zeros the item. Phase 1 scales content. Slow (1.5× budget)
    # must land in the Not Recommended numeric band even if the answer was perfect.
    scales = load_ruleset().get("speed_content_scale") or {}
    if band == "Slow":
        raw = raw * float(scales.get("Slow") or 0.25)
    elif band == "OK":
        raw = raw * float(scales.get("OK") or 0.9)
    sp = speed_points(speed)
    if sp is None:
        sp = raw
    if raw < 62:
        sp = min(float(sp), raw)
    cons = consistency_score(answers, successful, attempted)
    if cons is None:
        cons = raw
    if raw < 62:
        cons = min(float(cons), raw)
    sust = sustainability_score(headrooms, tok_s)
    if raw < 62:
        sust = min(float(sust), raw)
    return (
        float(w.get("content") or 0.70) * raw
        + float(w.get("speed") or 0.15) * float(sp)
        + float(w.get("consistency") or 0.10) * float(cons)
        + float(w.get("sustainability") or 0.05) * float(sust)
    )


def quality(answer: float | None, speed: str | None) -> float | None:
    """Backward-compatible alias: content mixed with speed only."""
    if answer is None:
        return None
    pts = speed_points(speed)
    if pts is None:
        return float(answer)
    return (float(answer) + pts) / 2.0


def havalllmphase2_quality_total(category_pct: dict[str, float | None]) -> float | None:
    weights = load_ruleset().get("havalllmphase2_quality_weights") or {}
    used = {k: float(v) for k, v in weights.items() if category_pct.get(k) is not None}
    if not used:
        return None
    scale = 100.0 / sum(used.values())
    total = 0.0
    for key, pts in used.items():
        raw = float(category_pct[key])
        total += (raw / 100.0) * pts * scale
    return total


def persona_phase2_score(persona: str, category_pct: dict[str, float | None]) -> float | None:
    table = load_ruleset().get("persona_phase2") or {}
    weights = table.get(persona)
    if not weights:
        return havalllmphase2_quality_total(category_pct)
    total_w = 0.0
    acc = 0.0
    for key, w in weights.items():
        ww = float(w)
        if ww <= 0:
            continue
        val = category_pct.get(key)
        if val is None:
            continue
        total_w += ww
        acc += ww * float(val)
    if total_w <= 0:
        return havalllmphase2_quality_total(category_pct)
    return acc / total_w


def combine_phases(phase1: float | None, phase2: float | None) -> float | None:
    if phase1 is None and phase2 is None:
        return None
    if phase1 is None:
        return phase2
    if phase2 is None:
        return phase1
    w = load_ruleset().get("combine_weights") or {}
    a = float(w.get("phase1") or 0.50)
    b = float(w.get("phase2") or 0.50)
    return a * float(phase1) + b * float(phase2)


_CAT_NAMES = {
    "reasoning": "reasoning",
    "coding": "coding",
    "instructionFollowing": "following instructions",
    "structuredOutput": "structured answers",
    "math": "math",
}

_LABEL_ORDER = ("Excellent", "Strong", "Acceptable", "Marginal Match", "Not Recommended")


def critical_categories(*personas: str) -> list[str]:
    table = load_ruleset().get("persona_phase2") or {}
    thresh = float(load_ruleset().get("critical_weight") or 25)
    keys: list[str] = []
    for name in personas:
        weights = table.get(name) or {}
        for key, pts in weights.items():
            if float(pts) >= thresh and key not in keys:
                keys.append(key)
    return keys


def _numeric_label(score: float) -> str:
    cuts = load_ruleset()["labels"]
    if score < float(cuts["marginal"]):
        return "Not Recommended"
    if score < float(cuts["acceptable"]):
        return "Marginal Match"
    if score < float(cuts["strong"]):
        return "Acceptable"
    if score < float(cuts["excellent"]):
        return "Strong"
    return "Excellent"


def _role_pass_block(phase2_pct: dict[str, float | None] | None, personas: list[str] | None) -> str | None:
    """Spreadsheet floors: score must meet the Light-ask minimum. Floor 0 = skip."""
    if not phase2_pct or not personas:
        return None
    table = load_ruleset().get("persona_phase2_floors") or {}
    worst_key = None
    worst_gap = None
    for name in personas:
        role = table.get(name) or {}
        for key, need in role.items():
            bar = float(need or 0)
            if bar <= 0:
                continue
            val = phase2_pct.get(key)
            if val is None:
                continue
            if float(val) < bar:
                gap = bar - float(val)
                if worst_gap is None or gap > worst_gap:
                    worst_key = key
                    worst_gap = gap
    return worst_key


def _floors_block(
    label: str,
    phase2_pct: dict[str, float | None] | None,
    crit: list[str],
    personas: list[str] | None = None,
) -> str | None:
    role_miss = _role_pass_block(phase2_pct, personas)
    if role_miss:
        return role_miss
    floors = load_ruleset().get("label_floors") or {}
    need = floors.get(label)
    if need is None or not crit or not phase2_pct:
        return None
    bar = float(need)
    worst_key = None
    worst_val = None
    for key in crit:
        val = phase2_pct.get(key)
        if val is None:
            continue
        if float(val) < bar and (worst_val is None or float(val) < worst_val):
            worst_key = key
            worst_val = float(val)
    return worst_key


def _and_join(parts: list[str]) -> str:
    parts = [p for p in parts if p]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    if len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    return ", ".join(parts[:-1]) + ", and " + parts[-1]


def _speed_clause(speeds: list[str | None] | None, speed: str | None) -> str:
    vals = [s for s in (speeds or []) if s and s != "—"]
    if not vals and speed and speed != "—":
        vals = [speed]
    if not vals:
        return ""
    if all(s == "Fast" for s in vals):
        return "it responded fast"
    if all(s == "Slow" for s in vals):
        return "it finished slowly"
    if all(s in {"OK", "Slow"} for s in vals) and "OK" in vals:
        return "it finished, but was very slow"
    if all(s in {"Fast", "OK"} for s in vals):
        return "it finished, but was very slow on some asks"
    return "it finished in a mixed time"


def _quality_clause(content: float | None, phase1: float | None) -> str:
    val = content if content is not None else phase1
    if val is None:
        return ""
    if val >= 88:
        return "high-quality task answers"
    if val >= 75:
        return "good task answers"
    if val >= 62:
        return "usable task answers"
    return ""


def match_explain(
    label: str,
    *,
    phase2_pct: dict[str, float | None] | None = None,
    crit: list[str] | None = None,
    blocked_by: str | None = None,
    speeds: list[str | None] | None = None,
    speed: str | None = None,
    content: float | None = None,
    phase1: float | None = None,
    fail_why: str | None = None,
) -> str:
    if label == "Failed":
        return fail_why or "Failed because it did not finish any answers."
    if label == "Not Recommended" and _too_slow(speeds, speed) and not blocked_by:
        return "Not Recommended because it was too slow for this role's expected response time."
    speed_bit = _speed_clause(speeds, speed)
    quality_bit = _quality_clause(content, phase1)
    strong_skills = []
    floors = load_ruleset().get("label_floors") or {}
    bar = float(floors.get(label) or 62)
    for key in crit or []:
        val = (phase2_pct or {}).get(key)
        if val is not None and float(val) >= bar:
            strong_skills.append(_CAT_NAMES.get(key, key))
    lead = ""
    if speed_bit and quality_bit:
        lead = f"{speed_bit} with {quality_bit}"
    else:
        lead = speed_bit or quality_bit
    skill_bit = ""
    if strong_skills:
        skill_bit = f"including solid {_and_join(strong_skills)}"
    if label == "Not Recommended" and blocked_by:
        name = _CAT_NAMES.get(blocked_by, blocked_by)
        score = (phase2_pct or {}).get(blocked_by)
        scored = f" scored {int(round(float(score)))}" if score is not None else ""
        prefix = f"{lead[0].upper() + lead[1:]}. " if lead else ""
        return f"{prefix}Not Recommended because {name}{scored} is too weak for this role."
    if lead and skill_bit:
        because = f"{lead}, {skill_bit}"
    else:
        because = lead or skill_bit or "the combined Phase 1 and Phase 2 score"
    text = f"{label} because {because}."
    if blocked_by:
        name = _CAT_NAMES.get(blocked_by, blocked_by)
        text += f" {name[0].upper() + name[1:]} was too weak for a higher mark."
    elif label != "Excellent" and (content or 0) >= 88 and not strong_skills:
        text += " The capability pack held it below Excellent."
    return " ".join(text.split())


def _too_slow(speeds: list[str | None] | None, speed: str | None) -> bool:
    if speed == "Slow":
        return True
    return any(s == "Slow" for s in (speeds or []))


def evaluate_match(
    *,
    finish: float | None,
    answer: float | None,
    speed: str | None = None,
    personas: list[str] | None = None,
    phase2_pct: dict[str, float | None] | None = None,
    phase1: float | None = None,
    content: float | None = None,
    speeds: list[str | None] | None = None,
    fail_why: str | None = None,
) -> dict:
    if not finish:
        return {"label": "Failed", "why": match_explain("Failed", fail_why=fail_why), "blocked_by": None}
    if _too_slow(speeds, speed):
        return {
            "label": "Not Recommended",
            "why": match_explain(
                "Not Recommended",
                speeds=speeds,
                speed=speed,
                content=content,
                phase1=phase1,
            ),
            "blocked_by": None,
        }
    score = quality(answer, speed) if speed is not None else answer
    if score is None:
        return {"label": "Failed", "why": match_explain("Failed", fail_why=fail_why), "blocked_by": None}
    numeric = _numeric_label(float(score))
    crit = critical_categories(*(personas or []))
    start = _LABEL_ORDER.index(numeric)
    chosen = "Not Recommended"
    first_block = None
    for label in _LABEL_ORDER[start:]:
        if label == "Not Recommended":
            chosen = label
            break
        block = _floors_block(label, phase2_pct, crit, personas)
        if block:
            first_block = first_block or block
            continue
        chosen = label
        break
    blocked_by = first_block if chosen != numeric else None
    why = match_explain(
        chosen,
        phase2_pct=phase2_pct,
        crit=crit,
        blocked_by=blocked_by,
        speeds=speeds,
        speed=speed,
        content=content,
        phase1=phase1,
    )
    return {"label": chosen, "why": why, "blocked_by": blocked_by}


def match_label(
    *,
    finish: float | None,
    answer: float | None,
    speed: str | None = None,
    personas: list[str] | None = None,
    phase2_pct: dict[str, float | None] | None = None,
    phase1: float | None = None,
    content: float | None = None,
    speeds: list[str | None] | None = None,
) -> str:
    return evaluate_match(
        finish=finish,
        answer=answer,
        speed=speed,
        personas=personas,
        phase2_pct=phase2_pct,
        phase1=phase1,
        content=content,
        speeds=speeds,
    )["label"]


def persona_answer(light: float | None, balanced: float | None, heavy: float | None) -> float | None:
    return mean([light, balanced, heavy])


def persona_quality(
    light: float | None,
    balanced: float | None,
    heavy: float | None,
    light_speed: str | None = None,
    balanced_speed: str | None = None,
    heavy_speed: str | None = None,
) -> float | None:
    return mean(
        [
            quality(light, light_speed),
            quality(balanced, balanced_speed),
            quality(heavy, heavy_speed),
        ]
    )
