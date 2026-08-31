"""Normalize instruction-following phrases so seed wording is not a hard wall."""

from __future__ import annotations

import re
import unicodedata

# Compact-form keys (output of fold()).
_ALIASES: dict[str, tuple[str, ...]] = {
    "16gb": ("16 gb", "16g ram", "16 gig", "16 gigabyte", "16 gigabytes"),
    "recommend": (
        "recommend",
        "recommendation",
        "recommended",
        "i would pick",
        "i'd pick",
        "go with laptop",
        "choose laptop",
        "pick laptop",
    ),
    "3pm": ("3 pm", "3:00pm", "3:00 p.m", "15:00", "3.00 pm"),
    "ingredients": ("ingredient", "you'll need", "you will need", "shopping list"),
    "peanut": ("peanuts", "nut-free", "nut free", "no nuts", "avoids peanuts", "peanut-free"),
    "title": ("titles", "headline", "headlines"),
    "meeting": ("meet", "call at 3"),
    "py 0p": ("py -0p", "py -0", "py0p"),
}


def fold(text: str) -> str:
    t = unicodedata.normalize("NFKC", text or "").lower().replace("\u00a0", " ")
    t = t.replace(",", "")
    t = re.sub(r"(\d+)\s*(g\.?\s*b\.?|gigabytes?)\b", r"\1gb", t)
    t = re.sub(r"(\d{1,2}):00\s*p\.?\s*m\.?", r"\1pm", t)
    t = re.sub(r"(\d{1,2})\s*p\.?\s*m\.?", r"\1pm", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def compact(text: str) -> str:
    return re.sub(r"\s+", "", fold(text))


def _date_swaps(folded: str) -> list[str]:
    parts = folded.split()
    if len(parts) != 2:
        return []
    a, b = parts
    if a.isdigit() and b.isalpha():
        return [f"{b} {a}", f"{b}{a}"]
    if b.isdigit() and a.isalpha():
        return [f"{b} {a}", f"{a}{b}"]
    return []


def contains_phrase(haystack: str, needle: str) -> bool:
    h = fold(haystack)
    n = fold(needle)
    if not n:
        return False
    hc = compact(haystack)
    candidates = [n, *(_date_swaps(n))]
    for cand in candidates:
        if cand in h:
            return True
        cc = compact(cand)
        if len(cc) >= 5 and cc in hc:
            return True
    for alt in _ALIASES.get(n, ()):
        af = fold(alt)
        if af and (af in h or (len(compact(alt)) >= 5 and compact(alt) in hc)):
            return True
    return False


def phrase_matches(haystack: str, spec: str) -> bool:
    """A must-token may list equivalents as `sleep|go to bed|bedtime`."""
    alts = [p.strip() for p in (spec or "").split("|") if p.strip()]
    if not alts:
        return False
    return any(contains_phrase(haystack, p) for p in alts)
