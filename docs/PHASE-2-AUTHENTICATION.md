# Phase 2: Authentication & Authorization

## Overview
Implement Azure AD (Entra ID) authentication for both frontend (MSAL) and backend (JWT validation) with role-based access control.

## Prerequisites
- Azure AD tenant access
- App registration permissions
- Phase 1 completed

---

## Tasks

### 2.1 Create Azure AD App Registrations

**Assignee:** Identity Engineer / Infrastructure
**Estimated effort:** 2 hours

#### Steps:

1. **Create Frontend App Registration:**
   - Name: `molslinjen-it-agent-frontend`
   - Supported account types: Single tenant
   - Redirect URIs:
     - `http://localhost:5173` (dev)
     - `https://your-domain.com` (prod)
   - Enable ID tokens (implicit flow)
   - Enable Access tokens

2. **Create Backend App Registration:**
   - Name: `molslinjen-it-agent-api`
   - Supported account types: Single tenant
   - Expose an API:
     - Application ID URI: `api://molslinjen-it-agent`
     - Scopes: `access_as_user`

3. **Configure API Permissions (Frontend app):**
   - Add permission to Backend API: `access_as_user`
   - Microsoft Graph: `User.Read`

4. **Create App Roles (Backend app):**
   ```json
   [
     {
       "displayName": "Employee",
       "value": "Employee",
       "allowedMemberTypes": ["User"]
     },
     {
       "displayName": "IT Admin",
       "value": "ITAdmin",
       "allowedMemberTypes": ["User"]
     }
   ]
   ```

5. **Assign Users to Roles:**
   - Enterprise Applications → Backend app → Users and groups
   - Assign IT staff to ITAdmin role
   - All employees get Employee role by default

#### Deliverables:
- Frontend Client ID
- Backend Client ID
- Tenant ID
- API scope URI

#### Acceptance Criteria:
- [ ] Both app registrations created
- [ ] Roles configured
- [ ] Test users assigned to roles
- [ ] Redirect URIs configured for all environments

---

### 2.2 Implement Frontend MSAL Authentication

**Assignee:** Frontend Developer
**Estimated effort:** 6 hours

#### Files to Create/Modify:

1. **Create `frontend/src/auth/msalConfig.ts`:**
   ```typescript
   import { Configuration, LogLevel } from '@azure/msal-browser';

   export const msalConfig: Configuration = {
     auth: {
       clientId: import.meta.env.VITE_AZURE_AD_CLIENT_ID,
       authority: `https://login.microsoftonline.com/${import.meta.env.VITE_AZURE_AD_TENANT_ID}`,
       redirectUri: import.meta.env.VITE_AZURE_AD_REDIRECT_URI,
     },
     cache: {
       cacheLocation: 'sessionStorage',
       storeAuthStateInCookie: false,
     },
   };

   export const loginRequest = {
     scopes: ['api://molslinjen-it-agent/access_as_user'],
   };
   ```

2. **Create `frontend/src/auth/AuthProvider.tsx`:**
   ```typescript
   // MsalProvider wrapper
   // - Initialize MSAL instance
   // - Handle redirect callbacks
   // - Provide auth context
   ```

3. **Create `frontend/src/auth/useAuth.ts`:**
   ```typescript
   // Custom hook for auth operations
   // - login()
   // - logout()
   // - getAccessToken()
   // - isAuthenticated
   // - user info
   // - roles
   ```

4. **Create `frontend/src/auth/ProtectedRoute.tsx`:**
   ```typescript
   // Route wrapper requiring authentication
   // - Redirect to login if not authenticated
   // - Optional role requirement
   ```

5. **Update `frontend/src/App.tsx`:**
   - Wrap with AuthProvider
   - Add login/logout UI
   - Show user info

6. **Update `frontend/src/api/client.ts`:**
   - Get token from MSAL before requests
   - Handle token refresh
   - Handle 401 responses

#### Acceptance Criteria:
- [ ] User can sign in with Microsoft account
- [ ] User can sign out
- [ ] Token automatically attached to API requests
- [ ] Token refresh works silently
- [ ] User info displayed in UI
- [ ] Protected routes redirect to login

#### Testing:
```typescript
// Manual testing checklist:
// 1. Open http://localhost:5173
// 2. Click "Sign In" → Microsoft login page
// 3. Enter credentials → Redirected back
// 4. User name displayed in header
// 5. API calls include Bearer token
// 6. Click "Sign Out" → Logged out
// 7. Protected routes redirect to login
```

---

### 2.3 Implement Backend JWT Validation

**Assignee:** Backend Developer
**Estimated effort:** 4 hours

#### Files to Modify:

1. **Update `backend/app/middleware/auth.py`:**
   ```python
   from jose import jwt, JWTError
   from jose.exceptions import ExpiredSignatureError
   import httpx

   # Cache for JWKS keys
   _jwks_cache: dict = {}
   _jwks_cache_time: float = 0

   async def get_azure_ad_jwks(tenant_id: str) -> dict:
       """Fetch Azure AD signing keys with caching."""
       # Implement JWKS fetching with 24h cache
       pass

   async def validate_token(
       credentials: HTTPAuthorizationCredentials,
       settings: Settings,
   ) -> dict:
       """Validate Azure AD JWT token."""
       token = credentials.credentials

       # 1. Decode header to get key ID
       # 2. Fetch JWKS and find matching key
       # 3. Validate signature, issuer, audience, expiry
       # 4. Return claims
       pass
   ```

2. **Add token validation tests `backend/tests/test_auth.py`:**
   ```python
   # Test valid token acceptance
   # Test expired token rejection
   # Test invalid signature rejection
   # Test wrong audience rejection
   # Test role extraction
   ```

#### Acceptance Criteria:
- [ ] Valid tokens accepted
- [ ] Expired tokens rejected (401)
- [ ] Invalid signatures rejected (401)
- [ ] Wrong audience rejected (401)
- [ ] Roles correctly extracted from token
- [ ] User claims available in request handlers

#### Testing:
```bash
# Get a token (use browser dev tools or az cli)
az account get-access-token --resource api://molslinjen-it-agent

