from __future__ import annotations

import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from haval_engine.models.params import parse_params

_LIBRARY_HREF = re.compile(r'href="(/library/[^"#?]+)"', re.I)
_SKIP_TAGS = {"assets", "tags", "blob", "toc"}
_UUID = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\)?$",
    re.I,
)
_SIZE_TAG = re.compile(r"^(latest|preview|[\d.]+b(?:-a[\d.]+b)?)$", re.I)
_QUANT_TAIL = re.compile(
    r"(iq[1-4][_-]?[a-z]{1,4}|q[2-8][_-]?k[_-]?(?:xl|[sml])|q[2-8][_-]?k|q[48][_-]?0|"
    r"fp16|bf16|f16|f32|mxfp4)",
    re.I,
)
_BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0"
)


def browser_headers() -> dict[str, str]:
    """Desktop Edge headers so Ollama library pages serve the same HTML a customer browser sees."""
    return {
        "User-Agent": _BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Cache-Control": "no-cache",
        "Upgrade-Insecure-Requests": "1",
    }


def parse_library_slugs(html: str) -> list[str]:
    slugs: list[str] = []
    seen: set[str] = set()
    for href in _LIBRARY_HREF.findall(html or ""):
        path = href.strip().rstrip("/")
        if ":" in path:
            continue
        parts = path.split("/")
        if len(parts) < 3 or parts[1] != "library":
            continue
        slug = parts[2]
        if not slug or slug in seen or slug.lower() in _SKIP_TAGS:
            continue
        seen.add(slug)
        slugs.append(slug)
    return slugs


def parse_model_tags(html: str, model: str) -> list[str]:
    model = model.strip().strip("/")
    if not model:
        return []
    escaped = re.escape(model)
    found = re.findall(rf"/library/{escaped}:([A-Za-z0-9._-]+)", html or "", re.I)
    tags: list[str] = []
    seen: set[str] = set()
    for tag in found:
        clean = tag.strip().rstrip(")")
        if not clean or clean.lower() in _SKIP_TAGS or _UUID.match(clean):
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        tags.append(clean)
    return tags


def _compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (text or "").lower())


def name_matches_query(name: str, query: str) -> bool:
    """True when the typed query is actually in the model name, not a related listing."""
    q = _compact(query)
    if len(q) < 2:
        return False
    return q in _compact(name)


def matching_slugs(slugs: list[str], query: str) -> list[str]:
    q_low = (query or "").strip().lower()
    hits = [s for s in slugs if name_matches_query(s, query)]
    hits.sort(key=lambda s: (0 if s.lower() == q_low else 1, 0 if q_low in s.lower() else 2, s.lower()))
    return hits


def format_quant(raw: str) -> str:
    text = (raw or "").strip().replace("-", "_")
    if not text:
        return ""
    return text.upper()


def quant_from_tag(tag: str) -> str:
    matches = _QUANT_TAIL.findall(tag or "")
    if not matches:
        return ""
    return format_quant(matches[-1])


def precision_of(*, name: str = "", tag: str = "", quant: str = "") -> str:
    """Display label for GGUF / Ollama precision (Q4_K_M, IQ2_M, FP16, …)."""
    for piece in (quant, tag, name):
        found = quant_from_tag(piece)
        if found:
            return found
    return ""


def is_primary_tag(tag: str) -> bool:
    return bool(_SIZE_TAG.match(tag or ""))


def _fetch(url: str, timeout: float = 14) -> str:
    req = urllib.request.Request(url, headers=browser_headers())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _hit(name: str, description: str = "") -> dict[str, Any]:
    parsed = parse_params(name, description)
    tag = name.split(":")[-1] if ":" in name else "latest"
    base = name.split(":")[0]
    display = base.split("/")[-1]
    return {
        "name": name,
        "display_name": display,
        "tag": tag,
        "description": description,
        "quant": precision_of(name=name, tag=tag, quant=quant_from_tag(tag)),
        "params_total": parsed["total"],
        "params_active": parsed["active"],
        "params_moe": parsed["moe"],
        "params_label": parsed["label"],
        "pull_command": f"ollama pull {name}",
    }


def _expand_library(slug: str, query: str) -> list[dict[str, Any]]:
    readme = ""
    try:
        from haval_engine.models.param_cards import confirm_from_html, parse_library_param_cards, pick_card, remember_checked

        readme = _fetch(f"https://ollama.com/library/{urllib.parse.quote(slug)}")
        confirm_from_html(readme, slug, slug=slug)
        page_cards = parse_library_param_cards(readme, slug=slug)
    except Exception:
        page_cards = {}
    html = _fetch(f"https://ollama.com/library/{urllib.parse.quote(slug)}/tags")
    tags = parse_model_tags(html, slug)
    if not tags:
        html = readme or _fetch(f"https://ollama.com/library/{urllib.parse.quote(slug)}")
        tags = parse_model_tags(html, slug)
    exact = slug.lower() == query.lower() or query.lower() == f"{slug}:".lower()
    if not tags:
        return [_hit(slug)]
    chosen = tags if exact else [t for t in tags if is_primary_tag(t)] or tags[:8]
    if exact:
        chosen = chosen[:80]
    else:
        chosen = chosen[:16]
    out = []
    for tag in chosen:
        name = f"{slug}:{tag}"
        pack = pick_card(page_cards, name) if page_cards else None
        if pack:
            remember_checked(name, pack)
        out.append(_hit(name))
    return out


def search_models(query: str) -> list[dict[str, Any]]:
    q = (query or "").strip()
    if not q:
        return []
    if q.startswith("hf.co/") or ("/" in q and not q.startswith("http")):
        return [_hit(q, "Hugging Face / namespace reference")]
    if ":" in q and "/" not in q.split(":")[0]:
        try:
            from haval_engine.models.param_cards import request_confirm

            request_confirm([q])
        except Exception:
            pass
        return [_hit(q, "Exact Ollama tag")]

    try:
        search_html = _fetch("https://ollama.com/search?" + urllib.parse.urlencode({"q": q}))
    except Exception:
        if name_matches_query(q, q):
            return [_hit(q, "Could not reach the Ollama library. Download will still try this name.")]
        return []

    slugs = matching_slugs(parse_library_slugs(search_html), q)
    if not slugs and re.fullmatch(r"[A-Za-z0-9._-]+", q) and name_matches_query(q, q):
        slugs = [q]
    slugs = slugs[:8]
    q_low = q.lower()

    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_expand_library, slug, q): slug for slug in slugs}
        for fut in as_completed(futures):
            try:
                hits = fut.result()
            except Exception:
                slug = futures[fut]
                hits = [_hit(slug, "Library page could not be read")]
            for hit in hits:
                name = str(hit["name"])
                if name in seen or not name_matches_query(name, q):
                    continue
                seen.add(name)
                out.append(hit)
    out.sort(
        key=lambda h: (
            0 if str(h["name"]).split(":")[0].lower() == q_low else 1,
            str(h.get("display_name") or ""),
            str(h.get("tag") or ""),
        )
    )
    if not out and re.fullmatch(r"[A-Za-z0-9._:-]+", q):
        out.append(_hit(q, "Download this name as an Ollama tag"))
    return [dict(item) for item in out[:120]]
