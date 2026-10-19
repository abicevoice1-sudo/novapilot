"""POST /api/chat — streaming chat with the model gateway (SSE)."""

import json
import logging

from actlet_gateway import BudgetExceeded, GatewayError
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import require_auth
from ..db import Conversation, Message, get_session
from ..gateway_dep import get_gateway

log = logging.getLogger("actlet.chat")
router = APIRouter()


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(max_length=20000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(max_length=200)
    model: str | None = None
    conversation_id: str | None = Field(default=None, max_length=200)


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

    # Audit fix: the frontend sends full history, but only the NEWEST user
    # message is new — earlier ones are already persisted. Persisting all of
    # them duplicates history on every turn.
    new_user_msgs = [m for m in req.messages if m.role == "user"]
    if new_user_msgs:
        session.add(Message(conversation_id=conv.id, role="user",
                            content=new_user_msgs[-1].content))
    await session.commit()

    payload = [{"role": m.role, "content": m.content} for m in req.messages]
    conv_id = conv.id

    # Compress long conversations so old turns don't drown the context window.
    if len(payload) > 22:
        from .memories import compress_conversation as _compress
        payload = _compress(payload)

    # Recall: inject relevant long-term memories so Actlet remembers last week.
    # Best-effort — chat works fine if memory is unavailable.
    try:
        from ..config import settings as _settings
        from ..memory import get_memory_service as _get_mem
        from .memories import build_memory_context as _ctx

        _svc = await _get_mem()
        _last_user = next((m.content for m in reversed(req.messages) if m.role == "user"), "")
        if _last_user:
            _hits = await _svc.recall(_settings.memory_namespace, _last_user, limit=5)
            if _hits:
                payload = [{"role": "system", "content": _ctx(_hits)}, *payload]
    except Exception:
        log.debug("memory recall skipped", exc_info=True)

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