# Test with valid token
curl -X GET "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer <token>"

# Test with invalid token
curl -X GET "http://localhost:8000/api/v1/chat/sessions" \
  -H "Authorization: Bearer invalid-token"
# Expected: 401 Unauthorized
```

---

### 2.4 Implement Role-Based Access Control

**Assignee:** Backend Developer
**Estimated effort:** 2 hours

#### Steps:

1. **Update admin routes to use `require_admin` dependency:**
   - Already stubbed in `routers/admin.py`
   - Verify all admin endpoints protected

2. **Add role checks to sensitive operations:**
   ```python
   # Example: Only admins can delete FAQs
   @router.delete("/{faq_id}")
   async def delete_faq(
       faq_id: str,
       user: UserClaims = Depends(require_admin),  # Enforces ITAdmin role
   ):
       ...
   ```

3. **Create `backend/tests/test_authorization.py`:**
   ```python
   # Test employee can access chat endpoints
   # Test employee cannot access admin endpoints
   # Test admin can access all endpoints
   ```

#### Acceptance Criteria:
- [ ] Employees can access: chat, tickets, feedback, FAQs (read)
- [ ] Admins can access: all above + admin dashboard, FAQ management
- [ ] Unauthorized access returns 403 Forbidden
- [ ] Role check happens after authentication

---

### 2.5 Update Frontend Environment Configuration

**Assignee:** Frontend Developer
**Estimated effort:** 30 minutes

#### Update `frontend/.env.local`:
```env
VITE_AZURE_AD_TENANT_ID=<your-tenant-id>
VITE_AZURE_AD_CLIENT_ID=<frontend-app-client-id>
VITE_AZURE_AD_REDIRECT_URI=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
VITE_API_SCOPE=api://molslinjen-it-agent/access_as_user
```

#### Acceptance Criteria:
- [ ] All auth-related env vars documented
- [ ] Example file updated
- [ ] CI/CD pipeline has env vars configured

---

## Security Checklist

- [ ] Tokens never logged (mask in logs)
- [ ] Tokens stored in sessionStorage (not localStorage)
- [ ] HTTPS enforced in production
- [ ] CORS configured for specific origins only
- [ ] Token expiry handled gracefully
- [ ] Refresh tokens used when available
- [ ] Failed auth attempts logged for monitoring

---

## Definition of Done

- [ ] Users can authenticate via Azure AD
- [ ] JWT validation working on all protected endpoints
- [ ] Role-based access control enforced
- [ ] Token refresh working silently
- [ ] Auth errors handled gracefully in UI
- [ ] Security review completed
- [ ] Documentation updated
