# Technical Hobbyist — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Get a small project unstuck — error, pin, 20-line script.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is what line 12 means.

**Rafi:** Balanced is a script I can flash or run.

**Lin:** Heavy is debug + the fix, not a rewrite of the whole repo.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role waits for a snippet, not a framework

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Coding is required. Not engineer-long. 45 coding floor — it should be able to run.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **350 tokens** | 8 s | **40 s** |
| Balanced | **700 tokens** / turn | 12 s | **90 s** |
| Heavy | **1100 tokens** / turn | 18 s | **2.5 min** |

---

## 1. Light

**Job:** What does this error on line 12 mean?

### Prompt (copy / paste)

```text
Explain this error in 6 lines. Then the smallest change.

LANG: Python 3
ERROR
[PASTE]
CODE
[PASTE]

No tutorial. No extra libraries.

HARD LIMIT: 160 words + a short patch.
```

### Expected result & local LLM time — Light

**Expected result:** 6-line why + patch. Cap ≤350 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **40 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** 20-line script that does one job.

### Prompt (copy / paste)

```text
Write one file.

JOB: read a folder of .wav names and print duration seconds using stdlib + one common lib if needed. If a lib is required name it.

Constraints: Python 3, one file, no comments that restate the code.

HARD LIMIT: 70 lines.
```

### Expected result & local LLM time — Balanced

**Expected result:** one runnable file. Cap ≤700 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **12 s** | ~21 s blank |
| Full answer | — | **90 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Fix this sketch that resets every 10s.

### Prompt (copy / paste)

```text
Board: Pico. Symptom: resets ~10s after WiFi connect.

CODE
[PASTE]

1) Most likely cause, 5 lines
2) Patched function only
3) How I confirm

Do not rewrite unrelated files.

HARD LIMIT: 90 lines of code + 8 lines of why.
```

### Expected result & local LLM time — Heavy

**Expected result:** cause + patched function. Cap ≤1100 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **18 s** | ~32 s blank |
| Full answer | — | **2.5 min** | frozen spinner past that |

### Local LLM time summary — Technical Hobbyist

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 350 | 8 s | 40 s |
| Balanced | 700 / turn | 12 s | 90 s |
| Heavy | 1100 / turn | 18 s | 2.5 min |

Split Heavy into two turns if the first answer hits the cap.

