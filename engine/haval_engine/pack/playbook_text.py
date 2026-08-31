"""Phase 1 prompts copied from Doc/roles/role-playbooks with [PASTE] filled in."""

from __future__ import annotations

STUDENT_PARA = (
    "Photosynthesis is how green plants make food. They take in carbon dioxide from air "
    "and water from roots. Sunlight hitting chlorophyll drives a reaction that builds glucose. "
    "Oxygen is released as a byproduct. The glucose stores chemical energy the plant can use later."
)

STUDENT_NOTES = (
    "Lecture: cells get energy from food. ATP is the energy currency. Mitochondria run aerobic "
    "respiration. Glycolysis is the first anaerobic step in the cytosol. The Krebs cycle follows "
    "in the matrix. Oxygen is the final electron acceptor. NADH carries electrons. Do not confuse "
    "this with photosynthesis in chloroplasts."
)

HEADSET_FACTS = (
    "H1 BoomMic USB: boom mic, USB-A, mute LED, $89, 280g.\n"
    "H2 AirBuds: no boom, Bluetooth only, $59, no mute light.\n"
    "H3 StudioX USB: boom mic, USB-C, no mute light, $139.\n"
    "H4 DeskLite: boom mic, USB-A, mute LED, $119, 310g."
)

SHOP_PASTE = (
    "Opt1 City Hatch $18,400, AWD, 32 mpg, source line 12.\n"
    "Opt2 Compact EV $27,900, FWD, 220 mi, source line 18.\n"
    "Opt3 Used wagon $12,200, AWD, 140k miles, source line 22."
)

WRITER_DRAFT = (
    "We missed the 12 May ship date by 4 days. Two engineers were out. The client still wants "
    "the 3pm review on Thursday. I am furious this slipped."
)

WRITER_FACTS = (
    "Ship slipped 4 days. Review stays Thursday 3pm. Owner: Priya. No discount offered. "
    "Next build Friday 10am."
)

WRITER_NOTES = (
    "Audience: hiring manager at a regional paper. Piece: 600-word personal statement later. "
    "Notes: interned at Harbor Lab summer 2024; GPA 3.6; edited campus weekly; no Rhodes; "
    "lived at 14 Oak Street junior year."
)

HOBBY_ERR = (
    "TypeError: can only concatenate str (not \"int\") to str\n"
    "  File \"app.py\", line 12, in show\n"
    "    print(\"score: \" + n)"
)

HOBBY_CODE = "n = 7\nprint(\"score: \" + n)\n"

PICO_CODE = (
    "while True:\n"
    "    wlan.connect(ssid, password)\n"
    "    time.sleep(10)\n"
    "    print(wlan.ifconfig())\n"
    "    # never sleeps after connect; watchdog bites ~10s\n"
)

SUPPORT_POLICY = (
    "Refunds within 30 days of delivery to original payment method. No cash. "
    "Store credit only if the item is unopened and within 14 days. Day 41 is out of policy. "
    "Escalate if the customer cites a written promise from a named agent."
)

SUPPORT_TICKET = (
    "Order 4419 delivered March 1. Today is April 11 (day 41). Customer wants store credit "
    "for a used keyboard. Serial not in ticket. Tone: polite but firm."
)

EXEC_METRICS = (
    "Revenue $12.4M vs $11.9M plan. Gross margin 41.2%. Vendor delay 3 weeks. "
    "Ask: two QA contractors through Oct 15. Budget left $42k."
)

EXEC_DECISION = (
    "Hire a 3-month contractor vs freeze the workstream until internal owner is at 0.6 FTE."
)

LEGAL_SOURCE = (
    "Employees must give 30 days written notice. Garden leave may apply. "
    "Do not discuss pending investigations with the press."
)

LEGAL_CONSTRAINTS = (
    "Keep the 30-day notice. Do not add a non-compete. Manager audience, not counsel."
)

LEGAL_TEXT = (
    "Clause 4: Vendor shall notify Customer within 10 days of a security incident. "
    "Clause 12: Customer may audit on 10 days notice. Clause 19: venue Delaware. "
    "Clause 4 vs 19 do not mention employees."
)

