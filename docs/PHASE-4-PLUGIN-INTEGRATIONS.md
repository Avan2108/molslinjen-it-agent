# Phase 4: Plugin Integrations

## Overview
Implement Semantic Kernel plugins for external service integrations: FreshService (ticketing), Microsoft Graph (user info), and Azure AI Search (knowledge base).

## Prerequisites
- Phase 3 completed (Agents working)
- FreshService API access
- Microsoft Graph app registration
- Azure AI Search index populated

---

## Tasks

### 4.1 Implement FreshService Plugin

**Assignee:** Backend Developer
**Estimated effort:** 8 hours

#### Purpose:
Enable the AI agent to create, read, and update support tickets in FreshService.

#### Files to Create:

1. **Create `backend/app/plugins/freshservice.py`:**
   ```python
   """FreshService plugin for Semantic Kernel."""

   import httpx
   from typing import Annotated
   from semantic_kernel.functions import kernel_function
   from app.config import get_settings
   from app.models import Ticket, TicketNote, TicketPriority, TicketStatus, TicketSource

   class FreshServicePlugin:
       """Plugin for FreshService ticket operations."""

       def __init__(self):
           settings = get_settings()
           self.base_url = f"https://{settings.FRESHSERVICE_DOMAIN}/api/v2"
           self.api_key = settings.FRESHSERVICE_API_KEY.get_secret_value()
           self.default_group_id = settings.FRESHSERVICE_DEFAULT_GROUP_ID

       def _get_client(self) -> httpx.AsyncClient:
           return httpx.AsyncClient(
               base_url=self.base_url,
               auth=(self.api_key, "X"),  # FreshService uses API key as username
               headers={"Content-Type": "application/json"},
           )

       @kernel_function(
           name="create_ticket",
           description="Create a new support ticket in FreshService"
       )
       async def create_ticket(
           self,
           subject: Annotated[str, "Ticket subject/title"],
           description: Annotated[str, "Detailed description of the issue"],
           requester_email: Annotated[str, "Email of the person reporting"],
           priority: Annotated[int, "Priority: 1=Urgent, 2=High, 3=Medium, 4=Low"] = 3,
           session_id: Annotated[str, "Chat session ID for context"] = None,
       ) -> Ticket:
           """Create a support ticket."""
           async with self._get_client() as client:
               payload = {
                   "subject": subject,
                   "description": description,
                   "email": requester_email,
                   "priority": priority,
                   "status": 2,  # Open
                   "source": TicketSource.AI_CHATBOT.value,
                   "group_id": self.default_group_id,
                   "custom_fields": {
                       "cf_ai_session_id": session_id,
                   },
               }

               response = await client.post("/tickets", json={"ticket": payload})
               response.raise_for_status()

               data = response.json()["ticket"]
               return self._map_ticket(data)

       @kernel_function(
           name="get_ticket",
           description="Get ticket details by ID"
       )
       async def get_ticket(
           self,
           ticket_id: Annotated[int, "The ticket ID number"],
       ) -> Ticket:
           """Get ticket by ID."""
           async with self._get_client() as client:
               response = await client.get(f"/tickets/{ticket_id}")
               response.raise_for_status()

               data = response.json()["ticket"]
               return self._map_ticket(data)

       @kernel_function(
           name="get_user_tickets",
           description="Get all tickets for a user by email"
       )
       async def get_user_tickets(
           self,
           email: Annotated[str, "User's email address"],
           status: Annotated[str, "Filter by status: open, in_progress, resolved, closed"] = None,
       ) -> list[Ticket]:
           """Get user's tickets."""
           async with self._get_client() as client:
               query = f'requester.email:"{email}"'
               if status:
                   status_map = {"open": 2, "in_progress": 3, "resolved": 4, "closed": 5}
                   query += f' AND status:{status_map.get(status, 2)}'

               response = await client.get("/tickets", params={"query": query})
               response.raise_for_status()

               tickets = response.json().get("tickets", [])
               return [self._map_ticket(t) for t in tickets]

       @kernel_function(
           name="add_ticket_note",
           description="Add a note/comment to a ticket"
       )
       async def add_ticket_note(
           self,
           ticket_id: Annotated[int, "The ticket ID"],
           body: Annotated[str, "Note content"],
           private: Annotated[bool, "Whether the note is private (internal only)"] = False,
       ) -> TicketNote:
           """Add note to ticket."""
           async with self._get_client() as client:
               payload = {
                   "body": body,
                   "private": private,
               }

               response = await client.post(
                   f"/tickets/{ticket_id}/notes",
                   json={"note": payload}
               )
               response.raise_for_status()

               data = response.json()["note"]
               return self._map_note(data)

       def _map_ticket(self, data: dict) -> Ticket:
           """Map FreshService response to Ticket model."""
           status_map = {2: "open", 3: "in_progress", 4: "resolved", 5: "closed"}
           return Ticket(
               id=data["id"],
               subject=data["subject"],
               description=data.get("description_text", ""),
               status=TicketStatus(status_map.get(data["status"], "open")),
               priority=TicketPriority(data.get("priority", 3)),
               requester_id=data["requester_id"],
               requester_email=data.get("requester", {}).get("email"),
               created_at=data["created_at"],
               updated_at=data["updated_at"],
               resolved_at=data.get("resolved_at"),
               closed_at=data.get("closed_at"),
           )

       def _map_note(self, data: dict) -> TicketNote:
           """Map FreshService note to TicketNote model."""
           return TicketNote(
               id=data["id"],
               body=data["body_text"],
               created_at=data["created_at"],
               user_id=data["user_id"],
               is_private=data.get("private", False),
           )
   ```

