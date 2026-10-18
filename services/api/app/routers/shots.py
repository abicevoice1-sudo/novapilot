"""Serve browser screenshots (task artifacts)."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from ..agent import shots_dir
from ..auth import require_auth

router = APIRouter(prefix="/api/shots", tags=["shots"])


@router.get("/{name}")
def get_shot(name: str, _auth: None = Depends(require_auth)):
    # Traversal-proof: the name must resolve to a file directly inside shots_dir.
    path = (shots_dir() / name).resolve()
    if path.parent != shots_dir().resolve() or path.suffix.lower() != ".png" or not path.is_file():
        raise HTTPException(404, "screenshot not found")
    return FileResponse(path, media_type="image/png")
