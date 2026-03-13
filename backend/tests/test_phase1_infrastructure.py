"""
Phase 1: Infrastructure Tests
Run these tests to verify infrastructure setup is complete.

Usage:
    pytest tests/test_phase1_infrastructure.py -v
    pytest tests/test_phase1_infrastructure.py -v -m "not slow"  # Skip slow tests
"""

import os
import pytest
from unittest.mock import patch, MagicMock

# Mark all tests in this module
pytestmark = pytest.mark.phase1


class TestEnvironmentConfiguration:
    """Test 1.1: Verify environment variables are configured."""

    def test_openai_api_key_set(self):
        """Verify OPENAI_API_KEY is configured."""
        from app.config import get_settings
        settings = get_settings()
        api_key = settings.OPENAI_API_KEY.get_secret_value()
        assert api_key, "OPENAI_API_KEY must be set"
        assert api_key != "sk-your-openai-api-key", "OPENAI_API_KEY must be replaced with actual key"

    def test_openai_model_configured(self):
        """Verify OpenAI model is set to gpt-5."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.OPENAI_MODEL == "gpt-5", f"Expected gpt-5, got {settings.OPENAI_MODEL}"

    def test_azure_search_endpoint_set(self):
        """Verify Azure Search endpoint is configured."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.AZURE_SEARCH_ENDPOINT, "AZURE_SEARCH_ENDPOINT must be set"
        assert "search.windows.net" in settings.AZURE_SEARCH_ENDPOINT

    def test_azure_storage_connection_string_set(self):
        """Verify Azure Storage connection string is configured."""
        from app.config import get_settings
        settings = get_settings()
        conn_str = settings.AZURE_STORAGE_CONNECTION_STRING.get_secret_value()
        assert conn_str, "AZURE_STORAGE_CONNECTION_STRING must be set"
        assert "AccountName=" in conn_str or "DefaultEndpointsProtocol=" in conn_str


class TestOpenAIConnectivity:
    """Test 1.2: Verify OpenAI API connectivity."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_openai_chat_completion(self):
        """Test GPT-5 chat completion works."""
        from app.config import get_settings
        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            base_url=settings.OPENAI_BASE_URL,
        )

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": "Respond with only the word 'OK'"}],
            max_tokens=10,
        )

        assert response.choices[0].message.content is not None
        assert len(response.choices[0].message.content) > 0

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_openai_embeddings(self):
        """Test embedding generation works."""
        from app.config import get_settings
        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value(),
            base_url=settings.OPENAI_BASE_URL,
        )

        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input="test embedding text",
        )

        embedding = response.data[0].embedding
        assert len(embedding) == 1536, f"Expected 1536 dimensions, got {len(embedding)}"


class TestAzureSearchConnectivity:
    """Test 1.3: Verify Azure AI Search connectivity."""

    @pytest.mark.slow
    def test_search_index_exists(self):
        """Verify it-knowledge index exists."""
        import httpx
        from app.config import get_settings

        settings = get_settings()
        response = httpx.get(
            f"{settings.AZURE_SEARCH_ENDPOINT}/indexes/{settings.AZURE_SEARCH_INDEX}",
            params={"api-version": "2024-07-01"},
            headers={"api-key": settings.AZURE_SEARCH_KEY.get_secret_value()},
        )

        assert response.status_code == 200, f"Index not found: {response.text}"
        data = response.json()
        assert data["name"] == settings.AZURE_SEARCH_INDEX

    @pytest.mark.slow
    def test_search_index_has_vector_field(self):
        """Verify index has vector search configured."""
        import httpx
        from app.config import get_settings

        settings = get_settings()
        response = httpx.get(
            f"{settings.AZURE_SEARCH_ENDPOINT}/indexes/{settings.AZURE_SEARCH_INDEX}",
            params={"api-version": "2024-07-01"},
            headers={"api-key": settings.AZURE_SEARCH_KEY.get_secret_value()},
        )

        assert response.status_code == 200
        data = response.json()

        # Check for vector field
        field_names = [f["name"] for f in data["fields"]]
        assert "content_vector" in field_names, "Missing content_vector field"

        # Check vector search config
        assert "vectorSearch" in data, "Missing vectorSearch configuration"


class TestAzureStorageConnectivity:
    """Test 1.4: Verify Azure Table Storage connectivity."""

    @pytest.mark.slow
    def test_storage_connection(self):
        """Verify can connect to Azure Table Storage."""
        from azure.data.tables import TableServiceClient
        from app.config import get_settings

        settings = get_settings()
        conn_str = settings.AZURE_STORAGE_CONNECTION_STRING.get_secret_value()

        service = TableServiceClient.from_connection_string(conn_str)
        # This will throw if connection fails
        tables = list(service.list_tables())
        # Tables may or may not exist yet, but connection should work
        assert isinstance(tables, list)

    @pytest.mark.slow
    def test_can_create_table(self):
        """Verify can create tables in storage."""
        from azure.data.tables import TableServiceClient
        from azure.core.exceptions import ResourceExistsError
        from app.config import get_settings

        settings = get_settings()
        conn_str = settings.AZURE_STORAGE_CONNECTION_STRING.get_secret_value()

        service = TableServiceClient.from_connection_string(conn_str)

        test_table_name = "TestPhase1"
        try:
            service.create_table(test_table_name)
        except ResourceExistsError:
            pass  # Table already exists, that's fine

        # Verify table exists
        tables = [t.name for t in service.list_tables()]
        assert test_table_name in tables

        # Cleanup
        service.delete_table(test_table_name)


class TestHealthEndpoint:
    """Test 1.5: Verify backend health endpoint."""

    def test_health_endpoint(self):
        """Verify /health endpoint returns ok."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root_endpoint(self):
        """Verify root endpoint returns API info."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


# ============================================================================
# Test Summary Report
# ============================================================================

def test_phase1_summary():
    """
    Phase 1 Infrastructure Checklist:

    Run this test file to verify all Phase 1 infrastructure is set up correctly.

    Quick test (no API calls):
        pytest tests/test_phase1_infrastructure.py -v -m "not slow"

    Full test (includes API calls):
        pytest tests/test_phase1_infrastructure.py -v

    Expected results:
    - [ ] Environment variables configured
    - [ ] OpenAI API accessible (gpt-5 and embeddings)
    - [ ] Azure AI Search index exists with vector field
    - [ ] Azure Table Storage accessible
    - [ ] Backend health endpoint working
    """
    pass
