# Haval LocalAI Bench — Consolidated Product Requirements Document (PRD)

**Version:** 1.1 · **Date:** August 29, 2026
**Status:** Consolidated requirements baseline — merges and reconciles all nine source documents in `/Doc`. Amended for architecture decisions D-1…D-8 (see companion Build Plan).
**Sources consolidated:**

| # | Source document | Authority |
|---|---|---|
| 1 | Haval-LocalAI-Bench-Application-Overview.md | Product vision and promise |
| 2 | Haval_LocalAI_Bench_Prerequisites_and_Model_Download.md | Doctor, prerequisites, repair, Model Library |
| 3 | Haval_LocalAI_Bench_UI_Design_Baseline.md | Visual/UX baseline for the Windows app |
| 4 | Haval-LocalAI-Final-Report-Requirements.md (+ .html twin) | Final report rules, data, calculations, structure |
| 5 | Haval-Hardware-First-LLM-Fit-Report.html | Normative visual example of the final report |
| 6 | Persona-AI-Match-Scoring-Methodology.docx | Scoring specification (quality, experience, reliability, gates) |
| 7 | Persona-AI-Workload-Quality-Evaluation-Matrix.xlsx | The 60 executable scenarios, rubric, and graders |
| 8 | Persona-AI-Workload-Response-Time-Source-Table.md | Persona TTFT/completion tolerances |
| 9 | Haval LocalAI Bench (standalone).html + Claude Design canvas | Interactive UI mockup (6 screens, Windows 11 frame) |

Where sources differ, this PRD records both and flags the conflict in §14 (Open Issues). Rule of authority: the **requirements documents govern behavior and calculations**; the **HTML report example and the UI mockup govern presentation**.

---

## 1. Product Vision

Haval LocalAI Bench is a self-guided **Windows 11 desktop application** that makes evaluating local AI models simple for anyone. It installs and repairs everything needed (Ollama, runtimes), verifies that hardware acceleration truly works, lets the customer download and select models through a clean graphical Model Library, runs realistic customer-focused benchmarks across 20 personas × 3 workload intensities, and produces an elegant, hardware-first final report.

The purpose is **not** to prove that an LLM can load. It is to determine **which LLM sizes and models genuinely fit the hardware, which customers and workloads they serve well, and where the experience becomes slow, inefficient, unreliable, or unusable.**

**Product promise:** *"From installation to recommendation, Haval LocalAI Bench turns the complexity of local AI into one simple, evidence-based customer experience."*

### 1.1 The final expected experience

1. Install and open the application easily (signed installer; no Python knowledge, PowerShell, terminals, or PATH edits).
2. Let the application (Doctor) inspect and prepare the PC.
3. See whether local AI acceleration is working correctly.
4. Discover, download, and select models through a clean graphical interface.
5. Start the evaluation with minimal decisions.
6. Follow clear progress while models are tested safely and sequentially.
7. Receive an elegant final report explaining exactly which LLM sizes, models, personas, and workloads best fit that hardware.

The outcome is confidence: **the user finishes knowing not only what can run on the PC, but what can run well, for whom, for which work, and why.**

### 1.2 Core product principles

- **Start with the hardware.** The tested system anchors every conclusion; the same model may be Excellent on one PC and Marginal on another. The unit of evaluation is the **model + hardware + quantization + workload** combination, never the model in isolation.
- **Recommend an operating envelope**, not a single winner: Fast/Light zone, Balanced Sweet Spot, High-Capability zone, Stretch/Out-of-Range zone.
- **Never use parameter count alone.** Consider total/active parameters, dense vs MoE, quantization, actual model bytes, runtime memory, VRAM/unified allocation, KV-cache and context, headroom, speed, TTFT, task completion time, quality, and reliability.
- **Recommend independently by business.** No universal "best model." Independent winners for **Consumer**, **Gaming**, and **Commercial** (never "Enterprise").
- **Measure human experience.** A fast but wrong answer must not win; a brilliant but unusably slow answer must not win; a model with no safe headroom is not a healthy fit.
- **Evidence, never invention.** Failed data is never replaced with invented values; source benchmark values are never silently corrected or reconciled.

---

## 2. Platform & Supported Environment

- **OS:** Windows 11 only (already 64-bit; do not present a separate 64-bit requirement). Block unsupported OS with a clear explanation.
- **Runtime:** Ollama is the inference runtime. The local Ollama API (normally `http://127.0.0.1:11434`) must be reachable.
- **Hardware acceleration (vendor-neutral):** NVIDIA/CUDA are NOT mandatory. Support any Windows 11 system where Ollama provides accelerated inference: discrete NVIDIA, discrete AMD, supported Intel GPU, integrated GPU/APU, unified-memory architectures, shared-system-memory GPUs, and any other backend the installed Ollama runtime supports. NVIDIA-specific checks (e.g., `nvidia-smi`) are supplemental and used only when NVIDIA hardware exists. The absence of NVIDIA tooling is never a failure on a non-NVIDIA system.
- **Not customer prerequisites:** Git, LM Studio, vLLM, llama.cpp, cloud APIs, separately installed Python, separately installed CUDA Toolkit.
- **Bundled by the installer:** Python runtime + application dependencies; required Microsoft Visual C++ runtime components (installed when permitted).
- **CPU-only:** The normal benchmark is hardware-accelerated. CPU-only inference must never be silently accepted. A future CPU-only benchmark, if added, is a separate, clearly labeled mode.

---

## 3. Functional Requirements — Installation, Doctor & Repair

### 3.1 Customer experience objective

> Install the signed Windows application, launch it, allow Doctor to prepare and verify the system, select or download models, and start the benchmark.

The customer must never normally need to: open PowerShell/CMD, copy Ollama commands, install Python, repair PATH, start/restart Ollama manually, change execution policies, or diagnose ports/permissions/services/GPU settings. Manual commands may exist for advanced support only.

### 3.1a Installation wizard — Ollama internet check

The Windows **installation wizard** (NSIS / first-run setup) must **detect Ollama before offering any download**.

| Condition | Wizard behavior |
|---|---|
| Ollama is already installed (known locations or a valid executable; not PATH-only) | Skip the Ollama download page. Do not mention the internet. Continue installing Haval LocalAI Bench as usual. |
| Ollama is **not** installed | Show one short page **before** any Ollama download. Require an internet connection for this step only. |

**Customer copy when Ollama is missing** (keep it this short):

- **Title:** Internet needed for Ollama
- **Body:** This PC does not have Ollama yet. Haval LocalAI Bench uses the official Ollama service to run models here. This step downloads the **latest Ollama service**. It is a **small, fast** download. Stay connected until it finishes.
- **Primary action:** Download Ollama
- **Secondary:** I’ll connect later

If the PC is offline and Ollama is missing: **do not start the download**. Explain that they need internet for this one small Ollama update. The Haval app may still be installed; Doctor finishes Ollama when a connection is available.

