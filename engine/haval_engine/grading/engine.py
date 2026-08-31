"""Phase 1 content: task checks. Code items use Phase 2-style execution pass/fail."""

from __future__ import annotations

import json
from typing import Any

from haval_engine.pack import load_fixture
from haval_engine.grading.match import contains_phrase, phrase_matches
from haval_engine.grading.sandbox import run_python_snippet
from haval_engine.grading.validators import validate_fixture, validate_schedule_json


def _first_json(text: str) -> Any | None:
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def _forbidden_hit(scenario: dict, text: str) -> str | None:
    for phrase in scenario.get("must_not_contain") or []:
        if contains_phrase(text, phrase):
            return phrase
    return None


def _answered(scenario: dict, text: str) -> bool:
    if not (text or "").strip():
        return False
    must = list(scenario.get("must_contain") or [])
    if not must:
        return True
    return all(phrase_matches(text, m) for m in must)


def _shape_ok(scenario: dict, text: str, parsed: Any) -> bool:
    if scenario.get("code_kind") == "python" and scenario.get("grader") == "code":
        return bool(
            run_python_snippet(
                text,
                extra_tests=scenario.get("code_tests") or None,
                prelude=scenario.get("sandbox_prelude") or None,
            ).get("ok")
        )
    if scenario.get("json_required"):
        if not isinstance(parsed, dict):
            return False
        if scenario.get("grader") == "schedule":
            ok, _ = validate_schedule_json(parsed)
            return bool(ok)
        return True
    return True


def _grounded(scenario: dict, text: str, parsed: Any) -> bool | None:
    """None = not applicable (do not award a free 25 points)."""
    hay = (text or "").lower()
    fixture = load_fixture(scenario.get("fixture"))
    numbers = scenario.get("numbers") or {}
    if scenario.get("grader") == "code":
        return None
    if not fixture and not numbers:
        return None
    if fixture:
        ok, _ = validate_fixture(fixture)
        if not ok:
            return False
    for key, want in numbers.items():
        blob = parsed if isinstance(parsed, dict) else {}
        got = blob.get(key)
        if got is not None:
            if abs(float(got) - float(want)) > 0.15:
                return False
            continue
        if str(want) not in hay and str(int(want)) not in hay:
            return False
    return True


def _quality_from_checks(checks: dict[str, bool | None], *, code: bool) -> tuple[float, bool]:
    if code:
        tests_ok = bool(checks.get("shape"))
        safe = bool(checks.get("safe"))
        answered = bool(checks.get("answered"))
        if tests_ok and safe:
            q = 100.0 if answered else 80.0
            return q, True
        if safe and answered:
            return 25.0, False
        if safe:
            return 0.0, False
        return 0.0, False
    active = {k: v for k, v in checks.items() if v is not None}
    if not active:
        return 0.0, False
    q = 100.0 * sum(1 for v in active.values() if v) / len(active)
    return q, all(active.values())


def grade_output(scenario: dict, output: str) -> dict:
    text = output or ""
    parsed = _first_json(text)
    banned = _forbidden_hit(scenario, text)
    checks: dict[str, bool | None] = {
        "answered": _answered(scenario, text),
        "safe": banned is None,
        "shape": _shape_ok(scenario, text, parsed),
        "grounded": _grounded(scenario, text, parsed),
    }
    code = scenario.get("code_kind") == "python" and scenario.get("grader") == "code"
    q, passed = _quality_from_checks(checks, code=code)
    reasons: list[str] = []
    if not checks["answered"]:
        reasons.append("did_not_answer_the_ask")
    if banned:
        reasons.append(f"forbidden:{banned}")
    if not checks["shape"]:
        reasons.append("shape")
    if checks["grounded"] is False:
        reasons.append("not_grounded")
    return {
        "scenario_id": scenario["id"],
        "scores": {k: (25.0 if v else 0.0) for k, v in checks.items() if v is not None},
        "Q": q,
        "hard_fail": not checks["safe"] or (scenario.get("json_required") and not checks["shape"]),
        "reasons": reasons,
        "passed": passed,
        "parsed": parsed if isinstance(parsed, dict) else None,
        "checks": checks,
    }


def grade_seed(scenario: dict, which: str) -> dict:
    return grade_output(scenario, scenario["seeds"][which])
