from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request
from typing import Any

OLLAMA_HOST = "http://127.0.0.1:11434"
# Never allow unbounded generate. A looping 1B can otherwise run for many minutes.
MAX_PREDICT = 4096
# Thinking uses extra tokens after the hidden pass.
MAX_PREDICT_THINK = 8192
MAX_CHARS = 24_000


def _request(method: str, path: str, body: dict | None = None, timeout: float = 8) -> tuple[int, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_HOST}{path}",
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            parsed = {"error": raw}
        return exc.code, parsed
    except Exception as exc:  # noqa: BLE001 — surface as connection failure
        return 0, {"error": str(exc)}


def tags(timeout: float = 4) -> tuple[bool, dict]:
    status, payload = _request("GET", "/api/tags", timeout=timeout)
    return status == 200, payload if isinstance(payload, dict) else {"error": payload}


def show(model: str) -> dict:
    _, payload = _request("POST", "/api/show", {"name": model}, timeout=12)
    return payload if isinstance(payload, dict) else {}


def ps() -> dict:
    _, payload = _request("GET", "/api/ps", timeout=4)
    return payload if isinstance(payload, dict) else {}


def output_is_stuck(text: str) -> bool:
    """True when the model is repeating the same fragment instead of finishing."""
    if len(text) < 280:
        return False
    tail = text[-80:]
    if tail.strip() and text.count(tail) >= 5:
        return True
    window = text[-120:]
    if len(set(window)) <= 2 and len(text) > 400:
        return True
    return False


def _set_sock_timeout(resp, seconds: float) -> None:
    seconds = max(0.5, float(seconds))
    for attr in ("fp.raw._sock",):
        try:
            resp.fp.raw._sock.settimeout(seconds)  # type: ignore[union-attr]
            return
        except Exception:
            pass
    try:
        resp.fp._sock.settimeout(seconds)  # type: ignore[union-attr]
    except Exception:
        pass


def generate_stream(
    model: str,
    prompt: str,
    num_predict: int = 64,
    timeout: float | None = 40,
    cancel=None,
    think: bool = False,
    stall_s: float | None = None,
    wall_s: float | None = None,
) -> dict:
    """Stream a generate call until Ollama reports done, a cap hits, or time runs out.

    ``num_predict < 0`` is treated as MAX_PREDICT so a run cannot stream forever.
    ``wall_s`` is a hard deadline. If omitted, ``timeout`` is used (default 40s).

    Thinking on: do not apply the short stall timer to thinking tokens — those can
    pause for a long time before the visible answer. Score the visible answer, not
    the thinking stream. If the model rejects ``think: true``, retry without it.
    """
    import time

    cap = MAX_PREDICT_THINK if think else MAX_PREDICT
    predict = cap if num_predict is None or int(num_predict) < 0 else int(num_predict)
    predict = min(predict, cap)
    deadline_s = wall_s if wall_s is not None else timeout
    if deadline_s is None or deadline_s <= 0:
        deadline_s = 90.0
    stall = stall_s if stall_s is not None else min(12.0, float(deadline_s))
    stall = min(float(stall), float(deadline_s))

    modes: list[bool | None] = [bool(think)]
    if think:
        modes.append(None)

    last_fail: dict = {"ok": False, "error": "no_attempt", "ttft_ms": None, "total_ms": 0, "text": ""}
    for think_mode in modes:
        got = _generate_once(
            model,
            prompt,
            predict=predict,
            think_mode=think_mode,
            deadline_s=deadline_s,
            stall=stall,
            cancel=cancel,
        )
        last_fail = got
        if got.get("ok") and (got.get("text") or "").strip():
            return got
        err = str(got.get("error") or "").lower()
        if got.get("error") in {"cancelled", "wall_timeout", "repeat_loop", "output_cap"}:
            return got
        if "timed out" in err or "timeout" in err:
            return got
        if think_mode is True:
            continue
        return got
    return last_fail


