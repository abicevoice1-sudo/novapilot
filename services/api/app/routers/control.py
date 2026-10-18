"""Global agent control: pause/resume, status."""

from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..control import in_quiet_hours, is_paused, set_paused

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.get("/status", dependencies=[Depends(require_auth)])
async def agent_status():
    return {
        "paused": is_paused(),
        "quiet_hours": in_quiet_hours(),
    }


@router.post("/pause", dependencies=[Depends(require_auth)])
async def pause_agent():
    set_paused(True)
    return {"paused": True}


@router.post("/resume", dependencies=[Depends(require_auth)])
async def resume_agent():
    set_paused(False)
    return {"paused": False}
