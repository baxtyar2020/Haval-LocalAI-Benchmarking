# Haval LocalAI Bench — Final Report Requirements

## 1. Purpose

This document defines the final reporting requirements for evaluating how well a hardware configuration supports different local LLM sizes and models.

The report must answer:

> **What size and type of local LLM can this hardware run well for the people who will actually use it?**

The report is not a generic model leaderboard. It evaluates each **hardware + model + quantization + workload** combination and identifies:

- the practical LLM-size range for the hardware;
- the best general-purpose model range;
- the highest-capability model that remains practical;
- where customer experience begins to degrade;
- the best tested model for Consumer customers;
- the best tested model for Gaming customers;
- the best tested model for Commercial customers;
- how every tested model performs for every persona under Light, Balanced, and Heavy workloads.

## 2. Normative Final Format and Design Reference

The following HTML report is the **final example for report format, visual design, information hierarchy, cards, tables, colors, spacing, and responsive behavior**:

**[Haval-Hardware-First-LLM-Fit-Report.html](../haval-hardware-first-report-example/Haval-Hardware-First-LLM-Fit-Report.html)**

The HTML example must be used as the visual baseline when implementing or generating the production report.

- This Markdown document is authoritative for product requirements, calculation rules, required data, terminology, and report behavior.
- The HTML example is authoritative for the final presentation format and design.
- If a visual interpretation is unclear in this document, follow the HTML example.
- If a calculation or data rule differs from a hypothetical value shown in the example, follow this requirements document and the measured benchmark data.
- All values marked hypothetical in the example must be replaced with actual benchmark values in a production report.

## 3. Core Product Principles

### 3.1 Start with the hardware

The tested system is the anchor of the report. Every conclusion must describe the fit of a particular model configuration on that exact hardware.

The same model may be an Excellent Match on one system and only Acceptable, Marginal, Not Recommended, or Failed on another system.

### 3.2 Recommend an operating envelope

The report must describe a practical range, not merely name one model or report whether a model loaded.

The range must identify:

1. Fast / Light zone
2. Balanced Sweet Spot
3. High-Capability zone
4. Stretch / Out-of-Range zone

### 3.3 Do not use parameter count alone

Nominal parameter count is insufficient to determine hardware suitability. The report must consider:

- total parameters;
- active parameters;
- dense versus Mixture-of-Experts architecture;
- quantization;
- actual model-file size;
- runtime memory consumption;
- VRAM or unified-memory allocation;
- KV-cache and context requirements;
- operating headroom;
- generation speed;
- time to first token;
- total customer-task completion time;
- quality;
- reliability;
- load failure, timeout, OOM, swap, or instability.

### 3.4 Recommend independently by business

There must be no universal “best overall model” recommendation.

The report must select an independent best-match model for:

- **Consumer**
- **Gaming**
- **Commercial**

The strongest model can differ by business because the personas, quality needs, response-time expectations, and workload distributions differ.

### 3.5 Measure human experience

A fast but incorrect answer must not win. A very high-quality answer with unusable latency must not win. A model that loads but leaves no safe hardware headroom must not be presented as a healthy fit.

Quality, response experience, reliability, and hardware fit must all influence the final result.

## 4. Required Inputs

| ID | Input group | Required fields | Use |
|---|---|---|---|
| DATA-01 | System identity | Product name, form factor, stable machine identifier | Headline and hardware context |
| DATA-02 | CPU | Vendor, model, cores, threads, architecture | Hardware panel and CPU-offload context |
| DATA-03 | GPU or accelerator | Name, quantity, VRAM or unified allocation, backend | Acceleration and memory boundary |
| DATA-04 | System memory | Total capacity, type, speed, unified/discrete status | Model envelope and headroom |
| DATA-05 | Model identity | Clean model name, family, architecture, total and active parameters | Comparison and model cards |
| DATA-06 | Model package | Quantization, exact model bytes, context setting | Practical capacity calculation |
| DATA-07 | Performance | Generation speed, TTFT, load time, memory used, host memory | Experience and hardware scoring |
| DATA-08 | Quality | Applicable quality dimensions and evaluator results | Scenario and persona scoring |
| DATA-09 | Reliability | Attempts, successes, OOM, timeout, invalid output, instability | Reliability and failure gates |
| DATA-10 | Scenario | Business, persona, intensity, prompt, rubric, timing targets | Workload-level evaluation |

