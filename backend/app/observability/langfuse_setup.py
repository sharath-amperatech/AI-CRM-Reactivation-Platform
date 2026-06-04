"""Langfuse observability — thin wrapper around the official v4 SDK.

Exports:
    observe              — the official @observe decorator (re-exported)
    configure_langfuse() — call once at app startup to set env vars
    flush_langfuse()     — call at app shutdown to drain the event queue
    get_current_trace_id() — returns the active Langfuse trace ID, or None
"""
from __future__ import annotations

import logging
import os

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def configure_langfuse() -> None:
    """Inject Langfuse credentials into env vars so the SDK decorator finds them."""
    settings = get_settings()
    pub = settings.LANGFUSE_PUBLIC_KEY
    sec = settings.LANGFUSE_SECRET_KEY.get_secret_value()
    if not pub or not sec:
        logger.info("langfuse_skipped: no keys configured")
        return
    os.environ.setdefault("LANGFUSE_PUBLIC_KEY", pub)
    os.environ.setdefault("LANGFUSE_SECRET_KEY", sec)
    os.environ.setdefault("LANGFUSE_HOST", settings.LANGFUSE_HOST)
    logger.info("langfuse_configured", extra={"host": settings.LANGFUSE_HOST})


def flush_langfuse() -> None:
    """Flush buffered Langfuse events. Call at shutdown."""
    try:
        from langfuse import get_client  # type: ignore[import]
        get_client().flush()
        logger.info("langfuse_flushed")
    except Exception as exc:
        logger.debug("langfuse_flush_error: %s", exc)


def get_current_trace_id() -> str | None:
    """Return the active Langfuse trace ID from context, or None."""
    try:
        from langfuse import get_client  # type: ignore[import]
        return get_client().get_current_trace_id()
    except Exception:
        return None


try:
    from langfuse import observe  # type: ignore[import]
except ImportError:
    import functools
    from typing import Callable

    def observe(fn: Callable | None = None, **_: object) -> Callable:  # type: ignore[misc]
        """No-op fallback when langfuse is not installed."""
        def decorator(f: Callable) -> Callable:
            @functools.wraps(f)
            async def wrapper(*args, **kwargs):
                return await f(*args, **kwargs)
            return wrapper
        return decorator(fn) if fn is not None else decorator
