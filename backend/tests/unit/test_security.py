from __future__ import annotations

import pytest

from app.core.security import generate_api_key, verify_api_key


def test_api_key_generation():
    key, key_hash = generate_api_key()
    assert key.startswith("riq_live_sk_")
    assert len(key_hash) == 64  # SHA-256 hex


def test_api_key_verification_correct():
    key, key_hash = generate_api_key()
    assert verify_api_key(key, key_hash) is True


def test_api_key_verification_wrong():
    _, key_hash = generate_api_key()
    wrong_key, _ = generate_api_key()
    assert verify_api_key(wrong_key, key_hash) is False


def test_api_key_verification_tampered_hash():
    key, _ = generate_api_key()
    fake_hash = "0" * 64
    assert verify_api_key(key, fake_hash) is False