Calculations must use exact unrounded values. Round only values displayed to the customer.

Source benchmark values must not be silently corrected, replaced, reconciled, or invented.

## 5. Model Identity and Roster Rules

- Remove repeated trailing size aliases from displayed names.
- Preserve the underlying source name in raw data.
- Distinguish dense models from Mixture-of-Experts models.
- Show total and active parameters when active parameters are available.
- Show quantization and exact model bytes.
- Do not infer model bytes from nominal parameters when measured bytes exist.
- Keep missing, failed, timed-out, or OOM models visible when they are part of the expected roster.
- Do not invent measurements for failed models.
- Exclude GPT-20B from this report family.

When present, use this model order:

1. Gemma4-26B
2. Qwen3-30B
3. Kimi-48B
4. Qwen3-80B
5. GPT-120B

The report logic must support any number of models. A three-model report is only a hypothetical example.

## 6. Hardware Capacity Zones

The capacity ranges must be derived from the tested hardware, quantization, context configuration, and measured results. They are not universal parameter-size promises.

| Zone | Meaning | Required interpretation |
|---|---|---|
| Fast / Light | Large performance and memory headroom | Fast assistants, summaries, and lightweight interaction |
| Balanced Sweet Spot | Best overall balance | Strong quality, natural speed, stability, and deployment headroom |
| High Capability | Usable with visible tradeoffs | Higher quality or reasoning may justify slower response |
| Stretch / Out of Range | Loads poorly, runs inefficiently, or fails | Not appropriate for dependable daily use |

The report must explain that two models with similar total parameters can behave differently because of architecture, active parameters, quantization, model bytes, and memory movement.

## 7. Business and Persona Taxonomy

Personas describe recurring work patterns and AI needs. They do not represent demographics.

### 7.1 Consumer

| Persona | Typical work | General AI need | Common quality emphasis |
|---|---|---|---|
| Everyday Organizer | Schedules, reminders, notes, household plans | Fast organization and clear next steps | Instruction following, structured output |
| Student & Learner | Study, practice, assignments | Patient explanations and tutoring | Accuracy, reasoning, math |
| Family Coordinator | Calendars, travel, meals, activities, purchases | Practical plans and comparisons | Instruction following, structure |
| Researcher & Shopper | Product research and option comparison | Evidence synthesis and recommendation logic | Accuracy, reasoning |
| Writer & Communicator | Emails, applications, documents, social content | Drafting, editing, and tone control | Creative writing, instruction following |
| Creative Prosumer | Stories, concepts, videos, and presentations | Ideas, refinement, and consistency | Creative quality, instruction following |
| Personal Adviser | Choices, routines, goals, travel, and wellness | Balanced and understandable guidance | Reasoning, accuracy, safety |
| Technical Hobbyist | PCs, scripts, electronics, and projects | Troubleshooting and usable examples | Problem solving, coding, instructions |

### 7.2 Gaming

| Persona | Typical work | General AI need | Common quality emphasis |
|---|---|---|---|
| Casual Gamer | Casual play, tips, settings, recommendations | Quick and simple game guidance | Accuracy, response speed |
| Power Player | Demanding games, builds, strategy, optimization | Deep and rapid high-volume assistance | Reasoning, accuracy, latency |
| Progressive Creator | Videos, streams, clips, scripts, social posts | Creative planning and audience adaptation | Creative writing, instruction following |
| Rising Game Developer | Small games, prototypes, mechanics, simple code | Beginner-friendly coding and debugging | Coding, problem solving, structured output |

### 7.3 Commercial

