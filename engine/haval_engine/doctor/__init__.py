from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from haval_engine.doctor.service import SERVICE

router = APIRouter(prefix="/doctor", tags=["doctor"])


class RepairBody(BaseModel):
    action: str | None = None


@router.get("/status")
def doctor_status() -> dict:
    return SERVICE.snapshot()


@router.post("/run")
def doctor_run() -> dict:
    SERVICE.run_async(repair=False)
    return SERVICE.snapshot()


@router.post("/repair")
def doctor_repair(_: RepairBody | None = None) -> dict:
    SERVICE.run_async(repair=True)
    return SERVICE.snapshot()


@router.get("/events")
async def doctor_events(request: Request) -> StreamingResponse:
    queue: asyncio.Queue[dict] = asyncio.Queue()
    loop = asyncio.get_event_loop()

    def push(snap: dict) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, snap)

    SERVICE.subscribe(push)
    queue.put_nowait(SERVICE.snapshot())

    async def gen():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    snap = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {json.dumps(snap)}\n\n"
                except TimeoutError:
                    yield "data: {\"ping\": true}\n\n"
        finally:
            SERVICE.unsubscribe(push)

    return StreamingResponse(gen(), media_type="text/event-stream")
