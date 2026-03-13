# Phase 1: Azure Infrastructure & AI Setup

## Overview
Set up Azure AI services required for the IT Support Agent including Azure AI Foundry (OpenAI), Azure AI Search, and configure connections.

## Prerequisites
- Azure subscription with Contributor access
- Azure CLI installed and authenticated
- Resource group created for the project

---

## Tasks

### 1.1 Create Azure AI Foundry Resource

**Assignee:** Infrastructure Engineer
**Estimated effort:** 2-3 hours

#### Steps:
1. Create Azure OpenAI resource in Azure Portal
   - Region: West Europe (or nearest supported region)
   - Pricing tier: Standard S0

2. Deploy models:
   | Deployment Name | Model | Purpose |
   |-----------------|-------|---------|
   | `gpt-5-mini` | gpt-4o-mini | Main chat responses |
   | `gpt-5` | gpt-4o | Triage/intent classification |
   | `gpt-5-nano` | gpt-4o-mini | Pre-filter (fast) |
   | `text-embedding-3-small` | text-embedding-3-small | Document embeddings |

3. Note down:
   - Endpoint URL
   - API Key
   - Deployment names

#### Acceptance Criteria:
- [ ] All 4 model deployments are active
- [ ] Can make test API call to each deployment
- [ ] Credentials stored in Azure Key Vault

#### Testing:
```bash
# Test chat deployment
curl -X POST "https://<endpoint>/openai/deployments/gpt-5-mini/chat/completions?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "api-key: <key>" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'

# Test embedding deployment
curl -X POST "https://<endpoint>/openai/deployments/text-embedding-3-small/embeddings?api-version=2024-02-01" \
  -H "Content-Type: application/json" \
  -H "api-key: <key>" \
  -d '{"input": "test text"}'
```

---

### 1.2 Create Azure AI Search Resource

**Assignee:** Infrastructure Engineer
**Estimated effort:** 2-3 hours

#### Steps:
1. Create Azure AI Search resource
   - Pricing tier: Basic (minimum for semantic ranking)
   - Region: Same as AI Foundry

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
- [ ] Vector search configured
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
**Estimated effort:** 1 hour

#### Steps:
1. Update `backend/.env` with actual values:
   ```env
   AZURE_FOUNDRY_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_FOUNDRY_KEY=<key>
   AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
   AZURE_SEARCH_KEY=<key>
   AZURE_STORAGE_CONNECTION_STRING=<connection-string>
   AZURE_STORAGE_ACCOUNT_NAME=<account-name>
   ```

2. Verify configuration loads:
   ```bash
   cd backend
   python -c "from app.config import get_settings; s = get_settings(); print(s.AZURE_FOUNDRY_ENDPOINT)"
   ```

#### Acceptance Criteria:
- [ ] All environment variables set
- [ ] Settings load without errors
- [ ] Secrets not committed to git

---

### 1.5 Create Azure SDK Integration Module

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Steps:
1. Create `backend/app/services/__init__.py`
2. Create `backend/app/services/ai_client.py`:
   ```python
   # Azure OpenAI client wrapper
   # - get_chat_completion()
   # - get_embedding()
   # - Retry logic with exponential backoff
   ```

3. Create `backend/app/services/search_client.py`:
   ```python
   # Azure AI Search client wrapper
   # - search_documents()
   # - hybrid_search() (text + vector)
   # - index_document()
   ```

#### Acceptance Criteria:
- [ ] AI client can call all deployments
- [ ] Search client can query index
- [ ] Error handling for rate limits
- [ ] Logging for debugging

#### Testing:
```bash
cd backend
pytest tests/test_ai_client.py -v
pytest tests/test_search_client.py -v
```

---

## Environment Variables Checklist

| Variable | Source | Required |
|----------|--------|----------|
| `AZURE_FOUNDRY_ENDPOINT` | AI Foundry resource | Yes |
| `AZURE_FOUNDRY_KEY` | AI Foundry keys | Yes |
| `AZURE_FOUNDRY_CHAT_DEPLOYMENT` | Deployment name | Yes |
| `AZURE_FOUNDRY_TRIAGE_DEPLOYMENT` | Deployment name | Yes |
| `AZURE_FOUNDRY_PREFILTER_DEPLOYMENT` | Deployment name | Yes |
| `AZURE_FOUNDRY_EMBEDDING_DEPLOYMENT` | Deployment name | Yes |
| `AZURE_SEARCH_ENDPOINT` | Search resource | Yes |
| `AZURE_SEARCH_KEY` | Search keys | Yes |
| `AZURE_SEARCH_INDEX` | Index name | Yes |
| `AZURE_STORAGE_CONNECTION_STRING` | Storage account | Yes |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account | Yes |

---

## Definition of Done
- [ ] All Azure resources provisioned
- [ ] SDK clients implemented and tested
- [ ] Environment configuration documented
- [ ] Integration tests passing
- [ ] Cost monitoring alerts configured