| Persona | Typical work | General AI need | Common quality emphasis |
|---|---|---|---|
| Executive & Decision Maker | Strategy, risk, performance, business cases | Concise synthesis and recommendations | Reasoning, accuracy, instruction following |
| Project & Operations Manager | Plans, owners, deadlines, risks, execution | Actions, status, risks, structured artifacts | Structured output, instruction following |
| Engineer & Software Developer | Systems, code, defects, tests, documentation | Correct code and technical reasoning | Coding, problem solving, JSON |
| Analyst & Finance Professional | Numbers, forecasts, data, spreadsheets | Accurate math and traceable assumptions | Math, accuracy, structured output |
| Research & Product Professional | Customers, markets, technology, requirements | Evidence synthesis and product insight | Reasoning, accuracy, structure |
| Sales & Marketing Professional | Campaigns, proposals, presentations, messaging | Positioning and personalized variants | Creative quality, instruction following |
| Customer Support Specialist | Questions, diagnosis, cases, resolutions | Fast, accurate troubleshooting with empathy | Accuracy, instructions, latency |
| People, Legal & Compliance | Policies, obligations, controls, careful review | Precise extraction and cautious comparison | Accuracy, instruction following, structure |

## 8. Workload Intensity

Every persona must be evaluated with three workload levels.

### 8.1 Light

- Short context
- Simple instructions
- Minimal reasoning or transformation
- Short output
- Typical first-response expectation: approximately 1–2 seconds
- Typical total-response expectation: approximately 10–30 seconds

### 8.2 Balanced

- Moderate context
- Multiple instructions
- Comparison, synthesis, or multi-step work
- Medium-length output
- Typical first-response expectation: approximately 2–4 seconds
- Typical total-response expectation: approximately 30–120 seconds

### 8.3 Heavy

- Long context
- Complex reasoning, coding, analysis, or structured generation
- Several constraints
- Longer output
- Typical first-response expectation: approximately 3–8 seconds
- Typical total-response expectation: approximately 2–10 minutes, depending on the scenario

Each scenario must store its own acceptable TTFT and total-response target. The ranges above are defaults for design guidance, not universal pass/fail limits.

## 9. Quality Dimensions

Only dimensions relevant to a scenario receive weight. Applicable weights must sum to 1.00.

| Dimension | What it measures |
|---|---|
| Accuracy | Factual correctness, faithful extraction, grounded claims, and absence of material hallucination |
| Reasoning | Sound analysis, relationships, conclusions, and appropriate explanation depth |
| Math | Correct calculations, formulas, units, intermediate logic, and numerical consistency |
| Coding and Problem Solving | Correct, runnable, maintainable solutions; debugging and technical completeness |
| Instruction Following | Compliance with constraints, tone, scope, length, ordering, and exclusions |
| Structured Output / JSON | Valid schema, required fields, correct types, stable and parseable formatting |
| Creative Writing | Originality, coherence, tone, audience fit, and style consistency when applicable |

Creative Writing is particularly applicable to Writer & Communicator, Creative Prosumer, Progressive Creator, and Sales & Marketing scenarios.

## 10. Scoring Equations

### 10.1 Scenario quality

```text
Q[p,w] = Σ(α[i] × q[i]), where Σα[i] = 1
```

Where:

- `q[i]` is the score for an applicable quality dimension;
- `α[i]` is its scenario-specific weight;
- `p` is the persona;
- `w` is Light, Balanced, or Heavy.

### 10.2 Response-time normalization

```text
r = actual response time / acceptable response time

g(r) = 100                         when r ≤ 1
g(r) = 100 × 2^−(r−1)             when r > 1
```

Calculate separate ratios for TTFT and total response time.

### 10.3 Customer response experience

```text
E[L] = 0.45 × g(TTFT ratio) + 0.55 × g(total-time ratio)
E[B] = 0.35 × g(TTFT ratio) + 0.65 × g(total-time ratio)
E[H] = 0.25 × g(TTFT ratio) + 0.75 × g(total-time ratio)
```

Total completion time receives greater importance as task intensity increases.

### 10.4 Reliability

```text
R[w] = 100 × successful runs / attempted runs
```

### 10.5 Workload match

```text
W[p,w] = Q[p,w]^0.60 × E[p,w]^0.30 × R[w]^0.10
```

This is a geometric score. Strength in one dimension cannot completely hide a severe weakness in another.

### 10.6 Persona overall

```text
P[p] = 0.25 × W[L] + 0.40 × W[B] + 0.35 × W[H]
```

