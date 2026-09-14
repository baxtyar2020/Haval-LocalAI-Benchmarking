# Haval LocalAI Bench

Windows desktop app that tests **local** AI models on **this PC**. It checks that acceleration works, lets you download models through Ollama, runs real customer jobs across 20 roles (Consumer, Gaming, Commercial), and writes a hardware-first report: which **LLM size** fits this machine for those jobs — not a cloud leaderboard, and not a “best model in the world” contest.

Work stays on the device.

## Read more / Windows installer

This repository is the **source** so you can inspect, compile, and run from code.

If you want the full product write-up, or a **Windows installer** (no compile), use:

**https://havalothman.com/blog/which-local-ai-llm-fits-your-pc**

## What you need to compile (Windows)

- Windows 10/11 (x64)
- [Node.js](https://nodejs.org/) 20 or newer
- [Rust](https://rustup.rs/) (stable), then `rustup default stable`
- [Python](https://www.python.org/) 3.12, with **Add python.exe to PATH**
- Visual Studio Build Tools with the **Desktop development with C++** workload (for the Rust/Tauri build)
- [WebView2](https://developer.microsoft.com/microsoft-edge/webview2/) (already present on most Windows 11 PCs)

To **run a benchmark** (not required just to compile the UI): install [Ollama](https://ollama.com/) and enough disk for models.

## Run from source

```powershell
git clone https://github.com/baxtyar2020/Haval-LocalAI-Benchmarking.git
cd Haval-LocalAI-Benchmarking
```

Python engine:

```powershell
cd engine
python -m pip install -r requirements.txt
cd ..
```

Desktop app (starts the engine for you):

```powershell
cd app
npm install
npm run tauri dev
```

Or from the repo root: `tauri-dev.bat`.

First Tauri build downloads Rust crates and can take several minutes.

### UI and engine in two terminals

```powershell
cd engine
$env:HAVAL_ENGINE_TOKEN="dev-local-token"
$env:HAVAL_ENGINE_PORT="8765"
python -m haval_engine
```

```powershell
cd app
npm install
npm run dev
```

Open `http://localhost:1420`. Browser-only mode expects the engine on port `8765` with token `dev-local-token`.

## Build the Windows installer

From the repository root (internet on the first run: embeddable Python, Node runtime, npm, Rust crates):

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1
```

Output: `app\src-tauri\target\release\bundle\nsis\`

That command is for people compiling this repo. Ready-made setup EXEs are not stored here. Download those from the article above.

UI-only Tauri bundle (no bundled Python/Node — not the customer installer):

```powershell
cd app
npm run tauri build
```

## Layout

| Path | What it is |
|---|---|
| `app/` | Tauri 2 + React UI |
| `engine/` | Python bench engine (localhost) |
| `config/` | Personas, scenarios, fixtures, scoring rules, preferred models |
| `installer/` | NSIS wizard, assets, and the full pack script |
| `scripts/` | Optional Python embed + Authenticode after you have a real cert |
| `LICENSE` | Terms for this source |

Reports on a machine that has run the app: `%LOCALAPPDATA%\Haval LocalAI Bench\runs\`

## Tests (engine)

```powershell
cd engine
python -m pytest
```

## License

See [`LICENSE`](LICENSE).
