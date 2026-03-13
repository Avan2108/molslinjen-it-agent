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

    # Azure OpenAI (preferred — used by the agent code)
    AZURE_OPENAI_ENDPOINT: str = ""
    AZURE_OPENAI_API_KEY: SecretStr = SecretStr("")
    AZURE_OPENAI_API_VERSION: str = "2024-02-01"
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = "gpt-4o-mini"
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = "text-embedding-3-small"

    # OpenAI API (fallback / architect compat)
    OPENAI_API_KEY: SecretStr = SecretStr("")
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"

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
