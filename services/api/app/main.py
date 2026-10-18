"""NovaPilot API — Milestone 3: agent core.

Chat (streaming SSE) + model catalog + conversation history, backed by the
LiteLLM model gateway (Ollama default, free-tier fallbacks, enforced budgets).
Agent tasks: LangGraph plan→execute→verify with tool calls, approval gates,
task states, cancellation, retries, and budgets.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .agent import get_runner_or_none
from .auth import auth_warning
from .config import settings
from .db import init_db
from .logging_config import configure_logging
from .routers import chat, conversations, memories, models, tasks

configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    auth_warning()
    from .agent import build_runner, override_runner
    from .memory import close_memory_service, get_memory_service

    if get_runner_or_none() is None:  # tests may inject their own runner
        memory_svc = await get_memory_service()
        override_runner(build_runner(memory_svc))
    runner = get_runner_or_none()
    await runner.reconcile()  # tasks orphaned by a restart become resumable
    yield
    await runner.aclose()
    await close_memory_service()


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
app.include_router(tasks.router)
app.include_router(memories.router)


@app.get("/health")
def health() -> dict:
    return {
        "ok": True,
        "service": "novapilot-api",
        "milestone": 3,
        "model_default": settings.model_default,
    }
