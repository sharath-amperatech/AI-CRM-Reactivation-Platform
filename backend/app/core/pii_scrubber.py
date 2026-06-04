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


def scrub_prompt(text: str, lead: dict) -> tuple[str, dict[str, str]]:
    """Mask known lead PII values and regex-detected emails/phones in a prompt string.

    Uses exact literal replacement on known lead fields (more precise than NLP),
    then sweeps for any remaining email/phone patterns in activity content.
    Returns (anonymized_text, mapping) where mapping is placeholder→original,
    suitable for passing to restore_prompt() to de-anonymize LLM output.
    """
    mapping: dict[str, str] = {}

    # Exact-match known PII fields; sort longest-first to avoid partial replacements
    known = [
        (lead.get("name") or "", "<PERSON>"),
        (lead.get("email") or "", "<EMAIL>"),
        (lead.get("phone") or "", "<PHONE>"),
    ]
    for original, placeholder in sorted(known, key=lambda x: len(x[0]), reverse=True):
        if original and original in text:
            mapping[placeholder] = original
            text = text.replace(original, placeholder)

    # Sweep for any remaining emails/phones in activity content
    text = _EMAIL_RE.sub("[redacted-email]", text)
    text = _PHONE_RE.sub("[redacted-phone]", text)

    return text, mapping


def restore_prompt(text: str, mapping: dict[str, str]) -> str:
    """Restore placeholders in LLM output back to their original PII values."""
    for placeholder, original in mapping.items():
        text = text.replace(placeholder, original)
    return text