2. **Create `backend/tests/test_freshservice_plugin.py`:**
   ```python
   import pytest
   from unittest.mock import AsyncMock, patch
   from app.plugins.freshservice import FreshServicePlugin

   @pytest.fixture
   def plugin():
       return FreshServicePlugin()

   @pytest.mark.asyncio
   async def test_create_ticket(plugin):
       with patch.object(plugin, '_get_client') as mock_client:
           # Setup mock response
           mock_response = AsyncMock()
           mock_response.json.return_value = {"ticket": {"id": 123, ...}}
           mock_client.return_value.__aenter__.return_value.post.return_value = mock_response

           ticket = await plugin.create_ticket(
               subject="Test ticket",
               description="Test description",
               requester_email="test@molslinjen.dk",
           )

           assert ticket.id == 123
   ```

#### FreshService API Reference:
- Base URL: `https://{domain}.freshservice.com/api/v2`
- Auth: Basic auth with API key as username, "X" as password
- Docs: https://api.freshservice.com/v2/

#### Acceptance Criteria:
- [ ] Create ticket with all required fields
- [ ] Get ticket by ID
- [ ] List user's tickets with filtering
- [ ] Add notes to tickets
- [ ] Map AI session ID to ticket custom field
- [ ] Handle API errors gracefully
- [ ] Rate limiting handling

#### Testing:
```bash
# Integration test with real FreshService (staging environment)
cd backend
FRESHSERVICE_DOMAIN=molslinjen-staging.freshservice.com \
FRESHSERVICE_API_KEY=test-key \
pytest tests/test_freshservice_plugin.py -v -m integration
```

---

### 4.2 Implement Microsoft Graph Plugin

**Assignee:** Backend Developer
**Estimated effort:** 6 hours

#### Purpose:
Enable the AI agent to look up user information, check calendar availability, and access org data.

#### Files to Create:

