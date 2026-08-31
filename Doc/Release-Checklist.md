# Haval LocalAI Bench — release and lab checklist

Unsigned NSIS builds are expected until an EV Authenticode certificate is available. Do not invent a signature.

## Accessibility (desktop)

- [ ] Keyboard-only: Tab order matches visual order; focus ring visible on every control.
- [ ] Skip link appears when focused and jumps to main content.
- [ ] Alt+1–6 switches Home / Doctor / Models / Benchmark / Reports / Settings.
- [ ] Escape closes Help.
- [ ] Narrator announces tab names, Doctor health pill, and benchmark progress (live region).
- [ ] Windows High Contrast: text, buttons, and cards remain outlined; primary actions use Highlight.
- [ ] Settings → Ease of Access → Visual effects → Animation effects Off: no decorative motion.
- [ ] Display scaling 100%, 125%, 150%, 200%: window min size 1100×720 still usable.
- [ ] Click targets are at least 40 px high (nav, buttons, icon button).

## Crash resilience

- [ ] Kill the hidden Python engine process while the UI is open: the sidecar should restart on the same port; UI reconnects.
- [ ] Incomplete runs remain in `%LOCALAPPDATA%\Haval LocalAI Bench\runs\` (no invented scores).
- [ ] Forced engine exception appends to `support.log`.
- [ ] UI error boundary shows a recovery screen without wiping stored runs.

## Packaged app (NSIS)

Customer installer (themed wizard + bundled Python). From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1
```

See [installer/README.md](../installer/README.md) for the folder map and wizard pages.

Installer lands under `app/src-tauri/target/release/bundle/nsis/`.

- [ ] Wizard title and body say **Haval LocalAI Benchmarking** (not “Bench”).
- [ ] Cream / burnt-orange pages; sidebar and header illustrations present.
- [ ] Install for current user (no admin required for the default NSIS mode).
- [ ] If Ollama is already installed, the Ollama page is skipped.
- [ ] If Ollama is missing: page copy matches PRD §3.1a; Download while offline does not start; “I’ll connect later” still installs Haval.
- [ ] WebView2 present (Windows 11) or bootstrapper if targeting older images.
- [ ] Packaged resources include `config/`, `haval_engine/` (or `engine/haval_engine`), and `python\python.exe`.
- [ ] `HAVAL_REPO_ROOT` / `HAVAL_CONFIG_DIR` resolve in the sidecar (Doctor, library, pack, scoring, report).
- [ ] No extra PATH mutation; no visible consoles during Doctor or bench.
- [ ] After install, Doctor run + library list works without the git checkout.

## Signing (when a real cert exists)

See `Doc/Code-Signing.md`. Use `scripts/sign-release.ps1` on the setup EXE and the app EXE. Never commit PFX files.

## Lab regression (do not skip math)

- [ ] Pack still has **60** scenarios, **3** attempts each.
- [ ] Start Benchmark gated: Doctor environment ready + at least one selected model.
- [ ] Optional smoke: `$env:HAVAL_BENCH_MAX_SCENARIOS="1"` then a short run — not a substitute for a full 60×3 lab pass.
- [ ] HTML report: hardware-first, Commercial as the third business name, failed models are insets not fake tables.
- [ ] Do not pull large models unless the lab session is meant to.

## Support bundle

Collect `%LOCALAPPDATA%\Haval LocalAI Bench\support.log`, `doctor-snapshot.json`, and the run folder for the failing `run_id`.
