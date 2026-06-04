from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import PostgresDsn, RedisDsn, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent.parent  # → backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── App ───────────────────────────────────────────────────
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    # ── Database ──────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/CRM_Reactivation"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 5
    DATABASE_POOL_TIMEOUT: int = 30
    DATABASE_POOL_RECYCLE: int = 1800

    # ── Redis / Celery ────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # ── AI Providers ──────────────────────────────────────────
    OPENAI_API_KEY: SecretStr = SecretStr("")
    ANTHROPIC_API_KEY: SecretStr = SecretStr("")
    COHERE_API_KEY: SecretStr = SecretStr("")
    LITELLM_PROXY_URL: str | None = None

    # ── Azure OpenAI ──────────────────────────────────────────
    AZURE_OPENAI_API_KEY: SecretStr = SecretStr("")
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_DEPLOYMENT_GPT41_MINI: str = "gpt-4.1-mini"
    AZURE_DEPLOYMENT_GPT5_NANO: str = "gpt-5-nano"
    AZURE_DEPLOYMENT_EMBEDDINGS: str = "text-embedding-3-small"

    # Dedicated embedding resource
    AZURE_OPENAI_TEXT_EMBEDDING_ENDPOINT: str = ""
    AZURE_OPENAI_TEXT_EMBEDDING_MODEL_NAME: str = "text-embedding-3-small"
    AZURE_OPENAI_TEXT_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"
    AZURE_OPENAI_TEXT_EMBEDDING_API_KEY: SecretStr = SecretStr("")

    # ── Langfuse ──────────────────────────────────────────────
    LANGFUSE_PUBLIC_KEY: str = ""
    LANGFUSE_SECRET_KEY: SecretStr = SecretStr("")
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # ── Auth — Clerk ──────────────────────────────────────────
    CLERK_PUBLISHABLE_KEY: str = ""
    CLERK_SECRET_KEY: SecretStr = SecretStr("")
    CLERK_JWKS_URL: str = ""

    # Internal API key config
    API_KEY_PREFIX: str = "riq_live_sk_"

    # ── Integrations ──────────────────────────────────────────
    RESEND_API_KEY: SecretStr = SecretStr("")
    RESEND_FROM_EMAIL: str = "noreply@reactiviq.ai"

    TWILIO_ACCOUNT_SID: str = ""
    TWILIO_AUTH_TOKEN: SecretStr = SecretStr("")
    TWILIO_FROM_NUMBER: str = ""

    HUBSPOT_API_KEY: SecretStr = SecretStr("")
    HUBSPOT_PORTAL_ID: str = ""

    CALENDLY_API_KEY: SecretStr = SecretStr("")

    # ── RAG / Embedding ───────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536
    RETRIEVAL_TOP_K: int = 20
    RERANK_TOP_N: int = 5
    SIMILARITY_THRESHOLD: float = 0.5

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
