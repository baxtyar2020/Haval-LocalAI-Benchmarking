"""Point tests at the real repo config, not a leftover HAVAL_REPO_ROOT (e.g. portable-app)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _haval_repo_config(monkeypatch):
    monkeypatch.setenv("HAVAL_REPO_ROOT", str(_REPO))
    monkeypatch.delenv("HAVAL_CONFIG_DIR", raising=False)
    from haval_engine.scoring.rules import load_ruleset

    load_ruleset.cache_clear()
    yield
    load_ruleset.cache_clear()
