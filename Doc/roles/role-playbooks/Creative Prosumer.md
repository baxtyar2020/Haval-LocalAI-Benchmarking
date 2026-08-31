# Creative Prosumer — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer makes their own stills and clips. They ask chat for captions, still-prompt text, and a small brief. Chat writes prompt text only — it does not render images or video. They copy the text and generate elsewhere.

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

**Ask / scenario:** They have a short desk-lamp clip and need post copy. They are asking the AI for three caption angles they can paste, with no emoji and no render.

### What they type

```text
Asset: 8s clip of a desk lamp turning on.
Audience: makers, 20–35.
Write 3 captions, different angle (utility / mood / mistake).
Max 12 words each. No emoji. No “unlock”.

HARD LIMIT: 80 words.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 3 captions. Cap ≤280 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They are packing one still for social. They are asking the AI to write the image-prompt text plus one IG line and one YT title — text only, no render.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** prompt + 2 lines. Cap ≤550 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They have Saturday morning for one repair-timelapse piece. They are asking the AI for a mini brief: shot list, thumbnail prompt text, caption, and what they will not do.

### What they type

```text
I have Sat morning. One piece: “repair a scratch on a desk” timelapse.

Write:
1) 5-beat shot list (SEE / HEAR only)
2) 1 still-prompt for the thumbnail
3) 1 caption
4) 3 things I will not do (scope)

HARD LIMIT: 260 words. No gear I did not name.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

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

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 3 captions, no emoji, no render | Asks to generate the image |
| Balanced | Still-prompt text + platform lines | Renders pixels or adds fake logos |
| Heavy | Beat list + thumbnail prompt text + scope no | Series bible or extra gear |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
