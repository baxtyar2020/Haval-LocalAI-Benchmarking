from __future__ import annotations

import html as html_lib
import json
import re
import threading
import time
from typing import Any

from haval_engine.models.params import format_b
from haval_engine.paths import cache_dir

_MOE_WITH = re.compile(
    r"(?P<total>[\d.]+)\s*B\s+parameter(?:s)?(?:\s+MoE)?\s+model\s+with\s+"
    r"(?P<active>[\d.]+)\s*B\s+active",
    re.I,
)
_ACTIVE_OF_TOTAL = re.compile(
    r"(?P<active>[\d.]+)\s*B\s+active(?:\s+parameters?)?\s+"
    r"(?:out\s+of|of|/)\s+(?P<total>[\d.]+)\s*B",
    re.I,
)
_TOTAL_WITH_ACTIVE = re.compile(
    r"(?P<total>[\d.]+)\s*B(?:illion)?(?:\s+total)?(?:\s+parameters?)?.{0,48}?"
    r"(?P<active>[\d.]+)\s*B\s+active",
    re.I | re.S,
)
_RUN = re.compile(r"ollama run ([A-Za-z0-9._:/-]+)", re.I)
_OK_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,180}$")

TTL_OK_S = 14 * 24 * 3600
TTL_FAIL_S = 30 * 60

_lock = threading.Lock()
_queue: set[str] = set()
_worker_started = False


def _pack(total: str, active: str, moe: bool) -> dict[str, Any]:
    return {
        "total": total,
        "active": active,
        "moe": moe,
        "label": f"{total} total · {active} active",
    }


def _norm(name: str) -> str:
    return (name or "").strip().lower()


def _looks_like_name(text: str) -> bool:
    raw = (text or "").strip()
    if not raw or " " in raw or not _OK_NAME.match(raw):
        return False
    if re.fullmatch(r"[\d.]+B", raw, re.I):
        return False
    return True


def _cache_path():
    return cache_dir() / "ollama-params.json"


def _load() -> dict[str, Any]:
    path = _cache_path()
    if not path.exists():
        return {"cards": {}, "attempts": {}}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"cards": {}, "attempts": {}}
    if not isinstance(data, dict):
        return {"cards": {}, "attempts": {}}
    data.setdefault("cards", {})
    data.setdefault("attempts", {})
    return data


def _save(data: dict[str, Any]) -> None:
    path = _cache_path()
    path.write_text(json.dumps(data, indent=0), encoding="utf-8")


def cached_params(*sources: object) -> dict | None:
    with _lock:
        cards = _load().get("cards") or {}
    for source in sources:
        key = _norm(str(source or ""))
        if not _looks_like_name(key):
            continue
        entry = cards.get(key)
        if not entry:
            continue
        total = str(entry.get("total") or "")
        active = str(entry.get("active") or "")
        if total and active and total != "—" and active != "—":
            out = _pack(total, active, bool(entry.get("moe")) or total != active)
            out["checked"] = bool(entry.get("checked"))
            return out
    return None


def remember_cards(cards: dict[str, dict], *, checked: bool = False) -> None:
    if not cards:
        return
    now = time.time()
    with _lock:
        data = _load()
        for name, pack in cards.items():
            key = _norm(name)
            if not _looks_like_name(key):
                continue
            prev = data["cards"].get(key) or {}
            data["cards"][key] = {
                "total": pack["total"],
                "active": pack["active"],
                "moe": bool(pack.get("moe")),
                "checked": True if checked else bool(prev.get("checked")),
                "checked_at": now if checked else prev.get("checked_at") or now,
            }
            data["attempts"].pop(key, None)
        _save(data)


def remember_checked(name: str, pack: dict) -> dict:
    """Stamp this exact pull name as live-checked, overwriting Total/Active when they differ."""
    remember_cards({_norm(name): pack}, checked=True)
    return {**_pack(pack["total"], pack["active"], bool(pack.get("moe"))), "checked": True}


def is_checked(name: str) -> bool:
    key = _norm(name)
    with _lock:
        entry = (_load().get("cards") or {}).get(key) or {}
    return bool(entry.get("checked"))


def _plain(html: str) -> str:
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html or "")
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html_lib.unescape(text)
    return re.sub(r"\s+", " ", text)


def _from_match(m: re.Match[str]) -> dict[str, Any] | None:
    total = format_b(m.group("total"))
    active = format_b(m.group("active"))
    if not total or not active or total == "—" or active == "—":
        return None
    try:
        if float(str(active).rstrip("Bb")) > float(str(total).rstrip("Bb")) * 1.05:
            return None
    except ValueError:
        return None
    return _pack(total, active, total != active)


