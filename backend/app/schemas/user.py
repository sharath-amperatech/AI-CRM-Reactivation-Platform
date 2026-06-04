from __future__ import annotations

import uuid
from datetime import datetime

from app.models.user import UserRole
from app.schemas.common import APIModel


class UserRead(APIModel):
    id: uuid.UUID
    org_id: uuid.UUID
    email: str
    name: str
    role: UserRole
    is_active: bool
    clerk_user_id: str | None
    created_at: datetime


class UserUpdate(APIModel):
    name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
