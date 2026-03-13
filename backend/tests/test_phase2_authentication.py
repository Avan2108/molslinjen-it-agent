"""
Phase 2: Authentication Tests
Run these tests to verify authentication setup is complete.

Usage:
    pytest tests/test_phase2_authentication.py -v
    pytest tests/test_phase2_authentication.py -v -m "not slow"
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

pytestmark = pytest.mark.phase2


class TestAzureADConfiguration:
    """Test 2.1: Verify Azure AD configuration."""

    def test_azure_ad_tenant_id_set(self):
        """Verify Azure AD tenant ID is configured."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.AZURE_AD_TENANT_ID, "AZURE_AD_TENANT_ID must be set"
        # Should be a GUID format
        assert len(settings.AZURE_AD_TENANT_ID) >= 32

    def test_azure_ad_client_id_set(self):
        """Verify Azure AD client ID is configured."""
        from app.config import get_settings
        settings = get_settings()
        assert settings.AZURE_AD_CLIENT_ID, "AZURE_AD_CLIENT_ID must be set"


class TestAuthMiddleware:
    """Test 2.2: Verify auth middleware behavior."""

    def test_protected_endpoint_requires_auth(self):
        """Verify protected endpoints require authentication."""
        from app.main import app
        client = TestClient(app)

        # Try to access protected endpoint without token
        response = client.get("/api/v1/chat/sessions")

        assert response.status_code == 403  # HTTPBearer returns 403 when no auth header

    def test_protected_endpoint_rejects_invalid_token(self):
        """Verify invalid tokens are rejected."""
        from app.main import app
        client = TestClient(app)

        response = client.get(
            "/api/v1/chat/sessions",
            headers={"Authorization": "Bearer invalid-token-here"}
        )

        # Should return 401 or 501 (not implemented yet)
        assert response.status_code in [401, 501]

    def test_dev_token_works_in_development(self):
        """Verify dev-token works for development."""
        from app.main import app
        client = TestClient(app)

        response = client.get(
            "/api/v1/chat/sessions",
            headers={"Authorization": "Bearer dev-token"}
        )

        # Should return 501 (not implemented) rather than auth error
        assert response.status_code == 501
        assert "not yet implemented" in response.json()["detail"].lower()


class TestUserClaimsExtraction:
    """Test 2.3: Verify user claims are extracted correctly."""

    def test_dev_user_has_employee_role(self):
        """Verify dev user has Employee role."""
        from app.middleware.auth import get_current_user
        from app.models.enums import UserRole
        from fastapi.security import HTTPAuthorizationCredentials
        from app.config import get_settings
        import asyncio

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials="dev-token"
        )
        settings = get_settings()

        user = asyncio.run(get_current_user(credentials, settings))

        assert user is not None
        assert UserRole.EMPLOYEE in user.roles
        assert user.email == "dev@molslinjen.dk"

    def test_user_claims_model(self):
        """Test UserClaims model properties."""
        from app.models.auth import UserClaims
        from app.models.enums import UserRole

        # Test employee
        employee = UserClaims(
            oid="test-oid",
            email="test@molslinjen.dk",
            name="Test User",
            preferred_username="test@molslinjen.dk",
            roles=[UserRole.EMPLOYEE],
            tenant_id="test-tenant",
        )
        assert not employee.is_admin
        assert employee.display_name == "Test User"

        # Test admin
        admin = UserClaims(
            oid="admin-oid",
            email="admin@molslinjen.dk",
            name="Admin User",
            preferred_username="admin@molslinjen.dk",
            roles=[UserRole.EMPLOYEE, UserRole.IT_ADMIN],
            tenant_id="test-tenant",
        )
        assert admin.is_admin


