# Phase 6: Full Route Implementation & Integration

## Overview
Complete all backend route implementations, integrate all components, and ensure end-to-end functionality.

## Prerequisites
- All previous phases completed
- All components implemented
- All plugins working

---

## Tasks

### 6.1 Complete Chat Router Implementation

**Assignee:** Backend Developer
**Estimated effort:** 8 hours

#### Modify `backend/app/routers/chat.py`:

Complete implementation including:

```python
@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user: UserClaims = Depends(get_current_user),
):
    """Full implementation:
    1. Pre-filter safety check
    2. Get or create session
    3. Triage intent classification
    4. Route to appropriate handler
    5. Generate response with RAG
    6. Save to session
    7. Track analytics
    """
    pass

@router.get("/sessions")
async def list_sessions(user: UserClaims = Depends(get_current_user)):
    """Get user's recent chat sessions."""
    sessions_table = ChatSessionsTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    sessions = sessions_table.get_user_sessions(user.oid)
    return [
        {
            "session_id": s.session_id,
            "created_at": s.created_at,
            "updated_at": s.updated_at,
            "preview": get_session_preview(s),
        }
        for s in sessions
    ]

@router.get("/sessions/{session_id}")
async def get_session(session_id: str, user: UserClaims = Depends(get_current_user)):
    """Get full session with messages."""
    sessions_table = ChatSessionsTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    session = sessions_table.get_session(user.oid, session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = json.loads(session.messages_json)
    return {
        "session_id": session.session_id,
        "created_at": session.created_at,
        "messages": messages,
        "locale": session.locale,
    }

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: UserClaims = Depends(get_current_user)):
    """Delete a chat session."""
    sessions_table = ChatSessionsTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    deleted = sessions_table.delete(user.oid, session_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"success": True}
```

#### Acceptance Criteria:
- [ ] Full chat flow working end-to-end
- [ ] Session persistence working
- [ ] Session listing and retrieval working
- [ ] Session deletion working
- [ ] Conversation context maintained
- [ ] Error handling for all edge cases

---

### 6.2 Complete Feedback Router Implementation

**Assignee:** Backend Developer
**Estimated effort:** 3 hours

#### Modify `backend/app/routers/feedback.py`:

```python
@router.post("", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    user: UserClaims = Depends(get_current_user),
):
    """Submit feedback for a message."""
    # Validate session exists and belongs to user
    sessions_table = ChatSessionsTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    session = sessions_table.get_session(user.oid, request.session_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Get the message being rated
    messages = json.loads(session.messages_json)
    if request.message_index >= len(messages):
        raise HTTPException(status_code=400, detail="Invalid message index")

    message = messages[request.message_index]

    # Save feedback
    feedback_table = FeedbackTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    feedback = feedback_table.add_feedback(
        session_id=request.session_id,
        message_index=request.message_index,
        user_oid=user.oid,
        rating=request.rating,
        query=messages[request.message_index - 1]["content"] if request.message_index > 0 else "",
        response=message["content"],
        intent=message.get("metadata", {}).get("intent", Intent.UNCLEAR),
        reason=request.reason,
        comment=request.comment,
    )

    # If negative feedback, potentially log as knowledge gap
    if request.rating == FeedbackRating.DOWN:
        await log_potential_gap(session, message, request)

    return FeedbackResponse(success=True, feedback_id=feedback.feedback_id)

@router.get("/stats")
async def get_feedback_stats(
    user: UserClaims = Depends(require_admin),
    days: int = 30,
):
    """Get feedback statistics for admin dashboard."""
    # Query feedback table for stats
    # Calculate:
    # - Total feedback count
    # - Positive/negative ratio
    # - Common negative reasons
    # - Trend over time
    pass
```

#### Acceptance Criteria:
- [ ] Feedback saved to Table Storage
- [ ] Session/message validation
- [ ] Negative feedback triggers gap logging
- [ ] Stats endpoint for admin dashboard

---

### 6.3 Complete FAQ Router Implementation

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Modify `backend/app/routers/faqs.py`:

