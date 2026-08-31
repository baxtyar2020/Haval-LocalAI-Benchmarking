# Writer & Communicator — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Say it in the asked voice and length. No extra claims.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is an 80-word rewrite I can send.

**Rafi:** Balanced is three variants that stay in voice.

**Lin:** Heavy is an outline then one section — not the whole piece in one shot.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants the paragraph now

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

IF is the product. Math unused. They will not wait for a think-piece.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **250 tokens** | 6 s | **25 s** |
| Balanced | **500 tokens** / turn | 8 s | **45 s** |
| Heavy | **900 tokens** / turn | 12 s | **90 s** |

---

## 1. Light

**Job:** Rewrite in this voice, ≤80 words.

### Prompt (copy / paste)

```text
Rewrite DRAFT in VOICE. Do not add facts.

VOICE: dry, specific, no slogans, no emoji.
MAX: 80 words.
Keep every number that is already in DRAFT.

DRAFT
[PASTE]

HARD LIMIT: 80 words of output + 1 line word count.
```

### Expected result & local LLM time — Light

**Expected result:** one rewrite + count. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Three variants, same facts, different jobs.

### Prompt (copy / paste)

```text
Same FACTS. Three pieces:
1) email subject + 3-line body
2) Slack, max 40 words
3) 1-sentence status

FACTS
[PASTE]
VOICE: calm, no hype.

Do not add a metric that is not in FACTS.

HARD LIMIT: 180 words total.
```

### Expected result & local LLM time — Balanced

**Expected result:** three labeled variants. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **45 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Outline plus section 1 only.

### Prompt (copy / paste)

```text
Audience: [WHO]
Piece: [WHAT]
Length target: 600 words later, not now.

From NOTES only:
1) 6-header outline
2) Write ONLY header 1, max 120 words
3) [MISSING] for holes

NOTES
[PASTE]

Do not write the full piece.

HARD LIMIT: 280 words this turn.
```

### Expected result & local LLM time — Heavy

**Expected result:** outline + one section. Cap ≤900 tokens. Next turn = next header.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **90 s** | frozen spinner past that |

### Local LLM time summary — Writer & Communicator

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 250 | 6 s | 25 s |
| Balanced | 500 / turn | 8 s | 45 s |
| Heavy | 900 / turn | 12 s | 90 s |

Split Heavy into two turns if the first answer hits the cap.

