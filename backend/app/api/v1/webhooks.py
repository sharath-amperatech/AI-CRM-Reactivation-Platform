from __future__ import annotations

from typing import Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request, status

from app.core.logging import get_logger

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = get_logger(__name__)


@router.post("/hubspot")
async def hubspot_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_hubspot_signature: str | None = Header(None),
):
    payload = await request.json()
    events = payload if isinstance(payload, list) else [payload]
    logger.info("hubspot_webhook_received", event_count=len(events))

    # Signature verification placeholder — implement HMAC check
    from app.integrations.hubspot.webhooks import HubSpotWebhookHandler
    handler = HubSpotWebhookHandler()
    background_tasks.add_task(handler.handle, events)
    return {"received": len(events)}


@router.post("/twilio")
async def twilio_webhook(request: Request, background_tasks: BackgroundTasks):
    """Inbound SMS reply from Twilio."""
    form_data = dict(await request.form())
    logger.info("twilio_webhook_received", from_number=form_data.get("From"))

    from app.integrations.twilio.client import get_twilio_client
    client = get_twilio_client()
    parsed = client.parse_inbound_webhook(form_data)

    # TODO: Match to Message by from_number, create Reply record, trigger workflow resume
    logger.info("twilio_reply_parsed", **{k: v for k, v in parsed.items() if k != "body"})
    return {"status": "received"}


@router.post("/resend")
async def resend_webhook(request: Request, background_tasks: BackgroundTasks):
    """Delivery events from Resend (delivered, bounced, complained)."""
    payload = await request.json()
    event_type = payload.get("type", "unknown")
    logger.info("resend_webhook_received", event_type=event_type)

    # TODO: Update message status based on delivery event
    return {"status": "received"}
