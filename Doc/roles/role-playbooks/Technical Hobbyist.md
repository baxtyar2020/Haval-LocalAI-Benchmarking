# Technical Hobbyist — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer wants a small project unstuck — an error explained, a 20-line script, or a patched function. They copy the snippet and run it themselves. Chat must not flash a board, install a toolchain, or rewrite the whole repo.

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

**Ask / scenario:** A hobby project threw an error on a pasted line. They are asking the AI what that error means in plain language, not to run the code.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 6-line why + patch. Cap ≤350 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **8 s** | ~14 s blank |
| Full answer | — | **40 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** They want a small script for one job they will run later. They are asking the AI to write that short script in the chat and not set up their machine.

### What they type

```text
Write one file.

JOB: read a folder of .wav names and print duration seconds using stdlib + one common lib if needed. If a lib is required name it.

Constraints: Python 3, one file, no comments that restate the code.

HARD LIMIT: 70 lines.
```

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** one runnable file. Cap ≤700 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **12 s** | ~21 s blank |
| Full answer | — | **90 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Their sketch resets every ten seconds and they pasted it. They are asking the AI what is wrong and what the fixed sketch should say in the reply.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

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

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 6-line why + smallest patch | Tutorial or extra libraries |
| Balanced | One runnable file for the job | Framework rewrite |
| Heavy | Cause + patched function only | Rewrites unrelated files or flashes the board |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
