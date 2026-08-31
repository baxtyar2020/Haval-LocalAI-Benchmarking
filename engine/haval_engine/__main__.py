from __future__ import annotations

import os
import sys
import traceback
from datetime import datetime, timezone

import uvicorn

from haval_engine.main import app
from haval_engine.paths import app_data_dir, support_log_path


def _install_crash_hook() -> None:
    previous = sys.excepthook

    def hook(etype, value, tb) -> None:  # type: ignore[no-untyped-def]
        try:
            with support_log_path().open("a", encoding="utf-8") as fh:
                fh.write(f"\n[{datetime.now(timezone.utc).isoformat()}] unhandled exception\n")
                traceback.print_exception(etype, value, tb, file=fh)
        except OSError:
            pass
        previous(etype, value, tb)

    sys.excepthook = hook


def main() -> None:
    _install_crash_hook()
    host = os.environ.get("HAVAL_ENGINE_HOST", "127.0.0.1")
    port = int(os.environ.get("HAVAL_ENGINE_PORT", "8765"))
    try:
        with support_log_path().open("a", encoding="utf-8") as fh:
            fh.write(f"[{datetime.now(timezone.utc).isoformat()}] engine listening on {host}:{port}\n")
        (app_data_dir() / "engine.port").write_text(str(port), encoding="utf-8")
    except OSError:
        pass
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
