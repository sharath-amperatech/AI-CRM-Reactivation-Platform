from __future__ import annotations

from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.api.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    ReactivIQError,
    http_exception_handler,
    reactiviq_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import configure_logging, get_logger
from app.core.middleware import RequestIDMiddleware, SecurityHeadersMiddleware
from app.db.base import close_engine, get_engine

# Configure structlog before any logger is created so the cache is warm
# with the correct processor chain — avoids TypeError on keyword log args.
_settings = get_settings()
configure_logging(debug=_settings.DEBUG, json_logs=not _settings.is_development)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    from app.observability import configure_langfuse
    configure_langfuse()

    logger.info(
        "reactiviq_starting",
        env=settings.APP_ENV,
        debug=settings.DEBUG,
        database_url=settings.DATABASE_URL.split("@")[-1],  # hide credentials
    )

    # Initialize DB engine (validates connectivity)
    engine = get_engine()

    # Pre-compile LangGraph (validates workflow on startup)
    try:
        from app.workflows.graph import get_compiled_graph
        _graph = get_compiled_graph()
        logger.info("workflow_graph_compiled")
    except Exception as exc:
        logger.warning("workflow_graph_compile_failed", error=str(exc))

    yield

    logger.info("reactiviq_shutting_down")
    await close_engine()

    from app.observability import flush_langfuse
    flush_langfuse()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title="ReactivIQ API",
        description="AI-powered CRM reactivation platform",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
        default_response_class=ORJSONResponse,
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost first) ───────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    # ── Exception handlers ────────────────────────────────────
    app.add_exception_handler(ReactivIQError, reactiviq_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Routes ────────────────────────────────────────────────
    app.include_router(api_router)

    # ── Health check ──────────────────────────────────────────
    @app.get("/health", tags=["health"])
    async def health():
        from sqlalchemy import text
        from app.db.base import get_session_factory

        db_status = "ok"
        redis_status = "ok"

        try:
            factory = get_session_factory()
            async with factory() as db:
                await db.execute(text("SELECT 1"))
        except Exception:
            db_status = "error"

        try:
            r = aioredis.from_url(settings.REDIS_URL)
            await r.ping()
            await r.aclose()
        except Exception:
            redis_status = "error"

        return {
            "status": "ok" if db_status == "ok" and redis_status == "ok" else "degraded",
            "version": "0.1.0",
            "environment": settings.APP_ENV,
            "database": db_status,
            "redis": redis_status,
        }

    return app


app = create_app()
