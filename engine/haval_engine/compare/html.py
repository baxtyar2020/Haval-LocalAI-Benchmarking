from __future__ import annotations

import html as html_lib
from dataclasses import dataclass

from haval_engine.compare.models import CAP_ORDER, MODEL_COLORS, MeasuredRun
from haval_engine.compare.parse import avg_task_seconds, estimate_task_seconds, format_mmss
from haval_engine.report.context import PERSONA_ORDER


def _e(text: object) -> str:
    return html_lib.escape(str(text if text is not None else ""), quote=True)


def _short(name: str) -> str:
    return name.replace(":latest", "").strip()


def _fmt_b(n: float | None) -> str:
    if n is None:
        return ""
    if abs(n - round(n)) < 0.05:
        return f"{int(round(n))}B"
    return f"{n:g}B"


def _cap(col: MeasuredRun, name: str) -> int | None:
    return col.capabilities.get(name)


def _ttft(col: MeasuredRun) -> float:
    return col.ttft_s if col.ttft_s is not None else 1e9


@dataclass
class Winners:
    overall: MeasuredRun | None
    everyday: MeasuredRun | None
    coder: MeasuredRun | None
    coder_title: str
    unusable: MeasuredRun | None


def pick_winners(cols: list[MeasuredRun]) -> Winners:
    def better_overall(a: MeasuredRun, b: MeasuredRun) -> MeasuredRun:
        af, bf = a.final or -1, b.final or -1
        if af != bf:
            return a if af > bf else b
        ap, bp = a.phase2 or -1, b.phase2 or -1
        if ap != bp:
            return a if ap > bp else b
        return a if (a.tok_s or 0) >= (b.tok_s or 0) else b

    def skill(c: MeasuredRun) -> tuple[int, int, int, int]:
        return (
            _cap(c, "Coding") or -1,
            _cap(c, "Reasoning") or -1,
            c.phase2 or -1,
            c.final or -1,
        )

    overall = cols[0]
    for c in cols[1:]:
        overall = better_overall(overall, c)

    everyday = None
    pool = [c for c in cols if (c.final or 0) >= 85 and (_cap(c, "Instruction following") or 0) >= 80]
    if not pool:
        pool = [c for c in cols if (c.final or 0) >= 85]
    if pool:
        everyday = min(pool, key=_ttft)

    coder = cols[0]
    for c in cols[1:]:
        if skill(c) > skill(coder):
            coder = c
    coder_title = "Best for code and reasoning"

    unusable = None
    bad = []
    for c in cols:
        floor_fail = (_cap(c, "Math") or 100) < 20 or (_cap(c, "Reasoning") or 100) < 40
        if (c.final or 100) < 75 or floor_fail:
            bad.append(c)
    if bad:
        unusable = min(bad, key=_ttft)

    return Winners(overall=overall, everyday=everyday, coder=coder, coder_title=coder_title, unusable=unusable)


