"""HavalLLMphase2 quality datasets. Multilingual and sensitivity are not used."""

from __future__ import annotations

from haval_engine.paths import config_dir


def havalllmphase2_dir():
    return config_dir() / "HavalLLMphase2"


def load_json(name: str) -> list:
    path = havalllmphase2_dir() / name
    import json

    return json.loads(path.read_text(encoding="utf-8"))
