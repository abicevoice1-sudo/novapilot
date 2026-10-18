"""NovaPilot API — Milestone 2: running foundation.

Chat (streaming SSE) + model catalog + conversation history, backed by the
LiteLLM model gateway (Ollama default, free-tier fallbacks, enforced budgets).
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import auth_warning
from .config import settings
from .db import init_db
from .logging_config import configure_logging
from .routers import chat, conversations, models

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    auth_warning()
    yield


app = FastAPI(title="NovaPilot API", version="0.2.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat.router)
app.include_router(models.router)
app.include_router(conversations.router)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "novapilot-api",
        "milestone": 2,
        "model_default": settings.model_default,
    }
