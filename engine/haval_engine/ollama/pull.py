from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Callable

from haval_engine.ollama.client import OLLAMA_HOST, _request


def delete_model(name: str) -> tuple[bool, str]:
    status, payload = _request("DELETE", "/api/delete", {"name": name}, timeout=30)
    if status in {200, 204}:
        return True, "Removed."
    err = payload.get("error") if isinstance(payload, dict) else str(payload)
    return False, str(err or f"HTTP {status}")


def pull_stream(
    name: str,
    on_event: Callable[[dict], None],
    cancelled: Callable[[], bool],
) -> str:
    data = json.dumps({"name": name, "stream": True}).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/pull",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60 * 60 * 6) as resp:
            for raw in resp:
                if cancelled():
                    return "cancelled"
                line = raw.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                on_event(event)
                if event.get("error"):
                    return "failed"
                if str(event.get("status") or "").lower() in {"success", "complete"}:
                    return "success"
    except urllib.error.HTTPError as exc:
        on_event({"error": exc.read().decode("utf-8", errors="replace") or str(exc)})
        return "failed"
    except Exception as exc:  # noqa: BLE001
        on_event({"error": str(exc)})
        return "failed"
    return "success"


def registry_search(query: str) -> list[dict[str, Any]]:
    from haval_engine.ollama.registry import search_models

    return search_models(query)
