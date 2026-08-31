# People, Legal & Compliance Professional — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Keep every constraint. Mark holes. Do not draft as if you are counsel of record.

Hardware is shared. Patience is not.

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

**Job:** Rewrite, keep every constraint, mark [MISSING].

### Prompt (copy / paste)

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

### Expected result & local LLM time — Light

**Expected result:** rewrite + kept constraints. Cap ≤300 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **35 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Clause map.

### Prompt (copy / paste)

```text
TEXT
[PASTE]

Table: clause | who it binds | trigger | obligation | exception | [MISSING]
Max 8 rows. No new clauses.

HARD LIMIT: 240 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** ≤8 rows. Cap ≤650 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **12 s** | ~21 s blank |
| Full answer | — | **75 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Review memo — issues only.

### Prompt (copy / paste)

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