Do not describe this as a large package, a model download, or a Python install. Official Ollama over HTTPS only; admin approval only if Windows requires it.

### 3.2 Required prerequisites (Doctor verifies all)

| Requirement | Required behavior |
|---|---|
| Windows 11 | Detect; block with clear explanation if unsupported |
| Ollama runtime | Detect existing install or install automatically |
| Ollama executable | Locate in standard or custom locations; never depend only on `PATH` |
| Ollama service/API | Confirm local API availability (normally `127.0.0.1:11434`) |
| Hardware acceleration | Prove via live model probe that inference is not CPU-only when acceleration should exist |
| Storage | Free space ≥ total selected download size + **10 GB operating reserve** |
| Application runtime | Python + dependencies bundled in the installer |
| Windows runtime components | Detect/install required VC++ components when permitted |
| Permissions & security | Detect blocked execution, access denied, quarantine, port conflicts, local security restrictions |

### 3.3 Doctor mode and the readiness gate

- The application starts in **Doctor mode** on first launch. Doctor is the readiness gate.
- **Start Benchmark stays disabled** until: all blocking prerequisites pass; the Ollama API is available; the machine-level acceleration probe passes; at least one model is installed AND selected; no selected model is actively downloading; no required repair is active.
- Each check presents a clear status: **Checking / Passed / Warning / Repairing / Failed / Blocked by policy**.
- Doctor keeps a technical log for support while showing plain-language status and repair guidance.
- Doctor must never silently continue with an invalid CPU-only configuration.

### 3.4 Doctor diagnostic sequence (required workflow)

1. Confirm Windows 11.
2. Detect CPU, GPU, integrated graphics, APU, unified-memory configuration, and system memory.
3. Detect whether Ollama is installed.
4. Locate the Ollama executable, including non-default locations.
5. Install Ollama automatically when missing and permitted.
6. Start or restart Ollama when necessary.
7. Poll the local Ollama API until ready or timeout.
8. Detect available disk space.
9. Inventory all models already installed through Ollama.
10. Select the smallest installed chat model for the machine-level probe.
11. If no suitable model exists, offer or auto-download a small probe model (e.g., `llama3.2:1b` or `gemma3:1b`).
12. Run a short deterministic generation (temperature 0, small output-token limit).
13. Inspect `ollama ps` while the model remains loaded.
14. Confirm full or partial hardware acceleration via Ollama and available platform telemetry.
15. Apply a performance sanity check against a conservative CPU-only range to detect false acceleration reports.
16. Open Model Library after the environment passes.
17. Enable Start Benchmark only after at least one model is installed, ready, and selected.

### 3.5 Vendor-neutral acceleration probe

**Purpose:** prove Ollama is actively using available acceleration and has not silently fallen back to CPU-only. Not every model must report `100% GPU`.

**Acceptable:** full GPU; GPU+CPU split from partial offload; unified-memory acceleration; shared-system-memory acceleration; iGPU/APU acceleration; normal CPU participation in loading/tokenization/scheduling. System RAM or unified memory holding model data while the GPU computes must NOT be misclassified as CPU-only.

**Probe result classification:**

| Observed result | Doctor decision |
|---|---|
| Fully GPU-accelerated | Pass |
| Meaningful GPU acceleration with some CPU offload | Pass with information notice |
| iGPU/APU/shared/unified-memory acceleration | Pass |
| Limited vendor telemetry but Ollama reports acceleration and performance supports it | Pass with verification details |
| Model too large; predominantly/entirely CPU | Fail that model; recommend smaller model or quantization |
| CPU-only although supported acceleration should be available | Fail; open automated repair flow |
| No compatible acceleration detected | Block normal benchmark; explain limitation |
| Telemetry sources contradict each other | Fail verification; collect evidence; open repair flow |

**Platform-specific supplemental evidence:** NVIDIA → `nvidia-smi`, Ollama processor split, runner GPU memory, generation speed. AMD/Intel/iGPU/APU → supported Windows GPU telemetry + Ollama processor/backend info + speed. Unified memory → confirmed accelerator activity + shared-memory use; dedicated VRAM must not be required.

### 3.6 Automated repair flows

- **Missing Ollama:** download official Windows installer over a trusted connection → verify when supported → request admin approval only if required → run → rediscover executable → start → verify version + API → continue to probe.
- **Path failure:** search known install locations → inspect registered app info → validate candidates → save resolved path in app config → start Ollama by full path → recheck API. Repair the app's own configuration first; modify system/user PATH only when necessary, permitted, and safe.
- **Service/API failure:** check executable existence, running processes, API address, port 11434 availability/conflicts, multiple instances, permissions, loopback policy, security quarantine, damaged install. Repair sequence: rediscover → repair internal path → stop stale process when safe → start from resolved location → poll API → restart on failure → offer repair/reinstall → request elevation only when required → re-run probe → export Doctor diagnostic report if still blocked.
- **Acceleration failure:** restart Ollama and re-probe; detect competing accelerator consumers (recommend closing games/recording/streaming/other model servers); verify runtime supports the detected backend; check env vars/backend config; check laptop high-performance/discrete-GPU settings; check iGPU/shared/unified availability; on NVIDIA check driver and use `nvidia-smi` as supplemental proof; guide driver update/reinstall only when needed; require reboot when a system change requires it; recommend smaller model/quantization when the model is too large; re-probe after repair. Never automatically rewrite GPU drivers or weaken security protections.
- **Insufficient storage:** `required = total selected download size + 10 GB reserve`. Offer: deselect models, choose smaller models/quantizations, choose another supported storage location, free space and retry.
- **PowerShell/security restrictions:** use signed executables and trusted installer mechanisms; prefer native application code for downloads, API checks, path discovery, process management; when PowerShell is used, run it hidden in a controlled background process; never permanently weaken execution policy; never silently disable Defender/firewall/AV/enterprise controls; request admin approval only when genuinely required; explain policy blocks in plain language; produce an IT-support-ready Doctor report when organizational policy prevents repair.

---

## 4. Functional Requirements — Model Library

A dedicated **Model Library / Models** tab with three clear areas: **Installed on this PC**, **Haval Preferred Models**, **Search Ollama Models** (mockup: search field on top; segmented filter Installed / Preferred / Search Ollama; storage summary, e.g., "318 GB free of 931 GB").

### 4.1 Installed models inventory

On open, query Ollama (internally `ollama list` or API) and display all local models with (when available): exact name+tag, friendly display name, parameter size, quantization, storage size, digest, family, installation status, estimated hardware fit, acceleration readiness, and an **Include in Benchmark** checkbox. The customer can: include/exclude any model, select all eligible, select only recommended, re-download/repair, and remove a model via a clearly confirmed destructive action. **Excluding or skipping a model never deletes it.**

### 4.2 Haval Preferred Models (configuration-driven catalog)

