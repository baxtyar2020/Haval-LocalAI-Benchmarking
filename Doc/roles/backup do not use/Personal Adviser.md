# Personal Adviser — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Lay out options and mark what is unknown. No medical, legal, or tax invention.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is two options and what you don’t know.

**Rafi:** Balanced is a decision card with kill criteria.

**Lin:** Heavy is a memo from pasted numbers only.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role will wait a little, then leave

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Reasoning matters. Invented advice is an IF fail. Coding unused.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 7 s | **30 s** |
| Balanced | **550 tokens** / turn | 10 s | **60 s** |
| Heavy | **1000 tokens** / turn | 15 s | **2 min** |

---

## 1. Light

**Job:** Two options, list what you don’t know.

### Prompt (copy / paste)

```text
Decision: keep the 2018 car 2 more years vs buy used ≤$18k.

FACTS I HAVE
- Car paid off
- Last year repairs $1,400
- Commute 12 miles

Write:
- Option A / B, 3 lines each
- What I must still find out (max 4)
- Do not recommend a lender or a diagnosis

HARD LIMIT: 180 words.
```

### Expected result & local LLM time — Light

**Expected result:** two options + unknowns. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **7 s** | ~12 s blank |
| Full answer | — | **30 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Decision card with a kill line.

### Prompt (copy / paste)

```text
Build a card.

QUESTION: [PASTE]
FACTS: [PASTE]

Sections:
- What is already decided
- Two paths
- Kill this plan if…
- [MISSING]

No medical/legal/tax rules unless they appear in FACTS.

HARD LIMIT: 220 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** one card. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **10 s** | ~18 s blank |
| Full answer | — | **60 s** | ~1.5× that |

---

## 3. Heavy

**Job:** One-page memo from pasted quotes.

### Prompt (copy / paste)

```text
Use QUOTES only.

QUOTES
[PASTE]

Write:
1) Situation in 4 lines
2) Options (max 3)
3) Tradeoffs table
4) What I am not qualified to decide here

HARD LIMIT: 320 words. Two turns if longer.
```

### Expected result & local LLM time — Heavy

**Expected result:** memo skeleton. Cap ≤1000 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **15 s** | ~27 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Personal Adviser

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 7 s | 30 s |
| Balanced | 550 / turn | 10 s | 60 s |
| Heavy | 1000 / turn | 15 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

