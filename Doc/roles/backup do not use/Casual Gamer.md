# Casual Gamer — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Pick something to play and how to start. No meta essay.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is three names.

**Rafi:** Balanced is one game and a 20-minute start plan.

**Lin:** Heavy is a weekend plan for one game I already own.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role has the shortest fuse

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Lowest bar in the set. If the answer is a guide, it already failed.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **200 tokens** | 5 s | **20 s** |
| Balanced | **400 tokens** / turn | 8 s | **40 s** |
| Heavy | **700 tokens** / turn | 10 s | **75 s** |

---

## 1. Light

**Job:** What should I play tonight, 3 names.

### Prompt (copy / paste)

```text
I have 90 minutes. I like cozy or light co-op. I own: Stardew, Overcooked 2, Rocket League.

Give 3 picks, 8 words of why each. No new titles I must buy.

HARD LIMIT: 80 words.
```

### Expected result & local LLM time — Light

**Expected result:** 3 named picks. Cap ≤200 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **5 s** | ~9 s blank |
| Full answer | — | **20 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** 20-minute start plan for one owned game.

### Prompt (copy / paste)

```text
Game: Stardew. I have 20 minutes before bed.
Tell me exactly what to do in 6 steps. No lore.

HARD LIMIT: 120 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** 6 steps. Cap ≤400 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **40 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Saturday session for a game I own.

### Prompt (copy / paste)

```text
Game: [NAME]. Window: Sat 2–5pm. Goal: have fun, not min-max.
Plan 3 blocks of 50 min + 10 min break.
Each block: one goal I can finish.

HARD LIMIT: 180 words.
```

### Expected result & local LLM time — Heavy

**Expected result:** 3 blocks. Cap ≤700 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **10 s** | ~18 s blank |
| Full answer | — | **75 s** | frozen spinner past that |

### Local LLM time summary — Casual Gamer

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 200 | 5 s | 20 s |
| Balanced | 400 / turn | 8 s | 40 s |
| Heavy | 700 / turn | 10 s | 75 s |

Split Heavy into two turns if the first answer hits the cap.

