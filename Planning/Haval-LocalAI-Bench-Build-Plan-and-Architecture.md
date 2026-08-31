# Haval LocalAI Bench — Build Plan & Draft Architecture

**Version:** 1.0 · **Date:** August 29, 2026
**Companion to:** *Haval-LocalAI-Bench-PRD.md* (requirements baseline). This document decides **how** to build the product: technology choices, application architecture, module design, data flow, the design/mockup implementation strategy, packaging, testing, and a phased delivery plan.

---

## 1. Constraints That Drive the Architecture

From the PRD, the choices below are effectively forced or strongly steered:

1. **Windows 11 desktop app**, signed installer, native window behavior (snap, DPI, Narrator, High Contrast) — rules out a plain web app.
2. **Python must be bundled** in the installer ("Bundle Python and required application dependencies inside the customer installer") — the benchmark/grading engine is naturally Python (sandboxed unit tests, JSON schema validation, deterministic validators, pandas/CSV, report templating).
3. **Hidden process & service management** (install/start/repair Ollama, no flashing terminals) — needs first-class subprocess control with hidden windows (`CREATE_NO_WINDOW`) and preference for **HTTP API calls over shelling out**.
4. **A rich, brand-heavy custom UI** (Fraunces/Inter, editorial cards, pill nav, the existing HTML mockup) — a web-technology UI layer reproduces the approved mockup almost 1:1, which is the fastest path to the accepted design.
5. **Self-contained HTML report** — template-driven HTML generation with inline SVG/fonts-as-fallback-stack.
6. **Auditability** — SQLite + CSV per run; versioned config packs.

## 2. Recommended Technology Stack

**Recommendation: a two-process desktop application — a Tauri 2 shell (Rust) hosting a React UI, with a bundled Python 3.12 engine ("Bench Engine") running as a local sidecar service.**

| Layer | Choice | Why |
|---|---|---|
| Desktop shell | **Tauri 2** (WebView2, ships with Windows 11) | Tiny footprint (~10 MB vs Electron ~150 MB); real native Win32 window (snap/DPI/accessibility via WebView2 + UIA); Rust side handles privileged operations (process spawn with hidden windows, elevation prompts, file dialogs, registry reads); first-class code signing & updater |
| UI | **React + TypeScript + vanilla CSS design tokens** (no heavy UI kit) | The approved mockup is already HTML/CSS with the token system; direct translation preserves the accepted design; tokens live in one `tokens.css` enabling future dark theme |
| Engine | **Python 3.12**, embedded distribution, exposed as a **FastAPI service on 127.0.0.1 (random port, localhost-only, token-authenticated)** | All benchmark, grading, scoring, data, and report logic in one testable package; FastAPI gives the UI a clean typed API + Server-Sent Events for progress streaming |
| Inference runtime | **Ollama via its HTTP API** (`/api/generate`, `/api/chat`, `/api/tags`, `/api/pull`, `/api/ps`, `/api/delete`) | Streaming JSON gives TTFT, token counts, load duration, and download progress **natively** — no PowerShell parsing, no terminal windows; CLI (`ollama --version`, `ollama ps`) only as supplemental evidence |
| Per-run store | **SQLite** (stdlib `sqlite3`) + **CSV exports** (pandas) | PRD §8 requirement; zero-install; single-file per run |
| Report | **Jinja2 template** derived from `Haval-Hardware-First-LLM-Fit-Report.html` | The normative example becomes the literal template; data injected from the run store |
| Hardware telemetry | Windows: WMI/CIM via `pywin32`/`wmi` (CPU, RAM, GPU name/VRAM), `psutil` (memory, processes, disk), DXGI/`dxdiag` fallback; NVIDIA: `nvidia-smi` (supplemental); AMD/Intel: Windows performance counters (GPU engine/memory) | Vendor-neutral first, per PRD §3.5 |
| Installer | **NSIS or WiX (MSI)** via Tauri bundler + **Authenticode signing**; VC++ redist chained; Python embedded dist packaged inside | Meets signed-installer and bundled-runtime requirements |

### 2.1 Alternatives considered

