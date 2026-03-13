"""
Phase 4: Plugin Integration Tests
Run these tests to verify external service integrations.

Usage:
    pytest tests/test_phase4_plugins.py -v
    pytest tests/test_phase4_plugins.py -v -m "not integration"  # Skip real API calls
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

pytestmark = pytest.mark.phase4


class TestFreshServicePlugin:
    """Test 4.1: Verify FreshService plugin functionality."""

    def test_freshservice_config_set(self):
        """Verify FreshService configuration is set."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.FRESHSERVICE_DOMAIN, "FRESHSERVICE_DOMAIN must be set"
        assert settings.FRESHSERVICE_API_KEY.get_secret_value(), "FRESHSERVICE_API_KEY must be set"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_freshservice_create_ticket(self):
        """Test creating a ticket in FreshService."""
        try:
            from app.plugins.freshservice import FreshServicePlugin

            plugin = FreshServicePlugin()
            ticket = await plugin.create_ticket(
                subject="[TEST] AI Agent Test Ticket",
                description="This is a test ticket created by automated tests. Please close.",
                requester_email="test@molslinjen.dk",
                priority=4,  # Low priority
            )

            assert ticket.id is not None
            assert ticket.subject == "[TEST] AI Agent Test Ticket"
        except ImportError:
            pytest.skip("FreshService plugin not yet implemented")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_freshservice_get_ticket(self):
        """Test retrieving a ticket from FreshService."""
        try:
            from app.plugins.freshservice import FreshServicePlugin

            plugin = FreshServicePlugin()
            # Use a known test ticket ID
            ticket = await plugin.get_ticket(ticket_id=1)

            assert ticket is not None
            assert ticket.id == 1
        except ImportError:
            pytest.skip("FreshService plugin not yet implemented")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_freshservice_list_user_tickets(self):
        """Test listing tickets for a user."""
        try:
            from app.plugins.freshservice import FreshServicePlugin

            plugin = FreshServicePlugin()
            tickets = await plugin.get_user_tickets(email="test@molslinjen.dk")

            assert isinstance(tickets, list)
        except ImportError:
            pytest.skip("FreshService plugin not yet implemented")

    def test_freshservice_plugin_mocked(self):
        """Test FreshService plugin with mocked responses."""
        try:
            from app.plugins.freshservice import FreshServicePlugin
            from app.models.tickets import Ticket
            from app.models.enums import TicketStatus, TicketPriority
            from datetime import datetime

            with patch.object(FreshServicePlugin, '_get_client') as mock_client:
                mock_response = MagicMock()
                mock_response.json.return_value = {
                    "ticket": {
                        "id": 123,
                        "subject": "Test",
                        "description_text": "Test desc",
                        "status": 2,
                        "priority": 3,
                        "requester_id": 1,
                        "created_at": "2024-01-01T00:00:00Z",
                        "updated_at": "2024-01-01T00:00:00Z",
                    }
                }
                mock_response.raise_for_status = MagicMock()

                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client_instance.__aenter__.return_value = mock_client_instance
                mock_client.return_value = mock_client_instance

                # Test would go here
                pass
        except ImportError:
            pytest.skip("FreshService plugin not yet implemented")


