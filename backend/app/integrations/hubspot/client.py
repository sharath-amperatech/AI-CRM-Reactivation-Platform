from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
HUBSPOT_API_BASE = "https://api.hubapi.com"


class HubSpotClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._client = httpx.AsyncClient(
            base_url=HUBSPOT_API_BASE,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=30,
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_contacts(
        self, limit: int = 100, after: str | None = None
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "properties": [
            "firstname", "lastname", "email", "phone", "company",
            "jobtitle", "industry", "city", "hs_lead_status",
        ]}
        if after:
            params["after"] = after
        resp = await self._client.get("/crm/v3/objects/contacts", params=params)
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_contact(self, contact_id: str) -> dict[str, Any]:
        resp = await self._client.get(
            f"/crm/v3/objects/contacts/{contact_id}",
            params={"properties": ["firstname", "lastname", "email", "phone", "company",
                                   "jobtitle", "industry", "hs_lead_status"]},
        )
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_engagements(
        self, contact_id: str, limit: int = 100
    ) -> dict[str, Any]:
        resp = await self._client.get(
            f"/crm/v3/objects/contacts/{contact_id}/associations/engagements",
            params={"limit": limit},
        )
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_engagement_detail(self, engagement_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/engagements/v1/engagements/{engagement_id}")
        resp.raise_for_status()
        return resp.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def get_deals_for_contact(self, contact_id: str) -> dict[str, Any]:
        resp = await self._client.get(
            f"/crm/v3/objects/contacts/{contact_id}/associations/deals",
            params={"limit": 50},
        )
        resp.raise_for_status()
        return resp.json()


def get_hubspot_client() -> HubSpotClient:
    settings = get_settings()
    return HubSpotClient(api_key=settings.HUBSPOT_API_KEY.get_secret_value())
