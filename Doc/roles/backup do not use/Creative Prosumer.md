# Creative Prosumer — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Make variants and briefs for their own content. Chat only — prompt text, not renders.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is three captions I can post.

**Rafi:** Balanced is a still-prompt + caption pack for one asset.

**Lin:** Heavy is a mini brief for a weekend project. Not a series bible.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role is faster than an engineer, slower than a poster in a panic

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Below Progressive Creator on continuity. Above Casual on structure. No coding.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **280 tokens** | 6 s | **25 s** |
| Balanced | **550 tokens** / turn | 8 s | **50 s** |
| Heavy | **900 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Job:** 3 caption variants, no emoji.

### Prompt (copy / paste)

```text
Asset: 8s clip of a desk lamp turning on.
Audience: makers, 20–35.
Write 3 captions, different angle (utility / mood / mistake).
Max 12 words each. No emoji. No “unlock”.

HARD LIMIT: 80 words.
```

### Expected result & local LLM time — Light

**Expected result:** 3 captions. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** One still-prompt (text) + 2 platform lines.

### Prompt (copy / paste)

```text
Write text only. Do not render.

STILL PROMPT
- 4:5 photo, warm lamp left, cold monitor right
- product: black headset on stand
- rejects: extra fingers, readable fake logos, watermark

Then:
- IG line ≤80 chars
- YT title ≤50 chars

HARD LIMIT: 160 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** prompt + 2 lines. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Weekend project brief, one sitting.

### Prompt (copy / paste)

```text
I have Sat morning. One piece: “repair a scratch on a desk” timelapse.

Write:
1) 5-beat shot list (SEE / HEAR only)
2) 1 still-prompt for the thumbnail
3) 1 caption
4) 3 things I will not do (scope)

HARD LIMIT: 260 words. No gear I did not name.
```

### Expected result & local LLM time — Heavy

**Expected result:** brief + prompt text. Cap ≤900 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Creative Prosumer

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 280 | 6 s | 25 s |
| Balanced | 550 / turn | 8 s | 50 s |
| Heavy | 900 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

