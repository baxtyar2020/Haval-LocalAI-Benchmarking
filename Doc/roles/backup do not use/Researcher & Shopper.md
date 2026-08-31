# Researcher & Shopper — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Compare options from pasted facts. Do not invent a spec or a price.

Hardware is shared. Patience is not.

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

**Job:** 3-row compare from pasted prices.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Light

**Expected result:** 3-row table + pick. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Pick a headset from pasted spec sheet.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Balanced

**Expected result:** winner / runner / rejects. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Shortlist of 4 with a reject list.

### Prompt (copy / paste)

```text
Build a 4-row shortlist from PASTE only.
Columns: option | price | must-haves hit | deal-breaker | source line.
Then 4 reject rules I should keep next time.

If PASTE has fewer than 4 options, do not invent rows.

PASTE
[PASTE]

HARD LIMIT: 280 words.
```

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