LEGAL_DOC = (
    "Master services agreement. Effective 2026-01-15. Governing law Delaware. "
    "Audit rights clause 12: 10 days notice. Retention of logs 2 years. "
    "No unlimited liability cap stated."
)

LEGAL_Q = "What must we do before an audit, and what is missing on liability?"

ADVISER_Q = "Keep the 2018 car two more years versus buy used at or under $18k."

ADVISER_FACTS = (
    "Car is paid off. Last year repairs $1,400. Commute 12 miles. No lender quotes yet."
)

ADVISER_QUOTES = (
    "\"I can float $400/month.\" \"Winter tires are shot.\" "
    "\"Bus is not an option on Sundays.\" \"I will not finance junk.\""
)

POWER_NAMES = "Jett, Sage, Phoenix, Brimstone, Harbor"

POWER_PATCH = (
    "Jett dash cooldown +2s. Sage slow orb +1s. Phoenix curveball unchanged. "
    "Brim stim beacon heal -10. Harbor wall duration -1s."
)

POWER_STATS = (
    "Rifle: 30 dmg body, 0.9s ADS. SMG: 18 dmg, 0.4s ADS. Shotgun: 15x8, 1.2s ADS. "
    "Armor 50. Sprint 5.8 m/s. Goal: burst."
)

PMO_MESS = (
    "Ava will send the deck Friday maybe. Ben has the risk log but no date. "
    "API vendor slipped. Launch still marked June. Nobody named for billing."
)

PMO_TASKS = "Send deck; update risk log; vendor call; freeze scope; billing checklist"

PMO_NOTES = (
    "Billing must work before launch. API delay makes status amber. Ava owns the deck. "
    "Ben owns the risk log. Vendor call Monday. Assumption: June date still real."
)

RP_NOTES = (
    "Comment A: Search is fine. Comment B: export to CSV is missing. "
    "NPS 32. Quote: \"We would pay for SSO.\" Theme counts: Export 14, Search 3."
)

RP_JOB = "When I close the month, I want to export the report to CSV so finance can load it."

RP_EVIDENCE = "14 tickets tagged Export. SSO mentioned in 9 interviews. No blockchain requests."

RP_RESULTS = "CSV export prototype: 12 of 15 testers completed unassisted. Time-on-task 4.2 min."

RP_HYP = "If we ship CSV, finance tickets drop 30% next quarter."

SALES_CLAIMS = (
    "Ships in 5 days. Setup under 30 minutes. Email support, business hours. "
    "Slip-resistance per approved lab note. No #1 claim. No discount."
)

SALES_NOTES = (
    "Objection: too expensive. Phrase: \"budget locked.\" Answer from notes: 5-day ship "
    "cuts downtime. Objection: support weekends. [MISSING]. No case study on file."
)

FAMILY_P1 = "Mon 9-5 office. Wed 4pm dentist kid A (drive). Fri 7pm dinner."
FAMILY_P2 = "Tue remote. Thu 6pm soccer field B snack duty. Sat off."
FAMILY_KIDS = "Mon-Fri school 8am. Sat 11am soccer. Sun 2pm grandparents."

NORTH_LAMP_EP = (
    "CANON: North Lamp. Nara, silver streak behind LEFT ear, scar through LEFT eyebrow, "
    "gold chain, olive jacket. Rainy port city.\n"
    "EPISODE 04 brief: Nara waits for a ferry that never shows; she leaves before the rain "
    "gets worse. New canon (approve?): dented steel thermos — treat as YES for this turn.\n"
    "Give: 4-frame board (A setup / B wait / C decision / D leave); continuity vs a prior "
    "episode; image prompts A-D; I2V for Frame C (3 seconds, one gesture); QC: streak side, "
    "scar side, chain, jacket, thermos dent.\n"
    "HARD LIMIT: 700 words. One line per shot. No novel. NOT IN CANON if you invent a brand."
)


def fill(template: str, **subs: str) -> str:
    out = template
    for k, v in subs.items():
        out = out.replace(k, v)
    return out


# --- Instantiated playbook prompts (Light / Balanced / Heavy per role) ---

