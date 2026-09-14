from __future__ import annotations

import html
import json
import re
from collections import defaultdict

from haval_engine.hardware import format_gb, gpu_card_copy, os_label
from haval_engine.models.params import parse_params
from haval_engine.pack import load_scenarios
from haval_engine.paths import config_dir
from haval_engine.scoring.fail_reason import customer_fail_line, summarize_failures
from haval_engine.scoring.pipeline import (
    combine_phases,
    evaluate_match,
    match_explain,
    mean,
    havalllmphase2_quality_total,
    persona_phase2_score,
    phase1_score,
    role_speed_band,
)

PERSONA_ORDER = [
    ("Consumer", "Everyday Organizer"),
    ("Consumer", "Student & Learner"),
    ("Consumer", "Family Coordinator"),
    ("Consumer", "Researcher & Shopper"),
    ("Consumer", "Writer & Communicator"),
    ("Consumer", "Creative Prosumer"),
    ("Consumer", "Personal Adviser"),
    ("Consumer", "Technical Hobbyist"),
    ("Gaming", "Casual Gamer"),
    ("Gaming", "Power Player"),
    ("Gaming", "Progressive Creator"),
    ("Gaming", "Rising Game Developer"),
    ("Commercial", "Executive & Decision Maker"),
    ("Commercial", "Project & Operations Manager"),
    ("Commercial", "Engineer & Software Developer"),
    ("Commercial", "Analyst & Finance Professional"),
    ("Commercial", "Research & Product Professional"),
    ("Commercial", "Sales & Marketing Professional"),
    ("Commercial", "Customer Support Specialist"),
    ("Commercial", "People, Legal & Compliance Professional"),
]

PERSONA_REF = [
    ("Consumer", "Everyday Organizer", "Schedules, reminders, notes, household tasks, and plans.", "Fast summaries, lists, rewriting, and clear next steps."),
    ("Consumer", "Student & Learner", "Studies, reviews material, practices problems, and prepares assignments.", "Tutoring, explanations, study guides, quizzes, and reasoning."),
    ("Consumer", "Family Coordinator", "Coordinates calendars, trips, meals, school activities, and purchases.", "Practical plans, organized lists, comparisons, and communication."),
    ("Consumer", "Researcher & Shopper", "Compares products, reviews specifications, and investigates options.", "Accurate comparisons, evidence summaries, and recommendation logic."),
    ("Consumer", "Writer & Communicator", "Writes emails, applications, documents, and social content.", "Drafting, tone adjustment, editing, and instruction following."),
    ("Consumer", "Creative Prosumer", "Creates stories, concepts, videos, presentations, and personal projects.", "Original ideas, refinement, consistency, and production help."),
    ("Consumer", "Personal Adviser", "Explores choices, routines, goals, travel, wellness, and life decisions.", "Balanced reasoning, options, personalization, and clear guidance."),
    ("Consumer", "Technical Hobbyist", "Experiments with PCs, scripts, electronics, and technical projects.", "Troubleshooting, code examples, explanations, and safe steps."),
    ("Gaming", "Casual Gamer", "Plays accessible games for relaxation and asks for occasional help.", "Quick tips, settings help, recommendations, and simple strategy."),
    ("Gaming", "Power Player", "Plays demanding games and optimizes performance, strategy, and builds.", "Deep analysis, configuration advice, and rapid high-volume help."),
    ("Gaming", "Progressive Creator", "Creates gaming videos, streams, clips, reviews, scripts, and posts.", "Concepts, content plans, scripts, titles, and audience adaptation."),
    ("Gaming", "Rising Game Developer", "Learns game creation and codes small games, prototypes, and mechanics.", "Beginner coding, debugging, design ideas, and runnable examples."),
    ("Commercial", "Executive & Decision Maker", "Reviews strategy, performance, risk, and business cases.", "Concise synthesis, scenarios, and defensible recommendations."),
    ("Commercial", "Project & Operations Manager", "Plans work, tracks owners, manages risks, and coordinates execution.", "Plans, status summaries, actions, risks, and structured artifacts."),
    ("Commercial", "Engineer & Software Developer", "Designs systems, writes code, reviews changes, and diagnoses defects.", "Correct code, debugging, architecture, tests, and documentation."),
    ("Commercial", "Analyst & Finance Professional", "Works with numbers, forecasts, performance data, and spreadsheets.", "Accurate math, interpretation, traceable assumptions, and tables."),
    ("Commercial", "Research & Product Professional", "Studies customers, markets, technologies, and requirements.", "Evidence synthesis, themes, requirements, and product insights."),
    ("Commercial", "Sales & Marketing Professional", "Builds campaigns, proposals, presentations, and sales content.", "Positioning, variants, personalization, and persuasive structure."),
    ("Commercial", "Customer Support Specialist", "Answers questions, diagnoses issues, and documents resolutions.", "Fast troubleshooting, accurate answers, empathy, and consistency."),
    ("Commercial", "People, Legal & Compliance Professional", "Reviews policies, obligations, controls, and careful documents.", "Precise extraction, cautious summaries, comparisons, and disclaimers."),
]


