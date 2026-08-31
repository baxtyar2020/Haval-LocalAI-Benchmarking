from __future__ import annotations

import time
from pathlib import Path

from haval_engine.ollama import client as ollama
from haval_engine.ollama.runtime import locate
from haval_engine.winproc import spawn_hidden


def port_11434_users() -> list[str]:
    users: list[str] = []
    try:
        import psutil
    except ImportError:
        return users
    for conn in psutil.net_connections(kind="inet"):
        if conn.laddr and conn.laddr.port == 11434:
            name = "?"
            if conn.pid:
                try:
                    name = psutil.Process(conn.pid).name()
                except (psutil.Error, ProcessLookupError):
                    name = str(conn.pid)
            users.append(f"{name} pid={conn.pid}")
    return users


def start_ollama() -> tuple[bool, str]:
    path, version = locate()
    if not path:
        return False, "Ollama executable was not found."
    ok, payload = ollama.tags(timeout=2)
    if ok:
        return True, f"API already responding ({version})."
    spawn_hidden([str(path), "serve"], cwd=path.parent)
    deadline = time.time() + 25
    while time.time() < deadline:
        ok, _ = ollama.tags(timeout=1.5)
        if ok:
            return True, f"Started Ollama from {path} ({version})."
        time.sleep(0.6)
    holders = port_11434_users()
    extra = f" Port 11434 is held by: {', '.join(holders)}." if holders else ""
    return False, f"Started the process but the API did not become ready.{extra}"


def stop_stale_ollama() -> str:
    try:
        import psutil
    except ImportError:
        return "psutil not installed; skipped process stop."
    killed = 0
    for proc in psutil.process_iter(["name", "exe"]):
        name = (proc.info.get("name") or "").lower()
        exe = (proc.info.get("exe") or "").lower()
        if "ollama" in name or exe.endswith("ollama.exe"):
            try:
                proc.terminate()
                killed += 1
            except (psutil.Error, ProcessLookupError):
                continue
    if killed:
        time.sleep(1.2)
        return f"Stopped {killed} Ollama process(es)."
    return "No Ollama process was running."