C_EO_L = """You keep my day list. Do not invent errands.

NOW
- Thu 6:00pm dentist (keep)
- Need milk
- Soccer moved from Sat 9am to Sat 11am

Write:
1) Today list, max 6 bullets, time first
2) One line: what changed
3) One line I should put on the fridge

HARD LIMIT: 120 words. No preamble. No tips."""

C_EO_B = """Plan 5:30–7:00pm for two kids, one bathroom, one oven.

CONSTRAINTS
- Pasta bake needs 25 min in oven
- Baths cannot overlap
- Homework 15 min each

Output a 6-row table: time | who | where | doing.
If something does not fit write [WON'T FIT] instead of stretching time.

HARD LIMIT: 180 words. No pep talk."""

C_EO_H = """Build a Mon–Sun board from ONLY these events:
- Mon 8am school
- Wed 4pm dentist (kid A)
- Sat 11am soccer
- Sun 2pm grandparents

Columns: day | must | flexible | note.
Do not add chores I did not list.
Mark conflicts [CONFLICT].

HARD LIMIT: 280 words. One table."""

C_SL_L = fill(
    """Explain ONLY the paragraph I paste. Do not add outside facts.

PARAGRAPH
[PASTE]

Write:
1) 5 bullets, plain words
2) 1 sentence I would write in the margin
3) 1 word I should look up — only if it is in the paragraph

HARD LIMIT: 160 words. No preamble.""",
    **{"[PASTE]": STUDENT_PARA},
)

C_SL_B = fill(
    """From NOTES only, write 5 quiz items.
3 recall, 2 “why”.
After each item put the answer in one line starting ANSWER:

NOTES
[PASTE]

If the notes do not support an item, skip it. Do not invent.

HARD LIMIT: 220 words.""",
    **{"[PASTE]": STUDENT_NOTES},
)

C_SL_H = fill(
    """Make a study sheet from NOTES only.

Sections:
- Must know (max 6)
- Why it matters (max 3)
- Likely test traps (max 3)
- [MISSING] lines for anything I asked that is not in the notes

NOTES
[PASTE]

HARD LIMIT: 320 words. No extra chapters.""",
    **{"[PASTE]": STUDENT_NOTES},
)

C_FC_L = """Update the family card.

KEEP
- Thu 6:00pm soccer, field B
- Kid A peanut allergy — no peanuts in any snack

CHANGE
- Snack duty this week: parent 2

Write 5 lines max: who / when / where / snack / allergy.
Do not add activities.

HARD LIMIT: 100 words."""

C_FC_B = """Build Sat 9–5 for two kids.

FACTS
- Kid A soccer 11:00–12:15 field B
- Kid B birthday party 12:00–2:00, 4 miles from field B
- One car 11:00–2:00
- Parent 2 is free after 1:30

Table: time | person | place | car.
If both events overlap with one car write [WON'T FIT] and one option.

HARD LIMIT: 200 words."""

C_FC_H = fill(
    """Merge these two calendars. Do not add events.

PARENT 1
[P1]
PARENT 2
[P2]
KIDS
[K]

Output:
1) Shared week grid
2) Conflicts only
3) Questions I must answer (max 4)

HARD LIMIT: 300 words.""",
    **{"[P1]": FAMILY_P1, "[P2]": FAMILY_P2, "[K]": FAMILY_KIDS},
)

C_RS_L = """Compare ONLY these three. Do not add models.

A: 14-inch, 16GB, $899, 1.3kg
B: 14-inch, 32GB, $1299, 1.4kg
C: 16-inch, 16GB, $1099, 1.8kg

Need: travel, 16GB min, budget $1100.

Table: name | RAM | weight | price | fit? (yes/no + 3 words)
Then one line: cheapest that fits, or [NONE].

HARD LIMIT: 140 words."""

C_RS_B = fill(
    """I will buy one. Use FACTS only.

FACTS
[PASTE]

Must: mic boom, USB, under $120.
Want: mute light.

Write:
- Winner + 2 lines why (cite facts)
- Runner-up + 1 line
- Rejects + 1 line each
- [MISSING] if a must is not in FACTS

HARD LIMIT: 200 words.""",
    **{"[PASTE]": HEADSET_FACTS},
)