def _persona_scope(summary: dict) -> list[tuple[str, str]]:
    names = summary.get("personas")
    if not names:
        return list(PERSONA_ORDER)
    wanted = set(names)
    scoped = [(b, p) for b, p in PERSONA_ORDER if p in wanted]
    return scoped or list(PERSONA_ORDER)


def dash(value, kind: str = "num") -> str:
    if value is None:
        return "—"
    if kind == "int":
        return str(int(round(float(value))))
    if kind == "1":
        return f"{float(value):.1f}"
    if kind == "tok":
        return f"{float(value):.1f} tok/s"
    if kind == "sec":
        return f"{float(value):.1f} sec"
    if kind == "mmss":
        total = int(round(float(value)))
        return f"{total // 60}:{total % 60:02d}"
    return str(value)


def status_class(label: str) -> str:
    table = {
        "Excellent": "excellent",
        "Strong": "strong",
        "OK": "acceptable",
        "Acceptable": "acceptable",
        "Acceptable Match": "acceptable",
        "Marginal Match": "marginal",
        "Not recommended": "no",
        "Not Recommended": "no",
        "Failed": "failed",
    }
    return table.get(label, "failed")


def _catalog() -> list[dict]:
    path = config_dir() / "preferred-models.json"
    if not path.exists():
        return []
    return list(json.loads(path.read_text(encoding="utf-8")).get("models") or [])


def _param_b(label: str) -> str:
    text = (label or "").strip()
    if not text or text == "—":
        return ""
    try:
        n = float(text.upper().rstrip("B"))
    except ValueError:
        return text
    if abs(n - round(n)) < 0.05:
        return f"{int(round(n))}B"
    return f"{n:g}B"


def _pretty_model_name(raw: str, ident: dict) -> str:
    display = str(ident.get("display") or raw or "").strip()
    display = re.sub(r":[\w.\-]+$", "", display)
    m = re.match(r"^(llama)\s*([0-9.]+)", display, re.I)
    if m:
        return f"Llama {m.group(2)}"
    m = re.match(r"^(gemma)\s*([0-9.]+)", display, re.I)
    if m:
        return f"Gemma {m.group(2)}"
    if display.lower().startswith("llama") and not display.lower().startswith("llama "):
        rest = display[5:]
        return ("Llama " + rest).strip()
    return display or raw


def _headline(ident: dict, raw_name: str) -> tuple[str, str]:
    pretty = _pretty_model_name(raw_name, ident)
    total = _param_b(str(ident.get("total") or ""))
    active = _param_b(str(ident.get("active") or ""))
    pe = html.escape(pretty)
    te = html.escape(total) if total else ""
    ae = html.escape(active) if active else ""
    if total and active:
        plain = f"How this PC performed on {pretty} with {total} and {active} active parameters"
        marked = (
            f"How this PC performed on <em>{pe}</em> with <em>{te}</em> "
            f"and <em>{ae}</em> active parameters"
        )
    elif total:
        plain = f"How this PC performed on {pretty} with {total}"
        marked = f"How this PC performed on <em>{pe}</em> with <em>{te}</em>"
    else:
        plain = f"How this PC performed on {pretty}"
        marked = f"How this PC performed on <em>{pe}</em>"
    return plain, marked


