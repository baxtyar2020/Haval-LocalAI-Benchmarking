from __future__ import annotations

import urllib.request
from pathlib import Path

from haval_engine.paths import cache_dir
from haval_engine.winproc import run_hidden

OLLAMA_SETUP_URL = "https://ollama.com/download/OllamaSetup.exe"


def download_ollama_installer() -> Path:
    dest = cache_dir() / "OllamaSetup.exe"
    urllib.request.urlretrieve(OLLAMA_SETUP_URL, dest)
    if dest.stat().st_size < 1_000_000:
        raise RuntimeError("Downloaded installer looks too small to be valid.")
    return dest


def run_ollama_installer(setup: Path) -> str:
    # Official NSIS installer; /S is silent. UAC may still appear when required.
    result = run_hidden([str(setup), "/S"], timeout=180)
    if result.returncode not in (0, None):
        return f"Installer exited with code {result.returncode}."
    return "Official Ollama installer finished."