C_RS_H = fill(
    """Build a 4-row shortlist from PASTE only.
Columns: option | price | must-haves hit | deal-breaker | source line.
Then 4 reject rules I should keep next time.

If PASTE has fewer than 4 options, do not invent rows.

PASTE
[PASTE]

HARD LIMIT: 280 words.""",
    **{"[PASTE]": SHOP_PASTE},
)

C_WC_L = fill(
    """Rewrite DRAFT in VOICE. Do not add facts.

VOICE: dry, specific, no slogans, no emoji.
MAX: 80 words.
Keep every number that is already in DRAFT.

DRAFT
[PASTE]

HARD LIMIT: 80 words of output + 1 line word count.""",
    **{"[PASTE]": WRITER_DRAFT},
)

C_WC_B = fill(
    """Same FACTS. Three pieces:
1) email subject + 3-line body
2) Slack, max 40 words
3) 1-sentence status

FACTS
[PASTE]
VOICE: calm, no hype.

Do not add a metric that is not in FACTS.

HARD LIMIT: 180 words total.""",
    **{"[PASTE]": WRITER_FACTS},
)

C_WC_H = fill(
    """Audience: hiring manager at a regional paper
Piece: personal statement
Length target: 600 words later, not now.

From NOTES only:
1) 6-header outline
2) Write ONLY header 1, max 120 words
3) [MISSING] for holes

NOTES
[PASTE]

Do not write the full piece.

HARD LIMIT: 280 words this turn.""",
    **{"[PASTE]": WRITER_NOTES},
)

C_CP_L = """Asset: 8s clip of a desk lamp turning on.
Audience: makers, 20–35.
Write 3 captions, different angle (utility / mood / mistake).
Max 12 words each. No emoji. No “unlock”.

HARD LIMIT: 80 words."""

C_CP_B = """Write text only. Do not render.

STILL PROMPT
- 4:5 photo, warm lamp left, cold monitor right
- product: black headset on stand
- rejects: extra fingers, readable fake logos, watermark

Then:
- IG line ≤80 chars
- YT title ≤50 chars

HARD LIMIT: 160 words."""

C_CP_H = """I have Sat morning. One piece: “repair a scratch on a desk” timelapse.

Write:
1) 5-beat shot list (SEE / HEAR only)
2) 1 still-prompt for the thumbnail
3) 1 caption
4) 3 things I will not do (scope)

HARD LIMIT: 260 words. No gear I did not name."""

C_PA_L = """Decision: keep the 2018 car 2 more years vs buy used ≤$18k.

FACTS I HAVE
- Car paid off
- Last year repairs $1,400
- Commute 12 miles

Write:
- Option A / B, 3 lines each
- What I must still find out (max 4)
- Do not recommend a lender or a diagnosis

HARD LIMIT: 180 words."""

C_PA_B = fill(
    """Build a card.

QUESTION: [Q]
FACTS: [F]

Sections:
- What is already decided
- Two paths
- Kill this plan if…
- [MISSING]

No medical/legal/tax rules unless they appear in FACTS.

HARD LIMIT: 220 words.""",
    **{"[Q]": ADVISER_Q, "[F]": ADVISER_FACTS},
)

C_PA_H = fill(
    """Use QUOTES only.

QUOTES
[PASTE]

Write:
1) Situation in 4 lines
2) Options (max 3)
3) Tradeoffs table
4) What I am not qualified to decide here

HARD LIMIT: 320 words. Two turns if longer.""",
    **{"[PASTE]": ADVISER_QUOTES},
)

C_TH_L = fill(
    """Explain this error in 6 lines. Then the smallest change.

LANG: Python 3
ERROR
[ERR]
CODE
[CODE]

No tutorial. No extra libraries.

HARD LIMIT: 160 words + a short patch.""",
    **{"[ERR]": HOBBY_ERR, "[CODE]": HOBBY_CODE},
)

C_TH_B = """Write one file.

JOB: read a folder of .wav names and print duration seconds using stdlib + one common lib if needed. If a lib is required name it.

Constraints: Python 3, one file, no comments that restate the code.

HARD LIMIT: 70 lines."""