def headline_for_run(run: dict | None) -> str:
    """Same plain headline as the HTML report, for lists in the app."""
    if not run:
        return "How this PC performed"
    try:
        summary = json.loads(run.get("summary_json") or "{}")
    except json.JSONDecodeError:
        summary = {}
    if summary.get("kind") == "comparison":
        models = summary.get("models") or []
        n = len(models) if isinstance(models, list) else 0
        return str(summary.get("headline") or f"Comparison · {n} models")
    try:
        models = json.loads(run.get("models_json") or "[]")
    except json.JSONDecodeError:
        models = []
    raw = str((models or [""])[0] or "").strip()
    if not raw:
        return "How this PC performed"
    ident = _identity(raw)
    plain, _ = _headline(ident, raw)
    return plain


_FIT_CLASSES = {"excellent", "strong", "acceptable"}
_LABEL_ORDER = ("Excellent", "Strong", "Acceptable", "Marginal Match", "Not Recommended", "Failed")


def _empty_mix() -> dict:
    return {
        "roles": 0,
        "fit_pct": 0,
        "not_pct": 0,
        "fit_n": 0,
        "not_n": 0,
        "summary": "",
        "detail": "",
        "bars": [],
    }


def _role_mix(persona_table: list[dict], business: str) -> dict:
    rows = [p for p in persona_table if p.get("business") == business]
    total = len(rows)
    if not total:
        return _empty_mix()
    fit_n = sum(1 for p in rows if p.get("final_class") in _FIT_CLASSES)
    not_n = total - fit_n
    fit_pct = int(round(100 * fit_n / total))
    not_pct = 100 - fit_pct
    counts: dict[str, int] = {}
    for row in rows:
        lab = row.get("final") or "Failed"
        counts[lab] = counts.get(lab, 0) + 1
    bars = []
    bits = []
    for lab in _LABEL_ORDER:
        n = counts.get(lab, 0)
        if n <= 0:
            continue
        pct = int(round(100 * n / total))
        if pct < 1:
            pct = 1
        bits.append(f"{n} {lab}")
        bars.append({"label": lab, "pct": pct, "cls": status_class(lab), "why": match_explain(lab)})
    for lab, n in counts.items():
        if lab not in _LABEL_ORDER and n > 0:
            pct = max(1, int(round(100 * n / total)))
            bits.append(f"{n} {lab}")
            bars.append({"label": lab, "pct": pct, "cls": status_class(lab), "why": match_explain(lab)})
    return {
        "roles": total,
        "fit_n": fit_n,
        "not_n": not_n,
        "fit_pct": fit_pct,
        "not_pct": not_pct,
        "summary": "",
        "detail": " · ".join(bits),
        "bars": bars,
    }


def _identity(name: str) -> dict:
    parsed = parse_params(name)
    display = name.split("/")[-1]
    tag = ""
    quant = "—"
    bytes_hint = "—"
    order = 99
    catalog_params = ""
    for row in _catalog():
        pull = str(row.get("pull") or "")
        if name == pull or name.startswith(pull) or pull in name or name == row.get("id"):
            catalog_params = str(row.get("params") or "")
            parsed = parse_params(catalog_params, name, row.get("tag"), row.get("display_name"))
            display = row.get("display_name") or display
            tag = row.get("tag") or tag
            quant = row.get("quant") or quant
            bytes_hint = row.get("size_hint") or bytes_hint
            order = int(row.get("roster_order") or 99)
            break
    else:
        parsed = parse_params(name)
    moe = parsed["moe"] or "-A" in catalog_params.upper() or "MoE" in catalog_params
    return {
        "display": display,
        "tag": tag,
        "arch": "MoE" if moe else "Dense",
        "total": parsed["total"],
        "active": parsed["active"],
        "quant": quant,
        "bytes": bytes_hint,
        "order": order,
    }


def _intensity_time(row: dict, attempts: list[dict], model: str) -> str:
    if not row:
        return "—"
    atts = _attempt_rows(attempts, model, row.get("scenario_id") or "")
    vals = [a.get("total_s") for a in atts if a.get("ok") and a.get("total_s") is not None]
    avg = mean(vals)
    return dash(avg, "mmss") if avg is not None else "—"


