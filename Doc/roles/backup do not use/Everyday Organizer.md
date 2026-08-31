# Everyday Organizer — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Keep a household day moving — lists, reminders, what moved.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is five lines I can glance at while locking the door.

**Rafi:** Balanced is tonight’s plan with times that do not collide.

**Lin:** Heavy is a week board. Still not a novel. Invented errands are a fail.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role wants the list now

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

They will not wait like an engineer. If the list takes a minute they wrote it themselves.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **250 tokens** | 6 s | **25 s** |
| Balanced | **500 tokens** / turn | 8 s | **45 s** |
| Heavy | **800 tokens** / turn | 12 s | **90 s** |

---

## 1. Light

**Job:** Move soccer, add milk, do not drop the dentist.

### Prompt (copy / paste)

```text
You keep my day list. Do not invent errands.

NOW
- Thu 6:00pm dentist (keep)
- Need milk
- Soccer moved from Sat 9am to Sat 11am

Write:
1) Today list, max 6 bullets, time first
2) One line: what changed
3) One line I should put on the fridge

HARD LIMIT: 120 words. No preamble. No tips.
```

### Expected result & local LLM time — Light

**Expected result:** 6 bullets + change line + fridge line. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Plan dinner-to-bed for two kids, 90 minutes, one bathroom.

### Prompt (copy / paste)

```text
Plan 5:30–7:00pm for two kids, one bathroom, one oven.

CONSTRAINTS
- Pasta bake needs 25 min in oven
- Baths cannot overlap
- Homework 15 min each

Output a 6-row table: time | who | where | doing.
If something does not fit write [WON'T FIT] instead of stretching time.

HARD LIMIT: 180 words. No pep talk.
```

### Expected result & local LLM time — Balanced

**Expected result:** 6-row schedule. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **45 s** | ~1.5× that |

---

## 3. Heavy

**Job:** One-week board from pasted events only.

### Prompt (copy / paste)

```text
Build a Mon–Sun board from ONLY these events:
- Mon 8am school
- Wed 4pm dentist (kid A)
- Sat 11am soccer
- Sun 2pm grandparents

Columns: day | must | flexible | note.
Do not add chores I did not list.
Mark conflicts [CONFLICT].

HARD LIMIT: 280 words. One table.
```

### Expected result & local LLM time — Heavy

**Expected result:** week table, no invented chores. Cap ≤800 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **90 s** | frozen spinner past that |

### Local LLM time summary — Everyday Organizer

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 250 | 6 s | 25 s |
| Balanced | 500 / turn | 8 s | 45 s |
| Heavy | 800 / turn | 12 s | 90 s |

Split Heavy into two turns if the first answer hits the cap.