C_TH_H = fill(
    """Board: Pico. Symptom: resets ~10s after WiFi connect.

CODE
[PASTE]

1) Most likely cause, 5 lines
2) Patched function only
3) How I confirm

Do not rewrite unrelated files.

HARD LIMIT: 90 lines of code + 8 lines of why.""",
    **{"[PASTE]": PICO_CODE},
)

G_CG_L = """I have 90 minutes. I like cozy or light co-op. I own: Stardew, Overcooked 2, Rocket League.

Give 3 picks, 8 words of why each. No new titles I must buy.

HARD LIMIT: 80 words."""

G_CG_B = """Game: Stardew. I have 20 minutes before bed.
Tell me exactly what to do in 6 steps. No lore.

HARD LIMIT: 120 words."""

G_CG_H = """Game: Stardew. Window: Sat 2–5pm. Goal: have fun, not min-max.
Plan 3 blocks of 50 min + 10 min break.
Each block: one goal I can finish.

HARD LIMIT: 180 words."""

G_PP_L = fill(
    """Tier these ONLY: [NAMES].
Patch: [PATCH]
Rows: S / A / B / C / leave-out.
One reason each, max 8 words, tied to the paste.

HARD LIMIT: 140 words.""",
    **{"[NAMES]": POWER_NAMES, "[PATCH]": POWER_PATCH},
)

G_PP_B = fill(
    """STATS
[PASTE]
Goal: burst
Give: 6 item/skill slots + 1 sentence why each.
Do not add stats not in PASTE. Use [MISSING].

HARD LIMIT: 200 words.""",
    **{"[PASTE]": POWER_STATS},
)

G_PP_H = fill(
    """MAIN: Jett
PATCH NOTES (paste)
[PASTE]

1) Buffs / nerfs that touch MAIN
2) Drop / keep / try — 3 lines
3) One thing I should test in 10 games

HARD LIMIT: 240 words. No invented winrates.""",
    **{"[PASTE]": POWER_PATCH},
)

G_CR_L = """You are my short-form editor, not a hype bot.

CLIP CONTEXT
- 12s vertical clip: clean desk, monitor glow, hands drop a headset onto a stand
- Audience: PC gamers and creators, 18–34
- Tone: calm, specific, zero “unlock your potential”
- Must not invent specs I didn’t give

TASK
1) Write 5 hooks (max 8 words each). Each hook must be a different angle:
   curiosity / sensory / mistake / status / utility
2) Write 1 caption (max 120 characters) + 3 hashtags that are actually used, not junk
3) Write 1 image-model prompt for a thumbnail that matches the clip
   - 9:16
   - same mood as “warm lamp + cold monitor”
   - no readable fake logos, no extra fingers, no watermark

FORMAT
Hooks:
1. ...
Caption:
...
Thumbnail prompt:
...

After the three blocks, add 2 lines only:
- Weakest hook and why
- One detail the thumbnail must keep consistent with the clip

HARD LIMIT: 280 words total. No preamble."""

G_CR_B = """You are a creative producer sitting next to me. Do not write ads. Write a shoot brief.

PRODUCT
- Over-ear gaming headset, matte black, subtle green accent ring on the cup
- We sell “late-session comfort,” not RGB fireworks

AUDIENCE
- People who stream or edit after midnight, not arena-finals fantasy

CONSTRAINTS
- No celebrity lookalikes
- No readable UI on screens
- No invented awards, dB numbers, or “used by pros”
- Talent is one adult, mid-20s, any gender, hoodie, tired-but-focused face
- Room: small apartment studio, practical lamps, not a warehouse set

DELIVER
1) Logline (1 sentence)
2) 30-second beat sheet (6 beats, each beat = what we SEE + what we HEAR)
3) 3 must-keep visual rules (identity of the product)
4) 3 automatic rejects (common AI mistakes for this scene)
5) Then wait. Do not write social copy yet.

HARD LIMIT: 400 words. No preamble."""

G_CR_H = NORTH_LAMP_EP

B_ED_L = """QUESTION: hire contractor 3 months vs freeze the workstream.
FACTS
- Budget left $42k
- Need date Oct 15
- Internal owner at 0.3 FTE

Write 3 options, 2 lines each, then 1 recommend line.
Do not invent a vendor name or a date.

HARD LIMIT: 160 words."""

