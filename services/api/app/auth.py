"""Token auth. If NOVAPILOT_TOKEN is set, /api/* requires it as a Bearer token.
Unset = open access (local single-user default), logged as a warning at startup."""

import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

log = logging.getLogger("novapilot.auth")
_bearer = HTTPBearer(auto_error=False)


async def require_auth(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> None:
    token = settings.novapilot_token
    if not token:
        return  # open in dev
    if creds is None or creds.credentials != token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")


def auth_warning() -> None:
    if not settings.novapilot_token:
        log.warning("NOVAPILOT_TOKEN not set — API is open. Set a token for shared networks.")
