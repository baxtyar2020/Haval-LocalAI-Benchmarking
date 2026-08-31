# Sales & Marketing Professional — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Write from approved claims only. No new promises.

Hardware is shared. Patience is not.

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

**Job:** Offer blurb from these three claims only.

### Prompt (copy / paste)

```text
CLAIMS (do not add)
1) Ships in 5 days
2) Setup under 30 minutes
3) Email support, business hours

Audience: ops manager, mid-market.
80 words max. No awards, no “#1”.

HARD LIMIT: 80 words.
```

### Expected result & local LLM time — Light

**Expected result:** one blurb. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Three-touch sequence, same claims.

### Prompt (copy / paste)

```text
CLAIMS: [PASTE]
Day 0 / Day 3 / Day 7
Each: subject ≤50 chars + 4-line body.
Do not add a discount unless it is in CLAIMS.

HARD LIMIT: 220 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** 3 emails. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Objection map from call notes.

### Prompt (copy / paste)

```text
NOTES
[PASTE]

Table: objection | exact phrase if any | answer from NOTES | [MISSING] if we have no answer
Max 6 rows. No invented case studies.

HARD LIMIT: 260 words.
```

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

