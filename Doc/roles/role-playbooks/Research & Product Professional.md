# Research & Product Professional — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer turns pasted evidence into a spec stub. No fake quotes. They ask chat for a problem statement, a PRD slice, or an experiment log. Coding is not required. Invented user quotes fail.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is problem / evidence / open.

**Rafi:** Balanced is a PRD slice from interviews.

**Lin:** Heavy is an experiment log from pasted results.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role will wait for structure, not for code

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

SQL is optional and not a gate. Invented user quotes fail.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **300 tokens** | 8 s | **30 s** |
| Balanced | **650 tokens** / turn | 10 s | **70 s** |
| Heavy | **1100 tokens** / turn | 15 s | **2.5 min** |

---

## 1. Light

**Ask / scenario:** They have a product problem and some evidence. They are asking the AI to write problem, evidence, and one open question — no extra research claims.

### What they type

```text
From NOTES only.

NOTES
[PASTE]

Write:
- Problem in 2 sentences
- Evidence (bullet per quote or metric in NOTES)
- Open questions (max 4)
- [MISSING]

HARD LIMIT: 180 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** three blocks. Cap ≤300 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **30 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They need one job story, not a full PRD. They are asking the AI for that slice from the pasted user problem only.

### What they type

```text
Job story I want: [PASTE]
Evidence: [PASTE]

Write:
1) User / job / circumstance
2) In-scope (max 5)
3) Out-of-scope (max 5)
4) Acceptance checks (max 5)
No roadmap fiction.

HARD LIMIT: 240 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** one slice. Cap ≤650 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **10 s** | ~18 s blank |
| Full answer | — | **70 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They ran a test and pasted the numbers. They are asking the AI to write the experiment log from those numbers and mark [MISSING] where the paste is silent.

### What they type

```text
RESULTS
[PASTE]
HYPOTHESIS
[PASTE]

Log:
- What we thought
- What we measured (only pasted numbers)
- What we did not measure
- Keep / drop / rerun
- [MISSING]

HARD LIMIT: 300 words. No p-values you cannot see.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** log. Cap ≤1100 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **15 s** | ~27 s blank |
| Full answer | — | **2.5 min** | frozen spinner past that |

### Local LLM time summary — Research & Product Professional

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 300 | 8 s | 30 s |
| Balanced | 650 / turn | 10 s | 70 s |
| Heavy | 1100 / turn | 15 s | 2.5 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Problem + evidence from notes + open Qs | Fake user quote |
| Balanced | One job-story slice, no roadmap fiction | Invented scope |
| Heavy | Experiment log from pasted numbers only | p-values you cannot see |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