The Standard Roster is **five** models (Decision D-2). GPT-OSS 20B is **not** in the preferred catalog; customers may still search, install, and include it in a benchmark (Decision D-5).

| Preferred model | Exact Ollama pull command | Roster order |
|---|---|---:|
| Gemma 4 26B | `ollama pull gemma4:26b` | 1 |
| Qwen 3 Coder 30B | `ollama pull qwen3-coder:30b` | 2 |
| Kimi Linear 48B | `ollama pull hf.co/mradermacher/Kimi-Linear-48B-A3B-Instruct-GGUF:Q4_K_S` | 3 |
| Qwen 3 Next 80B | `ollama pull qwen3-next:80b` | 4 |
| GPT-OSS 120B | `ollama pull gpt-oss:120b` | 5 |

Catalog source of truth: `config/preferred-models.json` (hot-updatable; never hardcoded in the UI). Each row: model name, size when known, download status, estimated hardware fit, estimated storage, **Download** button, individual progress bar, Include-in-Benchmark checkbox, cancel/retry/remove where applicable, and a clear error explanation on failure.

### 4.3 One-click download experience

- Download executes the exact pull command automatically; the customer never copies commands.
- **No flashing Command Prompt/PowerShell windows, no visible terminals, no manual command entry.** Background execution may use a hidden process or a supported application interface; capture stdout/stderr; parse Ollama progress; render a stable graphical progress bar; store technical output in a support log.
- Active download shows (when available): model name, current stage, % complete, downloaded/total size, transfer speed, ETA, pause/cancel when technically supported. On completion: show **Completed**, refresh inventory, enable the selection checkbox.

### 4.4 Download queue

Sequential by default (controlled parallel downloads may be a later advanced setting). Queue states: **Not installed / Queued / Downloading / Paused / Verifying / Completed / Failed / Cancelled**. A failure never cancels the remaining queue; the customer can retry, edit the tag, search an alternative, or skip.

### 4.5 Post-download validation

After every successful pull: confirm command success → refresh inventory → verify the exact model appears in Ollama → record name/tag/size/digest/family/parameters/quantization → run a short load test → check acceleration capability → classify as **Ready / Ready with partial offload / Installed but not verified / Not suitable for this hardware / Failed to load** → make eligible models selectable. A completed download does not automatically mean the model suits the hardware; if too large, recommend a smaller model or quantization rather than allowing an unexplained CPU-only run.

### 4.6 Search Ollama models

Search by name; paste exact Ollama tags; paste supported Hugging Face references (`hf.co/org/repo:quant`); filter by family/parameters/quantization/download size/estimated fit when metadata exists; review estimated storage and fit before downloading; add to the sequential queue; download via the same hidden background process; select the completed model for benchmarking. Errors must distinguish: model/tag not found, network unavailable, registry unavailable, authentication required, insufficient storage, unsupported/invalid format, unsupported sharded package, checksum/verification failure, load failure, model too large for acceleration policy. Offered actions: retry, edit tag, search another quantization, choose smaller model, skip, view technical details.

### 4.7 Benchmark selection gating

Start Benchmark remains disabled when: no model selected; a selected model still downloading/verifying; Ollama unavailable; machine-level probe failed; a required repair is active. Models that fail the acceleration policy stay visible with clear status and explanation — they never silently participate.

### 4.8 Internal support commands (implementation/support only, never customer actions)

`ollama --version`, `ollama list`, `ollama ps`, `ollama serve`, `ollama stop MODEL`, and on NVIDIA only `nvidia-smi`; API check `Invoke-RestMethod http://127.0.0.1:11434/api/tags`. If PowerShell is restricted, perform equivalent API requests and process control through signed native/bundled components.

---

## 5. Functional Requirements — Benchmark Engine

### 5.1 Evaluation architecture

- **3 businesses:** Consumer (8 personas), Gaming (4), Commercial (8) → **20 personas**.
- **3 workload intensities** per persona: Light, Balanced, Heavy → **60 scenarios** (24 Consumer, 12 Gaming, 24 Commercial), fully defined in the Persona-AI-Workload-Quality-Evaluation-Matrix (§5.5).
- Per completed model: **60 workload results + 20 persona-overall results**, plus Consumer/Gaming/Commercial business scores and a global hardware-model suitability score.
- Models are tested **safely and sequentially** with clear progress (mockup: overall progress bar, "Model 3 of 4 · Elapsed", current-step text in plain language, stat tiles for generation speed / TTFT / VRAM headroom / completion, Pause & Stop controls, collapsed Live technical log).

### 5.2 Controlled generation settings

Deterministic decoding: **temperature 0, top_p 1, seed 42**; one attempt per graded generation unless a scenario explicitly tests iteration; technical timeouts (current app baseline: 30 s general, 90 s coding — persona scenarios carry their own acceptance targets and completion limits, stored separately from the technical timeout). Two distinct time concepts must always be kept apart:

| Concept | Purpose | Effect |
|---|---|---|
| Technical timeout | Prevents unbounded runs | Reached without gradeable result → technical failure |
| Acceptance target | What the persona tolerates for the task | Normalizes Experience even when the run completes |

### 5.3 Measurements captured per run

Generation speed (tok/s), time to first token, total task-completion time, model load time, prompt/output token counts, memory use and hardware headroom (VRAM/unified/host), reliability & completion status (loaded, completed, OOM, crash, runner error, timeout, truncated), plus the quality-dimension evidence (§6).

### 5.4 Repetition & reliability

Run each scenario **at least 3 times** per model–hardware configuration. Technical success = model loads, runner healthy, within technical timeout, no OOM/crash/transport failure/runner exception, response complete enough to grade. Wrong-but-complete = quality failure, not reliability failure; crash-before-gradeable = reliability failure. Do not double-count: one evidence record may serve multiple views but the same run is never counted twice inside one component score.

### 5.5 The 60-scenario suite (authoritative: Evaluation Matrix workbook)

Each scenario row defines: **ID** (e.g., `C-EO-L`, `G-RD-H`, `B-PLC-B`), business, persona, workload, scenario name, **TTFT target (2/4/8 s for L/B/H)**, **completion limit (7–300 s, scenario-specific)**, required input/fixture (inline or a named fixture such as `WEEK_PLAN`, `CELL_ENERGY_10P`, `GAME_BENCH_LOGS`, `CONTRACT_25P`), the complete test prompt, the **primary quality dimension**, per-dimension grading notes or N/A, **hard acceptance gates**, recommended grader, applicable-quality count, and research basis. Fixtures are versioned, fixed test assets shipped with the app. Persona-level completion tolerances follow the Response-Time Source Table (Light ≤7–12 s, Balanced ≤30–90 s, Heavy ≤90 s–5 min depending on persona).