1. **Create `backend/app/plugins/graph.py`:**
   ```python
   """Microsoft Graph plugin for Semantic Kernel."""

   import httpx
   from msal import ConfidentialClientApplication
   from typing import Annotated
   from semantic_kernel.functions import kernel_function
   from app.config import get_settings

   class GraphPlugin:
       """Plugin for Microsoft Graph operations."""

       def __init__(self):
           settings = get_settings()
           self.client_id = settings.GRAPH_CLIENT_ID
           self.client_secret = settings.GRAPH_CLIENT_SECRET.get_secret_value()
           self.tenant_id = settings.GRAPH_TENANT_ID
           self._token_cache = {}

       async def _get_token(self) -> str:
           """Get access token using client credentials flow."""
           app = ConfidentialClientApplication(
               self.client_id,
               authority=f"https://login.microsoftonline.com/{self.tenant_id}",
               client_credential=self.client_secret,
           )

           result = app.acquire_token_for_client(
               scopes=["https://graph.microsoft.com/.default"]
           )

           if "access_token" in result:
               return result["access_token"]
           raise Exception(f"Failed to get token: {result.get('error_description')}")

       async def _get_client(self) -> httpx.AsyncClient:
           token = await self._get_token()
           return httpx.AsyncClient(
               base_url="https://graph.microsoft.com/v1.0",
               headers={"Authorization": f"Bearer {token}"},
           )

       @kernel_function(
           name="get_user_info",
           description="Get user information by email or user ID"
       )
       async def get_user_info(
           self,
           user_id: Annotated[str, "User email or Azure AD object ID"],
       ) -> dict:
           """Get user profile information."""
           async with await self._get_client() as client:
               response = await client.get(
                   f"/users/{user_id}",
                   params={"$select": "id,displayName,mail,department,jobTitle,officeLocation,mobilePhone"}
               )
               response.raise_for_status()
               return response.json()

       @kernel_function(
           name="get_user_manager",
           description="Get the manager of a user"
       )
       async def get_user_manager(
           self,
           user_id: Annotated[str, "User email or Azure AD object ID"],
       ) -> dict | None:
           """Get user's manager."""
           async with await self._get_client() as client:
               try:
                   response = await client.get(f"/users/{user_id}/manager")
                   response.raise_for_status()
                   return response.json()
               except httpx.HTTPStatusError as e:
                   if e.response.status_code == 404:
                       return None
                   raise

       @kernel_function(
           name="check_calendar_availability",
           description="Check if a user has availability in a time range"
       )
       async def check_calendar_availability(
           self,
           user_id: Annotated[str, "User email"],
           start_time: Annotated[str, "Start time in ISO format"],
           end_time: Annotated[str, "End time in ISO format"],
       ) -> dict:
           """Check calendar free/busy status."""
           async with await self._get_client() as client:
               payload = {
                   "schedules": [user_id],
                   "startTime": {"dateTime": start_time, "timeZone": "Europe/Copenhagen"},
                   "endTime": {"dateTime": end_time, "timeZone": "Europe/Copenhagen"},
                   "availabilityViewInterval": 30,
               }

               response = await client.post("/me/calendar/getSchedule", json=payload)
               response.raise_for_status()
               return response.json()

       @kernel_function(
           name="search_users",
           description="Search for users by name or email"
       )
       async def search_users(
           self,
           query: Annotated[str, "Search query (name or email)"],
           limit: Annotated[int, "Maximum results to return"] = 10,
       ) -> list[dict]:
           """Search for users."""
           async with await self._get_client() as client:
               response = await client.get(
                   "/users",
                   params={
                       "$filter": f"startswith(displayName,'{query}') or startswith(mail,'{query}')",
                       "$top": limit,
                       "$select": "id,displayName,mail,department",
                   }
               )
               response.raise_for_status()
               return response.json().get("value", [])
   ```

2. **Configure Graph permissions:**
   - User.Read.All
   - Calendars.Read
   - Directory.Read.All

#### Acceptance Criteria:
- [ ] Get user info by email/ID
- [ ] Get user's manager
- [ ] Check calendar availability
- [ ] Search users
- [ ] Token caching and refresh
- [ ] Handle missing permissions gracefully

---

### 4.3 Implement Knowledge Search Plugin

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Purpose:
Wrap Azure AI Search for the Semantic Kernel to use in RAG operations.

#### Files to Create:

