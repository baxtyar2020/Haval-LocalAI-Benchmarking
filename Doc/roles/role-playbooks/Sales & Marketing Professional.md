# Sales & Marketing Professional — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer writes from approved claims only. They paste claims or call notes and want a blurb, a three-touch sequence, or an objection map. No new promises, awards, or invented case studies.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is a blurb from three claims.

**Rafi:** Balanced is a sequence of three touches.

**Lin:** Heavy is an objection map from pasted call notes.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants copy they can send today

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

IF over math. Pipeline % is optional. Coding unused.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **250 tokens** | 6 s | **25 s** |
| Balanced | **550 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Ask / scenario:** They have three approved claims for an offer. They are asking the AI to write the blurb from those claims only, with no new proof points.

### What they type

```text
CLAIMS (do not add)
1) Ships in 5 days
2) Setup under 30 minutes
3) Email support, business hours

Audience: ops manager, mid-market.
80 words max. No awards, no “#1”.

HARD LIMIT: 80 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** one blurb. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They need a three-touch sequence that repeats the same claims. They are asking the AI for those three messages without adding features they did not name.

### What they type

```text
CLAIMS: [PASTE]
Day 0 / Day 3 / Day 7
Each: subject ≤50 chars + 4-line body.
Do not add a discount unless it is in CLAIMS.

HARD LIMIT: 220 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** 3 emails. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Call notes are pasted and objections are mixed in. They are asking the AI to map objections and replies from those notes, not from a generic sales book.

### What they type

```text
NOTES
[PASTE]

Table: objection | exact phrase if any | answer from NOTES | [MISSING] if we have no answer
Max 6 rows. No invented case studies.

HARD LIMIT: 260 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** ≤6 rows. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Sales & Marketing Professional

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 250 | 6 s | 25 s |
| Balanced | 550 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Blurb from three claims only | Awards or #1 |
| Balanced | 3 touches, no extra discount | New promise |
| Heavy | ≤6 objection rows from notes | Invented case study |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
