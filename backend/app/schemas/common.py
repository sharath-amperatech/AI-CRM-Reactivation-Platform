from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class APIModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class PaginatedResponse(APIModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(APIModel):
    error: str
    message: str
    details: dict | None = None


class SuccessResponse(APIModel):
    success: bool = True
    message: str


class HealthResponse(APIModel):
    status: str
    version: str
    environment: str
    database: str
    redis: str
