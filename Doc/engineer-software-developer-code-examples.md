# Engineer & Software Developer — 3 Code Examples

Light developing → balanced feature → heavy build & debug.

---

## Agents in the room

- **Maya** — mid-level engineer who ships small tools weekly
- **Rafi** — staff engineer who owns production systems
- **Lin** — hiring manager who screens “Engineer & Software Developer” portfolios

They argued for 2 minutes, then agreed on one rule: each example must show *what the person actually typed*, not a job-title paragraph.

**Maya:** Light should be something you can finish in a sitting and still be proud of. No frameworks, no infra.

**Rafi:** Balanced needs real error paths, config, and a little architecture. That’s the “I can own a feature” bar.

**Lin:** Heavy has to look like production pain — state, retries, concurrency, or a nasty debug. That’s the “I won’t set the house on fire” bar.

They locked these three.

---

## 1. Light — build a small, finished utility

**Task:** CLI that scans a folder, finds duplicate files by content hash, and prints a report. One file, stdlib only.

```python
#!/usr/bin/env python3
"""dupscan.py — find duplicate files by SHA-256. Light Saturday project."""
from __future__ import annotations
import argparse
import hashlib
from collections import defaultdict
from pathlib import Path


def file_hash(path: Path, chunk: int = 1 << 16) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def scan(root: Path) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = defaultdict(list)
    for p in root.rglob("*"):
        if p.is_file():
            groups[file_hash(p)].append(p)
    return {k: v for k, v in groups.items() if len(v) > 1}


def main() -> None:
    parser = argparse.ArgumentParser(description="Find duplicate files")
    parser.add_argument("path", type=Path, help="directory to scan")
    args = parser.parse_args()
    if not args.path.is_dir():
        raise SystemExit(f"not a directory: {args.path}")

    dups = scan(args.path)
    if not dups:
        print("No duplicates found.")
        return
    for digest, paths in dups.items():
        print(f"\n{digest[:12]}…  ({len(paths)} copies)")
        for p in paths:
            print(f"  {p}")


if __name__ == "__main__":
    main()
```

**What this shows:** you can ship a complete, usable tool with argparse, streaming I/O, and a clean main. That’s light developing.

---

## 2. Balanced — own a feature end-to-end

**Task:** Small FastAPI service that accepts a publish job, stores status in SQLite, and exposes poll + retry. Real error handling, typed models, one background worker.

```python
# publish_api.py — balanced “I own this service” example
from __future__ import annotations
import asyncio
import sqlite3
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

DB = Path("jobs.db")


class Status(str, Enum):
    queued = "queued"
    running = "running"
    ok = "ok"
    failed = "failed"


class JobIn(BaseModel):
    platform: str = Field(..., min_length=2, max_length=32)
    payload: dict


class JobOut(BaseModel):
    id: str
    status: Status
    error: str | None = None
    updated_at: datetime


def _db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _db() as c:
        c.execute(
            """CREATE TABLE IF NOT EXISTS jobs (
                   id TEXT PRIMARY KEY,
                   platform TEXT NOT NULL,
                   payload TEXT NOT NULL,
                   status TEXT NOT NULL,
                   error TEXT,
                   updated_at TEXT NOT NULL
               )"""
        )


async def worker(job_id: str) -> None:
    await asyncio.sleep(0.4)  # stand-in for upload
    with _db() as c:
        c.execute(
            "UPDATE jobs SET status=?, updated_at=? WHERE id=?",
            (Status.ok.value, datetime.now(timezone.utc).isoformat(), job_id),
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Publish API", lifespan=lifespan)


@app.post("/jobs", response_model=JobOut, status_code=202)
async def create_job(body: JobIn) -> JobOut:
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    with _db() as c:
        c.execute(
            "INSERT INTO jobs VALUES (?,?,?,?,?,?)",
            (job_id, body.platform, str(body.payload), Status.queued.value, None, now.isoformat()),
        )
    asyncio.create_task(worker(job_id))
    return JobOut(id=job_id, status=Status.queued, updated_at=now)


@app.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: str) -> JobOut:
    with _db() as c:
        row = c.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "job not found")
    return JobOut(
        id=row["id"],
        status=Status(row["status"]),
        error=row["error"],
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
```

**What this shows:** models, persistence, async side-effect, HTTP contract, and failure surface. Balanced — not a toy, not a platform.

---

## 3. Heavy — debug + harden a production-shaped system

**Task:** Multi-platform publisher with at-least-once delivery, per-platform backoff, and a race you actually have to fix.

**Symptom you inherited:** two workers pick the same `queued` row, both “succeed,” customer gets double posts.

```python
# heavy_publisher.py — excerpt: the bug + the fix
from __future__ import annotations
import asyncio
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class Status(str, Enum):
    queued = "queued"
    leased = "leased"
    ok = "ok"
    failed = "failed"


@dataclass
class Job:
    id: str
    platform: str
    attempts: int
    status: Status
    lease_until: datetime | None


# --- BROKEN claim (the thing you debug) ---
async def claim_job_broken(jobs: list[Job]) -> Job | None:
    for j in jobs:
        if j.status == Status.queued:
            j.status = Status.leased          # two workers can both pass this check
            return j
    return None


# --- FIXED claim: compare-and-swap + short lease ---
async def claim_job(store: "JobStore", worker_id: str) -> Job | None:
    """Atomic lease. Only one worker wins."""
    now = datetime.now(timezone.utc)
    job = await store.fetch_one(
        """
        UPDATE jobs
           SET status = :leased,
               lease_owner = :wid,
               lease_until = :until,
               attempts = attempts + 1
         WHERE id = (
               SELECT id FROM jobs
                WHERE status = :queued
                   OR (status = :leased AND lease_until < :now)
                ORDER BY updated_at
                LIMIT 1
               )
           AND (status = :queued
                OR (status = :leased AND lease_until < :now))
     RETURNING *
        """,
        queued=Status.queued.value,
        leased=Status.leased.value,
        wid=worker_id,
        until=(now + timedelta(seconds=30)).isoformat(),
        now=now.isoformat(),
    )
    return job


async def publish_with_backoff(job: Job) -> None:
    delay = min(2 ** job.attempts, 60)
    await asyncio.sleep(delay * random.uniform(0.8, 1.2))
    # platform call here; on 429/5xx raise Retryable; on 4xx raise Fatal


class Retryable(Exception):
    ...


class Fatal(Exception):
    ...


async def run_worker(store: "JobStore", worker_id: str) -> None:
    while True:
        job = await claim_job(store, worker_id)
        if not job:
            await asyncio.sleep(0.5)
            continue
        try:
            await publish_with_backoff(job)
            await store.mark_ok(job.id)
        except Retryable:
            await store.release_to_queued(job.id)   # lease expires → another worker
        except Fatal as e:
            await store.mark_failed(job.id, str(e))
        except Exception:
            await store.release_to_queued(job.id)
            raise
```

**What this shows:** you found a real race, replaced a check-then-act with a single atomic lease, added backoff and poison-pill handling. That’s heavy engineer work — build *and* debug.

---

## Lin’s close

Light proves you finish things. Balanced proves you design a feature. Heavy proves you can keep a system honest under concurrency and failure. Put one of each in a repo and most “Engineer & Software Developer” screens pass.
