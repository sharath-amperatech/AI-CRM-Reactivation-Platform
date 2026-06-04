from __future__ import annotations

from fastapi import HTTPException, Request, status
from fastapi.responses import ORJSONResponse


class ReactivIQError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, code: str = "internal_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(ReactivIQError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(f"{resource} '{resource_id}' not found", code="not_found")


class ForbiddenError(ReactivIQError):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message, code="forbidden")


class ConflictError(ReactivIQError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="conflict")


class ValidationError(ReactivIQError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="validation_error")


class ExternalServiceError(ReactivIQError):
    def __init__(self, service: str, message: str) -> None:
        super().__init__(f"{service} error: {message}", code="external_service_error")


# ── FastAPI exception handlers ────────────────────────────────

async def reactiviq_exception_handler(request: Request, exc: ReactivIQError) -> ORJSONResponse:
    status_map = {
        "not_found": status.HTTP_404_NOT_FOUND,
        "forbidden": status.HTTP_403_FORBIDDEN,
        "conflict": status.HTTP_409_CONFLICT,
        "validation_error": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "external_service_error": status.HTTP_502_BAD_GATEWAY,
        "internal_error": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }
    http_status = status_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    return ORJSONResponse(
        status_code=http_status,
        content={"error": exc.code, "message": exc.message},
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "message": exc.detail},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    return ORJSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "internal_error", "message": "An unexpected error occurred"},
    )