B_ED_B = fill(
    """METRICS (do not add)
[PASTE]

Page:
- What changed
- So what
- Options (max 3)
- Ask of me
- [MISSING]

HARD LIMIT: 240 words.""",
    **{"[PASTE]": EXEC_METRICS},
)

B_ED_H = fill(
    """DECISION: [D]
FACTS: [F]

1) Go looks like
2) No-go looks like
3) Kill this in 30 days if…
4) What I am not deciding today

HARD LIMIT: 300 words.""",
    **{"[D]": EXEC_DECISION, "[F]": EXEC_METRICS},
)

B_PO_L = fill(
    """Turn this mess into 5 rows: item | owner | date | status | note.
MESS
[PASTE]
If a field is unknown write [MISSING]. Do not invent an owner.

HARD LIMIT: 140 words.""",
    **{"[PASTE]": PMO_MESS},
)

B_PO_B = fill(
    """Workstream: Launch
People: Ava, Ben, vendor
Tasks: [T]

Table: task | R | A | C | I
One person in A per task. If you cannot tell, [MISSING].

HARD LIMIT: 200 words.""",
    **{"[T]": PMO_TASKS},
)

B_PO_H = fill(
    """NOTES
[PASTE]

Four lists: Risks | Assumptions | Issues | Dependencies
Each line: statement | owner | date if any | [MISSING] if none
Do not add items not implied by NOTES.

HARD LIMIT: 280 words.""",
    **{"[PASTE]": PMO_NOTES},
)

B_AF_L = """You are my FP&A desk partner, not a storyteller.

FACTS (do not add any others)
- Month: July
- Revenue plan: $4,200k
- Revenue actual: $3,780k
- Variance: −$420k (−10.0%)
Drivers I already pulled:
  1) Volume: −$310k (orders 1,840 vs plan 2,050)
  2) Price / mix: −$70k (more self-serve, less premium)
  3) FX: −$40k (USD stronger vs EUR)
- Gross margin still 41.2% vs plan 41.0% (not the issue)
- Pipeline for August looks on plan per sales ops Slack — I have not verified

TASK
1) Write a 6-sentence manager note:
   - sentence 1 = the miss in $ and %
   - sentences 2–4 = the three drivers, largest first
   - sentence 5 = what is NOT the problem (margin)
   - sentence 6 = what I will confirm by Wednesday
2) Give me 3 questions I should ask Sales, in plain language
3) Give me 1 sentence I should NOT send (the version that over-claims)

RULES
- No “headwinds / tailwinds / unpack / unpacking”
- No industry benchmark unless I pasted one
- If you want a number I did not give, write [MISSING]
Max 220 words. No extra analysis."""

B_AF_B = """Use ONLY this split I just typed. Do not re-split.

One-time: contractors $40k + travel $15k = $55k
Run-rate add: people $70k + contractors $25k + software $30k = $125k
Implied Q3 opex if we do nothing extra: $2,200k plan + $125k = $2,325k
[MISSING] exact overtime hours — payroll file still open

Write a one-pager in this exact shape:

HEADLINE (≤18 words, must include $180k and the run-rate $)
BRIDGE (5 bullets, $ on every line)
RUN-RATE (4 sentences)
RECOMMENDATION (keep / cut / watch — one choice per line: people, contractors, software, travel)
WATCHOUTS (3; include the [MISSING] overtime item)

Voice: calm, specific, no “leverage / synergy / optimize the cost base.”"""

B_AF_H = """PASTED MODEL OUTPUTS (base)
- Payback: 28 months
- NPV @ 10%, 3 years, no TV: −$140k
- Year-1 net cash: −$1.20M
- Year-2 net cash: +$0.48M
- Year-3 net cash: +$0.58M
- Downside (no FTE avoided): payback > 36 months, NPV −$410k
- Upside (FTE avoided + cycle time actually used to skip a $200k contractor): NPV +$90k

VENDOR CLAIM STATUS
- 30% cycle time: [UNVERIFIED] — process owner has not signed
- 1.5 FTE: [UNVERIFIED] — no named roles

Write the decision memo in this shape:

TITLE
RECOMMENDATION (Go / No-go / Go-if) in 2 sentences, include NPV and payback
WHY THIS IS NOT OBVIOUS (the toggle that flips the sign)
CASH BRIDGE (year by year, pasted numbers only)
CONDITIONS PRECEDENT if Go-if (max 4, each testable)
KILLS (2 events that mean we stop even after signing)
APPENDIX ASK (the two [UNVERIFIED] items and who owes them by when)

Tone: investment committee, not vendor webinar.
If you reach for a stat I did not paste, write [MISSING] and continue."""

