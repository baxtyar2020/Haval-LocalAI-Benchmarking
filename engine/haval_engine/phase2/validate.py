"""Deterministic graders for HavalLLMphase2 instruction-following and structured-output items."""

from __future__ import annotations

import json
import re
from typing import Any


def escape_regex(value: str) -> str:
    return re.escape(value)


def contains_standalone_token(text: str, token: str) -> bool:
    source = escape_regex(token.lower())
    return re.search(rf"(?:^|[^\w]){source}(?:$|[^\w])", text, flags=re.I) is not None


def normalize_expected(value: str) -> str:
    return re.sub(r"[.,;:!?]+$", "", value.strip().strip("\"'`“”‘’()[]{}")).lower()


def validate_instruction_following(response: str, question: dict) -> bool:
    text = (response or "").strip()
    p = question.get("params") or {}
    kind = question.get("validation")

    if kind == "numberedList":
        matches = re.findall(r"^\d+[.)]\s", text, flags=re.M)
        return len(matches) == int(p["expectedCount"])
    if kind == "sentenceCount":
        sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
        return len(sentences) == int(p["expectedCount"])
    if kind == "commaSeparated":
        items = [s.strip() for s in text.split(",") if s.strip()]
        return len(items) == int(p["expectedCount"])
    if kind == "wordCount":
        words = [w for w in text.split() if w]
        return len(words) == int(p["expectedCount"])
    if kind == "paragraphCount":
        paragraphs = [x for x in re.split(r"\n\s*\n", text) if x.strip()]
        return len(paragraphs) == int(p["expectedCount"])
    if kind == "forbiddenWords":
        lower = text.lower()
        return all(not contains_standalone_token(lower, w) for w in p.get("forbidden") or [])
    if kind == "forbiddenLetters":
        lower = text.lower()
        return all(letter.lower() not in lower for letter in p.get("forbidden") or [])
    if kind == "forbiddenPattern":
        try:
            return re.search(str(p["pattern"]), text) is None
        except re.error:
            return False
    if kind == "prosConsStructure":
        pros = re.search(r"(?:^|\n)\s*Pros\s*:\s*([\s\S]*?)(?=(?:\n\s*Cons\s*:)|$)", text, re.I)
        cons = re.search(r"(?:^|\n)\s*Cons\s*:\s*([\s\S]*)$", text, re.I)
        if not pros or not cons:
            return False
        if (pros.start() or 0) >= (cons.start() or 10**9):
            return False

        def count_items(block: str) -> int:
            lines = [ln.strip() for ln in block.splitlines() if ln.strip()]
            bullets = [ln for ln in lines if re.match(r"^([-*]|\d+[.)])\s+", ln)]
            return len(bullets) if bullets else len(lines)

        pi, ci = count_items(pros.group(1) or ""), count_items(cons.group(1) or "")
        if p.get("prosCount") is not None and pi != int(p["prosCount"]):
            return False
        if p.get("consCount") is not None and ci != int(p["consCount"]):
            return False
        return pi > 0 and ci > 0
    if kind == "startEnd":
        lower = text.lower()
        return lower.startswith(str(p["start"]).lower()) and lower.endswith(str(p["end"]).lower())
    if kind == "allQuestions":
        sentences = [s for s in re.split(r"[.!?]\s*", text) if s.strip()]
        if not sentences:
            return False
        return (text.count("?")) >= len(sentences) * 0.8
    if kind == "answerFormat":
        m = re.search(r"^\s*ANSWER:\s*(.+)\s*$", text, re.I | re.M)
        if not m:
            return False
        return normalize_expected(m.group(1)) == normalize_expected(str(p["expectedValue"]))
    if kind == "dashList":
        dashes = re.findall(r"^-\s", text, flags=re.M)
        return len(dashes) == int(p["expectedCount"])
    if kind == "fruitStartLength":
        start = str(p["startLetter"]).lower()
        words = [w for w in re.split(r"[\s,.:;!?]+", text) if re.fullmatch(r"[A-Za-z]+", w)]
        return any(w.lower().startswith(start) and len(w) >= int(p["minLength"]) for w in words)
    if kind == "wordLength":
        words = [w for w in text.split() if re.fullmatch(r"[A-Za-z]+", w)]
        return any(len(w) == int(p["expectedLength"]) for w in words)
    if kind == "listCount":
        count = int(p["expectedCount"])
        numbered = re.findall(r"^\d+[.)]\s", text, flags=re.M)
        dashed = re.findall(r"^-\s", text, flags=re.M)
        comma_items = [s for s in text.split(",") if s.strip()]
        if len(numbered) == count or len(dashed) == count or len(comma_items) == count:
            return True
        lines = [ln for ln in text.splitlines() if ln.strip()]
        return len(lines) == count
    if kind == "planetOrder":
        lower = text.lower()
        j, s = lower.find("jupiter"), lower.find("saturn")
        u, n = lower.find("uranus"), lower.find("neptune")
        if j < 0 or s < 0 or j >= s:
            return False
        third = u if u >= 0 else n
        return third >= 0 and s < third
    return False


