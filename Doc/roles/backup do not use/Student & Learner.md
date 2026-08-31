# Student & Learner — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Understand a passage and leave with something they can study.

Hardware is shared. Patience is not.

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

**Job:** Explain this paragraph in 5 bullets.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Light

**Expected result:** 5 bullets + margin line. Cap ≤280 tokens. Math/coding gates stay 0 unless the homework is STEM.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** 5 quiz items from my notes only.

### Prompt (copy / paste)

```text
From NOTES only, write 5 quiz items.
3 recall, 2 “why”.
After each item put the answer in one line starting ANSWER:

NOTES
[PASTE]

If the notes do not support an item, skip it. Do not invent.

HARD LIMIT: 220 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** 5 items with answers. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** One-page study sheet from pasted lecture notes.

### Prompt (copy / paste)

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

