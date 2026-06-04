from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    approvals,
    campaigns,
    integrations,
    leads,
    quality,
    settings,
    webhooks,
    workflows,
)

api_router = APIRouter()

# Versioned API routes
api_router.include_router(leads.router, prefix="/api/v1")
api_router.include_router(campaigns.router, prefix="/api/v1")
api_router.include_router(approvals.router, prefix="/api/v1")
api_router.include_router(analytics.router, prefix="/api/v1")
api_router.include_router(quality.router, prefix="/api/v1")
api_router.include_router(integrations.router, prefix="/api/v1")
api_router.include_router(settings.router, prefix="/api/v1")
api_router.include_router(workflows.router, prefix="/api/v1")

# Webhooks (no version prefix — stable external URLs)
api_router.include_router(webhooks.router)