**Grader types used across the matrix:** deterministic rule checks (counts, formats, banned words — IFEval-style), exact/tolerance numeric match, deterministic validators (schedule/constraint/rule engines, document diff, graph/date validators), sandboxed hidden unit tests for code, JSON parse + schema + value checks, golden-answer/golden-path matching, source-fact/atomic-claim grounding checks, and calibrated rubric judging (human or LLM) for creative quality. Each scenario's evaluator rubric and expected-answer requirements are stored with the scenario record.

### 5.6 Scenario traceability record

Every workload result must be traceable to a scenario record containing: scenario ID + version; business; persona; intensity; complete prompt; input context/attachment reference; applicable quality dimensions; quality weights; expected-answer requirements; evaluator rubric; acceptable TTFT; acceptable total time; attempt count; success criteria; raw output; raw timings; evaluator evidence; error/failure details. (Also see §8 Data Requirements.)

---

## 6. Functional Requirements — Quality, Scoring & Categories

### 6.1 Quality dimensions

Seven dimensions, scored only where applicable (N/A dimensions are excluded from numerator AND denominator — never zero):

| Code | Dimension | Measures |
|---|---|---|
| R | Reasoning | Logic, decomposition, inference, defensible conclusions |
| M | Math | Numerical correctness, units, calculations, consistency |
| P | Coding & Problem Solving | Executable correctness, debugging, technical resolution |
| I | Instruction Following | Scope, constraints, format, tone, exclusions |
| S | Structured Output / JSON | Validity, schema, types, fields, machine-readability |
| F | Factual Accuracy | Grounding, faithful extraction, no invention/hallucination |
| C | Creative Quality | Originality, coherence, audience fit, style, usefulness |

Experience (E: TTFT + completion time) applies to **every** scenario and is scored separately from quality.

Dimension rubric: 0–4 anchored scale (Excellent 4 / Good 3 / Partial 2 / Weak 1 / Fail 0) normalized ×25 to 0–100. Score anchors: 90–100 correct & complete; 80–89 strong, minor issues; 70–79 useful, revision advisable; 60–69 minimum usable; 50–59 fragile; 0–49 incorrect/unusable/unsafe.

### 6.2 Scenario quality score

**Primary-dimension weighting (methodology + matrix):** the scenario's primary dimension receives **40%**; remaining applicable dimensions divide **60% equally**; if only one dimension applies it receives 100%:

```text
Qw = 0.40·q_primary + Σ[ (0.60/(n−1)) · q_secondary ]        (n>1; if n=1, Qw = q_primary)
```

(The report-requirements doc states the general form `Q[p,w] = Σ(α[i]·q[i]), Σα=1` with scenario-specific weights — the 40/60 rule is the version-1 concrete weighting; scenario records may carry explicit per-dimension weights as in the `GAM-RGD-H-001` example. Both forms must be supported; weights always sum to 1.)

**Hard quality gates (automatic scenario failure regardless of arithmetic):** required JSON invalid or fails mandatory schema; submitted code doesn't run or fails mandatory correctness tests; an exact mandatory answer is wrong; a response invents a required source claim or contradicts supplied evidence; a technical instruction is unsafe for the stated context; a mandatory section/field/deliverable is absent. A completed response violating a hard gate is **Not Acceptable / Not Recommended** for that workload; no gradeable response at all is **Failed**.

**Quality pass threshold (matrix):** weighted quality ≥ 75/100 AND all hard gates pass. Record quality even when timing fails.

### 6.3 Response experience score

```text
r = actual_time / acceptable_time            (separate ratios for TTFT and total time)
g(r) = 100                    when r ≤ 1
g(r) = 100 × 2^−(r−1)         when r > 1     (2× target → 50; 3× → 25; 4× → 12.5)

E[L] = 0.45·g(r_TTFT) + 0.55·g(r_total)
E[B] = 0.35·g(r_TTFT) + 0.65·g(r_total)
E[H] = 0.25·g(r_TTFT) + 0.75·g(r_total)
```

Targets are **per scenario**, never universal. Default design guidance: Light TTFT ~1–2 s / total ~10–30 s; Balanced TTFT ~2–4 s / total ~30–120 s; Heavy TTFT ~3–8 s / total ~2–10 min with visible progress or streaming. Time-target authoring rules: base targets on realistic tolerance and output length; version targets with rationale; pair completion time with output requirements so verbosity is not rewarded; treat streaming/non-streaming consistently (documented substitute + flag if TTFT unavailable).

### 6.4 Reliability score

```text
R[w] = 100 × technically_successful_runs / attempted_runs      (minimum 3 attempts)
```

### 6.5 Workload match score (weighted geometric mean — no hidden compensation)

```text
W[p,w] = Q[p,w]^0.60 × E[p,w]^0.30 × R[w]^0.10
```

Zero in any required component → zero score (appropriate when there is no valid quality/experience/completion). Missing measurements are NOT converted to zero — they are reported as incomplete ("Insufficient Data", which is not a match category). Compute at full precision; store Qw, Ew, Rw and raw Ww; apply gates to raw values; round only for display; category boundaries apply to **unrounded** values.

### 6.6 Persona aggregation

```text
P[p] = 0.25·W[L] + 0.40·W[B] + 0.35·W[H]
```

Balanced carries the most weight (most common daily use); Heavy stays highly influential. Diagnostics Qp/Ep/Rp use the same 0.25/0.40/0.35 mix but are never substituted back into the workload formula. **Display all four badges** (L/B/H/Overall) — the Light-vs-Heavy difference is decision-useful.

Persona failure protections: one workload Failed → persona Overall capped at Acceptable; two workloads Failed → capped at Not Acceptable/Not Recommended; all three failed → persona Failed; a hard-gate violation makes that workload Not Acceptable with component/coverage gates still applying.

### 6.7 Business aggregation

```text
B[b,m] = Σ(ω[p] × P[p,m]),  Σω[p] = 1
```

Version 1 uses **equal persona weights** within each business (Consumer = mean of 8, Gaming = mean of 4, Commercial = mean of 8) until usage evidence justifies otherwise. Aggregate **numbers, never labels or colors**. Preserve business-level Light/Balanced/Heavy views and business diagnostics (QB/EB/RB) where possible.

Business coverage guards (category caps at business level): Excellent requires 90–100 AND every persona ≥ Strong AND none failed; Strong 80–89 AND every persona ≥ Good; Good 70–79 AND every persona ≥ Acceptable; Acceptable 60–69 with ≤25% personas Not Acceptable; Marginal 50–59 with ≥half Marginal-or-better; below that Not Acceptable; no gradeable persona → Failed. Failure caps: one persona completely fails → business capped at Acceptable; two or more → Not Acceptable; all → Failed.

**Business winner:** `Winner[b] = argmax B[b,m]` over **qualified completed models only**, independently per business. No universal winner anywhere.

### 6.8 Global hardware–model suitability

```text
S[m] = 100 × (Q/100)^0.40 × (E/100)^0.35 × (H/100)^0.25
```

