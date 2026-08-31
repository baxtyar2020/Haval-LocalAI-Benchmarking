# Haval LocalAI Bench

Windows 11 desktop app that prepares a PC (Doctor), downloads local models through Ollama, runs hardware-first benchmarks, and writes an evidence-based report.

Current tree: M0–M6. Doctor, Model Library, 60-scenario pack, live sequential benchmark, hardware-first HTML report, accessibility/High Contrast pass, crash logging, NSIS resources, and unsigned installer instructions. Authenticode signing is documented, not faked.

## Layout

- `app/` — Tauri 2 shell + React/TypeScript UI
- `engine/` — Python 3 Bench Engine (FastAPI on `127.0.0.1`)
- `config/preferred-models.json` — five-model Standard Roster (Decision D-2; no GPT-OSS 20B)
- `config/ruleset.json` — taxonomy mapping and scoring constants
- `config/scenarios.json` — 20 personas × Light/Balanced/Heavy (60 scenarios, ≥3 attempts)
- `config/fixtures/` — versioned test assets with deterministic goldens
- HTML reports write to `%LOCALAPPDATA%\Haval LocalAI Bench\runs\<id>\report.html`
- `Doc/` and `Planning/` — product requirements, architecture, [release checklist](Doc/Release-Checklist.md), [code signing](Doc/Code-Signing.md)
- `scripts/prepare-python-embed.ps1` — opt-in embeddable CPython download for offline installers
- `scripts/sign-release.ps1` — Authenticode via `signtool` when a real cert exists

## Run (desktop)

```powershell
cd app
npm install
npm run tauri dev
```

The Rust side starts the engine with a hidden window, a random localhost port, and a bearer token. The UI reads that via `engine_info`.

## Run (UI + engine separately)

```powershell
cd engine
$env:HAVAL_ENGINE_TOKEN="dev-local-token"
$env:HAVAL_ENGINE_PORT="8765"
python -m haval_engine
```

```powershell
cd app
npm run dev
```

Then open `http://localhost:1420`. Settings → Bench Engine uses the sidecar when launched from Tauri; in browser-only mode it expects the engine on port 8765 with token `dev-local-token`.

## Packaged installer (M6)

Full customer installer (themed wizard, bundled Python, **Benchmarking** copy):

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1
```

Layout, wizard pages, and what is / is not bundled: [installer/README.md](installer/README.md).

NSIS output: `app/src-tauri/target/release/bundle/nsis/`. Sign with `scripts/sign-release.ps1` only when you have a real certificate (`Doc/Code-Signing.md`). Lab steps: `Doc/Release-Checklist.md`.

Shell-only bundle without the Python runtime (developers):

```powershell
cd app
npm run tauri build
```

## Engine API (M0–M6)

`GET /health` · `GET /models/preferred` · `GET /models/library` · `POST /models/downloads` · `POST /models/select` · `GET /settings` · `GET /doctor/status` · `POST /doctor/run` · `POST /doctor/repair` · `GET /doctor/events` · `GET /bench/readiness` · `GET /pack/scenarios` · `GET /pack/fixtures` · `POST /bench/start` · `POST /bench/pause` · `POST /bench/stop` · `GET /bench/status` · `GET /bench/runs` · `POST /reports/{id}/render` · `GET /reports/{id}/html` · `GET /reports/{id}/paths`

All routes require `Authorization: Bearer <token>`. Doctor locates and starts Ollama with hidden windows, proves acceleration with a small live probe, and keeps **Start Benchmark** disabled until the environment is ready and at least one library model is selected. The Model Library inventories Ollama, shows the five preferred models, searches the registry, and downloads sequentially. A benchmark run is **20 personas × Light/Balanced/Heavy = 60 scenarios**, each attempted **3 times**, models sequential. Results go to `%LOCALAPPDATA%\Haval LocalAI Bench\runs\`.
