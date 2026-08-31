# Analyst & Finance Professional — 3 AI Assistance Examples

Not a coding role. The job is **judgment on numbers**: briefs, analysis, models, memos, and QC with AI chat + spreadsheets.

Light turn → balanced pack → heavy memo with sources, sensitivities, and a human who still owns the figure.

---

## Agents in the room

- **Maya** — FP&A analyst who closes the books and writes the Monday variance note
- **Rafi** — senior finance partner who reviews packs before they hit a VP
- **Lin** — hiring manager who has seen AI invent a 14% margin that never existed

**Maya:** Light is a *clean turn on numbers you already have*. Explain a variance, draft the email, list the three questions. If the model makes up a benchmark, you failed the light test.

**Rafi:** Balanced is a *pack*: bridge, drivers, next-month implication, and a tab the model is not allowed to touch. AI drafts; you tie to source.

**Lin:** Heavy is a memo someone will wire money or headcount on. Sources, sensitivities, “what would change my mind,” and every invented figure marked dead. Analyst & Finance Professional means you *progress the analysis*, not that you paste a chatbot paragraph into the deck.

They locked these three.

### Local LLM clock — this role wants the number back, not a novel

Same hardware as the other files: **10–20B Q4 in VRAM**, ~**20–40 tok/s**. Different patience.

An analyst sending a 6-sentence miss note will not wait like a developer waiting for a race-condition fix. They *will* wait a bit longer than a creator if the model is structuring a bridge. They will not wait for a 1,500-token “strategic narrative.”

| Tier | Output cap | Why this wait |
| --- | --- | --- |
| Light | **200–300 tokens** | Six sentences + 3 questions. Must be fast. |
| Balanced | **450–650 tokens** / turn | Bridge *or* one-pager *or* red-team. |
| Heavy | **800–1100 tokens** / turn | Memo from pasted outputs only. |

---

## How this role actually uses AI

| Tool type | What the analyst uses it for |
| --- | --- |
| AI chat | Structure, bridges, “what else could this be,” memo drafts, QA questions, sensitivity design |
| Spreadsheet | Source of truth — actuals, formulas, scenarios. AI does not own the workbook |
| Data / filings / bank exports | Inputs you attach or paste. Model may not “recall” a 10-K from memory as fact |
| Human | Materiality, politics of the number, sign-off, what gets sent upstairs |

**Standing rule for every prompt in this file:**  
If a figure is not in the pasted data, write `[MISSING]` or `[ASSUME — flag]`. Never fill a gap with a confident fake.

---

## 1. Light — one turn that ships the Monday note

**Job:** Revenue missed plan by $420k. You have the three driver lines. You need a 6-sentence note to your manager and 3 follow-up questions. Ten minutes. Chat only.

### Chat prompt (copy / paste)

```text
You are my FP&A desk partner, not a storyteller.

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
```

### What a good light output looks like

```text
NOTE
July revenue was $3,780k vs $4,200k plan (−$420k, −10.0%).
Volume is $310k of the miss: 1,840 orders vs 2,050 planned.
Price/mix is another $70k, from a heavier self-serve mix.
FX is $40k, USD vs EUR.
Gross margin held at 41.2% vs 41.0% plan, so this is not a unit-cost problem.
I will confirm August pipeline with Sales Ops by Wednesday before we reset forecast.

QUESTIONS
1) How many of the missing 210 orders slipped to August vs lost?
2) Was the self-serve mix a campaign choice or demand?
3) Is the EUR book hedged for August or still open?

DO NOT SEND
“Despite a challenging macro environment we outperformed on profitability and expect a full recovery in August.”
```

### Light ritual

1. Paste only numbers you tied to the file.  
2. Send the note.  
3. Ask the three questions.  
4. Do **not** ask the model for “a more executive version” that adds adjectives and deletes the $420k.

**What this shows:** you can brief facts, structure, and a forbidden sentence in one shot. Light analyst work.

### Expected result & local LLM time — Light

**Expected result:** 6-sentence note + 3 questions + do-not-send line. Cap: **≤300 tokens**. Add: `Max 220 words. No extra analysis.`

| Clock | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token | 1–4 seconds | **7 seconds** | 12 s blank |
| Full answer | 8–18 seconds | **30 seconds** | **45 seconds** |

---

## 2. Balanced — own one pack end-to-end