_ICONS: dict[str, str] = {
    "Everyday Organizer": "M8 7h8M8 12h8M8 17h5M6 4h12a2 2 0 0 1 2 2v14l-4-2-4 2-4-2-4 2V6a2 2 0 0 1 2-2z",
    "Student & Learner": "M4 19V7l8-4 8 4v12M4 11l8 4 8-4",
    "Family Coordinator": "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75",
    "Researcher & Shopper": "M11 19a8 8 0 1 0 0-16 8 8 0 0 0 0 16zM21 21l-4.3-4.3",
    "Writer & Communicator": "M12 20h9M16.5 3.5a2.1 2.1 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z",
    "Creative Prosumer": "M12 3l2.2 6.6H21l-5.4 4 2.1 6.4L12 16.8 6.3 20l2.1-6.4L3 9.6h6.8L12 3z",
    "Personal Adviser": "M12 2v4M12 18v4M4.9 4.9l2.8 2.8M16.3 16.3l2.8 2.8M2 12h4M18 12h4M4.9 19.1l2.8-2.8M16.3 7.7l2.8-2.8",
    "Technical Hobbyist": "M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z",
    "Casual Gamer": "M6 12h4M8 10v4M15 13h.01M18 11h.01M6 8h12a4 4 0 0 1 0 8H6a4 4 0 0 1 0-8z",
    "Power Player": "M13 2L3 14h8l-1 8 10-12h-8l1-8z",
    "Progressive Creator": "M23 7l-7 5 7 5V7zM3 5h11v14H3z",
    "Rising Game Developer": "M16 18l6-6-6-6M8 6l-6 6 6 6",
    "Executive & Decision Maker": "M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M4 7h16l-1 12H5L4 7z",
    "Project & Operations Manager": "M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01",
    "Engineer & Software Developer": "M4 6h16v12H4zM8 6v12M4 10h16",
    "Analyst & Finance Professional": "M3 3v18h18M7 14l4-4 4 4 5-6",
    "Research & Product Professional": "M9 3h6l1 7a4 4 0 1 1-8 0L9 3zM8 21h8",
    "Sales & Marketing Professional": "M3 11l19-8-8 19-2.5-6.5L3 11z",
    "Customer Support Specialist": "M3 18v-5a9 9 0 1 1 18 0v5M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z",
    "People, Legal & Compliance Professional": "M12 3l8 4v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z",
    "People, Legal & Compliance": "M12 3l8 4v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z",
}


def _icon_svg(persona: str) -> str:
    d = _ICONS.get(persona) or "M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2M9 7a4 4 0 1 0 0-8 4 4 0 0 0 0 8"
    return (
        f'<svg class="role-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>'
    )


