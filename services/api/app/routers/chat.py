"""POST /api/chat — streaming chat with the model gateway (SSE)."""

import json
import logging

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from novapilot_gateway import BudgetExceeded, GatewayError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..db import Conversation, Message, get_session
from ..gateway_dep import get_gateway

log = logging.getLogger("novapilot.chat")
router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: str | None = None
    conversation_id: str | None = None


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


@router.post("/api/chat")
async def chat(
    req: ChatRequest,
    session: AsyncSession = Depends(get_session),
    _auth: None = Depends(require_auth),
):
    gateway = get_gateway()

    conv: Conversation | None = None
    if req.conversation_id:
        conv = await session.get(Conversation, req.conversation_id)
    if conv is None:
        title = next((m.content[:60] for m in req.messages if m.role == "user"), "New chat")
        conv = Conversation(title=title or "New chat")
        session.add(conv)
        await session.flush()

    for m in req.messages:
        if m.role == "user":
            session.add(Message(conversation_id=conv.id, role=m.role, content=m.content))
    await session.commit()

    payload = [{"role": m.role, "content": m.content} for m in req.messages]
    conv_id = conv.id

    async def gen():
        yield _sse({"type": "started", "conversation_id": conv_id})
        parts: list[str] = []
        try:
            async for delta in gateway.chat_stream(payload, model=req.model):
                parts.append(delta)
                yield _sse({"type": "delta", "text": delta})
        except BudgetExceeded as e:
            log.warning("chat budget exceeded conv=%s: %s", conv_id, e)
            yield _sse({"type": "error", "message": f"Budget exceeded: {e}"})
            return
        except GatewayError as e:
            log.warning("chat gateway failed conv=%s: %s", conv_id, e)
            yield _sse({"type": "error", "message": str(e)})
            return
        text = "".join(parts)
        session.add(Message(conversation_id=conv_id, role="assistant", content=text))
        await session.commit()
        log.info("chat done conv=%s chars=%d usage=%s", conv_id, len(text), gateway.usage())
        yield _sse({"type": "done", "conversation_id": conv_id, "usage": gateway.usage()})

    return StreamingResponse(gen(), media_type="text/event-stream")
