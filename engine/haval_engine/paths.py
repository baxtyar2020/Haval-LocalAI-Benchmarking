from __future__ import annotations

import os
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
