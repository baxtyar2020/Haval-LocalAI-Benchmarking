from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CREATE_NO_WINDOW = 0x08000000


def hidden_kwargs(*, stdin=None) -> dict:
    kwargs: dict = {
        "stdin": stdin if stdin is not None else subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
    }
    if sys.platform == "win32":
        kwargs["creationflags"] = CREATE_NO_WINDOW
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = 0
        kwargs["startupinfo"] = startup
    return kwargs


def _kill_tree(pid: int) -> None:
    if sys.platform == "win32":
        flags = CREATE_NO_WINDOW
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=8,
                creationflags=flags,
            )
        except Exception:
            pass
        return
    try:
        subprocess.run(["kill", "-9", str(pid)], timeout=3, check=False)
    except Exception:
        pass


def run_hidden(
    args: list[str],
    timeout: float = 20,
    cwd: Path | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run a process and always return. On timeout the process tree is killed."""
    kwargs = hidden_kwargs(stdin=subprocess.PIPE if input_text is not None else None)
    proc = subprocess.Popen(args, cwd=str(cwd) if cwd else None, **kwargs)
    try:
        out, err = proc.communicate(input=input_text, timeout=timeout)
        return subprocess.CompletedProcess(args, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        _kill_tree(proc.pid)
        try:
            proc.kill()
        except Exception:
            pass
        try:
            out, err = proc.communicate(timeout=5)
        except Exception:
            out, err = "", ""
        return subprocess.CompletedProcess(args, 124, out or "", ((err or "") + "\ntimeout")[-500:])


def spawn_hidden(args: list[str], cwd: Path | None = None) -> subprocess.Popen[str]:
    return subprocess.Popen(args, cwd=str(cwd) if cwd else None, **hidden_kwargs())