def try_parse_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def safe_parse(text: str) -> Any | None:
    """Parse JSON as a whole reply, or one fenced block that is the entire reply."""
    trimmed = (text or "").strip()
    if not trimmed:
        return None
    fenced = re.match(
        r"^```(?:json|javascript|js|typescript|ts)?\s*([\s\S]*?)\s*```$",
        trimmed,
        re.I,
    )
    if fenced:
        return try_parse_json((fenced.group(1) or "").strip())
    return try_parse_json(trimmed)


def has_keys(obj: Any, keys: list[str]) -> bool:
    return isinstance(obj, dict) and all(k in obj for k in keys)


def check_type(value: Any, expected: str) -> bool:
    if expected == "array":
        return isinstance(value, list)
    if expected == "object":
        return isinstance(value, dict)
    if expected == "string":
        return isinstance(value, str)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    return False


def nested(obj: Any, path: list[str]) -> Any:
    cur = obj
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def parse_csv_line(line: str) -> list[str] | None:
    cells: list[str] = []
    current = ""
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        nxt = line[i + 1] if i + 1 < len(line) else ""
        if ch == '"':
            if in_quotes and nxt == '"':
                current += '"'
                i += 2
                continue
            in_quotes = not in_quotes
            i += 1
            continue
        if ch == "," and not in_quotes:
            cells.append(current.strip())
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    if in_quotes:
        return None
    cells.append(current.strip())
    return cells


def non_empty_lines(text: str) -> list[str]:
    return [ln.strip() for ln in re.split(r"\r?\n", (text or "").strip()) if ln.strip()]


def parse_md_row(line: str) -> list[str]:
    trimmed = line.strip()
    if "|" not in trimmed:
        return []
    normalized = f"{'' if trimmed.startswith('|') else '|'}{trimmed}{'' if trimmed.endswith('|') else '|'}"
    return [c.strip() for c in normalized.split("|")[1:-1]]


def is_md_sep(cell: str) -> bool:
    compact = re.sub(r"\s+", "", cell)
    return bool(re.fullmatch(r":?-{3,}:?", compact))


