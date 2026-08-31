"""Commercial Engineer & Software Developer Phase 1 tasks.

Prompts and seeds follow Doc/engineer-software-developer-code-examples.md.
Quality is judged by hidden execution (Phase 2 coding-style pass/fail), not keywords.
"""

from __future__ import annotations

# Installed FastAPI/Pydantic are not required. The sandbox prepends this so the
# model's publish_api.py can import those names and we still call the handlers.
FASTAPI_PRELUDE = r"""
import sys
import types

_fastapi = types.ModuleType("fastapi")

class HTTPException(Exception):
    def __init__(self, status_code=400, detail=""):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

class FastAPI:
    def __init__(self, *a, **k):
        pass
    def post(self, *a, **k):
        def deco(fn):
            return fn
        return deco
    def get(self, *a, **k):
        def deco(fn):
            return fn
        return deco

_fastapi.FastAPI = FastAPI
_fastapi.HTTPException = HTTPException
sys.modules["fastapi"] = _fastapi

_pyd = types.ModuleType("pydantic")

class BaseModel:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def Field(default=None, **kwargs):
    return default

_pyd.BaseModel = BaseModel
_pyd.Field = Field
sys.modules["pydantic"] = _pyd
"""

LIGHT_PROMPT = (
    "Write a complete stdlib-only Python CLI `dupscan.py`: scan a folder, group files by "
    "SHA-256 content hash, and print duplicate groups. Required: `file_hash(path)`, "
    "`scan(root)` returning only groups with 2+ files, argparse `main`, streaming reads. "
    "One file, no network, no third-party packages. Put the code in a python fence."
)

LIGHT_SEED = r'''
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
'''

LIGHT_TESTS = r"""
from pathlib import Path
root = Path("scanroot")
(root / "sub").mkdir(parents=True)
(root / "a.txt").write_bytes(b"same-bytes")
(root / "sub" / "b.txt").write_bytes(b"same-bytes")
(root / "c.txt").write_bytes(b"other")
assert file_hash(root / "a.txt") == file_hash(root / "sub" / "b.txt")
dups = scan(root)
assert len(dups) == 1
names = {p.name for p in next(iter(dups.values()))}
assert names == {"a.txt", "b.txt"}
empty = Path("empty")
empty.mkdir()
assert scan(empty) == {}
"""

LIGHT_BAD = """
def file_hash(path):
    return str(path)
def scan(root):
    return {}
def main():
    pass
"""

BALANCED_PROMPT = (
    "Write a working FastAPI publish job service (one Python file): pydantic JobIn/JobOut, "
    "SQLite jobs table, POST /jobs (202, enqueue), GET /jobs/{id} (404 if missing), "
    "Status enum queued/running/ok/failed, async worker that marks the job ok, lifespan "
    "init_db. Real error handling. No network calls. Fence the code."
)

BALANCED_SEED = r'''
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
    await asyncio.sleep(0.05)
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
'''

BALANCED_TESTS = r"""
import asyncio
init_db()
job = asyncio.run(create_job(JobIn(platform="yt", payload={"t": 1})))
assert job.id
assert str(job.status) in ("queued", "Status.queued") or getattr(job.status, "value", None) == "queued"
got = get_job(job.id)
assert got.id == job.id
try:
    get_job("missing-id-xyz")
    raise AssertionError("expected 404")
except HTTPException as exc:
    assert getattr(exc, "status_code", 404) == 404
"""

BALANCED_BAD = """
from fastapi import FastAPI, HTTPException
class JobIn:
    pass
class JobOut:
    pass
def init_db():
    pass
async def worker(job_id):
    pass
async def create_job(body):
    return None
def get_job(job_id):
    return None
app = FastAPI()
"""

HEAVY_PROMPT = (
    "Write a working in-memory job publisher that demonstrates the double-claim race and the fix. "
    "Required: Status (queued, leased, ok, failed), dataclass Job, claim_job_broken (check-then-act; "
    "yield with asyncio.sleep(0) between check and set so two workers can both win), "
    "JobStore with add/jobs/lock, atomic claim_job(store, worker_id) using a lock and expired-lease "
    "reclaim, publish_with_backoff, Retryable, Fatal, run_worker. Define the functions only — "
    "do not call run_worker() or start an infinite loop. No network. Fence the code."
)