**Job:** Q2 opex is $180k over plan. VP wants a one-pager: bridge, “is it run-rate,” and a recommendation. Spreadsheet stays yours. Chat structures and stress-tests.

### Step A — Chat: design the bridge before you write prose

```text
You are building the skeleton of an opex pack. Do not write the email yet.

PASTED ACTUALS ($000)
                Plan    Actual    Var
People          1,420   1,490     +70
Contractors       180     245     +65
Software          210     240     +30
Travel             90     105     +15
Facilities        160     160       0
Other             140     140       0
Total opex      2,200   2,380    +180

NOTES I KNOW
- People: 2 backfills hired in May, not in plan (≈$18k/mo × 2 mo ≈ $36k) + overtime $34k
- Contractors: data-migration project slipped; $40k is one-time, $25k looks ongoing
- Software: added product-analytics seats in April; will renew
- Travel: two unplanned on-sites; not repeating in Q3 as of today
- Headcount plan was 42; we exited Q2 at 44

DELIVER
1) Waterfall order (largest controllable first)
2) Split every line into one-time vs run-rate. If you cannot split from my notes, mark [SPLIT NEEDED]
3) Q3 run-rate estimate = Q2 actual minus one-time, plus anything that continues
4) 5 diligence questions ranked by $ impact
5) Stop. Do not recommend cut vs keep yet.
```

### Step B — You in the workbook (AI does not do this)

- New tab: `Q2 opex bridge`  
- Columns: Plan | Actual | Var | One-time | Run-rate | Source cell  
- People overtime tied to payroll export  
- Contractor PO list, not a vibe  

### Step C — Chat: write the one-pager from *your* split

```text
Use ONLY this split I just typed. Do not re-split.

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

Voice: calm, specific, no “leverage / synergy / optimize the cost base.”
```

### Step D — Chat: red-team your own pack

```text
Attack this one-pager like the VP who owns the budget.

- Which number is most likely wrong?
- What would Sales or Eng say I ignored?
- What happens to the recommendation if overtime is actually $10k not $34k?
Reply in 8 bullets. No pep talk.
```

### Balanced ritual

1. Structure first.  
2. Split one-time vs run-rate in the file *you* control.  
3. Draft from the split.  
4. Red-team.  
5. Send the pack with the source tab, not instead of it.

**What this shows:** sequence, materiality, and a model that is not allowed to re-invent the bridge. Balanced finance work.

### Expected result & local LLM time — Balanced

**Expected result per turn:** bridge *or* one-pager *or* red-team. Cap: **≤650 tokens**. Spreadsheet stays human.

| Clock | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token | 2–6 seconds | **10 seconds** | 18 s blank |
| One structured turn | 20–40 seconds | **70 seconds** | **2 minutes** |

---

## 3. Heavy — decision memo someone will act on

**Job:** Leadership wants a go / no-go on a $1.2M, 12-month vendor platform vs staying in-house. You will not “ask AI if it’s a good idea.” You will make the model hold a **decision file**: facts, model design, sensitivities, and the kill criteria.

### 3.1 Project instructions — paste once into a Chat Project

```text
SYSTEM / PROJECT — VENDOR PLATFORM DECISION FILE
You are the analyst’s challenge partner. You do not sell the deal. You do not kill the deal for sport.

HARD RULES
1) Every $ figure must cite: PASTED / MODEL / [ASSUME — flag] / [MISSING].
2) Never use a remembered market CAGR, valuation multiple, or “typical SaaS payback.”
3) If I paste two numbers that conflict, stop and show the conflict. Do not average them quietly.
4) Recommendations are structured as: Decision / Conditions / What would flip it.
5) After any memo draft, append a “Numbers the CFO will ask for” list.

CANON FOR THIS FILE (update only when I say CANON UPDATE)
- Decision: buy Vendor X platform vs keep in-house tooling
- Cash outlay if buy: $1.20M year 1 (license $0.80M + implementation $0.40M)
- In-house run-rate I own: $0.46M/year people + $0.09M tools = $0.55M
- Implementation: 5 months, 2 internal FTEs borrowed (costed at $12k/mo each = $120k, already inside the $0.40M? — FLAG)
- Benefits claimed by vendor (UNVERIFIED): 30% cycle-time cut, 1.5 FTE avoided in year 2
- Discount rate we use internally: 10%
- Horizon: 3 years, no terminal value unless I add one
- Currency: USD
```

### 3.2 Session 1 — force the model design before the essay

