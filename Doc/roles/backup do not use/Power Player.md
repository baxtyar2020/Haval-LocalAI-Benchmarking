# Power Player — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Compare loadouts and ranks from pasted patch notes / stats. Not a developer.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is a 5-row tier from these names.

**Rafi:** Balanced is a build from pasted numbers.

**Lin:** Heavy is a patch-diff plan. Invented stats fail.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role will wait for a table, not a manifesto

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Math is game-stat math. Coding not gated.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 6 s | **25 s** |
| Balanced | **550 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Job:** 5-row tier list from these names.

### Prompt (copy / paste)

```text
Tier these ONLY: [NAMES].
Patch: [PASTE 5 LINES] or write [NO PATCH] and use names only.

Rows: S / A / B / C / leave-out.
One reason each, max 8 words, tied to the paste.

HARD LIMIT: 140 words.
```

### Expected result & local LLM time — Light

**Expected result:** 5 rows. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** One build from pasted stats.

### Prompt (copy / paste)

```text
STATS
[PASTE]
Goal: [burst / sustain / safe]
Give: 6 item/skill slots + 1 sentence why each.
Do not add stats not in PASTE. Use [MISSING].

HARD LIMIT: 200 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** 6 slots. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** What changed for my main this patch.

### Prompt (copy / paste)

```text
MAIN: [NAME]
PATCH NOTES (paste)
[PASTE]

1) Buffs / nerfs that touch MAIN
2) Drop / keep / try — 3 lines
3) One thing I should test in 10 games

HARD LIMIT: 240 words. No invented winrates.
```

### Expected result & local LLM time — Heavy

**Expected result:** diff + plan. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Power Player

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 6 s | 25 s |
| Balanced | 550 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