def validate_structured_output(response: str, question: dict) -> bool:
    p = question.get("params") or {}
    kind = question.get("validation")
    if kind == "jsonKeys":
        parsed = safe_parse(response)
        if not isinstance(parsed, dict):
            return False
        keys = list(p.get("keys") or [])
        if not has_keys(parsed, keys):
            return False
        types = p.get("types") or {}
        return all(check_type(parsed[k], types[k]) for k in keys) if types else True
    if kind == "jsonArray":
        parsed = safe_parse(response)
        if not isinstance(parsed, list) or len(parsed) != int(p["length"]):
            return False
        keys = list(p.get("keys") or [])
        types = p.get("types") or {}
        return all(
            has_keys(item, keys) and all((not types.get(k) or check_type(item.get(k), types[k])) for k in keys)
            for item in parsed
        )
    if kind == "jsonNested":
        parsed = safe_parse(response)
        if parsed is None:
            return False
        paths = [p[k] for k in ("path1", "path2", "path3", "path4") if k in p]
        return all(nested(parsed, path) is not None for path in paths)
    if kind == "jsonNumberArray":
        parsed = safe_parse(response)
        if not isinstance(parsed, list) or len(parsed) != int(p["length"]):
            return False
        lo, hi = float(p["min"]), float(p["max"])
        return all(isinstance(v, (int, float)) and not isinstance(v, bool) and lo <= v <= hi for v in parsed)
    if kind == "jsonSchema":
        parsed = safe_parse(response)
        if not isinstance(parsed, dict):
            return False
        schema = p.get("schema") or {}
        for key, typ in schema.items():
            if key not in parsed or not check_type(parsed[key], typ):
                return False
        nested_key = p.get("nestedKey")
        if nested_key and p.get("nestedSchema"):
            inner = parsed.get(nested_key)
            if not isinstance(inner, dict):
                return False
            for key, typ in (p["nestedSchema"] or {}).items():
                if key not in inner or not check_type(inner[key], typ):
                    return False
        return True
    if kind == "jsonToolCall":
        parsed = safe_parse(response)
        if not isinstance(parsed, dict):
            return False
        fn = str(p["functionName"])
        if parsed.get("function") != fn and parsed.get("name") != fn:
            return False
        args = parsed.get("arguments")
        if args is None:
            args = parsed.get("params")
        if args is None:
            args = parsed.get("parameters")
        if not isinstance(args, dict):
            return False
        return str(args.get(p["argKey"])).lower() == str(p["argValue"]).lower()
    if kind == "jsonApiResponse":
        parsed = safe_parse(response)
        if not isinstance(parsed, dict):
            return False
        return (
            parsed.get("status") == p["status"]
            and isinstance(parsed.get("message"), str)
            and "data" in parsed
            and parsed["data"] is None
        )
    if kind == "jsonEvent":
        parsed = safe_parse(response)
        if not isinstance(parsed, dict) or parsed.get("type") != "event":
            return False
        if not isinstance(parsed.get("name"), str):
            return False
        if not isinstance(parsed.get("date"), str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", parsed["date"]):
            return False
        return isinstance(parsed.get("attendees"), (int, float)) and not isinstance(parsed.get("attendees"), bool)
    if kind == "keyValueLines":
        count = int(p["expectedCount"])
        lines = non_empty_lines(response)
        if len(lines) != count:
            return False
        pairs = [re.match(r"^([A-Za-z][A-Za-z\s_-]*):\s*(.+)$", ln) for ln in lines]
        if any(pair is None or not (pair.group(2) or "").strip() for pair in pairs):
            return False
        expected = [k.strip().lower() for k in (p.get("expectedKeys") or [])]
        if not expected:
            return True
        if len(expected) != len(lines):
            return False
        actual = sorted((pair.group(1) or "").strip().lower() for pair in pairs if pair)
        return sorted(expected) == actual
    if kind == "csvFormat":
        header_n = int(p["headerColumns"])
        data_n = int(p["dataRows"])
        lines = non_empty_lines(response)
        if len(lines) != 1 + data_n:
            return False
        rows = [parse_csv_line(ln) for ln in lines]
        if any(row is None or len(row) != header_n for row in rows):
            return False
        if any(not cell for cell in (rows[0] or [])):
            return False
        return all(row is not None and all(cell for cell in row) for row in rows[1:])
    if kind == "markdownTable":
        cols = int(p["columns"])
        data_n = int(p["dataRows"])
        lines = non_empty_lines(response)
        if len(lines) != 2 + data_n:
            return False
        header = parse_md_row(lines[0])
        if len(header) != cols or any(not c for c in header):
            return False
        sep = parse_md_row(lines[1])
        if len(sep) != cols or not all(is_md_sep(c) for c in sep):
            return False
        return all(len(parse_md_row(ln)) == cols and all(parse_md_row(ln)) for ln in lines[2:])
    if kind == "numberedDefinitions":
        matches = re.findall(r"^\d+\.\s+.+\s*[—–-]\s*.+", response, flags=re.M)
        return len(matches) == int(p["expectedCount"])
    if kind == "htmlList":
        has_ul = bool(re.search(r"<ul[\s>]", response, re.I) and re.search(r"</ul>", response, re.I))
        li = len(re.findall(r"<li[\s>]", response, flags=re.I))
        return has_ul and li == int(p["expectedCount"])
    return False