Balanced work receives the highest weight because it best represents meaningful daily use. Heavy work remains highly influential so strong Light performance cannot hide poor complex-task performance.

### 10.7 Business fit

```text
B[b,m] = Σ(ω[p] × P[p,m]), where Σω[p] = 1
```

Where:

- `b` is Consumer, Gaming, or Commercial;
- `m` is the tested model;
- `ω[p]` is the importance weight of the persona within that business.

Aggregate numeric persona scores. Never average labels or colors.

### 10.8 Global hardware-model suitability

```text
S[m] = 100 × (Q/100)^0.40 × (E/100)^0.35 × (H/100)^0.25
```

Where:

- `Q` is overall model quality;
- `E` is customer response experience;
- `H` is measured hardware fit.

This global suitability score answers whether the model-and-hardware pairing is healthy overall. It does not replace persona or business scores.

### 10.9 Business winner

```text
Winner[b] = arg max B[b,m] for all qualified models m
```

Select the best qualified model independently within each business.

## 11. Categories

| Exact numeric result | Category | Meaning |
|---:|---|---|
| 90–100 | Excellent Match | Preferred configuration for the evaluated scope |
| 80–89.9 | Strong Match | Dependable and recommended with manageable tradeoffs |
| 70–79.9 | Acceptable Match | Usable, but limitations are visible |
| 60–69.9 | Marginal Match | Runs, but efficiency or experience is weak |
| Below 60 | Not Recommended | Quality, experience, or hardware fit is insufficient |
| Non-numeric | Failed | Model or scenario did not complete |

Categories must be selected using exact unrounded values. Round only the displayed score.

A displayed score rounded to `90` may correctly remain Strong Match when its exact value is below 90.

## 12. Gates and Protection Rules

### 12.1 Global hardware-suitability gates

- Missing result, load failure, OOM, timeout, or incomplete representative scenario → **Failed**.
- Quality below 55 or Hardware Fit below 40 → **Not Recommended**.
- Severe swapping or unstable execution → category cannot exceed **Marginal Match**.
- Representative customer task longer than 15 minutes → category cannot exceed **Marginal Match**.
- Quality below 65 → category cannot exceed **Acceptable Match**.

### 12.2 Persona and business protection rules

- A failed Heavy workload cannot be hidden by good Light performance.
- Minimum persona coverage is required before issuing a business category.
- A critical persona failure may cap the business result.
- A business winner must be chosen only from qualified completed models.
- Failed workloads use em dashes for unavailable scores.
- The report must preserve the evidence-backed failure reason.

### 12.3 Failed versus unsuitable

- **Failed** means the model or test did not complete because of OOM, timeout, load failure, runtime failure, or another operational problem.
- **Not Recommended** means the model completed but its calculated quality, experience, or hardware fit is insufficient.
- **Marginal Match** means the model runs, but efficiency or customer experience is weak.

## 13. Approved Realistic Customer Scenario

Use one consistent customer task to make model response time understandable:

> A user provides the content of a medium-length, 10-page report and asks the model to produce a detailed, well-structured answer that summarizes and simplifies the report and clearly identifies the key takeaways.

The report must visually present:

```text
10-PAGE CONTENT → AI MODEL → KEY INSIGHTS
```

Use document, AI-chip, and lightbulb icons.

Every completed model must display its estimated time for the same task. Failed models display no invented time.

## 14. Required Final Report Structure

The production report must follow the structure and visual treatment demonstrated in `Haval-Hardware-First-LLM-Fit-Report.html`.

### 00 — Executive Hardware Verdict

- Dynamic title: `Evaluation of <Product Name> against Different LLM Sizes`
- Best general-purpose parameter range
- Highest practical capability range
- Stretch or out-of-range boundary
- Measured or hypothetical disclosure

### 01 — Tested Hardware Configuration

Show exactly four primary tiles:

1. System
2. GPU + VRAM
3. CPU
4. System Memory

Use device-aware inline SVG icons. Do not show OS or Power Mode tiles.

### 01A — Realistic Customer Scenario

- Show the approved 10-page task.
- Show `10-page content → AI model → key insights`.
- Use the approved document, AI-chip, and lightbulb visual composition.