def _attempt_rows(attempts: list[dict], model: str, scenario_id: str) -> list[dict]:
    return [a for a in attempts if a.get("model") == model and a.get("scenario_id") == scenario_id]


def _phase1_for(row: dict, attempts: list[dict], model: str, speed: str | None = None) -> float | None:
    atts = _attempt_rows(attempts, model, row.get("scenario_id") or "")
    content = row.get("q")
    if row.get("w") is not None and not atts:
        return float(row["w"])
    answers = [a.get("q") for a in atts] if atts else ([content] * int(row.get("successful") or 0))
    successful = int(row.get("successful") or 0)
    attempted = int(row.get("attempted") or 1)
    heads = [a.get("e") for a in atts] if atts else ([row.get("e")] if row.get("e") is not None else [])
    toks = [a.get("tok_s") for a in atts] if atts else []
    return phase1_score(
        content=content,
        speed=speed if speed and speed != "—" else row.get("internal"),
        answers=answers,
        successful=successful,
        attempted=attempted,
        headrooms=heads,
        tok_s=toks,
    )


def _ask_actual_s(row: dict, attempts: list[dict], model: str) -> float | None:
    if not row:
        return None
    atts = _attempt_rows(attempts, model, row.get("scenario_id") or "")
    vals = [a.get("total_s") for a in atts if a.get("ok") and a.get("total_s") is not None]
    return mean(vals)


def _role_speed(slot: dict, attempts: list[dict], model: str, pack: dict) -> str:
    actuals: list[float | None] = []
    expecteds: list[float | None] = []
    heavy_actual = None
    for intensity in ("Light", "Balanced", "Heavy"):
        row = slot.get(intensity) or {}
        if not row:
            continue
        sc = pack.get(row.get("scenario_id") or "") or {}
        exp = float(sc.get("total_s") or 0) or None
        act = _ask_actual_s(row, attempts, model)
        if act is not None and exp:
            actuals.append(act)
            expecteds.append(exp)
        if intensity == "Heavy":
            heavy_actual = act
    band = role_speed_band(actuals, expecteds, heavy_actual)
    if band != "—":
        return band
    bands = []
    for intensity in ("Light", "Balanced", "Heavy"):
        row = slot.get(intensity) or {}
        if row.get("internal"):
            bands.append(str(row.get("internal")))
    if bands and all(b == "Slow" for b in bands):
        return "Slow"
    if any(b == "Fast" for b in bands):
        return "Fast"
    if any(b == "OK" for b in bands):
        return "OK"
    return "—"


