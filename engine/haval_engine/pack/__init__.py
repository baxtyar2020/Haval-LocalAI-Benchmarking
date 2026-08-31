"""Pack loaders — scenarios.json is generated from matrix.py."""

from __future__ import annotations

import json
from functools import lru_cache

from haval_engine.pack.matrix import scenarios as build_scenarios
from haval_engine.pack.paths import fixtures_dir, scenarios_path


@lru_cache(maxsize=1)
def load_scenarios() -> list[dict]:
    path = scenarios_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return list(data.get("scenarios") or data)
    return build_scenarios()


def write_scenarios_json() -> None:
    path = scenarios_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": "1.0.0",
        "count": 60,
        "attempts_per_scenario": 1,
        "scenarios": build_scenarios(),
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    load_scenarios.cache_clear()
    from haval_engine.pack.ask_blurbs import write_blurbs_json
    from haval_engine.pack.playbook_asks import write_asks_json

    write_asks_json()
    write_blurbs_json()


def load_fixture(name: str | None) -> dict | None:
    if not name:
        return None
    path = fixtures_dir() / f"{name}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
