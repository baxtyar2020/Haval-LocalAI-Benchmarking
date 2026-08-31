# Student & Learner — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer wants to understand a pasted passage and leave with something they can study. They ask for bullets, a quiz from their notes, or a one-page sheet. Do not add outside chapters. Default student is not in a STEM class unless the paste is.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is five bullets I can reread on the bus.

**Rafi:** Balanced is a quiz I can fail honestly.

**Lin:** Heavy is a study sheet from MY notes, not a textbook the model invented.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants the sheet, not a lecture

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

They bounce if the model writes a chapter. Default student is not in a math or CS class — do not force those.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 6 s | **25 s** |
| Balanced | **550 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Ask / scenario:** They pasted a hard paragraph from class. They are asking the AI to explain it in five bullets using only that paragraph.

### What they type

```text
Explain ONLY the paragraph I paste. Do not add outside facts.

PARAGRAPH
[PASTE]

Write:
1) 5 bullets, plain words
2) 1 sentence I would write in the margin
3) 1 word I should look up — only if it is in the paragraph

HARD LIMIT: 160 words. No preamble.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 5 bullets + margin line. Cap ≤280 tokens. Math/coding gates stay 0 unless the homework is STEM.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They want to quiz themselves from their own notes. They are asking the AI for five questions that stay inside the paste and do not invent extra facts.

### What they type

```text
From NOTES only, write 5 quiz items.
3 recall, 2 “why”.
After each item put the answer in one line starting ANSWER:

NOTES
[PASTE]

If the notes do not support an item, skip it. Do not invent.

HARD LIMIT: 220 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** 5 items with answers. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Lecture notes are pasted and a test is coming. They are asking the AI for a one-page study sheet from those notes only.

### What they type

```text
Make a study sheet from NOTES only.

Sections:
- Must know (max 6)
- Why it matters (max 3)
- Likely test traps (max 3)
- [MISSING] lines for anything I asked that is not in the notes

NOTES
[PASTE]

HARD LIMIT: 320 words. No extra chapters.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Heavy

**Expected result:** one sheet, [MISSING] used. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Student & Learner

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 6 s | 25 s |
| Balanced | 550 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 5 bullets from the paragraph only | Outside textbook facts |
| Balanced | 5 quiz items with ANSWER lines from notes | Invented items |
| Heavy | Study sheet + [MISSING] for holes | Extra chapters |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
