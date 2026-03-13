"""
Pytest configuration and fixtures for all test phases.

Usage:
    pytest tests/ -v                          # Run all tests
    pytest tests/ -v -m phase1                # Run only Phase 1 tests
    pytest tests/ -v -m "not slow"            # Skip slow tests
    pytest tests/ -v -m "not integration"     # Skip integration tests
"""

import pytest
import os
import sys

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "phase1: Phase 1 Infrastructure tests")
    config.addinivalue_line("markers", "phase2: Phase 2 Authentication tests")
    config.addinivalue_line("markers", "phase3: Phase 3 Agent tests")
    config.addinivalue_line("markers", "phase4: Phase 4 Plugin tests")
    config.addinivalue_line("markers", "phase5: Phase 5 Frontend API tests")
    config.addinivalue_line("markers", "phase6: Phase 6 Integration tests")
    config.addinivalue_line("markers", "slow: Tests that make external API calls")
    config.addinivalue_line("markers", "integration: Tests requiring external services")


@pytest.fixture
def test_settings():
    """Fixture providing test settings."""
    from app.config import Settings

    return Settings(
        OPENAI_API_KEY="test-key",
        OPENAI_MODEL="gpt-5",
        AZURE_SEARCH_ENDPOINT="https://test.search.windows.net",
        AZURE_SEARCH_KEY="test-key",
        AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=test",
        AZURE_STORAGE_ACCOUNT_NAME="test",
        AZURE_AD_TENANT_ID="test-tenant",
        AZURE_AD_CLIENT_ID="test-client",
    )


@pytest.fixture
def mock_openai_client():
    """Fixture providing mocked OpenAI client."""
    from unittest.mock import AsyncMock, MagicMock

    client = MagicMock()

    # Mock chat completion
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.content = "Test response"
    client.chat.completions.create = AsyncMock(return_value=mock_completion)

    # Mock embeddings
    mock_embedding = MagicMock()
    mock_embedding.data = [MagicMock()]
    mock_embedding.data[0].embedding = [0.1] * 1536
    client.embeddings.create = AsyncMock(return_value=mock_embedding)

    return client


@pytest.fixture
def auth_headers():
    """Fixture providing development auth headers."""
    return {"Authorization": "Bearer dev-token"}


@pytest.fixture
def admin_headers():
    """Fixture providing admin auth headers.

    Note: This requires a real admin token for integration tests.
    For unit tests, mock the auth middleware instead.
    """
    # In real tests, this would be a valid admin token
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture
def sample_chat_request():
    """Fixture providing sample chat request."""
    return {
        "message": "How do I reset my password?",
        "locale": "en",
    }


@pytest.fixture
def sample_ticket_request():
    """Fixture providing sample ticket creation request."""
    return {
        "subject": "Test Ticket",
        "description": "This is a test ticket",
        "priority": 3,
    }


@pytest.fixture
def sample_feedback_request():
    """Fixture providing sample feedback request."""
    return {
        "session_id": "test-session-id",
        "message_index": 1,
        "rating": "up",
    }


# ============================================================================
# Test Utilities
# ============================================================================

def assert_valid_uuid(value: str):
    """Assert value is a valid UUID format."""
    import uuid
    try:
        uuid.UUID(value)
    except ValueError:
        pytest.fail(f"Invalid UUID format: {value}")


def assert_iso_datetime(value: str):
    """Assert value is valid ISO datetime format."""
    from datetime import datetime
    try:
        datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        pytest.fail(f"Invalid ISO datetime format: {value}")
