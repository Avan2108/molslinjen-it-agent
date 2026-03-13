# Phase 1: Infrastructure & AI Setup

## Overview
Set up the infrastructure required for the IT Support Agent including OpenAI API access, Azure AI Search, and Azure Table Storage.

## Prerequisites
- OpenAI API account with GPT-5 access
- Azure subscription with Contributor access
- Azure CLI installed and authenticated
- Resource group created for the project

---

## Tasks

### 1.1 Configure OpenAI API Access

**Assignee:** Backend Developer
**Estimated effort:** 30 minutes

#### Steps:
1. Get OpenAI API key from https://platform.openai.com/api-keys

2. Verify GPT-5 access:
   - Model: `gpt-5` - Used for all AI tasks (chat, triage, prefilter)
   - Model: `text-embedding-3-small` - Used for document embeddings

3. Note down:
   - API Key
   - Organization ID (if applicable)

#### Acceptance Criteria:
- [ ] API key obtained and working
- [ ] GPT-5 model accessible
- [ ] Embedding model accessible
- [ ] API key stored securely (not in code)

#### Testing:
```bash
# Test GPT-5 chat
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "gpt-5",
    "messages": [{"role": "user", "content": "Hello, respond with OK"}]
  }'

# Test embedding
curl -X POST "https://api.openai.com/v1/embeddings" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
    "model": "text-embedding-3-small",
    "input": "test text"
  }'
```

---

### 1.2 Create Azure AI Search Resource

**Assignee:** Infrastructure Engineer
**Estimated effort:** 2-3 hours

#### Steps:
1. Create Azure AI Search resource
   - Pricing tier: Basic (minimum for semantic ranking)
   - Region: West Europe (or nearest)

2. Create index `it-knowledge` with schema:
   ```json
   {
     "name": "it-knowledge",
     "fields": [
       {"name": "id", "type": "Edm.String", "key": true},
       {"name": "title", "type": "Edm.String", "searchable": true},
       {"name": "content", "type": "Edm.String", "searchable": true},
       {"name": "category", "type": "Edm.String", "filterable": true, "facetable": true},
       {"name": "source_url", "type": "Edm.String"},
       {"name": "last_updated", "type": "Edm.DateTimeOffset", "filterable": true, "sortable": true},
       {"name": "locale", "type": "Edm.String", "filterable": true},
       {"name": "content_vector", "type": "Collection(Edm.Single)", "dimensions": 1536, "vectorSearchProfile": "default-profile"}
     ],
     "vectorSearch": {
       "profiles": [{"name": "default-profile", "algorithm": "default-algorithm"}],
       "algorithms": [{"name": "default-algorithm", "kind": "hnsw"}]
     },
     "semantic": {
       "configurations": [{
         "name": "default",
         "prioritizedFields": {
           "titleField": {"fieldName": "title"},
           "contentFields": [{"fieldName": "content"}]
         }
       }]
     }
   }
   ```

3. Note down:
   - Search endpoint
   - Admin API key
   - Query API key

#### Acceptance Criteria:
- [ ] Index created with correct schema
- [ ] Vector search configured (1536 dimensions for text-embedding-3-small)
- [ ] Semantic ranking enabled
- [ ] Can perform test queries

#### Testing:
```bash
# Test index exists
curl -X GET "https://<search-endpoint>/indexes/it-knowledge?api-version=2024-07-01" \
  -H "api-key: <admin-key>"

# Test search (after adding documents)
curl -X POST "https://<search-endpoint>/indexes/it-knowledge/docs/search?api-version=2024-07-01" \
  -H "Content-Type: application/json" \
  -H "api-key: <query-key>" \
  -d '{"search": "password reset", "top": 5}'
```

---

### 1.3 Create Azure Storage Account

**Assignee:** Infrastructure Engineer
**Estimated effort:** 1 hour

#### Steps:
1. Create Storage Account
   - Performance: Standard
   - Redundancy: LRS (or GRS for production)
   - Enable Table Storage

2. Tables will be auto-created by the application:
   - `ChatSessions`
   - `Feedback`
   - `FAQEvents`
   - `AdminLog`

3. Note down:
   - Storage account name
   - Connection string

#### Acceptance Criteria:
- [ ] Storage account created
- [ ] Table service accessible
- [ ] Connection string works

#### Testing:
```python
from azure.data.tables import TableServiceClient

conn_str = "<connection-string>"
service = TableServiceClient.from_connection_string(conn_str)
tables = list(service.list_tables())
print(f"Tables: {tables}")
```

---

