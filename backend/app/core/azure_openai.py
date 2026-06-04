from openai import AsyncAzureOpenAI

from app.core.config import get_settings

_settings = get_settings()

azure_client = AsyncAzureOpenAI(
    api_key=_settings.AZURE_OPENAI_API_KEY.get_secret_value(),
    azure_endpoint=_settings.AZURE_OPENAI_ENDPOINT,
    api_version=_settings.AZURE_OPENAI_API_VERSION,
)
