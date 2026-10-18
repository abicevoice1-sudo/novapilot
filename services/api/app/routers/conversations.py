"""Conversation history (persisted in SQLite/Postgres)."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..db import Conversation, Message, get_session

router = APIRouter()


@router.get("/api/conversations")
async def list_conversations(
    session: AsyncSession = Depends(get_session), _auth: None = Depends(require_auth)
):
    rows = (
        (await session.execute(select(Conversation).order_by(Conversation.created_at.desc())))
        .scalars()
        .all()
    )
    return {
        "conversations": [
            {"id": c.id, "title": c.title, "created_at": c.created_at.isoformat()} for c in rows
        ]
    }


@router.get("/api/conversations/{conv_id}/messages")
async def get_messages(
    conv_id: str,
    session: AsyncSession = Depends(get_session),
    _auth: None = Depends(require_auth),
):
    conv = await session.get(Conversation, conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail="conversation not found")
    rows = (
        (
            await session.execute(
                select(Message)
                .where(Message.conversation_id == conv_id)
                .order_by(Message.created_at)
            )
        )
        .scalars()
        .all()
    )
    return {
        "messages": [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in rows
        ]
    }
