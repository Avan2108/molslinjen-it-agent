# Phase 7: Production Readiness

## Overview
Prepare the application for production deployment including Azure infrastructure, monitoring, security hardening, and operational procedures.

## Prerequisites
- All previous phases completed
- E2E testing passed
- UAT sign-off received

---

## Tasks

### 7.1 Azure Infrastructure Setup

**Assignee:** DevOps / Infrastructure Engineer
**Estimated effort:** 8 hours

#### Azure Resources to Create:

1. **Resource Group**: `rg-molslinjen-it-agent-prod`

2. **App Service Plan**:
   - SKU: P1v3 or higher
   - OS: Linux
   - Region: West Europe

3. **App Service (Backend)**:
   - Name: `app-molslinjen-it-agent-api`
   - Runtime: Python 3.12
   - Always On: Enabled
   - HTTPS Only: Enabled

4. **Static Web App (Frontend)**:
   - Name: `swa-molslinjen-it-agent-web`
   - SKU: Standard
   - Build: GitHub Actions

5. **Application Insights**:
   - Name: `appi-molslinjen-it-agent`
   - Workspace-based

6. **Key Vault**:
   - Name: `kv-molslinjen-it-agent`
   - All secrets stored here

7. **Azure Front Door** (optional):
   - WAF policy
   - CDN for static assets
   - SSL termination

#### Infrastructure as Code:

Create `infrastructure/main.bicep`:
```bicep
@description('Environment name')
param environment string = 'prod'

@description('Location for resources')
param location string = resourceGroup().location

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2022-03-01' = {
  name: 'asp-molslinjen-it-agent-${environment}'
  location: location
  sku: {
    name: 'P1v3'
    tier: 'PremiumV3'
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

// Backend App Service
resource backendApp 'Microsoft.Web/sites@2022-03-01' = {
  name: 'app-molslinjen-it-agent-api-${environment}'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      alwaysOn: true
      httpsOnly: true
      minTlsVersion: '1.2'
    }
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'appi-molslinjen-it-agent-${environment}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = {
  name: 'kv-mols-it-agent-${environment}'
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
}
```

#### Deployment:
```bash
az group create -n rg-molslinjen-it-agent-prod -l westeurope
az deployment group create -g rg-molslinjen-it-agent-prod -f infrastructure/main.bicep
```

---

### 7.2 CI/CD Pipeline Enhancement

**Assignee:** DevOps Engineer
**Estimated effort:** 6 hours

#### Update `.github/workflows/backend.yml`:

```yaml
name: Backend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'
  pull_request:
    branches: [main]

env:
  AZURE_WEBAPP_NAME: app-molslinjen-it-agent-api-prod

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # ... existing test steps

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Login to Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: ${{ env.AZURE_WEBAPP_NAME }}
          package: backend

      - name: Health check
        run: |
          sleep 30
          curl -f https://${{ env.AZURE_WEBAPP_NAME }}.azurewebsites.net/health
```

#### Update `.github/workflows/frontend.yml`:

```yaml
name: Frontend CI/CD

on:
  push:
    branches: [main]
    paths:
      - 'frontend/**'

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    environment: production

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install and Build
        run: |
          cd frontend
          npm ci
          npm run build
        env:
          VITE_AZURE_AD_TENANT_ID: ${{ secrets.AZURE_AD_TENANT_ID }}
          VITE_AZURE_AD_CLIENT_ID: ${{ secrets.AZURE_AD_CLIENT_ID }}
          VITE_API_BASE_URL: https://app-molslinjen-it-agent-api-prod.azurewebsites.net

      - name: Deploy to Static Web App
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          action: 'upload'
          app_location: 'frontend/dist'
```

---

### 7.3 Monitoring & Alerting

**Assignee:** DevOps Engineer
**Estimated effort:** 4 hours

#### Application Insights Integration:

1. **Backend instrumentation** - Create `backend/app/telemetry.py`:
   ```python
   from opencensus.ext.azure.log_exporter import AzureLogHandler
   from opencensus.ext.azure.trace_exporter import AzureExporter
   from opencensus.trace.samplers import ProbabilitySampler
   import logging

   def setup_telemetry(connection_string: str):
       # Configure logging
       logger = logging.getLogger(__name__)
       logger.addHandler(AzureLogHandler(connection_string=connection_string))

       # Configure tracing
       # ...
   ```

2. **Key metrics to track**:
   - Request rate and latency
   - Error rate by endpoint
   - AI model response times
   - Token usage
   - Active sessions
   - Escalation rate

3. **Create alerts**:
   | Alert | Condition | Severity |
   |-------|-----------|----------|
   | High error rate | >5% 5xx errors in 5 min | Sev 1 |
   | Slow responses | P95 latency >5s | Sev 2 |
   | AI service errors | >10 failures in 5 min | Sev 1 |
   | Low disk space | <20% free | Sev 2 |

