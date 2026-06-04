from __future__ import annotations

import re

_EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", re.IGNORECASE)
_PHONE_RE = re.compile(r"\+?[\d][\d\s\-().]{6,14}[\d]")

_PII_KEYS = frozenset({
    "email",
    "phone",
    "mobile",
    "cell",
    "contact_email",
    "owner_email",
    "phone_number",
    "mobile_number",
    "personal_email",
    "email_address",
    "phone_work",
    "phone_mobile",
})


def scrub_metadata(meta: dict) -> dict:
    """Return a copy of meta with PII keys dropped and PII patterns redacted from string values.

    Called before storing raw CRM payload in crm_activity.metadata so that
    embeddings are never stored alongside raw PII.
    """
    result: dict = {}
    for k, v in meta.items():
        if k.lower() in _PII_KEYS:
            continue
        if isinstance(v, str):
            v = _EMAIL_RE.sub("[redacted-email]", v)
            v = _PHONE_RE.sub("[redacted-phone]", v)
        result[k] = v
    return result