def build_comparison_html(columns: list[MeasuredRun], source_count: int) -> str:
    cols = columns[:5]
    colors = {id(c): MODEL_COLORS[i] for i, c in enumerate(cols)}
    wins = pick_winners(cols)
    machines = sorted({c.machine for c in cols if c.machine})
    mixed = len(machines) > 1
    think_off = any(c.thinking is False for c in cols) and not any(c.thinking is True for c in cols)
    hw = cols[0]
    chips = []
    if not mixed and hw.machine:
        chips.append(hw.machine)
    elif mixed:
        chips.extend(machines)
    if hw.gpu:
        chips.append(f"{hw.gpu}" + (f" · {hw.vram}" if hw.vram else ""))
    if hw.cpu:
        short_cpu = hw.cpu if len(hw.cpu) < 42 else hw.cpu[:40] + "…"
        chips.append(short_cpu)
    if hw.ram:
        chips.append(hw.ram)
    if think_off:
        chips.append("Thinking off")

    everyday = wins.everyday
    overall = wins.overall
    orange_word = "Fit"
    title = "Size is not the winner. Fit is."
    lead = _lead(wins, cols)
    verdict_h, verdict_p = _verdict(wins, cols)

    legend = "".join(
        f'<span class="leg"><i style="background:{colors[id(c)]}"></i>{_e(_short(c.model_name))}</span>'
        for c in cols
    )
    chip_html = "".join(f'<span class="chip">{_e(x)}</span>' for x in chips)
    if mixed:
        chip_html = '<span class="chip warn">Mixed hardware</span>' + chip_html

    winner_cards = _winner_cards(wins, colors)
    scoreboard = _scoreboard(cols, colors, everyday)
    caps = _capabilities(cols, colors)
    anatomy = _anatomy(cols, colors)
    time_ranks = _time_rank_cards(cols, colors)
    times = _time_table(cols, colors)
    quality_ranks = _quality_rank_cards(cols, colors)
    uses = _use_cases(wins, colors)

    hw_note = "Mixed hardware" if mixed else "Same hardware throughout"
    n = source_count

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Haval LocalAI · LLM size comparison on one PC</title>
<style>
:root{{
  --paper:#f4efe6; --paper2:#ece3d6; --ink:#1c1b19; --muted:#6a635b;
  --line:#d8cbb8; --orange:#dc4d18; --orange2:#ae3812; --soft:#f6ddcf;
  --green:#2f774b; --greenSoft:#dcebdd; --blue:#39748b; --gold:#a8731f;
  --red:#a74733; --violet:#745486; --shadow:0 18px 50px rgba(58,39,20,.08);
}}
*{{box-sizing:border-box}}
html,body{{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 Inter,ui-sans-serif,system-ui,sans-serif}}
body{{min-height:100vh;background:radial-gradient(900px 480px at 100% -10%, rgba(220,77,24,.12), transparent 55%), var(--paper)}}
.wrap{{max-width:1180px;margin:0 auto;padding:28px 28px 72px}}
.top{{display:flex;justify-content:space-between;gap:18px;align-items:flex-start;flex-wrap:wrap;margin-bottom:28px}}
.brand{{display:flex;gap:12px;align-items:center}}
.mark{{width:40px;height:40px;border-radius:11px;background:var(--orange);color:var(--paper);display:grid;place-items:center;font:700 14px/1 Inter,sans-serif}}
.brand b{{display:block;font:600 15px/1.2 Inter,sans-serif}}
.brand em{{display:block;font-style:normal;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}}
.chips{{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}}
.chip{{border:1px solid var(--line);background:#fffaf3;border-radius:999px;padding:6px 12px;font-size:12.5px}}
.chip.warn{{background:var(--soft);border-color:#e8b9a0}}
.kicker{{font-size:11px;font-weight:850;letter-spacing:.16em;text-transform:uppercase;color:var(--orange2);margin-bottom:10px}}
h1{{font:normal 42px/1.12 Georgia,serif;margin:0 0 12px;letter-spacing:-.02em}}
h1 span{{color:var(--orange)}}
.lead{{max-width:720px;margin:0 0 18px;color:var(--ink);font-size:17px}}
.legs{{display:flex;flex-wrap:wrap;gap:10px 16px;margin:0 0 18px}}
.leg{{display:flex;align-items:center;gap:7px;font-size:13px}}
.leg i{{width:10px;height:10px;border-radius:3px;display:inline-block}}
.verdict{{background:#1c1b19;color:#f4efe6;border-radius:22px;padding:22px 24px;box-shadow:var(--shadow)}}
.verdict h2{{font:normal 26px/1.25 Georgia,serif;margin:0 0 8px}}
.verdict p{{margin:0;color:#d9d0c4;font-size:15px}}
.sec{{margin-top:42px}}
.sec h3{{font:normal 26px/1.2 Georgia,serif;margin:6px 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:14px}}
.card{{background:#fffaf3;border:1px solid var(--line);border-radius:22px;padding:18px 18px 16px;box-shadow:var(--shadow)}}
.card h4{{margin:0 0 8px;font:600 15px/1.3 Inter,sans-serif}}
.card p{{margin:0;font-size:13.5px;color:var(--muted)}}
.axis{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--orange2);margin-bottom:6px}}
table{{width:100%;border-collapse:collapse}}
th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid var(--line);font-size:13.5px}}
th{{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:650}}
th.task-est{{white-space:normal;max-width:11em;letter-spacing:.04em;line-height:1.25}}
td.num{{font-variant-numeric:tabular-nums}}
tr.best td{{background:var(--greenSoft)}}
.scroll{{overflow-x:auto}}
.cap-block{{margin:0 0 22px}}
.cap-block .name{{font:600 14px/1.3 Inter,sans-serif;margin:0 0 8px}}
.bar-row{{display:grid;grid-template-columns:140px 1fr;gap:10px;align-items:center;margin:6px 0}}
.bar-row label{{font-size:12.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.track{{height:22px;border-radius:999px;background:var(--paper2);overflow:hidden}}
.fill{{height:100%;border-radius:999px;color:#fff;font:700 11px/22px Inter,sans-serif;padding:0 8px;min-width:8%}}
.anatomy{{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px}}
.split{{height:14px;border-radius:999px;overflow:hidden;display:flex;background:var(--paper2)}}
.split .w{{background:#a74733}}
.split .g{{background:#2f774b}}
.anatomy .cap{{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-top:8px}}
.time-sub{{margin:0 0 12px;color:var(--muted)}}
.time-sub b{{color:var(--orange);font-weight:650}}
.time-ranks{{display:flex;flex-wrap:nowrap;align-items:stretch;gap:10px;margin:0 0 18px}}
.time-ranks>.time-rank{{flex:1 1 0;min-width:0;padding:14px 12px 12px}}
.time-rank-head{{font:800 15px/1.2 Inter,sans-serif;letter-spacing:.04em;text-transform:uppercase;color:var(--ink);margin:0 0 8px;overflow-wrap:anywhere}}
.time-rank h4{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.time-rank p.time-rank-val{{font:700 28px/1 Georgia,serif;margin:8px 0 0;letter-spacing:-.02em;color:var(--ink)}}
.quality-rank h4{{font:700 16px/1.25 Inter,sans-serif;margin:0;white-space:normal;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical}}
.quality-rank.weak .time-rank-head{{color:var(--red)}}
.role{{display:flex;align-items:center;gap:10px}}
.role-ico{{width:30px;height:30px;padding:5px;border-radius:8px;background:#f3ebe0;color:var(--orange2);flex:none}}
.center{{text-align:center}}
.dash{{color:var(--muted)}}
.use{{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px}}
.foot{{margin-top:48px;color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:16px}}
@media (max-width:980px){{ h1{{font-size:32px}} .bar-row{{grid-template-columns:1fr}} }}
@media (max-width:640px){{ .wrap{{padding:18px 14px 48px}} h1{{font-size:28px}} }}
</style>
</head>
<body>
<div class="wrap">
  <header class="top">
    <div class="brand"><span class="mark">HL</span><div><b>Haval LocalAI Bench</b><em>Cross-model comparison</em></div></div>
    <div class="chips">{chip_html}</div>
  </header>
  <section>
    <div class="kicker">Haval LocalAI · LLM size comparison on one PC</div>
    <h1>{_hero_title(title, orange_word)}</h1>
    <p class="lead">{_e(lead)}</p>
    <div class="legs">{legend}</div>
    <div class="verdict"><h2>{_e(verdict_h)}</h2><p>{_e(verdict_p)}</p></div>
  </section>
  <section class="sec">
    <div class="kicker">01 · What each size actually won</div>
    <h3>What each size actually won</h3>
    <div class="grid">{winner_cards}</div>
  </section>
  <section class="sec">
    <div class="kicker">02 · Scoreboard</div>
    <h3>Scoreboard</h3>
    <div class="card scroll">{scoreboard}</div>
  </section>
  <section class="sec">
    <div class="kicker">03 · Capability pack</div>
    <h3>Capability pack</h3>
    {caps}
  </section>
  <section class="sec">
    <div class="kicker">04 · Time anatomy</div>
    <h3>Wait vs generate</h3>
    <div class="anatomy">{anatomy}</div>
  </section>
  <section class="sec">
    <div class="kicker">05 · Estimate total respond time per task</div>
    <h3>Estimate total respond time per task</h3>
    <p class="time-sub">The measure below is <b>Minute:Second</b> estimate.</p>
    <div class="time-ranks">{time_ranks}</div>
    <div class="kicker" style="margin-top:28px">06 · Model quality</div>
    <h3>Model quality</h3>
    <div class="time-ranks">{quality_ranks}</div>
    <div class="card scroll">{times}</div>
  </section>
  {uses}
  <footer class="foot">Haval LocalAI Bench · comparison built from {n} measured reports · {hw_note}</footer>
</div>
</body>
</html>
"""


def _hero_title(title: str, orange: str) -> str:
    if orange in title:
        a, b = title.split(orange, 1)
        return f"{_e(a)}<span>{_e(orange)}</span>{_e(b)}"
    return _e(title)


def _lead(wins: Winners, cols: list[MeasuredRun]) -> str:
    e, d = wins.everyday, wins.coder
    if e and d and e.model_key != d.model_key:
        return (
            f"{_short(e.model_name)} for chat and play, where first token matters. "
            f"{_short(d.model_name)} for engineering, where coding and reasoning come first. "
            "Fit depends on the job."
        )
    if d and not e:
        return f"{_short(d.model_name)} leads coding and reasoning on this PC. Fit depends on the job."
    if e:
        return f"{_short(e.model_name)} is the everyday fit when wait matters. Fit depends on the job."
    return f"{len(cols)} models on this PC. Fit depends on the job."


def _verdict(wins: Winners, cols: list[MeasuredRun]) -> tuple[str, str]:
    e, d, o = wins.everyday, wins.coder, wins.overall
    if e and d and e.model_key != d.model_key:
        h = f"{_short(e.model_name)} for chat and play. {_short(d.model_name)} for software engineering."
        p = "Consumer and gaming care about first token. Developers and deep roles care about coding and reasoning first; wait is second."
        return h, p
    if e and o and e.model_key != o.model_key:
        h = f"{_short(e.model_name)} for daily work. {_short(o.model_name)} when the problem is hard."
    elif e:
        h = f"{_short(e.model_name)} is the everyday model on this PC."
    elif d:
        h = f"{_short(d.model_name)} leads coding and reasoning on this PC."
    elif o:
        h = f"{_short(o.model_name)} posts the highest overall score."
    else:
        h = "Fit depends on the job."
    extra = []
    if d and (not e or d.model_key != e.model_key):
        extra.append(f"{_short(d.model_name)} leads coding and reasoning.")
    if wins.unusable:
        extra.append(f"{_short(wins.unusable.model_name)} is quick but not usable as a daily driver.")
    p = extra[0] if extra else "No single winner for every task. Chat cares about wait. Engineering cares about quality first."
    return h, p


def _winner_cards(wins: Winners, colors: dict[int, str]) -> str:
    cards = []
    if wins.overall:
        c = wins.overall
        cards.append(_wcard("Highest overall score", c, colors, f"Final {c.final if c.final is not None else '—'}. Phase 2 {c.phase2 if c.phase2 is not None else '—'}."))
    if wins.everyday:
        c = wins.everyday
        tt = f"{c.ttft_s:.1f}s" if c.ttft_s is not None else "—"
        cards.append(_wcard("Best everyday fit", c, colors, f"First token {tt}. For chat and play, wait matters more than peak coding."))
    if wins.coder:
        c = wins.coder
        code = _cap(c, "Coding")
        reason = _cap(c, "Reasoning")
        cards.append(
            _wcard(
                wins.coder_title,
                c,
                colors,
                f"Coding {code if code is not None else '—'}. Reasoning {reason if reason is not None else '—'}. For engineering, quality first; wait is second.",
            )
        )
    if wins.unusable:
        c = wins.unusable
        tt = f"{c.ttft_s:.1f}s" if c.ttft_s is not None else "—"
        cards.append(_wcard("Fastest, not usable", c, colors, f"First token {tt}. Final {c.final if c.final is not None else '—'}."))
    seen: set[str] = set()
    unique = []
    for card in cards:
        if card in seen:
            continue
        seen.add(card)
        unique.append(card)
    return "".join(unique[:4])


def _wcard(axis: str, col: MeasuredRun, colors: dict[int, str], body: str) -> str:
    color = colors[id(col)]
    return (
        f'<article class="card" style="border-top:4px solid {color}">'
        f'<div class="axis">{_e(axis)}</div>'
        f'<h4 style="color:{color}">{_e(_short(col.model_name))}</h4>'
        f"<p>{_e(body)}</p></article>"
    )


def _scoreboard(cols: list[MeasuredRun], colors: dict[int, str], everyday: MeasuredRun | None) -> str:
    rows = []
    for c in cols:
        color = colors[id(c)]
        size = _fmt_b(c.total_b) or "—"
        active = _fmt_b(c.active_b) or "—"
        tok = f"{c.tok_s:.1f}" if c.tok_s is not None else "—"
        avg = format_mmss(avg_task_seconds(c.personas))
        rows.append(
            f"<tr><td style=color:{color};font-weight:650>{_e(_short(c.model_name))}</td>"
            f"<td class=num>{_e(size)}</td><td class=num>{_e(active)}</td>"
            f"<td class=num>{_e(tok)}</td><td class=num>{_e(avg)}</td></tr>"
        )
    return (
        "<table><thead><tr><th>Model</th><th>Size</th><th>Active</th><th>Tok/s</th>"
        '<th class="task-est">Total estimated response per task</th></tr></thead><tbody>'
        + "".join(rows)
        + "</tbody></table>"
    )


def _capabilities(cols: list[MeasuredRun], colors: dict[int, str]) -> str:
    legend = "".join(
        f'<span class="leg"><i style="background:{colors[id(c)]}"></i>{_e(_short(c.model_name))}</span>'
        for c in cols
    )
    blocks = [f'<div class="legs">{legend}</div>']
    for cat in CAP_ORDER:
        rows = []
        for c in cols:
            score = _cap(c, cat)
            pct = 0 if score is None else max(0, min(100, score))
            width = max(8, pct) if score is not None else 8
            label = "—" if score is None else str(score)
            color = colors[id(c)]
            rows.append(
                f'<div class="bar-row"><label>{_e(_short(c.model_name))}</label>'
                f'<div class="track"><div class="fill" style="width:{width}%;background:{color}">{label}</div></div></div>'
            )
        blocks.append(f'<div class="cap-block"><div class="name">{_e(cat)}</div>{"".join(rows)}</div>')
    return "".join(blocks)


def _anatomy(cols: list[MeasuredRun], colors: dict[int, str]) -> str:
    cards = []
    for c in cols:
        wait = c.ttft_s if c.ttft_s is not None else 0
        mean = c.mean_s if c.mean_s is not None else 0
        gen = max(0.0, mean - wait)
        total = wait + gen
        wpct = (100 * wait / total) if total else 50
        gpct = 100 - wpct
        color = colors[id(c)]
        cards.append(
            f'<article class="card"><h4 style="color:{color}">{_e(_short(c.model_name))}</h4>'
            f'<div class="split"><span class="w" style="width:{wpct:.1f}%"></span>'
            f'<span class="g" style="width:{gpct:.1f}%"></span></div>'
            f'<div class="cap"><span>Wait {wait:.1f}s</span><span>Reply ~{format_mmss(mean)}</span></div></article>'
        )
    return "".join(cards)


def _place_label(index: int, *, first: str) -> str:
    place = index + 1
    if place == 1:
        return first
    if place == 2:
        return "2nd"
    if place == 3:
        return "3rd"
    return f"{place}th"


def _quality_flag(col: MeasuredRun) -> str | None:
    if col.finish == 0 or col.final is None:
        return "Failed quality"
    try:
        from haval_engine.scoring.rules import load_ruleset

        floor = float((load_ruleset().get("labels") or {}).get("marginal") or 48)
    except Exception:
        floor = 48.0
    if col.final < floor:
        return "Not recommended"
    return None


def _time_rank_cards(cols: list[MeasuredRun], colors: dict[int, str]) -> str:
    ranked: list[tuple[MeasuredRun, float | None]] = []
    for c in cols:
        ranked.append((c, avg_task_seconds(c.personas)))
    ranked.sort(key=lambda item: (item[1] is None, item[1] if item[1] is not None else 0.0))
    n = len(ranked)
    cards = []
    for i, (c, seconds) in enumerate(ranked):
        if n == 1:
            head = "Total respond time"
        elif i == 0 and seconds is not None:
            head = "Fastest"
        elif i == n - 1:
            head = "Slowest"
        else:
            head = _place_label(i, first="Fastest")
        cards.append(_rank_card(c, colors, head, format_mmss(seconds)))
    return "".join(cards)


def _quality_rank_cards(cols: list[MeasuredRun], colors: dict[int, str]) -> str:
    ranked = list(cols)
    ranked.sort(key=lambda c: (c.final is None, -(c.final or 0)))
    cards = []
    for i, c in enumerate(ranked):
        flag = _quality_flag(c)
        head = flag or _place_label(i, first="Highest quality")
        cards.append(_rank_card(c, colors, head, value=None, weak=bool(flag)))
    return "".join(cards)


def _rank_card(
    col: MeasuredRun,
    colors: dict[int, str],
    head: str,
    value: str | None = None,
    *,
    weak: bool = False,
) -> str:
    color = colors[id(col)]
    extra = ""
    if value is None:
        extra += " quality-rank"
    if weak:
        extra += " weak"
    body = f'<p class="time-rank-val">{_e(value)}</p>' if value is not None else ""
    return (
        f'<article class="card time-rank{extra}" style="border-top:4px solid {color}">'
        f'<div class="time-rank-head">{_e(head)}</div>'
        f'<h4 style="color:{color}">{_e(_short(col.model_name))}</h4>'
        f"{body}</article>"
    )


def _time_table(cols: list[MeasuredRun], colors: dict[int, str]) -> str:
    seen = {p.name for c in cols for p in c.personas}
    ordered = [(b, n) for b, n in PERSONA_ORDER if n in seen]
    extra = sorted(seen - {n for _, n in PERSONA_ORDER})
    rows_src = ordered + [("", n) for n in extra]
    head = "".join(
        f'<th class="center" style="color:{colors[id(c)]};text-transform:none;letter-spacing:0;font-size:13px">{_e(_short(c.model_name))}</th>'
        for c in cols
    )
    body = []
    for _, name in rows_src:
        cells = [f'<td><div class="role">{_icon_svg(name)}{_e(name)}</div></td>']
        for c in cols:
            row = next((p for p in c.personas if p.name == name), None)
            est = estimate_task_seconds(row) if row else None
            if est is None:
                cells.append('<td class="center dash">—</td>')
            else:
                cells.append(f'<td class="center num">{format_mmss(est)}</td>')
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (
        f'<table><thead><tr><th>Task / role</th>{head}</tr></thead><tbody>{"".join(body)}</tbody></table>'
    )


def _use_cases(wins: Winners, colors: dict[int, str]) -> str:
    cards = []
    if wins.everyday:
        c = wins.everyday
        cards.append(_ucard("Consumer and gaming", c, colors, "Chat and play. First-token wait is the priority. The answer still has to be usable."))
    if wins.coder and (not wins.everyday or wins.coder.model_key != wins.everyday.model_key):
        c = wins.coder
        cards.append(_ucard("Software engineering", c, colors, "Coding, reasoning, and deep work. Quality first. Response time is second."))
    if wins.overall and wins.coder and wins.overall.model_key != wins.coder.model_key and (
        not wins.everyday or wins.overall.model_key != wins.everyday.model_key
    ):
        o = wins.overall
        cards.append(_ucard("Hard problems only", o, colors, "Highest overall score on this PC."))
    if not cards:
        return ""
    return (
        '<section class="sec"><div class="kicker">07 · A simple rule for this PC</div>'
        f"<h3>A simple rule for this PC</h3><div class=\"use\">{''.join(cards[:3])}</div></section>"
    )


def _ucard(title: str, col: MeasuredRun, colors: dict[int, str], body: str) -> str:
    color = colors[id(col)]
    return (
        f'<article class="card"><div class="axis">{_e(title)}</div>'
        f'<h4 style="color:{color}">{_e(_short(col.model_name))}</h4>'
        f"<p>{_e(body)}</p></article>"
    )