B_RP_L = fill(
    """From NOTES only.

NOTES
[PASTE]

Write:
- Problem in 2 sentences
- Evidence (bullet per quote or metric in NOTES)
- Open questions (max 4)
- [MISSING]

HARD LIMIT: 180 words.""",
    **{"[PASTE]": RP_NOTES},
)

B_RP_B = fill(
    """Job story I want: [J]
Evidence: [E]

Write:
1) User / job / circumstance
2) In-scope (max 5)
3) Out-of-scope (max 5)
4) Acceptance checks (max 5)
No roadmap fiction.

HARD LIMIT: 240 words.""",
    **{"[J]": RP_JOB, "[E]": RP_EVIDENCE},
)

B_RP_H = fill(
    """RESULTS
[R]
HYPOTHESIS
[H]

Log:
- What we thought
- What we measured (only pasted numbers)
- What we did not measure
- Keep / drop / rerun
- [MISSING]

HARD LIMIT: 300 words. No p-values you cannot see.""",
    **{"[R]": RP_RESULTS, "[H]": RP_HYP},
)

B_SM_L = """CLAIMS (do not add)
1) Ships in 5 days
2) Setup under 30 minutes
3) Email support, business hours

Audience: ops manager, mid-market.
80 words max. No awards, no “#1”.

HARD LIMIT: 80 words."""

B_SM_B = fill(
    """CLAIMS: [C]
Day 0 / Day 3 / Day 7
Each: subject ≤50 chars + 4-line body.
Do not add a discount unless it is in CLAIMS.

HARD LIMIT: 220 words.""",
    **{"[C]": SALES_CLAIMS},
)

B_SM_H = fill(
    """NOTES
[PASTE]

Table: objection | exact phrase if any | answer from NOTES | [MISSING] if we have no answer
Max 6 rows. No invented case studies.

HARD LIMIT: 260 words.""",
    **{"[PASTE]": SALES_NOTES},
)

B_CS_L = """POLICY: Refunds within 30 days of delivery, original payment method, no cash.
Customer: “Can I get store credit on day 41?”
Write the reply, 6 lines max. If policy does not allow it, say so. No extra goodwill promise.

HARD LIMIT: 90 words."""

B_CS_B = fill(
    """POLICY
[P]
TICKET
[T]

Output:
- Reply (max 120 words)
- Status
- Reason code
- Next action
Use [MISSING] if the ticket lacks a fact.

HARD LIMIT: 180 words.""",
    **{"[P]": SUPPORT_POLICY, "[T]": SUPPORT_TICKET},
)

B_CS_H = fill(
    """POLICY
[PASTE]

Write 4 macros: allow / deny / need-more-info / escalate
Each: when to use (1 line) + text (max 70 words)
Do not invent a policy branch.

HARD LIMIT: 320 words.""",
    **{"[PASTE]": SUPPORT_POLICY},
)

B_PLC_L = fill(
    """SOURCE
[S]
CONSTRAINTS I MUST KEEP
[C]

Rewrite for a manager audience.
If a constraint cannot be kept in plain language, quote it.
Do not add a rule.

HARD LIMIT: 180 words.""",
    **{"[S]": LEGAL_SOURCE, "[C]": LEGAL_CONSTRAINTS},
)

B_PLC_B = fill(
    """TEXT
[PASTE]

Table: clause | who it binds | trigger | obligation | exception | [MISSING]
Max 8 rows. No new clauses.

HARD LIMIT: 240 words.""",
    **{"[PASTE]": LEGAL_TEXT},
)

