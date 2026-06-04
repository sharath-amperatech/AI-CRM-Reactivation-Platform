from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
RESEND_API_BASE = "https://api.resend.com"


class ResendClient:
    def __init__(self, api_key: str, from_email: str) -> None:
        self._from_email = from_email
        self._client = httpx.AsyncClient(
            base_url=RESEND_API_BASE,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            timeout=15,
        )

    async def close(self) -> None:
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8))
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        reply_to: str | None = None,
        metadata: dict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "from": self._from_email,
            "to": [to],
            "subject": subject,
            "html": html,
        }
        if reply_to:
            payload["reply_to"] = reply_to
        if metadata:
            payload["tags"] = [{"name": k, "value": str(v)} for k, v in metadata.items()]

        resp = await self._client.post("/emails", json=payload)
        resp.raise_for_status()
        result = resp.json()
        logger.info("email_sent", to=to, message_id=result.get("id"))
        return result

    async def get_email(self, email_id: str) -> dict[str, Any]:
        resp = await self._client.get(f"/emails/{email_id}")
        resp.raise_for_status()
        return resp.json()


def get_resend_client() -> ResendClient:
    settings = get_settings()
    return ResendClient(
        api_key=settings.RESEND_API_KEY.get_secret_value(),
        from_email=settings.RESEND_FROM_EMAIL,
    )