Q = overall model quality, E = customer response experience, H = **measured hardware fit** (memory headroom, stability, offload health). Answers whether the pairing is healthy overall; never replaces persona/business scores.

Global gates: missing result / load failure / OOM / timeout / incomplete representative scenario → **Failed**. Quality < 55 or Hardware Fit < 40 → **Not Recommended**. Severe swapping or unstable execution → cap at **Marginal**. Representative customer task > 15 minutes → cap at **Marginal**. Quality < 65 → cap at **Acceptable**.

### 6.9 Optional device-level score

`D = α·C + β·G + γ·M, α+β+γ=1` — only when the device's intended market mix is known; publish the weights; never let a device badge conceal category differences.

### 6.10 Match categories

**Report taxonomy (customer-facing, authoritative for the final report):**

| Exact numeric result | Category | Meaning |
|---:|---|---|
| 90–100 | Excellent Match | Preferred configuration for the evaluated scope |
| 80–89.9 | Strong Match | Dependable; manageable tradeoffs |
| 70–79.9 | Acceptable Match | Usable, but limitations visible |
| 60–69.9 | Marginal Match | Runs, but efficiency/experience is weak |
| < 60 | Not Recommended | Quality, experience, or hardware fit insufficient |
| Non-numeric | Failed | Model or scenario did not complete |

**Methodology taxonomy (7 levels, used internally by the scoring spec):** Excellent 90–100, Strong 80–89, **Good 70–79**, Acceptable 60–69, Marginal 50–59, Not Acceptable <50, Failed to Complete. With component floors per level (e.g., Strong requires min Q 80 / E 70 / R 90 and all workloads gradeable; final label = lowest category allowed by numeric band, component floors, hard gates, and completion rules). **⚠ These two taxonomies must be reconciled before implementation — see Open Issue OI-1.** In both, "Failed" strictly means no gradeable result (OOM/timeout/load/runtime failure), while "Not Recommended / Not Acceptable" means completed but unsuitable; "Marginal" means runs but weak.

### 6.11 Decision order (per workload)

1. Validate the run produced a complete, gradeable response.
2. Apply scenario hard quality gates.
3. Calculate applicable quality dimensions → Qw.
4. Calculate TTFT + completion normalization → Ew.
5. Calculate repeated-run reliability → Rw.
6. Calculate raw Ww (geometric formula).
7. Map the raw number to a candidate category.
8. Apply component floors, workload failure caps, coverage guards.
9. Aggregate numbers upward; repeat gates at persona and business levels.

### 6.12 Calibration & governance

The 60/30/10 workload weights, 25/40/35 persona mix, floors, and bands are **reasoned version-1 product weights**, not published standards. Requirements: version every rule set; record which score consumed which timeout policy; run sensitivity analysis (±10 pp per top-level weight, renormalized) before release and flag configurations whose category flips easily; plan a calibration study with representative users; monitor after launch. The QA checklist per category evaluation: unrounded inputs; N/A exclusions; scenario-specific targets; ≥3 attempts; hard gates before aggregation; floors and caps applied; numbers (not labels) aggregated; raw score, final label, cap reason, and evidence retained.

### 6.13 Relationship to the existing 39-item bench

The existing `full_end_to_end` pack (instruction following, math, reasoning, structured JSON, coding, factual/extraction, creative constraints, speed, three customer-timed tasks) supplies reusable evidence. Reuse existing scores only when the underlying task validly represents the persona scenario; store one evidence record referenced from both views; preserve the legacy timeout rule (correct-but-late = failed, −15 points; three timeouts in a category cap it at 40) as its own evidence field rather than silently changing historical scores.

---

## 7. Functional Requirements — Final Report

### 7.1 Format & authority

- One **self-contained HTML file** per run: no external fonts, scripts, images, or network access; inline SVG icons; responsive; wide tables scroll horizontally on small screens; printable; category pills and labels never clipped; readable contrast; business colors consistent throughout; the term **Commercial**, never "Enterprise".
- `Haval-Hardware-First-LLM-Fit-Report.html` is authoritative for presentation (cards, tables, colors, spacing, hierarchy, responsive behavior); the requirements doc is authoritative for rules and data. All hypothetical example values must be replaced by measured values; measured-vs-hypothetical status must be explicit.

### 7.2 Required structure

| Section | Content |
|---|---|
| **00 — Executive Hardware Verdict** | Dynamic title `Evaluation of <Product Name> against Different LLM Sizes`; best general-purpose parameter range; highest practical capability range; stretch/out-of-range boundary; measured/hypothetical disclosure |
| **01 — Tested Hardware Configuration** | Exactly four tiles: System, GPU + VRAM, CPU, System Memory; device-aware inline SVG icons; NO OS or Power Mode tiles |
| **01A — Realistic Customer Scenario** | The approved task: a 10-page report summarized into key takeaways; visual `10-PAGE CONTENT → AI MODEL → KEY INSIGHTS` with document, AI-chip, and lightbulb icons; every completed model shows its estimated time for this same task; failed models show no invented time; the internal token-estimation formula is never displayed |
| **02 — LLM Capacity Envelope** | Fast/Light, Balanced Sweet Spot, High Capability, Stretch/Out-of-Range zones, derived from tested hardware + quantization + context + measured results (never universal parameter promises); tested models placed in zones; explain why similar-parameter models can behave differently (architecture, active params, quantization, bytes, memory movement) |
| **03 — Best Model by Business** | Three independent winner cards: Consumer (teal), Gaming (purple), Commercial (blue); NO overall recommended model |
| **04 — Tested-Model Evidence Table** | Columns: Model, Architecture, Total/Active Parameters, Quantization, Model Bytes, Memory Used, Generation Speed, TTFT, Customer Task Time, Hardware Zone, Suitability Category |
| **04A — Final Verdict Response-Time Table** | Model, Generation Speed, TTFT, Estimated Time (s), Estimated Time (min:sec), Suitability Category — exact values for calculation, formula hidden |
| **05 — Business Match Matrix** | Model, Total/Active Parameters, Consumer Final Match, Gaming Final Match, Commercial Final Match, Recommended Use; NO universal overall score/rank/winner column |
| **06 — Sweet-Spot Model Drill-Down** | Name/family, dense/MoE, total & active params, quantization, footprint, Quality, Experience, Hardware Fit, Reliability, global suitability score+category, observed memory & headroom; supports the hardware-first conclusion, never the report's starting point |
| **07 — Persona Workload Tables (one per tested model)** | Per model: name, architecture, total/active params, quantization, short profile, Consumer/Gaming/Commercial finals, complete persona table with columns Business, Persona, Light, Balanced, Heavy, Overall, Final Match; all 20 personas in identical order; 60 workload + 20 persona results per completed model; independent calculation per model; failed values as em dashes; fully failed model = header + failure inset, never a fabricated table |
| **08 — Scoring Equation Card** | Dark premium card style; quality, timing normalization, experience, reliability, workload, persona, business, hardware-suitability, and winner equations; concise; no realistic-task token formula |
| **09 — Persona Reference Table** | Business, Persona, typical day-to-day work, what the persona needs from AI; state that personas describe task patterns, not demographics |

