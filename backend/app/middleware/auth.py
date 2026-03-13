"""Authentication middleware — Phase 1: optional auth (no Azure AD required).

Phase 1: All requests are accepted. If an Authorization header is present and
equals "dev-token", a developer/admin user is returned. Otherwise an anonymous
employee user is returned so the API works without any token.

Phase 3 (Azure AD): Replace `get_current_user` with real JWT validation.
"""

from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.models import UserClaims
from app.models.enums import UserRole

# auto_error=False means FastAPI won't raise 401 when the header is absent
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserClaims:
    """Return user claims.

    Phase 1 behaviour:
    - No Authorization header → anonymous employee (full access to chat/tickets)
    - Authorization: Bearer dev-token → dev/admin user
    - Any other token → accepted as anonymous employee

    Replace this function body in Phase 3 with real Azure AD validation.
    """
    if credentials and credentials.credentials == "dev-token":
        return UserClaims(
            oid="dev-user-oid",
            email="dev@molslinjen.dk",
            name="Development User",
            preferred_username="dev@molslinjen.dk",
            roles=[UserRole.EMPLOYEE, UserRole.IT_ADMIN],
            tenant_id="dev-tenant",
            department="IT",
            job_title="Developer",
        )

    # Phase 1: anonymous employee — no token required
    return UserClaims(
        oid="anonymous",
        email="anonymous@localhost",
        name="Anonymous",
        preferred_username="anonymous",
        roles=[UserRole.EMPLOYEE],
        tenant_id="",
        department=None,
        job_title=None,
    )


async def require_admin(
    user: Annotated[UserClaims, Depends(get_current_user)],
) -> UserClaims:
    """Dependency that requires IT Admin role."""
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IT Admin role required",
        )
    return user