```text
Do not write the memo.

Design a 3-year cash model with these rows only:
- License
- Implementation (cash)
- Internal borrowed FTE (if not already in implementation — resolve the FLAG)
- In-house cost avoided
- FTE avoided (year 2–3 only, and only if I later confirm the 1.5)
- Net cash
- Cumulative cash
- Simple payback month
- NPV at 10%

For each row: include? Y/N, timing, and PASTED vs [ASSUME — flag].
List 6 sensitivities (low / base / high) I must run in the sheet.
Then stop.
```

### 3.3 You in the workbook (non-negotiable)

Build `vendor_x_3yr.xlsx` yourself:

- Inputs tab (yellow)  
- Base / Downside / Upside  
- Toggle: “1.5 FTE avoided = ON/OFF”  
- Implementation double-count check  
- Output: payback, NPV, year-3 cumulative  

AI may propose formulas. You type them. You still own circular refs and the FTE rate.

### 3.4 Session 2 — memo from *model outputs you paste*

```text
PASTED MODEL OUTPUTS (base)
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
If you reach for a stat I did not paste, write [MISSING] and continue.
```

### 3.5 Session 3 — pre-meeting interrogation

```text
I present this in 12 minutes to a CFO who hates vendor ROI slides.

Give me:
1) The 8 questions they will ask, in likely order
2) A 20-second spoken opener that states recommendation + NPV + the flip toggle
3) The one chart I should show (describe axes — I will build it)
4) A short “if I am wrong” paragraph I can say out loud without looking weak
```

### 3.6 What you refuse to outsource (Lin’s list)

- The source file and the reconciling tick  
- Any figure that will be repeated in a board deck  
- Tax, lease accounting, or “the accountant said it’s fine”  
- Peer multiples you did not pull  
- A recommendation that only exists because the model sounded confident  
- Pasting a chatbot paragraph that contains a number you did not check  

**What this shows:** you can run a decision file — assumptions, model, memo, interrogation — and keep every dollar labeled. Heavy analyst work.

### Expected result & local LLM time — Heavy

**Expected result per turn:** model rows *or* memo from pasted outputs *or* 8 questions. Cap: **≤1100 tokens**. Never “write the IC memo and the model” in one shot.

| Clock | Target | **Max this role still accepts** | Feels broken |
| --- | --- | --- | --- |
| First token | 3–8 seconds | **15 seconds** | 25 s blank |
| One heavy turn | 40–80 seconds | **2.5 minutes** | **3.5 minutes** |

### Local LLM time summary — Analyst (not the other roles)

| Tier | Output cap | First token max | Full answer max |
| --- | --- | --- | --- |
| Light | 300 tokens | 7 s | **30 s** |
| Balanced | 650 tokens | 10 s | **70 s** |
| Heavy | 1100 tokens | 15 s | **2.5 min** |

---

## Prompt patterns this role should keep in a swipe file

| Pattern | When | One-line shape |
| --- | --- | --- |
| Facts block first | Every turn | “FACTS (do not add any others)” |
| `[MISSING]` law | Always | “If you lack it, write [MISSING]. Do not estimate quietly.” |
| Split then prose | Variances | “One-time vs run-rate first. No email until I split.” |
| Red-team | Before send | “Attack this like the VP who owns the budget.” |
| Model before memo | Decisions | “Design rows and sensitivities. Do not write the essay.” |
| Paste outputs | Heavy | “Use ONLY these model outputs.” |
| Flip toggle | Committees | “What would change the sign of NPV?” |
| Forbidden sentence | Light notes | “Give me the version I should not send.” |

---

## Portfolio / interview proof

| Level | What to show | What a lead looks for |
| --- | --- | --- |
| Light | Anonymized variance note + the facts block | You can explain a miss without poetry |
| Balanced | Bridge tab + one-pager + red-team notes | You separate one-time from run-rate |
| Heavy | Decision memo + input tab + “what flips it” | You will not bless a vendor slide |

Strip company names. Keep the structure. One clean pack beats a folder of AI essays titled `strategic insights`.

---

## Lin’s close

Light proves you can put a miss in six true sentences.  
Balanced proves you can own a bridge and a recommendation.  
Heavy proves you can hold a decision file until a CFO can attack it.

Analyst & Finance Professional is not “person who asks AI for insights.”  
It is **person who will not let a fluent paragraph outrun a tied number.**
