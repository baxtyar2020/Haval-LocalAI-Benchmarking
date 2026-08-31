# Researcher & Shopper — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer compares options from pasted facts only. They want a screenshotable table, a pick tied to a pasted number, or a shortlist with rejects. Do not invent a spec or a price.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is a 3-row table I can screenshot.

**Rafi:** Balanced is a pick with the reason tied to a pasted number.

**Lin:** Heavy is a shortlist with rejects. Fake review quotes are a fail.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants the matrix now

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Structure matters more than clever reasoning. Invented prices fail IF.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 6 s | **25 s** |
| Balanced | **550 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Ask / scenario:** They pasted prices for a few options. They are asking the AI for a three-row compare from that paste, with no imagined SKUs or sale prices.

### What they type

```text
Compare ONLY these three. Do not add models.

A: 14-inch, 16GB, $899, 1.3kg
B: 14-inch, 32GB, $1299, 1.4kg
C: 16-inch, 16GB, $1099, 1.8kg

Need: travel, 16GB min, budget $1100.

Table: name | RAM | weight | price | fit? (yes/no + 3 words)
Then one line: cheapest that fits, or [NONE].

HARD LIMIT: 140 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 3-row table + pick. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They pasted a spec sheet and need one headset pick. They are asking the AI to choose from those specs only and say why in short lines.

### What they type

```text
I will buy one. Use FACTS only.

FACTS
[PASTE SPECS / PRICES]

Must: mic boom, USB, under $120.
Want: mute light.

Write:
- Winner + 2 lines why (cite facts)
- Runner-up + 1 line
- Rejects + 1 line each
- [MISSING] if a must is not in FACTS

HARD LIMIT: 200 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** winner / runner / rejects. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They are narrowing a buy and pasted the candidates they will consider. They are asking the AI for a shortlist of four plus a reject list, still inside that paste.

### What they type

```text
Build a 4-row shortlist from PASTE only.
Columns: option | price | must-haves hit | deal-breaker | source line.
Then 4 reject rules I should keep next time.

If PASTE has fewer than 4 options, do not invent rows.

PASTE
[PASTE]

HARD LIMIT: 280 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** ≤4 rows, no invented options. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Researcher & Shopper

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 6 s | 25 s |
| Balanced | 550 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 3-row table + cheapest that fits or [NONE] | Added a fourth model or price |
| Balanced | Winner/runner/rejects citing FACTS | Invented mute-light if not in FACTS |
| Heavy | ≤4 rows from paste; no invented options | Fake review quotes |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