4. **Create dashboard**:
   - Real-time request metrics
   - Error breakdown
   - AI performance
   - User activity

---

### 7.4 Security Hardening

**Assignee:** Security Engineer
**Estimated effort:** 6 hours

#### Security Checklist:

1. **Network Security**:
   - [ ] Enable Azure Private Endpoints for storage/AI services
   - [ ] Configure NSG rules
   - [ ] Enable DDoS protection
   - [ ] WAF rules configured

2. **Authentication/Authorization**:
   - [ ] Token validation secure
   - [ ] Role checks on all protected endpoints
   - [ ] Session timeout configured
   - [ ] CORS strictly configured

3. **Data Protection**:
   - [ ] All data encrypted at rest
   - [ ] All data encrypted in transit (TLS 1.2+)
   - [ ] PII handling compliant with GDPR
   - [ ] Conversation data retention policy

4. **Secrets Management**:
   - [ ] All secrets in Key Vault
   - [ ] Managed identities used where possible
   - [ ] Secret rotation policy defined
   - [ ] No secrets in code/logs

5. **Logging & Audit**:
   - [ ] Security events logged
   - [ ] Admin actions audited
   - [ ] Log retention configured
   - [ ] Sensitive data not logged

6. **Vulnerability Management**:
   - [ ] Dependency scanning enabled
   - [ ] Container scanning (if applicable)
   - [ ] Regular security reviews scheduled

#### Security Headers:

Update `backend/app/main.py`:
```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# HTTPS redirect in production
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.azurewebsites.net"])
```

---

### 7.5 Documentation

**Assignee:** Technical Writer / Full Stack Developer
**Estimated effort:** 4 hours

#### Documents to Create:

1. **Operations Runbook** (`docs/OPERATIONS.md`):
   - Deployment procedures
   - Rollback procedures
   - Incident response
   - Common issues and solutions
   - Escalation contacts

2. **API Documentation**:
   - Keep OpenAPI spec updated
   - Add examples for each endpoint
   - Document error codes

3. **User Guide** (`docs/USER-GUIDE.md`):
   - How to use the chat
   - How to create tickets
   - How to provide feedback
   - FAQ

4. **Admin Guide** (`docs/ADMIN-GUIDE.md`):
   - Dashboard overview
   - Managing FAQs
   - Reviewing knowledge gaps
   - Reindexing procedures

---

### 7.6 Performance Testing

**Assignee:** QA Engineer
**Estimated effort:** 4 hours

#### Load Testing with k6:

Create `tests/load/chat-load-test.js`:
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'], // 95% of requests under 3s
    http_req_failed: ['rate<0.01'],    // Error rate under 1%
  },
};

export default function () {
  const res = http.post(
    'https://app-molslinjen-it-agent-api-prod.azurewebsites.net/api/v1/chat',
    JSON.stringify({ message: 'How do I reset my password?' }),
    {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${__ENV.TEST_TOKEN}`,
      },
    }
  );

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time OK': (r) => r.timings.duration < 3000,
  });

  sleep(1);
}
```

#### Performance Targets:
- P95 response time: <3 seconds
- Concurrent users: 100+
- Error rate: <1%
- Uptime: 99.9%

---

### 7.7 Go-Live Checklist

**Assignee:** Project Lead
**Estimated effort:** 2 hours

#### Pre-Launch:
- [ ] All tests passing
- [ ] Security review completed
- [ ] Performance testing passed
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Alerts configured
- [ ] Backup procedures tested
- [ ] Rollback plan documented
- [ ] Support team trained
- [ ] Stakeholder sign-off

#### Launch Day:
- [ ] Deploy to production
- [ ] Smoke test all features
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Verify logging working
- [ ] Test alerts trigger correctly

#### Post-Launch:
- [ ] Monitor for 24-48 hours
- [ ] Address any issues
- [ ] Gather initial feedback
- [ ] Plan first iteration improvements

---

## Operational Procedures

### Deployment
1. Merge to main triggers CI/CD
2. Automated tests run
3. Deploy to staging (if applicable)
4. Deploy to production
5. Health check verification
6. Monitor for issues

### Rollback
1. Identify issue requiring rollback
2. Azure Portal → App Service → Deployment slots
3. Swap to previous slot OR
4. GitHub Actions → Re-run previous successful deploy

### Incident Response
1. Alert received
2. Acknowledge and assess severity
3. Engage on-call engineer
4. Investigate and resolve
5. Post-incident review

---

## Definition of Done

- [ ] All infrastructure deployed
- [ ] CI/CD pipelines working
- [ ] Monitoring and alerting active
- [ ] Security hardening complete
- [ ] Documentation complete
- [ ] Performance targets met
- [ ] Go-live checklist completed
- [ ] Production deployment successful
- [ ] Handover to operations team
