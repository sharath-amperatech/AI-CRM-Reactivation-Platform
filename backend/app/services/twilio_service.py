from __future__ import annotations

from app.core.logging import get_logger
from app.integrations.twilio.client import get_twilio_client

logger = get_logger(__name__)


class TwilioService:
    async def send_sms(self, to: str, body: str) -> str:
        client = get_twilio_client()
        result = await client.send_sms(to=to, body=body)
        return result.get("sid", "")
