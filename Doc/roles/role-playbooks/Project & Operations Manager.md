# Project & Operations Manager — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer keeps owners, dates, and status consistent. They paste a mess of notes and want a 5-row plan, a RACI, or a RAID log. Spreadsheet stays human. Do not invent an owner.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is a 5-row plan.

**Rafi:** Balanced is a RACI for one workstream.

**Lin:** Heavy is a RAID from pasted status only.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants the table clean

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Structure is the gate. Coding is not. They bounce on essays.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 7 s | **30 s** |
| Balanced | **600 tokens** / turn | 10 s | **70 s** |
| Heavy | **1000 tokens** / turn | 15 s | **2.5 min** |

---

## 1. Light

**Ask / scenario:** A workstream needs a glanceable plan. They are asking the AI for a five-row owner / date / status table from the facts they typed, with no extra work invented.

### What they type

```text
Turn this mess into 5 rows: item | owner | date | status | note.
MESS
[PASTE]
If a field is unknown write [MISSING]. Do not invent an owner.

HARD LIMIT: 140 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 5 rows. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **7 s** | ~12 s blank |
| Full answer | — | **30 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** One workstream has fuzzy owners. They are asking the AI for a RACI on that stream only, using the names they gave.

### What they type

```text
Workstream: [NAME]
People: [LIST]
Tasks: [LIST]

Table: task | R | A | C | I
One person in A per task. If you cannot tell, [MISSING].

HARD LIMIT: 200 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** RACI table. Cap ≤600 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **10 s** | ~18 s blank |
| Full answer | — | **70 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Standup notes are pasted and risks are buried in chat. They are asking the AI to pull a RAID log from those notes and not invent risks that were not written.

### What they type

```text
NOTES
[PASTE]

Four lists: Risks | Assumptions | Issues | Dependencies
Each line: statement | owner | date if any | [MISSING] if none
Do not add items not implied by NOTES.

HARD LIMIT: 280 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** RAID lists. Cap ≤1000 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **15 s** | ~27 s blank |
| Full answer | — | **2.5 min** | frozen spinner past that |

### Local LLM time summary — Project & Operations Manager

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 7 s | 30 s |
| Balanced | 600 / turn | 10 s | 70 s |
| Heavy | 1000 / turn | 15 s | 2.5 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 5 rows; [MISSING] if no owner | Invented owner |
| Balanced | RACI, one A per task | Guesses A |
| Heavy | RAID from notes only | Adds items not implied |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