### 7.3 Model identity & roster rules

Strip repeated trailing size aliases from display names but preserve source names in raw data; distinguish dense vs MoE; show total AND active parameters when available; show quantization and exact model bytes (never inferred from nominal parameters when measured); keep missing/failed/timed-out/OOM models visible in expected order; never invent measurements; **exclude GPT-20B from this report family**; when present use model order Gemma4-26B → Qwen3-30B → Kimi-48B → Qwen3-80B → GPT-120B; support any number of models (three-model reports are only hypothetical examples).

### 7.4 Section 07 scaling behavior

Three completed models → three full 20-persona tables; five → five in prescribed order; entirely failed model → header + failure reason + em dashes; one failed workload → keep persona row, mark failed intensity, apply coverage gate; slow-but-completes → reduced Experience and category, never "Failed"; fast-but-inaccurate → quality weighting and gates prevent inflation.

### 7.5 Failure presentation

Keep the model in expected order; show parameter badge when known; em dash for scores; label **Failed**; display the evidence-backed reason; never invent values; never silently omit. When the only evidence is a missing expected result: **"Failed — Failed to run the LLM model."**

### 7.6 Report visual system

Warm ivory page `#F6F1E9`; near-black text `#201E1C`; Haval burnt orange `#DC4D18`; Consumer teal `#247F79`; Gaming purple `#79519A`; Commercial blue `#3F6797`; Excellent `#2F774B`; Strong `#39748B`; Acceptable `#A8731F`; Marginal `#745486`; Not Recommended `#A74733`; Failed dark neutral gray. Meaning never depends on color alone — always show the text category. Character: elegant, premium, calm, editorial rather than dashboard-heavy, Apple-style whitespace, serif headlines + clean sans body, rounded cards, restrained shadows.

### 7.7 Reports screen (application)

Editorial Reports tab: large Fraunces title; report cards with date, machine, model count, verdict; preview/summary; primary **Open Report**; secondary **Export PDF** and **Show in folder** actions (per mockup); a benchmark library listing all past runs.

---

## 8. Data & Persistence Requirements (per-run evaluation database)

**Every benchmark run must produce its own durable, self-describing data set** — a small per-run database plus portable CSV exports — so that every number in the report is traceable, re-computable, and analyzable outside the application.

### 8.1 Storage layout (per run)

```text
%LOCALAPPDATA%\Haval LocalAI Bench\
  config\            app settings, resolved Ollama path, preferred-model catalog (JSON)
  logs\              Doctor + download + benchmark technical logs (support)
  runs\<runId>\      one folder per benchmark run, runId = timestamp + machine slug
    run.sqlite       authoritative per-run relational store (all tables below)
    csv\             portable CSV exports (auto-generated at run completion)
      run_manifest.csv
      hardware.csv
      models.csv
      scenarios.csv          (scenario ID, version, prompt hash, targets, weights)
      attempts.csv           (one row per attempt: raw timings + technical status)
      quality_scores.csv     (one row per attempt × applicable dimension)
      workload_scores.csv    (Qw, Ew, Rw, raw Ww, gates applied, category, cap reason)
      persona_scores.csv     (P[p], diagnostics Qp/Ep/Rp, category, caps)
      business_scores.csv    (B, coverage results, winner flags)
      suitability.csv        (S[m], H, gates, hardware zone)
    raw\             raw model outputs (one file per attempt), evaluator evidence JSON
    report\          Haval-Report-<machine>-<date>.html (+ optional PDF export)
    doctor-snapshot.json     environment + probe evidence at run start
```

### 8.2 Required record content

- **Run manifest:** run ID, app version, rule-set/scoring version, scenario-pack version, fixture versions, grader versions, start/end time, settings (temperature, top_p, seed, timeouts), models attempted, completion status.
- **Configuration identity (audit fields):** model, quantization, runtime version, context settings, accelerator, RAM/VRAM, stable machine identifier.
- **Per attempt:** scenario ID + version, prompt version (immutable ID + rubric version), raw response (unmodified), model load time (when applicable), TTFT, total completion time, prompt tokens, output tokens, technical status (loaded / completed / OOM / crash / runner error / timeout / truncated), memory telemetry.
- **Quality evidence:** per-dimension scores, hard-gate results, grader version, notes/evidence.
- **Every aggregate:** raw unrounded score, final label, cap reason (which gate/floor/guard fired), and links to underlying evidence rows.

### 8.3 Data rules

- Calculations always read exact unrounded values; rounding happens only at display.
- Raw values are immutable once written — never silently corrected, replaced, reconciled, or invented; corrections happen only by re-running.
- Failed/missing data is stored as explicit status, never imputed ("Insufficient Data" ≠ "Failed").
- CSV exports are UTF-8, header row, stable column order, suitable for Excel/pandas.
- The report generator consumes only the per-run store — a run folder is sufficient to regenerate its report byte-for-byte.
- Runs are never overwritten; deleting a run is an explicit, confirmed user action.

---

## 9. Experience (UX/UI) Requirements — Application

### 9.1 Design vision

Preserve the warmth, editorial character, and burnt-orange identity of HavalOthman.com with the quiet precision of premium Apple-style product design — while remaining a **native-feeling Windows 11 application** (not a website replica, not a macOS imitation). The app should feel: elegant not decorative; warm not clinical; premium but approachable; powerful without appearing complicated; calm during long operations; consistent across setup, downloads, benchmarking, and reports. The customer always knows: where they are, what the app is doing, whether everything is healthy, what action is next, and what happened on failure.

### 9.2 Core principles

Simplicity first (advanced details behind View details / expandables; no logs or env vars in the primary view). One clear primary action per screen (Repair / Download / Continue / Start Benchmark / Open Report). Calm hierarchy (whitespace, typography, alignment before borders/colors). Progressive disclosure. Immediate feedback (every click responds; long work shows stable progress, never frozen). Human language ("Ollama is ready", not "API endpoint 127.0.0.1:11434 returned HTTP 200"). Restraint (no visual noise, glow, heavy shadows, rainbow dashboards).

### 9.3 Design tokens

**Core colors:** Canvas `#F6F1E9`, Surface `#FBF7EF`, Border `#E6DFD3`, Ink `#1A1A1A`, Ink Soft `#4A4540`, Accent `#DB4F1B`, Accent Soft `#F4DCD0`, On Accent `#F6F1E9`, Accent Text `#A83B15`, Accent Hover `#C54518`.
**Semantic:** Success `#287653`/`#DDEDE5`, Warning `#A76000`/`#F7E8C8`, Error `#B42318`/`#F8DFDC`, Info `#456A87`/`#E1EAF0`, Neutral `#625D57`/`#ECE6DD`. Every status combines color + icon + text; never pure white canvas, pure black regions, or orange for everything.

