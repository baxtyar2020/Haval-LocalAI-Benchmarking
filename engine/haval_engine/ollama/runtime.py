from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from haval_engine.paths import settings_path
from haval_engine.winproc import run_hidden


def load_settings() -> dict:
    path = settings_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_settings(data: dict) -> None:
    current = load_settings()
    current.update(data)
    settings_path().write_text(json.dumps(current, indent=2), encoding="utf-8")


def _registry_paths() -> list[Path]:
    paths: list[Path] = []
    try:
        import winreg
    except ImportError:
        return paths
    roots = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\App Paths\ollama.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ollama.exe"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Ollama"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall\Ollama"),
    ]
    for hive, key_path in roots:
        try:
            key = winreg.OpenKey(hive, key_path)
        except OSError:
            continue
        for name in ("", "Path", "InstallLocation", "DisplayIcon"):
            try:
                value, _ = winreg.QueryValueEx(key, name)
            except OSError:
                continue
            if not value:
                continue
            candidate = Path(str(value).strip().strip('"'))
            if candidate.suffix.lower() != ".exe":
                candidate = candidate / "ollama.exe"
            paths.append(candidate)
    return paths


def candidate_exes() -> list[Path]:
    found: list[Path] = []
    stored = load_settings().get("ollama_exe")
    if stored:
        found.append(Path(stored))
    local = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
    found.append(local)
    pf = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Ollama" / "ollama.exe"
    found.append(pf)
    pfx86 = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Ollama" / "ollama.exe"
    found.append(pfx86)
    found.extend(_registry_paths())
    which = shutil.which("ollama")
    if which:
        found.append(Path(which))
    unique: list[Path] = []
    seen: set[str] = set()
    for path in found:
        key = str(path).lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def validate_exe(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        result = run_hidden([str(path), "--version"], timeout=8)
    except Exception:
        return None
    if result.returncode != 0:
        return None
    text = (result.stdout or result.stderr or "").strip().splitlines()
    return text[0] if text else "ollama"


def locate() -> tuple[Path | None, str | None]:
    for path in candidate_exes():
        version = validate_exe(path)
        if version:
            save_settings({"ollama_exe": str(path)})
            return path, version
    return None, None