def build_context(run: dict, scores: list[dict], attempts: list[dict], hardware: dict) -> dict:
    pack = {s["id"]: s for s in load_scenarios()}
    models_order = json.loads(run.get("models_json") or "[]")
    try:
        summary = json.loads(run.get("summary_json") or "{}")
    except json.JSONDecodeError:
        summary = {}
    by_model_scores: dict[str, list[dict]] = defaultdict(list)
    for row in scores:
        sc = pack.get(row["scenario_id"]) or {}
        enriched = dict(row)
        enriched["persona"] = sc.get("persona")
        enriched["business"] = sc.get("business")
        enriched["intensity"] = sc.get("intensity")
        by_model_scores[row["model"]].append(enriched)
    by_model_attempts: dict[str, list[dict]] = defaultdict(list)
    for row in attempts:
        by_model_attempts[row["model"]].append(row)

    model_views = []
    for name in models_order:
        ident = _identity(name)
        rows = by_model_scores.get(name) or []
        atts = by_model_attempts.get(name) or []
        by_persona: dict[str, dict] = defaultdict(dict)
        meta: dict[str, str] = {}
        for row in rows:
            if row.get("persona"):
                by_persona[row["persona"]][row["intensity"]] = row
                meta[row["persona"]] = row.get("business") or ""
        roll = next((m for m in (summary.get("models") or []) if m.get("model") == name), {})
        fail = roll.get("fail") if isinstance(roll.get("fail"), dict) else None
        if not fail:
            fail = summarize_failures(atts, thinking=bool(summary.get("thinking")))
        too_slow = bool(fail and fail.get("kind") == "too_slow")
        failed_all = too_slow or not rows or all((r.get("successful") or 0) == 0 for r in rows)
        if failed_all and not fail:
            fail = summarize_failures(atts, thinking=bool(summary.get("thinking")))
        fail_why = customer_fail_line(fail) if fail else None
        phase2 = roll.get("phase2") or {}
        p2_pct = phase2.get("pct") or {}
        p2_total = phase2.get("total")
        if p2_total is None and p2_pct:
            p2_total = havalllmphase2_quality_total(p2_pct)
        scope = _persona_scope(summary)
        shown_biz = list(dict.fromkeys(b for b, _ in scope))
        persona_table = []
        for biz, persona in scope:
            slot = by_persona.get(persona) or {}
            light = slot.get("Light") or {}
            bal = slot.get("Balanced") or {}
            heavy = slot.get("Heavy") or {}
            role_speed = _role_speed(slot, atts, name, pack)
            p1_vals = [
                _phase1_for(light, atts, name, role_speed) if light else None,
                _phase1_for(bal, atts, name, role_speed) if bal else None,
                _phase1_for(heavy, atts, name, role_speed) if heavy else None,
            ]
            p1 = mean(p1_vals)
            finishes = [light.get("r"), bal.get("r"), heavy.get("r")]
            finish = mean(finishes)
            p2 = persona_phase2_score(persona, p2_pct) if p2_pct else None
            overall = combine_phases(p1, p2)
            contents = mean(
                [
                    light.get("q") if light else None,
                    bal.get("q") if bal else None,
                    heavy.get("q") if heavy else None,
                ]
            )
            verdict = evaluate_match(
                finish=finish,
                answer=overall,
                personas=[persona],
                phase2_pct=p2_pct or None,
                phase1=p1,
                content=contents,
                speeds=[role_speed],
                fail_why=fail_why,
            )
            final = verdict["label"]
            persona_table.append(
                {
                    "business": biz,
                    "persona": persona,
                    "bizclass": biz.lower(),
                    "light": _intensity_time(light, atts, name),
                    "balanced": _intensity_time(bal, atts, name),
                    "heavy": _intensity_time(heavy, atts, name),
                    "phase1": dash(p1, "int"),
                    "phase2": dash(p2, "int"),
                    "overall": dash(overall, "int"),
                    "final": final,
                    "final_class": status_class(final),
                    "why": verdict["why"],
                    "role_speed": role_speed,
                }
            )
        businesses: dict[str, list[float]] = defaultdict(list)
        for row in persona_table:
            if row["overall"] != "—":
                businesses[row["business"]].append(float(row["overall"]))
        biz_scores = {
            b: (sum(businesses[b]) / len(businesses[b]) if businesses.get(b) else None)
            for b in shown_biz
        }
        biz_labels = {}
        for b in ("Consumer", "Gaming", "Commercial"):
            if b not in shown_biz:
                biz_labels[b] = {
                    "score": None,
                    "customer": "—",
                    "cls": "failed",
                    "why": "This business was not part of this run.",
                    "skipped": True,
                    "fit_pct": 0,
                    "not_pct": 0,
                    "summary": "",
                    "detail": "",
                    "bars": [],
                    "roles": 0,
                }
                continue
            val = biz_scores.get(b)
            names = [p for biz, p in scope if biz == b]
            contents = mean(
                [row.get("q") for row in rows if (pack.get(row.get("scenario_id") or "") or {}).get("business") == b]
            )
            speeds = [
                prow.get("role_speed")
                for prow in persona_table
                if prow.get("business") == b
            ]
            verdict = evaluate_match(
                finish=100.0 if val is not None else 0.0,
                answer=val,
                personas=names,
                phase2_pct=p2_pct or None,
                content=contents,
                speeds=speeds,
                fail_why=fail_why,
            )
            lab = verdict["label"]
            mix = _role_mix(persona_table, b)
            biz_labels[b] = {
                "score": val,
                "customer": lab,
                "cls": status_class(lab),
                "why": verdict["why"],
                **mix,
            }
        q = mean([_phase1_for(r, atts, name, _role_speed(by_persona.get(r.get("persona") or "") or {}, atts, name, pack)) for r in rows])
        r = mean([r.get("r") for r in rows])
        combined = combine_phases(q, p2_total)
        tok = mean([a.get("tok_s") for a in atts if a.get("ok")])
        ttft = mean([a.get("ttft_s") for a in atts if a.get("ok")])
        task = mean([a.get("total_s") for a in atts if a.get("ok")])
        customer_v = evaluate_match(
            finish=0.0 if failed_all else (r or 0),
            answer=None if failed_all else combined,
            personas=[p for _, p in scope],
            phase2_pct=p2_pct or None,
            phase1=q,
            content=mean([row.get("q") for row in rows]),
            speeds=[prow.get("role_speed") for prow in persona_table],
            fail_why=fail_why,
        )
        customer = customer_v["label"]
        p2_rows = []
        labels = {
            "reasoning": "Reasoning",
            "coding": "Coding",
            "instructionFollowing": "Instruction following",
            "structuredOutput": "Structured output",
            "math": "Math",
        }
        for key, label in labels.items():
            cat = (phase2.get("categories") or {}).get(key) or {}
            p2_rows.append(
                {
                    "name": label,
                    "correct": cat.get("correct", "—"),
                    "total": cat.get("total", "—"),
                    "pct": dash(p2_pct.get(key), "int") if p2_pct.get(key) is not None else "—",
                }
            )
        model_views.append(
            {
                "name": name,
                "display": f"{ident['display']} {ident['tag']}".strip(),
                "ident": ident,
                "failed": failed_all,
                "fail_kind": (fail or {}).get("kind") if failed_all else None,
                "fail_reason": customer_fail_line(fail) if failed_all else None,
                "Q": combined,
                "R": r,
                "Qd": dash(combined, "int"),
                "Rd": dash(r, "int"),
                "p1d": dash(q, "int"),
                "p2d": dash(p2_total, "int"),
                "hardware_note": roll.get("hardware_note") or "—",
                "tok": dash(tok, "tok") if tok is not None else "—",
                "ttft": dash(ttft, "sec") if ttft is not None else "—",
                "task": dash(task, "mmss") if task is not None else "—",
                "task_s": dash(task, "1") if task is not None else "—",
                "suitability": customer,
                "suit_class": status_class(customer),
                "suit_why": customer_v["why"],
                "businesses": biz_labels,
                "personas": persona_table,
                "phase2_rows": p2_rows,
                "phase2_excluded": ", ".join(phase2.get("excluded") or ["multilingual", "sensitivity"]),
                "use": "—" if failed_all else "Final = 50% Phase 1 + 50% Phase 2. Role time uses the average of Light, Balanced, and Heavy. Over 2× that average expected time is Not Recommended, not Failed.",
            }
        )
    model_views.sort(key=lambda m: _identity(m["name"])["order"])

    def winner(business: str) -> dict:
        one = model_views[0] if len(model_views) == 1 else None
        if one and one["businesses"][business].get("skipped"):
            return {
                "display": "—",
                "why": "This business was not part of this run.",
                "pill": "—",
                "cls": "failed",
                "tip": "This business was not part of this run.",
                "skipped": True,
                "fit_pct": 0,
                "not_pct": 0,
                "summary": "",
                "detail": "",
                "bars": [],
                "roles": 0,
            }
        if one:
            biz = one["businesses"][business]
            return {
                "display": one["display"],
                "why": f"{business} match for this model on this hardware. It is not a ranking against other models.",
                "pill": biz.get("customer") or "Failed",
                "cls": biz.get("cls") or "failed",
                "tip": biz.get("why") or "",
                "fit_pct": biz.get("fit_pct", 0),
                "not_pct": biz.get("not_pct", 0),
                "summary": biz.get("summary") or "",
                "detail": biz.get("detail") or "",
                "bars": biz.get("bars") or [],
                "roles": biz.get("roles") or 0,
            }
        qualified = [m for m in model_views if not m["failed"] and m["businesses"][business]["score"] is not None]
        if not qualified:
            return {
                "display": "—",
                "why": "No gradeable score for this business on this run.",
                "pill": "Failed",
                "cls": "failed",
                "tip": (one.get("fail_reason") if one else None) or "Failed because it did not finish any answers.",
                "fit_pct": 0,
                "not_pct": 100,
                "summary": "",
                "detail": "",
                "bars": [],
                "roles": 0,
            }
        best = max(qualified, key=lambda m: m["businesses"][business]["score"])
        biz = best["businesses"][business]
        return {
            "display": best["display"],
            "why": f"Highest {business} score among completed models on this hardware.",
            "pill": biz["customer"],
            "cls": biz["cls"],
            "tip": biz.get("why") or "",
            "fit_pct": biz.get("fit_pct", 0),
            "not_pct": biz.get("not_pct", 0),
            "summary": biz.get("summary") or "",
            "detail": biz.get("detail") or "",
            "bars": biz.get("bars") or [],
            "roles": biz.get("roles") or 0,
        }

    hw = hardware or {}
    incomplete = (run.get("status") or "") != "completed"
    subject = model_views[0]["display"] if model_views else "—"
    one = len(model_views) == 1
    think_label = "thinking on" if summary.get("thinking") else "thinking off"
    scope = _persona_scope(summary)
    shown_biz = list(dict.fromkeys(b for b, _ in scope))
    ref = [row for row in PERSONA_REF if any(row[1] == p for _, p in scope)]
    notice = (
        "Incomplete measured run · missing cells are em dashes, not estimates."
        if incomplete
        else f"Measured benchmark · {think_label} · every number traces to the run store."
    )
    host = hw.get("computer_name") or hw.get("product") or "This PC"
    ident0 = model_views[0]["ident"] if model_views else {"total": "—", "active": "—", "display": subject}
    raw0 = model_views[0]["name"] if model_views else ""
    if model_views:
        headline, headline_html = _headline(ident0, raw0)
    else:
        headline, headline_html = "How this PC performed", "How this PC performed"
    card = gpu_card_copy(hw.get("nvidia_smi"), str(hw.get("gpu_title") or hw.get("gpu") or ""))
    gpu_title = card.get("title") or hw.get("gpu") or "—"
    gpu_vram_label = card.get("vram_label") or (format_gb(hw.get("vram_gb")) if hw.get("vram_gb") else "")
    unified = bool(hw.get("unified_memory")) if "unified_memory" in hw else not hw.get("vram_gb")
    if hw.get("ram_gb") is not None:
        ram_n = float(hw["ram_gb"])
        ram_value = f"{int(round(ram_n))} GB" if abs(ram_n - round(ram_n)) < 0.05 else f"{ram_n:.1f} GB"
    else:
        ram_value = "—"
    mem_kind = "Unified memory" if unified else "System memory"
    return {
        "run_id": run.get("id"),
        "status": run.get("status"),
        "incomplete": incomplete,
        "measured": True,
        "think_off": not bool(summary.get("thinking")),
        "thinking": bool(summary.get("thinking")),
        "one_model": one,
        "subject": subject,
        "headline": headline,
        "headline_html": headline_html,
        "model_pretty": _pretty_model_name(raw0, ident0) if model_views else subject,
        "notice": notice,
        "product": host,
        "os_label": hw.get("os_label") or os_label(),
        "cpu": hw.get("cpu") or "—",
        "gpu": gpu_title,
        "gpu_vram_label": gpu_vram_label,
        "unified_memory": unified,
        "ram": ram_value,
        "mem_value": ram_value,
        "mem_kind": mem_kind,
        "vram_value": gpu_vram_label or None,
        "form": hw.get("nvidia_smi") or gpu_title,
        "models": model_views,
        "model_count": len(model_views),
        "winners": {"Consumer": winner("Consumer"), "Gaming": winner("Gaming"), "Commercial": winner("Commercial")},
        "businesses_shown": shown_biz,
        "persona_ref": ref,
        "persona_count": len(scope),
        "suit_class": model_views[0]["suit_class"] if model_views else "failed",
    }