**Typography:** Fraunces (fallback Georgia) for expressive titles only (welcome, page titles, report headings, empty/completion states); Inter (fallback Segoe UI Variable/Segoe UI) for all operational UI; Cascadia Mono (fallback Consolas) for technical values. Type scale: Display 40/44 w500 · Page title 30/36 · Section 22/28 · Card title 17/22 w600 · Body 15/22 · Secondary 13/19 · Label 12/16 w600 · Metric 24–32 w600 · Mono 12–13. Uppercase editorial labels with 1.5–2 px letter spacing, used sparingly (SYSTEM READINESS, MODEL LIBRARY, BENCHMARK PROGRESS).

**Cards:** Surface `#FBF7EF`, 1 px `#E6DFD3` border, radius 14 px (dialogs 16 px), padding 20–24 px (dialogs 24–32), soft warm shadow `0 1px 2px rgba(26,26,26,.04), 0 6px 18px -8px rgba(26,26,26,.08)`; hover rise ≤1–2 px; noninteractive cards must not look clickable.

**Buttons/controls:** Primary = orange fill, ivory text, 38–42 px height, pill radius; Secondary = surface + border + ink; Tertiary = text-only with subtle hover; Destructive = semantic error + confirmation when data is deleted. Inputs 40–44 px, radius 10–12 px, orange focus ring, visible labels (placeholder never the only label). Checkboxes/switches native-feeling with brand accent, ≥32×32 px targets. Disabled controls remain readable and explain why.

**Motion:** hover/press 120–160 ms; tabs/selection 160–200 ms; expansion/dialogs 180–240 ms; ease-out for appearing, ease-in-out for state change; no continuous animation unless work is running; no flashing/pulsing; respect reduced-motion.

### 9.4 Window & navigation

Windows 11 target; default ~1360×860, minimum 1100×720; correct maximize/restore/minimize/resize/snap; remember last size/position; per-monitor DPI 100–200%; keyboard + screen-reader support. Canvas-colored client area, Windows 11 rounded windows, native shadows; custom title bar only if drag/resize/snap/system menu/accessibility/DPI remain correct; restrained Mica/translucency only in chrome.

**Top navigation (per mockup):** Header = product mark + name ("Haval LocalAI Bench / LOCAL MODEL EVALUATION") left; pill tabs **Home · Doctor · Models · Benchmark · Reports · Settings** center; machine-health pill (colored dot + label, e.g., "Needs attention") + Help right. Active tab: darker text + Accent Soft pill, 160–200 ms transition.

### 9.5 Layout

Content centered, max width ~1180 px; outer margins 28–36 px; 32–48 px between major sections; 20–24 px between related cards; 12–16 px title-to-support; 8 px base grid. Prefer one strong summary + supporting cards; logs collapsed; tables only for true repeated data; left-align text, right-align comparable numbers; predictable action placement.

### 9.6 Key screens (baseline + mockup)

- **Home:** editorial welcome ("WELCOME BACK" label; Fraunces headline "Know what your PC can really run."; one-line purpose), System Readiness card (status + Open Doctor; processor/graphics/memory/acceleration/storage/Ollama rows), Model Library card (installed & selected counts + Manage models), Last Benchmark card (models · personas · date, best balanced fit, Open report), one primary **Start Benchmark** action. ≤3–4 summary cards in first viewport.
- **Doctor:** reassuring, not alarming. Overall state (Ready / Needs attention / Repairing); vertical prerequisite checklist (icon, title, one-line status, optional action); one **Repair Automatically** primary action when repair is possible; collapsed Technical details. Green = confirmed ready; orange = action/active repair; red = true blockers only. Mockup shows the repair animating through "Repairing" to "Ready" with the header health pill updating.
- **Models:** search on top; segmented Installed / Preferred / Search Ollama; storage summary ("318 GB free of 931 GB" with usage bar); model rows: checkbox, icon, name + parameter badge, params · quantization · size, hardware-fit badge (Excellent fit / Strong fit …), install/download status, primary row action. During download the action becomes a clean progress bar + % + stage + cancel; progress track uses Border, fill uses Accent; completed uses success state without losing brand styling.
- **Benchmark:** "BENCHMARK PROGRESS" label; Fraunces "Benchmarking in progress"; Pause + Stop; Overall Progress card (large restrained bar, "Model 3 of 4 · Elapsed 12:48", current activity in plain language — e.g., "Qwen 2.5 7B — Commercial · Heavy workload / Structured output & JSON · persona 14 of 20"); stat tiles Generation Speed / Time to First Token / VRAM Headroom / Completion; collapsed Live technical log. No competing gauges or animated charts.
- **Reports:** Fraunces page title; benchmark-library cards (date, machine, model count, best-fit verdict, Open Report); full in-app hardware-first report view matching the report design (comfortable range statement, best match by customer, per-model suitability matrix); Export PDF and Show in folder secondary actions.
- **Settings:** grouped — Application; Ollama; Models & storage; Benchmark behavior; Privacy & support. Simple labeled controls; risky/advanced settings collapsed.

### 9.7 Status & messaging

Every major workflow: short headline → one-sentence explanation → status icon + label → one recommended action → optional technical details. Compact in-app toasts for completed background actions; critical failures visible until resolved; no modal for routine success; no unexplained error codes in the main message. Example patterns: "**Ollama is ready** — The local service is running and responding normally." / "**This model needs more memory** — Choose a smaller quantization for reliable acceleration on this PC."

### 9.8 Tables & dense data

Subtle header; row height 48–56 px; fine horizontal dividers, no full grids; model names left; comparable numbers aligned; selected row Accent Soft; keyboard row navigation; ≤2 primary actions per row; narrow windows hide secondary columns before shrinking text.

### 9.9 Accessibility & Windows quality

WCAG 2.2 AA contrast; visible keyboard focus; keyboard-only navigation; logical tab order; names/roles/values/states exposed to Windows accessibility APIs; Narrator + screen readers; Windows text scaling; reduced-motion and High Contrast (system colors take precedence); status never color-alone; targets ≥32×32 px (preferably 40 px high); crisp at common scaling levels.

### 9.10 Theming

V1 ships one polished light theme + Windows High Contrast support + centralized design tokens so a future deliberately designed dark theme can be added safely (never simple inversion).

### 9.11 Do / Do not (summary)

Do: warm ivory/cream, controlled burnt orange, generous whitespace, selective serif headings, 14 px cards + subtle shadows, plain language + progressive disclosure, calm truthful progress, obvious next action. Do not: copy macOS controls; webpage-in-a-window; dark gaming gradients; neon glow/glass/heavy shadows; metric-tile rainbows; raw PowerShell as the normal experience; orange everywhere; constant animation; shrinking fonts to cram data; generic failure messages.

