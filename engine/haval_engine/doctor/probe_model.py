from __future__ import annotations

DEFAULT_PROBE_MODEL = "smollm:135m-instruct-v0.2-q2_K"
MAX_PROBE_BYTES = 512 * 1024**2


def model_size_bytes(row: dict) -> int:
    try:
        return int(row.get("size") or 0)
    except (TypeError, ValueError):
        return 0


def is_hidden_probe_model(name: str | None) -> bool:
    """Doctor-only weights must not appear in Installed, wizard, or counts."""
    n = (name or "").strip().lower()
    if not n:
        return False
    want = DEFAULT_PROBE_MODEL.lower()
    return n == want or n.startswith(want + "-") or n.startswith(want + "@")


def pick_probe_model(models: list[dict], fallback_names: list[str] | None = None) -> str | None:
    """Return the hidden Doctor probe tag if it is installed. Never a roster model."""
    preferred: list[str] = []
    for name in [DEFAULT_PROBE_MODEL, *(fallback_names or [])]:
        key = str(name or "").strip()
        if key and key.lower() not in {p.lower() for p in preferred}:
            preferred.append(key)
    by_name = [(str(m.get("name") or ""), m) for m in models if m.get("name")]
    for want in preferred:
        want_l = want.lower()
        for name, row in by_name:
            low = name.lower()
            if low == want_l or low.startswith(want_l):
                size = model_size_bytes(row)
                if size == 0 or size <= MAX_PROBE_BYTES:
                    return name
    for name, row in by_name:
        if is_hidden_probe_model(name):
            size = model_size_bytes(row)
            if size == 0 or size <= MAX_PROBE_BYTES:
                return name
    return None
