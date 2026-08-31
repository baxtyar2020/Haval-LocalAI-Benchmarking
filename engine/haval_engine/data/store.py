from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from haval_engine.paths import app_data_dir


def runs_dir() -> Path:
    path = app_data_dir() / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def db_path() -> Path:
    return runs_dir() / "run.sqlite"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS runs (
            id TEXT PRIMARY KEY,
            started_at TEXT,
            ended_at TEXT,
            status TEXT,
            models_json TEXT,
            summary_json TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            model TEXT,
            scenario_id TEXT,
            attempt INTEGER,
            ok INTEGER,
            ttft_s REAL,
            total_s REAL,
            tok_s REAL,
            load_s REAL,
            prompt_tokens REAL,
            output_tokens REAL,
            q REAL,
            e REAL,
            hard_fail INTEGER,
            error TEXT,
            output TEXT,
            grade_json TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS scenario_scores (
            run_id TEXT,
            model TEXT,
            scenario_id TEXT,
            q REAL,
            e REAL,
            r REAL,
            w REAL,
            internal TEXT,
            customer TEXT,
            cap_reason TEXT,
            attempted INTEGER,
            successful INTEGER,
            PRIMARY KEY (run_id, model, scenario_id)
        )
        """
    )
    conn.commit()
    return conn


class RunStore:
    def __init__(self) -> None:
        self.conn = connect()

    def create_run(self, models: list[str]) -> str:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.conn.execute(
            "INSERT INTO runs (id, started_at, status, models_json, summary_json) VALUES (?, ?, ?, ?, ?)",
            (run_id, datetime.now(timezone.utc).isoformat(), "running", json.dumps(models), "{}"),
        )
        self.conn.commit()
        (runs_dir() / run_id).mkdir(exist_ok=True)
        return run_id

    def set_status(self, run_id: str, status: str, summary: dict | None = None) -> None:
        ended = datetime.now(timezone.utc).isoformat() if status in {"completed", "stopped", "failed"} else None
        if summary is not None:
            self.conn.execute(
                "UPDATE runs SET status=?, ended_at=COALESCE(?, ended_at), summary_json=? WHERE id=?",
                (status, ended, json.dumps(summary), run_id),
            )
        else:
            self.conn.execute(
                "UPDATE runs SET status=?, ended_at=COALESCE(?, ended_at) WHERE id=?",
                (status, ended, run_id),
            )
        self.conn.commit()

    def add_attempt(self, row: dict) -> None:
        self.conn.execute(
            """
            INSERT INTO attempts (
                run_id, model, scenario_id, attempt, ok, ttft_s, total_s, tok_s, load_s,
                prompt_tokens, output_tokens, q, e, hard_fail, error, output, grade_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["run_id"],
                row["model"],
                row["scenario_id"],
                row["attempt"],
                1 if row.get("ok") else 0,
                row.get("ttft_s"),
                row.get("total_s"),
                row.get("tok_s"),
                row.get("load_s"),
                row.get("prompt_tokens"),
                row.get("output_tokens"),
                row.get("q"),
                row.get("e"),
                1 if row.get("hard_fail") else 0,
                row.get("error"),
                row.get("output"),
                json.dumps(row.get("grade") or {}),
            ),
        )
        self.conn.commit()

    def upsert_scenario(self, row: dict) -> None:
        self.conn.execute(
            """
            INSERT OR REPLACE INTO scenario_scores (
                run_id, model, scenario_id, q, e, r, w, internal, customer, cap_reason, attempted, successful
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row["run_id"],
                row["model"],
                row["scenario_id"],
                row.get("q"),
                row.get("e"),
                row.get("r"),
                row.get("w"),
                row.get("internal"),
                row.get("customer"),
                row.get("cap_reason"),
                row.get("attempted"),
                row.get("successful"),
            ),
        )
        self.conn.commit()

    def latest(self) -> dict | None:
        cur = self.conn.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT 1")
        row = cur.fetchone()
        return dict(row) if row else None

    def get(self, run_id: str) -> dict | None:
        cur = self.conn.execute("SELECT * FROM runs WHERE id=?", (run_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def delete_run(self, run_id: str) -> None:
        self.conn.execute("DELETE FROM attempts WHERE run_id=?", (run_id,))
        self.conn.execute("DELETE FROM scenario_scores WHERE run_id=?", (run_id,))
        self.conn.execute("DELETE FROM runs WHERE id=?", (run_id,))
        self.conn.commit()

    def purge_run(self, run_id: str) -> tuple[bool, str]:
        """Remove the run row and every file in that report folder."""
        import re
        import shutil

        rid = (run_id or "").strip()
        if not re.fullmatch(r"[A-Za-z0-9._-]+", rid):
            return False, "Invalid report id."
        if not self.get(rid):
            return False, "Report not found."
        root = runs_dir().resolve()
        folder = (root / rid).resolve()
        try:
            folder.relative_to(root)
        except ValueError:
            return False, "Invalid report folder."
        if folder == root:
            return False, "Invalid report folder."
        self.delete_run(rid)
        if folder.is_dir():
            shutil.rmtree(folder, ignore_errors=True)
        return True, "Deleted."

    def prune_ghost_runs(self) -> None:
        """Drop finished runs whose folder no longer has a report or results file."""
        rows = self.conn.execute("SELECT id, status FROM runs").fetchall()
        for row in rows:
            rid = row["id"]
            if (row["status"] or "") == "running":
                continue
            folder = runs_dir() / rid
            if (folder / "report.html").is_file() or (folder / "results.xlsx").is_file():
                continue
            self.delete_run(rid)

    def list_runs(self, limit: int = 20) -> list[dict]:
        self.prune_ghost_runs()
        cur = self.conn.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,))
        return [dict(r) for r in cur.fetchall()]

    def attempts_for(self, run_id: str) -> list[dict]:
        cur = self.conn.execute("SELECT * FROM attempts WHERE run_id=? ORDER BY id", (run_id,))
        return [dict(r) for r in cur.fetchall()]

    def scenario_scores_for(self, run_id: str) -> list[dict]:
        cur = self.conn.execute("SELECT * FROM scenario_scores WHERE run_id=?", (run_id,))
        return [dict(r) for r in cur.fetchall()]

    def export_csv(self, run_id: str) -> Path:
        """One workbook: results.xlsx (kept name export_csv for callers)."""
        return self.export_results(run_id)

    def export_results(self, run_id: str) -> Path:
        from haval_engine.data.xlsx_export import write_xlsx

        folder = runs_dir() / run_id
        folder.mkdir(exist_ok=True)
        attempts = self.attempts_for(run_id)
        scenarios = self.scenario_scores_for(run_id)
        run = self.get(run_id) or {}

        def rows_from(items: list[dict], fields: list[str]) -> list[list[object]]:
            out: list[list[object]] = [fields]
            for item in items:
                out.append([item.get(k) for k in fields])
            return out

        write_xlsx(
            folder / "results.xlsx",
            {
                "Run": rows_from(
                    [run],
                    ["id", "started_at", "ended_at", "status", "models_json", "summary_json"],
                ),
                "Scenarios": rows_from(
                    scenarios,
                    [
                        "model",
                        "scenario_id",
                        "q",
                        "r",
                        "internal",
                        "customer",
                        "attempted",
                        "successful",
                    ],
                ),
                "Attempts": rows_from(
                    attempts,
                    [
                        "model",
                        "scenario_id",
                        "attempt",
                        "ok",
                        "ttft_s",
                        "total_s",
                        "tok_s",
                        "q",
                        "error",
                    ],
                ),
            },
        )
        return folder / "results.xlsx"