HEAVY_SEED = r'''
from __future__ import annotations
import asyncio
import random
from datetime import datetime, timedelta, timezone
from enum import Enum


class Status(str, Enum):
    queued = "queued"
    leased = "leased"
    ok = "ok"
    failed = "failed"


class Job:
    def __init__(
        self,
        id,
        platform,
        attempts=0,
        status=None,
        lease_until=None,
        lease_owner=None,
    ):
        self.id = id
        self.platform = platform
        self.attempts = attempts
        self.status = Status.queued if status is None else status
        self.lease_until = lease_until
        self.lease_owner = lease_owner


class JobStore:
    def __init__(self) -> None:
        self.jobs: list[Job] = []
        self.lock = asyncio.Lock()

    def add(self, job: Job) -> None:
        self.jobs.append(job)

    async def mark_ok(self, job_id: str) -> None:
        async with self.lock:
            for j in self.jobs:
                if j.id == job_id:
                    j.status = Status.ok

    async def mark_failed(self, job_id: str, err: str) -> None:
        async with self.lock:
            for j in self.jobs:
                if j.id == job_id:
                    j.status = Status.failed

    async def release_to_queued(self, job_id: str) -> None:
        async with self.lock:
            for j in self.jobs:
                if j.id == job_id:
                    j.status = Status.queued
                    j.lease_until = None
                    j.lease_owner = None


async def claim_job_broken(jobs: list[Job]) -> Job | None:
    for j in jobs:
        if j.status == Status.queued:
            await asyncio.sleep(0)
            j.status = Status.leased
            return j
    return None


async def claim_job(store: JobStore, worker_id: str) -> Job | None:
    now = datetime.now(timezone.utc)
    async with store.lock:
        for j in store.jobs:
            expired = j.status == Status.leased and j.lease_until is not None and j.lease_until < now
            if j.status == Status.queued or expired:
                j.status = Status.leased
                j.lease_owner = worker_id
                j.lease_until = now + timedelta(seconds=30)
                j.attempts += 1
                return j
    return None


class Retryable(Exception):
    pass


class Fatal(Exception):
    pass


async def publish_with_backoff(job: Job) -> None:
    delay = min(2 ** max(job.attempts, 1), 60)
    await asyncio.sleep(min(delay * 0.001, 0.02))


async def run_worker(store: JobStore, worker_id: str) -> None:
    while True:
        job = await claim_job(store, worker_id)
        if not job:
            await asyncio.sleep(0.5)
            continue
        try:
            await publish_with_backoff(job)
            await store.mark_ok(job.id)
        except Retryable:
            await store.release_to_queued(job.id)
        except Fatal as e:
            await store.mark_failed(job.id, str(e))
        except Exception:
            await store.release_to_queued(job.id)
            raise
'''

HEAVY_TESTS = r"""
import asyncio
from datetime import datetime, timedelta, timezone

store = JobStore()
store.add(Job(id="j1", platform="yt", attempts=0, status=Status.queued, lease_until=None))

async def race():
    a, b = await asyncio.gather(claim_job(store, "w1"), claim_job(store, "w2"))
    won = [x for x in (a, b) if x is not None]
    assert len(won) == 1

asyncio.run(race())

jobs = [Job(id="dup", platform="yt", attempts=0, status=Status.queued, lease_until=None)]

async def broken_race():
    x, y = await asyncio.gather(claim_job_broken(jobs), claim_job_broken(jobs))
    assert x is not None and y is not None and x.id == y.id

asyncio.run(broken_race())

store2 = JobStore()
old = Job(
    id="j2",
    platform="ig",
    attempts=1,
    status=Status.leased,
    lease_until=datetime.now(timezone.utc) - timedelta(seconds=5),
)
store2.add(old)
got = asyncio.run(claim_job(store2, "w3"))
assert got is not None and got.id == "j2"
assert issubclass(Retryable, Exception) and issubclass(Fatal, Exception)
"""

HEAVY_BAD = """
from enum import Enum
class Status(str, Enum):
    queued = "queued"
    leased = "leased"
class Job:
    def __init__(self, **k):
        self.__dict__.update(k)
class JobStore:
    def __init__(self):
        self.jobs = []
    def add(self, job):
        self.jobs.append(job)
async def claim_job_broken(jobs):
    return jobs[0] if jobs else None
async def claim_job(store, worker_id):
    return None
class Retryable(Exception):
    pass
class Fatal(Exception):
    pass
"""