### 1.4 Create Backend Configuration

**Assignee:** Backend Developer
**Estimated effort:** 30 minutes

#### Steps:
1. Update `backend/.env` with actual values:
   ```env
   # OpenAI
   OPENAI_API_KEY=sk-your-api-key
   OPENAI_MODEL=gpt-5
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small

   # Azure AI Search
   AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
   AZURE_SEARCH_KEY=<key>

   # Azure Table Storage
   AZURE_STORAGE_CONNECTION_STRING=<connection-string>
   AZURE_STORAGE_ACCOUNT_NAME=<account-name>
   ```

2. Verify configuration loads:
   ```bash
   cd backend
   python -c "from app.config import get_settings; s = get_settings(); print(s.OPENAI_MODEL)"
   ```

#### Acceptance Criteria:
- [ ] All environment variables set
- [ ] Settings load without errors
- [ ] Secrets not committed to git

---

### 1.5 Create SDK Integration Module

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Steps:
1. Create `backend/app/services/__init__.py`

2. Create `backend/app/services/openai_client.py`:
   ```python
   """OpenAI client wrapper."""

   from openai import AsyncOpenAI
   from app.config import get_settings

   class OpenAIClient:
       def __init__(self):
           settings = get_settings()
           self.client = AsyncOpenAI(
               api_key=settings.OPENAI_API_KEY.get_secret_value(),
               base_url=settings.OPENAI_BASE_URL,
           )
           self.model = settings.OPENAI_MODEL
           self.embedding_model = settings.OPENAI_EMBEDDING_MODEL

       async def chat(
           self,
           messages: list[dict],
           temperature: float = 0.7,
           max_tokens: int = 1000,
       ) -> str:
           """Get chat completion from GPT-5."""
           response = await self.client.chat.completions.create(
               model=self.model,
               messages=messages,
               temperature=temperature,
               max_tokens=max_tokens,
           )
           return response.choices[0].message.content

       async def embed(self, text: str) -> list[float]:
           """Get embedding vector."""
           response = await self.client.embeddings.create(
               model=self.embedding_model,
               input=text,
           )
           return response.data[0].embedding
   ```

3. Create `backend/app/services/search_client.py`:
   ```python
   """Azure AI Search client wrapper."""

   # - search_documents()
   # - hybrid_search() (text + vector)
   # - index_document()
   ```

4. Add `openai>=1.0.0` to requirements.txt

#### Acceptance Criteria:
- [ ] OpenAI client can call GPT-5
- [ ] OpenAI client can generate embeddings
- [ ] Search client can query index
- [ ] Error handling for rate limits
- [ ] Logging for debugging

#### Testing:
```bash
cd backend
pytest tests/test_openai_client.py -v
pytest tests/test_search_client.py -v
```

---

## Environment Variables Checklist

| Variable | Source | Required |
|----------|--------|----------|
| `OPENAI_API_KEY` | OpenAI Platform | Yes |
| `OPENAI_MODEL` | Model name (gpt-5) | Yes |
| `OPENAI_EMBEDDING_MODEL` | Model name | Yes |
| `OPENAI_BASE_URL` | API base URL | No (has default) |
| `AZURE_SEARCH_ENDPOINT` | Search resource | Yes |
| `AZURE_SEARCH_KEY` | Search keys | Yes |
| `AZURE_SEARCH_INDEX` | Index name | Yes |
| `AZURE_STORAGE_CONNECTION_STRING` | Storage account | Yes |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account | Yes |

---

## Architecture Note

Using a single GPT-5 model simplifies the architecture:

```
┌─────────────────────────────────────────┐
│              GPT-5 Model                │
│  ┌─────────┐ ┌─────────┐ ┌───────────┐  │
│  │  Chat   │ │ Triage  │ │ PreFilter │  │
│  │Response │ │ Intent  │ │  Safety   │  │
│  └─────────┘ └─────────┘ └───────────┘  │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│       text-embedding-3-small            │
│           (Embeddings only)             │
└─────────────────────────────────────────┘
```

**Benefits:**
- Simpler configuration (one model to manage)
- Consistent quality across all AI tasks
- Easier debugging and monitoring
- Can adjust via prompt engineering per task

**Trade-offs:**
- Higher cost per request (GPT-5 vs mini models)
- May be slower for simple tasks (consider caching)

---

## Definition of Done
- [ ] OpenAI API access configured
- [ ] Azure AI Search index created
- [ ] Azure Storage account created
- [ ] SDK clients implemented and tested
- [ ] Environment configuration documented
- [ ] Integration tests passing
