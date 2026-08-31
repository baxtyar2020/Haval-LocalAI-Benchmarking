from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from haval_engine.paths import config_dir


def ruleset_path() -> Path:
    return config_dir() / "ruleset.json"


@lru_cache(maxsize=1)
def load_ruleset() -> dict:
    return json.loads(ruleset_path().read_text(encoding="utf-8"))
