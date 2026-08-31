"""Answer parsers for Phase 2 (HavalLLMphase2 pack)."""

from __future__ import annotations

import math
import re

_THINK = re.compile(r"<think(?:ing)?[\s>][\s\S]*?</think(?:ing)?>", re.I)
_TRAILING_CTRL = re.compile(
    r"(?:\s*(?:<\|(?:im_end|eot_id|end_of_text|eom_id|end)\|>|</s>))+$",
    re.I,
)
_NUMBER = re.compile(
    r"[-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:e[-+]?\d+)?",
    re.I,
)
_ANSWER_NUMBER = re.compile(
    r"(?:answer|result|total|equals?)\s*(?:is|:)?\s*"
    r"([-+]?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?(?:e[-+]?\d+)?)",
    re.I,
)


def strip_think(text: str) -> str:
    body = _THINK.sub("", text or "")
    body = body.rstrip()
    body = _TRAILING_CTRL.sub("", body)
    return body.strip()


def _parse_numeric_token(token: str) -> float | None:
    try:
        parsed = float((token or "").replace(",", ""))
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def extract_choice(text: str) -> str | None:
    cleaned = strip_think(text)
    if re.fullmatch(r"[A-D]", cleaned, re.I):
        return cleaned.upper()
    answer_is = re.search(r"(?:the\s+)?answer\s+is\s+([A-D])\b", cleaned, re.I)
    if answer_is:
        return answer_is.group(1).upper()
    option = re.search(r"(?:option|choice)\s*[:\-]?\s*([A-D])\b", cleaned, re.I)
    if option:
        return option.group(1).upper()
    prefix = re.match(r"^([A-D])[).:](?!\w)", cleaned, re.I)
    if prefix:
        return prefix.group(1).upper()
    decision = re.search(
        r"\b(?:choose|chosen|pick|picked|answer|final answer)\b[\s:=\-]*(?:option|choice)?[\s:=\-]*([A-D])\b",
        cleaned,
        re.I,
    )
    if decision:
        return decision.group(1).upper()
    end = re.search(r"\b([A-D])\b[\s.!?]*$", cleaned, re.I)
    if end:
        return end.group(1).upper()
    return None


def extract_number(text: str) -> float | None:
    body = strip_think(text)
    labeled = _ANSWER_NUMBER.search(body)
    if labeled:
        return _parse_numeric_token(labeled.group(1))
    found = list(_NUMBER.finditer(body))
    if not found:
        return None
    return _parse_numeric_token(found[-1].group(0))


def math_matches(text: str, answer: float, tolerance: float = 0) -> bool:
    got = extract_number(text)
    if got is None:
        return False
    return abs(got - float(answer)) <= float(tolerance or 0)


def reasoning_matches(text: str, expected: str) -> bool:
    actual = extract_choice(text)
    if actual is None:
        actual = strip_think(text).strip()
    return actual == expected
