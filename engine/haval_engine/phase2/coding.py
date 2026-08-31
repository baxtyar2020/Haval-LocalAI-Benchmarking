from __future__ import annotations

import json
import shutil
from pathlib import Path

from haval_engine.winproc import run_hidden

SANDBOX_TIMEOUT_MS = 5000
DIFFICULTY_WEIGHT = {"easy": 1, "medium": 2, "hard": 3}
CODING_PROMPT = (
    "Write a JavaScript function with the following signature:\n"
    "{signature}\n\n"
    "{description}\n\n"
    "Reply with ONLY the function code, no explanation."
)


def sandbox_path() -> Path:
    return Path(__file__).with_name("coding_sandbox.js")


def item_weight(item: dict) -> int:
    return int(DIFFICULTY_WEIGHT.get(str(item.get("difficulty") or "medium").lower(), 2))


def isolated_wall_s(task: dict) -> float:
    n = len(task.get("tests") or [])
    estimated_ms = (n + 1) * SANDBOX_TIMEOUT_MS + 1000
    return max(8.0, min(60.0, estimated_ms / 1000.0))


def run_coding_tests(text: str, item: dict) -> dict:
    """Run hidden tests in an isolated Node vm."""
    total = len(item.get("tests") or [])
    empty = {"passed": 0, "total": total, "all_passed": False}
    node = shutil.which("node")
    if not node or not sandbox_path().is_file():
        return empty
    payload = json.dumps(
        {
            "text": text or "",
            "task": {
                "functionName": item.get("functionName"),
                "tests": item.get("tests") or [],
            },
            "sandboxTimeoutMs": SANDBOX_TIMEOUT_MS,
        }
    )
    try:
        result = run_hidden(
            [node, str(sandbox_path())],
            timeout=isolated_wall_s(item) + 2,
            input_text=payload,
        )
    except Exception:
        return empty
    try:
        parsed = json.loads((result.stdout or "").strip() or "{}")
    except json.JSONDecodeError:
        return empty
    passed = int(parsed.get("passed") or 0)
    reported = int(parsed.get("total") if parsed.get("total") is not None else total)
    return {
        "passed": passed,
        "total": reported,
        "all_passed": reported > 0 and passed == reported,
    }


def grade_coding_js(text: str, item: dict, timeout: float = 8) -> bool:
    del timeout
    return bool(run_coding_tests(text, item).get("all_passed"))


def weighted_coding_pct(items: list[dict], details: list[dict]) -> float:
    """All-or-nothing per task, then easy=1 / medium=2 / hard=3."""
    weighted_passed = 0
    weighted_total = 0
    for i, item in enumerate(items):
        weight = item_weight(item)
        weighted_total += weight
        if i < len(details) and details[i].get("correct"):
            weighted_passed += weight
    if weighted_total <= 0:
        return 0.0
    return 100.0 * weighted_passed / weighted_total