```python
# Use Azure AI Search or Table Storage for FAQs

@router.get("", response_model=list[FAQ])
async def list_faqs(
    locale: Locale = Locale.EN,
    category: str | None = None,
):
    """List active FAQs."""
    # Query FAQs from storage
    # Filter by locale and category
    # Sort by order
    pass

@router.post("", response_model=FAQ)
async def create_faq(
    request: FAQCreateRequest,
    user: UserClaims = Depends(require_admin),
):
    """Create new FAQ (admin only)."""
    # Create FAQ in storage
    # Log admin action
    pass

@router.put("/{faq_id}", response_model=FAQ)
async def update_faq(
    faq_id: str,
    request: FAQUpdateRequest,
    user: UserClaims = Depends(require_admin),
):
    """Update FAQ (admin only)."""
    pass

@router.delete("/{faq_id}")
async def delete_faq(
    faq_id: str,
    user: UserClaims = Depends(require_admin),
):
    """Delete FAQ (admin only)."""
    pass

@router.post("/{faq_id}/helpful")
async def mark_faq_helpful(
    faq_id: str,
    helpful: bool,
    user: UserClaims = Depends(get_current_user),
):
    """Track FAQ helpfulness."""
    faq_events = FAQEventsTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    faq_events.log_event(
        faq_id=faq_id,
        user_oid=user.oid,
        event_type="helpful" if helpful else "not_helpful",
    )
    return {"success": True}
```

---

### 6.4 Complete Admin Router Implementation

**Assignee:** Backend Developer
**Estimated effort:** 6 hours

#### Modify `backend/app/routers/admin.py`:

```python
@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    user: UserClaims = Depends(require_admin),
):
    """Get analytics dashboard data."""
    # Default to last 30 days
    if not end_date:
        end_date = datetime.utcnow()
    if not start_date:
        start_date = end_date - timedelta(days=30)

    # Query sessions table for metrics
    # Calculate:
    # - Total conversations
    # - Unique users
    # - Messages per session
    # - Resolution rate (sessions without escalation)
    # - Escalation rate
    # - Intent breakdown
    # - Top queries

    return AnalyticsResponse(
        period_start=start_date,
        period_end=end_date,
        total_conversations=...,
        # ... other metrics
    )

@router.get("/gaps", response_model=list[GapEntry])
async def list_knowledge_gaps(
    resolved: bool = False,
    limit: int = 50,
    user: UserClaims = Depends(require_admin),
):
    """List identified knowledge gaps."""
    # Query gaps from storage
    # Sort by occurrences (most frequent first)
    pass

@router.post("/gaps/{gap_id}/resolve")
async def resolve_gap(
    gap_id: str,
    user: UserClaims = Depends(require_admin),
):
    """Mark knowledge gap as resolved."""
    # Update gap status
    # Log admin action
    pass

@router.post("/reindex")
async def trigger_reindex(
    user: UserClaims = Depends(require_admin),
):
    """Trigger knowledge base reindexing."""
    # Start async reindex job
    # Return job ID for status tracking
    pass

@router.get("/reindex/status", response_model=ReindexStatus)
async def get_reindex_status(
    user: UserClaims = Depends(require_admin),
):
    """Get current reindex status."""
    # Return status of current/last reindex job
    pass

@router.get("/logs")
async def get_admin_logs(
    action: str | None = None,
    admin_email: str | None = None,
    limit: int = 100,
    user: UserClaims = Depends(require_admin),
):
    """Get admin action logs."""
    admin_log = AdminLogTable(settings.AZURE_STORAGE_CONNECTION_STRING)
    # Query with filters
    pass
```

---

### 6.5 Implement Knowledge Gap Tracking

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Create `backend/app/services/gap_tracker.py`:

```python
"""Track and manage knowledge gaps."""

from app.storage.tables import TableStorageClient
from app.models import GapEntry, Intent

class KnowledgeGapTracker:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def track_gap(
        self,
        query: str,
        intent: Intent,
        session_id: str,
        confidence: float,
    ):
        """Track a potential knowledge gap.

        Called when:
        - Low confidence response
        - User gives negative feedback
        - Agent explicitly says "I don't know"
        """
        # Check if similar gap exists (fuzzy match)
        # If exists, increment occurrences
        # If new, create gap entry
        pass

    async def get_unresolved_gaps(self, limit: int = 50) -> list[GapEntry]:
        """Get unresolved gaps sorted by occurrences."""
        pass

    async def resolve_gap(self, gap_id: str, resolver_email: str):
        """Mark gap as resolved."""
        pass
```