### 02 — LLM Capacity Envelope

- Fast / Light
- Balanced Sweet Spot
- High Capability
- Stretch / Out of Range
- Associate tested models with their capacity zones.

### 03 — Best Model by Business

Show three independent winner cards:

- Consumer winner in teal
- Gaming winner in purple
- Commercial winner in blue

Do not show an overall recommended model.

### 04 — Tested-Model Evidence Table

Required columns:

- Model
- Architecture
- Total / Active Parameters
- Quantization
- Model Bytes
- Memory Used
- Generation Speed
- TTFT
- Customer Task Time
- Hardware Zone
- Suitability Category

### 04A — Final Verdict Response-Time Table

Required columns:

- Model
- Generation Speed
- TTFT
- Estimated Time in Seconds
- Estimated Time in `min:sec`
- Suitability Category

Use exact performance values for calculations. Do not display the internal token-estimation formula in the report.

### 05 — Business Match Matrix

Required columns:

- Model
- Total / Active Parameters
- Consumer Final Match
- Gaming Final Match
- Commercial Final Match
- Recommended Use

Do not include a universal overall score, rank, or winner column.

### 06 — Selected Sweet-Spot Model Drill-Down

Show:

- model name and family;
- dense or MoE architecture;
- total parameters;
- active parameters;
- quantization;
- model footprint;
- Quality score;
- Experience score;
- Hardware Fit score;
- Reliability;
- global suitability score and category;
- observed memory and available headroom.

This card supports the hardware-first conclusion. It is not the starting point of the report.

### 07 — Persona Workload Tables for Every Tested Model

Create one complete table for every tested model.

Each model block must contain:

- model name;
- architecture;
- total and active parameters;
- quantization;
- short profile description;
- Consumer final result;
- Gaming final result;
- Commercial final result;
- a complete persona table.

Each completed model table must contain these columns:

| Business | Persona | Light | Balanced | Heavy | Overall | Final Match |
|---|---|---:|---:|---:|---:|---|

Requirements:

- All 20 personas must appear for every completed model.
- Persona ordering must remain identical across model tables.
- Each completed model produces 60 workload results and 20 persona-overall results.
- Every table is calculated independently.
- A persona can be Excellent on one model and Marginal on another.
- No model may inherit scores or categories from another model.
- Failed values display em dashes.
- A completely failed model shows its model header and a failure inset instead of a fabricated table.

### 08 — Scoring Equation Card

- Use the dark premium card style shown in the HTML example.
- Show quality, timing normalization, experience, reliability, workload, persona, business, hardware suitability, and winner equations.
- Keep explanations concise.
- Do not show the internal realistic-task token-count formula.

### 09 — Persona Reference Table

Required columns:

- Business
- Persona
- Typical day-to-day work
- What the persona generally needs from AI

State that personas describe task patterns rather than demographics.

## 15. Section 07 Scaling Behavior

| Situation | Required behavior |
|---|---|
| Three completed models | Render three full 20-persona tables |
| Five completed models | Render five tables in prescribed model order |
| Model failed entirely | Keep model header; show failure reason and em dashes |
| One workload failed | Keep persona row; mark failed intensity; apply coverage gate |
| Model is slow but completes | Reduce Experience and match category; do not call it Failed |
| Model is fast but inaccurate | Quality weighting and gates prevent an inflated result |

## 16. Prompt and Scenario Traceability

Every workload result must be traceable to a scenario record containing:

- scenario ID and version;
- business;
- persona;
- workload intensity;
- complete prompt;
- input context or attachment reference;
- applicable quality dimensions;
- quality weights;
- expected-answer requirements;
- evaluator rubric;
- acceptable TTFT;
- acceptable total time;
- attempt count;
- success criteria;
- raw output;
- raw timings;
- evaluator evidence;
- error or failure details.

Example:

```json
{
  "scenarioId": "GAM-RGD-H-001",
  "business": "Gaming",
  "persona": "Rising Game Developer",
  "intensity": "Heavy",
  "prompt": "Create and explain a small game mechanic...",
  "qualityWeights": {
    "coding": 0.40,
    "reasoning": 0.25,
    "instructionFollowing": 0.20,
    "structuredOutput": 0.15
  },
  "targets": {
    "ttftSeconds": 5,
    "totalSeconds": 240
  },
  "attempts": 3
}
```

