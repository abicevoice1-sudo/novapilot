"""GET /api/models — model catalog from the gateway."""

from dataclasses import asdict

from fastapi import APIRouter, Depends

from ..auth import require_auth
from ..gateway_dep import get_gateway

router = APIRouter()


@router.get("/api/models")
async def list_models(_auth: None = Depends(require_auth)):
    gw = get_gateway()
    return {"default": gw.default_model, "models": [asdict(m) for m in gw.list_models()]}
