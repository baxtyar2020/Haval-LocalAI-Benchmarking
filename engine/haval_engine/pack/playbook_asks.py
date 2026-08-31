"""Customer-facing Phase 1 asks, taken from Doc/roles/role-playbooks."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from haval_engine.paths import config_dir, repo_root

_TIER = re.compile(r"^## [123]\.\s*(Light|Balanced|Heavy)\b", re.I | re.M)
_TASK = re.compile(
    r"\*\*Task(?: you inherited)?:\*\*\s*(.+?)(?=\n```|\n### |\n\*\*Expected|\n\*\*What this shows)",
    re.S | re.I,
)
_FENCE_PROMPT = re.compile(
    r"### (?:(?:Chat )?Prompt \(copy / paste\)|What they type[^\n]*)\s*```(?:text)?\n(.*?)```",
    re.S | re.I,
)
_STEP_FENCE = re.compile(
    r"### Step [A-C][^\n]*Chat[^\n]*\s*```(?:text)?\n(.*?)```",
    re.S | re.I,
)
_ANY_TEXT_FENCE = re.compile(r"```(?:text)?\n(.*?)```", re.S)
_JOB = re.compile(r"\*\*Job:\*\*\s*(.+?)(?=\n### |\n```|\n\*\*Expected|\Z)", re.S | re.I)


def playbooks_dir() -> Path:
    return repo_root() / "Doc" / "roles" / "role-playbooks"


def asks_json_path() -> Path:
    return config_dir() / "playbook_asks.json"


def _clean(text: str) -> str:
    body = (text or "").strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def _ask_from_section(section: str) -> str:
    fences = _FENCE_PROMPT.findall(section)
    if not fences:
        fences = _STEP_FENCE.findall(section)
    if not fences:
        fences = _ANY_TEXT_FENCE.findall(section)[:1]
    if fences:
        return _clean("\n\n".join(fences))
    task = _TASK.search(section)
    if task:
        return _clean(task.group(1))
    job = _JOB.search(section)
    if job:
        return _clean(job.group(1))
    return ""


def parse_playbook(path: Path) -> dict[str, str]:
    md = path.read_text(encoding="utf-8")
    hits = list(_TIER.finditer(md))
    out: dict[str, str] = {}
    for i, match in enumerate(hits):
        tier = match.group(1).title()
        start = match.end()
        end = hits[i + 1].start() if i + 1 < len(hits) else len(md)
        ask = _ask_from_section(md[start:end])
        if ask:
            out[tier] = ask
    return out


def parse_all_playbooks() -> dict[str, dict[str, str]]:
    folder = playbooks_dir()
    by_persona: dict[str, dict[str, str]] = {}
    if not folder.is_dir():
        return by_persona
    for path in sorted(folder.glob("*.md")):
        persona = path.stem.replace(" Developer Developer", " Developer")
        by_persona[persona] = parse_playbook(path)
    return by_persona


def asks_by_scenario_id() -> dict[str, str]:
    from haval_engine.pack.matrix import scenarios as build_scenarios

    books = parse_all_playbooks()
    out: dict[str, str] = {}
    for row in build_scenarios():
        ask = (books.get(row["persona"]) or {}).get(row["intensity"]) or ""
        if ask:
            out[row["id"]] = ask
    return out


def write_asks_json() -> Path:
    payload = {"version": "1.0.0", "phase1": asks_by_scenario_id()}
    path = asks_json_path()
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    load_phase1_asks.cache_clear()
    return path


@lru_cache(maxsize=1)
def load_phase1_asks() -> dict[str, str]:
    path = asks_json_path()
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return dict(data.get("phase1") or {})
    return asks_by_scenario_id()