## 17. Visual Design Requirements

Follow `Haval-Hardware-First-LLM-Fit-Report.html` as the final design reference.

### 17.1 Visual character

- Elegant and premium
- Calm and easy to scan
- Editorial rather than dashboard-heavy
- Apple-style simplicity and whitespace
- Warm, human, and experience-led
- Rounded cards and restrained shadows
- Serif headlines with clean sans-serif body text

### 17.2 Color system

| Purpose | Color |
|---|---|
| Page background | Warm ivory `#F6F1E9` |
| Primary text | Near black `#201E1C` |
| Primary Haval accent | Burnt orange `#DC4D18` |
| Consumer | Teal `#247F79` |
| Gaming | Purple `#79519A` |
| Commercial | Blue `#3F6797` |
| Excellent Match | Green `#2F774B` |
| Strong Match | Blue/teal `#39748B` |
| Acceptable Match | Gold/amber `#A8731F` |
| Marginal Match | Violet `#745486` |
| Not Recommended | Red `#A74733` |
| Failed | Dark neutral gray |

Meaning must never depend on color alone. Always display the text category.

### 17.3 Technical presentation

- Produce one self-contained HTML file.
- Do not require external fonts, scripts, images, or network access.
- Use inline SVG for icons.
- Make the report responsive.
- Allow wide tables to scroll horizontally on small screens.
- Make the report printable.
- Avoid clipping category pills and table labels.
- Preserve readable contrast.
- Keep business colors consistent throughout every section.
- Use the term **Commercial**, never Enterprise.

## 18. Required Failure Presentation

When a model or workload fails:

- keep the model in the expected order;
- show its parameter badge when known;
- use an em dash instead of a numeric score;
- label the state **Failed**;
- display the evidence-backed reason;
- do not invent performance, quality, persona, or business values;
- do not silently omit the failed item.

When the only evidence is a missing expected result, use:

> **Failed — Failed to run the LLM model.**

## 19. Final Acceptance Checklist

### Data and calculation

- [ ] Every expected non-excluded model appears exactly once in comparison sections.
- [ ] Every tested model has a Section 07 persona table or failure inset.
- [ ] All 20 personas appear in consistent order for every completed model.
- [ ] Light, Balanced, Heavy, Overall, and Final Match are present.
- [ ] Scenario-appropriate quality dimensions are normalized.
- [ ] Response-time scoring uses scenario-specific acceptable targets.
- [ ] Exact unrounded values determine categories and winners.
- [ ] Reliability, quality, timing, stability, hardware, and coverage gates are applied.
- [ ] Consumer, Gaming, and Commercial winners are selected independently.
- [ ] No universal best-model recommendation appears.
- [ ] Failed data is never replaced with invented values.

### Report structure and experience

- [ ] The hardware verdict appears before model detail.
- [ ] The LLM capacity envelope is clear.
- [ ] Dense/MoE, total/active parameters, quantization, and bytes are visible.
- [ ] Hardware headroom is distinguished from “the model loaded.”
- [ ] The realistic 10-page customer scenario is included.
- [ ] The final response-time table is included.
- [ ] Business colors remain consistent.
- [ ] Categories use the approved six-state taxonomy.
- [ ] Failed values use em dashes and include a reason.
- [ ] Tables remain usable on smaller displays.
- [ ] The report works completely offline.
- [ ] The report prints cleanly.
- [ ] Persona definitions are included.
- [ ] Measured versus hypothetical status is explicit.
- [ ] The finished report visually follows `Haval-Hardware-First-LLM-Fit-Report.html`.

## 20. Final Product Principle

The strongest report is not the one with the most measurements. It is the one that lets a customer look at a hardware configuration and confidently understand:

- which LLM sizes fit;
- which exact model best serves each business;
- which personas and workloads are well supported;
- where the experience begins to degrade;
- whether a model is merely slow, genuinely unsuitable, or operationally failed;
- and why the report reached each conclusion.
