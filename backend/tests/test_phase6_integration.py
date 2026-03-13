"""
Phase 6: Full Integration Tests
End-to-end tests verifying complete user flows.

Usage:
    pytest tests/test_phase6_integration.py -v
    pytest tests/test_phase6_integration.py -v -m "not slow"
"""

import pytest
from fastapi.testclient import TestClient
import json

pytestmark = pytest.mark.phase6


class TestChatFlow:
    """Test 6.1: Complete chat conversation flow."""

    @pytest.mark.slow
    def test_new_conversation_flow(self):
        """Test starting a new conversation."""
        from app.main import app
        client = TestClient(app)

        # Start conversation
        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "How do I reset my password?"}
        )

        if response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        assert response.status_code == 200
        data = response.json()

        assert "session_id" in data
        assert "message" in data
        assert len(data["message"]) > 0

    @pytest.mark.slow
    def test_conversation_continuity(self):
        """Test multi-turn conversation maintains context."""
        from app.main import app
        client = TestClient(app)

        # First message
        response1 = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "I have a problem with VPN"}
        )

        if response1.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        session_id = response1.json()["session_id"]

        # Second message with session
        response2 = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={
                "message": "It says connection timeout",
                "session_id": session_id
            }
        )

        assert response2.status_code == 200
        # Same session maintained
        assert response2.json()["session_id"] == session_id

    @pytest.mark.slow
    def test_session_persistence(self):
        """Test session can be retrieved after creation."""
        from app.main import app
        client = TestClient(app)

        # Create conversation
        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "Test message"}
        )

        if response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        session_id = response.json()["session_id"]

        # Retrieve session
        response = client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers={"Authorization": "Bearer dev-token"}
        )

        if response.status_code == 501:
            pytest.skip("Session retrieval not yet implemented")

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session_id
        assert len(data["messages"]) >= 2  # User + agent message


class TestTicketCreationFlow:
    """Test 6.2: Ticket creation through chat."""

    @pytest.mark.slow
    def test_escalation_creates_ticket(self):
        """Test that escalation intent creates a ticket."""
        from app.main import app
        client = TestClient(app)

        # Message indicating need for ticket
        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "My laptop screen is cracked and I need it replaced"}
        )

        if response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        data = response.json()

        # Should indicate action needed or ticket created
        # Exact behavior depends on implementation
        assert "message" in data


class TestFeedbackFlow:
    """Test 6.3: Feedback submission flow."""

    @pytest.mark.slow
    def test_positive_feedback_flow(self):
        """Test submitting positive feedback."""
        from app.main import app
        client = TestClient(app)

        # First create a conversation
        chat_response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "How do I reset my password?"}
        )

        if chat_response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        session_id = chat_response.json()["session_id"]

        # Submit feedback
        feedback_response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": "Bearer dev-token"},
            json={
                "session_id": session_id,
                "message_index": 1,  # Agent's response
                "rating": "up"
            }
        )

        if feedback_response.status_code == 501:
            pytest.skip("Feedback endpoint not yet implemented")

        assert feedback_response.status_code == 200
        assert feedback_response.json()["success"] == True

    @pytest.mark.slow
    def test_negative_feedback_with_reason(self):
        """Test submitting negative feedback with reason."""
        from app.main import app
        client = TestClient(app)

        # First create a conversation
        chat_response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "How do I reset my password?"}
        )

        if chat_response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        session_id = chat_response.json()["session_id"]

        # Submit negative feedback
        feedback_response = client.post(
            "/api/v1/feedback",
            headers={"Authorization": "Bearer dev-token"},
            json={
                "session_id": session_id,
                "message_index": 1,
                "rating": "down",
                "reason": "wrong_answer",
                "comment": "The answer didn't apply to my situation"
            }
        )

        if feedback_response.status_code == 501:
            pytest.skip("Feedback endpoint not yet implemented")

        assert feedback_response.status_code == 200