B_PLC_H = fill(
    """DOCUMENT
[D]
QUESTION
[Q]

Memo:
- Issues found (cite a line)
- What the document does not say
- Questions for counsel / HR (max 5)
- What I did not decide

HARD LIMIT: 320 words. Not legal advice.""",
    **{"[D]": LEGAL_DOC, "[Q]": LEGAL_Q},
)

G_RD_L_PROMPT = """Can you write a Unity C# script for a simple 2D player?

I want left/right movement, a jump only when they are on the ground, and collecting coins. When they touch a coin, add 1 to a score and print it in the console, then remove the coin.

I already have a player with a Rigidbody2D. Coins are triggers tagged "Coin". I can add a small ground check object at the feet.

Please put the full script in your answer and a short list of what I should hook up in the Inspector. Don't create a Unity project and don't walk me through installing Unity."""

G_RD_B_PROMPT = """I need a Unity C# enemy script.

It should walk back and forth between two points. If the player comes within a detect range, it chases. If the player gets far enough away, it walks back to where it started and then patrols again.

Please use a simple state machine with Patrol, Chase, and Return so I can add Attack later without rewriting it. Put the speeds and ranges as fields I can change in the Inspector. If you can, add gizmos for the two ranges.

One script in the chat is enough. Tell me what to drag onto the component. Don't build a scene for me and don't use NavMesh unless I ask."""

G_RD_H_PROMPT = """My player dash is buggy. If I mash the button I dash twice and go flying. If I dash into a thin wall I end up on the other side.

Here is the script:

void Update() {
    if (Input.GetButtonDown("Jump"))
        StartCoroutine(DashBroken());
}

IEnumerator DashBroken() {
    float facing = Mathf.Sign(transform.localScale.x);
    float t = 0f;
    while (t < dashTime) {
        transform.Translate(Vector3.right * facing * dashSpeed * Time.deltaTime);
        t += Time.deltaTime;
        yield return null;
    }
}

First tell me why both bugs happen. Then write the fixed dash script I can paste over this one.

I want a cooldown so I cannot start another dash while one is running, and I want the move to use the Rigidbody so it stops at walls instead of sliding through them. A short raycast in front each step is fine.

One script in the chat plus a few lines mapping each bug to the fix. Don't ask me to hit Play and report back. Don't add extra systems."""

B_EN_L_ASK = """Can you write a small Python script that scans a folder and finds duplicate files by comparing the actual file contents, not the names?

I want it as a command-line tool I can run later myself. Use only the Python standard library. Hash the files in chunks so big files are okay. If the path I give is not a folder, just print an error.

Please put the full script in your answer and one example of how I would run it. Don't set anything up for me and don't run it."""

B_EN_B_ASK = """I need a small FastAPI service for publish jobs.

Someone posts a job with a platform name and a JSON payload. The API gives back a job id and a status. There should be a GET endpoint to check that job later. Store jobs in a local SQLite file. When a job is created, kick off a background task that just waits a moment and then marks the job as ok — I will replace that wait with a real upload later.

Please show me this as one Python file in the chat: models, database table, POST, GET, and the background task. If the id does not exist, return 404.

Don't start the server. Don't install packages. Don't create files. Just write the code and a few lines on how I would run it myself later."""

B_EN_H_ASK = """We have a bug. Two workers both pick the same queued job and the customer gets two posts.

Here is the claim function:

async def claim_job_broken(jobs):
    for j in jobs:
        if j.status == "queued":
            j.status = "leased"
            return j
    return None

Can you explain what is going wrong? Why can two workers both pass that if? What would a correct claim have to do in one step so only one worker wins?

Please don't write the new code yet. Just explain it in plain language.

Okay, now show me the fixed claim and the worker loop in the chat.

I want one atomic claim, like a single SQL update that leases one row only if it is still queued (or the lease expired), sets a short lease time, and bumps attempts.

Then a worker that: claims a job, tries to publish with exponential backoff, marks ok on success, puts it back in queue on a retryable error, and marks failed on a fatal error.

You can assume a store with methods like fetch_one, mark_ok, mark_failed, release_to_queued. Don't build the whole app. Don't run anything. Just the explanation, the functions, and a short why."""
