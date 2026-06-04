from __future__ import annotations

import hashlib
import hmac
import secrets
from typing import Any

import httpx
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
_jwks_cache: dict | None = None


async def _fetch_jwks() -> dict:
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache
    settings = get_settings()
    if not settings.CLERK_JWKS_URL:
        return {"keys": []}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(settings.CLERK_JWKS_URL)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        return _jwks_cache


async def verify_clerk_jwt(token: str) -> dict[str, Any]:
    jwks = await _fetch_jwks()
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        logger.warning("clerk_jwt_verification_failed", error=str(e))
        raise


def generate_api_key() -> tuple[str, str]:
    """Returns (plaintext_key, sha256_hash). Store only the hash."""
    settings = get_settings()
    raw = secrets.token_urlsafe(32)
    key = f"{settings.API_KEY_PREFIX}{raw}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return key, key_hash


def verify_api_key(plaintext_key: str, stored_hash: str) -> bool:
    computed = hashlib.sha256(plaintext_key.encode()).hexdigest()
    return hmac.compare_digest(computed, stored_hash)


def invalidate_jwks_cache() -> None:
    global _jwks_cache
    _jwks_cache = None