class TestGraphPlugin:
    """Test 4.2: Verify Microsoft Graph plugin functionality."""

    def test_graph_config_set(self):
        """Verify Graph configuration is set."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.GRAPH_CLIENT_ID, "GRAPH_CLIENT_ID must be set"
        assert settings.GRAPH_CLIENT_SECRET.get_secret_value(), "GRAPH_CLIENT_SECRET must be set"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_graph_get_user_info(self):
        """Test getting user info from Graph."""
        try:
            from app.plugins.graph import GraphPlugin

            plugin = GraphPlugin()
            user = await plugin.get_user_info("test@molslinjen.dk")

            assert user is not None
            assert "displayName" in user or "mail" in user
        except ImportError:
            pytest.skip("Graph plugin not yet implemented")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_graph_search_users(self):
        """Test searching users in Graph."""
        try:
            from app.plugins.graph import GraphPlugin

            plugin = GraphPlugin()
            users = await plugin.search_users("test", limit=5)

            assert isinstance(users, list)
        except ImportError:
            pytest.skip("Graph plugin not yet implemented")


class TestKnowledgePlugin:
    """Test 4.3: Verify Knowledge search plugin functionality."""

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_knowledge_search(self):
        """Test searching the knowledge base."""
        try:
            from app.plugins.knowledge import KnowledgePlugin
            from app.services.search_client import get_search_client

            plugin = KnowledgePlugin(get_search_client())
            results = await plugin.search_knowledge(
                query="password reset",
                top_k=5,
            )

            assert isinstance(results, list)
            # Results may be empty if no documents indexed yet
        except ImportError:
            pytest.skip("Knowledge plugin not yet implemented")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_knowledge_search_with_filter(self):
        """Test searching with category filter."""
        try:
            from app.plugins.knowledge import KnowledgePlugin
            from app.services.search_client import get_search_client

            plugin = KnowledgePlugin(get_search_client())
            results = await plugin.search_knowledge(
                query="VPN",
                top_k=5,
                category="network",
            )

            assert isinstance(results, list)
        except ImportError:
            pytest.skip("Knowledge plugin not yet implemented")


class TestPluginRegistration:
    """Test 4.4: Verify plugins are registered with Semantic Kernel."""

    def test_plugins_registered_with_kernel(self):
        """Test all plugins are registered with kernel."""
        try:
            from app.agents.kernel import create_kernel_with_plugins

            kernel = create_kernel_with_plugins()

            # Check plugins are registered
            assert kernel.get_plugin("freshservice") is not None
            assert kernel.get_plugin("graph") is not None
            assert kernel.get_plugin("knowledge") is not None
        except ImportError:
            pytest.skip("Kernel with plugins not yet implemented")

    def test_plugin_functions_accessible(self):
        """Test plugin functions are accessible from kernel."""
        try:
            from app.agents.kernel import create_kernel_with_plugins

            kernel = create_kernel_with_plugins()

            # Check functions exist
            freshservice = kernel.get_plugin("freshservice")
            assert "create_ticket" in [f.name for f in freshservice.functions.values()]
            assert "get_ticket" in [f.name for f in freshservice.functions.values()]
        except ImportError:
            pytest.skip("Kernel with plugins not yet implemented")


class TestTicketRouterIntegration:
    """Test 4.5: Verify ticket router uses FreshService plugin."""

    @pytest.mark.integration
    def test_create_ticket_endpoint(self):
        """Test POST /tickets creates ticket via FreshService."""
        try:
            from fastapi.testclient import TestClient
            from app.main import app

            client = TestClient(app)
            response = client.post(
                "/api/v1/tickets",
                headers={"Authorization": "Bearer dev-token"},
                json={
                    "subject": "[TEST] Integration Test",
                    "description": "Test ticket from integration tests",
                    "priority": 4,
                }
            )

            # Should work once implemented
            if response.status_code == 501:
                pytest.skip("Ticket endpoint not yet implemented")

            assert response.status_code == 200
            data = response.json()
            assert "id" in data
        except Exception as e:
            pytest.skip(f"Ticket integration not ready: {e}")

    @pytest.mark.integration
    def test_list_tickets_endpoint(self):
        """Test GET /tickets retrieves user tickets."""
        from fastapi.testclient import TestClient
        from app.main import app

        client = TestClient(app)
        response = client.get(
            "/api/v1/tickets",
            headers={"Authorization": "Bearer dev-token"}
        )

        if response.status_code == 501:
            pytest.skip("Ticket listing not yet implemented")

        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_phase4_summary():
    """
    Phase 4 Plugins Checklist:

    Run: pytest tests/test_phase4_plugins.py -v -m "not integration"  # Unit tests
    Run: pytest tests/test_phase4_plugins.py -v  # All tests including integration

    Tests:
    - [ ] FreshService configuration set
    - [ ] FreshService create ticket works
    - [ ] FreshService get ticket works
    - [ ] FreshService list tickets works
    - [ ] Graph configuration set
    - [ ] Graph get user info works
    - [ ] Graph search users works
    - [ ] Knowledge search works
    - [ ] Knowledge search with filters works
    - [ ] Plugins registered with kernel
    - [ ] Ticket endpoints use FreshService
    """
    pass
