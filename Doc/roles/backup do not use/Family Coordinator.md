# Family Coordinator — Light / Balanced / Heavy playbook

**Job of this role (who hits send):** Coordinate people, constraints, and times — allergies and pickups included.

Hardware is shared. Patience is not.

---

## Agents in the room

- **Maya** — uses the local model between other tasks
- **Rafi** — owns one artifact end-to-end
- **Lin** — will reject slop, invented facts, and essays

**Maya:** Light is who / when / don’t.

**Rafi:** Balanced is a weekend with two cars and one constraint that cannot slip.

**Lin:** Heavy is a conflict board. Inventing a babysitter is a fail.

They locked Light / Balanced / Heavy below.

### Local LLM clock — this role waits like a list-maker, not a developer

Same box for every pack: **10–20B Q4_K_M fully in VRAM**, 12–16 GB class GPU, plan **20–40 tok/s**. Prefill 1–4 s short / 5–15 s long paste. RAM offload voids the clock. Chat only — no image or video generate waits.

Missed peanut ban is an IF fail. They will not sit through a family-systems essay.

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | **250 tokens** | 6 s | **25 s** |
| Balanced | **500 tokens** / turn | 8 s | **50 s** |
| Heavy | **850 tokens** / turn | 12 s | **2 min** |

---

## 1. Light

**Job:** Thu 6pm game, no peanuts in snacks.

### Prompt (copy / paste)

```text
Update the family card.

KEEP
- Thu 6:00pm soccer, field B
- Kid A peanut allergy — no peanuts in any snack

CHANGE
- Snack duty this week: parent 2

Write 5 lines max: who / when / where / snack / allergy.
Do not add activities.

HARD LIMIT: 100 words.
```

### Expected result & local LLM time — Light

**Expected result:** 5-line card, allergy still present. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Job:** Saturday with two pickups, one car 11–2.

### Prompt (copy / paste)

```text
Build Sat 9–5 for two kids.

FACTS
- Kid A soccer 11:00–12:15 field B
- Kid B birthday party 12:00–2:00, 4 miles from field B
- One car 11:00–2:00
- Parent 2 is free after 1:30

Table: time | person | place | car.
If both events overlap with one car write [WON'T FIT] and one option.

HARD LIMIT: 200 words.
```

### Expected result & local LLM time — Balanced

**Expected result:** table + one [WON'T FIT] if needed. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Job:** Week conflict board from pasted calendars.

### Prompt (copy / paste)

```text
Merge these two calendars. Do not add events.

PARENT 1
[PASTE]
PARENT 2
[PASTE]
KIDS
[PASTE]

Output:
1) Shared week grid
2) Conflicts only
3) Questions I must answer (max 4)

HARD LIMIT: 300 words.
```

### Expected result & local LLM time — Heavy

**Expected result:** grid + conflicts + questions. Cap ≤850 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 3–10 s | **12 s** | ~21 s blank |
| Full answer | — | **2 min** | frozen spinner past that |

### Local LLM time summary — Family Coordinator

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 250 | 6 s | 25 s |
| Balanced | 500 / turn | 8 s | 50 s |
| Heavy | 850 / turn | 12 s | 2 min |

Split Heavy into two turns if the first answer hits the cap.

