# Power Player — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer compares loadouts and ranks from pasted patch notes or stats. They want a tier table, a build, or a patch-diff plan. Invented winrates or stats not in the paste fail.

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

**Ask / scenario:** They named the roster they care about. They are asking the AI for a five-row tier list from those names only, not a meta essay or new titles.

### What they type

```text
Tier these ONLY: [NAMES].
Patch: [PASTE 5 LINES] or write [NO PATCH] and use names only.

Rows: S / A / B / C / leave-out.
One reason each, max 8 words, tied to the paste.

HARD LIMIT: 140 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 5 rows. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They pasted a character’s stats and want one build. They are asking the AI to write that build from the paste, not from a guessed patch.

### What they type

```text
STATS
[PASTE]
Goal: [burst / sustain / safe]
Give: 6 item/skill slots + 1 sentence why each.
Do not add stats not in PASTE. Use [MISSING].

HARD LIMIT: 200 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** 6 slots. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Their main shifted this patch and they pasted the notes they have. They are asking the AI what changed for that main from those notes, not from memory of the live game.

### What they type

```text
MAIN: [NAME]
PATCH NOTES (paste)
[PASTE]

1) Buffs / nerfs that touch MAIN
2) Drop / keep / try — 3 lines
3) One thing I should test in 10 games

HARD LIMIT: 240 words. No invented winrates.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

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

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 5-row tier from named list + paste | Invented patch stat |
| Balanced | 6 slots from pasted stats only | Adds stats not in PASTE |
| Heavy | Buff/nerf + drop/keep/try from notes | Invented winrate |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
