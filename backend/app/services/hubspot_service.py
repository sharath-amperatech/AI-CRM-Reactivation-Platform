from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.integrations.hubspot.client import get_hubspot_client
from app.integrations.hubspot.sync import HubSpotSyncService

logger = get_logger(__name__)


class HubSpotService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def sync_contacts(self, org_id: str) -> dict[str, int]:
        client = get_hubspot_client()
        sync = HubSpotSyncService(client=client, db=self._db)
        try:
            return await sync.sync_contacts(org_id=org_id)
        finally:
            await client.close()

    async def test_connection(self) -> bool:
        client = get_hubspot_client()
        try:
            await client.get_contacts(limit=1)
            return True
        except Exception:
            return False
        finally:
            await client.close()
