from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path


def repo_root() -> Path:
    env = os.environ.get("HAVAL_REPO_ROOT")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    env = os.environ.get("HAVAL_CONFIG_DIR")
    if env:
        return Path(env)
    return repo_root() / "config"


def app_data_dir() -> Path:
    root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    path = root / "Haval LocalAI Bench"
    path.mkdir(parents=True, exist_ok=True)
    return path


def support_log_path() -> Path:
    return app_data_dir() / "support.log"


def snapshot_path() -> Path:
    return app_data_dir() / "doctor-snapshot.json"


def settings_path() -> Path:
    return app_data_dir() / "settings.json"


def cache_dir() -> Path:
    path = app_data_dir() / "cache"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _is_exe(path: Path | None) -> bool:
    return bool(path) and path.is_file()


def locate_python() -> Path | None:
    """Interpreter used for Phase 1 hidden Python tests. Prefer the bundled copy."""
    env = os.environ.get("HAVAL_PYTHON_EXE")
    if env:
        candidate = Path(env)
        if _is_exe(candidate):
            return candidate
    exe = Path(sys.executable)
    if _is_exe(exe) and "python" in exe.name.lower():
        return exe
    root = repo_root()
    for rel in (
        Path("python") / "python.exe",
        Path("python-embed") / "python.exe",
        Path("installer") / "runtime" / "python" / "python.exe",
    ):
        candidate = root / rel
        if _is_exe(candidate):
            return candidate
    which = shutil.which("python") or shutil.which("py")
    return Path(which) if which else None


def locate_node() -> Path | None:
    """Node used for Phase 2 coding hidden tests. Prefer the bundled copy, not PATH."""
    env = os.environ.get("HAVAL_NODE_EXE")
    if env:
        candidate = Path(env)
        if _is_exe(candidate):
            return candidate
    root = repo_root()
    py = locate_python()
    extras: list[Path] = [
        root / "node" / "node.exe",
        root / "installer" / "runtime" / "node" / "node.exe",
    ]
    if py:
        extras.append(py.parent.parent / "node" / "node.exe")
        extras.append(py.parent / "node.exe")
    for candidate in extras:
        if _is_exe(candidate):
            return candidate
    which = shutil.which("node")
    return Path(which) if which else None
