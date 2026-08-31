from __future__ import annotations

import os
import secrets

from fastapi import Header, HTTPException

DEV_TOKEN = "dev-local-token"


def expected_token() -> str:
    return os.environ.get("HAVAL_ENGINE_TOKEN") or DEV_TOKEN


def require_token(authorization: str | None = Header(default=None)) -> None:
    token = expected_token()
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization")
    scheme, _, value = authorization.partition(" ")
    provided = value if scheme.lower() == "bearer" else authorization
    if not secrets.compare_digest(provided, token):
        raise HTTPException(status_code=401, detail="Invalid token")