1. **Create `backend/app/plugins/knowledge.py`:**
   ```python
   """Knowledge base search plugin for Semantic Kernel."""

   from typing import Annotated
   from semantic_kernel.functions import kernel_function
   from app.services.search_client import SearchClient
   from app.models import Source

   class KnowledgePlugin:
       """Plugin for knowledge base search."""

       def __init__(self, search_client: SearchClient):
           self.search_client = search_client

       @kernel_function(
           name="search_knowledge",
           description="Search the IT knowledge base for relevant information"
       )
       async def search_knowledge(
           self,
           query: Annotated[str, "Search query"],
           top_k: Annotated[int, "Number of results to return"] = 5,
           category: Annotated[str, "Filter by category (optional)"] = None,
           locale: Annotated[str, "Preferred language: en, da, sv"] = None,
       ) -> list[Source]:
           """Search knowledge base."""
           results = await self.search_client.hybrid_search(
               query=query,
               top_k=top_k,
               filters={
                   "category": category,
                   "locale": locale,
               } if category or locale else None,
           )

           return [
               Source(
                   title=r["title"],
                   url=r.get("source_url"),
                   snippet=r.get("content", "")[:500],
                   confidence=r.get("@search.score", 0.0),
               )
               for r in results
           ]

       @kernel_function(
           name="get_top_faqs",
           description="Get most frequently asked questions by category"
       )
       async def get_top_faqs(
           self,
           category: Annotated[str, "FAQ category"] = None,
           limit: Annotated[int, "Number of FAQs to return"] = 5,
       ) -> list[dict]:
           """Get top FAQs."""
           # Implementation depends on FAQ storage
           pass
   ```

#### Acceptance Criteria:
- [ ] Hybrid search (text + vector) working
- [ ] Category filtering
- [ ] Locale filtering
- [ ] Confidence scores returned
- [ ] Snippets extracted properly

---

### 4.4 Register Plugins with Kernel

**Assignee:** Backend Developer
**Estimated effort:** 2 hours

#### Modify `backend/app/agents/kernel.py`:

```python
from app.plugins.freshservice import FreshServicePlugin
from app.plugins.graph import GraphPlugin
from app.plugins.knowledge import KnowledgePlugin
from app.services.search_client import get_search_client

def create_kernel_with_plugins() -> Kernel:
    """Create kernel with all plugins registered."""
    kernel = create_kernel()

    # Register plugins
    kernel.add_plugin(FreshServicePlugin(), plugin_name="freshservice")
    kernel.add_plugin(GraphPlugin(), plugin_name="graph")
    kernel.add_plugin(KnowledgePlugin(get_search_client()), plugin_name="knowledge")

    return kernel
```

#### Update IT Support Agent to use plugins:

```python
class ITSupportAgent(BaseAgent):
    async def chat(self, ...):
        # Agent can now call plugins via function calling
        # e.g., kernel.invoke("freshservice", "create_ticket", ...)
        pass
```

---

### 4.5 Update Ticket Router with FreshService

**Assignee:** Backend Developer
**Estimated effort:** 3 hours

#### Modify `backend/app/routers/tickets.py`:

```python
from app.plugins.freshservice import FreshServicePlugin

@router.post("", response_model=Ticket)
async def create_ticket(
    request: CreateTicketRequest,
    user: UserClaims = Depends(get_current_user),
):
    plugin = FreshServicePlugin()
    ticket = await plugin.create_ticket(
        subject=request.subject,
        description=request.description,
        requester_email=user.email,
        priority=request.priority.value,
        session_id=request.session_id,
    )
    return ticket

@router.get("", response_model=list[Ticket])
async def list_tickets(
    user: UserClaims = Depends(get_current_user),
    status_filter: str | None = None,
):
    plugin = FreshServicePlugin()
    tickets = await plugin.get_user_tickets(
        email=user.email,
        status=status_filter,
    )
    return tickets
```

---

## Integration Testing

### FreshService Integration Test:
```bash
# Create test ticket
curl -X POST "http://localhost:8000/api/v1/tickets" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test from AI Agent",
    "description": "This is a test ticket created by the IT Support Agent",
    "priority": 3
  }'

# Verify in FreshService portal that ticket was created
```

### Graph Integration Test:
```bash
# Get user info (via internal API or test endpoint)
curl -X GET "http://localhost:8000/api/v1/admin/users/test@molslinjen.dk" \
  -H "Authorization: Bearer <admin-token>"
```

---

## Definition of Done

- [ ] FreshService plugin fully implemented
- [ ] Graph plugin fully implemented
- [ ] Knowledge plugin integrated with search
- [ ] All plugins registered with kernel
- [ ] Ticket endpoints using FreshService plugin
- [ ] Integration tests passing
- [ ] Error handling for external service failures
- [ ] Rate limiting/retry logic implemented
- [ ] Secrets not logged
