from __future__ import annotations

from datetime import datetime


def _parse_hhmm(value: str) -> int:
    h, m = value.split(":")
    return int(h) * 60 + int(m)


def validate_schedule_json(payload: dict) -> tuple[bool, str]:
    days = payload.get("days") or []
    if not days:
        return False, "no_days"
    for day in days:
        blocks = sorted(day.get("blocks") or [], key=lambda b: b.get("start") or "")
        prev_end = -1
        for block in blocks:
            try:
                start = _parse_hhmm(block["start"])
                end = _parse_hhmm(block["end"])
            except (KeyError, ValueError):
                return False, "bad_time"
            if end <= start:
                return False, "end_before_start"
            if start < prev_end:
                return False, "overlap"
            prev_end = end
    return True, "ok"


def validate_fixture(fixture: dict) -> tuple[bool, str]:
    kind = fixture.get("kind")
    golden = fixture.get("golden") or {}
    if kind == "schedule":
        events = fixture.get("events") or []
        if golden.get("conflicts_after_fix") != 0:
            return False, "golden_still_conflicted"
        times = []
        for ev in events:
            if ev.get("removed"):
                continue
            start = ev["start"]
            end = ev["end"]
            if end <= start:
                return False, "event_order"
            for prev_s, prev_e, day in times:
                if day == ev.get("day") and start < prev_e and end > prev_s:
                    return False, "overlap_in_fixture"
            times.append((start, end, ev.get("day")))
        return True, "ok"
    if kind == "finance":
        pl = fixture.get("p_and_l") or {}
        net = pl["revenue"] - pl["cogs"] - pl["opex"]
        if net != golden.get("net"):
            return False, "net_mismatch"
        q1, q2 = fixture["quarters"][0]["rev"], fixture["quarters"][1]["rev"]
        growth = round(100.0 * (q2 - q1) / q1, 1)
        if growth != golden.get("qoq_growth_pct"):
            return False, "qoq_mismatch"
        return True, "ok"
    if kind == "catalog":
        ids = {item["id"] for item in fixture.get("items") or []}
        if golden.get("winner") not in ids:
            return False, "winner_missing"
        return True, "ok"
    if kind == "contract":
        clause = next((c for c in fixture.get("clauses") or [] if c.get("n") == golden.get("audit_clause")), None)
        if not clause or golden.get("audit_snippet") not in clause.get("text", ""):
            return False, "audit_clause"
        if fixture.get("effective_date") != golden.get("effective_date"):
            return False, "effective_date"
        return True, "ok"
    if kind == "policy_pair":
        if golden.get("retention_from") not in fixture["v1"]["retention"]:
            return False, "retention_from"
        if golden.get("retention_to") not in fixture["v2"]["retention"]:
            return False, "retention_to"
        return True, "ok"
    if kind == "logs":
        if golden.get("root_cause") not in {e.get("code") for e in fixture.get("events") or []}:
            return False, "root_not_in_logs"
        return True, "ok"
    if kind == "text":
        for key in golden.get("must_appear") or []:
            blob = json_blob(fixture)
            if key.lower() not in blob.lower():
                return False, f"missing:{key}"
        return True, "ok"
    return True, "ok"


def json_blob(obj: object) -> str:
    import json

    return json.dumps(obj)


def iso_ok(value: str) -> bool:
    datetime.strptime(value, "%Y-%m-%d")
    return True
