"""Questions shown on the Benchmark screen. Models still get the full generate prompt."""

from __future__ import annotations

import json
import re
from functools import lru_cache

from haval_engine.pack.ask_blurbs import load_phase1_blurbs
from haval_engine.paths import config_dir


@lru_cache(maxsize=1)
def _ui_map() -> dict:
    path = config_dir() / "ui_questions.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _no_json(text: str) -> str:
    body = (text or "").strip()
    body = re.sub(r"\{[^{}]*\}", " ", body)
    body = re.sub(r"\s+", " ", body).strip(" :;,-")
    return body


def phase1_question(scenario: dict) -> str:
    sid = str(scenario.get("id") or "")
    mapped = load_phase1_blurbs().get(sid)
    if mapped:
        return mapped.strip()
    prompt = str(scenario.get("prompt") or "")
    if "--- Fixture" in prompt:
        prompt = prompt.split("--- Fixture", 1)[0]
    prompt = prompt.strip()
    if prompt:
        return prompt
    return str(scenario.get("name") or "Working on this task.")


def phase2_question(category: str, item: dict) -> str:
    if category == "structuredOutput":
        mapped = (_ui_map().get("phase2_structured") or {}).get(str(item.get("id")))
        if mapped:
            return mapped.strip()
    if category in {"reasoning", "math"}:
        return _no_json(str(item.get("question") or ""))
    if category == "instructionFollowing":
        return _no_json(str(item.get("prompt") or ""))
    if category == "coding":
        return _no_json(str(item.get("description") or ""))
    return _no_json(str(item.get("prompt") or item.get("question") or item.get("description") or ""))