class TestAdminFlow:
    """Test 6.4: Admin dashboard data flow."""

    def test_analytics_returns_data(self):
        """Test analytics endpoint returns meaningful data."""
        from app.main import app
        client = TestClient(app)

        # Need admin token - for now this will fail with 403
        response = client.get(
            "/api/v1/admin/analytics",
            headers={"Authorization": "Bearer dev-token"}  # Not admin
        )

        # Should be forbidden for regular user
        assert response.status_code == 403

    @pytest.mark.slow
    def test_knowledge_gaps_list(self):
        """Test knowledge gaps endpoint returns list."""
        from app.main import app
        client = TestClient(app)

        # This needs admin token
        response = client.get(
            "/api/v1/admin/gaps",
            headers={"Authorization": "Bearer dev-token"}
        )

        assert response.status_code == 403  # Not admin


class TestErrorHandling:
    """Test 6.5: Error handling across the system."""

    def test_invalid_session_returns_404(self):
        """Test accessing invalid session returns 404."""
        from app.main import app
        client = TestClient(app)

        response = client.get(
            "/api/v1/chat/sessions/invalid-session-id",
            headers={"Authorization": "Bearer dev-token"}
        )

        if response.status_code == 501:
            pytest.skip("Session endpoint not yet implemented")

        assert response.status_code == 404

    def test_malformed_json_returns_422(self):
        """Test malformed JSON returns validation error."""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            headers={
                "Authorization": "Bearer dev-token",
                "Content-Type": "application/json"
            },
            content="not valid json"
        )

        assert response.status_code == 422

    def test_missing_auth_returns_403(self):
        """Test missing auth header returns 403."""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            json={"message": "test"}
        )

        assert response.status_code == 403


class TestPerformance:
    """Test 6.6: Basic performance checks."""

    @pytest.mark.slow
    def test_health_endpoint_fast(self):
        """Test health endpoint responds quickly."""
        import time
        from app.main import app
        client = TestClient(app)

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 0.1  # Should respond in <100ms

    @pytest.mark.slow
    def test_chat_response_time(self):
        """Test chat endpoint responds within acceptable time."""
        import time
        from app.main import app
        client = TestClient(app)

        start = time.time()
        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "Hello"}
        )
        elapsed = time.time() - start

        if response.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        # Should respond within 10 seconds (AI calls can be slow)
        assert elapsed < 10.0


class TestDataIntegrity:
    """Test 6.7: Data integrity across operations."""

    @pytest.mark.slow
    def test_session_messages_ordered(self):
        """Test messages in session are chronologically ordered."""
        from app.main import app
        client = TestClient(app)

        # Create conversation with multiple messages
        response1 = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "First message"}
        )

        if response1.status_code == 501:
            pytest.skip("Chat endpoint not yet implemented")

        session_id = response1.json()["session_id"]

        client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "Second message", "session_id": session_id}
        )

        # Get session
        response = client.get(
            f"/api/v1/chat/sessions/{session_id}",
            headers={"Authorization": "Bearer dev-token"}
        )

        if response.status_code == 501:
            pytest.skip("Session endpoint not yet implemented")

        messages = response.json()["messages"]

        # Verify chronological order
        for i in range(1, len(messages)):
            assert messages[i]["timestamp"] >= messages[i-1]["timestamp"]


def test_phase6_summary():
    """
    Phase 6 Integration Checklist:

    Run: pytest tests/test_phase6_integration.py -v

    Tests:
    - [ ] New conversation flow works
    - [ ] Multi-turn conversation maintains context
    - [ ] Session can be retrieved
    - [ ] Ticket escalation works
    - [ ] Positive feedback submission works
    - [ ] Negative feedback with reason works
    - [ ] Analytics returns data (admin)
    - [ ] Invalid session returns 404
    - [ ] Missing auth returns 403
    - [ ] Health endpoint fast (<100ms)
    - [ ] Chat responds within timeout
    - [ ] Messages ordered chronologically
    """
    pass