---

## 10. Technical Requirements (non-functional)

1. **Reliability of the UI:** background processing never freezes the UI; progress updates flow through the main UI thread responsively; long-running work always shows stable progress, current step, elapsed time, and (only when reliable) ETA; Cancel/Pause visible when supported.
2. **Hidden command execution:** all process execution (Ollama, probes, downloads) hidden — no flashing PowerShell/CMD windows ever.
3. **Security posture:** signed installer + signed executables; trusted download channels; verify installers when supported; least-privilege (elevation only when genuinely required); never weaken Defender/firewall/AV/policies; produce IT-support diagnostic reports when blocked.
4. **Offline behavior:** benchmarking and report generation fully offline; network needed only for Ollama/model downloads; generated reports work completely offline.
5. **Determinism & auditability:** versioned scenario packs, rubrics, weights, rule sets, graders; deterministic decoding; unrounded internal math; complete audit trail per §8.
6. **Sequential safety:** models benchmarked one at a time; downloads sequential by default; storage checked before download (10 GB reserve).
7. **Crash resilience:** a crash or power loss must not corrupt previous runs; partial runs are marked incomplete, resumable or discardable.
8. **Performance:** the app itself must stay light — measurement overhead must not materially distort TTFT/throughput measurements.
9. **Logging:** plain-language customer surface + full technical support logs (Doctor, downloads, benchmark) with export.
10. **Configuration-driven content:** preferred-model catalog, scenario pack, personas, weights, targets, and report thresholds ship as versioned configuration/data, not hardcoded logic.

---

## 11. Acceptance Criteria (consolidated)

### 11.1 Setup & Model Library (from prerequisites doc §17)

Windows 11 customer installs/launches without manual Python; Doctor detects/installs/locates/starts/verifies Ollama graphically; non-NVIDIA systems are not rejected for lacking CUDA/`nvidia-smi`; NVIDIA-specific validation applies when NVIDIA exists; iGPU/APU/shared/unified acceleration can pass; CPU-only never silently accepted; Doctor distinguishes full/partial/unified/CPU-only; path/port/permission/service/API/security failures have automated repair routes; PowerShell/Windows security never permanently weakened; Model Library lists all installed models; all six preferred models appear with exact pull commands; one-click independent downloads without terminal flashes; per-model clean status/progress; a failed pull never kills the queue; completed models auto-refresh and validate; every installed model independently includable/excludable; excluding never deletes; search + download of other Ollama models works; Start Benchmark disabled until environment + ≥1 selected model ready.

### 11.2 Report — data & calculation (from report doc §19)

Every expected non-excluded model appears exactly once in comparison sections; every tested model has a Section 07 table or failure inset; all 20 personas in consistent order; Light/Balanced/Heavy/Overall/Final Match present; scenario-appropriate quality dimensions normalized; response-time scoring uses scenario-specific targets; exact unrounded values determine categories and winners; reliability/quality/timing/stability/hardware/coverage gates applied; Consumer/Gaming/Commercial winners independent; no universal best-model; failed data never invented.

### 11.3 Report — structure & experience

Hardware verdict before model detail; capacity envelope clear; dense/MoE + total/active + quantization + bytes visible; headroom distinguished from "it loaded"; realistic 10-page scenario included; final response-time table included; business colors consistent; approved category taxonomy; em dashes + reasons for failures; tables usable on small displays; fully offline; prints cleanly; persona definitions included; measured-vs-hypothetical explicit; visually follows the HTML example.

### 11.4 Design acceptance (from UI baseline §19)

Defined palette used consistently; screens visually belong to the HavalOthman.com family while feeling native to Windows 11; active tab clear; one obvious primary action per screen; consistent card rules; serif-for-expression/sans-for-operation; all control states (normal/hover/pressed/focus/selected/disabled/error); Doctor understandable without technical details; downloads show stable progress without terminal flashing; benchmarks never appear frozen; usable at minimum window size; sharp at common scaling; keyboard/focus/Narrator/high-contrast verified; status never color-alone; final UI feels calm, elegant, human, deliberately crafted.

---

## 12. Out of Scope (V1)

Dark theme (tokens prepared only); CPU-only benchmark mode (future, separate & labeled); parallel downloads (future advanced setting); macOS/Linux; non-Ollama runtimes (LM Studio, vLLM, llama.cpp); cloud API evaluation; device-level score display when market mix unknown; automatic GPU driver installation; weight calibration study (planned post-V1).

---

## 13. Glossary

**TTFT** — time to first token. **Acceptance target** — persona-tolerated time for the task (Experience input). **Technical timeout** — hard limit after which a run is a technical failure. **Hard gate** — binary quality condition that fails a scenario regardless of arithmetic. **Component floor** — minimum Q/E/R required for a category band. **Coverage guard** — persona-level condition capping a business category. **Hardware Fit (H)** — measured memory headroom/stability/offload health input to S[m]. **Capacity zone** — Fast/Light, Balanced Sweet Spot, High Capability, Stretch/Out-of-Range. **Fixture** — versioned fixed input asset for a scenario. **Insufficient Data** — required test not executed/recorded (not a match category).

---

## 14. Open Issues — resolved (D-1…D-8)

All eight items are decided in *Haval-LocalAI-Bench-Build-Plan-and-Architecture.md* §12. Binding summaries:

| ID | Decision | Binding outcome |
|---|---|---|
| OI-1 / **D-1** | Dual taxonomy | Internal 7-level bands + floors; customer 6-level labels at every UI/report surface. Mapping in `config/ruleset.json`. |
| OI-2 / **D-2** | GPT-OSS 20B removed from Preferred Models | Preferred catalog has **five** models. Users may still install/select GPT-OSS 20B (D-5). |
| OI-3 / **D-3** | Scenario-specific quality weights | Every scenario carries explicit weights summing to 1; 40/60 generator is the fallback. |
| OI-4 / **D-4** | Dual-layer quality thresholds | 75 = scenario diagnostic pass; 55 / 65 remain customer-facing gates. |
| OI-5 / **D-5** | Standard Roster + open selection | Roster order: Gemma 4 26B → Qwen 3 Coder 30B → Kimi Linear 48B → Qwen 3 Next 80B → GPT-OSS 120B. Extra user-selected models append. |
| OI-6 / **D-6** | Local LLM judge | Strongest installed model that is not under test; no self-judge. |
| OI-7 / **D-7** | AI fixture authoring | Allowed only with deterministic golden validation + human sign-off + CI. |
| OI-8 / **D-8** | Hardware Fit formula | Adopted H formula in `config/ruleset.json`. |

---

*End of PRD. The companion document — **Haval-LocalAI-Bench-Build-Plan-and-Architecture.md** — defines how this product should be built.*
