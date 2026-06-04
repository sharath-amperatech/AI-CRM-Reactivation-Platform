from __future__ import annotations

from app.core.logging import get_logger
from app.integrations.resend.client import get_resend_client

logger = get_logger(__name__)


class ResendService:
    async def send_email(
        self,
        to: str,
        subject: str,
        html: str,
        metadata: dict | None = None,
    ) -> str:
        client = get_resend_client()
        try:
            result = await client.send_email(to=to, subject=subject, html=html, metadata=metadata)
            return result.get("id", "")
        finally:
            await client.close()

    def text_to_html(self, text: str) -> str:
        import html as html_lib
        escaped = html_lib.escape(text)
        lines = escaped.replace("\n\n", "</p><p>").replace("\n", "<br>")
        return f"<p>{lines}</p>"
