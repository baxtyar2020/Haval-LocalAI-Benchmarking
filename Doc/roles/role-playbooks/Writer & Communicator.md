# Writer & Communicator — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer needs the asked voice and length, with no extra claims. They paste a draft or notes and want a rewrite, three variants, or an outline plus one section. They will not wait for a think-piece.

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

**Ask / scenario:** They have a draft and a voice they want. They are asking the AI to rewrite it in that voice, short, without adding new claims.

### What they type

```text
Rewrite DRAFT in VOICE. Do not add facts.

VOICE: dry, specific, no slogans, no emoji.
MAX: 80 words.
Keep every number that is already in DRAFT.

DRAFT
[PASTE]

HARD LIMIT: 80 words of output + 1 line word count.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** one rewrite + count. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** One set of facts must do three jobs (email, post, blurb). They are asking the AI for three variants that keep the same facts and change only the job.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** three labeled variants. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **45 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** They need a piece started, not finished. They are asking the AI for an outline and section 1 only, from the brief they pasted.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

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

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | Voice rewrite ≤80 words + count | Added facts |
| Balanced | Three labeled variants, same facts | New metric |
| Heavy | Outline + header 1 only | Writes the full piece |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
