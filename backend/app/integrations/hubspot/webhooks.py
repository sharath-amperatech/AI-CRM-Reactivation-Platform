from __future__ import annotations

from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


class HubSpotWebhookHandler:
    """Parses and dispatches HubSpot webhook events."""

    SUPPORTED_EVENTS = {
        "contact.creation",
        "contact.propertyChange",
        "deal.creation",
        "deal.propertyChange",
    }

    async def handle(self, events: list[dict[str, Any]]) -> dict[str, int]:
        processed = skipped = errors = 0

        for event in events:
            event_type = event.get("subscriptionType", "")
            if event_type not in self.SUPPORTED_EVENTS:
                skipped += 1
                continue
            try:
                await self._dispatch(event_type, event)
                processed += 1
            except Exception as exc:
                logger.error(
                    "hubspot_webhook_dispatch_error",
                    event_type=event_type,
                    error=str(exc),
                )
                errors += 1

        return {"processed": processed, "skipped": skipped, "errors": errors}

    async def _dispatch(self, event_type: str, event: dict[str, Any]) -> None:
        if event_type == "contact.creation":
            await self._on_contact_created(event)
        elif event_type == "contact.propertyChange":
            await self._on_contact_updated(event)
        elif event_type in ("deal.creation", "deal.propertyChange"):
            await self._on_deal_changed(event)

    async def _on_contact_created(self, event: dict) -> None:
        logger.info("hubspot_contact_created", object_id=event.get("objectId"))

    async def _on_contact_updated(self, event: dict) -> None:
        logger.info("hubspot_contact_updated", object_id=event.get("objectId"),
                    property_name=event.get("propertyName"))

    async def _on_deal_changed(self, event: dict) -> None:
        logger.info("hubspot_deal_changed", object_id=event.get("objectId"))
