"""Channel status endpoints."""

from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..channels import get_channel_manager

router = APIRouter(prefix="/api/channels", tags=["channels"])


@router.get("", dependencies=[Depends(require_auth)])
async def channel_status():
    mgr = get_channel_manager()
    return {"channels": mgr.status()}