| Option | Verdict |
|---|---|
| **Electron + Python sidecar** | Works, same UI reuse; rejected for size, memory, and weaker native-window feel. Acceptable fallback if the team knows Electron well. |
| **WinUI 3 / WPF (C#)** | Most native; rejected because reproducing the editorial brand UI (Fraunces serif, pill nav, card system) is slow in XAML, and the Python-bundling requirement forces a second runtime anyway. |
| **PySide6/Qt single-process** | One language everywhere; rejected because QML/Widgets restyling to the approved mockup is expensive and web mockup reuse is lost. Viable plan-B if the team is Python-only. |
| **Flutter** | Good visuals, but immature Windows accessibility + a third language; rejected. |

*Decision rule: if the implementing team is uncomfortable with Rust/Tauri, substitute Electron; every other layer of this plan is unchanged.*

## 3. Application Architecture (draft)

```text
┌────────────────────────────────────────────────────────────────────────┐
│  Haval LocalAI Bench.exe  (Tauri shell, signed)                        │
│                                                                        │
│  ┌──────────────────────────────┐   ┌───────────────────────────────┐  │
│  │  React UI (WebView2)         │   │  Rust core commands           │  │
│  │  Home · Doctor · Models ·    │   │  · spawn/stop hidden procs    │  │
│  │  Benchmark · Reports ·       │◄──┤  · UAC elevation broker       │  │
│  │  Settings                    │   │  · registry/app discovery     │  │
│  │  tokens.css (design system)  │   │  · file dialogs, Show in      │  │
│  └───────────▲──────────────────┘   │    folder, open report        │  │
│              │ HTTP + SSE (localhost, token)  └────────▲─────────────┘  │
└──────────────┼──────────────────────────────────────────┼──────────────┘
               │                                          │ supervises
┌──────────────▼──────────────────────────────────────────┴──────────────┐
│  Bench Engine  (bundled Python 3.12, FastAPI @ 127.0.0.1:<port>)       │
│                                                                        │
│  doctor/        environment checks · acceleration probe · repair flows │
│  ollama/        client (API) · locator · process manager · installer   │
│  models/        inventory · preferred catalog · search · download queue│
│  bench/         run orchestrator · scenario runner · fixtures · timing │
│  grading/       rule checks · validators · code sandbox · JSON schema  │
│                 · golden answers · grounding checks · rubric judge     │
│  scoring/       Qw/Ew/Rw/Ww · persona · business · S[m] · gates/floors │
│  data/          run store (SQLite) · CSV export · config packs         │
│  report/        Jinja2 → self-contained HTML · PDF export (print)      │
└───────────────▲────────────────────────────────────────────────────────┘
                │ HTTP (localhost:11434)
        ┌───────┴────────┐
        │  Ollama service │  ← installed/started/repaired by the app
        └────────────────┘
```

**Process rules:** the shell launches and supervises the engine (restarts on crash, kills on exit); every child process starts with a hidden window; nothing privileged runs in the engine — elevation requests route through the Rust broker so UAC prompts are rare, explained, and only when genuinely required.

### 3.1 Module responsibilities

- **doctor/** — implements the 17-step diagnostic sequence, probe classification table, and all repair flows from PRD §3. Emits check states (Checking/Passed/Warning/Repairing/Failed/Blocked-by-policy) over SSE. Writes `doctor-snapshot.json` and the support log. Includes the false-acceleration sanity model (expected CPU-only tok/s ranges per hardware class, shipped as config).
- **ollama/** — single client for all Ollama interaction. Locator searches default + custom install paths and registry; process manager starts/stops by resolved full path; installer downloads the official installer over HTTPS, verifies, executes. Downloads use `/api/pull` streaming (status, completed/total bytes → progress %, speed, ETA); `ollama stop` between models to guarantee clean sequential loads.
- **models/** — inventory from `/api/tags` (+ `/api/show` for family/params/quant/digest), preferred-catalog JSON (config-driven, updatable; per Decision D-2 the catalog ships **without GPT-OSS 20B** — the Standard Roster is Gemma 4 26B, Qwen 3 Coder 30B, Kimi Linear 48B, Qwen 3 Next 80B, GPT-OSS 120B; per Decision D-5 any user-selected model may still join a benchmark and its report), Ollama search, hardware-fit estimator (model bytes + KV-cache estimate vs VRAM/unified memory → Excellent/Strong/Partial/Not suitable), sequential download queue with the 8 PRD states, post-download validation (load test + acceleration check → 5 classifications).
- **bench/** — run orchestrator: builds the run plan (selected models × 60 scenarios × ≥3 attempts), executes strictly sequentially, streams progress (model i of n, persona j of 20, current dimension, elapsed), supports Pause (between attempts) and Stop (finalize partial run as incomplete). Scenario runner loads fixture, sends prompt with temperature 0/top_p 1/seed 42, records TTFT (first streamed token), total time, load duration, token counts, and memory telemetry sampled during generation; enforces technical timeouts separately from acceptance targets.
- **grading/** — grader registry keyed by the matrix's "Recommended Grader" column: `rules` (counts, formats, banned words, line/word/char limits), `exact`/`numeric-tolerance`, `schedule-validator`, `decision-rules`, `diff-facts`, `json-schema` (jsonschema lib + value checks), `golden` (golden answers/paths/conflict sets), `grounding` (atomic-claim vs fixture matching), `code-sandbox` (run generated code + hidden tests in a subprocess with no network, temp cwd, CPU/memory/time limits), `rubric-judge` (see §6.4). Each grader returns per-dimension 0–4 scores + hard-gate results + evidence.
- **scoring/** — pure, deterministic, fully unit-tested implementation of PRD §6: dimension normalization ×25, explicit per-scenario dimension weights (40/60 primary rule as generator/fallback — Decision D-3), g(r) timing curve, E mixes, reliability, geometric Ww, persona 25/40/35, business equal-weight means, coverage guards, component floors, global S[m] with H, and category mapping per Decision D-1: **all internal calculation, gates, and floors use the 7-level technical taxonomy; a fixed mapping converts to the 6-level customer-facing taxonomy at every display surface** (UI + report): Excellent→Excellent, Strong→Strong, Good (70–79)→Acceptable Match, Acceptable (60–69)→Marginal Match, Marginal (50–59) and Not Acceptable (<50)→Not Recommended, Failed to Complete→Failed. Both the internal label and the displayed label are stored with every score, plus cap-reason tracking. All weights/bands/floors load from a **versioned `ruleset.json`** — never hardcoded.
- **data/** — creates `runs/<runId>/run.sqlite` with the schema below, writes raw outputs to `raw/`, exports the nine CSVs at completion, and guarantees immutability (append-only; report regeneration reads only this store).
- **report/** — Jinja2 template built from the normative HTML example; fills sections 00–09; em-dash/failure insets; measured-vs-hypothetical banner; inline SVG icon set; print stylesheet doubles as PDF export (WebView2 print-to-PDF via the shell).

### 3.2 Per-run SQLite schema (draft)

```sql
run(run_id PK, started_at, finished_at, app_version, ruleset_version,
    scenario_pack_version, machine_id, status, settings_json)
hardware(run_id FK, product_name, form_factor, cpu_vendor, cpu_model, cores,
    threads, gpu_name, gpu_count, vram_mb, backend, ram_mb, ram_type,
    unified BOOLEAN, storage_free_gb)
model(run_id FK, model_id PK, source_name, display_name, family, architecture,
    total_params, active_params, moe BOOLEAN, quantization, model_bytes,
    digest, roster_order, excluded_from_report BOOLEAN)
scenario(scenario_id PK, version, business, persona, intensity, prompt,
    fixture_id, fixture_version, primary_dimension, weights_json,
    ttft_target_s, total_target_s, completion_limit_s, gates_json,
    grader, rubric_version)
attempt(attempt_id PK, run_id, model_id, scenario_id, attempt_no,
    load_time_ms, ttft_ms, total_ms, prompt_tokens, output_tokens,
    tok_per_s, mem_used_mb, host_mem_mb, vram_headroom_mb,
    technical_status, error_detail, raw_output_path)
quality_score(attempt_id FK, dimension, raw_0_4, normalized, is_primary,
    gate_failed BOOLEAN, evidence_json, grader_version)
workload_score(run_id, model_id, persona, intensity, q, e, r, w_raw,
    candidate_category, final_category, cap_reason)
persona_score(run_id, model_id, persona, p_overall, q_diag, e_diag, r_diag,
    category, cap_reason)
business_score(run_id, model_id, business, score, category, coverage_json,
    is_winner BOOLEAN)
suitability(run_id, model_id, q_overall, e_overall, h_fit, s_score,
    hardware_zone, category, gate_reasons_json, customer_task_est_s)
```

CSV exports mirror these tables 1:1 (PRD §8.1).

### 3.3 Key API surface (UI ⇄ engine)

`GET /doctor/status` · `POST /doctor/run` · `POST /doctor/repair` · SSE `/doctor/events`
`GET /models/installed` · `GET /models/preferred` · `GET /models/search?q=` · `POST /downloads` · `POST /downloads/{id}/cancel|retry` · SSE `/downloads/events`
`POST /bench/start` · `POST /bench/pause|resume|stop` · SSE `/bench/events` · `GET /bench/state`
`GET /runs` · `GET /runs/{id}` · `POST /runs/{id}/report` · `POST /runs/{id}/export-pdf` · `GET /runs/{id}/csv.zip`
`GET/PUT /settings`

## 4. Design & Mockup Implementation

- **Source of truth:** the exported `Haval LocalAI Bench (standalone).html` mockup (6 screens: Home, Doctor, Models, Benchmark, Reports, Settings inside a Windows 11 frame) + the UI Design Baseline doc. Port the mockup's markup/styles into React components; extract every color/spacing/type value into `tokens.css` custom properties exactly as the baseline tables define them.
- **Fonts:** bundle Fraunces + Inter (verify license files ship in the installer); fallbacks Georgia / Segoe UI Variable; Cascadia Mono → Consolas for technical values.
- **Icons:** one rounded-line icon family (the mockup uses Lucide — adopt it; 18–20 px, ~1.6 px stroke); no emoji as UI icons.
- **Component inventory to build once, reuse everywhere:** AppHeader (brand, pill tabs, health pill, help), Card/ElevatedCard, PrimaryButton/Secondary/Tertiary/Destructive, StatusPill (icon+label+color, 6 semantic states), ProgressBar (Border track / Accent fill), ModelRow, ChecklistItem (Doctor), StatTile (metric), SegmentedFilter, SearchInput, Toast, CollapsibleLog, ReportCard, SettingRow.
- **Accessibility from day one:** semantic HTML + ARIA in WebView2 (exposed through UIA), focus rings, reduced-motion media query, High Contrast (forced-colors) stylesheet, full keyboard navigation, ≥32 px targets.
- **Theming:** all colors flow through tokens; a future dark theme = a second token sheet, deliberately designed later.

## 5. Doctor & Repair — Implementation Notes

- OS check: `RtlGetVersion`/registry build number (Windows 11 = build ≥ 22000).
- Hardware detect: WMI `Win32_Processor`, `Win32_VideoController` (AdapterRAM unreliable for >4 GB — prefer registry `HardwareInformation.qwMemorySize` and `nvidia-smi`/DXGI when available), `Win32_PhysicalMemory`, `psutil.disk_usage`.
- Ollama discovery order: stored config path → `%LOCALAPPDATA%\Programs\Ollama` → Program Files → App Paths registry → uninstall registry keys → `where ollama` (last). Validate candidate by `--version` exit code. Persist resolved path.
- API readiness: poll `GET /api/tags` with backoff; port-conflict diagnosis via `psutil.net_connections` on 11434.
- Acceleration probe: pick smallest installed chat model (or pull `llama3.2:1b`/`gemma3:1b` with consent) → `POST /api/generate` (temp 0, `num_predict` ≈ 64) capturing TTFT and eval rate → `GET /api/ps` while loaded for the processor split (`size_vram` vs `size`) → supplemental vendor telemetry → compare tok/s against the config-shipped CPU-only sanity band → classify per PRD table.
- Every repair action = idempotent step with plain-language name, technical log line, and rollback-safety note; the "Repair Automatically" button runs the ordered chain and streams states.

## 6. Benchmark, Grading & Scoring — Implementation Notes

### 6.1 Scenario pack

Ship as versioned data: `scenarios.json` generated from the Evaluation Matrix workbook (60 rows, IDs like `C-EO-L` … `B-PLC-H`), plus a `fixtures/` folder. Per Decision D-3, every scenario record carries **explicit numeric dimension weights summing to 1** — the workbook marks only the primary dimension, so authoring the 60 weight sets is an M3 deliverable (generated by the 40/60 rule, then hand-reviewed and adjusted where a scenario warrants it; the 40/60 generator remains the fallback for any scenario without explicit weights). Per Decision D-7, fixtures are **AI-authored** to accelerate M3, under the guardrail in §6.6. **~20 fixtures must be produced** (WEEK_PLAN, CELL_ENERGY_10P, FAMILY_WEEK/MONTH, LAPTOP_5, VEHICLE_COMPARE, APPLICATION_DRAFT, CREATOR_BRIEF, RELOCATION_CASE, PC_DIAGNOSTIC, CASUAL_GAMER_PROFILE+GAME_CATALOG, GAME_BENCH_LOGS, GAMEPLAY_TRANSCRIPT+CHANNEL_BRIEF, QUARTER_UPDATE, BOARD_REPORT_10P, PROJECT_SNAPSHOT, PROGRAM_PACK, FINANCE_MODEL, COMPETITOR_TABLE+quotes, PRODUCT_RESEARCH_PACK, ACCOUNT_PACK+APPROVED_CLAIMS, KB_KEYBOARD, CASE_HISTORY+DEVICE_LOGS, POLICY_2025/2026, CONTRACT_25P) — each with seeded golden answers/conflicts and a version stamp. This is real content work; it is scheduled as its own phase (M3).

### 6.2 Timing integrity

TTFT = time from request start to first streamed token (Ollama streaming); total = last token; load time from Ollama's `load_duration`; keep the machine otherwise idle-checked (warn if CPU/GPU busy before run); `ollama stop` + short settle between models; memory sampling on a side thread at ~1 Hz so measurement never blocks generation.

### 6.3 Hardware Fit (H) — adopted formula (Decision D-8; versioned in ruleset.json)

```text
headroom_ratio = free_accel_memory_during_run / total_accel_memory
offload_health = fraction of model resident on accelerator (from /api/ps split)
stability      = 100 if no swap/instability events; scaled down per event
H = 100 × clamp( 0.45·offload_health + 0.35·min(1, headroom_ratio/0.15)
                 + 0.20·stability/100 , 0, 1 )
```

Severe swapping or <100% load success trips the PRD's Marginal cap regardless of H.

### 6.4 Rubric judge (Decision D-6 — adopted)

Rubric-graded dimensions (Creative Quality; some Reasoning/Factual rubrics) use a **local LLM judge**: the strongest *installed* model that is not the model under test (preferring an instruction-strong mid-size model), run at temperature 0 with the scenario's rubric converted to a strict JSON-output scoring prompt; judge model + version recorded in the evidence. Where no second model exists, the app grades deterministic dimensions only and marks rubric dimensions "Insufficient Data" rather than self-judging. (Alternative accepted by the methodology: human rubric grading in a review mode — out of scope V1.)

### 6.5 Code sandbox

Generated code runs via the bundled Python: dedicated subprocess, temp working dir, no network (job object + socket-blocking site hook), 5 s CPU/512 MB caps, hidden window; hidden tests injected after the model's code; verdicts + stdout captured as evidence. Only Python code scenarios exist in the pack (G-RD-B/H, B-EN-L/B/H); GDScript scenario G-RD-L grades by token/structure rules, not execution.

### 6.6 Fixture authoring pipeline (Decision D-7 — AI-automated, with validation guardrail)

Fixtures are generated by AI from each scenario's requirements to accelerate M3, but a fixture's **seeded golden answers are the ground truth every model score rests on**, so no AI-generated fixture ships unverified. Required pipeline per fixture: (1) AI drafts the fixture + its golden answers/seeded conflicts from the scenario spec; (2) a **deterministic validation script** proves the goldens are internally consistent (the seeded schedule really is conflict-free after the golden changes, the arithmetic totals are exact, the seeded root cause is uniquely supported by the logs, the contract's golden obligations exist at the cited clauses, etc.) — one validator per fixture family, reused by the runtime graders; (3) a **human review pass** signs off realism, difficulty, and ambiguity; (4) the fixture is version-stamped and frozen. A fixture that cannot be deterministically validated (purely creative briefs) gets a documented rubric-review instead. Validation scripts are kept in the repo and re-run in CI whenever a fixture changes.

## 7. Packaging, Signing & Updates

- Tauri bundler → NSIS installer; chain VC++ redistributable; embed Python runtime (python-embed + wheels, no py launcher, no PATH changes); EV Authenticode certificate signs installer + all exes (SmartScreen reputation).
- Install per-user by default (no elevation); machine-wide optional.
- App data in `%LOCALAPPDATA%\Haval LocalAI Bench\` per PRD §8.1.
- Updater: Tauri signed updater (or manual download in V1); preferred-model catalog + scenario pack + ruleset are hot-updatable config with version pinning recorded per run.

### 7.1 Installation wizard — Ollama (conditional)

Follow PRD **§3.1a**. The wizard **checks for an existing Ollama install first**.

- **Ollama present:** skip any Ollama/internet page.
- **Ollama missing:** one clear page: internet is required for a **small, fast download of the latest Ollama service**. Do not start the download while offline. Do not bundle Ollama or models in the Haval NSIS package.

Lab: clean VM with no Ollama (must show the page + refuse download offline); VM with Ollama already installed (must skip the page).

## 8. Testing Strategy

1. **Scoring golden tests** — every equation and gate from the methodology's worked examples (e.g., Q=92/E=55/R=100 → raw 79.5 → capped Acceptable; Power Player 93/84/62 → 78.55) as unit tests; property tests for monotonicity and zero-handling; sensitivity harness (±10 pp weight shifts) per PRD §6.12.
2. **Grader tests** — golden fixtures with known-good and known-bad model outputs per scenario; sandbox escape/timeout tests; JSON-schema edge cases.
3. **Doctor simulation matrix** — mock Ollama (missing, stale, wrong port, CPU-only, partial offload, contradictory telemetry) to exercise every probe classification and repair path.
4. **Report snapshot tests** — render from a canned run store; diff against approved HTML; checklist assertions (20 personas × order, em dashes, no invented values, four hardware tiles, no overall winner).
5. **UI tests** — component states (all control states), keyboard navigation, Narrator smoke pass, 100–200% DPI screenshots, minimum window size.
6. **Hardware lab pass** — at least: NVIDIA discrete, AMD discrete, Intel iGPU, AMD APU/unified-memory machines before release.

## 9. Delivery Plan (phases)

| Phase | Scope | Exit criteria |
|---|---|---|
| **M0 — Foundations** (2–3 wks) | Repo, Tauri shell + engine skeleton, tokens.css + component library from mockup, engine supervision, settings | All 6 screens navigable with live design system; engine health endpoint |
| **M1 — Doctor** (3–4 wks) | Detection, Ollama locate/install/start, API polling, acceleration probe, repair flows, support log/report | Doctor passes/repairs on the 4-machine lab matrix; readiness gate wired |
| **M2 — Model Library** (2–3 wks) | Inventory, preferred catalog, search, sequential download queue via /api/pull, post-download validation, fit estimator, selection gating | All §11.1 model-library acceptance items |
| **M3 — Scenario pack & fixtures** (3–4 wks, parallel content track) | 60 scenarios encoded, ~20 fixtures authored with golden answers, grader registry, code sandbox, rubric-judge | Every scenario grades correctly against seeded good/bad outputs |
| **M4 — Benchmark engine + scoring** (3 wks) | Orchestrator, timing capture, ≥3 attempts, pause/stop, run store + CSV export, full scoring pipeline with the D-1 dual taxonomy (internal 7-level + display mapping) and D-4 dual thresholds | Golden scoring tests green; complete run.sqlite + 9 CSVs from an end-to-end run |
| **M5 — Reports** (2–3 wks) | Jinja2 report (sections 00–09), Reports tab, PDF export, Show in folder | Report acceptance checklists §11.2/§11.3 green; byte-stable regeneration |
| **M6 — Hardening & release** (2–3 wks) | Accessibility pass, High Contrast, crash resilience, installer + signing, **Ollama internet check in the install wizard (§7.1)**, docs, lab regression | Design acceptance §11.4; signed installer; wizard skips Ollama when already installed and states a small/fast latest-service download when it is not |

Total ≈ 4–5 months with a 2–3 person team (1 UI, 1 engine, shared content/QA); the fixture/content track (M3) is the schedule risk and starts early.

## 10. Risk Register

| Risk | Impact | Mitigation |
|---|---|---|
| Preferred-model tags change/vanish upstream | Downloads fail | Config-driven catalog, remote-updatable; per-model failure never kills queue |
| VRAM detection unreliable on some adapters | Wrong fit estimates | Multi-source detection + probe-measured truth overrides estimates |
| Heavy scenarios × 3 attempts × many models = very long runs | User abandons | Honest ETA from measured throughput; pause/resume; per-model completion; report renders from partial run as "incomplete" |
| Local LLM judge variance for creative rubrics | Score instability | Temp-0 judge, strict JSON rubric, judge version recorded; flagged as "rubric-judged" in evidence; calibration study post-V1 |
| Antivirus/enterprise policy blocks engine or sandbox | Setup fails | Signed binaries, native API calls over scripts, Doctor policy-block explanations + IT report |
| Ollama API changes | Breakage | Pin minimum version; Doctor verifies version; abstraction layer in ollama/ module |
| AI-generated fixture with wrong golden answers (D-7) | Silently corrupts every model's score on that scenario | Mandatory validation pipeline §6.6 (deterministic golden verification + human sign-off + CI re-validation) |
| Dual taxonomy mapping drift (D-1) | Internal and displayed labels disagree | Mapping lives once in ruleset.json; both labels stored per score; snapshot tests assert the mapping |

## 11. Immediate Next Steps

1. Amend the PRD for the resolved decisions (D-1…D-8 below) — in particular the preferred-model catalog and its acceptance criterion change from six to **five** models (D-2), and the scenario record schema gains mandatory explicit weight sets (D-3).
2. Confirm the stack recommendation (Tauri vs Electron fallback) against team skills.
3. Approve the per-run schema (§3.2) and the ruleset.json shape (now carrying the D-1 taxonomy mapping, D-4 thresholds, and D-8 formula).
4. Start M0 and the fixture-authoring content track (with the §6.6 validation pipeline) in parallel.

## 12. Resolved Decisions

All eight PRD open issues (OI-1…OI-8) are decided. Each decision is binding for implementation; caveats note the follow-through work the decision creates.

| ID | Decision | Details & caveats |
|---|---|---|
| **D-1** (OI-1) | **Dual taxonomy** | The engine uses the 7-level technical taxonomy (Scoring Methodology) for all internal calculation, component floors, gates, and stored raw labels. A fixed mapping converts to the 6-level customer-facing taxonomy (Report Requirements) for every UI display and the Final Report: Good (70–79)→Acceptable Match; Acceptable (60–69)→Marginal Match; Marginal (50–59) and Not Acceptable (<50)→Not Recommended; Failed to Complete→Failed. Both labels are persisted per score; the mapping is versioned in ruleset.json. |
| **D-2** (OI-2) | **GPT-OSS 20B removed from Preferred Models** | The preferred catalog and download suggestions exclude GPT-OSS 20B, keeping Model Library and report roster consistent. *Caveat:* the prerequisites document's acceptance criterion "all six Haval Preferred Models appear" becomes **five**; the PRD and catalog config must be amended (Next Step 1). A user can still install/select it manually (see D-5). |
| **D-3** (OI-3) | **Scenario-specific quality weights** | Every scenario record carries explicit per-dimension weights summing to 1 (e.g., coding .40 / reasoning .25 / IF .20 / structured .15). *Caveat:* the Evaluation Matrix marks only primary dimensions, so all 60 weight sets must be authored in M3 — generated by the 40/60 rule, then reviewed and tuned; the 40/60 generator remains the documented fallback. |
| **D-4** (OI-4) | **Dual-layer quality thresholds** | 75/100 is the engine-level scenario "quality pass" diagnostic flag (stored, surfaced in diagnostics). The 55 (Not Recommended) and 65 (cap at Acceptable) gates govern customer-facing report labels. Both layers apply simultaneously and are versioned in ruleset.json. |
| **D-5** (OI-5) | **Standard Roster + open selection** | The 5-model list (Gemma4-26B → Qwen3-30B → Kimi-48B → Qwen3-80B → GPT-120B) is the Standard Roster and default report order; the engine supports any number of user-selected models in a benchmark and its report, with roster models keeping the prescribed order and extra models appended deterministically. |
| **D-6** (OI-6) | **Automated local LLM judge** | Rubric dimensions (Creative Quality; rubric-graded Reasoning/Factual) are scored by the strongest installed model that is not under test, temperature 0, strict JSON rubric output; judge model + version recorded in evidence. If no second model exists, rubric dimensions report "Insufficient Data" rather than self-judging. Post-V1 calibration study still planned. |
| **D-7** (OI-7) | **AI-automated fixture generation** | Fixtures are AI-authored from scenario requirements to accelerate M3 — under the mandatory §6.6 guardrail: deterministic golden-answer validation, human sign-off, version freeze, CI re-validation. An unvalidated fixture never ships. |
| **D-8** (OI-8) | **Hardware Fit formula adopted** | `H = 100 × clamp(0.45·offload_health + 0.35·min(1, headroom_ratio/0.15) + 0.20·stability/100, 0, 1)` as specified in §6.3, versioned in ruleset.json, with the PRD's severe-swap/instability Marginal cap applying regardless of H. Coefficients to be sanity-checked on the four-machine hardware lab during M4. |

*End of Build Plan & Architecture.*
