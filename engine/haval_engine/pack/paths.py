from __future__ import annotations

from pathlib import Path

from haval_engine.paths import config_dir, repo_root

__all__ = ["config_dir", "repo_root", "fixtures_dir", "scenarios_path"]


def fixtures_dir() -> Path:
    return config_dir() / "fixtures"


def scenarios_path() -> Path:
    return config_dir() / "scenarios.json"