#### Integration points:
- Call `track_gap` when confidence < `CONFIDENCE_THRESHOLD_LOW`
- Call `track_gap` on negative feedback
- Show gaps in admin dashboard

---

### 6.6 End-to-End Integration Testing

**Assignee:** QA / Full Stack Developer
**Estimated effort:** 8 hours

#### Create `backend/tests/test_e2e.py`:

```python
"""End-to-end integration tests."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestChatFlow:
    def test_full_conversation_flow(self, auth_token):
        """Test complete chat conversation."""
        # 1. Start new conversation
        response = client.post(
            "/api/v1/chat",
            json={"message": "How do I reset my password?"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        session_id = data["session_id"]
        assert "password" in data["message"].lower()

        # 2. Follow-up question
        response = client.post(
            "/api/v1/chat",
            json={"message": "What if I forgot my username too?", "session_id": session_id},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

        # 3. List sessions
        response = client.get(
            "/api/v1/chat/sessions",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        sessions = response.json()
        assert any(s["session_id"] == session_id for s in sessions)

        # 4. Submit feedback
        response = client.post(
            "/api/v1/feedback",
            json={"session_id": session_id, "message_index": 1, "rating": "up"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200

class TestTicketFlow:
    def test_ticket_creation_flow(self, auth_token):
        """Test ticket creation through chat."""
        # 1. User describes problem
        response = client.post(
            "/api/v1/chat",
            json={"message": "My laptop screen is broken, I need help"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        # Agent should offer to create ticket

        # 2. User confirms ticket creation
        # ...

        # 3. Verify ticket in list
        # ...

class TestAdminFlow:
    def test_admin_dashboard(self, admin_token):
        """Test admin dashboard data."""
        response = client.get(
            "/api/v1/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "total_conversations" in data
```

#### Create frontend E2E tests with Playwright:

```typescript
// frontend/e2e/chat.spec.ts
import { test, expect } from '@playwright/test';

test('user can have conversation with agent', async ({ page }) => {
  await page.goto('/');

  // Login
  await page.click('text=Sign In');
  // ... handle Microsoft login

  // Send message
  await page.fill('[placeholder="Type your question..."]', 'How do I reset my password?');
  await page.click('text=Send');

  // Wait for response
  await expect(page.locator('.message-bubble').last()).toContainText('password', { timeout: 30000 });

  // Submit feedback
  await page.click('[aria-label="Thumbs up"]');
  await expect(page.locator('text=Thanks for your feedback')).toBeVisible();
});
```

---

### 6.7 Performance Optimization

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Tasks:

1. **Add response streaming** (optional enhancement):
   ```python
   @router.post("/stream")
   async def stream_message(request: ChatRequest):
       async def generate():
           async for chunk in agent.stream_chat(...):
               yield f"data: {json.dumps({'chunk': chunk})}\n\n"
       return StreamingResponse(generate(), media_type="text/event-stream")
   ```

2. **Add caching for knowledge search**:
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   async def cached_search(query: str, top_k: int):
       return await search_client.hybrid_search(query, top_k)
   ```

3. **Optimize database queries**:
   - Add indexes to Table Storage queries
   - Batch operations where possible

4. **Add connection pooling**:
   - Reuse HTTP clients
   - Connection pool for Azure services

---

## Integration Checklist

### Backend
- [ ] All routes returning real data
- [ ] Session persistence working
- [ ] Feedback storage working
- [ ] Admin analytics working
- [ ] Gap tracking working
- [ ] All error cases handled
- [ ] Logging comprehensive

### Frontend
- [ ] All pages functional
- [ ] API integration complete
- [ ] Error handling in UI
- [ ] Loading states working
- [ ] Responsive design verified

### End-to-End
- [ ] Full chat conversation works
- [ ] Ticket creation through chat works
- [ ] Feedback submission works
- [ ] Admin dashboard shows data
- [ ] Authentication/authorization enforced

---

## Definition of Done

- [ ] All routes fully implemented
- [ ] E2E tests passing
- [ ] Performance acceptable (<3s response)
- [ ] No console errors
- [ ] Error tracking configured
- [ ] Documentation complete
- [ ] Code review completed
- [ ] UAT sign-off
