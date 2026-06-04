from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import CurrentUser, get_org_id
from app.db.session import get_db
from app.models.prompt_version import PromptVersion
from app.schemas.common import SuccessResponse

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/prompts")
async def list_prompts(
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PromptVersion)
        .where(PromptVersion.org_id == org_id)
        .order_by(PromptVersion.name, PromptVersion.version.desc())
    )
    prompts = result.scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "version": p.version,
            "description": p.description,
            "is_active": p.is_active,
            "variables": p.variables,
            "created_at": p.created_at.isoformat(),
        }
        for p in prompts
    ]


@router.get("/prompts/{prompt_id}")
async def get_prompt(
    prompt_id: uuid.UUID,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PromptVersion).where(
            PromptVersion.id == prompt_id, PromptVersion.org_id == org_id
        )
    )
    prompt = result.scalar_one_or_none()
    if prompt is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Prompt not found")
    return {
        "id": str(prompt.id),
        "name": prompt.name,
        "version": prompt.version,
        "template": prompt.template,
        "variables": prompt.variables,
        "is_active": prompt.is_active,
    }


@router.put("/prompts/{prompt_id}", response_model=SuccessResponse)
async def update_prompt(
    prompt_id: uuid.UUID,
    updates: dict,
    org_id: uuid.UUID = Depends(get_org_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PromptVersion).where(
            PromptVersion.id == prompt_id, PromptVersion.org_id == org_id
        )
    )
    prompt = result.scalar_one_or_none()
    if prompt is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Prompt not found")

    for field in ("template", "description", "is_active"):
        if field in updates:
            setattr(prompt, field, updates[field])
    await db.flush()
    return SuccessResponse(message="Prompt updated")
