"""Authentication middleware for Azure AD token validation."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings, get_settings
from app.models import UserClaims
from app.models.enums import UserRole

security = HTTPBearer()


async def validate_token(
    credentials: HTTPAuthorizationCredentials,
    settings: Settings,
) -> dict:
    """Validate Azure AD JWT token.

    TODO: Implement actual token validation using:
    - python-jose for JWT decoding
    - Azure AD JWKS endpoint for key retrieval
    - Issuer and audience validation
    """
    # Placeholder - will be implemented with actual Azure AD validation
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Token validation not yet implemented",
    )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> UserClaims:
    """Extract and validate user claims from Azure AD token.

    This dependency:
    1. Extracts the Bearer token from Authorization header
    2. Validates the token against Azure AD
    3. Extracts user claims and maps roles

    Returns:
        UserClaims with user information and roles

    Raises:
        HTTPException 401 if token is invalid or expired
        HTTPException 403 if user lacks required permissions
    """
    # For development, return a mock user
    # TODO: Replace with actual token validation
    if credentials.credentials == "dev-token":
        return UserClaims(
            oid="dev-user-oid",
            email="dev@molslinjen.dk",
            name="Development User",
            preferred_username="dev@molslinjen.dk",
            roles=[UserRole.EMPLOYEE],
            tenant_id="dev-tenant",
            department="IT",
            job_title="Developer",
        )

    token_data = await validate_token(credentials, settings)

    # Extract roles from token claims
    roles = []
    token_roles = token_data.get("roles", [])
    for role in token_roles:
        try:
            roles.append(UserRole(role))
        except ValueError:
            # Unknown role, skip
            pass

    # Default to Employee if no roles assigned
    if not roles:
        roles = [UserRole.EMPLOYEE]

    return UserClaims(
        oid=token_data["oid"],
        email=token_data.get("email", token_data.get("preferred_username", "")),
        name=token_data.get("name", ""),
        preferred_username=token_data.get("preferred_username", ""),
        roles=roles,
        tenant_id=token_data.get("tid", ""),
        department=token_data.get("department"),
        job_title=token_data.get("jobTitle"),
    )


async def require_admin(
    user: Annotated[UserClaims, Depends(get_current_user)],
) -> UserClaims:
    """Dependency that requires IT Admin role.

    Use this dependency on admin-only endpoints.

    Returns:
        UserClaims if user is admin

    Raises:
        HTTPException 403 if user is not an admin
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="IT Admin role required",
        )
    return user