def parse_library_param_cards(html: str, slug: str = "") -> dict[str, dict]:
    """Pull total/active from an Ollama library README (e.g. Llama 4 Maverick)."""
    text = _plain(html)
    out: dict[str, dict] = {}
    runs = list(_RUN.finditer(text))
    for i, run in enumerate(runs):
        name = run.group(1).strip()
        end = runs[i + 1].start() if i + 1 < len(runs) else min(len(text), run.end() + 480)
        chunk = text[run.end() : end]
        pack = _card_from_text(chunk) or _card_from_text(text[run.start() : end])
        if pack:
            out[_norm(name)] = pack
            if ":" not in name and slug:
                out[_norm(f"{slug}:{name.split('/')[-1]}")] = pack

    slug_n = _norm(slug)
    page = _card_from_text(text)
    if page and slug_n and slug_n not in out:
        tagged = [k for k in out if k == slug_n or k.startswith(f"{slug_n}:")]
        if not tagged:
            out[slug_n] = page
    return {k: v for k, v in out.items() if _looks_like_name(k)}


def _card_from_text(chunk: str) -> dict | None:
    for pattern in (_MOE_WITH, _ACTIVE_OF_TOTAL, _TOTAL_WITH_ACTIVE):
        m = pattern.search(chunk or "")
        if m:
            pack = _from_match(m)
            if pack:
                return pack
    return None


def pick_card(cards: dict[str, dict], name: str) -> dict | None:
    key = _norm(name)
    if key in cards:
        return cards[key]
    if ":" in key:
        slug, tag = key.split(":", 1)
        for cand in (f"{slug}:{tag}", tag, key):
            if cand in cards:
                return cards[cand]
        for stored, pack in cards.items():
            if stored.endswith(f":{tag}") or stored == tag:
                return pack
    slug = key.split(":")[0]
    matches = [p for n, p in cards.items() if n == slug or n.startswith(f"{slug}:")]
    if len(matches) == 1:
        return matches[0]
    return None


def library_page_url(name: str) -> str | None:
    base = (name or "").split(":")[0].strip()
    if not base or base.startswith("hf.co/") or base.startswith("http"):
        return None
    if "/" in base:
        user, model = base.split("/", 1)
        if user and model:
            return f"https://ollama.com/{user}/{model}"
        return None
    return f"https://ollama.com/library/{base}"


def confirm_from_html(html: str, name: str, slug: str = "") -> dict | None:
    cards = parse_library_param_cards(html, slug=slug or name.split(":")[0])
    remember_cards(cards)
    pack = pick_card(cards, name)
    if pack:
        remember_cards({_norm(name): pack})
    return pack


def _fetch_pages(name: str) -> str | None:
    from haval_engine.ollama.registry import _fetch
    import urllib.parse

    base = library_page_url(name)
    if not base:
        return None
    urls: list[str] = []
    if ":" in name:
        tag = name.split(":", 1)[1]
        urls.append(f"{base}:{urllib.parse.quote(tag)}")
    urls.append(base)
    last_html = None
    for url in urls:
        try:
            last_html = _fetch(url, timeout=10)
            cards = parse_library_param_cards(last_html, slug=name.split(":")[0].split("/")[-1])
            if pick_card(cards, name):
                return last_html
        except Exception:
            continue
    return last_html


def _mark_attempt(name: str) -> None:
    with _lock:
        data = _load()
        data["attempts"][_norm(name)] = time.time()
        _save(data)


def _should_fetch(name: str) -> bool:
    key = _norm(name)
    if not _looks_like_name(key):
        return False
    now = time.time()
    with _lock:
        data = _load()
        card = (data.get("cards") or {}).get(key) or {}
        if card.get("checked") and now - float(card.get("checked_at") or 0) < TTL_OK_S:
            return False
        last = float((data.get("attempts") or {}).get(key) or 0)
        if last and now - last < TTL_FAIL_S:
            return False
    return True


def confirm_name(name: str) -> dict | None:
    """Fetch the Ollama library page for this exact pull name.

    Always stamps the installed/search name as checked when the page is reachable.
    Overwrites cached Total/Active when the live card differs.
    """
    html = _fetch_pages(name)
    if html is None and library_page_url(name):
        _mark_attempt(name)
        return None
    if html is None:
        return None
    slug = name.split(":")[0].split("/")[-1]
    pack = confirm_from_html(html, name, slug=slug)
    if not pack:
        from haval_engine.models.params import lookup_known

        pack = lookup_known(name)
    if pack:
        return remember_checked(name, pack)
    _mark_attempt(name)
    return None


def request_confirm(names: list[str]) -> None:
    pending = [n for n in names if n and _should_fetch(n)]
    if not pending:
        return
    with _lock:
        _queue.update(_norm(n) for n in pending)
        global _worker_started
        if not _worker_started:
            _worker_started = True
            threading.Thread(target=_loop, name="haval-param-cards", daemon=True).start()


def _loop() -> None:
    while True:
        name = None
        with _lock:
            if _queue:
                name = _queue.pop()
        if not name:
            time.sleep(0.6)
            continue
        try:
            confirm_name(name)
        except Exception:
            _mark_attempt(name)
        time.sleep(0.25)
