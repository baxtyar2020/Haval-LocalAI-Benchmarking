from __future__ import annotations

import ast
import re
import tempfile
from pathlib import Path

from haval_engine.winproc import run_hidden


_FENCE = re.compile(r"```(?:python)?\n(.*?)```", re.S | re.I)


def extract_python(text: str) -> str:
    blocks = _FENCE.findall(text)
    code = "\n\n".join(blocks) if blocks else text
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        idx = code.rfind("\n{")
        if idx > 0:
            clipped = code[:idx]
            try:
                ast.parse(clipped)
                return clipped
            except SyntaxError:
                pass
        return code


def _split_future(code: str) -> tuple[str, str]:
    """Keep from __future__ at the top of the combined sandbox file."""
    lines = code.splitlines(True)
    head: list[str] = []
    i = 0
    while i < len(lines) and (
        not lines[i].strip()
        or lines[i].lstrip().startswith("#")
        or lines[i].startswith("#!")
        or lines[i].strip().startswith('"""')
        or lines[i].strip().startswith("'''")
    ):
        head.append(lines[i])
        i += 1
        if head and (head[-1].strip().endswith('"""') or head[-1].strip().endswith("'''")) and len(head) > 1:
            break
    while i < len(lines) and lines[i].lstrip().startswith("from __future__ import"):
        head.append(lines[i])
        i += 1
    return "".join(head), "".join(lines[i:])


def run_python_snippet(
    text: str,
    timeout: float = 5,
    extra_tests: str | None = None,
    prelude: str | None = None,
) -> dict:
    code = extract_python(text)
    future, body = _split_future(code)
    parts: list[str] = []
    if future.strip():
        parts.append(future.rstrip())
    if prelude and prelude.strip():
        parts.append(prelude.strip())
    parts.append("__name__ = 'haval_sandbox'")
    parts.append(body.rstrip() if body.strip() else code.rstrip())
    if extra_tests and extra_tests.strip():
        parts.append("# hidden tests\n" + extra_tests.strip())
        timeout = max(timeout, 12)
    full = "\n\n".join(p for p in parts if p) + "\n"
    try:
        ast.parse(full)
    except SyntaxError as exc:
        return {"ok": False, "error": f"syntax: {exc}"}
    lowered = full.lower()
    if any(tok in lowered for tok in ("socket", "urllib", "requests", "http.client", "subprocess", "os.system")):
        return {"ok": False, "error": "network_or_process_blocked"}
    with tempfile.TemporaryDirectory(prefix="haval-sandbox-") as tmp:
        path = Path(tmp) / "snippet.py"
        path.write_text(full, encoding="utf-8")
        try:
            result = run_hidden(["python", "-I", str(path)], timeout=timeout, cwd=Path(tmp))
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "exit")[:500]
        if result.returncode == 124 or "timeout" in err.lower():
            return {"ok": False, "error": "timeout"}
        return {"ok": False, "error": err}
    return {"ok": True, "stdout": result.stdout or ""}
