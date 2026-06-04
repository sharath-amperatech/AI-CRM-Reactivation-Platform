from __future__ import annotations

from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential
from twilio.rest import Client as TwilioRestClient

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TwilioClient:
    def __init__(self, account_sid: str, auth_token: str, from_number: str) -> None:
        self._client = TwilioRestClient(account_sid, auth_token)
        self._from_number = from_number

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def send_sms(self, to: str, body: str) -> dict[str, Any]:
        import anyio

        def _send():
            return self._client.messages.create(
                body=body, from_=self._from_number, to=to
            )

        message = await anyio.to_thread.run_sync(_send)
        logger.info("sms_sent", to=to, sid=message.sid, status=message.status)
        return {"sid": message.sid, "status": message.status}

    def parse_inbound_webhook(self, form_data: dict[str, str]) -> dict[str, Any]:
        return {
            "message_sid": form_data.get("MessageSid"),
            "from_number": form_data.get("From"),
            "to_number": form_data.get("To"),
            "body": form_data.get("Body", ""),
            "num_media": int(form_data.get("NumMedia", 0)),
        }


def get_twilio_client() -> TwilioClient:
    settings = get_settings()
    return TwilioClient(
        account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN.get_secret_value(),
        from_number=settings.TWILIO_FROM_NUMBER,
    )