def _generate_once(
    model: str,
    prompt: str,
    *,
    predict: int,
    think_mode: bool | None,
    deadline_s: float,
    stall: float,
    cancel,
) -> dict:
    import time

    body: dict = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {"temperature": 0, "top_p": 1, "seed": 42, "num_predict": predict},
    }
    if think_mode is not None:
        body["think"] = bool(think_mode)
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    started = time.perf_counter()
    ttft_ms = None
    think_ttft_ms = None
    last: dict = {}
    chunks: list[str] = []
    thinking: list[str] = []
    holder: dict = {"resp": None}
    finished = threading.Event()

    def _fail(error: str) -> dict:
        visible = "".join(chunks) or "".join(thinking)
        resp = holder.get("resp")
        if resp is not None:
            try:
                resp.close()
            except Exception:
                pass
        return {
            "ok": False,
            "error": error,
            "ttft_ms": ttft_ms,
            "total_ms": (time.perf_counter() - started) * 1000,
            "text": visible,
        }

    def watch() -> None:
        if not finished.wait(deadline_s):
            resp = holder.get("resp")
            if resp is not None:
                try:
                    resp.close()
                except Exception:
                    pass

    watcher = threading.Thread(target=watch, daemon=True, name="ollama-wall")
    connect_timeout = float(deadline_s)
    try:
        resp = urllib.request.urlopen(req, timeout=connect_timeout)
        holder["resp"] = resp
        watcher.start()
        with resp:
            _set_sock_timeout(resp, float(deadline_s))
            for line in resp:
                now = time.perf_counter()
                elapsed = now - started
                if elapsed > deadline_s:
                    return _fail("wall_timeout")
                remaining = max(0.5, deadline_s - elapsed)
                # Short stall starts after the first *visible* token. Thinking chunks
                # can pause for tens of seconds; treating them as output killed the run.
                has_answer = bool(chunks)
                _set_sock_timeout(resp, min(stall if has_answer else remaining, remaining))
                if cancel is not None and getattr(cancel, "is_set", lambda: False)():
                    return _fail("cancelled")
                text = line.decode("utf-8", errors="replace").strip()
                if not text:
                    continue
                try:
                    obj = json.loads(text)
                except json.JSONDecodeError:
                    continue
                msg = obj.get("message") if isinstance(obj.get("message"), dict) else {}
                think_piece = obj.get("thinking") or obj.get("reasoning") or msg.get("thinking") or ""
                if think_piece:
                    thinking.append(think_piece)
                    if think_ttft_ms is None:
                        think_ttft_ms = elapsed * 1000
                piece = obj.get("response") or msg.get("content") or ""
                if piece:
                    chunks.append(piece)
                    if ttft_ms is None:
                        ttft_ms = elapsed * 1000
                    visible = "".join(chunks)
                    if len(visible) >= MAX_CHARS or output_is_stuck(visible):
                        return _fail("repeat_loop" if output_is_stuck(visible) else "output_cap")
                last = obj
                if obj.get("done"):
                    break
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw) if raw else {}
            err = f"HTTP {exc.code}: {parsed.get('error') or raw or exc.reason}"
        except json.JSONDecodeError:
            err = f"HTTP {exc.code}: {raw or exc.reason}"
        elapsed = time.perf_counter() - started
        return {"ok": False, "error": err, "ttft_ms": ttft_ms, "text": "".join(chunks), "total_ms": elapsed * 1000}
    except Exception as exc:  # noqa: BLE001
        elapsed = time.perf_counter() - started
        err = str(exc)
        if elapsed >= deadline_s * 0.95 or "timed out" in err.lower() or "timeout" in err.lower():
            return _fail("wall_timeout")
        visible = "".join(chunks) or "".join(thinking)
        return {"ok": False, "error": err, "ttft_ms": ttft_ms, "text": visible, "total_ms": elapsed * 1000}
    finally:
        finished.set()
    total_ms = (time.perf_counter() - started) * 1000
    eval_count = float(last.get("eval_count") or 0)
    eval_ns = float(last.get("eval_duration") or 0)
    prompt_count = float(last.get("prompt_eval_count") or 0)
    tok_s = (eval_count / (eval_ns / 1e9)) if eval_ns else 0.0
    visible = "".join(chunks)
    fallback = "".join(thinking)
    text_out = visible.strip() and visible or (fallback if think_mode is not True else visible)
    return {
        "ok": bool(last.get("done")) and not last.get("error") and bool((visible or fallback).strip()) and bool(text_out.strip()),
        "ttft_ms": ttft_ms if ttft_ms is not None else think_ttft_ms,
        "total_ms": total_ms,
        "tok_s": tok_s,
        "eval_count": eval_count,
        "prompt_eval_count": prompt_count,
        "load_duration_ns": last.get("load_duration"),
        "text": text_out,
        "error": last.get("error"),
        "done_reason": last.get("done_reason"),
    }


def unload(model: str) -> None:
    _request("POST", "/api/generate", {"model": model, "keep_alive": 0, "prompt": ""}, timeout=8)
