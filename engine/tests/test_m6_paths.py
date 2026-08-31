from __future__ import annotations

import os
from pathlib import Path

from haval_engine.paths import config_dir, repo_root


def test_config_dir_follows_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HAVAL_CONFIG_DIR", str(tmp_path))
    assert config_dir() == tmp_path


def test_repo_root_follows_env(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("HAVAL_REPO_ROOT", str(tmp_path))
    assert repo_root() == tmp_path
    monkeypatch.delenv("HAVAL_REPO_ROOT", raising=False)
    monkeypatch.delenv("HAVAL_CONFIG_DIR", raising=False)
    root = repo_root()
    assert (root / "config" / "ruleset.json").exists()
    assert config_dir() == root / "config"
    assert os.environ.get("HAVAL_REPO_ROOT") is None
