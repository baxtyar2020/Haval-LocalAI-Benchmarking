# Family Coordinator — Customer Chat Pack (text-in / text-out)

Pack name: **Customer Chat Pack**  
Rule: **text-in / text-out** — they type a question; the model answers with text in the reply. No tools, no folders on disk, no execution, no image or video generate waits.

## Role description

This customer coordinates people, constraints, and times — allergies and pickups included. They paste calendars and hard rules and want a card, a table, or a conflict board. Inventing a babysitter or dropping an allergy is a fail.

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

**Ask / scenario:** Thursday soccer stays, snack duty changed, peanut allergy stays. They are asking the AI for a five-line family card that keeps the allergy and adds no extra activities.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Light

**Expected result:** 5-line card, allergy still present. Cap ≤250 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 s | **6 s** | ~10 s blank |
| Full answer | — | **25 s** | ~1.5× that, still going |

---

## 2. Balanced

**Ask / scenario:** Two kids have overlapping Saturday events and only one car for part of the day. They are asking the AI for a time table and a [WON'T FIT] call if the car cannot cover both.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

### Expected result & local LLM time — Balanced

**Expected result:** table + one [WON'T FIT] if needed. Cap ≤500 tokens.

| Clock | Target | Max this role still accepts | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 s | **8 s** | ~14 s blank |
| Full answer | — | **50 s** | ~1.5× that |

---

## 3. Heavy

**Ask / scenario:** Two parents and the kids have separate calendars pasted in. They are asking the AI to merge them, list only real conflicts, and ask at most four questions — no invented babysitter.

### What they type

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

### What a good text answer looks like

The reply stays on one artifact, uses only pasted facts, and never asks to run, install, render, or open a tool. See expected result below.

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

## Quick score (text only)

| | Pass | Fail |
| --- | --- | --- |
| Light | 5-line card keeps allergy and snack duty | Drops peanut ban or adds events |
| Balanced | Sat table + [WON'T FIT] if one car cannot cover | Invented second car or sitter |
| Heavy | Merged grid + conflicts + questions only | Adds events not in calendars |

Every item is scored as **text-in / text-out**. A later human run is a second scorecard, not this pack.

---

Skill version: **role-task-playbooks 1.3** · Customer Chat Pack · text-in / text-out · Ask / scenario required on every tier.