class TestRoleBasedAccess:
    """Test 2.4: Verify role-based access control."""

    def test_admin_endpoint_requires_admin_role(self):
        """Verify admin endpoints require ITAdmin role."""
        from app.main import app
        client = TestClient(app)

        # Dev token has Employee role, not Admin
        response = client.get(
            "/api/v1/admin/analytics",
            headers={"Authorization": "Bearer dev-token"}
        )

        # Should be forbidden (403) not unauthorized (401)
        assert response.status_code == 403
        assert "admin" in response.json()["detail"].lower()

    def test_employee_can_access_chat(self):
        """Verify employees can access chat endpoints."""
        from app.main import app
        client = TestClient(app)

        response = client.post(
            "/api/v1/chat",
            headers={"Authorization": "Bearer dev-token"},
            json={"message": "test"}
        )

        # Should return 501 (not implemented) not 403 (forbidden)
        assert response.status_code == 501

    def test_employee_can_access_tickets(self):
        """Verify employees can access ticket endpoints."""
        from app.main import app
        client = TestClient(app)

        response = client.get(
            "/api/v1/tickets",
            headers={"Authorization": "Bearer dev-token"}
        )

        assert response.status_code == 501  # Not implemented, but authorized


class TestRequireAdminDependency:
    """Test 2.5: Test require_admin dependency."""

    @pytest.mark.asyncio
    async def test_require_admin_allows_admin(self):
        """Verify require_admin allows admin users."""
        from app.middleware.auth import require_admin
        from app.models.auth import UserClaims
        from app.models.enums import UserRole

        admin_user = UserClaims(
            oid="admin-oid",
            email="admin@molslinjen.dk",
            name="Admin",
            preferred_username="admin@molslinjen.dk",
            roles=[UserRole.IT_ADMIN],
            tenant_id="test-tenant",
        )

        result = await require_admin(admin_user)
        assert result == admin_user

    @pytest.mark.asyncio
    async def test_require_admin_blocks_employee(self):
        """Verify require_admin blocks non-admin users."""
        from app.middleware.auth import require_admin
        from app.models.auth import UserClaims
        from app.models.enums import UserRole
        from fastapi import HTTPException

        employee = UserClaims(
            oid="emp-oid",
            email="emp@molslinjen.dk",
            name="Employee",
            preferred_username="emp@molslinjen.dk",
            roles=[UserRole.EMPLOYEE],
            tenant_id="test-tenant",
        )

        with pytest.raises(HTTPException) as exc_info:
            await require_admin(employee)

        assert exc_info.value.status_code == 403


# ============================================================================
# Frontend Auth Tests (Manual Checklist)
# ============================================================================

class TestFrontendAuthChecklist:
    """
    Frontend Authentication Manual Test Checklist.

    These tests must be performed manually in the browser.
    """

    def test_frontend_auth_checklist(self):
        """
        Manual Frontend Auth Tests:

        1. Sign In Flow:
           [ ] Navigate to http://localhost:5173
           [ ] Click "Sign In" button
           [ ] Redirected to Microsoft login
           [ ] Enter valid credentials
           [ ] Redirected back to app
           [ ] User name displayed in header

        2. Token Handling:
           [ ] Open browser DevTools → Network tab
           [ ] Make any API request
           [ ] Verify Authorization header contains "Bearer <token>"
           [ ] Token is not visible in URL

        3. Sign Out:
           [ ] Click "Sign Out" button
           [ ] Session cleared
           [ ] Redirected to login or home

        4. Protected Routes:
           [ ] Try accessing /admin without admin role
           [ ] Should see access denied or redirect

        5. Token Refresh:
           [ ] Stay logged in for >1 hour
           [ ] Make API request
           [ ] Should still work (silent refresh)
        """
        pass


def test_phase2_summary():
    """
    Phase 2 Authentication Checklist:

    Run: pytest tests/test_phase2_authentication.py -v

    Backend Tests:
    - [ ] Azure AD configuration set
    - [ ] Auth middleware protecting endpoints
    - [ ] Dev token working for development
    - [ ] User claims extraction working
    - [ ] Role-based access control enforced
    - [ ] Admin endpoints require ITAdmin role

    Frontend Tests (Manual):
    - [ ] Sign in with Microsoft works
    - [ ] Token attached to API requests
    - [ ] Sign out clears session
    - [ ] Admin routes protected
    """
    pass
