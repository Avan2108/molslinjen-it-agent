"""Environment configuration using pydantic-settings."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # OpenAI API
    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-5"  # Used for chat, triage, and prefilter
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"  # Override for Azure or other providers

    # Azure AI Search
    AZURE_SEARCH_ENDPOINT: str = ""
    AZURE_SEARCH_KEY: SecretStr = SecretStr("")
    AZURE_SEARCH_INDEX: str = "it-knowledge"

    # Azure Table Storage
    AZURE_STORAGE_CONNECTION_STRING: SecretStr = SecretStr("")
    AZURE_STORAGE_ACCOUNT_NAME: str = ""

    # FreshService
    FRESHSERVICE_DOMAIN: str = ""
    FRESHSERVICE_API_KEY: SecretStr = SecretStr("")
    FRESHSERVICE_DEFAULT_GROUP_ID: int = 0

    # Azure AD
    AZURE_AD_TENANT_ID: str = ""
    AZURE_AD_CLIENT_ID: str = ""

    # Microsoft Graph
    GRAPH_CLIENT_ID: str = ""
    GRAPH_CLIENT_SECRET: SecretStr = SecretStr("")
    GRAPH_TENANT_ID: str = ""

    # App Config
    CONFIDENCE_THRESHOLD_HIGH: float = 0.80
    CONFIDENCE_THRESHOLD_LOW: float = 0.40
    MAX_CONVERSATION_TURNS: int = 10
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
