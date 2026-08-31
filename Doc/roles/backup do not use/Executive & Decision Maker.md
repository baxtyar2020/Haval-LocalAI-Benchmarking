# Executive & Decision Maker — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Choose among options without puffing the facts.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is three options and one recommend.

**Rafi:** Balanced is a one-pager from pasted metrics.

**Lin:** Heavy is go / no-go with kill criteria. No code.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role reads on a phone between meetings

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

They will wait for structure. They will not wait for a novel or a model they did not ask for.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 8 s | **30 s** |
| Balanced | **600 tokens** / turn | 10 s | **70 s** |
| Heavy | **1000 tokens** / turn | 15 s | **2.5 min** |

---

## 1. Light

**Job:** 3 options, one recommend, no new facts.

### Prompt (copy / paste)

```text
QUESTION: hire contractor 3 months vs freeze the workstream.
FACTS
- Budget left $42k
- Need date Oct 15
- Internal owner at 0.3 FTE

Write 3 options, 2 lines each, then 1 recommend line.
Do not invent a vendor name or a date.

HARD LIMIT: 160 words.
```

### Expected result & local LLM time — Light

**Expected result:** 3 options + recommend. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **30 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** One-pager from pasted metrics.

### Prompt (copy / paste)

```text
METRICS (do not add)
[PASTE]

Page:
- What changed
- So what
- Options (max 3)
- Ask of me
- [MISSING]

HARD LIMIT: 240 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** one-pager. Cap ≤600 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **10 s** | ~18 s blank |
| Full answer | — | **70 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Go / no-go card.

### Prompt (copy / paste)

```text
DECISION: [PASTE]
FACTS: [PASTE]

1) Go looks like
2) No-go looks like
3) Kill this in 30 days if…
4) What I am not deciding today

HARD LIMIT: 300 words.
```

### Expected result & local LLM time — Heavy

**Expected result:** decision card. Cap ≤1000 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **15 s** | ~27 s blank |
| Full answer | — | **2.5 min** | frozen spinner past that |

### Local LLM time summary — Executive & Decision Maker

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 8 s | 30 s |
| Balanced | 600 / turn | 10 s | 70 s |
| Heavy | 1000 / turn | 15 s | 2.5 min |

Split Heavy into two turns if the first answer hits the cap.

