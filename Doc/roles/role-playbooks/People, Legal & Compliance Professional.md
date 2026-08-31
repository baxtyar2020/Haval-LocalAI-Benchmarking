# People, Legal & Compliance Professional — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer keeps every constraint and marks holes. They paste source text and ask for a rewrite, a clause map, or an issues memo. This pack is not legal advice. Chat must not add a rule or draft as counsel of record.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is a rewrite that drops nothing.

**Rafi:** Balanced is a clause map.

**Lin:** Heavy is a review memo from pasted text.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role will wait for care, not for speed-slop

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Highest IF floor in the set. Still a floor. Coding and math unused.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **300 tokens** | 8 s | **35 s** |
| Balanced | **650 tokens** / turn | 12 s | **75 s** |
| Heavy | **1100 tokens** / turn | 18 s | **2.5 min** |

---

## 1. Light

**Ask / scenario:** They have a draft that must keep every named constraint. They are asking the AI to rewrite it, keep those limits, and mark [MISSING] instead of filling gaps.

### What they type

```text
SOURCE
[PASTE]
CONSTRAINTS I MUST KEEP
[PASTE]

Rewrite for a manager audience.
If a constraint cannot be kept in plain language, quote it.
Do not add a rule.

HARD LIMIT: 180 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** rewrite + kept constraints. Cap ≤300 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **35 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They pasted contract or policy language. They are asking the AI to map the clauses they must keep, drop, or flag — without adding legal advice that was not in the paste.

### What they type

```text
TEXT
[PASTE]

Table: clause | who it binds | trigger | obligation | exception | [MISSING]
Max 8 rows. No new clauses.

HARD LIMIT: 240 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** ≤8 rows. Cap ≤650 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **12 s** | ~21 s blank |
| Full answer | — | **75 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They need a review memo before something ships. They are asking the AI to list issues only from the pasted text, not a general lecture on the law.

### What they type

```text
DOCUMENT
[PASTE]
QUESTION
[PASTE]

Memo:
- Issues found (cite a line)
- What the document does not say
- Questions for counsel / HR (max 5)
- What I did not decide

HARD LIMIT: 320 words. Not legal advice.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** issue memo. Cap ≤1100 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **18 s** | ~32 s blank |
| Full answer | — | **2.5 min** | frozen spinner past that |

### Local LLM time summary — People, Legal & Compliance Professional

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 300 | 8 s | 35 s |
| Balanced | 650 / turn | 12 s | 75 s |
| Heavy | 1100 / turn | 18 s | 2.5 min |

Split Heavy into two turns if the first answer hits the cap.

This pack is not legal advice. The human owns the filing.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Rewrite keeps every constraint; quotes if needed | Adds a rule |
| Balanced | ≤8-row clause map, no new clauses | Invented obligation |
| Heavy | Issue memo, not legal advice | Drafts as counsel of record |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
