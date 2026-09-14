# Haval LocalAI Benchmarking — Windows installer

The **installed app** stays named `Haval LocalAI Bench` (window title, data folder, Start menu).  
The **setup wizard** always says **Haval LocalAI Benchmarking**.

Ollama and models are **not** inside this package. The wizard checks for Ollama first. If it is missing, one page asks for internet and offers a small, fast download of the latest official Ollama service. If Ollama is already on the PC, that page is skipped.

Python and Node.js **are** inside the package when you use the full build command below. Node is required for Phase 2 coding hidden tests. Without it, coding scores 0 even when the model wrote correct JavaScript.

Customer download of a pre-built setup EXE: [which local AI LLM fits your PC](https://havalothman.com/blog/which-local-ai-llm-fits-your-pc). This folder is only for compiling the installer from source.

## One command

From the repository root (needs internet the first time, for Python embed, Node.js, and npm/Rust crates):

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1
```

- **First run** keeps the current version and copies `HavalLocalAIBench-<ver>-setup.exe` to `What-to-ship final\`.
- **Every later run** bumps the patch version and writes the new EXE plus `latest.json` to `What-to-ship final\updates\` (upload both to R2 `havalbencmarkingapp/update/`).

Force a first ship or an update:

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1 -FirstRelease
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1 -Update -Notes "Fixes Doctor GPU label. Your reports stay."
```

Resulting setup EXE:

`app\src-tauri\target\release\bundle\nsis\`

Sign it only with a real certificate (`scripts\sign-release.ps1`). Unsigned local builds are expected until then.

Skip the Python runtime (not for customers):

```powershell
powershell -ExecutionPolicy Bypass -File installer\tools\build-installer.ps1 -SkipPython
```

## Folder map

```
installer/
  README.md                 ← this file
  tauri.bundle.json         ← extra Tauri config used only for the full installer
                              (adds installer/runtime/python as python\ and Node as node\ next to the app)
  nsis/
    installer.nsi           ← Tauri NSIS template (welcome, license, Ollama page, copy files, finish)
    hooks.nsh               ← cream/orange theme, Ollama detect/download, progress bar colors
    English.nsh             ← wizard strings using “Benchmarking”
  assets/
    source/                 ← PNG illustrations (sidebar, header, Ollama page, app icon)
    bmp/                    ← generated NSIS bitmaps + wizard.ico  (created by prepare-assets.ps1)
  runtime/
    python/                 ← generated embeddable CPython + engine wheels (gitignored)
    node/                   ← official Node.js win-x64 node.exe (gitignored)
  tools/
    prepare-assets.ps1      ← PNG → 164×314 / 150×57 BMP + .ico
    prepare-python.ps1      ← official embeddable CPython 3.12 + pip + engine requirements
    prepare-node.ps1        ← official Node.js for Phase 2 coding hidden tests
    build-installer.ps1     ← runs the prepare scripts, then tauri build

app/src-tauri/
  tauri.conf.json           ← NSIS template, icons, header/sidebar, license
  icons/                    ← app icon set used by the EXE and the wizard

scripts/
  sign-release.ps1          ← Authenticode after the EXE exists
```

What is **not** in the NSIS package:

- Ollama
- LLM weights (including the hidden Doctor probe)
- Code-signing certificates

Those stay as download-on-demand (wizard or Doctor).

## Wizard pages (customer order)

1. **Welcome** — sidebar illustration, cream canvas, “Haval LocalAI Benchmarking”.
2. **License** — `LICENSE`.
3. **Folder** — per-user default (`%LOCALAPPDATA%\Haval LocalAI Bench`).
4. **Start Menu** — shortcut name still matches the app EXE.
5. **Ollama** — only if `ollama.exe` is not in the usual Program Files / LocalAppData / App Paths locations.
   - Copy: internet needed; small, fast latest Ollama service.
   - **Download Ollama** (default) or **I'll connect later**.
   - Offline + Download: the wizard does **not** start the download; it explains to connect, or continue and let Doctor finish later.
6. **Installing** — orange smooth progress bar while Haval files (bundled Python and Node.js) are copied.
7. **Finish** — open Haval LocalAI Benchmarking.

## Theme

Matches `app/src/tokens.css`: canvas `#F6F1E9`, ink `#1A1A1A`, accent `#DB4F1B`.  
NSIS cannot run CSS animations; the wizard uses the illustrated bitmaps, a striped/smooth orange progress bar, and a marquee bar during the Ollama download.

## After install

Doctor still runs on first launch (splash → ready, or splash → Doctor if something still needs repair). The probe model is pulled then, not at setup time.
