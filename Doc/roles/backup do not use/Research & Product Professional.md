# Research & Product Professional — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Turn evidence into a spec stub. No fake quotes. Coding not required.

Hardware is shared. Patience is not.

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

**Job:** Problem / evidence / open question.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Light

**Expected result:** three blocks. Cap ≤300 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **30 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** PRD slice — one job story.

### Prompt (copy / paste)

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

### Expected result & local LLM time — Balanced

**Expected result:** one slice. Cap ≤650 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **10 s** | ~18 s blank |
| Full answer | — | **70 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Experiment log from pasted numbers.

### Prompt (copy / paste)

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

